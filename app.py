import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Calculadora de Carbono | Mobilidade",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Fatores médios editáveis pelo usuário (kg CO2e por unidade)
DEFAULT_FACTORS = {
    "Gasolina": 2.31,
    "Etanol": 1.50,
    "Diesel": 2.68,
    "Eletricidade (rede)": 0.08,
}


def emissao_combustao(distancia, consumo, fator):
    return distancia * consumo / 100 * fator


def emissao_eletrica(distancia, consumo, fator):
    return distancia * consumo / 100 * fator


def card_metric(label, value, help_text=None):
    st.metric(label, value, help=help_text)


st.markdown(
    """
    <style>
    .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {background: #0b0d0f;}
    [data-testid="stMetric"] {background: #ffffff; border: 1px solid #e3ece6;
      padding: 16px; border-radius: 14px; box-shadow: 0 2px 8px #173d2410;}
    [data-testid="stMetric"] label,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricDelta"] {color: #123b27 !important;}
    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {color: #f4f7f5;}
    [data-testid="stMetric"] [data-testid="stMarkdownContainer"] p {color: #527060 !important;}
    .hero h1 {color: #ffffff;}
    .hero p {color: #b9c8be;}
    .note p {color: #214c32 !important;}
    [data-testid="stSidebar"] {background: #171b19;}
    [data-testid="stSidebar"] * {color: #f4f7f5;}
    .hero {padding: 8px 0 18px 0;}
    .hero h1 {color: #123b27; margin-bottom: 4px;}
    .hero p {color: #527060; font-size: 1.05rem;}
    .note {background: #eaf6ee; border-left: 4px solid #2e9d5b; padding: 12px 16px;
      border-radius: 8px; color: #214c32;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>🌱 Calculadora de carbono para mobilidade</h1>'
    '<p>Compare as emissões estimadas de diferentes formas de transporte e entenda o impacto de cada escolha.</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Parâmetros da viagem")
    distancia = st.number_input("Distância total percorrida (km)", min_value=1.0, value=1000.0, step=50.0)
    st.caption("Informe a distância no período que deseja analisar (por exemplo, um mês ou um ano).")
    st.divider()
    st.header("Fatores de emissão")
    st.caption("kg CO₂e por litro ou kWh. Ajuste conforme sua fonte de dados.")
    fatores = {
        chave: st.number_input(chave, min_value=0.0, value=valor, step=0.01, format="%.2f")
        for chave, valor in DEFAULT_FACTORS.items()
    }
    st.divider()
    st.info("Os resultados são estimativas. O uso real, o trânsito, a ocupação do veículo e a matriz elétrica podem alterar os valores.")

st.subheader("Configure os veículos")
tab_carro_e, tab_carro_c, tab_hibrido, tab_moto = st.tabs(
    ["⚡ Carro elétrico", "⛽ Carro a combustão", "🔋 Híbrido", "🏍️ Moto"]
)

with tab_carro_e:
    consumo_e = st.number_input("Consumo elétrico (kWh/100 km)", min_value=1.0, value=16.0, step=0.5, key="consumo_e")
    nome_e = st.text_input("Nome para o gráfico", "Carro elétrico", key="nome_e")

with tab_carro_c:
    combustivel_c = st.selectbox("Combustível", ["Gasolina", "Etanol", "Diesel"], key="combustivel_c")
    consumo_c = st.number_input("Consumo (L/100 km)", min_value=1.0, value=9.0, step=0.1, key="consumo_c")
    nome_c = st.text_input("Nome para o gráfico", "Carro a combustão", key="nome_c")

with tab_hibrido:
    combustivel_h = st.selectbox("Combustível do motor", ["Gasolina", "Etanol"], key="combustivel_h")
    consumo_h = st.number_input("Consumo de combustível (L/100 km)", min_value=0.1, value=4.5, step=0.1, key="consumo_h")
    consumo_h_e = st.number_input("Consumo elétrico adicional (kWh/100 km)", min_value=0.0, value=2.0, step=0.5, key="consumo_h_e")
    nome_h = st.text_input("Nome para o gráfico", "Híbrido", key="nome_h")

with tab_moto:
    combustivel_m = st.selectbox("Combustível", ["Gasolina", "Etanol"], key="combustivel_m")
    consumo_m = st.number_input("Consumo (L/100 km)", min_value=0.5, value=3.0, step=0.1, key="consumo_m")
    nome_m = st.text_input("Nome para o gráfico", "Moto", key="nome_m")

emissoes = {
    nome_e: emissao_eletrica(distancia, consumo_e, fatores["Eletricidade (rede)"]),
    nome_c: emissao_combustao(distancia, consumo_c, fatores[combustivel_c]),
    nome_h: emissao_combustao(distancia, consumo_h, fatores[combustivel_h]) + emissao_eletrica(distancia, consumo_h_e, fatores["Eletricidade (rede)"]),
    nome_m: emissao_combustao(distancia, consumo_m, fatores[combustivel_m]),
}

df = pd.DataFrame({"Modalidade": list(emissoes.keys()), "Emissões (kg CO₂e)": list(emissoes.values())})
baseline = emissoes[nome_c]
menor = min(emissoes.values())
melhor_nome = min(emissoes, key=emissoes.get)
economia = max(0.0, baseline - menor)
reducao = (economia / baseline * 100) if baseline else 0

st.subheader("Resumo do impacto")
k1, k2, k3, k4 = st.columns(4)
with k1:
    card_metric("Menor emissão", f"{menor / 1000:.2f} t CO₂e", melhor_nome)
with k2:
    card_metric("Economia vs. combustão", f"{economia:.1f} kg", "Comparação com o carro a combustão configurado")
with k3:
    card_metric("Redução potencial", f"{reducao:.0f}%", "Em relação ao carro a combustão")
with k4:
    card_metric("Equivalente em árvores", f"{economia / 21.77:.1f}", "Estimativa de árvores absorvendo 21,77 kg CO₂e/ano")

st.markdown(
    f'<div class="note"><b>Melhor resultado:</b> {melhor_nome} emite aproximadamente '
    f'<b>{menor:.1f} kg CO₂e</b> no período informado.</div>',
    unsafe_allow_html=True,
)

col_chart, col_table = st.columns([1.6, 1])
with col_chart:
    st.subheader("Comparação de emissões")
    fig = px.bar(df.sort_values("Emissões (kg CO₂e)"), x="Modalidade", y="Emissões (kg CO₂e)", color="Emissões (kg CO₂e)", color_continuous_scale=["#b8e0c3", "#1d7a43"])
    fig.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="kg CO₂e", xaxis_title="", margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
with col_table:
    st.subheader("Detalhamento")
    tabela = df.copy()
    tabela["Emissões (kg CO₂e)"] = tabela["Emissões (kg CO₂e)"].round(1)
    tabela["vs. combustão"] = ((1 - tabela["Emissões (kg CO₂e)"] / baseline) * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(tabela, hide_index=True, use_container_width=True)

with st.expander("Premissas e como interpretar"):
    st.markdown(
        """
        - Combustíveis são calculados por `distância × consumo ÷ 100 × fator de emissão`.
        - Eletricidade segue a mesma lógica, usando kWh/100 km e o fator da rede elétrica.
        - O híbrido soma as parcelas de combustível e eletricidade informadas.
        - CO₂e inclui uma aproximação dos gases de efeito estufa convertidos em CO₂ equivalente.
        - A equivalência de árvores usa 21,77 kg de CO₂e absorvidos por árvore ao ano; é apenas uma referência didática.
        - Os fatores padrão são médias ilustrativas e devem ser substituídos por dados locais ou do fabricante quando disponíveis.
        """
    )

st.caption("Calculadora educacional • Ajuste os parâmetros na barra lateral para explorar cenários.")
