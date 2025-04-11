import streamlit as st

# Configuração da página
st.set_page_config(page_title="Zeus IA", layout="centered")

# Título do app
st.title("Zeus - Seu treinador inteligente")
st.markdown("Fale comigo sobre *treinos, **alimentação* ou *dúvidas da faculdade de Administração*!")

# Campo de entrada do usuário
user_input = st.text_input("Digite sua pergunta para o Zeus:")

# Função para gerar treinos de acordo com o músculo solicitado
def gerar_treino(resposta_usuario):
    if "peito" in resposta_usuario.lower():
        return (
            "Treino de Peito:\n"
            "- Supino reto: 4x10\n"
            "- Supino inclinado: 4x10\n"
            "- Crossover: 3x12\n"
            "- Flexão: 3x15"
        )
    elif "perna" in resposta_usuario.lower():
        return (
            "Treino de Perna:\n"
            "- Agachamento livre: 4x12\n"
            "- Leg press: 4x10\n"
            "- Cadeira extensora: 3x12\n"
            "- Stiff: 3x10"
        )
    elif "costas" in resposta_usuario.lower():
        return (
            "Treino de Costas:\n"
            "- Puxada frontal: 4x10\n"
            "- Remada curvada: 4x10\n"
            "- Pulldown: 3x12\n"
            "- Remada baixa: 3x12"
        )
    elif "bíceps" in resposta_usuario.lower():
        return (
            "Treino de Bíceps:\n"
            "- Rosca direta: 4x12\n"
            "- Rosca alternada: 4x10\n"
            "- Rosca martelo: 3x12"
        )
    elif "tríceps" in resposta_usuario.lower():
        return (
            "Treino de Tríceps:\n"
            "- Tríceps pulley: 4x12\n"
            "- Tríceps testa: 4x10\n"
            "- Tríceps banco: 3x15"
        )
    else:
        return "Ainda não entendi seu pedido. Tente algo como: 'Me passe um treino de peito'."

# Resposta do Zeus
if user_input:
    resposta = gerar_treino(user_input)
    st.markdown(f"*Zeus:* {resposta}")
