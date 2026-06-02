import streamlit as st
import pandas as pd
import gspread

# Configuração da página
st.set_page_config(page_title="Painel Administrativo", layout="wide")

# --- CONEXÃO COM PLANILHA ---
def get_data(aba):
    try:
        gc = gspread.service_account(filename='credenciais.json')
        sh = gc.open("SistemaAprovacoes")
        worksheet = sh.worksheet(aba)
        dados = worksheet.get_all_records(head=1)
        return pd.DataFrame(dados) if dados else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao conectar com a aba '{aba}': {e}")
        return pd.DataFrame()

# Simulação de usuários online (Substitua pela lógica do seu DB no futuro)
def get_online_users():
    return [
        {"nome": "Admin", "status": "orange"},
        {"nome": "Membro Ativo", "status": "red"},
        {"nome": "Membro Ausente", "status": "white"}
    ]

# --- INICIALIZAÇÃO DE SESSÃO ---
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.mensagens = []
    st.session_state.perfil = {"foto": "👤", "efeito": "Normal"}
    st.session_state.cargo = "Membro"
    st.session_state.emo_clicado = ""

# --- LOGIN ---
if not st.session_state.user:
    st.title("🔐 Login Administrativo")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin":
            st.session_state.user = "Admin"
            st.session_state.cargo = "Resp"
            st.rerun()
        else:
            st.error("Credenciais incorretas.")
    st.stop()

# --- CSS CUSTOMIZADO (Visual Xat) ---
st.markdown("""
    <style>
    /* Remover bordas e fundo dos botões de emoji */
    .stButton > button {
        background-color: transparent !important;
        border: none !important;
        font-size: 30px !important; /* Emojis maiores */
        padding: 0px !important;
        width: 40px !important;
        height: 40px !important;
        transition: transform 0.2s;
    }
    .stButton > button:hover { transform: scale(1.2); }
    
    /* Ajuste do layout de chat */
    [data-testid="stChatMessage"] { background-color: transparent !important; border-bottom: 1px solid #333; padding: 5px 0px; }
    [data-testid="stChatMessageAvatarUser"] { display: none; }
    
    /* Status dots */
    .status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL ---
st.sidebar.write(f"👤 **{st.session_state.user}**")
st.sidebar.write(f"💼 {st.session_state.cargo}")
menu = st.sidebar.radio("Navegação", ["Chat Online", "Dashboard (Registros)", "Gerenciar Membros", "Meu Perfil"])

if st.sidebar.button("Sair"):
    st.session_state.user = None
    st.rerun()

# --- ABAS E FUNCIONALIDADES ---

if menu == "Dashboard (Registros)":
    st.title("📊 Registros")
    df = get_data("Folha1")
    if not df.empty: st.dataframe(df, use_container_width=True)
    else: st.info("Planilha vazia.")

elif menu == "Gerenciar Membros":
    st.title("👥 Gerenciar Equipe")
    with st.form("cadastrar"):
        st.text_input("Novo Usuário"); st.text_input("Senha", type="password")
        if st.form_submit_button("Adicionar"): st.success("Processado.")

elif menu == "Meu Perfil":
    st.title("⚙️ Customizar Perfil")
    uploaded_file = st.file_uploader("Sua foto", type=['png', 'jpg'])
    if uploaded_file: st.session_state.perfil["foto"] = uploaded_file.getvalue()
    st.success("Salvo.")

elif menu == "Chat Online":
    st.title("💬 Chat da Equipe")
    col_chat, col_users = st.columns([0.75, 0.25])

    with col_chat:
        container = st.container(height=350)
        with container:
            for msg in st.session_state.mensagens:
                st.markdown(f"**{msg['usuario']}**: {msg['texto']}")
        
        # Barra de Emojis Sem Caixinha
        st.markdown("---")
        emojis = ["😀", "👍", "🚀", "🔥", "✅", "💡", "💬", "😎", "😂", "😢"]
        
        # Criando colunas estreitas para os emojis ficarem próximos
        cols = st.columns(len(emojis))
        for i, emo in enumerate(emojis):
            if cols[i].button(emo, key=f"e_{i}"):
                st.session_state.emo_clicado = emo
        
        texto = st.chat_input("Digite sua mensagem...")
        
        if texto or st.session_state.emo_clicado:
            texto_final = (texto if texto else "") + st.session_state.emo_clicado
            st.session_state.mensagens.append({
                "usuario": st.session_state.user, 
                "texto": texto_final
            })
            st.session_state.emo_clicado = ""
            st.rerun()

    with col_users:
        st.subheader("👥 Online")
        # Renderiza a lista dinâmica
        usuarios = get_online_users()
        for u in usuarios:
            st.markdown(f'<span class="status-dot" style="background-color: {u["status"]};"></span> {u["nome"]}', unsafe_allow_html=True)