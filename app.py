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
    Gera imagem via Pollinations com tratamento de URL longa.
    """
    # 1. Limpa e encurta o prompt para não quebrar a URL (Max 80 chars)
    prompt_clean = prompt.replace("\n", " ").replace('"', "").strip()
    if len(prompt_clean) > 80:
        prompt_clean = prompt_clean[:80]
    
    # Adiciona palavras-chave de qualidade
    final_prompt = f"{prompt_clean}, hyperrealistic, 8k, product photography"
    prompt_encoded = urllib.parse.quote(final_prompt)
    
    seed = random.randint(1, 99999)
    
    # URL Direta
    image_url = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
    
    # Headers para fingir ser um browser (evita bloqueio)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Tenta baixar
    response = requests.get(image_url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        # Verifica se é realmente uma imagem
        if "image" in response.headers.get("content-type", ""):
            return response.content
        else:
            raise Exception("Servidor retornou texto em vez de imagem.")
    else:
        raise Exception(f"Erro {response.status_code}")

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
            
    # Fallback: tenta listar da conta
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

    raise Exception("Nenhum modelo do Google funcionou. Verifique sua chave API.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Chaves de Acesso")
    
    if "GOOGLE_API_KEY" in st.secrets:
        google_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Google AI Conectado", icon="✅")
    else:
        google_key = st.text_input("Google API Key", type="password")

    st.success("Gerador de Imagem: Pollinations (Ativo)", icon="🎨")

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
                    TAREFA 1: Crie um prompt MUITO CURTO (max 10 palavras) em INGLÊS apenas descrevendo o objeto principal para gerar uma foto. Comece com 'PROMPT_IMG:'.
                    TAREFA 2: Crie um anúncio persuasivo para Shopee.
                    """
                    
                    response_text, modelo_texto = get_text_ai_response(google_key, prompt_full, image)
                    st.toast(f"Texto ok ({modelo_texto})", icon='📝')
                    
                    try:
                        prompt_img = response_text.split("PROMPT_IMG:")[1].split("\n")[0].strip()
                    except:
                        prompt_img = f"product in {cenario}"
                    
                    st.markdown(response_text.replace("PROMPT_IMG:", "**Prompt Visual:** "))
                    
                except Exception as e:
                    st.error(f"Erro Texto: {e}")
                    st.stop()
            
            # --- FASE 2: IMAGEM (POLLINATIONS SEGURO) ---
            st.divider()
            st.subheader(f"📸 {qtd_imagens} Variações")
            cols = st.columns(qtd_imagens)
            
            for i in range(qtd_imagens):
                with cols[i]:
                    with st.spinner(f"Criando foto {i+1}..."):
                        try:
                            # Chama a função nova que corta o prompt se for grande
                            img_bytes = generate_image_pollinations(prompt_img)
                            
                            # Tenta converter
                            try:
                                generated_image = Image.open(io.BytesIO(img_bytes))
                                st.image(generated_image, use_column_width=True)
                            except Exception as e:
                                st.warning("Imagem corrompida. Tente gerar novamente.")
                                
                        except Exception as e:
                            st.warning(f"Erro foto {i+1}: URL muito longa ou servidor ocupado.")
            
            st.success("Sucesso! Pode cadastrar na Shopee.")
