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
    resposta = f"Zeus aqui! Sobre '{user_input}', posso te ajudar com dicas de treino, montar uma dieta ou resolver algo da faculdade!"

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
