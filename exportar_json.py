import json
import math
from pathlib import Path
import pandas as pd


EXCEL_PATH = Path("catalogo_teste.xlsx")
OUTPUT_DIR = Path("dados")

SHEET_FAMILIAS = "Familias"
SHEET_CATALOGO = "Catalogo"
SHEET_PARAMETROS = "Parametros"
SHEET_MMG = "MAPAL_MMG"
SHEET_MMG_NEW = "MAPAL_MMG_NEW"


def is_na(val) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    if pd.isna(val):
        return True
    return str(val).strip() == ""


def to_str(val, default: str = "") -> str:
    if is_na(val):
        return default
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val).strip()


def to_float(val, default=None):
    if is_na(val):
        return default
    if isinstance(val, (int, float)):
        f = float(val)
        return default if math.isnan(f) else f
    s = str(val).strip().replace(",", ".")
    try:
        f = float(s)
        return default if math.isnan(f) else f
    except ValueError:
        return default


def normalizar_refrigeracao(raw) -> str:
    s = to_str(raw).lower()
    if not s:
        return ""
    if "int" in s or s in ("ik", "ic"):
        return "int"
    if "mql" in s or "mms" in s:
        return "mql"
    if s == "ar" or "air" in s or s.startswith("ar "):
        return "ar"
    if "ext" in s or "sem" in s:
        return "ext"
    return s


def normalizar_gama(raw) -> str:
    s = to_str(raw).lower()
    if not s:
        return ""
    if "expert" in s:
        return "expert"
    if "performance" in s:
        return "performance"
    if "basic" in s:
        return "basic"
    return s


def extrair_encabadouro(texto: str) -> str:
    import re
    t = to_str(texto).upper()
    if not t:
        return ""
    m = re.search(r"(?:^|[^A-Z0-9])(HA|HB|HE)(?:[^A-Z0-9]|$|\d)", t)
    if m:
        return m.group(1)
    m2 = re.search(r"(?:-|_|/|\s|\d)(HA|HB|HE)(?=\d|\b|$)", t)
    return m2.group(1) if m2 else ""


def extrair_iso(codigo: str) -> str:
    c = to_str(codigo).upper()
    return c[0] if c and c[0].isalpha() else ""


def extrair_subgrupo(codigo: str) -> str:
    import re
    c = to_str(codigo).upper()
    m = re.match(r"^([A-Z]+\d+)", c)
    return m.group(1) if m else ""


def ler_mapa_familias(xls: pd.ExcelFile) -> dict[str, dict]:
    mapa: dict[str, dict] = {}
    if SHEET_FAMILIAS not in xls.sheet_names:
        return mapa

    df = pd.read_excel(xls, sheet_name=SHEET_FAMILIAS)
    df.columns = [str(c).strip() for c in df.columns]

    for _, row in df.iterrows():
        fam = to_str(row.get("Familia"))
        if not fam:
            continue
        nome_prod = to_str(row.get("Nome do produto"))
        gama_raw = to_str(row.get("Gama"))
        categoria = to_str(row.get("Categoria"))

        mapa[fam.lower()] = {
            "familia": fam,
            "nome_produto": nome_prod,
            "gama": normalizar_gama(gama_raw),
            "gama_label": gama_raw,
            "categoria": categoria,
        }
    return mapa


def exportar_familias(mapa_familias: dict[str, dict]) -> list[dict]:
    return list(mapa_familias.values())


def exportar_catalogo(xls: pd.ExcelFile, mapa_familias: dict[str, dict]) -> list[dict]:
    if SHEET_CATALOGO not in xls.sheet_names:
        return []

    df = pd.read_excel(xls, sheet_name=SHEET_CATALOGO)
    df.columns = [str(c).strip() for c in df.columns]

    referencias = []
    for _, row in df.iterrows():
        order_no = to_str(row.get("Order no."))
        spec = to_str(row.get("Specification"))
        fam = to_str(row.get("Familia"))
        if not order_no and not spec and not fam:
            continue

        fam_info = mapa_familias.get(fam.lower(), {})
        refrig_raw = to_str(row.get("Refrigeração"))
        encabadouro = extrair_encabadouro(f"{spec} {order_no}")

        item = {
            "order_no": order_no,
            "specification": spec,
            "familia": fam_info.get("familia", fam),
            "nome_produto": fam_info.get("nome_produto", ""),
            "gama": fam_info.get("gama", ""),
            "gama_label": fam_info.get("gama_label", ""),
            "categoria": fam_info.get("categoria", ""),
            "variante": to_str(row.get("Variante")),
            "refrigeracao": normalizar_refrigeracao(refrig_raw),
            "refrigeracao_label": refrig_raw,
            "encabadouro": encabadouro,
            "d1": to_float(row.get("d1")),
            "d2": to_float(row.get("d2")),
            "l1": to_float(row.get("l1")),
            "l2": to_float(row.get("l2")),
            "l3": to_float(row.get("l3")),
            "l4": to_float(row.get("l4")),
        }
        referencias.append(item)

    return referencias


