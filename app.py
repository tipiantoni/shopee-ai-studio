import streamlit as st
import google.generativeai as genai
from PIL import Image
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
    .prompt-box {
        background-color: #262730;
        color: #ffffff;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #4e4e4e;
        font-family: monospace;
        margin-top: 10px;
    }
    .metric-card {
        background-color: #e0f7fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #b2ebf2;
        text-align: center;
        margin-bottom: 10px;
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
    
    # Lista de modelos para tentar
    modelos = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]
    
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
        except: continue
            
    # Fallback: Tenta listar da conta
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
        st.success("Cérebro Conectado", icon="✅")
    else:
        google_key = st.text_input("Cole sua Google API Key", type="password")

    st.divider()
    st.markdown("© 2025 **Ti Piantoni**")

# --- 6. NAVEGAÇÃO POR ABAS ---
tab1, tab2 = st.tabs(["🎨 Estúdio Criativo (IA)", "🧮 Calculadora de Preço (R$)"])

# ==========================================
# ABA 1: CRIAÇÃO DE CONTEÚDO (CÓDIGO ORIGINAL)
# ==========================================
with tab1:
    st.header("Gerador de Estratégia & Prompts")
    
    cenario = st.selectbox("Onde o produto será fotografado?", [
        "Fundo Infinito Branco (E-commerce Padrão)", 
        "Cozinha Gourmet Moderna (High End)",
        "Banheiro de Luxo em Mármore (Spa Vibe)", 
        "Sala de Estar Aconchegante (Lifestyle)", 
        "Ao Ar Livre / Natureza (Golden Hour)", 
        "Mesa de Escritório Minimalista (Productivity)",
        "Estúdio Neon Cyberpunk (Gamer/Tech)"
    ])
    st.info("💡 Dica: O prompt gerado aqui deve ser usado no Midjourney, Leonardo.ai ou Bing.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Seu Produto")
        uploaded_file = st.file_uploader("Arraste a foto do fornecedor", type=["jpg", "png", "jpeg", "webp"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Referência", use_column_width=True)
            btn_gerar = st.button("🚀 Gerar Estratégia + Prompt Master", type="primary", use_container_width=True)

    if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
        if not google_key:
            st.error("⚠️ Você precisa colocar a chave do Google na barra lateral.")
        else:
            with col2:
                st.subheader("2. Estratégia IA")
                with st.spinner("🧠 Analisando texturas, luz e mercado..."):
                    try:
                        full_response = get_ai_strategy(google_key, image, cenario)
                        
                        if "---DIVISOR---" in full_response:
                            parts = full_response.split("---DIVISOR---")
                            copy_shopee = parts[0].strip()
                            prompt_img = parts[1].strip().replace("SAÍDA 2: PROMPT MASTER DE IMAGEM (Em Inglês)", "").strip()
                        else:
                            copy_shopee = full_response
                            prompt_img = "Erro ao separar o prompt."

                        # EXIBIÇÃO DA COPY
                        st.markdown(copy_shopee)
                        st.divider()
                        
                        # EXIBIÇÃO DO PROMPT
                        st.subheader("🎨 Seu Prompt Gerador de Imagens")
                        st.markdown("Copie o código abaixo e cole na sua IA de imagem preferida:")
                        st.code(prompt_img, language="text")
                        st.success("Sucesso!")
                        
                    except Exception as e:
                        st.error(f"Ocorreu um erro: {e}")

# ==========================================
# ABA 2: CALCULADORA DE PRECIFICAÇÃO
# ==========================================
with tab2:
    st.header("🧮 Calculadora de Lucro Real (Shopee)")
    st.markdown("Descubra o **Preço de Venda** exato para garantir o lucro que você deseja.")
    
    c_calc1, c_calc2 = st.columns(2)
    
    with c_calc1:
        st.subheader("Custos & Metas")
        custo_produto = st.number_input("Custo do Produto (R$)", value=0.00, step=1.00, help="Quanto você paga no fornecedor?")
        custo_extra = st.number_input("Embalagem/Impostos (R$)", value=2.00, step=0.50, help="Caixa, fita, etiqueta, brinde.")
        lucro_desejado = st.number_input("Lucro Desejado LIMPO (R$)", value=15.00, step=1.00, help="Quanto você quer no bolso?")
        
        st.divider()
        st.subheader("Taxas da Shopee")
        programa_frete = st.checkbox("Participo do Frete Grátis Extra (+6%)", value=True)
        
        if programa_frete:
            taxa_pct = 0.20 # 20%
        else:
            taxa_pct = 0.14 # 14%
            
        taxa_fixa = 4.00 # Taxa fixa
        st.caption(f"Taxa Shopee: {taxa_pct*100:.0f}% + R$ {taxa_fixa:.2f} por item.")

    with c_calc2:
        st.subheader("Resultado")
        try:
            # FÓRMULA DE MARKUP REVERSO
            # Preço = (Custos + Lucro + TaxaFixa) / (1 - %Comissão)
            custo_total_base = custo_produto + custo_extra + lucro_desejado + taxa_fixa
            divisor = 1 - taxa_pct
            
            if divisor <= 0:
                st.error("Erro: Taxas inviáveis (>100%).")
            else:
                preco_venda = custo_total_base / divisor
                
                # Exibe o preço grande
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Venda na Shopee por:</div>
                    <div class="metric-value">R$ {preco_venda:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Tabela de Detalhamento
                st.markdown("### 🔍 Para onde vai o dinheiro?")
                comissao_shopee = preco_venda * taxa_pct
                total_shopee = comissao_shopee + taxa_fixa
                custos_totais = custo_produto + custo_extra
                lucro_real = preco_venda - total_shopee - custos_totais
                
                df = pd.DataFrame({
                    "Destino": ["Shopee (Comissão + Taxa)", "Seus Custos (Prod + Emb)", "Seu Lucro Real"],
                    "Valor (R$)": [f"R$ {total_shopee:.2f}", f"R$ {custos_totais:.2f}", f"R$ {lucro_real:.2f}"]
                })
                st.table(df)
        except:
            st.error("Verifique os valores.")
