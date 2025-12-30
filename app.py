import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time
import random
import urllib.parse
import re

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
    /* Esconde traceback de erro para não assustar o usuário */
    .stException { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO VISUAL ---
st.markdown("""
<div class="branding-box">
    <div class="branding-title">🚀 Shopee AI Studio</div>
    <div class="branding-subtitle">Ferramenta desenvolvida por <b>Ti Piantoni</b> | Especialista em IA & Automação</div>
</div>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE IA (BLINDADAS) ---

def sanitize_prompt(text):
    """
    O TRITURADOR: Remove tudo que não for letra ou número e corta o tamanho
    para garantir que a URL nunca quebre.
    """
    # Mantém apenas letras (a-z, A-Z), números (0-9) e espaços. Remove o resto.
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Corta para no máximo 100 caracteres por segurança extrema
    return cleaned[:100]

def generate_image_pollinations_safe(prompt):
    """
    Gera imagem via Pollinations com tratamento de erro robusto.
    Retorna None se falhar, em vez de travar o app.
    """
    try:
        # 1. Limpeza Extrema do Prompt
        prompt_safe = sanitize_prompt(prompt)
        
        # 2. Monta a URL
        prompt_encoded = urllib.parse.quote(prompt_safe)
        seed = random.randint(1, 99999)
        # Usando modelo 'flux' que é o melhor atualmente lá
        image_url = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
        
        # Fake browser headers
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
        response = requests.get(image_url, headers=headers, timeout=20)
        
        # Verifica se deu certo E se o que voltou é realmente uma imagem
        if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
            return response.content
        else:
            return None # Falhou silenciosamente
            
    except Exception:
        return None # Falhou silenciosamente

def get_text_ai_response(api_key, prompt, image):
    # Tenta vários modelos do Google em ordem
    genai.configure(api_key=api_key)
    candidate_models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]
    
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text, model_name
        except: continue
            
    # Tenta listar da conta se os padrão falharem
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                 try:
                    model = genai.GenerativeModel(m.name)
                    response = model.generate_content([prompt, image])
                    return response.text, m.name
                 except: continue
    except: pass
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
    cenario = st.selectbox("Cenário", ["Fundo Infinito Branco", "Banheiro de Luxo", "Cozinha Moderna", "Sala de Estar", "Ao Ar Livre", "Escritório Minimalista"])
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
            # FASE 1: TEXTO
            with st.spinner("🧠 Analisando produto..."):
                try:
                    # Pedimos apenas PALAVRAS-CHAVE para a imagem
                    prompt_full = f"""
                    Analise esta imagem. O produto deve ser inserido neste cenário: {cenario}.
                    TAREFA 1 (IMPORTANTE): Para gerar a imagem, me dê APENAS 3 a 5 PALAVRAS-CHAVE em Inglês. Não use frases completas. Exemplo: 'red shoes modern kitchen sunlight'. Comece com 'PROMPT_IMG:'.
                    TAREFA 2: Crie um anúncio persuasivo para Shopee (Título, Descrição, Benefícios).
                    """
                    response_text, modelo_texto = get_text_ai_response(google_key, prompt_full, image)
                    st.toast(f"Texto ok ({modelo_texto})", icon='📝')
                    try: prompt_img = response_text.split("PROMPT_IMG:")[1].split("\n")[0].strip()
                    except: prompt_img = f"product {cenario} high quality"
                    st.markdown(response_text.replace("PROMPT_IMG:", "**Keywords da Imagem:** "))
                except Exception as e:
                    st.error(f"Erro Texto: {e}")
                    st.stop()
            
            # FASE 2: IMAGEM (BLINDADA)
            st.divider()
            st.subheader(f"📸 {qtd_imagens} Variações")
            cols = st.columns(qtd_imagens)
            for i in range(qtd_imagens):
                with cols[i]:
                    with st.spinner(f"Criando foto {i+1}..."):
                        # Chama a função segura
                        img_bytes = generate_image_pollinations_safe(prompt_img)
                        if img_bytes:
                            try:
                                # Tenta mostrar a imagem
                                st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
                            except:
                                # Se a imagem veio corrompida
                                st.warning("⚠️ Falha na renderização.")
                        else:
                             # Se o servidor de imagem falhou (retornou None)
                            st.warning("⚠️ Servidor de imagem instável. Tente novamente.")
            
            st.success("Processo finalizado.")
