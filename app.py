import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Calculadora de Parâmetros de Corte - MAPAL", page_icon="⚙️", layout="wide")

st.title("⚙️ Calculadora de Parâmetros de Corte MAPAL")
st.markdown("Selecione a broca, o grupo de material e o diâmetro pretendido para calcular os parâmetros de corte exatos (Catálogo e Interpolação por Intervalo).")

# Dados do Catálogo MAPAL
# SCD661 (Tritan-Drill-Steel)
# Diâmetros de referência: 4.00, 5.50, 7.50, 10.50, 14.50, 20.00
scd661_data = {
    "P1.1": {"desc": "Aços estruturais, de corte livre (< 700 N/mm²)", "vc_int": 115, "vc_ext": 105, "vc_mql": 105, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.24, 0.30, 0.37, 0.46, 0.56, 0.65]},
    "P1.2": {"desc": "Aços estruturais, de corte livre (< 1200 N/mm²)", "vc_int": 105, "vc_ext": 85, "vc_mql": 85, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.30, 0.37, 0.46, 0.58, 0.70, 0.81]},
    "P2.1": {"desc": "Aços de têmpera, nitretados, liga (< 900 N/mm²)", "vc_int": 115, "vc_ext": 100, "vc_mql": 100, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.28, 0.35, 0.44, 0.55, 0.66, 0.77]},
    "P2.2": {"desc": "Aços de têmpera, nitretados, liga (< 1400 N/mm²)", "vc_int": 80, "vc_ext": 70, "vc_mql": 70, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.24, 0.29, 0.36, 0.44, 0.53, 0.61]},
    "P3.1": {"desc": "Aços para ferramentas, rolamento (< 800 N/mm²)", "vc_int": 85, "vc_ext": 75, "vc_mql": 75, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.25, 0.31, 0.39, 0.49, 0.60, 0.69]},
    "P3.2": {"desc": "Aços para ferramentas, rolamento (< 1000 N/mm²)", "vc_int": 70, "vc_ext": 65, "vc_mql": 65, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.21, 0.26, 0.33, 0.41, 0.49, 0.56]},
    "P3.3": {"desc": "Aços para ferramentas, rolamento (< 1500 N/mm²)", "vc_int": 70, "vc_ext": 50, "vc_mql": 60, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.18, 0.21, 0.26, 0.32, 0.38, 0.43]},
    "P5.1": {"desc": "Aço fundido", "vc_int": 115, "vc_ext": 100, "vc_mql": 100, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.28, 0.35, 0.44, 0.55, 0.66, 0.77]},
    "M1.1": {"desc": "Aços inoxidáveis austeníticos (< 700 N/mm²)", "vc_int": 55, "vc_ext": 35, "vc_mql": 35, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.11, 0.14, 0.18, 0.22, 0.27, 0.31]},
    "M1.2": {"desc": "Aços inoxidáveis ferríticos/austeníticos (Duplex) (< 1000 N/mm²)", "vc_int": 140, "vc_ext": 100, "vc_mql": 100, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.34, 0.45, 0.58, 0.75, 0.92, 1.08]},
    "K1.1": {"desc": "Ferro fundido lamelar GJL (< 300 N/mm²)", "vc_int": 185, "vc_ext": 115, "vc_mql": 140, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.34, 0.43, 0.55, 0.70, 0.85, 1.00]},
    "K2.1": {"desc": "Ferro fundido esferoidal GJS (< 500 N/mm²)", "vc_int": 115, "vc_ext": 85, "vc_mql": 85, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.30, 0.38, 0.48, 0.61, 0.74, 0.86]},
    "K2.2": {"desc": "Ferro fundido esferoidal GJS (<= 800 N/mm²)", "vc_int": 70, "vc_ext": 45, "vc_mql": 60, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.16, 0.20, 0.31, 0.25, 0.38, 0.44]},
    "K2.3": {"desc": "Ferro fundido esferoidal GJS (> 800 N/mm²)", "vc_int": 105, "vc_ext": 90, "vc_mql": 90, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.32, 0.41, 0.52, 0.65, 0.79, 0.92]},
    "K3.1": {"desc": "Ferro fundido GJV / maleável (< 500 N/mm²)", "vc_int": 90, "vc_ext": 80, "vc_mql": 80, "diametros": [4.00, 5.50, 7.50, 10.50, 14.50, 20.00], "f": [0.27, 0.34, 0.42, 0.52, 0.63, 0.73]}
}

