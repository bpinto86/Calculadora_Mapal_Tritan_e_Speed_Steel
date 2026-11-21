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
    return f"{val:.1f}" if not val.is_integer() else f"{val:.1f}"


def exportar_json(
    excel_path: str = "dados/parametros_corte.xlsx",
    sheet_name: str = "Parametros_Corte",
    output_path: str = "dados/furacao_parametros.json",
) -> list[dict]:
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    registos = []
    familia_atual = None
    col_map = None

    vc_map = {
        "interna": ["VC_INT", "VC INT", "INTERNA", "INT"],
        "externa": ["VC_EXT", "VC EXT", "EXTERNA", "EXT"],
        "mql": ["VC_MQL", "VC MQL", "MQL"],
        "ar": ["VC_AR", "VC AR", "AR"],
    }

    for _, row in df.iterrows():
        celulas = [
            str(x).strip()
            for x in row.tolist()
            if x is not None and not (isinstance(x, float) and math.isnan(x))
        ]
        if not celulas:
            continue

        row_upper = [str(x).strip().upper() if pd.notna(x) else "" for x in row.tolist()]
        if "MMG" in row_upper or "GRUPO" in row_upper:
            col_map = {"mmg": None, "vc": {}, "f_by_d": {}}
            for idx, val in enumerate(row.tolist()):
                if pd.isna(val):
                    continue
                nome = str(val).strip()
                up = nome.upper()
                if up in {"MMG", "GRUPO", "MAT_GRUPO", "GRUPO_MAT"}:
                    col_map["mmg"] = idx
                else:
                    matched_vc = None
                    for k_vc, aliases in vc_map.items():
                        if up in aliases:
                            col_map["vc"][k_vc] = idx
                            matched_vc = k_vc
                            break
                    if not matched_vc:
                        d_key = _parse_diametro(nome)
                        if d_key is not None:
                            col_map["f_by_d"][idx] = d_key
            continue

        primeira = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        if (
            primeira
            and primeira.upper() not in {"MMG", "GRUPO"}
            and not re.match(r"^[PMKNHSC]\d+(\.\d+)?$", primeira.upper())
            and len(celulas) <= 3
            and all(_parse_num(c) is None for c in celulas[1:])
        ):
            familia_atual = primeira
            col_map = None
            continue

        if col_map and col_map["mmg"] is not None:
            mmg_raw = row.iloc[col_map["mmg"]]
            if pd.isna(mmg_raw) or str(mmg_raw).strip() == "":
                continue
            mmg_val = str(mmg_raw).strip()

            vc_entry = {}
            for k_vc in ["interna", "externa", "mql", "ar"]:
                c_idx = col_map["vc"].get(k_vc)
                vc_entry[k_vc] = _parse_num(row.iloc[c_idx]) if c_idx is not None else None

            avancos_f = {}
            for c_idx, d_key in col_map["f_by_d"].items():
                avancos_f[d_key] = _parse_num(row.iloc[c_idx])

            tem_dados = any(v is not None for v in vc_entry.values()) or any(
                v is not None for v in avancos_f.values()
            )

            registos.append({
                "familia": familia_atual,
                "mmg": mmg_val,
                "vc": vc_entry,
                "suportado": tem_dados,
                "avancos_f": avancos_f,
            })

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registos, indent=2, ensure_ascii=False), encoding="utf-8")
    return registos