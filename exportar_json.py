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
    return f"{val:.1f}"


def _limpar_str(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return ""
    return str(val).strip()


def _norm_key(val):
    return _limpar_str(val).upper()


def _norm_codigo_mmg(val):
    """Normaliza separadores de subcódigo (ex.: 'P1-1' -> 'P1.1') para comparação e cruzamento."""
    s = _limpar_str(val).upper()
    return re.sub(r"\s*-\s*", ".", s)


def _extrair_iso_do_codigo(codigo: str) -> str:
    m = re.match(r"^([A-Z])", _limpar_str(codigo).upper())
    return m.group(1) if m else ""


def _extrair_subgrupo_do_codigo(codigo: str) -> str:
    """Extrai o subgrupo (ex.: 'P1' de 'P1-1' ou 'P1.1') quando a coluna Subgrupo não existe."""
    m = re.match(r"^([A-Z]+\d+)", _limpar_str(codigo).upper())
    return m.group(1) if m else ""


def _norm_col(col_name):
    return re.sub(r"[^a-z0-9]+", "_", str(col_name).strip().lower()).strip("_")


def _extrair_registos_aba_mmg(xls: pd.ExcelFile, sheet_name: str, origem: str) -> list[dict]:
    if sheet_name not in xls.sheet_names:
        return []

    df = pd.read_excel(xls, sheet_name=sheet_name)
    if df.empty:
        return []

    cols_norm = {_norm_col(c): c for c in df.columns}

    def pick_col(*aliases):
        for a in aliases:
            k = _norm_col(a)
            if k in cols_norm:
                return cols_norm[k]
        return None

    c_codigo = pick_col(
        "grupo_de_maquinacao",
        "grupo_mapal_mmg",
        "grupo_mapal",
        "mmg",
        "grupo",
        "codigo",
    )
    c_iso = pick_col("grupo_iso", "grupo_iso_513", "grupo_isso", "iso")
    c_subgrupo = pick_col("subgrupo")
    c_material = pick_col(
        "material_da_peca_workpiece_material",
        "material_da_peca",
        "workpiece_material",
        "material",
    )
    c_estrutura = pick_col(
        "estrutura_composicao_structure_composition",
        "estrutura_composicao",
        "estrutura",
    )
    c_condicao = pick_col("condicao_condition", "condicao")
    c_resistencia = pick_col(
        "resistencia_dureza_strength_hardness_n_mm_hrc",
        "resistencia_a_tracao_r_n_mm_tensile_strength_r_n_mm",
        "resistencia_dureza",
        "resistencia",
    )
    c_dureza = pick_col("dureza_hardness_hb_hrc", "dureza")
    c_freq = pick_col(
        "materiais_frequentes_frequently_machined_workpiece_materials",
        "materiais_frequentes",
        "descricao_1_describition_1",
        "descricao_1",
    )

    registos = []
    for _, row in df.iterrows():
        codigo = _limpar_str(row[c_codigo]) if c_codigo else ""
        if not codigo:
            continue

        material = _limpar_str(row[c_material]) if c_material else ""
        iso = _limpar_str(row[c_iso]).upper() if c_iso else ""
        if not iso:
            iso = _extrair_iso_do_codigo(codigo)

        subgrupo = _limpar_str(row[c_subgrupo]).upper() if c_subgrupo else ""
        if not subgrupo:
            subgrupo = _extrair_subgrupo_do_codigo(codigo)

        estrutura = _limpar_str(row[c_estrutura]) if c_estrutura else ""
        condicao = _limpar_str(row[c_condicao]) if c_condicao else ""
        resistencia = _limpar_str(row[c_resistencia]) if c_resistencia else ""
        dureza = _limpar_str(row[c_dureza]) if c_dureza else ""
        materiais_freq = _limpar_str(row[c_freq]) if c_freq else ""

        detalhes = [
            x for x in [estrutura, condicao, resistencia, dureza]
            if x and x != "-"
        ]
        if material and detalhes:
            label = f"{codigo} — {material} ({' | '.join(detalhes[:2])})"
        elif material:
            label = f"{codigo} — {material}"
        elif detalhes:
            label = f"{codigo} ({' | '.join(detalhes[:2])})"
        else:
            label = codigo

        registos.append({
            "codigo": codigo,
            "codigo_normalizado": _norm_codigo_mmg(codigo),
            "label": label,
            "iso": iso,
            "subgrupo": subgrupo,
            "material": material,
            "estrutura": estrutura,
            "condicao": condicao,
            "resistencia": resistencia,
            "dureza": dureza,
            "materiais_frequentes": materiais_freq,
            "origem": origem,
        })

    return registos


def exportar_grupos_mmg_json(
    excel_path: str = "catalogo_teste.xlsx",
    sheets: tuple[str, ...] = ("MAPAL_MMG", "MAPAL_MMG_NEW"),
    output_path: str = "dados/grupos_mmg.json",
) -> list[dict]:
    xls = pd.ExcelFile(excel_path)
    registos = []
    vistos = set()

    for sheet_name in sheets:
        for item in _extrair_registos_aba_mmg(xls, sheet_name, sheet_name):
            chave = (_norm_key(item["codigo"]), _norm_key(item["origem"]))
            if chave in vistos:
                continue
            vistos.add(chave)
            registos.append(item)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registos, indent=2, ensure_ascii=False), encoding="utf-8")
    return registos


