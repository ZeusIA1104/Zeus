
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Zeus IA", layout="centered")

st.title("ZEUS — Inteligência Artificial para Treinos e Dietas")
st.caption("Seu assistente pessoal para ganhar massa muscular, perder gordura e organizar estudos.")

# Seção de Objetivo
st.header("1. Qual o seu objetivo principal?")
objetivo = st.radio("Escolha uma opção:", ["Perder gordura", "Ganhar massa muscular", "Manter forma física"])

# Dados do usuário
st.header("2. Informações pessoais")
col1, col2 = st.columns(2)
with col1:
    idade = st.number_input("Idade", min_value=10, max_value=80, value=19)
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=72.0)
with col2:
    altura = st.number_input("Altura (cm)", min_value=140, max_value=220, value=172)

# Cálculo de TMB (Taxa Metabólica Basal) simplificado
tmb = 10 * peso + 6.25 * altura - 5 * idade + 5  # Fórmula Mifflin-St Jeor para homens

st.write(f"**Sua TMB estimada:** {tmb:.2f} calorias/dia")

# Refeições do dia
st.header("3. Registro de Refeições")
refeicoes = st.text_area("Descreva o que você comeu hoje (Ex: 2 ovos, 150g arroz, etc)")

# Treino do dia
st.header("4. Registro de Treino")
tipo_treino = st.selectbox("Tipo de treino:", ["Peito", "Costas", "Pernas", "Cardio", "Descanso"])
duracao = st.slider("Duração do treino (minutos)", 0, 180, 40)
cardio_min = st.slider("Minutos de cardio (esteira, bike, corrida)", 0, 60, 12)

# Estimativa de gasto calórico com treino e cardio
gasto_treino = duracao * 8  # média 8 kcal/min
gasto_cardio = cardio_min * 10  # média 10 kcal/min

gasto_total = gasto_treino + gasto_cardio

st.success(f"Você gastou aproximadamente **{gasto_total} calorias** no treino de hoje.")

# Análise simples
if objetivo == "Perder gordura":
    meta = tmb - 300
    st.info(f"Para perder gordura, sua meta calórica diária seria por volta de **{meta:.0f} kcal**.")
elif objetivo == "Ganhar massa muscular":
    meta = tmb + 300
    st.info(f"Para ganhar massa muscular, sua meta calórica diária seria por volta de **{meta:.0f} kcal**.")
else:
    st.info(f"Para manter sua forma física, sua meta calórica diária seria por volta de **{tmb:.0f} kcal**.")

# Rodapé
st.markdown("---")
st.caption(f"Zeus IA - {datetime.now().year} | Desenvolvido com Streamlit")

