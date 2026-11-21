import json
from pathlib import Path
import pandas as pd

EXCEL_PATH = Path("catalogo_teste.xlsx")
OUT_DIR = Path("dados")
OUT_DIR.mkdir(exist_ok=True)

FAMILIAS_SEM_REFRIG_INT = {"SCD360", "SCD600"}
COLUNAS_AVANCO_IDX = [6, 7, 8, 9, 10, 11]  # Colunas G a L


def to_float_or_none(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    try:
        return float(str(val).replace(",", ".").strip())
    except ValueError:
        return None

def to_order_str(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

df_dim = pd.read_excel(EXCEL_PATH, sheet_name="Dimensoes")
df_par = pd.read_excel(EXCEL_PATH, sheet_name="Parametros_Corte", header=None)
df_dim = pd.read_excel(EXCEL_PATH, sheet_name="Dimensoes")
df_dim.columns = df_dim.columns.str.strip()

# 1. Dimensões e referências
referencias = []
for _, r in df_dim.iterrows():
    if pd.isna(r.get("Familia")) or pd.isna(r.get("Order_no")):
        continue
    referencias.append({
        "operacao": "furacao",
        "familia": str(r["Familia"]).strip(),
        "variante": str(r.get("Variante", "")).strip(),
        "refrigeracao": str(r.get("Refrig", "")).strip(),
        "d1": to_float_or_none(r.get("d1")),
        "d2": to_float_or_none(r.get("d2")),
        "l1": to_float_or_none(r.get("l1")),
        "l2": to_float_or_none(r.get("l2")),
        "l3": to_float_or_none(r.get("l3")),
        "l4": to_float_or_none(r.get("l4")),
        "specification": str(r.get("Specification", "")).strip(),
        "order_no": to_order_str(r["Order_no"]),
    })

# 2. Parâmetros de corte com cabeçalhos dinâmicos por bloco
parametros = []
diametros_bloco_atual = [1.0, 1.82, 3.31, 6.03, 10.99, 20.0]

for _, r in df_par.iterrows():
    col0 = str(r.iloc[0]).strip() if len(r) > 0 and pd.notna(r.iloc[0]) else ""
    col1 = str(r.iloc[1]).strip() if len(r) > 1 and pd.notna(r.iloc[1]) else ""

    if not col0 and not col1:
        continue

    # Deteta linha de cabeçalho de bloco
    if col0.lower() == "familia" and col1.lower() == "mmg":
        novos_diametros = []
        for idx_c in COLUNAS_AVANCO_IDX:
            d_val = to_float_or_none(r.iloc[idx_c]) if idx_c < len(r) else None
            if d_val is not None:
                novos_diametros.append(d_val)
        if len(novos_diametros) == 6:
            diametros_bloco_atual = novos_diametros
        continue

    if not col0 or not col1:
        continue

    familia = col0
    mmg = col1

    vc_int = to_float_or_none(r.iloc[2]) if len(r) > 2 else None
    vc_ext = to_float_or_none(r.iloc[3]) if len(r) > 3 else None
    vc_mql = to_float_or_none(r.iloc[4]) if len(r) > 4 else None
    vc_ar = to_float_or_none(r.iloc[5]) if len(r) > 5 else None

    if familia.upper() in FAMILIAS_SEM_REFRIG_INT:
        vc_int = None

    avancos_por_diametro = {}
    for d_ref, idx_c in zip(diametros_bloco_atual, COLUNAS_AVANCO_IDX):
        val_f = to_float_or_none(r.iloc[idx_c]) if idx_c < len(r) else None
        avancos_por_diametro[str(d_ref)] = val_f

    tem_vc = any(v is not None for v in [vc_int, vc_ext, vc_mql, vc_ar])
    tem_avanco = any(v is not None for v in avancos_por_diametro.values())

    parametros.append({
        "familia": familia,
        "mmg": mmg,
        "vc": {
            "interna": vc_int,
            "externa": vc_ext,
            "mql": vc_mql,
            "ar": vc_ar,
        },
        "suportado": tem_vc and tem_avanco,
        "avancos_f": avancos_por_diametro,
    })

(OUT_DIR / "referencias.json").write_text(
    json.dumps(referencias, ensure_ascii=False, indent=2), encoding="utf-8"
)
(OUT_DIR / "furacao_parametros.json").write_text(
    json.dumps(parametros, ensure_ascii=False, indent=2), encoding="utf-8"
)

print(f"OK: {len(referencias)} dimensões | {len(parametros)} linhas de corte.")