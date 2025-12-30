import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Shopee AI Studio | Ti Piantoni", page_icon="🚀", layout="wide")

# --- 2. ESTILO CSS (BRANDING TI PIANTONI) ---
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
    .step-card {
        background-color: #e8f4f8;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        font-weight: bold;
        color: #0e1117;
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

# --- 4. FAQ / MANUAL INTEGRADO ---
with st.expander("📚 CLIQUE AQUI: Manual de Uso Passo a Passo"):
    st.markdown("""
    ### Como transformar produtos em vendas:
    
    1.  **📸 O Upload:** Tire um print ou baixe a foto do produto do fornecedor (pode ser fundo branco simples). Arraste para a área de upload.
    2.  **⚙️ A Configuração:**
        * Na barra lateral, escolha o **Cenário** que mais valoriza o produto (ex: *Cozinha Moderna* para utensílios).
        * Defina quantas **Variações de Imagem** você quer (recomendado: 2).
    3.  **🚀 A Mágica:** Clique no botão azul **"Gerar Copy + Fotos"**.
    4.  **💰 O Lucro:**
        * A IA vai escrever o Título e a Descrição Persuasiva.
        * A IA vai desenhar novas fotos lifestyle do produto.
        * **Copie tudo e cadastre na Shopee!**
    """)

st.divider()

# --- 5. FUNÇÕES DE IA ---
def query_huggingface(payload, api_key):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# --- 6. BARRA LATERAL (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("🔐 Chaves de Acesso")
    
    # Verifica Secrets ou pede manual
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
    
    cenario = st.selectbox("Onde o produto deve aparecer?", [
        "Fundo Infinito Branco (Studio)",
        "Banheiro de Luxo (Luxury Bathroom)",
        "Cozinha Moderna (Modern Kitchen)",
        "Sala de Estar Aconchegante (Living Room)",
        "Ao Ar Livre/Natureza (Outdoor)",
        "Mesa de Escritório Minimalista (Office)",
        "Academia / Fitness (Gym)"
    ])
    
    qtd_imagens = st.slider("Quantidade de Fotos", 1, 4, 2)
    st.caption("Nota: Mais fotos levam mais tempo para gerar.")
    
    st.divider()
    st.markdown("© 2025 **Ti Piantoni**")

# --- 7. INTERFACE PRINCIPAL ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Produto Original")
    uploaded_file = st.file_uploader("Faça upload da foto aqui", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Foto do Fornecedor", use_column_width=True)
        btn_gerar = st.button(f"🚀 Gerar Copy + {qtd_imagens} Fotos", type="primary", use_container_width=True)

# --- 8. LÓGICA DE PROCESSAMENTO ---
if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
    if not google_key or not hf_key:
        st.error("⚠️ ERRO: Configure as chaves de API na barra lateral ou nos Secrets.")
    else:
        with col2:
            st.subheader("2. Resultado IA")
            
            # PARTE 1: TEXTO (GOOGLE)
            with st.spinner("🧠 Ti Piantoni AI: Criando estratégia de vendas..."):
                try:
                    genai.configure(api_key=google_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt_full = f"""
                    Analise esta imagem. O produto deve ser inserido neste cenário: {cenario}.
                    
                    TAREFA 1: Crie um prompt descritivo em INGLÊS para gerar uma foto realista deste produto neste cenário. Comece com 'PROMPT_IMG:'.
                    
                    TAREFA 2: Crie um anúncio para Shopee (Título SEO + Descrição AIDA + Benefícios). Use tom persuasivo.
                    """
                    
                    response_text = model.generate_content([prompt_full, image]).text
                    
                    # Extrai o prompt da imagem
                    try:
                        prompt_img = response_text.split("PROMPT_IMG:")[1].split("\n")[0].strip()
                    except:
                        prompt_img = f"Professional photo of the product in a {cenario}, 4k, realistic"
                    
                    st.markdown(response_text.replace("PROMPT_IMG:", "**Prompt Visual Interno:** "))
                    
                except Exception as e:
                    st.error(f"Erro na análise de texto: {e}")
                    st.stop()
            
            # PARTE 2: IMAGEM (HUGGING FACE)
            st.divider()
            st.subheader(f"📸 {qtd_imagens} Novas Fotos Geradas")
            
            cols = st.columns(qtd_imagens)
            
            for i in range(qtd_imagens):
                with cols[i]:
                    with st.spinner(f"Renderizando foto {i+1}..."):
                        try:
                            image_bytes = query_huggingface({
                                "inputs": prompt_img,
                                "parameters": {
                                    "negative_prompt": "blurry, low quality, distorted, watermark, text, bad anatomy, deformed, ugly",
                                    "seed": i * 9999 # Garante variação
                                }
                            }, hf_key)
                            
                            generated_image = Image.open(io.BytesIO(image_bytes))
                            st.image(generated_image, caption=f"Opção {i+1}", use_column_width=True)
                            
                        except Exception as e:
                            st.warning("Servidor de imagem ocupado. Tente novamente em instantes.")
            
            st.success("Análise concluída com sucesso!")
