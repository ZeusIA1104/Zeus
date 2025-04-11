import streamlit as st
import pandas as pd

st.set_page_config(page_title="Zeus IA", layout="centered")

st.title("Zeus - Seu Assistente de Treino e Nutrição")

menu = st.sidebar.selectbox("Escolha uma opção", [
    "Início",
    "Calcular IMC",
    "Montar Treino",
    "Montar Dieta",
    "Dicas de Suplementos",
    "Receitas Fitness"
])

def calcular_imc():
    st.header("Calculadora de IMC")
    peso = st.number_input("Informe seu peso (kg)", min_value=30.0, max_value=200.0)
    altura = st.number_input("Informe sua altura (m)", min_value=1.0, max_value=2.5)

    if peso and altura:
        imc = peso / (altura ** 2)
        st.write(f"Seu IMC é: *{imc:.2f}*")
        if imc < 18.5:
            st.warning("Abaixo do peso")
        elif 18.5 <= imc < 25:
            st.success("Peso normal")
        elif 25 <= imc < 30:
            st.warning("Sobrepeso")
        else:
            st.error("Obesidade")

def montar_treino():
    st.header("Monte seu Treino")
    objetivo = st.selectbox("Qual seu objetivo?", ["Hipertrofia", "Definição", "Resistência"])
    nivel = st.selectbox("Qual seu nível?", ["Iniciante", "Intermediário", "Avançado"])

    if st.button("Gerar Treino"):
        if objetivo == "Hipertrofia":
            st.subheader("Treino para Hipertrofia")
            if nivel == "Iniciante":
                st.write("- Supino reto 3x10\n- Remada curvada 3x10\n- Agachamento 3x12")
            elif nivel == "Intermediário":
                st.write("- Supino inclinado 4x8\n- Puxada frente 4x10\n- Leg press 4x12")
            else:
                st.write("- Crucifixo máquina 4x10\n- Pull-up 4x12\n- Agachamento livre 4x10")

        elif objetivo == "Definição":
            st.subheader("Treino para Definição")
            st.write("- Circuito com 30s por exercício\n- Baixo tempo de descanso\n- Cardio pós treino")

        elif objetivo == "Resistência":
            st.subheader("Treino para Resistência")
            st.write("- Treino funcional\n- Exercícios com peso corporal\n- Corrida ou bike")

def montar_dieta():
    st.header("Montar Dieta")
    genero = st.selectbox("Gênero", ["Masculino", "Feminino"])
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0)
    objetivo = st.selectbox("Objetivo", ["Emagrecimento", "Hipertrofia", "Ganho de Massa Muscular"])

    if st.button("Gerar Dieta"):
        st.subheader(f"Dieta para {objetivo}")
        if objetivo == "Emagrecimento":
            calorias = peso * 22
        elif objetivo == "Hipertrofia":
            calorias = peso * 35
        else:
            calorias = peso * 32

        st.write(f"Calorias diárias estimadas: *{calorias:.0f} kcal*")

        st.write("Exemplo de Refeições:")
        st.write("- Café da manhã: ovos mexidos com aveia e fruta")
        st.write("- Almoço: arroz, feijão, frango grelhado e salada")
        st.write("- Jantar: batata doce, carne magra e legumes")

def dicas_suplementos():
    st.header("Dicas de Suplementos")
    objetivo = st.selectbox("Objetivo", ["Hipertrofia", "Emagrecimento", "Energia", "Saúde Geral"])

    if objetivo == "Hipertrofia":
        st.write("- Whey Protein\n- Creatina\n- BCAA\n- Albumina")
    elif objetivo == "Emagrecimento":
        st.write("- Termogênicos\n- L-carnitina\n- Cafeína")
    elif objetivo == "Energia":
        st.write("- Pré-treino\n- Cafeína\n- Taurina")
    else:
        st.write("- Multivitamínico\n- Ômega 3\n- Vitamina D")

def receitas_fitness():
    st.header("Receitas Fitness")
    st.write("1. Panqueca de banana com aveia\n2. Frango grelhado com legumes\n3. Bowl de salada com ovo e grão-de-bico")
    st.write("4. Shake de whey com frutas\n5. Omelete de claras com espinafre")

# Roteamento
if menu == "Início":
    st.write("Bem-vindo ao Zeus, sua inteligência artificial para treinos, dietas e saúde!")
elif menu == "Calcular IMC":
    calcular_imc()
elif menu == "Montar Treino":
    montar_treino()
elif menu == "Montar Dieta":
    montar_dieta()
elif menu == "Dicas de Suplementos":
    dicas_suplementos()
elif menu == "Receitas Fitness":
    receitas_fitness()
