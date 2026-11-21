import json
import math
import re
from pathlib import Path
import pandas as pd


def _parse_num(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_diametro(col_name):
    if col_name is None or (isinstance(col_name, float) and math.isnan(col_name)):
        return None
    s = str(col_name).strip().replace(",", ".")
    m = re.search(r"(?:[dDØø]\s*)?(\d+(?:\.\d+)?)", s)
    if not m:
        return None
    val = float(m.group(1))
    return str(int(val)) if val.is_integer() else str(val)


def exportar_json(
    excel_path: str = "dados/parametros_corte.xlsx",
    sheet_name: str = "Parametros_Corte",
    output_path: str = "dados/furacao_parametros.json",
) -> list[dict]:
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    registos = []
    familia_atual = None
    col_map = None

    vc_cols = ["Vc_Int", "Vc_Ext", "Vc_MQL", "Vc_Ar"]

    for _, row in df.iterrows():
        celulas = [
            str(x).strip()
            for x in row.tolist()
            if x is not None and not (isinstance(x, float) and math.isnan(x))
        ]
        if not celulas:
            continue

        # Deteta título de família (ex.: linha com texto que não é cabeçalho de tabela nem MMG)
        primeira = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        if (
            primeira
            and primeira.upper() not in {"MMG", "GRUPO", "VC_INT", "VC_EXT", "VC_MQL", "VC_AR"}
            and not primeira.lower().startswith("mmg")
            and "mmg" not in [c.lower() for c in row.astype(str)]
        ):
            # Verifica se a linha parece cabeçalho de tabela com diâmetros
            tem_diametros = any(_parse_diametro(c) is not None for c in row.iloc[1:])
            if not tem_diametros and len(celulas) == 1:
                familia_atual = primeira
                col_map = None
                continue

        # Deteta linha de cabeçalho da tabela (contém MMG / Grupo / Vc / diâmetros)
        row_upper = [str(x).strip().upper() if pd.notna(x) else "" for x in row.tolist()]
        if "MMG" in row_upper or "GRUPO" in row_upper:
            col_map = {"mmg": None, "grupo": None, "vc": {}, "f_by_d": {}}
            for idx, val in enumerate(row.tolist()):
                if pd.isna(val):
                    continue
                nome = str(val).strip()
                up = nome.upper()
                if up == "MMG":
                    col_map["mmg"] = idx
                elif up in {"GRUPO", "MAT_GRUPO", "GRUPO_MAT"}:
                    col_map["grupo"] = idx
                elif up in {"VC_INT", "VC INT"}:
                    col_map["vc"]["Vc_Int"] = idx
                elif up in {"VC_EXT", "VC EXT"}:
                    col_map["vc"]["Vc_Ext"] = idx
                elif up in {"VC_MQL", "VC MQL"}:
                    col_map["vc"]["Vc_MQL"] = idx
                elif up in {"VC_AR", "VC AR"}:
                    col_map["vc"]["Vc_Ar"] = idx
                else:
                    d_key = _parse_diametro(nome)
                    if d_key is not None:
                        col_map["f_by_d"][idx] = d_key
            continue

        # Lê linha de dados se existir cabeçalho ativo
        if col_map and col_map["mmg"] is not None:
            mmg_raw = row.iloc[col_map["mmg"]]
            if pd.isna(mmg_raw) or str(mmg_raw).strip() == "":
                continue
            mmg_val = str(mmg_raw).strip()

            grupo_val = None
            if col_map["grupo"] is not None:
                g_raw = row.iloc[col_map["grupo"]]
                if pd.notna(g_raw) and str(g_raw).strip() != "":
                    grupo_val = str(g_raw).strip()

            entrada = {
                "familia": familia_atual,
                "grupo": grupo_val if grupo_val is not None else mmg_val,
                "mmg": mmg_val,
            }

            for vc_key in vc_cols:
                c_idx = col_map["vc"].get(vc_key)
                entrada[vc_key] = _parse_num(row.iloc[c_idx]) if c_idx is not None else None

            f_by_d = {}
            for c_idx, d_key in col_map["f_by_d"].items():
                f_val = _parse_num(row.iloc[c_idx])
                if f_val is not None:
                    f_by_d[d_key] = f_val

            entrada["f_by_d"] = f_by_d
            registos.append(entrada)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registos, indent=2, ensure_ascii=False), encoding="utf-8")
    return registos