def exportar_familias_json(
    excel_path: str = "catalogo_teste.xlsx",
    sheet_name: str = "Familias",
    output_path: str = "dados/familias.json",
) -> list[dict]:
    xls = pd.ExcelFile(excel_path)
    if sheet_name not in xls.sheet_names:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("[]", encoding="utf-8")
        return []

    df = pd.read_excel(xls, sheet_name=sheet_name)
    if df.empty:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("[]", encoding="utf-8")
        return []

    cols_norm = {_norm_col(c): c for c in df.columns}

    def pick_col(*aliases):
        for a in aliases:
            k = _norm_col(a)
            if k in cols_norm:
                return cols_norm[k]
        return None

    c_fam = pick_col("familia", "family", "codigo", "código")
    c_prod = pick_col("nome_do_produto", "nome produto", "produto", "product_name", "designacao", "designação")
    c_gama = pick_col("gama", "linha", "line")
    c_cat = pick_col("categoria", "category", "tipo_de_operacao", "tipo_operacao", "operacao", "operação")

    registos = []
    for _, row in df.iterrows():
        fam_val = _limpar_str(row[c_fam]) if c_fam else ""
        prod_val = _limpar_str(row[c_prod]) if c_prod else ""
        gama_val = _limpar_str(row[c_gama]) if c_gama else ""
        cat_val = _limpar_str(row[c_cat]) if c_cat else ""

        if not fam_val and not prod_val and not gama_val and not cat_val:
            continue

        registos.append({
            "familia": fam_val,
            "nome_produto": prod_val,
            "gama": gama_val,
            "categoria": cat_val,
        })

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registos, indent=2, ensure_ascii=False), encoding="utf-8")
    return registos


