import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Parâmetros de Corte MAPAL", page_icon="⚙️", layout="wide")

html_content = '''
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
        <!-- Header Simplificado -->
        <header class="bg-slate-800 p-4 rounded-xl border border-slate-700">
            <h1 class="text-xl font-bold text-white">Parâmetros de Corte MAPAL</h1>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- Painel de Controlo (Esquerda) -->
            <div class="lg:col-span-4 bg-slate-800 p-5 rounded-xl border border-slate-700 space-y-5">
                <h2 class="text-sm font-semibold text-blue-400 uppercase tracking-wider">Configuração da Operação</h2>
                
                <!-- Modelo de Broca -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">1. BROCA DE METAL DURO INTEGRAL</label>
                    <select id="broca" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-blue-500" onchange="mudarBroca()">
                        <option value="scd231">SCD231 (MEGA 180° Drill)</option>
                        <option value="scd661">SCD661 (Tritan-Drill-Steel)</option>
                        <option value="scd621">SCD621 (MEGA-Speed-Drill-Steel)</option>
                        <option value="scd360">SCD360 (ECU-Drill-Steel - Sem Refrig. Interna)</option>
                        <option value="scd361">SCD361 (ECU-Drill-Steel - Com Refrig. Interna)</option>
                    </select>
                </div>

                <!-- Grupo de Materiais -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">2. GRUPO DE MATERIAIS (MMG)</label>
                    <select id="grupo" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-blue-500" onchange="atualizarCalculo()">
                        <!-- Preenchido dinamicamente via JS -->
                    </select>
                </div>

                <!-- Checkbox regra de liga MAPAL -->
                <div class="bg-slate-900 p-3 rounded-lg border border-slate-700/80 space-y-1">
                    <label class="flex items-start gap-2 cursor-pointer text-xs text-slate-300">
                        <input type="checkbox" id="liga-check" class="mt-0.5 rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-0" onchange="atualizarCalculo()">
                        <span><strong>Soma de elementos de liga (Cr, Mo, Ni, V, W) > 8%</strong><br><span class="text-[10px] text-amber-400">Regra MAPAL: avança automaticamente para o grupo seguinte.</span></span>
                    </label>
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
                    <p id="aviso-refrig" class="text-[10px] text-amber-400 hidden">Nota: A broca SCD360 não permite refrigeração interna.</p>
                </div>

                <!-- Diâmetro Pretendido -->
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <label class="text-xs font-medium text-slate-300">4. DIÂMETRO PRETENDIDO (Ø)</label>
                        <span id="badge-metodo" class="text-[10px] bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded border border-blue-700">Interpolação Linear</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <button onclick="ajustarDiametro(-0.5)" class="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-lg text-white font-bold">-</button>
                        <input type="number" id="diametro" value="8.00" step="0.1" min="1" max="30" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-center text-lg font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        <button onclick="ajustarDiametro(0.5)" class="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-lg text-white font-bold">+</button>
                    </div>
                </div>

                <!-- Controlos de Ajuste Percentual (Vc e f) -->
                <div class="space-y-3 pt-2 border-t border-slate-700">
                    <label class="text-xs font-medium text-blue-400 uppercase tracking-wider">Ajustes Percentuais (%)</label>
                    
                    <!-- Ajuste Vc (%) -->
                    <div class="space-y-1">
                        <div class="flex justify-between text-xs text-slate-300">
                            <span>Ajuste Vc (%):</span>
                            <span id="vc-pct-val" class="font-bold text-cyan-400">0%</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <button onclick="ajustarPct('vc', -1)" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded text-white text-xs font-bold">-1%</button>
                            <input type="range" id="vc-slider" min="-50" max="50" value="0" step="1" class="w-full accent-blue-500" oninput="onSliderVc()">
                            <button onclick="ajustarPct('vc', 1)" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded text-white text-xs font-bold">+1%</button>
                            <button onclick="resetPct('vc')" class="bg-slate-900 border border-slate-600 text-slate-400 hover:text-white px-2 py-1 rounded text-xs">Reset</button>
                        </div>
                    </div>

                    <!-- Ajuste f (%) -->
                    <div class="space-y-1">
                        <div class="flex justify-between text-xs text-slate-300">
                            <span>Ajuste Avanço f (%):</span>
                            <span id="f-pct-val" class="font-bold text-cyan-400">0%</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <button onclick="ajustarPct('f', -1)" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded text-white text-xs font-bold">-1%</button>
                            <input type="range" id="f-slider" min="-50" max="50" value="0" step="1" class="w-full accent-blue-500" oninput="onSliderF()">
                            <button onclick="ajustarPct('f', 1)" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded text-white text-xs font-bold">+1%</button>
                            <button onclick="resetPct('f')" class="bg-slate-900 border border-slate-600 text-slate-400 hover:text-white px-2 py-1 rounded text-xs">Reset</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Resultados e Indicadores (Direita) -->
            <div class="lg:col-span-8 space-y-6">
                <!-- Grid de Métricas CNC -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <!-- Cartão Avanço / Rotação (f) com Cadeado -->
                    <div id="card-f" class="bg-slate-800 p-4 rounded-xl border border-slate-700 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-400">Avanço / Rotação (f)</span>
                            <button type="button" onclick="toggleLock('f')" id="btn-lock-f" title="Desbloquear para edição manual" class="text-sm px-1.5 py-0.5 rounded bg-slate-900/80 border border-slate-700 hover:border-slate-500 transition">
                                🔒
                            </button>
                        </div>
                        <input type="number" id="input-f" value="0.3850" step="0.005" min="0.001" readonly oninput="onManualInput('f')" class="w-full bg-transparent text-2xl font-bold text-white mt-1 focus:outline-none rounded px-1 -ml-1">
                        <div class="flex justify-between items-center mt-0.5">
                            <span class="text-[10px] text-blue-400">mm/rot</span>
                            <span id="status-f" class="text-[10px] text-slate-500">Auto</span>
                        </div>
                    </div>

                    <!-- Cartão Velocidade de Corte (Vc) com Cadeado -->
                    <div id="card-vc" class="bg-slate-800 p-4 rounded-xl border border-slate-700 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-400">Velocidade de Corte (Vc)</span>
                            <button type="button" onclick="toggleLock('vc')" id="btn-lock-vc" title="Desbloquear para edição manual" class="text-sm px-1.5 py-0.5 rounded bg-slate-900/80 border border-slate-700 hover:border-slate-500 transition">
                                🔒
                            </button>
                        </div>
                        <input type="number" id="input-vc" value="105" step="1" min="1" readonly oninput="onManualInput('vc')" class="w-full bg-transparent text-2xl font-bold text-white mt-1 focus:outline-none rounded px-1 -ml-1">
                        <div class="flex justify-between items-center mt-0.5">
                            <span class="text-[10px] text-slate-400">m/min</span>
                            <span id="status-vc" class="text-[10px] text-slate-500">Auto</span>
                        </div>
                    </div>

                    <!-- Rotações (Spindle) -->
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Rotações (Spindle)</span>
                        <div class="text-2xl font-bold text-white mt-1" id="res-n">4178</div>
                        <span class="text-[10px] text-slate-400">rpm</span>
                    </div>

                    <!-- Avanço de Trabalho -->
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Avanço de Trabalho</span>
                        <div class="text-2xl font-bold text-white mt-1" id="res-vf">1608</div>
                        <span class="text-[10px] text-slate-400">mm/min</span>
                    </div>
                </div>

                <!-- Valores auxiliares compactos -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Intercepção (a)</span>
                        <div class="font-mono text-lg font-bold text-white mt-1" id="val-a">0.1450 mm/rot</div>
                    </div>
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Declive / Desvio (b)</span>
                        <div class="font-mono text-lg font-bold text-white mt-1" id="val-b">0.0300 mm/rot·mm</div>
                    </div>
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <span class="text-xs text-slate-400">Estado da Gama</span>
                        <div class="text-sm font-bold text-emerald-400 mt-1.5" id="val-estado">Dentro do intervalo consecutivo</div>
                    </div>
                </div>

                <!-- Tabela de Referência e Gráfico lado a lado -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Tabela de Referência -->
                    <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 space-y-3">
                        <h3 class="text-xs font-semibold text-slate-400 uppercase">Tabela de Referência do Catálogo</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead>
                                    <tr class="border-b border-slate-700 text-slate-400">
                                        <th class="pb-2">Ø (mm)</th>
                                        <th class="pb-2">f Cat.</th>
                                        <th class="pb-2">RPM (n)</th>
                                        <th class="pb-2">Avanço (v_f)</th>
                                    </tr>
                                </thead>
                                <tbody id="tabela-ref" class="divide-y divide-slate-700/50"></tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Gráfico Interativo SVG -->
                    <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 space-y-3 flex flex-col justify-between">
                        <div class="flex justify-between items-center">
                            <h3 class="text-xs font-semibold text-slate-400 uppercase">Curva por Intervalos: Avanço (f) vs. Ø</h3>
                            <span class="text-[10px] text-slate-400">SVG Interativo</span>
                        </div>
                        <div class="relative w-full h-48 bg-slate-900 rounded-lg border border-slate-700 p-2 flex items-center justify-center">
                            <svg id="svg-grafico" class="w-full h-full" viewBox="0 0 400 180"></svg>
                        </div>
                        <div class="flex justify-center gap-4 text-[10px] text-slate-400">
                            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block"></span> Catálogo</span>
                            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-orange-500 inline-block"></span> Calculado</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Assinatura / Rodapé -->
        <footer class="bg-slate-800/80 p-4 rounded-xl border border-slate-700/80 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs text-slate-400">
            <div class="font-medium text-slate-300">
                Created by <span class="text-white font-semibold">Bruno Pinto</span>
            </div>
            <div class="flex flex-wrap items-center gap-4">
                <a href="mailto:bruno.pinto@alamo-ferramentas.com" class="hover:text-blue-400 transition flex items-center gap-1.5">
                    <span>✉️</span> bruno.pinto@alamo-ferramentas.com
                </a>
                <a href="tel:+351936959415" class="hover:text-blue-400 transition flex items-center gap-1.5">
                    <span>📱</span> +351 936 959 415
                </a>
            </div>
        </footer>
    </div>

    <script>
        let refrigAtual = 'int';
        let vcPct = 0;
        let fPct = 0;
        let fUnlocked = false;
        let vcUnlocked = false;

        const dados = {
            scd231: {
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
                    "K3.1": "K3.1 — Ferro fundido esferoidal GJV / Mableável GJM (< 500 N/mm²)",
                    "K3.2": "K3.2 — Ferro fundido esferoidal GJV / Mableável GJM (> 500 N/mm²)"
                },
                grupos: {
                    "P1.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
                    "P1.2": { vc: {int:70, ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
                    "P2.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.08, 0.11, 0.14, 0.19, 0.24, 0.28] },
                    "P2.2": { vc: {int:55, ext:50, mql:50, ar:0}, f: [0.07, 0.09, 0.12, 0.15, 0.19, 0.22] },
                    "P3.1": { vc: {int:60, ext:50, mql:50, ar:0}, f: [0.07, 0.10, 0.13, 0.17, 0.21, 0.25] },
                    "P3.2": { vc: {int:50, ext:45, mql:45, ar:0}, f: [0.06, 0.08, 0.11, 0.14, 0.17, 0.21] },
                    "P3.3": { vc: {int:50, ext:35, mql:40, ar:0}, f: [0.05, 0.07, 0.09, 0.11, 0.14, 0.16] },
                    "P5.1": { vc: {int:80, ext:70, mql:70, ar:0}, f: [0.08, 0.11, 0.14, 0.19, 0.24, 0.28] },
                    "K1.1": { vc: {int:95, ext:70, mql:70, ar:70}, f: [0.09, 0.14, 0.19, 0.25, 0.33, 0.39] },
                    "K2.1": { vc: {int:130, ext:80, mql:95, ar:95}, f: [0.10, 0.13, 0.18, 0.24, 0.30, 0.36] },
                    "K2.2": { vc: {int:80, ext:60, mql:60, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
                    "K2.3": { vc: {int:50, ext:30, mql:40, ar:0}, f: [0.06, 0.08, 0.11, 0.14, 0.17, 0.21] },
                    "K3.1": { vc: {int:70, ext:65, mql:65, ar:0}, f: [0.09, 0.13, 0.17, 0.22, 0.28, 0.33] },
                    "K3.2": { vc: {int:65, ext:55, mql:55, ar:0}, f: [0.08, 0.11, 0.14, 0.18, 0.22, 0.26] }
                }
            },
            scd661: {
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
            scd360: {
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
                    "K3.1": "K3.1 — Ferro fundido esferoidal GJV / Mableável GJM (< 500 N/mm²)",
                    "K3.2": "K3.2 — Ferro fundido esferoidal GJV / Mableável GJM (> 500 N/mm²)"
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
                    "K3.1": "K3.1 — Ferro fundido esferoidal GJV / Mableável GJM (< 500 N/mm²)",
                    "K3.2": "K3.2 — Ferro fundido esferoidal GJV / Mableável GJM (> 500 N/mm²)"
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
            }
        };

        function mudarBroca() {
            const brocaKey = document.getElementById('broca').value;
            const grupoSelect = document.getElementById('grupo');
            const toolData = dados[brocaKey];
            
            grupoSelect.innerHTML = '';
            toolData.gruposList.forEach((gKey, idx) => {
                const opt = document.createElement('option');
                opt.value = gKey;
                opt.text = toolData.gruposNames[gKey];
                if(idx === 0) opt.selected = true;
                grupoSelect.appendChild(opt);
            });

            // Tratamento especial para SCD360 (sem refrigeração interna)
            const btnInt = document.getElementById('ref-int');
            const avisoRefrig = document.getElementById('aviso-refrig');
            if (brocaKey === 'scd360') {
                btnInt.disabled = true;
                btnInt.className = "py-2 rounded bg-slate-800 text-slate-600 cursor-not-allowed";
                avisoRefrig.classList.remove('hidden');
                if (refrigAtual === 'int') {
                    setRefrig('ext');
                }
            } else {
                btnInt.disabled = false;
                avisoRefrig.classList.add('hidden');
                if (refrigAtual === 'int' || brocaKey === 'scd231') {
                    setRefrig('int');
                }
            }

            atualizarCalculo();
        }

        function setRefrig(tipo) {
            const brocaKey = document.getElementById('broca').value;
            if (brocaKey === 'scd360' && tipo === 'int') return;

            refrigAtual = tipo;
            ['int', 'ext', 'mql', 'ar'].forEach(t => {
                const btn = document.getElementById(`ref-${t}`);
                if (brocaKey === 'scd360' && t === 'int') return;
                if(t === tipo) {
                    btn.className = "py-2 rounded bg-blue-600 text-white transition";
                } else {
                    btn.className = "py-2 rounded text-slate-400 hover:text-white transition";
                }
            });
            atualizarCalculo();
        }

        function toggleLock(tipo) {
            if (tipo === 'f') {
                fUnlocked = !fUnlocked;
                const input = document.getElementById('input-f');
                const btn = document.getElementById('btn-lock-f');
                const card = document.getElementById('card-f');
                const status = document.getElementById('status-f');
                
                input.readOnly = !fUnlocked;
                if (fUnlocked) {
                    btn.innerText = '🔓';
                    btn.title = 'Bloquear e voltar ao cálculo automático';
                    card.className = 'bg-slate-800 p-4 rounded-xl border border-amber-500/80 transition-colors';
                    input.className = 'w-full bg-slate-900 text-2xl font-bold text-amber-300 mt-1 focus:outline-none rounded px-1.5 py-0.5 -ml-1 border border-amber-500/40';
                    status.innerText = 'Manual';
                    status.className = 'text-[10px] text-amber-400 font-semibold';
                    input.focus();
                } else {
                    btn.innerText = '🔒';
                    btn.title = 'Desbloquear para edição manual';
                    card.className = 'bg-slate-800 p-4 rounded-xl border border-slate-700 transition-colors';
                    input.className = 'w-full bg-transparent text-2xl font-bold text-white mt-1 focus:outline-none rounded px-1 -ml-1';
                    status.innerText = 'Auto';
                    status.className = 'text-[10px] text-slate-500';
                    atualizarCalculo();
                }
            } else if (tipo === 'vc') {
                vcUnlocked = !vcUnlocked;
                const input = document.getElementById('input-vc');
                const btn = document.getElementById('btn-lock-vc');
                const card = document.getElementById('card-vc');
                const status = document.getElementById('status-vc');
                
                input.readOnly = !vcUnlocked;
                if (vcUnlocked) {
                    btn.innerText = '🔓';
                    btn.title = 'Bloquear e voltar ao cálculo automático';
                    card.className = 'bg-slate-800 p-4 rounded-xl border border-amber-500/80 transition-colors';
                    input.className = 'w-full bg-slate-900 text-2xl font-bold text-amber-300 mt-1 focus:outline-none rounded px-1.5 py-0.5 -ml-1 border border-amber-500/40';
                    status.innerText = 'Manual';
                    status.className = 'text-[10px] text-amber-400 font-semibold';
                    input.focus();
                } else {
                    btn.innerText = '🔒';
                    btn.title = 'Desbloquear para edição manual';
                    card.className = 'bg-slate-800 p-4 rounded-xl border border-slate-700 transition-colors';
                    input.className = 'w-full bg-transparent text-2xl font-bold text-white mt-1 focus:outline-none rounded px-1 -ml-1';
                    status.innerText = 'Auto';
                    status.className = 'text-[10px] text-slate-500';
                    atualizarCalculo();
                }
            }
        }

        function onManualInput(tipo) {
            atualizarCalculo();
        }

        function ajustarDiametro(val) {
            const input = document.getElementById('diametro');
            let atual = parseFloat(input.value) || 0;
            atual = Math.max(1, Math.min(30, atual + val));
            input.value = atual.toFixed(2);
            atualizarCalculo();
        }

        function ajustarPct(tipo, valor) {
            if (tipo === 'vc') {
                vcPct = Math.max(-50, Math.min(50, vcPct + valor));
                document.getElementById('vc-slider').value = vcPct;
            } else {
                fPct = Math.max(-50, Math.min(50, fPct + valor));
                document.getElementById('f-slider').value = fPct;
            }
            atualizarCalculo();
        }

        function onSliderVc() {
            vcPct = parseInt(document.getElementById('vc-slider').value);
            atualizarCalculo();
        }

        function onSliderF() {
            fPct = parseInt(document.getElementById('f-slider').value);
            atualizarCalculo();
        }

        function resetPct(tipo) {
            if (tipo === 'vc') {
                vcPct = 0;
                document.getElementById('vc-slider').value = 0;
            } else {
                fPct = 0;
                document.getElementById('f-slider').value = 0;
            }
            atualizarCalculo();
        }

        function atualizarCalculo() {
            const brocaKey = document.getElementById('broca').value;
            let grupoKey = document.getElementById('grupo').value;
            const ligaChecked = document.getElementById('liga-check').checked;
            const diamPrat = parseFloat(document.getElementById('diametro').value) || 8;

            document.getElementById('vc-pct-val').innerText = (vcPct > 0 ? `+${vcPct}%` : `${vcPct}%`);
            document.getElementById('f-pct-val').innerText = (fPct > 0 ? `+${fPct}%` : `${fPct}%`);

            const toolData = dados[brocaKey];
            const diametros = toolData.diametros;
            const gruposList = toolData.gruposList;

            if (ligaChecked) {
                let idxG = gruposList.indexOf(grupoKey);
                if (idxG !== -1 && idxG < gruposList.length - 1) {
                    grupoKey = gruposList[idxG + 1];
                }
            }

            const grupoData = toolData.grupos[grupoKey] || toolData.grupos[gruposList[0]];
            const avancos = grupoData.f;
            
            // Obter Vc com base na refrigeração selecionada
            let vcBase = grupoData.vc[refrigAtual];
            if (vcBase === undefined || vcBase === 0) {
                // Fallback se a refrigeração escolhida não existir para esta broca/material
                vcBase = grupoData.vc['ext'] || 50;
            }

            let vcFinal = 0;
            if (vcUnlocked) {
                vcFinal = parseFloat(document.getElementById('input-vc').value) || 0;
            } else {
                vcFinal = vcBase * (1 + vcPct / 100);
                document.getElementById('input-vc').value = vcFinal.toFixed(0);
            }

            let fBase = 0;
            let a = 0, b = 0;
            let estadoTxt = "";

            if (diametros.includes(diamPrat)) {
                const idx = diametros.indexOf(diamPrat);
                fBase = avancos[idx];
                estadoTxt = "Valor Exato Tabelado";
                document.getElementById('badge-metodo').className = "text-[10px] bg-emerald-900/60 text-emerald-300 px-2 py-0.5 rounded border border-emerald-700";
                document.getElementById('badge-metodo').innerText = "Catálogo Direto";
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
                        fBase = a + b * diamPrat;
                        estadoTxt = "Dentro do intervalo consecutivo";
                        segEncontrado = true;
                        document.getElementById('badge-metodo').className = "text-[10px] bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded border border-blue-700";
                        document.getElementById('badge-metodo').innerText = "Interpolação Linear";
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
                    fBase = a + b * diamPrat;
                    document.getElementById('val-a').innerText = `${a.toFixed(4)}`;
                    document.getElementById('val-b').innerText = `${b.toFixed(4)}`;
                }
                document.getElementById('val-estado').innerText = estadoTxt;
            }

            let fFinal = 0;
            if (fUnlocked) {
                fFinal = parseFloat(document.getElementById('input-f').value) || 0;
            } else {
                fFinal = fBase * (1 + fPct / 100);
                document.getElementById('input-f').value = fFinal.toFixed(4);
            }

            const n = (vcFinal * 1000) / (Math.PI * diamPrat);
            const vf = n * fFinal;

            document.getElementById('res-n').innerText = n.toFixed(0);
            document.getElementById('res-vf').innerText = vf.toFixed(0);

            const tbody = document.getElementById('tabela-ref');
            tbody.innerHTML = '';
            for(let i=0; i<diametros.length; i++) {
                const d = diametros[i];
                const fValCat = avancos[i];
                const nRef = (vcFinal * 1000) / (Math.PI * d);
                const vfRef = nRef * fValCat;
                const isHighlight = diamPrat === d ? 'bg-blue-900/30 text-blue-300 font-semibold' : '';
                tbody.innerHTML += `<tr class="border-b border-slate-700/50 ${isHighlight}">
                    <td class="py-2 px-1">Ø ${d.toFixed(2)}</td>
                    <td class="py-2 px-1">${fValCat.toFixed(3)}</td>
                    <td class="py-2 px-1">${nRef.toFixed(0)}</td>
                    <td class="py-2 px-1">${vfRef.toFixed(0)}</td>
                </tr>`;
            }

            desenharGrafico(diametros, avancos, diamPrat, fFinal);
        }

        function desenharGrafico(diametros, avancos, diamPrat, fFinal) {
            const svg = document.getElementById('svg-grafico');
            const w = 400, h = 180;
            const padding = 30;
            
            const minX = diametros[0] - 0.5;
            const maxX = diametros[diametros.length - 1] + 1;
            const minY = 0;
            const maxY = Math.max(...avancos, fFinal) * 1.2;

            function scaleX(d) { return padding + (d - minX) / (maxX - minX) * (w - 2 * padding); }
            function scaleY(f) { return h - padding - (f - minY) / (maxY - minY) * (h - 2 * padding); }

            let svgHTML = `
                <line x1="${padding}" y1="${h-padding}" x2="${w-padding}" y2="${h-padding}" stroke="#475569" stroke-width="1" />
                <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${h-padding}" stroke="#475569" stroke-width="1" />
            `;

            let pathD = "";
            for(let i=0; i<diametros.length; i++) {
                const cx = scaleX(diametros[i]);
                const cy = scaleY(avancos[i]);
                pathD += (i === 0 ? `M ${cx} ${cy}` : ` L ${cx} ${cy}`);
            }
            svgHTML += `<path d="${pathD}" fill="none" stroke="#3b82f6" stroke-width="2" />`;

            for(let i=0; i<diametros.length; i++) {
                const cx = scaleX(diametros[i]);
                const cy = scaleY(avancos[i]);
                svgHTML += `<circle cx="${cx}" cy="${cy}" r="4" fill="#3b82f6" />`;
            }

            const px = scaleX(diamPrat);
            const py = scaleY(fFinal);
            svgHTML += `
                <line x1="${px}" y1="${h-padding}" x2="${px}" y2="${py}" stroke="#f97316" stroke-dasharray="3,3" stroke-width="1.5" />
                <line x1="${padding}" y1="${py}" x2="${px}" y2="${py}" stroke="#f97316" stroke-dasharray="3,3" stroke-width="1.5" />
                <circle cx="${px}" cy="${py}" r="5" fill="#f97316" />
                <text x="${Math.min(px + 8, w - 70)}" y="${Math.max(py - 8, 20)}" fill="#f8fafc" font-size="10" font-weight="bold">Ø${diamPrat.toFixed(1)} : ${fFinal.toFixed(3)}</text>
            `;

            svg.innerHTML = svgHTML;
        }

        window.onload = function() {
            mudarBroca();
        };
    </script>
</body>
</html>
'''

components.html(html_content, height=1100, scrolling=True)
