import streamlit as st
import google.generativeai as genai
from PIL import Image
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

# --- 3. CABEÇALHO ---
st.markdown("""
<div class="branding-box">
    <div class="branding-title">🚀 Shopee AI Studio</div>
    <div class="branding-subtitle">Ferramenta desenvolvida por <b>Ti Piantoni</b> | Especialista em IA & Automação</div>
</div>
""", unsafe_allow_html=True)

# --- 4. CÉREBRO DA IA (GOOGLE) ---
def get_ai_strategy(api_key, image, cenario):
    genai.configure(api_key=api_key)
    
    # LISTAS DE VARIAÇÃO ALEATÓRIA (O Segredo do Dinamismo)
    # O Python escolhe um desses a cada clique, garantindo que o prompt nunca seja igual.
    iluminacoes = [
        "Cinematic Volumetric Lighting (God Rays)",
        "Soft Studio Lighting (High Key)",
        "Moody Dark Lighting (Low Key)",
        "Golden Hour Natural Sunlight",
        "Neon Cyberpunk Rim Lights",
        "Dramatic Chiaroscuro"
    ]
    
    angulos = [
        "Low Angle (Hero View)",
        "Eye Level (Product Focus)",
        "Top Down (Flat Lay)",
        "Dutch Angle (Dynamic)",
        "Macro Close-up (Texture Focus)"
    ]
    
    # Sorteia a direção de arte da vez
    luz_sorteada = random.choice(iluminacoes)
    angulo_sorteado = random.choice(angulos)
    
    # Lista de modelos (Tenta o mais inteligente primeiro)
    modelos = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
    
    prompt_sistema = f"""
    Você é um Engenheiro de Prompt Sênior (Expert em Midjourney v6 e Flux).
    Analise esta imagem do produto.
    
    O produto deve ser inserido neste cenário: {cenario}.
    
    DIREÇÃO DE ARTE OBRIGATÓRIA PARA O PROMPT:
    - Iluminação: {luz_sorteada}
    - Ângulo: {angulo_sorteado}
    
    GERE DUAS SAÍDAS:
    
    SAÍDA 1: COPY SHOPEE
    - Título SEO e Descrição AIDA curta.
    
    SAÍDA 2: PROMPT MASTER DINÂMICO (Em Inglês)
    Crie um prompt visualmente rico.
    IMPORTANTE: No final do prompt, adicione parâmetros que forcem variação mas mantenham a qualidade.
    Estrutura:
    [SUBJECT: Detailed description of the product from image] + 
    [ENVIRONMENT: {cenario}, detailed texture, background elements] + 
    [TECH: {luz_sorteada}, {angulo_sorteado}, 8k, photorealistic, Unreal Engine 5] +
    [PARAMETERS: --chaos 15 --stylize 250 --v 6.0]
    
    Separe as saídas com: ---DIVISOR---
    """
    
    for model_name in modelos:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt_sistema, image])
            return response.text, luz_sorteada, angulo_sorteado
        except: continue
            
    raise Exception("Erro de conexão com Google AI.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Configuração")
    if "GOOGLE_API_KEY" in st.secrets:
        google_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Cérebro Conectado", icon="✅")
    else:
        google_key = st.text_input("Cole sua Google API Key", type="password")

    st.divider()
    st.header("🎨 Direção de Arte")
    cenario = st.selectbox("Cenário Base", [
        "Fundo Infinito Branco", 
        "Cozinha Gourmet Moderna",
        "Banheiro de Luxo em Mármore", 
        "Sala de Estar Aconchegante", 
        "Ao Ar Livre / Natureza", 
        "Mesa de Escritório Minimalista",
        "Estúdio Neon High-Tech"
    ])
    
    st.info("ℹ️ Cada clique gera um prompt com Luz e Ângulo diferentes automaticamente.")
    st.markdown("© 2025 **Ti Piantoni**")

# --- 6. INTERFACE PRINCIPAL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Seu Produto")
    uploaded_file = st.file_uploader("Arraste a foto do fornecedor", type=["jpg", "png", "jpeg", "webp"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Referência", use_column_width=True)
        btn_gerar = st.button("🎲 Gerar Prompt Dinâmico", type="primary", use_container_width=True)

# --- 7. PROCESSAMENTO ---
if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
    if not google_key:
        st.error("⚠️ Falta a chave do Google.")
    else:
        with col2:
            st.subheader("2. Estratégia Gerada")
            
            with st.spinner("🧠 Sorteando direção de arte e criando prompt..."):
                try:
                    full_response, luz, angulo = get_ai_strategy(google_key, image, cenario)
                    
                    if "---DIVISOR---" in full_response:
                        parts = full_response.split("---DIVISOR---")
                        copy_shopee = parts[0].strip()
                        prompt_img = parts[1].strip().replace("SAÍDA 2: PROMPT MASTER DINÂMICO (Em Inglês)", "").strip()
                    else:
                        copy_shopee = full_response
                        prompt_img = "Erro na formatação. Tente novamente."

                    # Mostra a Copy
                    with st.expander("📝 Ver Copy para Shopee", expanded=False):
                        st.markdown(copy_shopee)
                    
                    st.divider()
                    
                    # Mostra os detalhes sorteados (Para você saber o que ele criou)
                    st.caption(f"✨ Variação Automática: **{luz}** | **{angulo}**")
                    
                    st.subheader("🎨 Seu Prompt Mestre")
                    st.markdown("Este prompt contém parâmetros `--chaos` e `--stylize` para gerar resultados variados a cada tentativa.")
                    st.code(prompt_img, language="text")
                    
                    st.success("Pronto! Copie e cole no Midjourney/Flux.")
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