# SCD621 (MEGA-Speed-Drill-Steel)
scd621_data = {
    "P1.1": {"desc": "Aços estruturais, de corte livre (< 700 N/mm²)", "vc_int": 170, "vc_ext": 155, "vc_mql": 155, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.13, 0.17, 0.22, 0.29, 0.36, 0.43]},
    "P1.2": {"desc": "Aços estruturais, de corte livre (< 1200 N/mm²)", "vc_int": 155, "vc_ext": 130, "vc_mql": 130, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.16, 0.21, 0.36, 0.28, 0.45, 0.54]},
    "P2.1": {"desc": "Aços de têmpera, nitretados, liga (< 900 N/mm²)", "vc_int": 170, "vc_ext": 145, "vc_mql": 145, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.15, 0.20, 0.34, 0.26, 0.43, 0.51]},
    "P2.2": {"desc": "Aços de têmpera, nitretados, liga (< 1400 N/mm²)", "vc_int": 120, "vc_ext": 100, "vc_mql": 100, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.13, 0.17, 0.21, 0.27, 0.34, 0.40]},
    "P3.1": {"desc": "Aços para ferramentas, rolamento (< 800 N/mm²)", "vc_int": 130, "vc_ext": 110, "vc_mql": 110, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.13, 0.18, 0.30, 0.23, 0.39, 0.46]},
    "P3.2": {"desc": "Aços para ferramentas, rolamento (< 1000 N/mm²)", "vc_int": 100, "vc_ext": 95, "vc_mql": 95, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.12, 0.15, 0.20, 0.25, 0.32, 0.37]},
    "P3.3": {"desc": "Aços para ferramentas, rolamento (< 1500 N/mm²)", "vc_int": 100, "vc_ext": 75, "vc_mql": 85, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.10, 0.12, 0.16, 0.20, 0.25, 0.29]},
    "P4.1": {"desc": "Aços inoxidáveis ferríticos e martensíticos", "vc_int": 100, "vc_ext": 75, "vc_mql": 85, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.09, 0.12, 0.16, 0.20, 0.25, 0.30]},
    "M1.1": {"desc": "Aços inoxidáveis austeníticos (< 700 N/mm²)", "vc_int": 65, "vc_ext": 40, "vc_mql": 40, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.07, 0.09, 0.12, 0.15, 0.19, 0.23]},
    "K1.1": {"desc": "Ferro fundido lamelar GJL (< 300 N/mm²)", "vc_int": 150, "vc_ext": 105, "vc_mql": 105, "diametros": [3.00, 4.50, 6.50, 9.50, 14.00, 20.00], "f": [0.14, 0.21, 0.38, 0.28, 0.49, 0.59]}
}

st.sidebar.header("🔧 Configuração da Ferramenta")
broca_escolhida = st.sidebar.selectbox("Modelo da Broca", ["Tritan-Drill-Steel SCD661", "MEGA-Speed-Drill-Steel SCD621"])
dados_tabela = scd661_data if "661" in broca_escolhida else scd621_data

grupo_mat = st.sidebar.selectbox("Grupo de Material MAPAL", list(dados_tabela.keys()), format_func=lambda x: f"{x} - {dados_tabela[x]['desc']}")
refrig = st.sidebar.selectbox("Refrigeração", ["Interna", "Externa", "MQL", "Ar"])

diam_pret = st.sidebar.number_input("Diâmetro Pretendido (Ø mm)", min_value=1.0, max_value=30.0, value=8.0, step=0.1)
liga_alta = st.sidebar.checkbox("Teor de liga (Cr, Mo, Ni, V, W) > 8% (Avança grupo)")

# Lógica de cálculo
info = dados_tabela[grupo_mat]
diametros_ref = info["diametros"]
avancos_ref = info["f"]

# Determinar Vc
vc_base = info["vc_int"] if refrig == "Interna" else (info["vc_ext"] if refrig == "Externa" else info["vc_mql"])

# Verificar se é diâmetro de catálogo exato
if diam_pret in diametros_ref:
    idx = diametros_ref.index(diam_pret)
    f_calc = avancos_ref[idx]
    metodo = "Valor Direto de Catálogo MAPAL (Sem Interpolação)"
else:
    # Encontrar intervalo
    di = diam_pret
    # Achar o segmento [d1, d2]
    seg_encontrado = False
    f_calc = 0
    metodo = ""
    for i in range(len(diametros_ref) - 1):
        d1, d2 = diametros_ref[i], diametros_ref[i+1]
        if d1 <= di <= d2:
            f1, f2 = avancos_ref[i], avancos_ref[i+1]
            # Cálculo de declive e intercepção no intervalo
            b = (f2 - f1) / (d2 - d1)
            a = f1 - b * d1
            f_calc = a + b * di
            metodo = f"Interpolação por Intervalo [{d1}mm a {d2}mm] (f = {a:.4f} + {b:.4f} × Ø)"
            seg_encontrado = True
            break
    if not seg_encontrado:
        # Fora dos limites, usar o mais próximo ou extrapolar linearmente com os extremos
        if di < diametros_ref[0]:
            d1, d2 = diametros_ref[0], diametros_ref[1]
            f1, f2 = avancos_ref[0], avancos_ref[1]
        else:
            d1, d2 = diametros_ref[-2], diametros_ref[-1]
            f1, f2 = avancos_ref[-2], avancos_ref[-1]
        b = (f2 - f1) / (d2 - d1)
        a = f1 - b * d1
        f_calc = a + b * di
        metodo = f"Extrapolação Linear (Fora do intervalo padrão)"

# Rotações e Avanço de Trabalho
n = (vc_base * 1000) / (np.pi * diam_pret)
vf = n * f_calc
q = (np.pi * (diam_pret**2) / 4000) * vf

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avanço / Rotação (f)", f"{f_calc:.4f} mm/rot")
col2.metric("Rotações (n)", f"{n:.0f} rpm")
col3.metric("Avanço de Trabalho (vf)", f"{vf:.1f} mm/min")
col4.metric("Taxa de Remoção (Q)", f"{q:.1f} cm³/min")

st.info(f"**Método de Cálculo:** {metodo}")

st.markdown("---")
st.subheader("📋 Tabela de Referência do Catálogo para o Grupo Selecionado")
df_ref = pd.DataFrame({"Diâmetro (mm)": diametros_ref, "Avanço f (mm/rot)": avancos_ref})
st.dataframe(df_ref, use_container_width=True)
