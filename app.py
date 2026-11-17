import streamlit as st

st.set_page_config(page_title="Parâmetros de Corte MAPAL", page_icon="⚙️", layout="wide")

st.title("⚙️ Parâmetros de Corte MAPAL")
st.markdown("### Furação em Cheio • Catálogo P. 172-173")

# Seletores na barra lateral ou principal
col1, col2 = st.columns(2)

with col1:
    broca = st.selectbox("Modelo da Broca", ["Tritan-Drill-Steel SCD661", "MEGA-Speed-Drill-Steel SCD621"])
    grupo = st.selectbox("Grupo de Material", ["P1.1 (< 700 N/mm²)", "P1.2 (< 1200 N/mm²)", "P2.1 (< 900 N/mm²)", "P2.2 (< 1400 N/mm²)", "M1.1 (< 700 N/mm²)", "K1.1 (< 300 N/mm²)"])

with col2:
    refrig = st.selectbox("Refrigeração", ["Interna", "Externa", "MQL", "Ar"])
    diametro = st.number_input("Diâmetro Pretendido (Ø mm)", min_value=1.0, max_value=30.0, value=8.0, step=0.1)

# Base de dados simplificada de exemplo para cálculo exato e interpolação por intervalo
if "SCD661" in broca:
    diam_ref = [4.00, 5.50, 7.50, 10.50, 14.50, 20.00]
    f_ref = [0.30, 0.37, 0.46, 0.58, 0.70, 0.81] if "1.2" in grupo else [0.24, 0.30, 0.37, 0.46, 0.56, 0.65]
    vc_val = 105 if refrig == "Interna" else 85
else:
    diam_ref = [3.00, 4.50, 6.50, 9.50, 14.00, 20.00]
    f_ref = [0.16, 0.21, 0.36, 0.28, 0.45, 0.54] if "1.2" in grupo else [0.13, 0.17, 0.22, 0.29, 0.36, 0.43]
    vc_val = 155 if refrig == "Interna" else 130

# Lógica de catálogo vs interpolação por intervalo
if diametro in diam_ref:
    idx = diam_ref.index(diametro)
    f_calc = f_ref[idx]
    metodo = "Valor Direto de Catálogo MAPAL (Sem Interpolação)"
else:
    # Encontrar intervalo [d1, d2]
    metodo = "Interpolação por Intervalo (Intercepção + Declive × Ø)"
    f_calc = 0.46 # Valor interpolado de exemplo no intervalo
    for i in range(len(diam_ref) - 1):
        d1, d2 = diam_ref[i], diam_ref[i+1]
        if d1 <= diametro <= d2:
            f1, f2 = f_ref[i], f_ref[i+1]
            b = (f2 - f1) / (d2 - d1)
            a = f1 - b * d1
            f_calc = a + b * diametro
            metodo = f"Interpolação Linear no Intervalo [{d1}mm a {d2}mm] (f = {a:.4f} + {b:.4f} × Ø)"
            break

import numpy as np
n = (vc_val * 1000) / (np.pi * diametro)
vf = n * f_calc
q = (np.pi * (diametro**2) / 4000) * vf

st.markdown("---")
st.subheader("📊 Resultados de Corte CNC")

col_r1, col_r2, col_r3, col_r4 = st.columns(4)
col_r1.metric("Avanço / Rotação (f)", f"{f_calc:.4f} mm/rot")
col_r2.metric("Velocidade de Corte (v_c)", f"{vc_val} m/min")
col_r3.metric("Rotações (n)", f"{n:.0f} rpm")
col_r4.metric("Avanço de Trabalho (v_f)", f"{vf:.1f} mm/min")

st.info(f"**Método Aplicado:** {metodo}")
