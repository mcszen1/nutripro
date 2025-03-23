import streamlit as st
from openai import OpenAI
import os
import io
from docx import Document
from docx.shared import Pt

# ========== CONFIGURAÇÃO DA API ==========
api_key_env = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="NutriChef Pro", page_icon="🥦")
st.image("NIDUp.png", width=250, caption="Núcleo de Inteligência de Dados")

st.title("🥦 NutriChef Pro – Receita inteligente com IA")

if not api_key_env:
    st.warning("🔐 Sua chave da OpenAI não foi encontrada no ambiente.")
    api_key_input = st.text_input("Insira sua chave da OpenAI aqui para continuar:", type="password")
    if not api_key_input:
        st.stop()
    client = OpenAI(api_key=api_key_input)
else:
    client = OpenAI(api_key=api_key_env)

st.markdown("**Preencha o formulário para receber sua receita personalizada!**")

# ========== FORMULÁRIO ==========
with st.form("form_receita"):
    nome = st.text_input("Seu nome (opcional)", "")
    objetivo = st.selectbox("Objetivo principal:", ["Hipertrofia", "Cutting", "Endurance", "Manutenção"])
    fase = st.selectbox("Fase do treino:", ["Bulk", "Definição", "Manutenção", "Não sei"])
    dieta = st.selectbox("Estilo alimentar:", ["Tradicional", "Low-carb", "Vegana", "Vegetariana", "Outra"])
    restricoes = st.multiselect("Restrições alimentares:", ["Sem lactose", "Sem glúten", "Não consumo ovos", "Nenhuma"])

    equipamentos_lista = ["Fogão", "Micro-ondas", "Airfryer", "Liquidificador", "Forno", "Só preparo frio"]
    equipamentos_selecao = st.multiselect("Equipamentos disponíveis:", ["Todos"] + equipamentos_lista)

    if "Todos" in equipamentos_selecao:
        equipamentos_selecao = equipamentos_lista

    tempo = st.selectbox("Tempo disponível para cozinhar:", ["Até 10 minutos", "Até 20 minutos", "Até 30 minutos", "Tempo livre"])
    refeicao = st.selectbox("Tipo de refeição:", ["Café da manhã", "Almoço", "Pré-treino", "Pós-treino", "Jantar", "Aleatória"])
    preferencia = st.text_input("Algum alimento que ama ou quer evitar?", "")
    dica = st.radio("Deseja uma dica de performance com a receita?", ["Sim", "Não"])

    enviar = st.form_submit_button("🔍 Gerar Receita")

# ========== GERAÇÃO COM IA ==========
if enviar:
    restricoes_str = ", ".join(restricoes) if restricoes else "Nenhuma"
    equipamentos_str = ", ".join(equipamentos_selecao) if equipamentos_selecao else "Não informado"

    prompt = f"""
Você é um nutricionista esportivo especializado em alimentação de performance.
Gere uma receita simples e prática com base nas informações abaixo:

Usuário: {nome or 'Usuário'}
Objetivo: {objetivo}
Fase do treino: {fase}
Estilo alimentar: {dieta}
Restrições: {restricoes_str}
Equipamentos: {equipamentos_str}
Tempo disponível: {tempo}
Tipo de refeição: {refeicao}
Preferências: {preferencia or 'Nenhuma'}
Deseja dica de performance? {dica}

Formato da resposta:
1. Nome da receita
2. Objetivo declarado
3. Tempo de preparo
4. Ingredientes com quantidades
5. Modo de preparo passo a passo
6. Macros estimados (proteína, carboidrato, gordura, calorias)
7. Dica extra (se solicitado)

Seja simples, direto e prático. Use alimentos comuns no Brasil e foque em performance.
"""

    with st.spinner("Gerando sua receita com IA... 🍳"):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um nutricionista funcional especializado em nutrição esportiva personalizada."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        resposta = response.choices[0].message.content

    st.markdown("---")
    st.subheader("🍽️ Receita NutriChef Pro:")
    st.markdown(resposta)

    # ========== GERAR RELATÓRIO EM .DOCX ==========
    doc = Document()
    doc.add_heading("Receita NutriChef Pro", level=1)
    for linha in resposta.split("\n"):
        if linha.strip():
            paragrafo = doc.add_paragraph()
            paragrafo.add_run(linha.strip()).font.size = Pt(11)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="📥 Baixar receita como .docx",
        data=buffer,
        file_name="Receita_NutriChef_Pro.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # ========== CHAMADA PARA FUNIL ==========
    st.markdown("---")
    st.success("💡 Curtiu a receita?")
    st.markdown("Receba um plano completo de 3 ou 7 dias com IA:")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("📅 Plano de 3 dias", "https://seulink.com/plano3")
    with col2:
        st.link_button("🔥 Quero o PRO+ 7 dias", "https://seulink.com/assinatura")
