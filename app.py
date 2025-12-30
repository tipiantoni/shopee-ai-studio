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
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

def get_working_model_response(api_key, prompt, image):
    """
    FUNÇÃO DE AUTO-DESCOBERTA:
    Em vez de adivinhar o modelo, pergunta para a API quais estão disponíveis
    e usa o primeiro que funcionar.
    """
    genai.configure(api_key=api_key)
    
    available_models = []
    log_tentativas = []

    # 1. Lista todos os modelos que a SUA chave consegue ver
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Prioriza modelos Flash (mais rápidos/baratos) colocando no topo
                if 'flash' in m.name:
                    available_models.insert(0, m.name)
                else:
                    available_models.append(m.name)
    except Exception as e:
        raise Exception(f"Erro ao listar modelos da conta: {e}")

    if not available_models:
        raise Exception("Nenhum modelo disponível encontrado para esta API Key.")

    # 2. Tenta usar os modelos da lista um por um
    for model_name in available_models:
        try:
            # Pula modelos vision antigos que dão erro
            if '1.0' in model_name or 'vision' in model_name:
                continue
                
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text, model_name # SUCESSO!
            
        except Exception as e:
            error_msg = str(e)
            log_tentativas.append(f"{model_name}: {error_msg}")
            # Se for erro de Cota (429), tenta o próximo. Se for 404, tenta o próximo.
            continue
            
    # Se chegou aqui, nada funcionou
    raise Exception(f"Falha em todos os modelos listados.\nDetalhes: {log_tentativas}")

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
    with st.expander("ℹ️ Info Técnica"):
        st.info("Modo: Auto-Discovery (Detecta modelos da sua conta)")

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
            
            with st.spinner("🧠 Ti Piantoni AI: Buscando o melhor modelo disponível..."):
                try:
                    prompt_full = f"""
                    Analise esta imagem. O produto deve ser inserido neste cenário: {cenario}.
                    
                    TAREFA 1: Crie um prompt curto em INGLÊS para gerar uma foto realista (Comece com 'PROMPT_IMG:').
                    
                    TAREFA 2: Crie um anúncio persuasivo para Shopee.
                    Formato:
                    # Título com Ícones
                    ## Descrição (AIDA)
                    ## Benefícios
                    ## Ficha Técnica Visual
                    """
                    
                    # --- CHAMA A FUNÇÃO DE AUTO-DESCOBERTA ---
                    response_text, modelo_usado = get_working_model_response(google_key, prompt_full, image)
                    
                    st.toast(f"Conectado via: {modelo_usado}", icon='🤖')
                    
                    try:
                        prompt_img = response_text.split("PROMPT_IMG:")[1].split("\n")[0].strip()
                    except:
                        prompt_img = f"Professional photo of product in {cenario}, 4k"
                    
                    st.markdown(response_text.replace("PROMPT_IMG:", "**Prompt Visual:** "))
                    
                except Exception as e:
                    st.error(f"ERRO FATAL: Sua chave não tem acesso a nenhum modelo de geração. Erro: {e}")
                    st.stop()
            
            # PARTE 2: IMAGEM
            st.divider()
            st.subheader(f"📸 {qtd_imagens} Variações")
            cols = st.columns(qtd_imagens)
            for i in range(qtd_imagens):
                with cols[i]:
                    try:
                        image_bytes = query_huggingface({
                            "inputs": prompt_img, 
                            "parameters": {"seed": i*55, "negative_prompt": "blurry, bad art"}
                        }, hf_key)
                        st.image(Image.open(io.BytesIO(image_bytes)), use_column_width=True)
                    except:
                        st.caption("Erro ao gerar imagem.")
            st.success("Sucesso!")
