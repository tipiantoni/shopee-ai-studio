import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time

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

def query_huggingface(payload, api_key):
    """
    Tenta conectar na API de imagem. Se o servidor estiver 'dormindo' (Erro 503),
    ele espera o tempo solicitado e tenta de novo.
    """
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Tenta até 3 vezes
    for tentativa in range(3):
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Sucesso (200)
        if response.status_code == 200:
            return response.content
        
        # Servidor Carregando (503)
        elif response.status_code == 503:
            try:
                dados = response.json()
                tempo_estimado = dados.get('estimated_time', 15)
                st.toast(f"💤 O servidor de imagem está acordando... Aguarde {tempo_estimado:.0f}s.", icon="⏳")
                time.sleep(tempo_estimado)
                continue # Tenta de novo
            except:
                break
        
        # Erro de Autorização (401)
        elif response.status_code == 401:
            raise Exception("Erro na Chave Hugging Face. Verifique se o Token tem permissão 'WRITE'.")
            
    # Se falhar após tentativas
    response.raise_for_status()
    return response.content

def get_working_model_response(api_key, prompt, image):
    """
    Auto-Descoberta de modelo do Google (Texto)
    """
    genai.configure(api_key=api_key)
    available_models = []

    try:
        # Lista modelos disponíveis
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: # Prioriza Flash
                    available_models.insert(0, m.name)
                else:
                    available_models.append(m.name)
    except Exception as e:
        raise Exception(f"Erro ao listar modelos: {e}")

    # Testa um por um
    for model_name in available_models:
        try:
            if '1.0' in model_name or 'vision' in model_name: continue
            
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text, model_name
        except:
            continue
            
    raise Exception("Nenhum modelo do Google funcionou. Verifique sua chave API.")

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
            
            # --- FASE 1: TEXTO (GOOGLE) ---
            with st.spinner("🧠 Ti Piantoni AI: Criando estratégia..."):
                try:
                    prompt_full = f"""
                    Analise esta imagem. O produto deve ser inserido neste cenário: {cenario}.
                    TAREFA 1: Crie um prompt curto em INGLÊS para gerar uma foto realista (Comece com 'PROMPT_IMG:').
                    TAREFA 2: Crie um anúncio persuasivo para Shopee.
                    Formato: # Título, ## Descrição, ## Benefícios, ## Ficha Técnica
                    """
                    
                    response_text, modelo_usado = get_working_model_response(google_key, prompt_full, image)
                    st.toast(f"Texto gerado com: {modelo_usado}", icon='🤖')
                    
                    try:
                        prompt_img = response_text.split("PROMPT_IMG:")[1].split("\n")[0].strip()
                    except:
                        prompt_img = f"Professional photo of product in {cenario}, 4k"
                    
                    st.markdown(response_text.replace("PROMPT_IMG:", "**Prompt Visual:** "))
                    
                except Exception as e:
                    st.error(f"Erro no Texto: {e}")
                    st.stop()
            
            # --- FASE 2: IMAGEM (HUGGING FACE COM ESPERA) ---
            st.divider()
            st.subheader(f"📸 {qtd_imagens} Variações")
            cols = st.columns(qtd_imagens)
            
            for i in range(qtd_imagens):
                with cols[i]:
                    with st.spinner(f"Criando foto {i+1}..."):
                        try:
                            # Adiciona um pouco de "caos" na semente para variar as fotos
                            seed_variation = i * 1234 + int(time.time() % 100)
                            
                            image_bytes = query_huggingface({
                                "inputs": prompt_img, 
                                "parameters": {
                                    "seed": seed_variation, 
                                    "negative_prompt": "blurry, bad art, distorted, ugly, watermark, text"
                                }
                            }, hf_key)
                            
                            # Tenta abrir a imagem. Se falhar, mostra o erro que veio.
                            try:
                                generated_image = Image.open(io.BytesIO(image_bytes))
                                st.image(generated_image, use_column_width=True)
                            except:
                                st.error("Erro ao processar imagem.")
                                st.code(image_bytes) # Mostra o erro técnico se não for imagem
                                
                        except Exception as e:
                            st.warning(f"Falha na imagem {i+1}: {e}")
            
            st.success("Processo Finalizado!")
