import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import requests
import io
import time
import random
import urllib.parse
import re
import os
from datetime import datetime

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
    /* Esconde traceback de erro */
    .stException { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO ---
st.markdown("""
<div class="branding-box">
    <div class="branding-title">🚀 Shopee AI Studio</div>
    <div class="branding-subtitle">Ferramenta desenvolvida por <b>Ti Piantoni</b> | Especialista em IA & Automação</div>
</div>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DO SISTEMA ---

# ARQUIVO DE HISTÓRICO
HISTORY_FILE = 'historico_jobs.csv'

def salvar_no_historico(nome_arquivo, cenario, copy, prompt):
    """Salva o trabalho atual no CSV."""
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    novo_dado = {
        "Data": [data_hoje],
        "Arquivo Original": [nome_arquivo],
        "Cenário": [cenario],
        "Copy Gerada": [copy],
        "Prompt Imagem": [prompt]
    }
    
    df_novo = pd.DataFrame(novo_dado)
    
    if os.path.exists(HISTORY_FILE):
        df_antigo = pd.read_csv(HISTORY_FILE)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
    else:
        df_final = df_novo
        
    df_final.to_csv(HISTORY_FILE, index=False)

def carregar_historico():
    """Lê o CSV para exibir na tela."""
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    return pd.DataFrame()

def sanitize_prompt(text):
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return cleaned[:100]

def generate_image_pollinations_safe(prompt):
    try:
        prompt_safe = sanitize_prompt(prompt)
        prompt_encoded = urllib.parse.quote(prompt_safe)
        seed = random.randint(1, 99999)
        image_url = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        
        response = requests.get(image_url, headers=headers, timeout=20)
        if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
            return response.content
        return None
    except:
        return None

def get_ai_strategy(api_key, image, cenario, observacoes=""):
    genai.configure(api_key=api_key)
    texto_extra = f"OBSERVAÇÕES: {observacoes}" if observacoes else ""
    
    prompt_sistema = f"""
    Você é um especialista em E-commerce.
    1. ANALISE A IMAGEM.
    2. CONSIDERE: {texto_extra}
    3. CENÁRIO: {cenario}.
    
    GERE DUAS SAÍDAS:
    SAÍDA 1: COPY SHOPEE (Título SEO, Descrição AIDA, 5 Bullets).
    SAÍDA 2: PROMPT MASTER DE IMAGEM (Em Inglês, visual, detalhado).
    Separe as saídas com a tag: ---DIVISOR---
    """
    
    # Tentativa de modelos
    modelos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    for m in modelos:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content([prompt_sistema, image])
            return response.text
        except: continue
    
    # Fallback listagem
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                try:
                    model = genai.GenerativeModel(m.name)
                    response = model.generate_content([prompt_sistema, image])
                    return response.text
                except: continue
    except: pass
    
    raise Exception("Erro Google AI.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Configuração")
    if "GOOGLE_API_KEY" in st.secrets:
        google_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Google AI Conectado", icon="✅")
    else:
        google_key = st.text_input("Google API Key", type="password")

    st.divider()
    st.markdown("© 2025 **Ti Piantoni**")

# --- 6. NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["🎨 Estúdio (IA)", "🧮 Calculadora", "📜 Histórico"])

# ==========================================
# ABA 1: CRIAÇÃO
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Produto")
        uploaded_file = st.file_uploader("Foto do produto", type=["jpg", "png", "jpeg"])
        observacoes = st.text_area("Detalhes (Opcional)", placeholder="Ex: Molho caseiro, apimentado...")
        cenario = st.selectbox("Cenário", ["Fundo Branco", "Cozinha Gourmet", "Mesa de Jantar", "Ao Ar Livre", "Estúdio Minimalista"])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Referência", use_column_width=True)
            btn_gerar = st.button("🚀 Gerar Criativos", type="primary", use_container_width=True)

    if uploaded_file and 'btn_gerar' in locals() and btn_gerar:
        if not google_key:
            st.error("Coloque a chave API.")
        else:
            with col2:
                st.subheader("2. Resultado")
                with st.spinner("🧠 Criando estratégia..."):
                    try:
                        full_response = get_ai_strategy(google_key, image, cenario, observacoes)
                        
                        if "---DIVISOR---" in full_response:
                            parts = full_response.split("---DIVISOR---")
                            copy_shopee = parts[0].strip()
                            prompt_img = parts[1].strip().replace("SAÍDA 2: PROMPT MASTER DE IMAGEM (Em Inglês)", "").strip()
                        else:
                            copy_shopee = full_response
                            prompt_img = "Erro parsing."

                        # EXIBE COPY
                        st.markdown(copy_shopee)
                        st.divider()
                        
                        # EXIBE PROMPT
                        st.code(prompt_img, language="text")
                        
                        # GERA IMAGEM (1 Exemplo rápido)
                        st.caption("Prévia da Imagem:")
                        img_bytes = generate_image_pollinations_safe(prompt_img)
                        if img_bytes:
                            st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
                        
                        # SALVA NO HISTÓRICO AUTOMATICAMENTE
                        salvar_no_historico(uploaded_file.name, cenario, copy_shopee, prompt_img)
                        st.toast("Salvo no Histórico!", icon="💾")
                        st.success("Sucesso!")
                        
                    except Exception as e:
                        st.error(f"Erro: {e}")

# ==========================================
# ABA 2: CALCULADORA
# ==========================================
with tab2:
    st.header("🧮 Calculadora Shopee")
    c1, c2 = st.columns(2)
    with c1:
        custo_prod = st.number_input("Custo Produto (R$)", 0.0, step=1.0)
        custo_extra = st.number_input("Embalagem (R$)", 2.0, step=0.5)
        lucro = st.number_input("Lucro Limpo (R$)", 15.0, step=1.0)
        frete_extra = st.checkbox("Frete Grátis Extra (+6%)", True)
    with c2:
        taxa = 0.20 if frete_extra else 0.14
        fixo = 4.00
        try:
            total_base = custo_prod + custo_extra + lucro + fixo
            preco = total_base / (1 - taxa)
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Venda por:</div><div class="metric-value">R$ {preco:.2f}</div></div>""", unsafe_allow_html=True)
            
            df = pd.DataFrame({
                "Item": ["Shopee", "Custos", "Lucro"],
                "Valor": [f"R$ {(preco*taxa)+fixo:.2f}", f"R$ {custo_prod+custo_extra:.2f}", f"R$ {preco - ((preco*taxa)+fixo) - (custo_prod+custo_extra):.2f}"]
            })
            st.table(df)
        except: st.error("Erro cálculo")

# ==========================================
# ABA 3: HISTÓRICO
# ==========================================
with tab3:
    st.header("📜 Histórico de Jobs")
    st.markdown("Aqui ficam salvos todos os produtos que você já gerou.")
    
    df_history = carregar_historico()
    
    if not df_history.empty:
        # Mostra os dados mais recentes primeiro
        df_history = df_history.iloc[::-1]
        
        st.dataframe(df_history, use_container_width=True)
        
        # Botão de Download
        csv = df_history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Planilha (Excel/CSV)",
            data=csv,
            file_name='shopee_studio_historico.csv',
            mime='text/csv',
        )
        
        if st.button("🗑️ Limpar Histórico Completo"):
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
                st.rerun()
    else:
        st.info("Nenhum job salvo ainda. Gere seu primeiro criativo na aba 'Estúdio'!")
