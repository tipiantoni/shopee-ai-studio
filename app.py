import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time
import random
import urllib.parse

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

def generate_image_pollinations(prompt):
    """
    Gera imagem usando Pollinations.ai (Não precisa de API Key).
    """
    # Codifica o prompt para URL
    prompt_encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 99999)
    
    # URL Mágica (Modelo Flux ou SDXL)
    image_url = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&seed={seed}&model=flux"
    
    # Baixa a imagem gerada
    response = requests.get(image_url, timeout=30)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Erro no servidor Pollinations: {response.status_code}")

def get_text_ai_response(api_key, prompt, image):
    """
    Auto-Descoberta de modelo do Google (Texto)
    """
    genai.configure(api_key=api_key)
    
    # Tenta modelos na ordem de preferência
    candidate_models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]
    
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text, model_name
        except:
            continue
            
    # Se falhar nos nomes padrão, tenta listar da conta
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                 try:
                    model = genai.GenerativeModel(m.name)
                    response = model.generate_content([prompt, image])
                    return response.text, m.name
                 except:
                     continue
    except:
        pass

    raise Exception("Erro no Google AI. Verifique a chave API ou a Cota.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Chaves de Acesso")
    
    if "GOOGLE_API_KEY" in st.secrets:
        google_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Google AI Conectado", icon="✅")
    else:
        google_key = st.text_input("Google API Key", type="password")

    # REMOVI O CAMPO DA HUGGING FACE POIS NÃO PRECISA MAIS!
    st.success("Gerador de Imagem: Pollinations (Grátis/Sem Chave)", icon="🎨")

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
    if not google_key:
        st.error("⚠️ Coloque a Google API Key primeiro.")
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
            
            # --- FASE 2: IMAGEM (POLLINATIONS - SEM CHAVE) ---
            st.divider()
            st.subheader(f"📸 {qtd_imagens} Variações")
            cols = st.columns(qtd_imagens)
            
            for i in range(qtd_imagens):
                with cols[i]:
                    with st.spinner(f"Criando foto {i+1}..."):
                        try:
                            # Adiciona detalhes para melhorar a qualidade
                            final_prompt = f"{prompt_img}, photorealistic, 8k, highly detailed, product photography"
                            
                            img_bytes = generate_image_pollinations(final_prompt)
                            
                            st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
                                
                        except Exception as e:
                            st.warning(f"Erro foto {i+1}: {e}")
            
            st.success("Sucesso! Pode cadastrar na Shopee.")