def exportar_json(
    excel_path: str = "dados/parametros_corte.xlsx",
    sheet_name: str = "Parametros_Corte",
    output_path: str = "dados/furacao_parametros.json",
    familias_map: dict[str, dict] | None = None,
) -> list[dict]:
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    registos = []
    familia_atual = None
    col_map = None

    if familias_map is None:
        fams_lista = exportar_familias_json(excel_path=excel_path)
        familias_map = {_norm_key(f["familia"]): f for f in fams_lista if f.get("familia")}

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
            col_map = {"familia": None, "mmg": None, "vc": {}, "f_by_d": {}}
            for idx, val in enumerate(row.tolist()):
                if pd.isna(val):
                    continue
                nome = str(val).strip()
                up = nome.upper()
                if up in {"FAMILIA", "FAMÍLIA", "FAMILY"}:
                    col_map["familia"] = idx
                elif up in {"MMG", "GRUPO", "MAT_GRUPO", "GRUPO_MAT"}:
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
            and primeira.upper() not in {"FAMILIA", "FAMÍLIA", "MMG", "GRUPO"}
            and not re.match(r"^[PMKNHSC]\d+([.-]\d+)?$", primeira.upper())
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

            fam_linha = familia_atual or ""
            if col_map.get("familia") is not None:
                fam_cell = _limpar_str(row.iloc[col_map["familia"]])
                if fam_cell:
                    fam_linha = fam_cell
                    familia_atual = fam_cell

            info_fam = familias_map.get(_norm_key(fam_linha), {})

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
                "familia": fam_linha,
                "nome_produto": info_fam.get("nome_produto", ""),
                "gama": info_fam.get("gama", ""),
                "categoria": info_fam.get("categoria", ""),
                "mmg": mmg_val,
                "mmg_normalizado": _norm_codigo_mmg(mmg_val),
                "vc": vc_entry,
                "suportado": tem_dados,
                "avancos_f": avancos_f,
            })

    # --- REGRA DE HERANÇA AUTOMÁTICA: SCD**1 -> SCD**0 ---
    familias_com_params = {_norm_key(r["familia"]) for r in registos if r.get("familia")}
    registos_herdados = []

    for r in registos:
        fam_norm = _norm_key(r.get("familia", ""))
        if re.match(r"^SCD\d+1$", fam_norm):
            fam_irma_norm = fam_norm[:-1] + "0"
            if fam_irma_norm in familias_map and fam_irma_norm not in familias_com_params:
                info_irma = familias_map[fam_irma_norm]
                vc_irma = dict(r["vc"])
                vc_irma["interna"] = None
                avancos_irma = dict(r["avancos_f"])
                tem_dados_irma = any(v is not None for v in vc_irma.values()) or any(
                    v is not None for v in avancos_irma.values()
                )
                registos_herdados.append({
                    "familia": info_irma.get("familia") or fam_irma_norm,
                    "nome_produto": info_irma.get("nome_produto", r.get("nome_produto", "")),
                    "gama": info_irma.get("gama", r.get("gama", "")),
                    "categoria": info_irma.get("categoria", r.get("categoria", "")),
                    "mmg": r["mmg"],
                    "mmg_normalizado": r.get("mmg_normalizado", _norm_codigo_mmg(r["mmg"])),
                    "vc": vc_irma,
                    "suportado": tem_dados_irma,
                    "avancos_f": avancos_irma,
                })

    registos.extend(registos_herdados)
    # -----------------------------------------------------

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registos, indent=2, ensure_ascii=False), encoding="utf-8")
    return registos


