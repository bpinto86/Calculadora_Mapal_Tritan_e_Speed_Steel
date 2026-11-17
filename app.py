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
                        <span id="badge-metodo" class="text-[10px] bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded border border-blue-700">Interpolação Linear</span>
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

                <!-- Tabela de Refer
