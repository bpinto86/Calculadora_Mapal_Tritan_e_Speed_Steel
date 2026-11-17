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
                
                <!-- 1ª Escolha Lógica: Linha -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">1. LINHA DE FERRAMENTA</label>
                    <select id="linha" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-blue-500" onchange="atualizarFiltroBrocas()">
                        <option value="expert">Expert Line (Alta Performance)</option>
                        <option value="performance">Performance Line</option>
                        <option value="basic">Basic Line (Uso Geral)</option>
                    </select>
                </div>

                <!-- 2ª Escolha Lógica: Refrigeração pretendida -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">2. REFRIGERAÇÃO DISPONÍVEL</label>
                    <select id="filtro-refrig" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-blue-500" onchange="atualizarFiltroBrocas()">
                        <option value="com">Com Refrigeração Interna</option>
                        <option value="sem">Sem Refrigeração Interna</option>
                    </select>
                </div>

                <!-- 3ª Escolha: Modelo de Broca Específico -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">3. MODELO DE BROCA</label>
                    <select id="broca" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-blue-500" onchange="mudarBroca()">
                        <!-- Preenchido dinamicamente via JS -->
                    </select>
                </div>

                <!-- Grupo de Materiais -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">4. GRUPO DE MATERIAIS (MMG)</label>
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

                <!-- Tipo de Refrigeração Ativa -->
                <div class="space-y-2">
                    <label class="text-xs font-medium text-slate-300">5. MÉTODO DE REFRIGERAÇÃO A USAR</label>
                    <div class="grid grid-cols-4 gap-1 bg-slate-900 p-1 rounded-lg border border-slate-700 text-xs text-center font-medium">
                        <button type="button" onclick="setRefrig('int')" id="ref-int" class="py-2 rounded bg-blue-600 text-white transition">Interna</button>
                        <button type="button" onclick="setRefrig('ext')" id="ref-ext" class="py-2 rounded text-slate-400 hover:text-white transition">Externa</button>
                        <button type="button" onclick="setRefrig('mql')" id="ref-mql" class="py-2 rounded text-slate-400 hover:text-white transition">MQL</button>
                        <button type="button" onclick="setRefrig('ar')" id="ref-ar" class="py-2 rounded text-slate-400 hover:text-white transition">Ar</button>
                    </div>
                    <p id="aviso-refrig" class="text-[10px] text-amber-400 hidden">Nota: Esta ferramenta não permite refrigeração interna.</p>
                </div>

                <!-- Diâmetro Pretendido -->
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <label class="text-xs font-medium text-slate-300">6. DIÂMETRO PRETENDIDO (Ø)</label>
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
            scd661: {
                linha: 'expert',
                temRefrigInt: true,
                nome: 'SCD661 (Tritan-Drill-Steel)',
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
                    "K2.1": "K2.1 — Ferro fundido esferoidal GJS (< 5
