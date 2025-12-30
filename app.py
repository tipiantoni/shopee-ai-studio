import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time
import random
import urllib.parse
import re
import pandas as pd

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
    .metric-card {
        background-color: #e0f7fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #b2ebf2;
        text-align: center;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #006064;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555;
    }
    /* Esconde traceback de erro */
    .stException { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO VISUAL ---
st.markdown("""
<div class="branding-box">
    <div class="branding-title">🚀 Shopee AI Studio 2.0</div>
    <div class="branding-subtitle">Ferramenta desenvolvida por <b>Ti Piantoni</b> | Especialista em IA & Automação</div>
</div>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE IA (BLINDADAS) ---

def sanitize_prompt(text):
    """Remove caracteres especiais e limita tamanho para URL segura."""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return cleaned[:100]

def generate_image_pollinations_safe(prompt):
    """Gera imagem via Pollinations (Grátis e Sem Chave)."""
    try:
        prompt_safe = sanitize_prompt(prompt)
        prompt_encoded = urllib.parse.quote(prompt_safe)
        seed = random.randint(1, 99999)
        image_url = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        
        response = requests.get(image_url, headers=headers, timeout=20)
        if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
            return response.content
        else:
            return None
    except:
        return None

def get_text_ai_response(api_key, prompt, image):
    """Gera texto com Google Gemini."""
    genai.configure(api_key=api_key)
    candidate_models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]
    
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text, model_name
        except: continue
    
    # Tentativa de listar modelos da conta
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                 try:
                    model = genai.GenerativeModel(m.name)
                    response = model.generate_content([prompt, image])
                    return response.text, m.name
                 except: continue
    except: pass
    raise Exception("Erro Google AI.")

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
    st.markdown("© 2025 **Ti Piantoni**")

# --- 6. NAVEGAÇÃO POR ABAS ---
tab1, tab2 = st.tabs(["🎨 Estúdio Criativo (IA)", "🧮 Calculadora de Preço (R$)"])

# ==========================================
# ABA 1: GERADOR DE CRIATIVOS (IA)
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("1. Produto Original")
        
        # Configuração do Cenário aqui dentro para ficar organizado
        cenario = st.selectbox("Escolha o Cenário:", ["Fundo Infinito Branco", "Banheiro de Luxo", "Cozinha Moderna", "Sala de Estar", "Ao Ar Livre", "Escritório Minimalista"])
        qtd_imagens = st.slider("Qtd. Fotos", 1, 4, 2)
        
        uploaded_file = st.file_uploader("Upload da Foto", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Sua Foto", use_column_width=True)
            btn_gerar = st.button(f"🚀 Gerar Copy + {qtd_imagens} Fotos", type="primary", use_container_width=True)

    if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
        if not google_key:
            st.error("⚠️ Coloque a Google API Key na barra lateral.")
        else:
            with col2:
                st.subheader("2. Resultado IA")
                # FASE 1: TEXTO
                with st.spinner("🧠 Analisando produto..."):
                    try:
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
                
                # FASE 2: IMAGEM
                st.divider()
                st.subheader(f"📸 {qtd_imagens} Variações")
                cols = st.columns(qtd_imagens)
                for i in range(qtd_imagens):
                    with cols[i]:
                        with st.spinner(f"Criando foto {i+1}..."):
                            img_bytes = generate_image_pollinations_safe(prompt_img)
                            if img_bytes:
                                try: st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
                                except: st.warning("⚠️ Falha na renderização.")
                            else: st.warning("⚠️ Instabilidade no servidor.")
                st.success("Criativos gerados!")

# ==========================================
# ABA 2: CALCULADORA DE PRECIFICAÇÃO
# ==========================================
with tab2:
    st.header("🧮 Calculadora de Lucro Real (Shopee)")
    st.markdown("Descubra o **Preço de Venda** exato para garantir o lucro que você deseja.")
    
    col_calc_1, col_calc_2 = st.columns(2)
    
    with col_calc_1:
        st.subheader("1. Custos & Metas")
        
        custo_produto = st.number_input("Custo do Produto (R$)", value=0.00, step=1.00, help="Quanto você paga no fornecedor?")
        custo_extra = st.number_input("Embalagem/Mimo/Impostos (R$)", value=2.00, step=0.50, help="Custo de etiqueta, caixa, fita, brinde.")
        lucro_desejado = st.number_input("Lucro Desejado no Bolso (R$)", value=15.00, step=1.00, help="Quanto você quer ganhar LIMPO?")
        
        st.divider()
        st.subheader("2. Taxas da Shopee")
        programa_frete = st.checkbox("Participo do Frete Grátis Extra (+6%)", value=True)
        
        if programa_frete:
            taxa_pct = 0.20 # 20%
            texto_taxa = "20% (14% Padrão + 6% Frete)"
        else:
            taxa_pct = 0.14 # 14%
            texto_taxa = "14% (Padrão)"
            
        taxa_fixa = 4.00 # R$ 3 a R$ 4 (Usando 4 por segurança)
        st.caption(f"Considerando Taxa Fixa de R$ {taxa_fixa:.2f} por item vendido.")

    with col_calc_2:
        st.subheader("3. Resultado Final")
        
        # FÓRMULA DE MARKUP
        # Preço = (Custos + Lucro + TaxaFixa) / (1 - Taxa%)
        try:
            custo_total_base = custo_produto + custo_extra + lucro_desejado + taxa_fixa
            divisor = 1 - taxa_pct
            
            if divisor <= 0:
                st.error("Erro: As taxas são maiores que 100%. Impossível calcular.")
            else:
                preco_venda = custo_total_base / divisor
                
                # Exibição do Preço Ideal
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Venda na Shopee por:</div>
                    <div class="metric-value">R$ {preco_venda:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Prova Real (Breakdown)
                st.markdown("### 🔍 Para onde vai o dinheiro?")
                
                comissao_shopee = preco_venda * taxa_pct
                total_shopee = comissao_shopee + taxa_fixa
                custos_totais = custo_produto + custo_extra
                lucro_real = preco_venda - total_shopee - custos_totais
                
                df = pd.DataFrame({
                    "Destino": ["Shopee (Comissão + Taxa)", "Custo Produto + Emb.", "Seu Lucro Real"],
                    "Valor (R$)": [f"R$ {total_shopee:.2f}", f"R$ {custos_totais:.2f}", f"R$ {lucro_real:.2f}"]
                })
                st.table(df)
                
                if lucro_real < lucro_desejado - 0.05: # Margem de erro de arredondamento
                    st.warning("Atenção: Arredondamentos podem variar centavos.")
                else:
                    st.success(f"✅ Parabéns! Vendendo a R$ {preco_venda:.2f}, você garante seus R$ {lucro_desejado:.2f} de lucro.")

        except Exception as e:
            st.error("Preencha os valores para calcular.")
