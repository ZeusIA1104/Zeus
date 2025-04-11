import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Zeus - Inteligência Artificial", layout="centered")

st.title("Zeus - Sua IA de Treinos, Dieta e Produtividade")

st.markdown("### O que você quer que o Zeus faça hoje?")
opcao = st.selectbox("Escolha uma opção:", ["Montar treino", "Montar dieta", "Gerar gráficos", "Ajudar com trabalhos da faculdade"])

if opcao == "Montar treino":
    objetivo = st.radio("Qual seu objetivo?", ["Hipertrofia", "Emagrecimento", "Resistência"])
    dias = st.slider("Quantos dias por semana você treina?", 1, 7, 4)
    st.success(f"Beleza! Vou montar um treino de {dias} dias focado em {objetivo.lower()}.")

elif opcao == "Montar dieta":
    peso = st.number_input("Seu peso atual (kg):", 40.0, 200.0, 70.0)
    objetivo_dieta = st.radio("Objetivo da dieta:", ["Perder gordura", "Ganhar massa", "Manter peso"])
    calorias = 0
    if objetivo_dieta == "Perder gordura":
        calorias = peso * 22
    elif objetivo_dieta == "Ganhar massa":
        calorias = peso * 35
    else:
        calorias = peso * 30
    st.info(f"Recomendação calórica diária aproximada: *{int(calorias)} kcal*")

elif opcao == "Gerar gráficos":
    st.subheader("Gráfico de evolução de peso")
    pesos = st.text_area("Insira seus pesos separados por vírgula (ex: 72, 71.5, 70.8):")
    if pesos:
        lista_pesos = [float(p.strip()) for p in pesos.split(",")]
        plt.plot(lista_pesos, marker="o")
        plt.xlabel("Semana")
        plt.ylabel("Peso (kg)")
        plt.title("Evolução de Peso")
        st.pyplot(plt)

elif opcao == "Ajudar com trabalhos da faculdade":
    tema = st.text_input("Qual o tema do trabalho?")
    if tema:
        st.write(f"Legal! Posso te ajudar com ideias, estrutura, ou até escrever um rascunho sobre *{tema}*.")
