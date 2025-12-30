import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Shopee AI Studio | Ti Piantoni", page_icon="🚀", layout="wide")

# --- 2. ESTILO CSS (VISUAL TI PIANTONI) ---
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
    .prompt-box {
        background-color: #262730;
        color: #ffffff;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #4e4e4e;
        font-family: monospace;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO ---
st.markdown("""
<div class="branding-box">
    <div class="branding-title">🚀 Shopee AI Studio</div>
    <div class="branding-subtitle">Ferramenta desenvolvida por <b>Ti Piantoni</b> | Especialista em IA & Automação</div>
</div>
""", unsafe_allow_html=True)

# --- 4. FUNÇÃO DE INTELIGÊNCIA (GOOGLE) ---
def get_ai_strategy(api_key, image, cenario):
    genai.configure(api_key=api_key)
    
    # Lista de modelos para tentar (do mais rápido para o mais robusto)
    modelos = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]
    
    # Prompt de Engenharia Reversa para criar o PROMPT DE IMAGEM PERFEITO
    prompt_sistema = f"""
    Você é um especialista em E-commerce e um Engenheiro de Prompt Sênior para Midjourney e Flux.
    Analise esta imagem do produto. O objetivo é vender este produto na Shopee.
    
    O produto deve ser imaginado neste cenário: {cenario}.
    
    GERE DUAS SAÍDAS DISTINTAS:
    
    SAÍDA 1: COPY SHOPEE
    - Título SEO (com ícones, max 60 chars)
    - Descrição AIDA (Atenção, Interesse, Desejo, Ação) curta e persuasiva.
    - 5 Benefícios em bullets.
    
    SAÍDA 2: PROMPT MASTER DE IMAGEM (Em Inglês)
    Escreva um prompt altamente detalhado para gerar uma foto publicitária premiada deste produto.
    Estrutura do Prompt:
    [Sujeito Principal Detalhado] + [Ambiente/Cenário] + [Iluminação de Estúdio/Cinemática] + [Detalhes da Câmera] + [Estilo: Photorealistic, 8k, Unreal Engine 5 render].
    Não use frases como "Generate an image". Comece direto com a descrição visual.
    Use palavras-chave como: "hyper-detailed", "soft lighting", "bokeh", "product photography", "award winning".
    
    Separe as saídas com a tag: ---DIVISOR---
    """
    
    for model_name in modelos:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt_sistema, image])
            return response.text
        except:
            continue
            
    # Tenta listar da conta se os padrão falharem
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                 try:
                    model = genai.GenerativeModel(m.name)
                    response = model.generate_content([prompt_sistema, image])
                    return response.text
                 except: continue
    except: pass
    
    raise Exception("Erro de conexão com Google AI. Verifique sua chave.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Configuração")
    if "GOOGLE_API_KEY" in st.secrets:
        google_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Cérebro Conectado (Google)", icon="✅")
    else:
        google_key = st.text_input("Cole sua Google API Key", type="password")

    st.divider()
    st.header("🎨 Direção de Arte")
    cenario = st.selectbox("Onde o produto será fotografado?", [
        "Fundo Infinito Branco (E-commerce Padrão)", 
        "Cozinha Gourmet Moderna (High End)",
        "Banheiro de Luxo em Mármore (Spa Vibe)", 
        "Sala de Estar Aconchegante (Lifestyle)", 
        "Ao Ar Livre / Natureza (Golden Hour)", 
        "Mesa de Escritório Minimalista (Productivity)",
        "Estúdio Neon Cyberpunk (Gamer/Tech)"
    ])
    
    st.info("💡 Dica: Copie o prompt gerado e use no Midjourney, Leonardo.ai ou Bing Image Creator.")
    st.markdown("© 2025 **Ti Piantoni**")

# --- 6. INTERFACE PRINCIPAL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Seu Produto")
    uploaded_file = st.file_uploader("Arraste a foto do fornecedor", type=["jpg", "png", "jpeg", "webp"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Referência", use_column_width=True)
        btn_gerar = st.button("🚀 Gerar Estratégia + Prompt Master", type="primary", use_container_width=True)

# --- 7. PROCESSAMENTO ---
if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
    if not google_key:
        st.error("⚠️ Você precisa colocar a chave do Google na barra lateral.")
    else:
        with col2:
            st.subheader("2. Estratégia IA")
            
            with st.spinner("🧠 Analisando texturas, luz e mercado..."):
                try:
                    full_response = get_ai_strategy(google_key, image, cenario)
                    
                    # Separa a Copy do Prompt
                    if "---DIVISOR---" in full_response:
                        parts = full_response.split("---DIVISOR---")
                        copy_shopee = parts[0].strip()
                        prompt_img = parts[1].strip().replace("SAÍDA 2: PROMPT MASTER DE IMAGEM (Em Inglês)", "").strip()
                    else:
                        copy_shopee = full_response
                        prompt_img = "Erro ao separar o prompt. Tente novamente."

                    # EXIBIÇÃO DA COPY
                    st.markdown(copy_shopee)
                    
                    st.divider()
                    
                    # EXIBIÇÃO DO PROMPT
                    st.subheader("🎨 Seu Prompt Gerador de Imagens")
                    st.markdown("Copie o código abaixo e cole em qualquer IA de imagem (Midjourney, Bing, Leonardo, Flux):")
                    
                    # Caixa de código para facilitar a cópia
                    st.code(prompt_img, language="text")
                    
                    st.success("Estratégia criada! Agora você tem o controle total da imagem.")
                    
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")
