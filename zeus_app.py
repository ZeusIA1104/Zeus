import streamlit as st

# Título do app
st.title("Zeus - Seu Personal Trainer Virtual")

# Menu principal
menu = st.sidebar.selectbox("Escolha uma opção", [
    "Calculadora de IMC",
    "Montar Treino",
    "Montar Dieta",
    "Suplementos e Receitas"
])

# Função de cálculo de IMC
def calcular_imc(peso, altura):
    imc = peso / (altura ** 2)
    if imc < 18.5:
        return imc, "Abaixo do peso"
    elif imc < 25:
        return imc, "Peso normal"
    elif imc < 30:
        return imc, "Sobrepeso"
    else:
        return imc, "Obesidade"

# Página 1 - IMC
if menu == "Calculadora de IMC":
    st.header("Cálculo de IMC")
    peso = st.number_input("Informe seu peso (kg)", min_value=30.0, max_value=200.0)
    altura = st.number_input("Informe sua altura (m)", min_value=1.0, max_value=2.5)
    if st.button("Calcular IMC"):
        imc, classificacao = calcular_imc(peso, altura)
        st.success(f"Seu IMC é {imc:.2f} - {classificacao}")

# Página 2 - Treinos
elif menu == "Montar Treino":
    st.header("Montar Treino")
    objetivo = st.selectbox("Qual seu objetivo?", ["Hipertrofia", "Definição", "Resistência"])
    nivel = st.selectbox("Qual seu nível de treino?", ["Iniciante", "Intermediário", "Avançado"])
    
    if st.button("Gerar Treino"):
        if objetivo == "Hipertrofia":
            treino = {
                "Peito": ["Supino Reto", "Supino Inclinado", "Crossover"],
                "Costas": ["Puxada Aberta", "Remada Curvada", "Levantamento Terra"],
                "Pernas": ["Agachamento Livre", "Leg Press", "Cadeira Extensora"]
            }
        elif objetivo == "Definição":
            treino = {
                "Circuito Fullbody": ["Flexão", "Agachamento", "Burpee", "Abdominal", "Corrida leve 10min"]
            }
        else:
            treino = {
                "Funcional": ["Corrida", "Pliometria", "Battle Rope", "Box Jump"]
            }
        for grupo, exercicios in treino.items():
            st.subheader(grupo)
            for ex in exercicios:
                st.write(f"- {ex}")

# Página 3 - Dietas
elif menu == "Montar Dieta":
    st.header("Montar Dieta Personalizada")
    objetivo_dieta = st.selectbox("Objetivo da dieta", ["Emagrecimento", "Hipertrofia", "Manutenção"])
    genero = st.radio("Gênero", ["Masculino", "Feminino"])
    peso = st.number_input("Peso atual (kg)", min_value=30.0, max_value=200.0)
    altura = st.number_input("Altura (m)", min_value=1.0, max_value=2.5)
    idade = st.number_input("Idade", min_value=10, max_value=100)

    if st.button("Gerar Dieta"):
        calorias_base = (10 * peso + 6.25 * (altura * 100) - 5 * idade + (5 if genero == "Masculino" else -161))
        if objetivo_dieta == "Emagrecimento":
            calorias = calorias_base - 500
        elif objetivo_dieta == "Hipertrofia":
            calorias = calorias_base + 400
        else:
            calorias = calorias_base

        st.success(f"Recomendação calórica diária: {int(calorias)} kcal")
        st.subheader("Dieta exemplo:")
        st.write("- Café da manhã: 2 ovos, 1 banana, aveia, 1 scoop de whey")
        st.write("- Almoço: 150g arroz, 150g frango, salada à vontade")
        st.write("- Lanche: 1 iogurte natural + castanhas")
        st.write("- Jantar: Omelete com legumes ou shake de proteína")

# Página 4 - Suplementos e Receitas
elif menu == "Suplementos e Receitas":
    st.header("Suplementos e Receitas")
    tipo_info = st.radio("O que deseja ver?", ["Suplementos", "Receitas saudáveis"])
    
    if tipo_info == "Suplementos":
        st.subheader("Suplementos recomendados:")
        st.write("- Whey Protein: reconstrução muscular")
        st.write("- Creatina: força e desempenho")
        st.write("- Cafeína: energia e foco")
        st.write("- Multivitamínico: suporte geral")
    else:
        st.subheader("Receitas Fit:")
        st.write("1. Panqueca de banana e aveia")
        st.write("2. Shake de proteína com morango")
        st.write("3. Omelete com legumes e frango")
