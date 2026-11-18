import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Parâmetros de Corte MAPAL", page_icon="⚙️", layout="wide")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
        max-width: 100% !important;
    }
    iframe {
        height: 100vh !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

html_content = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Parâmetros de Corte MAPAL</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 0; height: 100vh; overflow: hidden; }
    </style>
</head>
<body class="h-screen p-2 flex flex-col box-border">
    <div class="w-full h-full flex flex-col gap-2">
        <!-- Header Compacto -->
        <header class="bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 flex justify-between items-center shrink-0">
            <h1 class="text-base font-bold text-white">Parâmetros de Corte MAPAL</h1>
            <button onclick="toggleFullScreen()" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                <span>⛶</span> Ecrã Inteiro / Janela
            </button>
        </header>

        <!-- Layout Principal em Grid de Altura Total -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0">
            <!-- Painel de Controlo (Esquerda) -->
            <div class="lg:col-span-4 bg-slate-800 p-3.5 rounded-lg border border-slate-700 flex flex-col gap-2.5 overflow-y-auto min-h-0">
                <h2 class="text-xs font-semibold text-blue-400 uppercase tracking-wider shrink-0">Configuração da Operação</h2>
                
                <!-- 1. Linha de Ferramenta -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">1. LINHA DE FERRAMENTA</label>
                    <select id="linha" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="atualizarFiltroBrocas()">
                        <option value="expert">Expert Line (Alta Performance)</option>
                        <option value="performance">Performance Line</option>
                        <option value="basic">Basic Line (Uso Geral)</option>
                    </select>
                </div>

                <!-- 2. Tipo de Operação / Categoria -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">2. TIPO DE OPERAÇÃO / CATEGORIA</label>
                    <select id="categoria" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="atualizarFiltroBrocas()">
                        <option value="solid">Solid Carbide / Standard Drilling</option>
                        <option value="insert">Insert Drilling (Pastilhas Amovíveis)</option>
                        <option value="spot">Spot Drilling (Centragem / Ponto)</option>
                        <option value="stepped">Stepped Drilling (Escalonada)</option>
                        <option value="deep">Deep Drilling (Furação Profunda)</option>
                        <option value="reaming">Drill Reaming (Alargamento)</option>
                    </select>
                </div>

                <!-- 3. Refrigeração Disponível -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">3. REFRIGERAÇÃO DISPONÍVEL</label>
                    <select id="filtro-refrig" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="atualizarFiltroBrocas()">
                        <option value="com">Com Refrigeração Interna</option>
                        <option value="sem">Sem Refrigeração Interna</option>
                    </select>
                </div>

                <!-- 4. Modelo de Ferramenta -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">4. MODELO DE FERRAMENTA</label>
                    <select id="broca" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="mudarBroca()">
                    </select>
                </div>

                <!-- 5. Grupo de Materiais -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">5. GRUPO DE MATERIAIS (MMG)</label>
                    <select id="grupo" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="atualizarCalculo()">
                    </select>
                </div>

                <!-- Checkbox regra de liga MAPAL -->
                <div class="bg-slate-900 p-2 rounded-md border border-slate-700/80 space-y-0.5 shrink-0">
                    <label class="flex items-start gap-1.5 cursor-pointer text-[11px] text-slate-300">
                        <input type="checkbox" id="liga-check" class="mt-0.5 rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-0" onchange="atualizarCalculo()">
                        <span><strong>Soma liga (Cr, Mo, Ni, V, W) > 8%</strong><br><span class="text-[9px] text-amber-400">Regra MAPAL: avança para o grupo seguinte.</span></span>
                    </label>
                </div>

                <!-- 6. Método de Refrigeração -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">6. MÉTODO DE REFRIGERAÇÃO A USAR</label>
                    <div class="grid grid-cols-4 gap-1 bg-slate-900 p-1 rounded-md border border-slate-700 text-[11
