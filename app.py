<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora de Corte — Brocas Integrais</title>
    <style>
        :root {
            --bg: #0f172a;
            --card: #1e293b;
            --card-2: #0b1220;
            --border: #334155;
            --text: #f1f5f9;
            --muted: #94a3b8;
            --accent: #38bdf8;
            --accent-2: #22c55e;
            --warn: #f59e0b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 16px;
            line-height: 1.45;
        }
        .container { max-width: 980px; margin: 0 auto; }
        h1 { font-size: 1.35rem; margin-bottom: 12px; color: var(--accent); }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 12px;
            background: var(--card);
            padding: 14px;
            border-radius: 10px;
            border: 1px solid var(--border);
            margin-bottom: 14px;
        }
        label {
            display: flex;
            flex-direction: column;
            gap: 5px;
            font-size: 0.82rem;
            color: var(--muted);
        }
        select, input {
            background: var(--card-2);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 0.92rem;
        }
        select:disabled { opacity: 0.45; cursor: not-allowed; }
        .results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 10px;
            margin-bottom: 14px;
        }
        .box {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
        }
        .box .k { font-size: 0.76rem; color: var(--muted); text-transform: uppercase; }
        .box .v { font-size: 1.25rem; font-weight: 700; color: var(--accent-2); margin-top: 2px; }
        .box .sub { font-size: 0.78rem; color: var(--muted); margin-top: 2px; }
        .note {
            background: var(--card-2);
            border-left: 3px solid var(--warn);
            padding: 10px 12px;
            border-radius: 6px;
            font-size: 0.82rem;
            color: var(--muted);
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Parâmetros de Corte — Brocas Integrais</h1>

    <div class="grid">
        <label>
            1. Linha
            <select id="selLinha">
                <option value="expert">Expert Line</option>
                <option value="performance">Performance Line</option>
                <option value="basic">Basic Line</option>
            </select>
        </label>

        <label>
            2. Categoria
            <select id="selCategoria">
                <option value="solid">Brocas Integrais (Solid)</option>
            </select>
        </label>

        <label>
            3. Refrigeração
            <select id="selRefrig">
                <option value="int">Interna (Emulsão / Óleo)</option>
                <option value="ext">Externa (Emulsão / Óleo)</option>
                <option value="mql">MQL</option>
                <option value="ar">Ar / A Seco</option>
            </select>
        </label>

        <label>
            4. Modelo
            <select id="selModelo"></select>
        </label>

        <label>
            5. Profundidade (×D)
            <select id="selVariante"></select>
        </label>

        <label>
            6. Material (ISO)
            <select id="selGrupo"></select>
        </label>

        <label>
            7. Diâmetro DC (mm)
            <select id="selDiametro"></select>
            <input id="inpDiametroCustom" type="number" step="0.01" min="0.1" placeholder="Diâmetro custom (mm) — interpola f" style="margin-top:4px;">
        </label>

        <label>
            8. Profundidade Furo L (mm)
            <input id="inpProf" type="number" step="0.1" min="0.1" value="20">
        </label>
    </div>

    <div class="results">
        <div class="box">
            <div class="k">Velocidade Corte (vc)</div>
            <div class="v" id="outVc">—</div>
            <div class="sub">m/min</div>
        </div>
        <div class="box">
            <div class="k">Rotação (n)</div>
            <div class="v" id="outN">—</div>
            <div class="sub">rpm</div>
        </div>
        <div class="box">
            <div class="k">Avanço / Rotação (f)</div>
            <div class="v" id="outF">—</div>
            <div class="sub">mm/rot</div>
        </div>
        <div class="box">
            <div class="k">Avanço Mesa (vf)</div>
            <div class="v" id="outVf">—</div>
            <div class="sub">mm/min</div>
        </div>
        <div class="box">
            <div class="k">Tempo Corte (tc)</div>
            <div class="v" id="outTc">—</div>
            <div class="sub" id="outTcSub">seg (prof. L)</div>
        </div>
        <div class="box">
            <div class="k">Remoção Cavaco (Q)</div>
            <div class="v" id="outQ">—</div>
            <div class="sub">cm³/min</div>
        </div>
    </div>

    <div class="note" id="notaInfo"></div>
</div>

<script>
const dados = {
    scd631: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'Tritan-Drill-Uni-Plus SCD631',
        variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "M1.1", "M1.2", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2", "N1.1", "N1.2", "N1.3", "N1.4", "N2.1", "N2.2", "N2.3"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "M1.2": "M1.2 — Aços inoxidáveis Duplex (< 1000 N/mm²)",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)",
            "N1.1": "N1.1 — Alumínio não ligado e ligado < 3% Si",
            "N1.2": "N1.2 — Alumínio ligado ≤ 7% Si",
            "N1.3": "N1.3 — Alumínio ligado > 7-12% Si",
            "N1.4": "N1.4 — Alumínio ligado > 12% Si",
            "N2.1": "N2.1 — Cobre não ligado (< 300 N/mm²)",
            "N2.2": "N2.2 — Cobre ligado (> 300 N/mm²)",
            "N2.3": "N2.3 — Latão, bronze (< 1200 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:115, ext:105, mql:105, ar:0}, f: [0.22, 0.27, 0.34, 0.42, 0.51, 0.59] },
            "P1.2": { vc: {int:105, ext:85, mql:85, ar:0}, f: [0.27, 0.34, 0.42, 0.53, 0.64, 0.74] },
            "P2.1": { vc: {int:115, ext:100, mql:100, ar:0}, f: [0.25, 0.32, 0.40, 0.50, 0.60, 0.70] },
            "P2.2": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.21, 0.26, 0.32, 0.40, 0.48, 0.55] },
            "P3.1": { vc: {int:85, ext:75, mql:75, ar:0}, f: [0.23, 0.29, 0.36, 0.45, 0.54, 0.63] },
            "P3.2": { vc: {int:70, ext:65, mql:65, ar:0}, f: [0.19, 0.24, 0.30, 0.37, 0.44, 0.51] },
            "P3.3": { vc: {int:70, ext:50, mql:60, ar:0}, f: [0.16, 0.19, 0.29, 0.24, 0.34, 0.40] },
            "P5.1": { vc: {int:115, ext:100, mql:100, ar:0}, f: [0.25, 0.32, 0.40, 0.50, 0.60, 0.70] },
            "M1.1": { vc: {int:55, ext:35, mql:35, ar:0}, f: [0.11, 0.14, 0.18, 0.22, 0.27, 0.31] },
            "M1.2": { vc: {int:140, ext:100, mql:100, ar:100}, f: [0.31, 0.41, 0.53, 0.68, 0.84, 0.98] },
            "K1.1": { vc: {int:185, ext:140, mql:115, ar:140}, f: [0.30, 0.39, 0.50, 0.64, 0.78, 0.91] },
            "K2.1": { vc: {int:115, ext:85, mql:85, ar:0}, f: [0.27, 0.35, 0.44, 0.55, 0.67, 0.78] },
            "K2.2": { vc: {int:70, ext:45, mql:60, ar:0}, f: [0.14, 0.18, 0.28, 0.22, 0.33, 0.38] },
            "K2.3": { vc: {int:105, ext:90, mql:90, ar:0}, f: [0.29, 0.37, 0.47, 0.59, 0.72, 0.84] },
            "K3.1": { vc: {int:90, ext:80, mql:80, ar:0}, f: [0.25, 0.31, 0.48, 0.38, 0.57, 0.66] },
            "K3.2": { vc: {int:345, ext:230, mql:290, ar:0}, f: [0.22, 0.27, 0.34, 0.42, 0.51, 0.59] },
            "N1.1": { vc: {int:290, ext:205, mql:230, ar:0}, f: [0.27, 0.35, 0.55, 0.44, 0.67, 0.78] },
            "N1.2": { vc: {int:255, ext:205, mql:175, ar:0}, f: [0.27, 0.35, 0.55, 0.44, 0.67, 0.78] },
            "N1.3": { vc: {int:205, ext:175, mql:140, ar:0}, f: [0.27, 0.35, 0.55, 0.44, 0.67, 0.78] },
            "N1.4": { vc: {int:140, ext:105, mql:0, ar:0}, f: [0.20, 0.26, 0.41, 0.33, 0.50, 0.58] },
            "N2.1": { vc: {int:230, ext:185, mql:185, ar:140}, f: [0.31, 0.41, 0.68, 0.53, 0.84, 0.98] },
            "N2.2": { vc: {int:230, ext:185, mql:185, ar:140}, f: [0.31, 0.41, 0.68, 0.53, 0.84, 0.98] },
            "N2.3": { vc: {int:230, ext:185, mql:185, ar:140}, f: [0.31, 0.41, 0.68, 0.53, 0.84, 0.98] }
        }
    },
    scd221: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Speed-Drill-Uni SCD221',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P5.1", "P6.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P4.1": "P4.1 — Aços inoxidáveis ferríticos e martensíticos",
            "P5.1": "P5.1 — Aço fundido",
            "P6.1": "P6.1 — Aços fundidos inoxidáveis",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:170, ext:155, mql:155, ar:0}, f: [0.11, 0.14, 0.23, 0.18, 0.30, 0.36] },
            "P1.2": { vc: {int:155, ext:130, mql:130, ar:0}, f: [0.14, 0.18, 0.22, 0.29, 0.37, 0.45] },
            "P2.1": { vc: {int:170, ext:145, mql:145, ar:0}, f: [0.13, 0.17, 0.21, 0.27, 0.35, 0.43] },
            "P2.2": { vc: {int:120, ext:100, mql:100, ar:0}, f: [0.11, 0.14, 0.17, 0.22, 0.28, 0.34] },
            "P3.1": { vc: {int:130, ext:110, mql:110, ar:0}, f: [0.11, 0.15, 0.25, 0.19, 0.32, 0.38] },
            "P3.2": { vc: {int:115, ext:100, mql:95, ar:0}, f: [0.10, 0.14, 0.22, 0.17, 0.28, 0.35] },
            "P3.3": { vc: {int:100, ext:75, mql:85, ar:0}, f: [0.10, 0.13, 0.16, 0.20, 0.26, 0.31] },
            "P4.1": { vc: {int:100, ext:75, mql:85, ar:0}, f: [0.08, 0.10, 0.16, 0.13, 0.21, 0.25] },
            "P5.1": { vc: {int:170, ext:145, mql:145, ar:0}, f: [0.13, 0.17, 0.27, 0.21, 0.35, 0.43] },
            "P6.1": { vc: {int:100, ext:85, mql:75, ar:0}, f: [0.08, 0.10, 0.13, 0.16, 0.21, 0.25] },
            "K1.1": { vc: {int:150, ext:105, mql:105, ar:105}, f: [0.13, 0.19, 0.26, 0.35, 0.45, 0.54] },
            "K2.1": { vc: {int:200, ext:150, mql:125, ar:150}, f: [0.13, 0.18, 0.25, 0.33, 0.42, 0.50] },
            "K2.2": { vc: {int:125, ext:95, mql:95, ar:0}, f: [0.12, 0.16, 0.22, 0.28, 0.36, 0.43] },
            "K2.3": { vc: {int:75, ext:50, mql:65, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "K3.1": { vc: {int:115, ext:100, mql:100, ar:0}, f: [0.13, 0.18, 0.23, 0.31, 0.39, 0.46] },
            "K3.2": { vc: {int:100, ext:90, mql:90, ar:0}, f: [0.11, 0.15, 0.19, 0.25, 0.31, 0.36] }
        }
    },
    scd231: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-180°-Drill SCD231',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
            "P1.2": { vc: {int:70, ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "P2.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.08, 0.11, 0.14, 0.19, 0.24, 0.28] },
            "P2.2": { vc: {int:55, ext:50, mql:50, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.22] },
            "P3.1": { vc: {int:60, ext:50, mql:50, ar:0}, f: [0.07, 0.10, 0.13, 0.17, 0.21, 0.25] },
            "P3.2": { vc: {int:50, ext:45, mql:45, ar:0}, f: [0.06, 0.08, 0.11, 0.14, 0.17, 0.21] },
            "P3.3": { vc: {int:50, ext:40, mql:35, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.16] },
            "P5.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.08, 0.11, 0.14, 0.19, 0.24, 0.28] },
            "K1.1": { vc: {int:95, ext:70, mql:70, ar:70}, f: [0.09, 0.14, 0.19, 0.25, 0.33, 0.39] },
            "K2.1": { vc: {int:130, ext:95, mql:80, ar:95}, f: [0.10, 0.13, 0.18, 0.24, 0.30, 0.36] },
            "K2.2": { vc: {int:80, ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
            "K2.3": { vc: {int:50, ext:40, mql:30, ar:0}, f: [0.06, 0.08, 0.11, 0.14, 0.17, 0.21] },
            "K3.1": { vc: {int:70, ext:65, mql:65, ar:0}, f: [0.09, 0.13, 0.17, 0.22, 0.28, 0.33] },
            "K3.2": { vc: {int:65, ext:55, mql:55, ar:0}, f: [0.08, 0.11, 0.14, 0.18, 0.22, 0.26] }
        }
    },
    scd241: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-180°-Drill-Alu SCD241 (Com Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["N1.1", "N1.2", "N1.3", "N1.4", "N2.1", "N2.2", "N2.3"],
        gruposNames: {
            "N1.1": "N1.1 — Alumínio não ligado e ligado < 3% Si",
            "N1.2": "N1.2 — Alumínio ligado ≤ 7% Si",
            "N1.3": "N1.3 — Alumínio ligado > 7-12% Si",
            "N1.4": "N1.4 — Alumínio ligado > 12% Si",
            "N2.1": "N2.1 — Cobre não ligado e de baixa liga (< 300 N/mm²)",
            "N2.2": "N2.2 — Cobre ligado (> 300 N/mm²)",
            "N2.3": "N2.3 — Latão, bronze (< 1200 N/mm²)"
        },
        grupos: {
            "N1.1": { vc: {int:240, ext:160, mql:200, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
            "N1.2": { vc: {int:200, ext:145, mql:160, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
            "N1.3": { vc: {int:175, ext:145, mql:120, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
            "N1.4": { vc: {int:145, ext:95, mql:120, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
            "N2.1": { vc: {int:110, ext:80, mql:0, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
            "N2.2": { vc: {int:95, ext:70, mql:0, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
            "N2.3": { vc: {int:160, ext:130, mql:130, ar:95}, f: [0.09, 0.14, 0.19, 0.25, 0.33, 0.39] }
        }
    },
    scd661: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'SCD661 (Tritan-Drill-Steel)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "M1.1", "K1.1", "K2.1"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:115, ext:105, mql:105, ar:100}, f: [0.24, 0.30, 0.37, 0.46, 0.56, 0.65] },
            "P1.2": { vc: {int:105, ext:85, mql:85, ar:80}, f: [0.30, 0.37, 0.46, 0.58, 0.70, 0.81] },
            "P2.1": { vc: {int:115, ext:100, mql:100, ar:90}, f: [0.28, 0.35, 0.44, 0.55, 0.66, 0.77] },
            "P2.2": { vc: {int:80, ext:70, mql:70, ar:60}, f: [0.24, 0.29, 0.36, 0.44, 0.53, 0.61] },
            "P3.1": { vc: {int:85, ext:75, mql:75, ar:70}, f: [0.25, 0.31, 0.39, 0.49, 0.60, 0.69] },
            "P3.2": { vc: {int:70, ext:65, mql:65, ar:60}, f: [0.21, 0.26, 0.33, 0.41, 0.49, 0.56] },
            "P3.3": { vc: {int:70, ext:50, mql:60, ar:45}, f: [0.18, 0.21, 0.26, 0.32, 0.38, 0.43] },
            "M1.1": { vc: {int:55, ext:35, mql:35, ar:30}, f: [0.11, 0.14, 0.18, 0.22, 0.27, 0.31] },
            "K1.1": { vc: {int:185, ext:115, mql:140, ar:100}, f: [0.34, 0.43, 0.55, 0.70, 0.85, 1.00] },
            "K2.1": { vc: {int:115, ext:85, mql:85, ar:75}, f: [0.30, 0.38, 0.48, 0.61, 0.74, 0.86] }
        }
    },
    scd621: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'SCD621 (MEGA-Speed-Drill-Steel)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "M1.1", "K1.1"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:170, ext:155, mql:155, ar:150}, f: [0.13, 0.17, 0.22, 0.29, 0.36, 0.43] },
            "P1.2": { vc: {int:155, ext:130, mql:130, ar:120}, f: [0.16, 0.21, 0.28, 0.36, 0.45, 0.54] },
            "P2.1": { vc: {int:170, ext:145, mql:145, ar:130}, f: [0.15, 0.20, 0.26, 0.34, 0.43, 0.51] },
            "P2.2": { vc: {int:120, ext:100, mql:100, ar:90}, f: [0.13, 0.17, 0.21, 0.27, 0.34, 0.40] },
            "P3.1": { vc: {int:130, ext:110, mql:110, ar:100}, f: [0.13, 0.18, 0.23, 0.30, 0.39, 0.46] },
            "P3.2": { vc: {int:100, ext:95, mql:95, ar:85}, f: [0.12, 0.15, 0.20, 0.25, 0.32, 0.37] },
            "P3.3": { vc: {int:100, ext:75, mql:85, ar:70}, f: [0.10, 0.12, 0.16, 0.20, 0.25, 0.29] },
            "M1.1": { vc: {int:65, ext:40, mql:40, ar:35}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.23] },
            "K1.1": { vc: {int:150, ext:105, mql:105, ar:95}, f: [0.14, 0.21, 0.28, 0.38, 0.49, 0.59] }
        }
    },
    scd411: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Speed-Drill-Inox SCD411 (Com Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P5.1", "P6.1", "M1.1", "M1.2", "M2.1", "M3.1", "S1.1", "S2.1", "S2.2", "S3.1", "S3.2", "S4.1", "S5.1"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P4.1": "P4.1 — Aços inoxidáveis ferríticos e martensíticos",
            "P5.1": "P5.1 — Aço fundido",
            "P6.1": "P6.1 — Aços fundidos inoxidáveis ferríticos/martensíticos",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "M1.2": "M1.2 — Aços inoxidáveis Duplex (< 1000 N/mm²)",
            "M2.1": "M2.1 — Aços fundidos austeníticos (< 700 N/mm²)",
            "M3.1": "M3.1 — Aços fundidos Duplex (< 1000 N/mm²)",
            "S1.1": "S1.1 — Titânio e ligas de titânio (< 400 N/mm²)",
            "S2.1": "S2.1 — Titânio e ligas de titânio (< 1200 N/mm²)",
            "S2.2": "S2.2 — Titânio e ligas de titânio (> 1200 N/mm²)",
            "S3.1": "S3.1 — Níquel não ligado e ligado (< 900 N/mm²)",
            "S3.2": "S3.2 — Níquel não ligado e ligado (> 900 N/mm²)",
            "S4.1": "S4.1 — Superligas de alta temperatura (Ni, Co, Fe)",
            "S5.1": "S5.1 — Ligas de tungsténio e molibdénio"
        },
        grupos: {
            "P1.1": { vc: {int:150, ext:135, mql:135, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "P1.2": { vc: {int:135, ext:115, mql:115, ar:0}, f: [0.11, 0.15, 0.19, 0.25, 0.31, 0.37] },
            "P2.1": { vc: {int:150, ext:130, mql:130, ar:0}, f: [0.10, 0.14, 0.18, 0.23, 0.30, 0.35] },
            "P2.2": { vc: {int:105, ext:90, mql:90, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "P3.1": { vc: {int:115, ext:100, mql:100, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.27, 0.32] },
            "P3.2": { vc: {int:90, ext:85, mql:85, ar:0}, f: [0.08, 0.10, 0.13, 0.17, 0.22, 0.26] },
            "P3.3": { vc: {int:90, ext:70, mql:75, ar:0}, f: [0.07, 0.09, 0.11, 0.14, 0.17, 0.20] },
            "P4.1": { vc: {int:70, ext:55, mql:60, ar:0}, f: [0.06, 0.08, 0.11, 0.14, 0.18, 0.21] },
            "P5.1": { vc: {int:150, ext:130, mql:130, ar:0}, f: [0.10, 0.14, 0.18, 0.23, 0.30, 0.35] },
            "P6.1": { vc: {int:70, ext:60, mql:55, ar:0}, f: [0.06, 0.08, 0.11, 0.14, 0.18, 0.21] },
            "M1.1": { vc: {int:80, ext:50, mql:50, ar:0}, f: [0.08, 0.10, 0.13, 0.17, 0.22, 0.26] },
            "M1.2": { vc: {int:75, ext:45, mql:45, ar:0}, f: [0.07, 0.09, 0.11, 0.15, 0.19, 0.22] },
            "M2.1": { vc: {int:80, ext:50, mql:50, ar:0}, f: [0.08, 0.10, 0.13, 0.17, 0.22, 0.26] },
            "M3.1": { vc: {int:75, ext:45, mql:45, ar:0}, f: [0.07, 0.09, 0.11, 0.15, 0.19, 0.22] },
            "S1.1": { vc: {int:35, ext:25, mql:25, ar:0}, f: [0.06, 0.08, 0.11, 0.14, 0.18, 0.21] },
            "S2.1": { vc: {int:30, ext:20, mql:20, ar:0}, f: [0.05, 0.07, 0.09, 0.12, 0.15, 0.18] },
            "S2.2": { vc: {int:25, ext:20, mql:20, ar:0}, f: [0.04, 0.06, 0.07, 0.10, 0.12, 0.14] },
            "S3.1": { vc: {int:20, ext:10, mql:10, ar:0}, f: [0.05, 0.07, 0.09, 0.12, 0.15, 0.18] },
            "S3.2": { vc: {int:20, ext:10, mql:10, ar:0}, f: [0.04, 0.06, 0.07, 0.10, 0.12, 0.14] },
            "S4.1": { vc: {int:20, ext:10, mql:10, ar:0}, f: [0.04, 0.06, 0.07, 0.10, 0.12, 0.14] },
            "S5.1": { vc: {int:0, ext:0, mql:0, ar:0}, f: [0.07, 0.10, 0.13, 0.17, 0.21, 0.25] }
        }
    },
    scd421: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Speed-Drill-Iron SCD421 (Com Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "K1.1": { vc: {int:170, ext:120, mql:120, ar:120}, f: [0.15, 0.21, 0.29, 0.40, 0.51, 0.61] },
            "K2.1": { vc: {int:225, ext:170, mql:170, ar:140}, f: [0.15, 0.21, 0.28, 0.37, 0.48, 0.57] },
            "K2.2": { vc: {int:140, ext:105, mql:105, ar:105}, f: [0.14, 0.19, 0.32, 0.25, 0.41, 0.49] },
            "K2.3": { vc: {int:85, ext:55, mql:70, ar:0}, f: [0.10, 0.13, 0.17, 0.22, 0.27, 0.32] },
            "K3.1": { vc: {int:125, ext:110, mql:110, ar:0}, f: [0.15, 0.20, 0.35, 0.26, 0.44, 0.52] },
            "K3.2": { vc: {int:110, ext:100, mql:100, ar:0}, f: [0.13, 0.17, 0.22, 0.28, 0.35, 0.41] }
        }
    },
    scd271: {
        linha: 'expert', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Drill-Composite-UDX SCD271 (Com Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 } },
        diametros: [3.00, 4.00, 5.50, 7.50, 10.00, 12.00],
        gruposList: ["C1.1", "C1.2", "C1.3", "C2.1"],
        gruposNames: {
            "C1.1": "C1.1 — Matriz plástica, reforçada com fibra de aramida (AFRP)",
            "C1.2": "C1.2 — Matriz plástica (termofixa), CFRP / GFRP",
            "C1.3": "C1.3 — Matriz plástica (termoplástica), CFRP / GFRP",
            "C2.1": "C2.1 — Matriz de carbono, reforçada com fibra de carbono (CFC)"
        },
        grupos: {
            "C1.1": { vc: {int:90, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
            "C1.2": { vc: {int:75, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
            "C1.3": { vc: {int:75, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
            "C2.1": { vc: {int:90, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] }
        }
    },
    scd270: {
        linha: 'expert', categoria: 'solid', temRefrigInt: false,
        nome: 'MEGA-Drill-Composite-UDX SCD270 (Sem Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 } },
        diametros: [3.00, 4.00, 5.50, 7.50, 10.00, 12.00],
        gruposList: ["C1.1", "C1.2", "C1.3", "C2.1"],
        gruposNames: {
            "C1.1": "C1.1 — Matriz plástica, reforçada com fibra de aramida (AFRP)",
            "C1.2": "C1.2 — Matriz plástica (termofixa), CFRP / GFRP",
            "C1.3": "C1.3 — Matriz plástica (termoplástica), CFRP / GFRP",
            "C2.1": "C2.1 — Matriz de carbono, reforçada com fibra de carbono (CFC)"
        },
        grupos: {
            "C1.1": { vc: {ext:90, mql:90, ar:90}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
            "C1.2": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
            "C1.3": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
            "C2.1": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] }
        }
    },
    scd600: {
        linha: 'performance', categoria: 'solid', temRefrigInt: false,
        nome: 'MEGA-Drill-Steel-Plus SCD600 (Sem Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P5.1", "P6.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2", "H1.1", "H1.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P4.1": "P4.1 — Aços inoxidáveis ferríticos e martensíticos",
            "P5.1": "P5.1 — Aço fundido",
            "P6.1": "P6.1 — Aços fundidos inoxidáveis ferríticos/martensíticos",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido esferoidal GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido esferoidal GJV / Maleável GJM (> 500 N/mm²)",
            "H1.1": "H1.1 — Aços temperados / Aço fundido (< 44 HRC)",
            "H1.2": "H1.2 — Aços temperados / Aço fundido (< 55 HRC)"
        },
        grupos: {
            "P1.1": { vc: {ext:100, mql:100, ar:0}, f: [0.10, 0.13, 0.17, 0.22, 0.28, 0.33] },
            "P1.2": { vc: {ext:85, mql:85, ar:0}, f: [0.12, 0.16, 0.21, 0.27, 0.34, 0.41] },
            "P2.1": { vc: {ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.38] },
            "P2.2": { vc: {ext:65, mql:65, ar:0}, f: [0.10, 0.13, 0.16, 0.21, 0.26, 0.30] },
            "P3.1": { vc: {ext:70, mql:70, ar:0}, f: [0.10, 0.14, 0.18, 0.23, 0.29, 0.35] },
            "P3.2": { vc: {ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "P3.3": { vc: {ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.22] },
            "P4.1": { vc: {ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.23] },
            "P5.1": { vc: {ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.38] },
            "P6.1": { vc: {ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.23] },
            "K1.1": { vc: {ext:85, mql:85, ar:85}, f: [0.13, 0.19, 0.26, 0.35, 0.45, 0.54] },
            "K2.1": { vc: {ext:100, mql:120, ar:120}, f: [0.13, 0.18, 0.25, 0.33, 0.42, 0.50] },
            "K2.2": { vc: {ext:75, mql:75, ar:0}, f: [0.12, 0.16, 0.22, 0.28, 0.36, 0.43] },
            "K2.3": { vc: {ext:40, mql:50, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "K3.1": { vc: {ext:80, mql:80, ar:0}, f: [0.13, 0.18, 0.23, 0.31, 0.39, 0.46] },
            "K3.2": { vc: {ext:70, mql:70, ar:0}, f: [0.11, 0.15, 0.19, 0.25, 0.31, 0.36] },
            "H1.1": { vc: {ext:90, mql:90, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "H1.2": { vc: {ext:25, mql:25, ar:0}, f: [0.05, 0.06, 0.08, 0.11, 0.14, 0.16] }
        }
    },
    scd601: {
        linha: 'performance', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Drill-Steel-Plus SCD601 (Com Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P5.1", "P6.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2", "H1.1", "H1.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P4.1": "P4.1 — Aços inoxidáveis ferríticos e martensíticos",
            "P5.1": "P5.1 — Aço fundido",
            "P6.1": "P6.1 — Aços fundidos inoxidáveis ferríticos/martensíticos",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido esferoidal GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido esferoidal GJV / Maleável GJM (> 500 N/mm²)",
            "H1.1": "H1.1 — Aços temperados / Aço fundido (< 44 HRC)",
            "H1.2": "H1.2 — Aços temperados / Aço fundido (< 55 HRC)"
        },
        grupos: {
            "P1.1": { vc: {int:110, ext:100, mql:100, ar:0}, f: [0.10, 0.13, 0.17, 0.22, 0.28, 0.33] },
            "P1.2": { vc: {int:100, ext:85, mql:85, ar:0}, f: [0.12, 0.16, 0.21, 0.27, 0.34, 0.41] },
            "P2.1": { vc: {int:110, ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.38] },
            "P2.2": { vc: {int:75, ext:65, mql:65, ar:0}, f: [0.10, 0.13, 0.16, 0.21, 0.26, 0.30] },
            "P3.1": { vc: {int:85, ext:70, mql:70, ar:0}, f: [0.10, 0.14, 0.18, 0.23, 0.29, 0.35] },
            "P3.2": { vc: {int:65, ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "P3.3": { vc: {int:65, ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.22] },
            "P4.1": { vc: {int:65, ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.23] },
            "P5.1": { vc: {int:110, ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.38] },
            "P6.1": { vc: {int:65, ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.23] },
            "K1.1": { vc: {int:120, ext:85, mql:85, ar:85}, f: [0.13, 0.19, 0.26, 0.35, 0.45, 0.54] },
            "K2.1": { vc: {int:160, ext:100, mql:120, ar:120}, f: [0.13, 0.18, 0.25, 0.33, 0.42, 0.50] },
            "K2.2": { vc: {int:100, ext:75, mql:75, ar:0}, f: [0.12, 0.16, 0.22, 0.28, 0.36, 0.43] },
            "K2.3": { vc: {int:60, ext:40, mql:50, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "K3.1": { vc: {int:90, ext:80, mql:80, ar:0}, f: [0.13, 0.18, 0.23, 0.31, 0.39, 0.46] },
            "K3.2": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.11, 0.15, 0.19, 0.25, 0.31, 0.36] },
            "H1.1": { vc: {int:90, ext:90, mql:90, ar:0}, f: [0.09, 0.12, 0.15, 0.19, 0.24, 0.28] },
            "H1.2": { vc: {int:25, ext:25, mql:25, ar:0}, f: [0.05, 0.06, 0.08, 0.11, 0.14, 0.16] }
        }
    },
    scd610: {
        linha: 'performance', categoria: 'solid', temRefrigInt: false,
        nome: 'MEGA-Quadro-Drill-Plus SCD610 (Sem Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {ext:100, mql:100, ar:0}, f: [0.10, 0.13, 0.17, 0.22, 0.28, 0.33] },
            "P1.2": { vc: {ext:85, mql:85, ar:0}, f: [0.12, 0.16, 0.27, 0.21, 0.34, 0.41] },
            "P2.1": { vc: {ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.26, 0.20, 0.33, 0.38] },
            "P2.2": { vc: {ext:65, mql:65, ar:0}, f: [0.10, 0.13, 0.21, 0.16, 0.26, 0.30] },
            "P3.1": { vc: {ext:70, mql:70, ar:0}, f: [0.10, 0.14, 0.18, 0.23, 0.29, 0.35] },
            "P3.2": { vc: {ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.19, 0.15, 0.24, 0.28] },
            "P3.3": { vc: {ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.22] },
            "P5.1": { vc: {ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.26, 0.20, 0.33, 0.38] },
            "K1.1": { vc: {ext:95, mql:95, ar:95}, f: [0.13, 0.19, 0.35, 0.26, 0.45, 0.54] },
            "K2.1": { vc: {ext:110, mql:130, ar:130}, f: [0.13, 0.18, 0.25, 0.33, 0.42, 0.50] },
            "K2.2": { vc: {ext:85, mql:85, ar:0}, f: [0.12, 0.16, 0.28, 0.22, 0.36, 0.43] },
            "K2.3": { vc: {ext:45, mql:55, ar:0}, f: [0.09, 0.12, 0.19, 0.15, 0.24, 0.28] },
            "K3.1": { vc: {ext:90, mql:90, ar:0}, f: [0.13, 0.18, 0.23, 0.31, 0.39, 0.46] },
            "K3.2": { vc: {ext:75, mql:75, ar:0}, f: [0.11, 0.15, 0.19, 0.25, 0.31, 0.36] }
        }
    },
    scd611: {
        linha: 'performance', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Quadro-Drill-Plus SCD611 (Com Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:110, ext:100, mql:100, ar:0}, f: [0.10, 0.13, 0.17, 0.22, 0.28, 0.33] },
            "P1.2": { vc: {int:100, ext:85, mql:85, ar:0}, f: [0.12, 0.16, 0.27, 0.21, 0.34, 0.41] },
            "P2.1": { vc: {int:110, ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.26, 0.20, 0.33, 0.38] },
            "P2.2": { vc: {int:75, ext:65, mql:65, ar:0}, f: [0.10, 0.13, 0.21, 0.16, 0.26, 0.30] },
            "P3.1": { vc: {int:85, ext:70, mql:70, ar:0}, f: [0.10, 0.14, 0.18, 0.23, 0.29, 0.35] },
            "P3.2": { vc: {int:65, ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.19, 0.15, 0.24, 0.28] },
            "P3.3": { vc: {int:65, ext:50, mql:55, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.22] },
            "P5.1": { vc: {int:110, ext:95, mql:95, ar:0}, f: [0.11, 0.15, 0.26, 0.20, 0.33, 0.38] },
            "K1.1": { vc: {int:130, ext:95, mql:95, ar:95}, f: [0.13, 0.19, 0.35, 0.26, 0.45, 0.54] },
            "K2.1": { vc: {int:175, ext:110, mql:130, ar:130}, f: [0.13, 0.18, 0.25, 0.33, 0.42, 0.50] },
            "K2.2": { vc: {int:110, ext:85, mql:85, ar:0}, f: [0.12, 0.16, 0.28, 0.22, 0.36, 0.43] },
            "K2.3": { vc: {int:65, ext:45, mql:55, ar:0}, f: [0.09, 0.12, 0.19, 0.15, 0.24, 0.28] },
            "K3.1": { vc: {int:100, ext:90, mql:90, ar:0}, f: [0.13, 0.18, 0.23, 0.31, 0.39, 0.46] },
            "K3.2": { vc: {int:90, ext:75, mql:75, ar:0}, f: [0.11, 0.15, 0.19, 0.25, 0.31, 0.36] }
        }
    },
    scd371: {
        linha: 'performance', categoria: 'solid', temRefrigInt: true,
        nome: 'MICRO-Drill-Steel SCD371 (Com Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "M1.1", "M1.2", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "M1.2": "M1.2 — Aços inoxidáveis Duplex (< 1000 N/mm²)",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
            "P1.2": { vc: {int:70, ext:60, mql:60, ar:0}, f: [0.04, 0.05, 0.07, 0.06, 0.08, 0.10] },
            "P2.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.04, 0.05, 0.06, 0.07, 0.08, 0.09] },
            "P2.2": { vc: {int:55, ext:50, mql:50, ar:0}, f: [0.04, 0.05, 0.05, 0.06, 0.07, 0.08] },
            "P3.1": { vc: {int:60, ext:50, mql:50, ar:0}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
            "P3.2": { vc: {int:50, ext:45, mql:45, ar:0}, f: [0.04, 0.04, 0.05, 0.04, 0.06, 0.07] },
            "P3.3": { vc: {int:50, ext:35, mql:40, ar:0}, f: [0.03, 0.04, 0.05, 0.04, 0.05, 0.06] },
            "P5.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.04, 0.05, 0.07, 0.06, 0.08, 0.09] },
            "M1.1": { vc: {int:40, ext:25, mql:25, ar:0}, f: [0.03, 0.03, 0.04, 0.03, 0.05, 0.06] },
            "M1.2": { vc: {int:95, ext:70, mql:70, ar:70}, f: [0.03, 0.04, 0.06, 0.05, 0.08, 0.11] },
            "K1.1": { vc: {int:130, ext:80, mql:95, ar:95}, f: [0.04, 0.05, 0.07, 0.06, 0.09, 0.11] },
            "K2.1": { vc: {int:80, ext:60, mql:60, ar:0}, f: [0.04, 0.05, 0.05, 0.07, 0.08, 0.10] },
            "K2.2": { vc: {int:70, ext:65, mql:65, ar:0}, f: [0.04, 0.05, 0.07, 0.06, 0.09, 0.11] },
            "K2.3": { vc: {int:65, ext:55, mql:55, ar:0}, f: [0.04, 0.05, 0.07, 0.06, 0.08, 0.09] },
            "K3.1": { vc: {int:55, ext:45, mql:45, ar:0}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
            "K3.2": { vc: {int:45, ext:40, mql:40, ar:0}, f: [0.03, 0.04, 0.05, 0.04, 0.06, 0.07] }
        }
    },
    scd140: {
        linha: 'performance', categoria: 'solid', temRefrigInt: false,
        nome: 'MEGA-Drill-Hardened SCD140 (Sem Refrig. Interna)',
        variantes: { '4xD': { ratio: 4 } },
        diametros: [2.50, 3.62, 5.25, 7.61, 11.04, 16.00],
        gruposList: ["H1.1", "H1.2", "H2.1", "H2.2", "H2.3"],
        gruposNames: {
            "H1.1": "H1.1 — Aço temperado / Aço fundido (< 44 HRC)",
            "H1.2": "H1.2 — Aço temperado / Aço fundido (< 55 HRC)",
            "H2.1": "H2.1 — Aço temperado / Aço fundido (< 60 HRC)",
            "H2.2": "H2.2 — Aço temperado / Aço fundido (< 65 HRC)",
            "H2.3": "H2.3 — Aço temperado / Aço fundido (< 68 HRC)"
        },
        grupos: {
            "H1.1": { vc: {ext:80, mql:80, ar:0}, f: [0.07, 0.09, 0.11, 0.02, 0.19, 0.20] },
            "H1.2": { vc: {ext:30, mql:30, ar:0}, f: [0.05, 0.06, 0.10, 0.08, 0.13, 0.16] },
            "H2.1": { vc: {ext:30, mql:30, ar:0}, f: [0.04, 0.05, 0.09, 0.07, 0.11, 0.13] },
            "H2.2": { vc: {ext:20, mql:20, ar:0}, f: [0.03, 0.04, 0.05, 0.06, 0.08, 0.09] },
            "H2.3": { vc: {ext:15, mql:15, ar:0}, f: [0.03, 0.04, 0.05, 0.06, 0.08, 0.09] }
        }
    },
    scd131: {
        linha: 'performance', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Drill-Alu SCD131 (Com Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["N1.1", "N1.2", "N1.3", "N1.4", "N2.1", "N2.2", "N2.3"],
        gruposNames: {
            "N1.1": "N1.1 — Alumínio não ligado e ligado < 3% Si",
            "N1.2": "N1.2 — Alumínio ligado ≤ 7% Si",
            "N1.3": "N1.3 — Alumínio ligado > 7-12% Si",
            "N1.4": "N1.4 — Alumínio ligado > 12% Si",
            "N2.1": "N2.1 — Cobre não ligado (< 300 N/mm²)",
            "N2.2": "N2.2 — Cobre ligado (> 300 N/mm²)",
            "N2.3": "N2.3 — Latão, bronze (< 1200 N/mm²)"
        },
        grupos: {
            "N1.1": { vc: {int:300, ext:200, mql:250, ar:200}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "N1.2": { vc: {int:250, ext:180, mql:200, ar:160}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
            "N1.3": { vc: {int:220, ext:150, mql:180, ar:160}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
            "N1.4": { vc: {int:180, ext:120, mql:150, ar:120}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
            "N2.1": { vc: {int:140, ext:100, mql:120, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "N2.2": { vc: {int:120, ext:90, mql:100, ar:0}, f: [0.11, 0.15, 0.26, 0.20, 0.33, 0.39] },
            "N2.3": { vc: {int:200, ext:160, mql:160, ar:0}, f: [0.09, 0.14, 0.19, 0.25, 0.33, 0.39] }
        }
    },
    scd250: {
        linha: 'performance', categoria: 'solid', temRefrigInt: false,
        nome: 'MEGA-Drill-Composite-MD SCD250 (Sem Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 } },
        diametros: [3.00, 4.00, 5.50, 7.50, 10.00, 12.00],
        gruposList: ["N3.1", "N3.2", "C1.1", "C1.2", "C1.3", "C2.1", "C3.1"],
        gruposNames: {
            "N3.1": "N3.1 — Grafite, > 8 µm",
            "N3.2": "N3.2 — Grafite, ≤ 8 µm",
            "C1.1": "C1.1 — Matriz plástica, reforçada com fibra de aramida (AFRP)",
            "C1.2": "C1.2 — Matriz plástica (termofixa), CFRP / GFRP",
            "C1.3": "C1.3 — Matriz plástica (termoplástica), CFRP / GFRP",
            "C2.1": "C2.1 — Matriz de carbono, reforçada com fibra de carbono (CFC)",
            "C3.1": "C3.1 — Matriz metálica (MMC)"
        },
        grupos: {
            "N3.1": { vc: {ext:200, mql:200, ar:200}, f: [0.07, 0.09, 0.11, 0.14, 0.16, 0.18] },
            "N3.2": { vc: {ext:200, mql:200, ar:200}, f: [0.07, 0.09, 0.11, 0.14, 0.16, 0.18] },
            "C1.1": { vc: {ext:90, mql:90, ar:90}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
            "C1.2": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
            "C1.3": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
            "C2.1": { vc: {ext:400, mql:400, ar:400}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
            "C3.1": { vc: {ext:400, mql:400, ar:400}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] }
        }
    },
    scd120: {
        linha: 'performance', categoria: 'solid', temRefrigInt: false,
        nome: 'MEGA-Drill-Inox SCD120 (Sem Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P5.1", "P6.1", "M1.1", "M1.2", "M2.1", "M3.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2", "N2.1", "N2.2", "N2.3"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P4.1": "P4.1 — Aços inoxidáveis ferríticos e martensíticos",
            "P5.1": "P5.1 — Aço fundido",
            "P6.1": "P6.1 — Aços fundidos inoxidáveis",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "M1.2": "M1.2 — Aços inoxidáveis Duplex (< 1000 N/mm²)",
            "M2.1": "M2.1 — Aços fundidos austeníticos (< 700 N/mm²)",
            "M3.1": "M3.1 — Aços fundidos Duplex (< 1000 N/mm²)",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)",
            "N2.1": "N2.1 — Cobre não ligado (< 300 N/mm²)",
            "N2.2": "N2.2 — Cobre ligado (> 300 N/mm²)",
            "N2.3": "N2.3 — Latão, bronze (< 1200 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {ext:90, mql:90, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
            "P1.2": { vc: {ext:75, mql:75, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "P2.1": { vc: {ext:85, mql:85, ar:0}, f: [0.08, 0.11, 0.19, 0.14, 0.24, 0.28] },
            "P2.2": { vc: {ext:60, mql:60, ar:0}, f: [0.07, 0.09, 0.15, 0.12, 0.19, 0.22] },
            "P3.1": { vc: {ext:65, mql:65, ar:0}, f: [0.07, 0.10, 0.13, 0.17, 0.21, 0.25] },
            "P3.2": { vc: {ext:55, mql:55, ar:0}, f: [0.06, 0.08, 0.14, 0.11, 0.17, 0.21] },
            "P3.3": { vc: {ext:50, mql:45, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.16] },
            "P4.1": { vc: {ext:45, mql:50, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.17] },
            "P5.1": { vc: {ext:85, mql:85, ar:0}, f: [0.08, 0.11, 0.19, 0.14, 0.24, 0.28] },
            "P6.1": { vc: {ext:50, mql:45, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.17] },
            "M1.1": { vc: {ext:35, mql:35, ar:0}, f: [0.06, 0.08, 0.14, 0.11, 0.18, 0.21] },
            "M1.2": { vc: {ext:30, mql:30, ar:0}, f: [0.05, 0.07, 0.12, 0.09, 0.15, 0.18] },
            "M2.1": { vc: {ext:35, mql:35, ar:0}, f: [0.06, 0.08, 0.14, 0.11, 0.18, 0.21] },
            "M3.1": { vc: {ext:30, mql:30, ar:0}, f: [0.05, 0.07, 0.12, 0.09, 0.15, 0.18] },
            "K1.1": { vc: {ext:85, mql:85, ar:85}, f: [0.12, 0.17, 0.24, 0.32, 0.41, 0.49] },
            "K2.1": { vc: {ext:120, mql:100, ar:120}, f: [0.12, 0.17, 0.22, 0.30, 0.38, 0.45] },
            "K2.2": { vc: {ext:75, mql:75, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
            "K2.3": { vc: {ext:50, mql:40, ar:0}, f: [0.08, 0.10, 0.17, 0.13, 0.22, 0.26] },
            "K3.1": { vc: {ext:80, mql:80, ar:0}, f: [0.12, 0.16, 0.28, 0.21, 0.35, 0.42] },
            "K3.2": { vc: {ext:70, mql:70, ar:0}, f: [0.10, 0.13, 0.22, 0.17, 0.28, 0.33] },
            "N2.1": { vc: {ext:100, mql:0, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "N2.2": { vc: {ext:90, mql:0, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
            "N2.3": { vc: {ext:160, mql:160, ar:120}, f: [0.12, 0.17, 0.24, 0.32, 0.41, 0.49] }
        }
    },
    scd121: {
        linha: 'performance', categoria: 'solid', temRefrigInt: true,
        nome: 'MEGA-Drill-Inox SCD121 (Com Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P5.1", "P6.1", "M1.1", "M1.2", "M2.1", "M3.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2", "N2.1", "N2.2", "N2.3"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P4.1": "P4.1 — Aços inoxidáveis ferríticos e martensíticos",
            "P5.1": "P5.1 — Aço fundido",
            "P6.1": "P6.1 — Aços fundidos inoxidáveis",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "M1.2": "M1.2 — Aços inoxidáveis Duplex (< 1000 N/mm²)",
            "M2.1": "M2.1 — Aços fundidos austeníticos (< 700 N/mm²)",
            "M3.1": "M3.1 — Aços fundidos Duplex (< 1000 N/mm²)",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido GJV / Maleável GJM (> 500 N/mm²)",
            "N2.1": "N2.1 — Cobre não ligado (< 300 N/mm²)",
            "N2.2": "N2.2 — Cobre ligado (> 300 N/mm²)",
            "N2.3": "N2.3 — Latão, bronze (< 1200 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:100, ext:90, mql:90, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
            "P1.2": { vc: {int:90, ext:75, mql:75, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "P2.1": { vc: {int:100, ext:85, mql:85, ar:0}, f: [0.08, 0.11, 0.19, 0.14, 0.24, 0.28] },
            "P2.2": { vc: {int:70, ext:60, mql:60, ar:0}, f: [0.07, 0.09, 0.15, 0.12, 0.19, 0.22] },
            "P3.1": { vc: {int:75, ext:65, mql:65, ar:0}, f: [0.07, 0.10, 0.13, 0.17, 0.21, 0.25] },
            "P3.2": { vc: {int:60, ext:55, mql:55, ar:0}, f: [0.06, 0.08, 0.14, 0.11, 0.17, 0.21] },
            "P3.3": { vc: {int:60, ext:50, mql:45, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.16] },
            "P4.1": { vc: {int:60, ext:45, mql:50, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.17] },
            "P5.1": { vc: {int:100, ext:85, mql:85, ar:0}, f: [0.08, 0.11, 0.19, 0.14, 0.24, 0.28] },
            "P6.1": { vc: {int:60, ext:50, mql:45, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.17] },
            "M1.1": { vc: {int:55, ext:35, mql:35, ar:0}, f: [0.06, 0.08, 0.14, 0.11, 0.18, 0.21] },
            "M1.2": { vc: {int:50, ext:30, mql:30, ar:0}, f: [0.05, 0.07, 0.12, 0.09, 0.15, 0.18] },
            "M2.1": { vc: {int:55, ext:35, mql:35, ar:0}, f: [0.06, 0.08, 0.14, 0.11, 0.18, 0.21] },
            "M3.1": { vc: {int:50, ext:30, mql:30, ar:0}, f: [0.05, 0.07, 0.12, 0.09, 0.15, 0.18] },
            "K1.1": { vc: {int:120, ext:85, mql:85, ar:85}, f: [0.12, 0.17, 0.24, 0.32, 0.41, 0.49] },
            "K2.1": { vc: {int:160, ext:120, mql:100, ar:120}, f: [0.12, 0.17, 0.22, 0.30, 0.38, 0.45] },
            "K2.2": { vc: {int:100, ext:75, mql:75, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
            "K2.3": { vc: {int:60, ext:50, mql:40, ar:0}, f: [0.08, 0.10, 0.17, 0.13, 0.22, 0.26] },
            "K3.1": { vc: {int:90, ext:80, mql:80, ar:0}, f: [0.12, 0.16, 0.28, 0.21, 0.35, 0.42] },
            "K3.2": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.10, 0.13, 0.22, 0.17, 0.28, 0.33] },
            "N2.1": { vc: {int:140, ext:100, mql:0, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
            "N2.2": { vc: {int:120, ext:90, mql:0, ar:0}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
            "N2.3": { vc: {int:200, ext:160, mql:160, ar:120}, f: [0.12, 0.17, 0.24, 0.32, 0.41, 0.49] }
        }
    },
    scd350: {
        linha: 'basic', categoria: 'solid', temRefrigInt: false,
        nome: 'ECU-Drill-Uni SCD350 (Sem Refrig. Interna)',
        variantes: { '4xD': { ratio: 4 }, '6xD': { ratio: 6 } },
        diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "M1.1", "M1.2", "M2.1", "M3.1", "K2.1", "K2.2", "K2.3"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "M1.2": "M1.2 — Aços inoxidáveis ferríticos/austeníticos (Duplex) (< 1000 N/mm²)",
            "M2.1": "M2.1 — Aços fundidos inoxidáveis/refratários austeníticos (< 700 N/mm²)",
            "M3.1": "M3.1 — Aços fundidos inoxidáveis ferríticos/austeníticos (Duplex) (< 1000 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {ext:70, mql:70, ar:0}, f: [0.03, 0.05, 0.07, 0.10, 0.16, 0.21] },
            "P1.2": { vc: {ext:55, mql:55, ar:0}, f: [0.04, 0.06, 0.08, 0.13, 0.20, 0.27] },
            "P2.1": { vc: {ext:65, mql:65, ar:0}, f: [0.04, 0.05, 0.08, 0.12, 0.18, 0.25] },
            "P2.2": { vc: {ext:45, mql:45, ar:0}, f: [0.04, 0.05, 0.07, 0.10, 0.15, 0.20] },
            "P3.1": { vc: {ext:50, mql:50, ar:0}, f: [0.03, 0.05, 0.07, 0.11, 0.17, 0.23] },
            "P3.2": { vc: {ext:40, mql:40, ar:0}, f: [0.03, 0.04, 0.06, 0.09, 0.14, 0.18] },
            "P3.3": { vc: {ext:40, mql:35, ar:0}, f: [0.03, 0.04, 0.05, 0.11, 0.11, 0.14] },
            "P5.1": { vc: {ext:65, mql:65, ar:0}, f: [0.04, 0.05, 0.08, 0.12, 0.18, 0.25] },
            "M1.1": { vc: {ext:30, mql:30, ar:0}, f: [0.03, 0.04, 0.06, 0.09, 0.14, 0.19] },
            "M1.2": { vc: {ext:25, mql:25, ar:0}, f: [0.02, 0.03, 0.05, 0.08, 0.12, 0.16] },
            "M2.1": { vc: {ext:30, mql:30, ar:0}, f: [0.03, 0.04, 0.06, 0.09, 0.14, 0.19] },
            "M3.1": { vc: {ext:25, mql:25, ar:0}, f: [0.02, 0.03, 0.05, 0.08, 0.12, 0.16] },
            "K2.1": { vc: {ext:90, mql:75, ar:90}, f: [0.05, 0.07, 0.12, 0.19, 0.30, 0.41] },
            "K2.2": { vc: {ext:55, mql:55, ar:0}, f: [0.04, 0.07, 0.11, 0.17, 0.26, 0.35] },
            "K2.3": { vc: {ext:55, mql:55, ar:0}, f: [0.04, 0.07, 0.11, 0.17, 0.26, 0.35] }
        }
    },
    scd351: {
        linha: 'basic', categoria: 'solid', temRefrigInt: true,
        nome: 'ECU-Drill-Uni SCD351 (Com Refrig. Interna)',
        variantes: { '4xD': { ratio: 4 }, '6xD': { ratio: 6 } },
        diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "M1.1", "M1.2", "M2.1", "M3.1", "K2.1", "K2.2", "K2.3"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "M1.1": "M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)",
            "M1.2": "M1.2 — Aços inoxidáveis ferríticos/austeníticos (Duplex) (< 1000 N/mm²)",
            "M2.1": "M2.1 — Aços fundidos inoxidáveis/refratários austeníticos (< 700 N/mm²)",
            "M3.1": "M3.1 — Aços fundidos inoxidáveis ferríticos/austeníticos (Duplex) (< 1000 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:75, ext:70, mql:70, ar:70}, f: [0.03, 0.05, 0.07, 0.10, 0.16, 0.21] },
            "P1.2": { vc: {int:70, ext:55, mql:55, ar:55}, f: [0.04, 0.06, 0.08, 0.13, 0.20, 0.27] },
            "P2.1": { vc: {int:75, ext:65, mql:65, ar:65}, f: [0.04, 0.05, 0.08, 0.12, 0.18, 0.25] },
            "P2.2": { vc: {int:55, ext:45, mql:45, ar:45}, f: [0.04, 0.05, 0.07, 0.10, 0.15, 0.20] },
            "P3.1": { vc: {int:55, ext:50, mql:50, ar:50}, f: [0.03, 0.05, 0.07, 0.11, 0.17, 0.23] },
            "P3.2": { vc: {int:45, ext:40, mql:40, ar:40}, f: [0.03, 0.04, 0.06, 0.09, 0.14, 0.18] },
            "P3.3": { vc: {int:45, ext:40, mql:35, ar:35}, f: [0.03, 0.04, 0.05, 0.11, 0.11, 0.14] },
            "P5.1": { vc: {int:75, ext:65, mql:65, ar:65}, f: [0.04, 0.05, 0.08, 0.12, 0.18, 0.25] },
            "M1.1": { vc: {int:45, ext:30, mql:30, ar:30}, f: [0.03, 0.04, 0.06, 0.09, 0.14, 0.19] },
            "M1.2": { vc: {int:45, ext:25, mql:25, ar:25}, f: [0.02, 0.03, 0.05, 0.08, 0.12, 0.16] },
            "M2.1": { vc: {int:45, ext:30, mql:30, ar:30}, f: [0.03, 0.04, 0.06, 0.09, 0.14, 0.19] },
            "M3.1": { vc: {int:45, ext:25, mql:25, ar:25}, f: [0.02, 0.03, 0.05, 0.08, 0.12, 0.16] },
            "K2.1": { vc: {int:120, ext:90, mql:75, ar:90}, f: [0.05, 0.07, 0.12, 0.19, 0.30, 0.41] },
            "K2.2": { vc: {int:75, ext:55, mql:55, ar:55}, f: [0.04, 0.07, 0.11, 0.17, 0.26, 0.35] },
            "K2.3": { vc: {int:75, ext:55, mql:55, ar:55}, f: [0.04, 0.07, 0.11, 0.17, 0.26, 0.35] }
        }
    },
    scd360: {
        linha: 'basic', categoria: 'solid', temRefrigInt: false,
        nome: 'SCD360 (ECU-Drill-Steel - Sem Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido esferoidal GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido esferoidal GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {ext:70, mql:70, ar:0}, f: [0.04, 0.06, 0.08, 0.13, 0.20, 0.27] },
            "P1.2": { vc: {ext:55, mql:55, ar:0}, f: [0.05, 0.07, 0.11, 0.16, 0.24, 0.33] },
            "P2.1": { vc: {ext:65, mql:65, ar:0}, f: [0.05, 0.07, 0.10, 0.15, 0.23, 0.31] },
            "P2.2": { vc: {ext:45, mql:45, ar:0}, f: [0.05, 0.06, 0.13, 0.09, 0.18, 0.25] },
            "P3.1": { vc: {ext:50, mql:50, ar:0}, f: [0.04, 0.06, 0.14, 0.09, 0.21, 0.28] },
            "P3.2": { vc: {ext:40, mql:40, ar:0}, f: [0.04, 0.05, 0.12, 0.08, 0.17, 0.23] },
            "P3.3": { vc: {ext:35, mql:40, ar:0}, f: [0.04, 0.05, 0.06, 0.09, 0.13, 0.18] },
            "P5.1": { vc: {ext:65, mql:65, ar:0}, f: [0.05, 0.07, 0.15, 0.10, 0.23, 0.31] },
            "K1.1": { vc: {ext:40, mql:35, ar:0}, f: [0.03, 0.04, 0.09, 0.06, 0.14, 0.19] },
            "K2.1": { vc: {ext:60, mql:60, ar:60}, f: [0.04, 0.07, 0.12, 0.20, 0.32, 0.44] },
            "K2.2": { vc: {ext:80, mql:70, ar:80}, f: [0.05, 0.07, 0.12, 0.19, 0.30, 0.41] },
            "K2.3": { vc: {ext:50, mql:50, ar:0}, f: [0.04, 0.07, 0.11, 0.17, 0.26, 0.35] },
            "K3.1": { vc: {ext:35, mql:25, ar:0}, f: [0.04, 0.05, 0.08, 0.12, 0.17, 0.23] },
            "K3.2": { vc: {ext:55, mql:55, ar:0}, f: [0.05, 0.07, 0.11, 0.18, 0.27, 0.38] }
        }
    },
    scd361: {
        linha: 'basic', categoria: 'solid', temRefrigInt: true,
        nome: 'SCD361 (ECU-Drill-Steel - Com Refrig. Interna)',
        variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
        diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
        gruposList: ["P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P5.1", "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2"],
        gruposNames: {
            "P1.1": "P1.1 — Aços estruturais, corte livre (< 700 N/mm²)",
            "P1.2": "P1.2 — Aços estruturais, corte livre (< 1200 N/mm²)",
            "P2.1": "P2.1 — Aços de têmpera, nitretados (< 900 N/mm²)",
            "P2.2": "P2.2 — Aços de têmpera, nitretados (< 1400 N/mm²)",
            "P3.1": "P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)",
            "P3.2": "P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)",
            "P3.3": "P3.3 — Aços para ferramentas, rolamento (< 1500 N/mm²)",
            "P5.1": "P5.1 — Aço fundido",
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "K2.3": "K2.3 — Ferro fundido esferoidal GJS (> 800 N/mm²)",
            "K3.1": "K3.1 — Ferro fundido esferoidal GJV / Maleável GJM (< 500 N/mm²)",
            "K3.2": "K3.2 — Ferro fundido esferoidal GJV / Maleável GJM (> 500 N/mm²)"
        },
        grupos: {
            "P1.1": { vc: {int:75, ext:70, mql:70, ar:70}, f: [0.04, 0.06, 0.08, 0.13, 0.20, 0.27] },
            "P1.2": { vc: {int:70, ext:55, mql:55, ar:55}, f: [0.05, 0.07, 0.11, 0.16, 0.24, 0.33] },
            "P2.1": { vc: {int:75, ext:65, mql:65, ar:65}, f: [0.05, 0.07, 0.10, 0.15, 0.23, 0.31] },
            "P2.2": { vc: {int:55, ext:45, mql:45, ar:45}, f: [0.05, 0.06, 0.13, 0.09, 0.18, 0.25] },
            "P3.1": { vc: {int:55, ext:50, mql:50, ar:50}, f: [0.04, 0.06, 0.14, 0.09, 0.21, 0.28] },
            "P3.2": { vc: {int:45, ext:40, mql:40, ar:40}, f: [0.04, 0.05, 0.12, 0.08, 0.17, 0.23] },
            "P3.3": { vc: {int:45, ext:35, mql:40, ar:40}, f: [0.04, 0.05, 0.06, 0.09, 0.13, 0.18] },
            "P5.1": { vc: {int:75, ext:65, mql:65, ar:65}, f: [0.05, 0.07, 0.15, 0.10, 0.23, 0.31] },
            "K1.1": { vc: {int:45, ext:40, mql:35, ar:35}, f: [0.03, 0.04, 0.09, 0.06, 0.14, 0.19] },
            "K2.1": { vc: {int:80, ext:60, mql:60, ar:60}, f: [0.04, 0.07, 0.12, 0.20, 0.32, 0.44] },
            "K2.2": { vc: {int:110, ext:80, mql:70, ar:80}, f: [0.05, 0.07, 0.12, 0.19, 0.30, 0.41] },
            "K2.3": { vc: {int:70, ext:50, mql:50, ar:50}, f: [0.04, 0.07, 0.11, 0.17, 0.26, 0.35] },
            "K3.1": { vc: {int:40, ext:35, mql:25, ar:25}, f: [0.04, 0.05, 0.08, 0.12, 0.17, 0.23] },
            "K3.2": { vc: {int:60, ext:55, mql:55, ar:55}, f: [0.05, 0.07, 0.11, 0.18, 0.27, 0.38] }
        }
    },
    scd211: {
        linha: 'basic', categoria: 'solid', temRefrigInt: true,
        nome: 'ECU-G-Drill SCD211 (Com Refrig. Interna)',
        variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
        diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
        gruposList: ["K1.1", "K2.1", "K2.2", "N1.2", "N1.3", "N1.4", "N2.3"],
        gruposNames: {
            "K1.1": "K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)",
            "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 500 N/mm²)",
            "K2.2": "K2.2 — Ferro fundido esferoidal GJS (≤ 800 N/mm²)",
            "N1.2": "N1.2 — Alumínio ligado ≤ 7% Si",
            "N1.3": "N1.3 — Alumínio ligado > 7-12% Si",
            "N1.4": "N1.4 — Alumínio ligado > 12% Si",
            "N2.3": "N2.3 — Latão, bronze (< 1200 N/mm²)"
        },
        grupos: {
            "K1.1": { vc: {int:90, ext:65, mql:65, ar:65}, f: [0.08, 0.12, 0.16, 0.22, 0.29, 0.34] },
            "K2.1": { vc: {int:120, ext:90, mql:75, ar:90}, f: [0.08, 0.12, 0.16, 0.21, 0.27, 0.32] },
            "K2.2": { vc: {int:75, ext:55, mql:55, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
            "N1.2": { vc: {int:215, ext:155, mql:170, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
            "N1.3": { vc: {int:185, ext:155, mql:130, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
            "N1.4": { vc: {int:155, ext:100, mql:130, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
            "N2.3": { vc: {int:160, ext:130, mql:130, ar:95}, f: [0.08, 0.12, 0.16, 0.22, 0.29, 0.34] }
        }
    }
};

const elLinha = document.getElementById('selLinha');
const elCategoria = document.getElementById('selCategoria');
const elRefrig = document.getElementById('selRefrig');
const elModelo = document.getElementById('selModelo');
const elVariante = document.getElementById('selVariante');
const elGrupo = document.getElementById('selGrupo');
const elDiametro = document.getElementById('selDiametro');
const elDiamCustom = document.getElementById('inpDiametroCustom');
const elProf = document.getElementById('inpProf');
const elNota = document.getElementById('notaInfo');

function interpolarLinear(xs, ys, x) {
    if (x <= xs[0]) return ys[0];
    if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
    for (let i = 0; i < xs.length - 1; i++) {
        if (x >= xs[i] && x <= xs[i + 1]) {
            const t = (x - xs[i]) / (xs[i + 1] - xs[i]);
            return ys[i] + t * (ys[i + 1] - ys[i]);
        }
    }
    return ys[0];
}

function popularModelos() {
    const linha = elLinha.value;
    const cat = elCategoria.value;
    const refrig = elRefrig.value;

    const modelos = Object.entries(dados).filter(([, d]) => {
        if (d.linha !== linha || d.categoria !== cat) return false;
        if (refrig === 'int' && !d.temRefrigInt) return false;
        return true;
    });

    const prev = elModelo.value;
    elModelo.innerHTML = '';
    modelos.forEach(([key, d]) => {
        const opt = document.createElement('option');
        opt.value = key;
        opt.textContent = d.nome;
        elModelo.appendChild(opt);
    });
    if (modelos.some(([k]) => k === prev)) elModelo.value = prev;
    popularVariantesEGrupos();
}

function popularVariantesEGrupos() {
    const d = dados[elModelo.value];
    if (!d) return;

    const prevVar = elVariante.value;
    elVariante.innerHTML = '';
    Object.keys(d.variantes).forEach(vKey => {
        const opt = document.createElement('option');
        opt.value = vKey;
        opt.textContent = vKey;
        elVariante.appendChild(opt);
    });
    if (d.variantes[prevVar]) elVariante.value = prevVar;

    const prevGrp = elGrupo.value;
    elGrupo.innerHTML = '';
    d.gruposList.forEach(gKey => {
        const opt = document.createElement('option');
        opt.value = gKey;
        opt.textContent = d.gruposNames[gKey] || gKey;
        elGrupo.appendChild(opt);
    });
    if (d.gruposList.includes(prevGrp)) elGrupo.value = prevGrp;

    const prevDia = elDiametro.value;
    elDiametro.innerHTML = '';
    d.diametros.forEach((dia, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = `${dia.toFixed(2)} mm`;
        elDiametro.appendChild(opt);
    });
    if (elDiametro.options[prevDia]) elDiametro.value = prevDia;

    calcular();
}

function calcular() {
    const d = dados[elModelo.value];
    if (!d) return;

    const grpKey = elGrupo.value;
    const grp = d.grupos[grpKey];
    const refrig = elRefrig.value;
    const varKey = elVariante.value;
    const ratio = d.variantes[varKey]?.ratio ?? 5;

    const customVal = parseFloat(elDiamCustom.value);
    const usarCustom = !Number.isNaN(customVal) && customVal > 0;
    const dc = usarCustom ? customVal : d.diametros[parseInt(elDiametro.value, 10) || 0];

    const f = usarCustom
        ? interpolarLinear(d.diametros, grp.f, dc)
        : grp.f[parseInt(elDiametro.value, 10) || 0];

    const vc = grp.vc[refrig] ?? 0;
    const n = vc > 0 && dc > 0 ? (vc * 1000) / (Math.PI * dc) : 0;
    const vf = n * f;
    const prof = Math.max(0.1, parseFloat(elProf.value) || 0);
    const tcMin = vf > 0 ? prof / vf : 0;
    const tcSeg = tcMin * 60;
    const qCm3Min = (Math.PI * Math.pow(dc / 2, 2) * vf) / 1000;

    document.getElementById('outVc').textContent = vc > 0 ? vc.toFixed(0) : '0';
    document.getElementById('outN').textContent = n > 0 ? Math.round(n).toLocaleString('pt-PT') : '—';
    document.getElementById('outF').textContent = f > 0 ? f.toFixed(3) : '—';
    document.getElementById('outVf').textContent = vf > 0 ? Math.round(vf).toLocaleString('pt-PT') : '—';
    document.getElementById('outTc').textContent = tcSeg > 0 ? `${tcSeg.toFixed(1)} s` : '—';
    document.getElementById('outTcSub').textContent = `${tcMin.toFixed(2)} min (L = ${prof} mm)`;
    document.getElementById('outQ').textContent = qCm3Min > 0 ? qCm3Min.toFixed(2) : '—';

    const maxProfRecomendada = (dc * ratio).toFixed(1);
    const avisoRefrig = vc === 0
        ? 'Atenção: vc = 0 para este modo de refrigeração neste material/modelo.'
        : 'Valores base de catálogo; ajustar conforme rigidez da fixação, balanço e condição da máquina.';

    elNota.textContent = `Variante ${varKey} (prof. máx. ref. ≈ ${maxProfRecomendada} mm para DC = ${dc.toFixed(2)} mm) · ${avisoRefrig}`;
}

[elLinha, elCategoria, elRefrig].forEach(el => el.addEventListener('change', popularModelos));
[elModelo, elVariante, elGrupo, elDiametro].forEach(el => el.addEventListener('change', calcular));
[elDiamCustom, elProf].forEach(el => el.addEventListener('input', calcular));

popularModelos();
</script>
</body>
</html>
