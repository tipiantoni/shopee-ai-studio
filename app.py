import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
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

# --- 4. CÉREBRO DA IA (GOOGLE) ---
def get_ai_strategy(api_key, image, cenario):
    genai.configure(api_key=api_key)
    
    # LISTAS DE VARIAÇÃO ALEATÓRIA (O Segredo do Dinamismo)
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
    st.markdown("© 2025 **Ti Piantoni**")

# --- 6. NAVEGAÇÃO (ABAS) ---
tab1, tab2 = st.tabs(["🎨 Estúdio Criativo (IA)", "🧮 Calculadora de Preço (R$)"])

# ==================================================
# ABA 1: ESTÚDIO CRIATIVO (Seu código original)
# ==================================================
with tab1:
    st.header("Gerador de Prompts Dinâmicos")
    
    # Coloquei o seletor de cenário aqui dentro para organizar
    cenario = st.selectbox("Cenário Base", [
        "Fundo Infinito Branco", 
        "Cozinha Gourmet Moderna",
        "Banheiro de Luxo em Mármore", 
        "Sala de Estar Aconchegante", 
        "Ao Ar Livre / Natureza", 
        "Mesa de Escritório Minimalista",
        "Estúdio Neon High-Tech"
    ])
    st.caption("ℹ️ Cada clique gera um prompt com Luz e Ângulo diferentes automaticamente.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Seu Produto")
        uploaded_file = st.file_uploader("Arraste a foto do fornecedor", type=["jpg", "png", "jpeg", "webp"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Referência", use_column_width=True)
            btn_gerar = st.button("🎲 Gerar Prompt Dinâmico", type="primary", use_container_width=True)

    # Lógica de processamento
    if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
        if not google_key:
            st.error("⚠️ Falta a chave do Google na barra lateral.")
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
                        
                        # Mostra os detalhes sorteados
                        st.caption(f"✨ Variação Automática: **{luz}** | **{angulo}**")
                        
                        st.subheader("🎨 Seu Prompt Mestre")
                        st.markdown("Use este prompt no Midjourney, Flux ou Leonardo.ai:")
                        st.code(prompt_img, language="text")
                        
                        st.success("Pronto! Copie e crie sua imagem.")
                        
                    except Exception as e:
                        st.error(f"Erro: {e}")

# ==================================================
# ABA 2: CALCULADORA DE PREÇO
# ==================================================
with tab2:
    st.header("🧮 Calculadora de Lucro Real (Shopee)")
    st.markdown("Descubra o **Preço de Venda** exato para garantir o lucro que você deseja.")
    
    c_calc1, c_calc2 = st.columns(2)
    
    with c_calc1:
        st.subheader("Custos & Metas")
        custo_produto = st.number_input("Custo do Produto (R$)", value=0.00, step=1.00, help="Quanto você paga no fornecedor?")
        custo_extra = st.number_input("Embalagem/Impostos (R$)", value=2.00, step=0.50)
        lucro_desejado = st.number_input("Lucro Desejado LIMPO (R$)", value=15.00, step=1.00)
        
        st.divider()
        st.subheader("Taxas da Shopee")
        programa_frete = st.checkbox("Participo do Frete Grátis Extra (+6%)", value=True)
        
        if programa_frete:
            taxa_pct = 0.20 # 20%
        else:
            taxa_pct = 0.14 # 14%
            
        taxa_fixa = 4.00 # Taxa fixa por item
        st.caption(f"Taxa Shopee: {taxa_pct*100:.0f}% + R$ {taxa_fixa:.2f}")

    with c_calc2:
        st.subheader("Resultado")
        
        # FÓRMULA DE MARKUP
        try:
            custo_total_base = custo_produto + custo_extra + lucro_desejado + taxa_fixa
            divisor = 1 - taxa_pct
            
            if divisor <= 0:
                st.error("Erro: Taxas inviáveis.")
            else:
                preco_venda = custo_total_base / divisor
                
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
                    "Destino": ["Shopee (Taxas)", "Seus Custos", "Seu Lucro Real"],
                    "Valor (R$)": [f"R$ {total_shopee:.2f}", f"R$ {custos_totais:.2f}", f"R$ {lucro_real:.2f}"]
                })
                st.table(df)
        except:
            st.error("Verifique os valores.")