def exportar_parametros(xls: pd.ExcelFile, mapa_familias: dict[str, dict]) -> list[dict]:
    if SHEET_PARAMETROS not in xls.sheet_names:
        return []

    df = pd.read_excel(xls, sheet_name=SHEET_PARAMETROS)
    df.columns = [str(c).strip() for c in df.columns]

    colunas_diametro = []
    for col in df.columns:
        if col.startswith("f_d_"):
            d_str = col.replace("f_d_", "").strip().replace(",", ".")
            d_val = to_float(d_str)
            if d_val is not None:
                colunas_diametro.append((col, d_val))

    colunas_diametro.sort(key=lambda x: x[1])

    registos = []
    for _, row in df.iterrows():
        fam = to_str(row.get("Familia"))
        grupo = to_str(row.get("Grupo")).upper()
        if not fam or not grupo:
            continue

        vc_int = to_float(row.get("Vc_Int"), 0.0)
        vc_ext = to_float(row.get("Vc_Ext"), 0.0)
        vc_mql = to_float(row.get("Vc_MQL"), 0.0)
        vc_ar = to_float(row.get("Vc_Ar"), 0.0)

        avancos_f = {}
        diametros = []
        f_lista = []

        for col_name, d_val in colunas_diametro:
            f_val = to_float(row.get(col_name))
            if f_val is not None and f_val > 0:
                key_d = f"{d_val:g}"
                avancos_f[key_d] = round(f_val, 5)
                diametros.append(d_val)
                f_lista.append(round(f_val, 5))

        suportado = any(v > 0 for v in (vc_int, vc_ext, vc_mql, vc_ar)) and len(f_lista) > 0
        fam_info = mapa_familias.get(fam.lower(), {})

        registos.append({
            "familia": fam_info.get("familia", fam),
            "nome_produto": fam_info.get("nome_produto", ""),
            "gama": fam_info.get("gama", ""),
            "categoria": fam_info.get("categoria", ""),
            "grupo": grupo,
            "suportado": suportado,
            "vc": {
                "int": vc_int,
                "ext": vc_ext,
                "mql": vc_mql,
                "ar": vc_ar,
            },
            "diametros": diametros,
            "f": f_lista,
            "avancos_f": avancos_f,
        })

    return registos


def processar_aba_mmg(xls: pd.ExcelFile, sheet_name: str) -> list[dict]:
    if sheet_name not in xls.sheet_names:
        return []

    df = pd.read_excel(xls, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]

    grupos = []
    for _, row in df.iterrows():
        cod = to_str(row.get("Grupo")).upper()
        if not cod:
            continue

        iso_raw = to_str(row.get("ISO")).upper()
        iso_clean = iso_raw.replace("*", "").strip() or extrair_iso(cod)
        subgrupo = to_str(row.get("Subgrupo")).upper() or extrair_subgrupo(cod)
        desc = to_str(row.get("Descrição"))
        mat_freq = to_str(row.get("Materiais Frequentes"))
        dureza = to_str(row.get("Dureza"))
        resist = to_str(row.get("Resistência"))

        label = f"{cod} — {desc}" if desc else cod

        grupos.append({
            "codigo": cod,
            "label": label,
            "descricao": desc,
            "iso": iso_clean,
            "iso_raw": iso_raw,
            "subgrupo": subgrupo,
            "materiais_frequentes": mat_freq,
            "dureza": dureza,
            "resistencia": resist,
            "origem": sheet_name,
        })

    return grupos


def exportar_grupos_mmg(xls: pd.ExcelFile) -> list[dict]:
    grupos_antigos = processar_aba_mmg(xls, SHEET_MMG)
    grupos_novos = processar_aba_mmg(xls, SHEET_MMG_NEW)
    return grupos_antigos + grupos_novos


def main():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"Ficheiro Excel não encontrado: {EXCEL_PATH.resolve()}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    xls = pd.ExcelFile(EXCEL_PATH)

    mapa_familias = ler_mapa_familias(xls)
    familias = exportar_familias(mapa_familias)
    referencias = exportar_catalogo(xls, mapa_familias)
    parametros = exportar_parametros(xls, mapa_familias)
    grupos_mmg = exportar_grupos_mmg(xls)

    out_familias = OUTPUT_DIR / "familias.json"
    out_referencias = OUTPUT_DIR / "referencias.json"
    out_parametros = OUTPUT_DIR / "furacao_parametros.json"
    out_grupos_mmg = OUTPUT_DIR / "grupos_mmg.json"

    out_familias.write_text(json.dumps(familias, ensure_ascii=False, indent=2), encoding="utf-8")
    out_referencias.write_text(json.dumps(referencias, ensure_ascii=False, indent=2), encoding="utf-8")
    out_parametros.write_text(json.dumps(parametros, ensure_ascii=False, indent=2), encoding="utf-8")
    out_grupos_mmg.write_text(json.dumps(grupos_mmg, ensure_ascii=False, indent=2), encoding="utf-8")

    suportados = sum(1 for p in parametros if p["suportado"])
    qtd_antigos = sum(1 for g in grupos_mmg if g.get("origem") == SHEET_MMG)
    qtd_novos = sum(1 for g in grupos_mmg if g.get("origem") == SHEET_MMG_NEW)
    print(f"[OK] {out_familias}: {len(familias)} famílias exportadas.")
    print(f"[OK] {out_referencias}: {len(referencias)} referências exportadas.")
    print(f"[OK] {out_parametros}: {len(parametros)} registos ({suportados} com parâmetros ativos).")
    print(f"[OK] {out_grupos_mmg}: {len(grupos_mmg)} grupos MMG exportados ({qtd_antigos} MAPAL_MMG + {qtd_novos} MAPAL_MMG_NEW).")


if __name__ == "__main__":
    main()