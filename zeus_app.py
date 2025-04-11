import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Zeus - Seu Coach IA", layout="centered")

st.title("Zeus - Seu Coach Pessoal")

st.markdown("Fale comigo sobre treinos, alimentação ou faculdade!")

# Histórico de conversa
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Entrada do usuário
user_input = st.text_input("Você:", key="user_input")

if user_input:
    # Resposta simulada (depois a gente liga com uma IA real)
    def gerar_treino(resposta_usuario):
    if "peito" in resposta_usuario.lower():
        return "Treino de Peito:\n- Supino reto: 4x10\n- Supino inclinado: 4x10\n- Crossover: 3x12\n- Flexão: 3x15"
    elif "perna" in resposta_usuario.lower():
        return "Treino de Perna:\n- Agachamento livre: 4x12\n- Leg press: 4x10\n- Cadeira extensora: 3x12\n- Stiff: 3x10"
    elif "costas" in resposta_usuario.lower():
        return "Treino de Costas:\n- Puxada frontal: 4x10\n- Remada curvada: 4x10\n- Pulldown: 3x12\n- Remada baixa: 3x12"
    elif "bíceps" in resposta_usuario.lower():
        return "Treino de Bíceps:\n- Rosca direta: 4x12\n- Rosca alternada: 4x10\n- Rosca martelo: 3x12"
    elif "tríceps" in resposta_usuario.lower():
        return "Treino de Tríceps:\n- Tríceps pulley: 4x12\n- Tríceps testa: 4x10\n- Tríceps banco: 3x15"
    else:
        return "Ainda não entendi seu pedido, tente dizer por exemplo: 'me passe um treino de peito'."

resposta = gerar_treino(user_input)

    # Armazena no histórico
    st.session_state.chat_history.append(("Você", user_input))
    st.session_state.chat_history.append(("Zeus", resposta))

# Exibe o histórico
for autor, mensagem in st.session_state.chat_history:
    if autor == "Você":
        st.markdown(f"*{autor}:* {mensagem}")
    else:
        st.markdown(f"*{autor}:* {mensagem}")

st.markdown("---")
st.caption(f"Powered by Zeus - {datetime.now().year}")
