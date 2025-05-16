import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

def check_password():
    """Retorna `True` se o usuário acertar a senha."""
    
    def password_entered():
        """Verifica se a senha está correta."""
        if (st.session_state["username"] == "admin" and 
            st.session_state["password"] == "brasil02"):
            st.session_state["password_correct"] = True
            st.session_state["user"] = "admin"  # Armazena o usuário
            del st.session_state["password"]  # Remove a senha da memória
        else:
            st.session_state["password_correct"] = False
    
    # Mostra o formulário de login se não estiver logado
    if "password_correct" not in st.session_state:
        st.text_input("Usuário", key="username", on_change=password_entered)
        st.text_input("Senha", type="password", key="password", on_change=password_entered)
        st.error("😕 Usuário/senha incorretos" if "password_correct" in st.session_state and not st.session_state["password_correct"] else "")
        return False
    elif not st.session_state["password_correct"]:
        # Senha incorreta, mostra o formulário novamente
        st.text_input("Usuário", key="username", on_change=password_entered)
        st.text_input("Senha", type="password", key="password", on_change=password_entered)
        st.error("😕 Usuário/senha incorretos")
        return False
    else:
        # Usuário autenticado!
        return True

if not check_password():
    st.stop()  # Interrompe a execução se não estiver logado




# Configuração da página
st.set_page_config(page_title="Envio de Álbuns", layout="wide")

st.title("📦 SISTEMA DE CONTROLE DE ENVIO DE ÁLBUNS")
st.markdown("---")

# Conexão com banco SQLite
conn = sqlite3.connect("albuns_envios.db", check_same_thread=False)
c = conn.cursor()

# Criação da tabela (caso não exista) - REMOVIDO O CEP E ALTERADO LAM PARA LAMINAS
c.execute("""
CREATE TABLE IF NOT EXISTS envios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    os TEXT,
    nome TEXT,
    modelo TEXT,
    estojo TEXT,
    tamanho TEXT,
    laminas TEXT,   
    rastreio TEXT,
    turma TEXT,
    data_envio TEXT
)
""")

# ------------------- FORMULÁRIO -------------------
col1, col2, col3, col4 = st.columns([1.2, 2, 1.2, 1.2])
with col1:
    os = st.text_input("OS")
with col2:
    nome = st.text_input("Nome")
with col3:
    modelo = st.text_input("Modelo")
with col4:
    estojo = st.text_input("Estojo")

col5, col6, col7 = st.columns([1, 1, 2])  # Removida uma coluna (era o CEP)
with col5:
    tam = st.text_input("TAM.")
with col6:
    laminas = st.text_input("LÂMINAS")  # Alterado de LAM para LÂMINAS
with col7:
    rastreio = st.text_input("Código de Rastreamento")

col9 = st.columns(1)[0]
with col9:
    turma = st.text_input("Turma")

# Botão centralizado
st.markdown("<br>", unsafe_allow_html=True)
col_btn = st.columns([2, 1, 2])
with col_btn[1]:
    if st.button("✅ Cadastrar Envio"):
        if os and nome:
            data_envio = datetime.now().strftime("%Y-%m-%d")
            c.execute("""
                INSERT INTO envios (os, nome, modelo, estojo, tamanho, laminas, rastreio, turma, data_envio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (os, nome, modelo, estojo, tam, laminas, rastreio, turma, data_envio))
            conn.commit()
            st.success(f"Enviado com sucesso em {data_envio}!")
            st.rerun()
        else:
            st.warning("Por favor, preencha ao menos OS e Nome.")

st.markdown("---")

# ------------------- TABELA DE REGISTROS -------------------
st.subheader("📋 Envios cadastrados")

df = pd.read_sql_query("SELECT * FROM envios ORDER BY id DESC", conn)
st.dataframe(df, use_container_width=True)

# ------------------- GERAR RELATÓRIO POR DATA -------------------
st.markdown("---")
st.subheader("📅 Gerar Relatório por Data")

data_filtro = st.date_input("Selecione a data desejada para exportar")

if st.button("📤 Gerar Relatório Excel"):
    data_str = data_filtro.strftime("%Y-%m-%d")
    df_filtrado = pd.read_sql_query(
        "SELECT * FROM envios WHERE data_envio = ?", conn, params=(data_str,)
    )

    if df_filtrado.empty:
        st.warning("Nenhum envio encontrado para essa data.")
    else:
        # Criar Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Envios')
            writer.close()
            processed_data = output.getvalue()

        st.success(f"Relatório gerado com sucesso para {data_str}!")

        st.download_button(
            label="📥 Baixar Relatório Excel",
            data=processed_data,
            file_name=f"envios_{data_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
