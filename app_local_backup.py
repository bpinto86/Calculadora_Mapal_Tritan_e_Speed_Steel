import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Calculadora Técnica MAPAL", layout="wide")


@st.cache_data
def load_json(path: str):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def fmt_num(val, decimais: int = 0, sufixo: str = " mm") -> str:
    if val is None:
        return "—"
    return f"{val:.{decimais}f}{sufixo}"


referencias = load_json("dados/referencias.json")
parametros_furacao = load_json("dados/furacao_parametros.json")

operacao = st.radio("Operação", ["Furação", "Fresagem"], horizontal=True)

pesquisa = st.text_input(
    "Pesquisa rápida (Order no., Specification, Família ou Diâmetro)",
    placeholder="Ex.: 30802220, SCD661-1200, SCD361 ou 12.00",
).strip().lower()

candidatos = referencias
if pesquisa:
    candidatos = [
        item for item in referencias
        if pesquisa in str(item.get("order_no", "")).lower()
        or pesquisa in str(item.get("specification", "")).lower()
        or pesquisa in str(item.get("familia", "")).lower()
        or (item.get("d1") is not None and pesquisa in f"{item['d1']:.2f}")
    ]

if operacao == "Furação":
    if not candidatos:
        st.warning("Nenhuma ferramenta encontrada com esse filtro.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        # 1. Diâmetro d1 (vazio por defeito -> mostra todos os diâmetros disponíveis)
        diametros = sorted({c["d1"] for c in candidatos if c.get("d1") is not None})
        d1_sel = col1.selectbox(
            "1. Diâmetro d1 (mm)",
            diametros,
            index=None,
            placeholder="Todos os diâmetros...",
            format_func=lambda d: f"Ø {d:.2f} mm",
        )
        filtrados = [c for c in candidatos if d1_sel is None or c.get("d1") == d1_sel]

        # 2. Variante xD (filtra com base no diâmetro escolhido)
        variantes = sorted({c.get("variante") for c in filtrados if c.get("variante")})
        var_sel = col2.selectbox(
            "2. Variante (xD)",
            variantes,
            index=None,
            placeholder="Todas as variantes...",
        )
        filtrados = [c for c in filtrados if var_sel is None or c.get("variante") == var_sel]

        # 3. Refrigeração (Interna / Externa)
        refrig_opcoes = sorted({c.get("refrigeracao") for c in filtrados if c.get("refrigeracao")})
        refrig_sel = col3.selectbox(
            "3. Refrigeração",
            refrig_opcoes,
            index=None,
            placeholder="Interna ou Externa...",
        )
        filtrados = [c for c in filtrados if refrig_sel is None or c.get("refrigeracao") == refrig_sel]

        # 4. Família (opcional, para afinar se houver várias famílias compatíveis)
        familias = sorted({c.get("familia") for c in filtrados if c.get("familia")})
        fam_sel = col4.selectbox(
            "4. Família (opcional)",
            familias,
            index=None,
            placeholder="Todas as famílias...",
        )
        filtrados = [c for c in filtrados if fam_sel is None or c.get("familia") == fam_sel]

        st.caption(f"Ferramentas compatíveis encontradas: **{len(filtrados)}**")

        if not filtrados:
            st.warning("Nenhuma ferramenta corresponde a essa combinação de filtros.")
        else:
            # Seleção da referência final (vazia se houver várias, ou automática se só sobrar 1)
            default_idx = 0 if len(filtrados) == 1 else None
            rotulos = [
                f"{c.get('familia')} | Ø {fmt_num(c.get('d1'), 2, '')} mm ({c.get('variante') or '—'}) | "
                f"{c.get('refrigeracao') or '—'} — Order: {c.get('order_no')}"
                for c in filtrados
            ]
            idx = st.selectbox(
                "5. Selecionar ferramenta / Order no.",
                range(len(rotulos)),
                index=default_idx,
                placeholder="Escolhe uma das ferramentas compatíveis...",
                format_func=lambda i: rotulos[i],
            )

            if idx is None:
                st.info("Seleciona os filtros acima ou escolhe uma ferramenta na lista para ver as cotas e validar a profundidade.")
            else:
                ferramenta = filtrados[idx]
                st.divider()

                c_ord, c_d1, c_d2 = st.columns(3)
                c_ord.metric("Order no.", ferramenta.get("order_no") or "—")
                c_d1.metric("d1 — Diâmetro de corte", fmt_num(ferramenta.get("d1"), 2))
                c_d2.metric("d2 — Diâmetro encabadouro", fmt_num(ferramenta.get("d2"), 1))

                c_l1, c_l2, c_l3, c_l4 = st.columns(4)
                c_l1.metric("l1 — Comprimento total", fmt_num(ferramenta.get("l1"), 0))
                c_l2.metric("l2 — Comprimento navalha", fmt_num(ferramenta.get("l2"), 0))
                c_l3.metric("l3 — Comprimento útil de corte", fmt_num(ferramenta.get("l3"), 0))
                c_l4.metric("l4 — Comprimento do encabadouro", fmt_num(ferramenta.get("l4"), 0))

                st.caption(
                    f"Família: `{ferramenta.get('familia') or '—'}` | "
                    f"Specification: `{ferramenta.get('specification') or '—'}` | "
                    f"Variante: `{ferramenta.get('variante') or '—'}` | "
                    f"Refrigeração: `{ferramenta.get('refrigeracao') or '—'}`"
                )

                profundidade_furo = st.number_input(
                    "Profundidade do furo L (mm)",
                    min_value=1.0,
                    value=31.0,
                    step=1.0,
                )

                variante_txt = str(ferramenta.get("variante") or "").lower().replace(" ", "")
                mult_xd = 3.0
                if "xd" in variante_txt:
                    try:
                        mult_xd = float(variante_txt.split("xd")[0].replace(",", "."))
                    except ValueError:
                        mult_xd = 3.0

                d1_val = ferramenta.get("d1") or 0.0
                prof_xd = mult_xd * d1_val
                lim_l3 = ferramenta.get("l3") if ferramenta.get("l3") is not None else prof_xd

                if profundidade_furo <= lim_l3:
                    st.success(
                        f"Profundidade dentro do limite do catálogo ({ferramenta.get('variante') or '—'} = {prof_xd:.1f} mm | "
                        f"l3 máx.: {lim_l3:.0f} mm | l4 encabadouro: {fmt_num(ferramenta.get('l4'), 0)})."
                    )
                else:
                    st.error(
                        f"Profundidade a validar com catálogo ({ferramenta.get('variante') or '—'} @ Ø{d1_val:.2f} = {prof_xd:.1f} mm | "
                        f"Lim. l3: {lim_l3:.0f} mm) — **FORA DO LIMITE**"
                    )
else:
    st.info("Módulo de **Fresagem** pronto a receber dados.")