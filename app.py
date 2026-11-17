import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Parâmetros de Corte MAPAL", page_icon="⚙️", layout="wide")

html_content = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Parâmetros de Corte MAPAL</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }
    </style>
</head>
<body class="p-4 md:p-6">
    <div class="max-w-7xl mx-auto space-y-6">
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-800 p-4 rounded-xl border border-slate-700 gap-4">
            <div>
                <div class="flex items-center gap-3">
                    <h1 class="text-xl font-bold text-white">Parâmetros de Corte MAPAL</h1>
                    <span class="bg-blue-600 text-xs px-2.5 py-1 rounded-full font-medium">CATÁLOGO P. 172-173</span>
                </div>
                <p class="text-xs text-slate-400 mt-1">Furação em cheio • Valor direto de catálogo ou interpolação por intervalo</p>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- Painel de Controlo (Esquerda) -->
            <div class="lg:col-span-4 bg-slate-800 p-5 rounded-xl border border-slate-700 space-y-5">
                <h2 class="text-sm font-semibold text-blue-400 uppercase tracking-wider">Configuração da Operação</h2>
                
                <!-- Modelo de Broca -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">1. BROCA DE METAL DURO INTEGRAL</label>
                    <select id="broca" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-blue-500" onchange="atualizarCalculo()">
                        <option value="scd661">SCD661 (Tritan-Drill-Steel)</option>
                        <option value="scd621">SCD621 (MEGA-Speed-Drill-Steel)</option>
                    </select>
                </div>

                <!-- Grupo de Materiais -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">2. GRUPO DE MATERIAIS (MMG)</label>
                    <select id="grupo" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-blue-500" onchange="atualizarCalculo()">
                        <option value="P1.1">P1.1 — Aços estruturais, de corte livre (< 700 N/mm²)</option>
                        <option value="P1.2" selected>P1.2 — Aços estruturais, de corte livre (< 1200 N/mm²)</option>
                        <option value="P2.1">P2.1 — Aços de têmpera, nitretados, liga (< 900 N/mm²)</option>
                        <option value="P2.2">P2.2 — Aços de têmpera, nitretados, liga (< 1400 N/mm²)</option>
                        <option value="P3.1">P3.1 — Aços para ferramentas, rolamento (< 800 N/mm²)</option>
                        <option value="P3.2">P3.2 — Aços para ferramentas, rolamento (< 1000 N/mm²)</option>
                        <option value="M1.1">M1.1 — Aços inoxidáveis austeníticos (< 700 N/mm²)</option>
                        <option value="K1.1">K1.1 — Ferro fundido lamelar GJL (< 300 N/mm²)</option>
                    </select>
                </div>

                <!-- Refrigeração -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">3. REFRIGERAÇÃO</label>
                    <div class="grid grid-cols-4 gap-1 bg-slate-900 p-1 rounded-lg border border-slate-700 text-xs text-center font-medium">
                        <button type="button" onclick="setRefrig('int')" id="ref-int" class="py-2 rounded bg-blue-600 text-white transition">Interna</button>
                        <button type="button" onclick="setRefrig('ext')" id="ref-ext" class="py-2 rounded text-slate-400 hover:text-white transition">Externa</button>
                        <button type="button" onclick="setRefrig('mql')" id="ref-mql" class="py-2 rounded text-slate-400 hover:text-white transition">MQL</button>
                        <button type="button" onclick="setRefrig('ar')" id="ref-ar" class="py-2 rounded text-slate-400 hover:text-white transition">Ar</button>
                    </div>
                </div>

                <!-- Diâmetro Pretendido -->
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <label class="text-xs font-medium text-slate-300">4. DIÂMETRO PRETENDIDO (Ø)</label>
                        <span id="badge-metodo" class="text-[10px] bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded border border-blue-700">Interpolação no Intervalo</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <button onclick="ajustarDiametro(-0.5)" class="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-lg text-white font-bold">-</button>
                        <input type="number" id="diametro" value="8.00" step="0.1" min="1" max="30" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-center text-lg font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        <button onclick="ajustarDiametro(0.5)" class="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-lg text-white font-bold">+</button>
                    </div>
                </div>
            </div>

            <!-- Resultados e Indicadores (Direita) -->
            <div class="lg:col-span-8 space-y-6">
                <!-- Grid de Métricas CNC -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Avanço / Rotação</span>
                        <div class="text-2xl font-bold text-white mt-1" id="res-f">0.3850</div>
                        <span class="text-[10px] text-blue-400">mm/rot</span>
                    </div>
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Velocidade de Corte</span>
                        <div class="text-2xl font-bold text-white mt-1" id="res-vc">105</div>
                        <span class="text-[10px] text-slate-400">m/min</span>
                    </div>
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Rotações (Spindle)</span>
                        <div class="text-2xl font-bold text-white mt-1" id="res-n">4178</div>
                        <span class="text-[10px] text-slate-400">rpm</span>
                    </div>
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Avanço de Trabalho</span>
                        <div class="text-2xl font-bold text-white mt-1" id="res-vf">1608</div>
                        <span class="text-[10px] text-slate-400">mm/min</span>
                    </div>
                </div>

                <!-- Detalhe da Fórmula -->
                <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 space-y-3">
                    <h3 class="text-xs font-semibold text-slate-400 uppercase">Modelo Matemático Aplicado</h3>
                    <div class="bg-slate-900 p-3 rounded-lg border border-slate-700 font-mono text-sm text-cyan-400" id="formula-txt">
                        f = 0.1600 + 0.0400 × 8.00 = 0.4800 mm/rot
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                        <div class="bg-slate-900/50 p-2.5 rounded border border-slate-700/50">
                            <span class="text-slate-400">Intercepção (a)</span>
                            <div class="font-mono font-bold text-white mt-0.5" id="val-a">0.1600 mm/rot</div>
                        </div>
                        <div class="bg-slate-900/50 p-2.5 rounded border border-slate-700/50">
                            <span class="text-slate-400">Declive / Desvio (b)</span>
                            <div class="font-mono font-bold text-white mt-0.5" id="val-b">0.0400 mm/rot·mm</div>
                        </div>
                        <div class="bg-slate-900/50 p-2.5 rounded border border-slate-700/50">
                            <span class="text-slate-400">Estado da Gama</span>
                            <div class="font-bold text-emerald-400 mt-0.5" id="val-estado">Dentro do intervalo consecutivo</div>
                        </div>
                    </div>
                </div>

                <!-- Tabela de Referência -->
                <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 space-y-3">
                    <h3 class="text-xs font-semibold text-slate-400 uppercase">Tabela de Referência do Catálogo MAPAL</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b border-slate-700 text-slate-400">
                                    <th class="pb-2">Diâmetro (Ø)</th>
                                    <th class="pb-2">f Catálogo</th>
                                    <th class="pb-2">Rotações (n)</th>
                                    <th class="pb-2">Avanço (v_f)</th>
                                </tr>
                            </thead>
                            <tbody id="tabela-ref" class="divide-y divide-slate-700/50"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let refrigAtual = 'int';
        const dados = {
            scd661: {
                diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
                grupos: {
                    "P1.1": { vc: {int:115, ext:105, mql:105, ar:100}, f: [0.24, 0.30, 0.37, 0.46, 0.56, 0.65] },
                    "P1.2": { vc: {int:105, ext:85, mql:85, ar:80}, f: [0.30, 0.37, 0.46, 0.58, 0.70, 0.81] },
                    "P2.1": { vc: {int:115, ext:100, mql:100, ar:90}, f: [0.28, 0.35, 0.44, 0.55, 0.66, 0.77] },
                    "P2.2": { vc: {int:80, ext:70, mql:70, ar:60}, f: [0.24, 0.29, 0.36, 0.44, 0.53, 0.61] },
                    "P3.1": { vc: {int:85, ext:75, mql:75, ar:70}, f: [0.25, 0.31, 0.39, 0.49, 0.60, 0.69] },
                    "P3.2": { vc: {int:70, ext:65, mql:65, ar:60}, f: [0.21, 0.26, 0.33, 0.41, 0.49, 0.56] },
                    "M1.1": { vc: {int:55, ext:35, mql:35, ar:30}, f: [0.11, 0.14, 0.18, 0.22, 0.27, 0.31] },
                    "K1.1": { vc: {int:185, ext:115, mql:140, ar:100}, f: [0.34, 0.43, 0.55, 0.70, 0.85, 1.00] }
                }
            },
            scd621: {
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
                grupos: {
                    "P1.1": { vc: {int:170, ext:155, mql:155, ar:150}, f: [0.13, 0.17, 0.22, 0.29, 0.36, 0.43] },
                    "P1.2": { vc: {int:155, ext:130, mql:130, ar:120}, f: [0.16, 0.21, 0.36, 0.28, 0.45, 0.54] },
                    "P2.1": { vc: {int:170, ext:145, mql:145, ar:130}, f: [0.15, 0.20, 0.34, 0.26, 0.43, 0.51] },
                    "P2.2": { vc: {int:120, ext:100, mql:100, ar:90}, f: [0.13, 0.17, 0.21, 0.27, 0.34, 0.40] },
                    "P3.1": { vc: {int:130, ext:110, mql:110, ar:100}, f: [0.13, 0.18, 0.30, 0.23, 0.39, 0.46] },
                    "P3.2": { vc: {int:100, ext:95, mql:95, ar:85}, f: [0.12, 0.15, 0.20, 0.25, 0.32, 0.37] },
                    "M1.1": { vc: {int:65, ext:40, mql:40, ar:35}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.23] },
                    "K1.1": { vc: {int:150, ext:105, mql:105, ar:95}, f: [0.14, 0.21, 0.38, 0.28, 0.49, 0.59] }
                }
            }
        };

        function setRefrig(tipo) {
            refrigAtual = tipo;
            ['int', 'ext', 'mql', 'ar'].forEach(t => {
                const btn = document.getElementById(`ref-${t}`);
                if(t === tipo) {
                    btn.className = "py-2 rounded bg-blue-600 text-white transition";
                } else {
                    btn.className = "py-2 rounded text-slate-400 hover:text-white transition";
                }
            });
            atualizarCalculo();
        }

        function ajustarDiametro(val) {
            const input = document.getElementById('diametro');
            let atual = parseFloat(input.value) || 0;
            atual = Math.max(1, Math.min(30, atual + val));
            input.value = atual.toFixed(2);
            atualizarCalculo();
        }

        function atualizarCalculo() {
            const brocaKey = document.getElementById('broca').value;
            const grupoKey = document.getElementById('grupo').value;
            const diamPrat = parseFloat(document.getElementById('diametro').value) || 8;

            const diametros = dados[brocaKey].diametros;
            const grupoData = dados[brocaKey].grupos[grupoKey] || dados[brocaKey].grupos["P1.2"];
            const avancos = grupoData.f;
            const vc = grupoData.vc[refrigAtual] || grupoData.vc['int'];

            let fCalc = 0;
            let a = 0, b = 0;
            let estadoTxt = "";

            if (diametros.includes(diamPrat)) {
                const idx = diametros.indexOf(diamPrat);
                fCalc = avancos[idx];
                estadoTxt = "Valor Exato Tabelado";
                document.getElementById('badge-metodo').className = "text-[10px] bg-emerald-900/60 text-emerald-300 px-2 py-0.5 rounded border border-emerald-700";
                document.getElementById('badge-metodo').innerText = "Catálogo Direto";
                document.getElementById('formula-txt').innerText = `f = ${fCalc.toFixed(4)} mm/rot (Tabelado)`;
                document.getElementById('val-a').innerText = "-";
                document.getElementById('val-b').innerText = "-";
            } else {
                let segEncontrado = false;
                for (let i = 0; i < diametros.length - 1; i++) {
                    const d1 = diametros[i], d2 = diametros[i+1];
                    if (d1 <= diamPrat && diamPrat <= d2) {
                        const f1 = avancos[i], f2 = avancos[i+1];
                        b = (f2 - f1) / (d2 - d1);
                        a = f1 - b * d1;
                        fCalc = a + b * diamPrat;
                        estadoTxt = "Dentro do intervalo consecutivo";
                        segEncontrado = true;
                        document.getElementById('badge-metodo').className = "text-[10px] bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded border border-blue-700";
                        document.getElementById('badge-metodo').innerText = "Interpolação Linear";
                        document.getElementById('formula-txt').innerText = `f = ${a.toFixed(4)} + ${b.toFixed(4)} × ${diamPrat.toFixed(2)} = ${fCalc.toFixed(4)} mm/rot`;
                        document.getElementById('val-a').innerText = `${a.toFixed(4)} mm/rot`;
                        document.getElementById('val-b').innerText = `${b.toFixed(4)} mm/rot·mm`;
                        break;
                    }
                }
                if (!segEncontrado) {
                    const i = diamPrat < diametros[0] ? 0 : diametros.length - 2;
                    const d1 = diametros[i], d2 = diametros[i+1];
                    const f1 = avancos[i], f2 = avancos[i+1];
                    b = (f2 - f1) / (d2 - d1);
                    a = f1 - b * d1;
                    fCalc = a + b * diamPrat;
                    document.getElementById('formula-txt').innerText = `Extrapolação: f = ${fCalc.toFixed(4)} mm/rot`;
                    document.getElementById('val-a').innerText = `${a.toFixed(4)}`;
                    document.getElementById('val-b').innerText = `${b.toFixed(4)}`;
                }
                document.getElementById('val-estado').innerText = estadoTxt;
            }

            const n = (vc * 1000) / (Math.PI * diamPrat);
            const vf = n * fCalc;

            document.getElementById('res-f').innerText = fCalc.toFixed(4);
            document.getElementById('res-vc').innerText = vc;
            document.getElementById('res-n').innerText = n.toFixed(0);
            document.getElementById('res-vf').innerText = vf.toFixed(0);

            const tbody = document.getElementById('tabela-ref');
            tbody.innerHTML = '';
            for(let i=0; i<diametros.length; i++) {
                const d = diametros[i];
                const fVal = avancos[i];
                const nRef = (vc * 1000) / (Math.PI * d);
                const vfRef = nRef * fVal;
                const isHighlight = diamPrat === d ? 'bg-blue-900/30 text-blue-300 font-semibold' : '';
                tbody.innerHTML += `<tr class="border-b border-slate-700/50 ${isHighlight}">
                    <td class="py-2 px-1">Ø ${d.toFixed(2)} mm</td>
                    <td class="py-2 px-1">${fVal.toFixed(3)}</td>
                    <td class="py-2 px-1">${nRef.toFixed(0)} rpm</td>
                    <td class="py-2 px-1">${vfRef.toFixed(0)} mm/min</td>
                </tr>`;
            }
        }

        window.onload = atualizarCalculo;
    </script>
</body>
</html>
"""

components.html(html_content, height=900, scrolling=True)
