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
                    <p id="aviso-refrig" class="text-[10px] text-amber-400 hidden">Nota: A broca SCD360 não permite refrigeração