def exportar_referencias_json(
    excel_path: str = "catalogo_teste.xlsx",
    sheet_name: str = "Dimensoes",
    output_path: str = "dados/referencias.json",
    familias_map: dict[str, dict] | None = None,
) -> list[dict]:
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, sheet_name=sheet_name)

    if familias_map is None:
        fams_lista = exportar_familias_json(excel_path=excel_path)
        familias_map = {_norm_key(f["familia"]): f for f in fams_lista if f.get("familia")}

    if df.empty:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("[]", encoding="utf-8")
        return []

    cols_norm = {_norm_col(c): c for c in df.columns}

    def pick_col(*aliases):
        for a in aliases:
            key = _norm_col(a)
            if key in cols_norm:
                return cols_norm[key]
        return None

    c_order = pick_col("order_no", "order no", "orderno", "order", "referencia", "ref")
    c_spec = pick_col("specification", "especificacao", "designacao", "descricao")
    c_fam = pick_col("familia", "family", "modelo")
    c_var = pick_col("variante", "variant", "xd", "x_d")
    c_refrig = pick_col("refrigeracao", "refrig", "coolant", "lubrificacao")
    c_enc = pick_col("encabadouro", "din_6535", "din6535", "shank")
    c_gama = pick_col("gama", "linha", "line")
    c_cat = pick_col("categoria", "category", "operacao", "tipo_operacao")
    c_d1 = pick_col("d1", "diametro", "diametro_d1", "dc")
    c_d2 = pick_col("d2", "diametro_d2", "dcon")
    c_l1 = pick_col("l1", "comp_total", "comprimento_total")
    c_l2 = pick_col("l2", "comp_navalha", "comprimento_navalha", "lcn")
    c_l3 = pick_col("l3", "util_corte", "comprimento_util", "lu")
    c_l4 = pick_col("l4", "comp_encab", "comprimento_encabadouro")

    registos = []
    for _, row in df.iterrows():
        order_val = _limpar_str(row[c_order]) if c_order else ""
        spec_val = _limpar_str(row[c_spec]) if c_spec else ""
        fam_val = _limpar_str(row[c_fam]) if c_fam else ""

        if not order_val and not spec_val and not fam_val:
            continue

        info_fam = familias_map.get(_norm_key(fam_val), {})
        gama_val = info_fam.get("gama") or (_limpar_str(row[c_gama]) if c_gama else "")
        cat_val = info_fam.get("categoria") or (_limpar_str(row[c_cat]) if c_cat else "")
        prod_val = info_fam.get("nome_produto", "")

        item = {
            "order_no": order_val,
            "specification": spec_val,
            "familia": fam_val,
            "nome_produto": prod_val,
            "variante": _limpar_str(row[c_var]) if c_var else "",
            "refrigeracao": _limpar_str(row[c_refrig]) if c_refrig else "",
            "encabadouro": _limpar_str(row[c_enc]) if c_enc else "",
            "gama": gama_val,
            "categoria": cat_val,
            "d1": _parse_num(row[c_d1]) if c_d1 else None,
            "d2": _parse_num(row[c_d2]) if c_d2 else None,
            "l1": _parse_num(row[c_l1]) if c_l1 else None,
            "l2": _parse_num(row[c_l2]) if c_l2 else None,
            "l3": _parse_num(row[c_l3]) if c_l3 else None,
            "l4": _parse_num(row[c_l4]) if c_l4 else None,
        }
        registos.append(item)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registos, indent=2, ensure_ascii=False), encoding="utf-8")
    return registos


def exportar_tudo_json(
    excel_path: str = "catalogo_teste.xlsx",
    output_dir: str = "dados",
) -> dict[str, list[dict]]:
    out_base = Path(output_dir)
    out_base.mkdir(parents=True, exist_ok=True)

    familias = exportar_familias_json(
        excel_path=excel_path,
        sheet_name="Familias",
        output_path=str(out_base / "familias.json"),
    )
    familias_map = {_norm_key(f["familia"]): f for f in familias if f.get("familia")}

    referencias = exportar_referencias_json(
        excel_path=excel_path,
        sheet_name="Dimensoes",
        output_path=str(out_base / "referencias.json"),
        familias_map=familias_map,
    )
    parametros = exportar_json(
        excel_path=excel_path,
        sheet_name="Parametros_Corte",
        output_path=str(out_base / "furacao_parametros.json"),
        familias_map=familias_map,
    )
    grupos_mmg = exportar_grupos_mmg_json(
        excel_path=excel_path,
        sheets=("MAPAL_MMG", "MAPAL_MMG_NEW"),
        output_path=str(out_base / "grupos_mmg.json"),
    )

    return {
        "familias": familias,
        "referencias": referencias,
        "parametros_corte": parametros,
        "grupos_mmg": grupos_mmg,
    }


if __name__ == "__main__":
    exportar_tudo_json()