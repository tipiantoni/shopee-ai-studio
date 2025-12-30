import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time
import random

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Shopee AI Studio | Ti Piantoni", page_icon="🚀", layout="wide")

# --- 2. ESTILO CSS ---
st.markdown("""
<style>
    .branding-box {
        background-color: #f8f9fa;
        border-left: 6px solid #ff4b4b;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .branding-title {
        color: #31333F;
        font-family: 'Helvetica', sans-serif;
        font-weight: 800;
        font-size: 1.2rem;
        margin: 0;
    }
    .branding-subtitle {
        color: #555;
        font-size: 0.95rem;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO VISUAL ---
st.markdown("""
<div class="branding-box">
    <div class="branding-title">🚀 Shopee AI Studio</div>
    <div class="branding-subtitle">Ferramenta desenvolvida por <b>Ti Piantoni</b> | Especialista em IA & Automação</div>
</div>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE IA ---

def generate_image_with_fallback(prompt, api_key):
    """
    Tenta gerar imagem usando uma lista de modelos. Se um falhar, tenta o próximo.
    """
    # LISTA DE MODELOS (Do mais novo para o mais antigo/estável)
    modelos = [
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
        "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
        "https://api-inference.huggingface.co/models/prompthero/openjourney",
        "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    ]
    
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt, "parameters": {"negative_prompt": "blurry, bad quality, watermark, text, ugly"}}

    log_erros = []

    for model_url in modelos:
        model_name = model_url.split("/")[-1]
        
        # Tenta conectar no modelo atual (até 3 tentativas de 'acordar')
        for tentativa in range(3):
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=20)
                
                # SUCESSO (200)
                if response.status_code == 200:
                    return response.content, model_name
                
                # DORMINDO (503)
                elif response.status_code == 503:
                    wait_time = response.json().get('estimated_time', 10)
                    st.toast(f"⏳ {model_name} carregando ({wait_time:.0f}s)...", icon="💤")
                    time.sleep(wait_time)
                    continue # Tenta o mesmo modelo de novo
                
                # ERRO DE ACESSO/MODELO (404, 410, 403)
                else:
                    # Se der erro fatal, sai do loop de tentativas e vai pro próximo modelo
                    break
                    
            except Exception as e:
                break
        
        # Se chegou aqui, o modelo falhou. Registra e vai pro próximo da lista.
        log_erros.append(f"{model_name}: Falhou")
        continue

    # Se saiu do loop principal, nenhum funcionou
    raise Exception(f"Todos os geradores falharam. Verifique seu Token HF. (Log: {log_erros})")

def get_text_ai_response(api_key, prompt, image):
    """
    Auto-Descoberta de modelo do Google (Texto)
    """
    genai.configure(api_key=api_key)
    available_models = []
    
    # Lista modelos
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: available_models.insert(0, m.name)
                else: available_models.append(m.name)
    except:
        # Fallback manual se a listagem falhar
        available_models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']

    # Testa modelos
    for model_name in available_models:
        try:
            if 'vision' in model_name and '1.0' in model_name: continue
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text, model_name
        except:
            continue
            
    raise Exception("Erro no Google AI. Verifique a chave API.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Chaves de Acesso")
    
    if "GOOGLE_API_KEY" in st.secrets:
        google_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Google AI Conectado", icon="✅")
    else:
        google_key = st.text_input("Google API Key", type="password")

    if "HUGGINGFACE_KEY" in st.secrets:
        hf_key = st.secrets["HUGGINGFACE_KEY"]
        st.success("Hugging Face Conectado", icon="✅")
    else:
        hf_key = st.text_input("Hugging Face Token", type="password")

    st.divider()
    st.header("🎨 Estúdio Criativo")
    cenario = st.selectbox("Cenário", [
        "Fundo Infinito Branco", "Banheiro de Luxo", "Cozinha Moderna", 
        "Sala de Estar", "Ao Ar Livre", "Escritório Minimalista"
    ])
    qtd_imagens = st.slider("Qtd. Fotos", 1, 4, 2)
    st.markdown("© 2025 **Ti Piantoni**")

# --- 6. INTERFACE PRINCIPAL ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Produto Original")
    uploaded_file = st.file_uploader("Upload da Foto", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Sua Foto", use_column_width=True)
        btn_gerar = st.button(f"🚀 Gerar Copy + {qtd_imagens} Fotos", type="primary", use_container_width=True)

# --- 7. LÓGICA PRINCIPAL ---
if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
    if not google_key or not hf_key:
        st.error("⚠️ Configure as chaves de API primeiro.")
    else:
        with col2:
            st.subheader("2. Resultado IA")
            
            # --- FASE 1: TEXTO ---
            with st.spinner("🧠 Analisando produto..."):
                try:
                    prompt_full = f"""
                    Analise esta imagem. O produto deve ser inserido neste cenário: {cenario}.
                    TAREFA 1: Crie um prompt curto em INGLÊS para gerar uma foto realista (Comece com 'PROMPT_IMG:').
                    TAREFA 2: Crie um anúncio persuasivo para Shopee.
                    """
                    
                    response_text, modelo_texto = get_text_ai_response(google_key, prompt_full, image)
                    st.toast(f"Texto ok ({modelo_texto})", icon='📝')
                    
                    try:
                        prompt_img = response_text.split("PROMPT_IMG:")[1].split("\n")[0].strip()
                    except:
                        prompt_img = f"High quality photo of product in {cenario}, 4k"
                    
                    st.markdown(response_text.replace("PROMPT_IMG:", "**Prompt Visual:** "))
                    
                except Exception as e:
                    st.error(f"Erro Texto: {e}")
                    st.stop()
            
            # --- FASE 2: IMAGEM (MULTI-MOTOR) ---
            st.divider()
            st.subheader(f"📸 {qtd_imagens} Variações")
            cols = st.columns(qtd_imagens)
            
            for i in range(qtd_imagens):
                with cols[i]:
                    with st.spinner(f"Criando foto {i+1}..."):
                        try:
                            # Varia a 'semente' para a foto não sair igual
                            seed = random.randint(1, 99999)
                            final_prompt = f"{prompt_img}, seed: {seed}"
                            
                            img_bytes, modelo_img = generate_image_with_fallback(final_prompt, hf_key)
                            
                            st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
                            st.caption(f"Gerado via: {modelo_img}")
                                
                        except Exception as e:
                            st.warning(f"Erro foto {i+1}: {e}")
            
            st.success("Sucesso! Pode cadastrar na Shopee.")
