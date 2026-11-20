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
    <title>Parâmetros de Corte MAPAL & Proposta Comercial PDF</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 0; height: 100vh; overflow: hidden; }
    </style>
</head>
<body class="h-screen p-2 flex flex-col box-border">
    <div class="w-full h-full flex flex-col gap-2">
        <!-- Header Compacto -->
        <header class="bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 flex justify-between items-center shrink-0">
            <h1 class="text-base font-bold text-white flex items-center gap-2">
                <span>⚙️</span> Parâmetros de Corte MAPAL & Proposta Comercial PDF
            </h1>
            <div class="flex items-center gap-2">
                <button onclick="resetRapidoTudo()" title="Repor Vc, f, RPM máx., ajustes % e pecking" class="bg-amber-600 hover:bg-amber-500 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>↺</span> Reset Rápido
                </button>
                <button onclick="abrirModalComparacao()" class="bg-emerald-600 hover:bg-emerald-500 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>⚖️</span> Comparar Família
                </button>
                <button onclick="abrirModalExportacao()" class="bg-blue-600 hover:bg-blue-500 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>📄</span> Exportar Proposta PDF
                </button>
                <button onclick="toggleFullScreen()" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>⛶</span> Ecrã Inteiro
                </button>
            </div>
        </header>

        <!-- Layout Principal em Grid de Altura Total -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0">
            <!-- Painel de Controlo (Esquerda) -->
            <div class="lg:col-span-4 bg-slate-800 p-3.5 rounded-lg border border-slate-700 flex flex-col gap-2.5 overflow-y-auto min-h-0">
                <h2 class="text-xs font-semibold text-blue-400 uppercase tracking-wider shrink-0">Configuração da Operação</h2>

                <!-- Pesquisa Rápida por Referência -->
                <div class="space-y-1 shrink-0 bg-slate-900/90 p-2 rounded-md border border-cyan-800/60">
                    <label class="text-[11px] font-medium text-cyan-300 block">PESQUISA RÁPIDA POR REFERÊNCIA / xD</label>
                    <div class="flex gap-1.5">
                        <input type="text" id="ref-pesquisa" placeholder="Ex: SCD661 12XD, SCD631 8xD, SCD231..." class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500" onkeydown="if(event.key==='Enter') aplicarPesquisaReferencia()">
                        <button type="button" onclick="aplicarPesquisaReferencia()" class="bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white transition shrink-0">Aplicar</button>
                    </div>
                    <span id="ref-feedback" class="text-[10px] text-slate-400 block">Deteta família e variante ×D automaticamente.</span>
                </div>
                
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

                <!-- 4. Modelo de Ferramenta & Variante xD -->
                <div class="grid grid-cols-3 gap-2 shrink-0">
                    <div class="col-span-2 space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">4. MODELO DE FERRAMENTA</label>
                        <select id="broca" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="mudarBroca()">
                        </select>
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">VARIANTE</label>
                        <select id="variante-xd" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs font-bold text-cyan-300 focus:outline-none focus:border-blue-500" onchange="atualizarCalculo()">
                        </select>
                    </div>
                </div>

                <!-- 5. Grupo de Materiais -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">5. GRUPO DE MATERIAIS (MMG)</label>
                    <select id="grupo" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="mudarGrupoMaterial()">
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
                    <div class="grid grid-cols-4 gap-1 bg-slate-900 p-1 rounded-md border border-slate-700 text-[11px] text-center font-medium">
                        <button type="button" onclick="setRefrig('int')" id="ref-int" class="py-1.5 rounded bg-blue-600 text-white transition">Interna</button>
                        <button type="button" onclick="setRefrig('ext')" id="ref-ext" class="py-1.5 rounded text-slate-400 hover:text-white transition">Externa</button>
                        <button type="button" onclick="setRefrig('mql')" id="ref-mql" class="py-1.5 rounded text-slate-400 hover:text-white transition">MQL</button>
                        <button type="button" onclick="setRefrig('ar')" id="ref-ar" class="py-1.5 rounded text-slate-400 hover:text-white transition">Ar</button>
                    </div>
                    <p id="aviso-refrig" class="text-[9px] text-amber-400 hidden">Nota: Esta ferramenta não permite refrigeração interna.</p>
                </div>

                <!-- 7. Dimensões, Lote e Pecking -->
                <div class="grid grid-cols-2 gap-2 shrink-0">
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">7. DIÂMETRO (Ø)</label>
                        <div class="flex items-center gap-1">
                            <button onclick="ajustarDiametro(-0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">-</button>
                            <input type="number" id="diametro" value="00" step="0.1" min="0.5" max="60" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                            <button onclick="ajustarDiametro(0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">+</button>
                        </div>
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">8. PROFUNDIDADE/FURO (L)</label>
                        <div class="flex items-center gap-1">
                            <input type="number" id="profundidade" value="00" step="1" min="0.1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                            <span class="text-[10px] text-slate-400 font-medium">mm</span>
                        </div>
                    </div>
                </div>

                <!-- Validação de Profundidade com Catálogo e Limite Nominal -->
                <div id="alerta-profundidade" class="bg-slate-900 px-2.5 py-1.5 rounded-md border border-slate-700 text-[10px] text-slate-200 flex justify-between items-center gap-2 shrink-0">
                    <span id="texto-limite-prof">Profundidade a validar com catálogo (5xD @ Ø12.0 | Lim. nom.: 60 mm)</span>
                    <span id="badge-limite-prof" class="font-bold text-amber-400 shrink-0">VALIDAR CATÁLOGO</span>
                </div>

                <div class="grid grid-cols-2 gap-2 shrink-0 pt-1">
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">9. QTD. FUROS (LOTE)</label>
                        <input type="number" id="qtd-furos" value="00" step="1" min="1" max="100000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">10. DENSIDADE (g/cm³)</label>
                        <input type="number" id="densidade" value="7.85" step="0.01" min="0.5" max="25" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                    </div>
                </div>

                <!-- Configuração de Ciclo com Pecking (Quebra de Cavaco) -->
                <div class="bg-slate-900 p-2.5 rounded-md border border-slate-700/80 space-y-2 shrink-0">
                    <label class="flex items-center gap-2 cursor-pointer text-[11px] text-slate-300">
                        <input type="checkbox" id="pecking-check" class="rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-0" onchange="togglePeckingInputs()">
                        <span><strong>Ciclo com Quebra de Cavaco (Pecking)</strong></span>
                    </label>
                    <div id="pecking-options" class="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800 hidden">
                        <div class="space-y-1">
                            <div class="flex justify-between items-center">
                                <label class="text-[10px] font-medium text-slate-400">PASSO (Q)</label>
                                <select id="pecking-unidade" class="bg-slate-800 border border-slate-700 rounded px-1 text-[9px] text-cyan-400 focus:outline-none" onchange="onChangePeckingUnidade()">
                                    <option value="xd" selected>×D</option>
                                    <option value="mm">mm</option>
                                </select>
                            </div>
                            <input type="number" id="pecking-passo" value="3.0" step="0.5" min="0.1" max="500" class="w-full bg-slate-800 border border-slate-700 rounded p-1 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                            <span id="pecking-equiv" class="text-[9px] text-cyan-400 block text-center">Equiv: 36.0 mm (4 passos)</span>
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] font-medium text-slate-400 block">AVANÇO RETRAÇÃO (mm/min)</label>
                            <input type="number" id="pecking-retensao" value="5000" step="500" min="500" max="20000" class="w-full bg-slate-800 border border-slate-700 rounded p-1 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                            <span class="text-[9px] text-slate-500 block text-center">Retorno alívio</span>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-2 shrink-0 pt-1">
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">11. VALOR SUCATA (€/kg)</label>
                        <input type="number" id="preco-sucata" value="0.35" step="0.05" min="0" max="50" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">12. CUSTO HORA MÁQUINA (€/h)</label>
                        <input type="number" id="custo-hora" value="50.00" step="5" min="1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                    </div>
                </div>

                <!-- Capacidade do Spindle da Máquina (Opcional) -->
                <div class="space-y-2 pt-2 border-t border-slate-700 shrink-0">
                    <div class="flex justify-between items-center">
                        <label class="text-[11px] font-medium text-amber-400 uppercase tracking-wider">13. Capacidade do Spindle (Opcional)</label>
                        <span class="text-[9px] text-slate-400">Deixar vazio se n/a</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div class="space-y-1">
                            <div class="flex justify-between items-center">
                                <label class="text-[10px] font-medium text-slate-300">POTÊNCIA MÁX.</label>
                                <select id="unidade-potencia" class="bg-slate-900 border border-slate-700 rounded px-1 text-[9px] text-cyan-400 focus:outline-none" onchange="atualizarCalculo()">
                                    <option value="kw">kW</option>
                                    <option value="cv">CV</option>
                                </select>
                            </div>
                            <input type="number" id="spindle-potencia" placeholder="Ex: 11.0" step="0.5" min="0" max="200" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white placeholder-slate-600 focus:outline-none focus:border-amber-500" oninput="atualizarCalculo()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] font-medium text-slate-300 block">BINÁRIO MÁX. (N·m)</label>
                            <input type="number" id="spindle-binario" placeholder="Ex: 70" step="1" min="0" max="2000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white placeholder-slate-600 focus:outline-none focus:border-amber-500" oninput="atualizarCalculo()">
                        </div>
                    </div>
                </div>

                <!-- Ajustes Percentuais (%) -->
                <div class="space-y-2 pt-1 border-t border-slate-700 shrink-0">
                    <label class="text-[11px] font-medium text-blue-400 uppercase tracking-wider">Ajustes Percentuais (%)</label>
                    <div class="space-y-1">
                        <div class="flex justify-between text-[11px] text-slate-300">
                            <span>Ajuste Vc (%):</span>
                            <span id="vc-pct-val" class="font-bold text-cyan-400">0%</span>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <button onclick="ajustarPct('vc', -1)" class="bg-slate-700 hover:bg-slate-600 px-2 py-0.5 rounded text-white text-[10px] font-bold">-1%</button>
                            <input type="range" id="vc-slider" min="-50" max="50" value="0" step="1" class="w-full accent-blue-500" oninput="onSliderVc()">
                            <button onclick="ajustarPct('vc', 1)" class="bg-slate-700 hover:bg-slate-600 px-2 py-0.5 rounded text-white text-[10px] font-bold">+1%</button>
                            <button onclick="resetPct('vc')" class="bg-slate-900 border border-slate-600 text-slate-400 hover:text-white px-1.5 py-0.5 rounded text-[10px]">Reset</button>
                        </div>
                    </div>
                    <div class="space-y-1">
                        <div class="flex justify-between text-[11px] text-slate-300">
                            <span>Ajuste Avanço f (%):</span>
                            <span id="f-pct-val" class="font-bold text-cyan-400">0%</span>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <button onclick="ajustarPct('f', -1)" class="bg-slate-700 hover:bg-slate-600 px-2 py-0.5 rounded text-white text-[10px] font-bold">-1%</button>
                            <input type="range" id="f-slider" min="-50" max="50" value="0" step="1" class="w-full accent-blue-500" oninput="onSliderF()">
                            <button onclick="ajustarPct('f', 1)" class="bg-slate-700 hover:bg-slate-600 px-2 py-0.5 rounded text-white text-[10px] font-bold">+1%</button>
                            <button onclick="resetPct('f')" class="bg-slate-900 border border-slate-600 text-slate-400 hover:text-white px-1.5 py-0.5 rounded text-[10px]">Reset</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Resultados e Indicadores (Direita) -->
            <div class="lg:col-span-8 flex flex-col gap-2.5 min-h-0 overflow-y-auto">
                <!-- Grid de Métricas CNC Principal -->
                <div class="grid grid-cols-2 md:grid-cols-5 gap-2.5 shrink-0">
                    <div id="card-f" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="text-[11px] text-slate-400">Avanço (f)</span>
                            <button type="button" onclick="toggleLock('f')" id="btn-lock-f" title="Desbloquear para edição manual" class="text-xs px-1 py-0.5 rounded bg-slate-900/80 border border-slate-700 hover:border-slate-500 transition">🔒</button>
                        </div>
                        <input type="number" id="input-f" value="0.3850" step="0.005" min="0.001" readonly oninput="onManualInput('f')" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
                        <div class="flex justify-between items-center mt-0.5">
                            <span class="text-[9px] text-blue-400">mm/rot</span>
                            <span id="status-f" class="text-[9px] text-slate-500">Auto</span>
                        </div>
                    </div>

                    <div id="card-vc" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="text-[11px] text-slate-400">Vc</span>
                            <button type="button" onclick="toggleLock('vc')" id="btn-lock-vc" title="Desbloquear para edição manual" class="text-xs px-1 py-0.5 rounded bg-slate-900/80 border border-slate-700 hover:border-slate-500 transition">🔒</button>
                        </div>
                        <input type="number" id="input-vc" value="105" step="1" min="1" readonly oninput="onManualInput('vc')" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
                        <div class="flex justify-between items-center mt-0.5">
                            <span class="text-[9px] text-slate-400">m/min</span>
                            <span id="status-vc" class="text-[9px] text-slate-500">Auto</span>
                        </div>
                    </div>

                    <div id="card-rpm-max" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="text-[11px] text-slate-400">RPM Máx. Máquina</span>
                            <button type="button" onclick="toggleLock('rpm-max')" id="btn-lock-rpm-max" title="Desbloquear para definir limite de RPM" class="text-xs px-1 py-0.5 rounded bg-slate-900/80 border border-slate-700 hover:border-slate-500 transition">🔒</button>
                        </div>
                        <input type="number" id="input-rpm-max" value="8000" step="100" min="100" max="60000" readonly oninput="onManualInput('rpm-max')" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
                        <div class="flex justify-between items-center mt-0.5">
                            <span class="text-[9px] text-slate-400">rpm</span>
                            <span id="status-rpm-max" class="text-[9px] text-slate-500">Inativo</span>
                        </div>
                    </div>

                    <div class="bg-slate-800 p-2.5 rounded-lg border border-slate-700">
                        <span class="text-[11px] text-slate-400">Rotações (Spindle)</span>
                        <div class="text-xl font-bold text-white mt-0.5" id="res-n">4178</div>
                        <span class="text-[9px] text-slate-400">rpm</span>
                    </div>

                    <div class="bg-slate-800 p-2.5 rounded-lg border border-slate-700">
                        <span class="text-[11px] text-slate-400">Avanço Trabalho</span>
                        <div class="text-xl font-bold text-white mt-0.5" id="res-vf">1608</div>
                        <span class="text-[9px] text-slate-400">mm/min</span>
                    </div>
                </div>

                <!-- Gráficos Visuais em Meia-Lua -->
                <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 shrink-0">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[11px] font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                            <span>🎛️</span> Monitor Gráfico de Carga do Spindle (Conta-Rotações)
                        </span>
                        <span class="text-[10px] text-slate-400">Zona Verde (&lt;70%) | Amarela (70-90%) | Vermelha (&gt;90% Stall)</span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                        <div class="bg-slate-900/90 p-2.5 rounded-md border border-slate-700/80 flex flex-col items-center relative">
                            <span class="text-[10px] font-semibold text-slate-300 uppercase mb-1">Potência de Corte Requerida</span>
                            <div class="relative w-48 h-24 overflow-hidden flex justify-center items-end">
                                <svg class="w-48 h-24 overflow-visible" viewBox="0 0 200 100">
                                    <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#334155" stroke-width="16" stroke-linecap="round" />
                                    <path d="M 20 100 A 80 80 0 0 1 132.5 28.5" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" />
                                    <path d="M 132.5 28.5 A 80 80 0 0 1 165.4 53.2" fill="none" stroke="#f59e0b" stroke-width="16" />
                                    <path d="M 165.4 53.2 A 80 80 0 0 1 180 100" fill="none" stroke="#ef4444" stroke-width="16" stroke-linecap="round" />
                                    <g id="needle-potencia" transform="rotate(0, 100, 100)" style="transform-origin: 100px 100px; transition: transform 0.4s ease-in-out;">
                                        <line x1="100" y1="100" x2="100" y2="30" stroke="#ffffff" stroke-width="3" stroke-linecap="round" />
                                        <circle cx="100" cy="100" r="5" fill="#f8fafc" />
                                    </g>
                                </svg>
                            </div>
                            <div class="flex justify-between w-full px-2 mt-1 items-center">
                                <span class="text-xs font-bold text-white" id="val-gauge-pot">0.00 kW</span>
                                <span id="badge-gauge-pot" class="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">Standby</span>
                            </div>
                        </div>

                        <div class="bg-slate-900/90 p-2.5 rounded-md border border-slate-700/80 flex flex-col items-center relative">
                            <span class="text-[10px] font-semibold text-slate-300 uppercase mb-1">Binário de Corte Requerido (Mc)</span>
                            <div class="relative w-48 h-24 overflow-hidden flex justify-center items-end">
                                <svg class="w-48 h-24 overflow-visible" viewBox="0 0 200 100">
                                    <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#334155" stroke-width="16" stroke-linecap="round" />
                                    <path d="M 20 100 A 80 80 0 0 1 132.5 28.5" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" />
                                    <path d="M 132.5 28.5 A 80 80 0 0 1 165.4 53.2" fill="none" stroke="#f59e0b" stroke-width="16" />
                                    <path d="M 165.4 53.2 A 80 80 0 0 1 180 100" fill="none" stroke="#ef4444" stroke-width="16" stroke-linecap="round" />
                                    <g id="needle-binario" transform="rotate(0, 100, 100)" style="transform-origin: 100px 100px; transition: transform 0.4s ease-in-out;">
                                        <line x1="100" y1="100" x2="100" y2="30" stroke="#ffffff" stroke-width="3" stroke-linecap="round" />
                                        <circle cx="100" cy="100" r="5" fill="#f8fafc" />
                                    </g>
                                </svg>
                            </div>
                            <div class="flex justify-between w-full px-2 mt-1 items-center">
                                <span class="text-xs font-bold text-white" id="val-gauge-bin">0.0 N·m</span>
                                <span id="badge-gauge-bin" class="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">Standby</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Indicadores de Tempo e Volume -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
                    <div class="bg-gradient-to-r from-blue-900/40 to-slate-800 p-2.5 rounded-lg border border-blue-700/50 flex justify-between items-center">
                        <div>
                            <span class="text-[11px] text-blue-300 font-semibold uppercase tracking-wider">⏱️ Tempo de Ciclo (Total Lote / Unitário)</span>
                            <div class="text-lg font-extrabold text-white mt-0.5" id="res-tempo-total">0.0 min <span class="text-xs font-normal text-slate-300" id="res-tempo-unit">(0.0 seg/furo)</span></div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400">Metragem Linear (Lote)</span>
                            <div class="text-xs font-mono font-bold text-cyan-400" id="res-metragem">0.0 metros</div>
                        </div>
                    </div>
                    <div class="bg-gradient-to-r from-emerald-900/40 to-slate-800 p-2.5 rounded-lg border border-emerald-700/50 flex justify-between items-center">
                        <div>
                            <span class="text-[11px] text-emerald-300 font-semibold uppercase tracking-wider">📦 Volume de Material (Total Lote)</span>
                            <div class="text-lg font-extrabold text-white mt-0.5" id="res-volume-total">0.0 cm³</div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400">Taxa de Remoção</span>
                            <div class="text-xs font-mono font-bold text-emerald-400" id="res-taxa">-- cm³/min</div>
                        </div>
                    </div>
                </div>

                <!-- Peso e Sucata -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
                    <div class="bg-gradient-to-r from-cyan-900/40 to-slate-800 p-2.5 rounded-lg border border-cyan-700/50 flex justify-between items-center">
                        <div>
                            <span class="text-[11px] text-cyan-300 font-semibold uppercase tracking-wider">⚖️ Peso Total de Limalha (Lote)</span>
                            <div class="text-xl font-extrabold text-white mt-0.5" id="res-peso">0.000 <span class="text-sm font-normal text-slate-300">kg</span></div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400">Massa por Furo</span>
                            <div class="text-xs font-mono font-bold text-cyan-400" id="res-peso-g">0.00 g</div>
                        </div>
                    </div>
                    <div class="bg-gradient-to-r from-teal-900/40 to-slate-800 p-2.5 rounded-lg border border-teal-700/50 flex justify-between items-center">
                        <div>
                            <span class="text-[11px] text-teal-300 font-semibold uppercase tracking-wider">💶 Valor Total de Sucata (Lote)</span>
                            <div class="text-xl font-extrabold text-white mt-0.5" id="res-sucata-val">0.00 <span class="text-sm font-normal text-slate-300">€</span></div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400">Retorno Comercial</span>
                            <div class="text-xs font-mono font-bold text-teal-400" id="res-sucata-furo">0.00 € / furo</div>
                        </div>
                    </div>
                </div>

                <!-- Custos, Força e Binário -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 shrink-0">
                    <div class="bg-gradient-to-r from-indigo-900/40 to-slate-800 p-2.5 rounded-lg border border-indigo-700/50 flex justify-between items-center">
                        <div>
                            <span class="text-[11px] text-indigo-300 font-semibold uppercase tracking-wider">💰 Custo Maquinação</span>
                            <div class="text-base font-extrabold text-white mt-0.5" id="res-custo-total">0.00 € <span class="text-[10px] font-normal text-slate-300" id="res-custo-furo">(0.00 €/furo)</span></div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400">Custo Hora</span>
                            <div class="text-xs font-mono font-bold text-indigo-400" id="res-custo-hora-ref">50.00 €/h</div>
                        </div>
                    </div>
                    <div class="bg-gradient-to-r from-amber-900/40 to-slate-800 p-2.5 rounded-lg border border-amber-700/50 flex justify-between items-center">
                        <div>
                            <span class="text-[11px] text-amber-300 font-semibold uppercase tracking-wider">⚡ Força Axial (Ff)</span>
                            <div class="text-xl font-extrabold text-white mt-0.5" id="res-forca">0 <span class="text-sm font-normal text-slate-300">N</span></div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400">Esforço em Z</span>
                            <div class="text-xs font-mono font-bold text-amber-400" id="res-forca-kgf">0 kgf</div>
                        </div>
                    </div>
                    <div class="bg-gradient-to-r from-purple-900/40 to-slate-800 p-2.5 rounded-lg border border-purple-700/50 flex justify-between items-center">
                        <div>
                            <span class="text-[11px] text-purple-300 font-semibold uppercase tracking-wider">🔄 Binário de Corte (Mc)</span>
                            <div class="text-xl font-extrabold text-white mt-0.5" id="res-binario-card">0.0 <span class="text-sm font-normal text-slate-300">N·m</span></div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400">Torque Ferramenta</span>
                            <div class="text-xs font-mono font-bold text-purple-400">Estimado por kc</div>
                        </div>
                    </div>
                </div>

                <!-- Tabela e Gráfico -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 flex-1 min-h-[220px]">
                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 flex flex-col min-h-0">
                        <div class="flex justify-between items-center mb-1.5 shrink-0">
                            <h3 class="text-[11px] font-semibold text-slate-400 uppercase">Tabela de Referência do Catálogo</h3>
                            <span class="text-[9px] font-bold text-emerald-400" id="val-estado">Dentro da gama</span>
                        </div>
                        <div class="overflow-y-auto flex-1 min-h-0 max-h-[180px]">
                            <table class="w-full text-left text-xs">
                                <thead class="sticky top-0 bg-slate-800">
                                    <tr class="border-b border-slate-700 text-slate-400">
                                        <th class="pb-1">Ø (mm)</th>
                                        <th class="pb-1">f Cat.</th>
                                        <th class="pb-1">RPM (n)</th>
                                        <th class="pb-1">Avanço (v_f)</th>
                                    </tr>
                                </thead>
                                <tbody id="tabela-ref" class="divide-y divide-slate-700/50"></tbody>
                            </table>
                        </div>
                    </div>

                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 flex flex-col justify-between min-h-0">
                        <div class="flex justify-between items-center shrink-0">
                            <h3 class="text-[11px] font-semibold text-slate-400 uppercase">Curva por Intervalos: Avanço (f) vs. Ø</h3>
                            <span class="text-[9px] text-slate-400" id="badge-metodo">Interpolação Linear</span>
                        </div>
                        <div class="relative w-full flex-1 bg-slate-900 rounded-md border border-slate-700 p-1 flex items-center justify-center my-1.5 min-h-[120px]">
                            <svg id="svg-grafico" class="w-full h-full max-h-36" viewBox="0 0 400 180" preserveAspectRatio="xMidYMid meet"></svg>
                        </div>
                        <div class="flex justify-center gap-4 text-[9px] text-slate-400 shrink-0">
                            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-blue-500 inline-block"></span> Catálogo</span>
                            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-orange-500 inline-block"></span> Calculado</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- PASSO 1: Modal de Configuração da Comparação (Focado em Inputs Limpos) -->
        <div id="modal-comparacao" class="fixed inset-0 bg-black/75 flex items-center justify-center z-50 hidden p-3">
            <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 w-full max-w-3xl shadow-2xl flex flex-col gap-3.5 max-h-[92vh] overflow-y-auto">
                <div class="flex justify-between items-center border-b border-slate-700 pb-2.5">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2"><span>⚖️</span> Comparação Técnico-Comercial — Passo 1: Dados da Aplicação</h3>
                        <p class="text-[11px] text-slate-400">Preencha os parâmetros da ferramenta, reafiações e condições de oficina e clique em <strong>Ver Resultado &amp; Gráficos</strong>.</p>
                    </div>
                    <button onclick="fecharModalComparacao()" class="text-slate-400 hover:text-white font-bold text-sm px-2 py-1">✕</button>
                </div>

                <!-- Seleção da ferramenta a comparar + Botão de Condição de Corte Interrompido -->
                <div class="grid grid-cols-1 md:grid-cols-12 gap-3 bg-slate-900/90 p-3 rounded-lg border border-slate-700 items-end">
                    <div class="md:col-span-5 space-y-1">
                        <label class="text-[10px] font-semibold text-emerald-400 uppercase block">Selecionar Família ou Ferramenta do Cliente</label>
                        <select id="comp-ferramenta" class="w-full bg-slate-800 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onChangeFonteComparacao()"></select>
                    </div>
                    <div id="comp-bloco-variante" class="md:col-span-2 space-y-1">
                        <label class="text-[10px] font-semibold text-cyan-400 uppercase block">Variante ×D</label>
                        <select id="comp-variante" class="w-full bg-slate-800 border border-slate-700 rounded-md p-1.5 text-xs font-bold text-cyan-300 focus:outline-none focus:border-cyan-500" onchange="atualizarComparacao()"></select>
                    </div>
                    <div class="md:col-span-5 space-y-1">
                        <label class="text-[10px] font-semibold text-amber-300 uppercase block">Condição da Aplicação</label>
                        <button type="button" id="btn-corte-interrompido" onclick="toggleCorteInterrompido()" aria-pressed="false" class="w-full py-1.5 px-3 rounded-md text-xs font-semibold border transition flex items-center justify-center gap-1.5 bg-slate-800 border-slate-600 text-slate-300 hover:border-amber-500 hover:text-amber-200">
                            <span id="icone-corte-interrompido">○</span>
                            <span>Corte Interrompido (Interceções / Cascatas)</span>
                        </button>
                    </div>
                </div>

                <!-- Inputs manuais apenas quando "Ferramenta do Cliente (Manual)" está selecionada -->
                <div id="comp-bloco-cliente" class="bg-slate-900/90 p-3 rounded-lg border border-amber-700/50 space-y-3 hidden">
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div class="space-y-1">
                            <label class="text-[10px] font-semibold text-amber-300 uppercase block">Designação (Opcional)</label>
                            <input type="text" id="comp-cliente-nome" value="Ferramenta do Cliente" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1.5 text-xs text-white focus:outline-none focus:border-amber-500" oninput="atualizarComparacao()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] font-semibold text-amber-300 uppercase block">Vc Cliente (m/min)</label>
                            <input type="number" id="comp-cliente-vc" value="70" step="1" min="1" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1.5 text-xs font-bold text-white text-center focus:outline-none focus:border-amber-500" oninput="atualizarComparacao()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] font-semibold text-amber-300 uppercase block">Avanço f Cliente (mm/rot)</label>
                            <input type="number" id="comp-cliente-f" value="0.0200" step="0.005" min="0.001" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1.5 text-xs font-bold text-white text-center focus:outline-none focus:border-amber-500" oninput="atualizarComparacao()">
                        </div>
                    </div>

                    <!-- Furo-Piloto Prévio & Broca Canhão (Máquina Parada na Afiação) -->
                    <div class="pt-2.5 border-t border-slate-800 space-y-2.5">
                        <label class="flex items-center gap-2 cursor-pointer text-xs text-amber-200 font-medium">
                            <input type="checkbox" id="comp-requer-piloto" class="rounded bg-slate-800 border-slate-600 text-amber-500 focus:ring-0" onchange="togglePilotoInputs()">
                            <span>Requer furo-piloto prévio (ex.: broca canhão / broca longa)?</span>
                        </label>
                        <div id="comp-piloto-opcoes" class="space-y-2.5 pt-1 hidden">
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div class="space-y-1">
                                    <label class="text-[10px] font-semibold text-slate-300 uppercase block">Tempo furo-piloto + troca (seg/furo)</label>
                                    <input type="number" id="comp-tempo-piloto-seg" value="20" step="1" min="0" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-amber-500" oninput="atualizarComparacao()">
                                    <span class="text-[9px] text-slate-400 block text-center">Inclui troca de ferramenta, entrada guia e recuo.</span>
                                </div>
                                <div class="space-y-1">
                                    <label class="text-[10px] font-semibold text-slate-300 uppercase block">Custo adicional broca piloto / furo (€)</label>
                                    <input type="number" id="comp-custo-piloto-furo" value="0.05" step="0.01" min="0" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-amber-500" oninput="atualizarComparacao()">
                                    <span class="text-[9px] text-slate-400 block text-center">Desgaste diluído da broca curta de guia.</span>
                                </div>
                            </div>

                            <!-- Bloco Específico: Cliente Usa Broca Canhão -->
                            <div class="bg-slate-800/70 p-2.5 rounded-md border border-amber-600/40 space-y-2">
                                <label class="flex items-center gap-2 cursor-pointer text-xs text-amber-200 font-medium">
                                    <input type="checkbox" id="comp-usa-broca-canhao" class="rounded bg-slate-900 border-slate-600 text-amber-500 focus:ring-0" onchange="toggleBrocaCanhaoInputs()">
                                    <span>Cliente usa broca canhão (sem ferramenta gémea → máquina parada para afiar, montar e zerar)</span>
                                </label>
                                <div id="comp-canhao-opcoes" class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1 border-t border-slate-700/70 hidden">
                                    <div class="space-y-1">
                                        <label class="text-[10px] font-semibold text-amber-300 uppercase block">Tempo paragem máquina / afiação (min)</label>
                                        <input type="number" id="comp-tempo-paragem-afi-min" value="25" step="5" min="0" max="300" class="w-full bg-slate-900 border border-slate-700 rounded-md px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-amber-500" oninput="atualizarComparacao()">
                                        <span class="text-[9px] text-slate-400 block text-center">Parar, afiar ponta, montar, zerar e retomar.</span>
                                    </div>
                                    <div class="flex flex-col justify-center bg-slate-900/90 rounded-md px-2.5 py-1.5 border border-slate-700/80">
                                        <span class="text-[10px] text-slate-400 uppercase font-semibold">Pré-visualização Paragens</span>
                                        <span id="comp-canhao-resumo" class="text-xs font-bold text-amber-300 mt-0.5">0 paragens · +0.0 min</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Parâmetros Económicos da Comparação: Preço Brocas, Vida Útil e Reafiações -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-700/80">
                    <div class="space-y-2 border-b md:border-b-0 md:border-r border-slate-800 pb-2 md:pb-0 md:pr-3">
                        <span class="text-[10px] font-bold text-blue-400 uppercase block">Ferramenta MAPAL Atual</span>
                        <div class="grid grid-cols-2 gap-2">
                            <div class="space-y-1">
                                <label class="text-[10px] text-slate-400 block">Preço Broca (€)</label>
                                <input type="number" id="comp-preco-atual" value="680.00" step="5" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-blue-500" oninput="atualizarComparacao()">
                            </div>
                            <div class="space-y-1">
                                <div class="flex justify-between items-center">
                                    <label class="text-[10px] text-slate-400">Vida / Afiação</label>
                                    <select id="comp-vida-unid-atual" class="bg-slate-800 border border-slate-700 rounded px-1 text-[9px] text-cyan-400 focus:outline-none" onchange="atualizarComparacao()">
                                        <option value="furos" selected>furos</option>
                                        <option value="metros">metros</option>
                                    </select>
                                </div>
                                <input type="number" id="comp-vida-atual" value="90" step="10" min="1" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-blue-500" oninput="atualizarComparacao()">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2 pt-1">
                            <div class="space-y-1">
                                <label class="text-[10px] text-slate-400 block">N.º Reafiações</label>
                                <input type="number" id="comp-afi-qtd-atual" value="0" step="1" min="0" max="30" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-cyan-300 text-center focus:outline-none focus:border-blue-500" oninput="atualizarComparacao()">
                            </div>
                            <div class="space-y-1">
                                <label class="text-[10px] text-slate-400 block">Custo / Afiação (€)</label>
                                <input type="number" id="comp-afi-custo-atual" value="25.00" step="5" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-blue-500" oninput="atualizarComparacao()">
                            </div>
                        </div>
                    </div>

                    <div class="space-y-2">
                        <span class="text-[10px] font-bold text-emerald-400 uppercase block">Ferramenta a Comparar / Cliente</span>
                        <div class="grid grid-cols-2 gap-2">
                            <div class="space-y-1">
                                <label class="text-[10px] text-slate-400 block">Preço Broca (€)</label>
                                <input type="number" id="comp-preco-alvo" value="80.00" step="5" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-emerald-500" oninput="atualizarComparacao()">
                            </div>
                            <div class="space-y-1">
                                <div class="flex justify-between items-center">
                                    <label class="text-[10px] text-slate-400">Vida / Afiação</label>
                                    <select id="comp-vida-unid-alvo" class="bg-slate-800 border border-slate-700 rounded px-1 text-[9px] text-cyan-400 focus:outline-none" onchange="atualizarComparacao()">
                                        <option value="furos" selected>furos</option>
                                        <option value="metros">metros</option>
                                    </select>
                                </div>
                                <input type="number" id="comp-vida-alvo" value="250" step="10" min="1" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-emerald-500" oninput="atualizarComparacao()">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2 pt-1">
                            <div class="space-y-1">
                                <label class="text-[10px] text-slate-400 block">N.º Reafiações</label>
                                <input type="number" id="comp-afi-qtd-alvo" value="0" step="1" min="0" max="30" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-cyan-300 text-center focus:outline-none focus:border-emerald-500" oninput="atualizarComparacao()">
                            </div>
                            <div class="space-y-1">
                                <label class="text-[10px] text-slate-400 block">Custo / Afiação (€)</label>
                                <input type="number" id="comp-afi-custo-alvo" value="15.00" step="5" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-emerald-500" oninput="atualizarComparacao()">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Custo Hora Máquina + Referência de Corte Contínuo (quando corte interrompido ativo) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-900/60 px-3 py-2.5 rounded-lg border border-slate-700/70 items-center">
                    <div class="space-y-1">
                        <label class="text-[10px] font-semibold text-indigo-300 uppercase block">Preço / Custo Hora Máquina (€/h)</label>
                        <input type="number" id="comp-custo-hora" value="50.00" step="5" min="1" max="500" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-indigo-500" oninput="sincronizarCustoHoraComparacao()">
                    </div>
                    <div id="comp-nota-interrompido" class="text-[11px] text-amber-200 bg-amber-950/50 border border-amber-600/60 rounded-md px-2.5 py-2 space-y-1 hidden">
                        <div class="text-[10px] font-semibold text-amber-300">Corte Interrompido (Interceções / Cascatas)</div>
                        <div class="flex flex-wrap items-center gap-1.5">
                            <span class="text-[10px] text-amber-200">Ref. contínuo:</span>
                            <input type="number" id="comp-metros-continuo" value="90" step="5" min="1" max="2000" class="w-16 bg-slate-900 border border-amber-500/70 rounded px-1.5 py-0.5 text-xs font-bold text-white text-center focus:outline-none focus:border-amber-300" oninput="atualizarComparacao()">
                            <span class="text-[10px] text-amber-300">m</span>
                            <span id="comp-equiv-continuo" class="text-[10px] text-amber-100/90">(~643 furos)</span>
                        </div>
                    </div>
                </div>

                <div id="comp-aviso-grupo" class="text-[11px] text-amber-300 bg-amber-950/40 border border-amber-700/50 rounded-md px-3 py-2 hidden"></div>

                <!-- Rodapé do Passo 1: Incluir no PDF + Botão Principal de Abrir Janela de Resultados -->
                <div class="flex flex-wrap justify-between items-center gap-3 pt-2 border-t border-slate-700">
                    <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                        <input type="checkbox" id="comp-incluir-pdf" class="rounded bg-slate-900 border-slate-600 text-emerald-500 focus:ring-0" checked>
                        <span>Incluir este comparativo no PDF</span>
                    </label>
                    <div class="flex gap-2">
                        <button onclick="fecharModalComparacao()" class="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-md text-xs font-medium text-white transition">Fechar</button>
                        <button onclick="abrirJanelaResultadoComparacao()" class="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-md text-xs font-bold text-white shadow-lg transition flex items-center gap-1.5">
                            <span>📊</span> Ver Resultado &amp; Gráficos
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- PASSO 2: Janela Dedicada de Resultados Visuais, Gráficos Apelativos e Tabela -->
        <div id="modal-resultado-comparacao" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 hidden p-3">
            <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 w-full max-w-5xl shadow-2xl flex flex-col gap-4 max-h-[94vh] overflow-y-auto">
                <div class="flex flex-wrap justify-between items-center gap-2 border-b border-slate-700 pb-3">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <span>📊</span> Resultado do Comparativo Técnico-Comercial
                        </h3>
                        <p id="res-comp-subtitulo" class="text-[11px] text-cyan-300 font-medium mt-0.5">MAPAL vs. Ferramenta Comparada</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <button onclick="voltarParaInputsComparacao()" class="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-md text-xs font-semibold text-white transition flex items-center gap-1">
                            <span>←</span> Alterar Dados
                        </button>
                        <button onclick="fecharJanelaResultadoComparacao()" class="text-slate-400 hover:text-white font-bold text-sm px-2 py-1">✕</button>
                    </div>
                </div>

                <!-- Cartões Executivos de Impacto -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div class="bg-slate-900/90 p-3 rounded-lg border border-emerald-700/50">
                        <span class="text-[10px] font-semibold text-emerald-400 uppercase block">Capacidade &amp; Tempo</span>
                        <p id="comp-capacidade-texto" class="text-xs text-white font-medium mt-1">A calcular...</p>
                    </div>
                    <div class="bg-slate-900/90 p-3 rounded-lg border border-amber-600/50">
                        <span class="text-[10px] font-semibold text-amber-300 uppercase block">Ponto de Equilíbrio (Payback)</span>
                        <p id="comp-breakeven-texto" class="text-xs text-white font-medium mt-1">A calcular...</p>
                    </div>
                    <div class="bg-slate-900/90 p-3 rounded-lg border border-cyan-700/50">
                        <span class="text-[10px] font-semibold text-cyan-300 uppercase block">Impacto Financeiro no Lote</span>
                        <p id="comp-resumo-lote-destaque" class="text-xs text-white font-medium mt-1">A calcular...</p>
                    </div>
                </div>

                <!-- Gráficos Visuais Apelativos (SVG) -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
                    <!-- Gráfico 1: Composição do Custo Total no Lote -->
                    <div class="bg-slate-900/95 p-3 rounded-lg border border-slate-700 flex flex-col justify-between">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] font-bold text-indigo-300 uppercase">1. Custo Total no Lote (€)</span>
                            <span class="text-[9px] text-slate-400">Máq. + Ferr.</span>
                        </div>
                        <div class="w-full h-44 flex items-center justify-center">
                            <svg id="svg-comp-custo" class="w-full h-full" viewBox="0 0 300 175" preserveAspectRatio="xMidYMid meet"></svg>
                        </div>
                        <div class="flex justify-center gap-3 text-[9px] text-slate-400 pt-1 border-t border-slate-800">
                            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-blue-500 inline-block"></span> MAPAL</span>
                            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-rose-500 inline-block"></span> Comparada</span>
                        </div>
                    </div>

                    <!-- Gráfico 2: Tempo Total no Lote (Corte + Piloto + Paragens) -->
                    <div class="bg-slate-900/95 p-3 rounded-lg border border-slate-700 flex flex-col justify-between">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] font-bold text-cyan-300 uppercase">2. Tempo Total no Lote (min)</span>
                            <span class="text-[9px] text-slate-400">Corte + Extras</span>
                        </div>
                        <div class="w-full h-44 flex items-center justify-center">
                            <svg id="svg-comp-tempo" class="w-full h-full" viewBox="0 0 300 175" preserveAspectRatio="xMidYMid meet"></svg>
                        </div>
                        <div class="flex justify-center gap-3 text-[9px] text-slate-400 pt-1 border-t border-slate-800">
                            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block"></span> MAPAL</span>
                            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-amber-500 inline-block"></span> Comparada</span>
                        </div>
                    </div>

                    <!-- Gráfico 3: Curva de Ponto de Equilíbrio (Break-Even) -->
                    <div class="bg-slate-900/95 p-3 rounded-lg border border-slate-700 flex flex-col justify-between">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] font-bold text-amber-300 uppercase">3. Curva de Break-Even (€)</span>
                            <span class="text-[9px] text-slate-400">Acumulado</span>
                        </div>
                        <div class="w-full h-44 flex items-center justify-center">
                            <svg id="svg-comp-breakeven" class="w-full h-full" viewBox="0 0 300 175" preserveAspectRatio="xMidYMid meet"></svg>
                        </div>
                        <div class="flex justify-center gap-3 text-[9px] text-slate-400 pt-1 border-t border-slate-800">
                            <span class="flex items-center gap-1"><span class="w-2.5 h-0.5 bg-sky-400 inline-block"></span> MAPAL</span>
                            <span class="flex items-center gap-1"><span class="w-2.5 h-0.5 bg-amber-400 inline-block"></span> Comparada</span>
                        </div>
                    </div>
                </div>

                <!-- Tabela Detalhada Lado a Lado -->
                <div class="overflow-x-auto bg-slate-900 rounded-lg border border-slate-700">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b border-slate-700 text-slate-400 bg-slate-900/80">
                                <th class="py-2 px-3">Indicador</th>
                                <th class="py-2 px-3 text-blue-400" id="comp-th-atual">Ferramenta Atual</th>
                                <th class="py-2 px-3 text-emerald-400" id="comp-th-alvo">Ferramenta Comparada</th>
                                <th class="py-2 px-3 text-amber-300">Diferença</th>
                            </tr>
                        </thead>
                        <tbody id="comp-tabela-corpo" class="divide-y divide-slate-800"></tbody>
                    </table>
                </div>

                <!-- Rodapé do Passo 2 -->
                <div class="flex flex-wrap justify-between items-center gap-2 pt-1">
                    <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                        <input type="checkbox" id="comp-incluir-pdf-res" class="rounded bg-slate-900 border-slate-600 text-emerald-500 focus:ring-0" checked onchange="document.getElementById('comp-incluir-pdf').checked = this.checked">
                        <span>Incluir este comparativo no PDF</span>
                    </label>
                    <div class="flex gap-2">
                        <button id="btn-usar-comparada" onclick="aplicarFerramentaComparada()" class="bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded-md text-xs font-semibold text-white transition">Usar esta Ferramenta</button>
                        <button onclick="fecharJanelaResultadoComparacao()" class="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-md text-xs font-medium text-white transition">Fechar</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal de Seleção de Exportação PDF -->
        <div id="modal-export" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 hidden">
            <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 w-96 shadow-2xl flex flex-col gap-4">
                <div class="flex justify-between items-center">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2"><span>📄</span> Escolher Tipo de Proposta PDF</h3>
                    <button onclick="fecharModalExportacao()" class="text-slate-400 hover:text-white font-bold text-sm">✕</button>
                </div>
                <p class="text-xs text-slate-300">Selecione o nível de detalhe que pretende incluir na proposta técnico-comercial para o cliente:</p>
                <div class="flex flex-col gap-2">
                    <label class="flex items-start gap-2 bg-slate-900 p-2.5 rounded-md border border-slate-700 cursor-pointer hover:border-blue-500 transition">
                        <input type="radio" name="tipo-relatorio" value="resumido" class="mt-0.5 accent-blue-500" checked>
                        <div>
                            <strong class="text-xs text-white block">Proposta Comercial Resumida</strong>
                            <span class="text-[10px] text-slate-400">Ferramenta, Parâmetros de Corte (Vc, RPM, Avanço) e Custos por Furo/Lote.</span>
                        </div>
                    </label>
                    <label class="flex items-start gap-2 bg-slate-900 p-2.5 rounded-md border border-slate-700 cursor-pointer hover:border-blue-500 transition">
                        <input type="radio" name="tipo-relatorio" value="completo" class="mt-0.5 accent-blue-500">
                        <div>
                            <strong class="text-xs text-white block">Proposta Técnica Completa</strong>
                            <span class="text-[10px] text-slate-400">Inclui parâmetros, tempo total, volume, limalha, sucata, pecking e esforço/carga de spindle.</span>
                        </div>
                    </label>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button onclick="fecharModalExportacao()" class="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-md text-xs font-medium text-white transition">Cancelar</button>
                    <button onclick="gerarPDF()" class="bg-blue-600 hover:bg-blue-500 px-3 py-1.5 rounded-md text-xs font-medium text-white transition flex items-center gap-1"><span>📥</span> Gerar PDF</button>
                </div>
            </div>
        </div>

        <!-- Rodapé -->
        <footer class="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/80 flex flex-col sm:flex-row justify-between items-center gap-2 text-[11px] text-slate-400 shrink-0">
            <div class="font-medium text-slate-300">
                Created by <span class="text-white font-semibold">Bruno Pinto</span>
            </div>
            <div class="flex flex-wrap items-center gap-4">
                <a href="mailto:bruno.pinto@alamo-ferramentas.com" class="hover:text-blue-400 transition flex items-center gap-1">
                    <span>✉️</span> bruno.pinto@alamo-ferramentas.com
                </a>
                <a href="tel:+351936959415" class="hover:text-blue-400 transition flex items-center gap-1">
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
        let rpmMaxUnlocked = false;
        let corteInterrompidoAtivo = false;

        const GRUPOS_MAPAL_PADRAO = {
            gruposList: [
                "P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P5.1", "P6.1",
                "M1.1", "M1.2", "M2.1", "M3.1",
                "K1.1", "K2.1", "K2.2", "K2.3", "K3.1", "K3.2",
                "N1.1", "N1.2", "N1.3", "N1.4", "N2.1", "N2.2", "N2.3", "N3.1", "N3.2",
                "S1.1", "S2.1", "S2.2", "S3.1", "S3.2", "S4.1", "S5.1",
                "H1.1", "H1.2", "H2.1", "H2.2", "H2.3",
                "C1.1", "C1.2", "C1.3", "C2.1", "C3.1"
            ],
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
                "N2.3": "N2.3 — Latão, bronze (< 1200 N/mm²)",
                "N3.1": "N3.1 — Grafite, > 8 µm",
                "N3.2": "N3.2 — Grafite, ≤ 8 µm",
                "S1.1": "S1.1 — Titânio e ligas de titânio (< 400 N/mm²)",
                "S2.1": "S2.1 — Titânio e ligas de titânio (< 1200 N/mm²)",
                "S2.2": "S2.2 — Titânio e ligas de titânio (> 1200 N/mm²)",
                "S3.1": "S3.1 — Níquel não ligado e ligado (< 900 N/mm²)",
                "S3.2": "S3.2 — Níquel não ligado e ligado (> 900 N/mm²)",
                "S4.1": "S4.1 — Superligas de alta temperatura (Ni, Co, Fe)",
                "S5.1": "S5.1 — Ligas de tungsténio e molibdénio",
                "H1.1": "H1.1 — Aços temperados / Aço fundido (< 44 HRC)",
                "H1.2": "H1.2 — Aços temperados / Aço fundido (< 55 HRC)",
                "H2.1": "H2.1 — Aços temperados / Aço fundido (< 60 HRC)",
                "H2.2": "H2.2 — Aços temperados / Aço fundido (< 65 HRC)",
                "H2.3": "H2.3 — Aços temperados / Aço fundido (< 68 HRC)",
                "C1.1": "C1.1 — Matriz plástica, reforçada com fibra de aramida (AFRP)",
                "C1.2": "C1.2 — Matriz plástica (termofixa), CFRP / GFRP",
                "C1.3": "C1.3 — Matriz plástica (termoplástica), CFRP / GFRP",
                "C2.1": "C2.1 — Matriz de carbono, reforçada com fibra de carbono (CFC)",
                "C3.1": "C3.1 — Matriz metálica (MMC)"
            }
        };

        function construirFerramenta(cfg) {
            const gruposList = Object.keys(cfg.grupos);
            const gruposNames = {};
            gruposList.forEach(g => {
                gruposNames[g] = GRUPOS_MAPAL_PADRAO.gruposNames[g] || g;
            });
            return {
                linha: cfg.linha,
                categoria: cfg.categoria,
                temRefrigInt: cfg.temRefrigInt,
                nome: cfg.nome,
                variantes: cfg.variantes,
                diametros: cfg.diametros,
                gruposList,
                gruposNames,
                grupos: cfg.grupos
            };
        }

        const dados = {
            scd631: construirFerramenta({
                linha: 'expert', categoria: 'solid', temRefrigInt: true,
                nome: 'Tritan-Drill-Uni-Plus SCD631',
                variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
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
            }),
            scd221: construirFerramenta({
                linha: 'expert', categoria: 'solid', temRefrigInt: true,
                nome: 'MEGA-Speed-Drill-Uni SCD221',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd231: construirFerramenta({
                linha: 'expert', categoria: 'spot', temRefrigInt: true,
                nome: 'MEGA-180°-Drill SCD231',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd241: construirFerramenta({
                linha: 'expert', categoria: 'spot', temRefrigInt: true,
                nome: 'MEGA-180°-Drill-Alu SCD241',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
                grupos: {
                    "N1.1": { vc: {int:240, ext:160, mql:200, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
                    "N1.2": { vc: {int:200, ext:145, mql:160, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
                    "N1.3": { vc: {int:175, ext:145, mql:120, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
                    "N1.4": { vc: {int:145, ext:95, mql:120, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
                    "N2.1": { vc: {int:110, ext:80, mql:0, ar:0}, f: [0.07, 0.09, 0.12, 0.16, 0.20, 0.24] },
                    "N2.2": { vc: {int:95, ext:70, mql:0, ar:0}, f: [0.09, 0.12, 0.16, 0.21, 0.26, 0.31] },
                    "N2.3": { vc: {int:160, ext:130, mql:130, ar:95}, f: [0.09, 0.14, 0.19, 0.25, 0.33, 0.39] }
                }
            }),
            scd661: construirFerramenta({
                linha: 'expert', categoria: 'solid', temRefrigInt: true,
                nome: 'Tritan-Drill-Steel SCD661',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
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
            }),
            scd621: construirFerramenta({
                linha: 'expert', categoria: 'solid', temRefrigInt: true,
                nome: 'MEGA-Speed-Drill-Steel SCD621',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd411: construirFerramenta({
                linha: 'expert', categoria: 'deep', temRefrigInt: true,
                nome: 'MEGA-Speed-Drill-Inox SCD411',
                variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd421: construirFerramenta({
                linha: 'expert', categoria: 'solid', temRefrigInt: true,
                nome: 'MEGA-Speed-Drill-Iron SCD421',
                variantes: { '5xD': { ratio: 5 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
                grupos: {
                    "K1.1": { vc: {int:170, ext:120, mql:120, ar:120}, f: [0.15, 0.21, 0.29, 0.40, 0.51, 0.61] },
                    "K2.1": { vc: {int:225, ext:170, mql:170, ar:140}, f: [0.15, 0.21, 0.28, 0.37, 0.48, 0.57] },
                    "K2.2": { vc: {int:140, ext:105, mql:105, ar:105}, f: [0.14, 0.19, 0.32, 0.25, 0.41, 0.49] },
                    "K2.3": { vc: {int:85, ext:55, mql:70, ar:0}, f: [0.10, 0.13, 0.17, 0.22, 0.27, 0.32] },
                    "K3.1": { vc: {int:125, ext:110, mql:110, ar:0}, f: [0.15, 0.20, 0.35, 0.26, 0.44, 0.52] },
                    "K3.2": { vc: {int:110, ext:100, mql:100, ar:0}, f: [0.13, 0.17, 0.22, 0.28, 0.35, 0.41] }
                }
            }),
            scd271: construirFerramenta({
                linha: 'expert', categoria: 'solid', temRefrigInt: true,
                nome: 'MEGA-Drill-Composite-UDX SCD271',
                variantes: { '5xD': { ratio: 5 } },
                diametros: [3.00, 4.00, 5.50, 7.50, 10.00, 12.00],
                grupos: {
                    "C1.1": { vc: {int:90, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
                    "C1.2": { vc: {int:75, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
                    "C1.3": { vc: {int:75, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
                    "C2.1": { vc: {int:90, ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] }
                }
            }),
            scd270: construirFerramenta({
                linha: 'expert', categoria: 'solid', temRefrigInt: false,
                nome: 'MEGA-Drill-Composite-UDX SCD270',
                variantes: { '5xD': { ratio: 5 } },
                diametros: [3.00, 4.00, 5.50, 7.50, 10.00, 12.00],
                grupos: {
                    "C1.1": { vc: {ext:90, mql:90, ar:90}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
                    "C1.2": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
                    "C1.3": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] },
                    "C2.1": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.06, 0.05, 0.07, 0.08] }
                }
            }),
            scd600: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: false,
                nome: 'MEGA-Drill-Steel-Plus SCD600 (Sem Refrig. Interna)',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd601: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: true,
                nome: 'MEGA-Drill-Steel-Plus SCD601',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd610: construirFerramenta({
                linha: 'performance', categoria: 'stepped', temRefrigInt: false,
                nome: 'MEGA-Quadro-Drill-Plus SCD610',
                variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
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
            }),
            scd611: construirFerramenta({
                linha: 'performance', categoria: 'stepped', temRefrigInt: true,
                nome: 'MEGA-Quadro-Drill-Plus SCD611',
                variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
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
            }),
            scd371: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: true,
                nome: 'MICRO-Drill-Steel SCD371',
                variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [4.00, 5.50, 7.50, 10.50, 14.50, 20.00],
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
            }),
            scd140: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: false,
                nome: 'MEGA-Drill-Hardened SCD140',
                variantes: { '4xD': { ratio: 4 } },
                diametros: [2.50, 3.62, 5.25, 7.61, 11.04, 16.00],
                grupos: {
                    "H1.1": { vc: {ext:80, mql:80, ar:0}, f: [0.07, 0.09, 0.11, 0.02, 0.19, 0.20] },
                    "H1.2": { vc: {ext:30, mql:30, ar:0}, f: [0.05, 0.06, 0.10, 0.08, 0.13, 0.16] },
                    "H2.1": { vc: {ext:30, mql:30, ar:0}, f: [0.04, 0.05, 0.09, 0.07, 0.11, 0.13] },
                    "H2.2": { vc: {ext:20, mql:20, ar:0}, f: [0.03, 0.04, 0.05, 0.06, 0.08, 0.09] },
                    "H2.3": { vc: {ext:15, mql:15, ar:0}, f: [0.03, 0.04, 0.05, 0.06, 0.08, 0.09] }
                }
            }),
            scd131: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: true,
                nome: 'MEGA-Drill-Alu SCD131',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
                grupos: {
                    "N1.1": { vc: {int:300, ext:200, mql:250, ar:200}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
                    "N1.2": { vc: {int:250, ext:180, mql:200, ar:160}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
                    "N1.3": { vc: {int:220, ext:150, mql:180, ar:160}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
                    "N1.4": { vc: {int:180, ext:120, mql:150, ar:120}, f: [0.11, 0.15, 0.20, 0.26, 0.33, 0.39] },
                    "N2.1": { vc: {int:140, ext:100, mql:120, ar:0}, f: [0.09, 0.12, 0.15, 0.20, 0.25, 0.30] },
                    "N2.2": { vc: {int:120, ext:90, mql:100, ar:0}, f: [0.11, 0.15, 0.26, 0.20, 0.33, 0.39] },
                    "N2.3": { vc: {int:200, ext:160, mql:160, ar:0}, f: [0.09, 0.14, 0.19, 0.25, 0.33, 0.39] }
                }
            }),
            scd250: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: false,
                nome: 'MEGA-Drill-Composite-MD SCD250',
                variantes: { '5xD': { ratio: 5 } },
                diametros: [3.00, 4.00, 5.50, 7.50, 10.00, 12.00],
                grupos: {
                    "N3.1": { vc: {ext:200, mql:200, ar:200}, f: [0.07, 0.09, 0.11, 0.14, 0.16, 0.18] },
                    "N3.2": { vc: {ext:200, mql:200, ar:200}, f: [0.07, 0.09, 0.11, 0.14, 0.16, 0.18] },
                    "C1.1": { vc: {ext:90, mql:90, ar:90}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
                    "C1.2": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
                    "C1.3": { vc: {ext:75, mql:75, ar:75}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
                    "C2.1": { vc: {ext:400, mql:400, ar:400}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] },
                    "C3.1": { vc: {ext:400, mql:400, ar:400}, f: [0.04, 0.04, 0.05, 0.06, 0.07, 0.08] }
                }
            }),
            scd120: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: false,
                nome: 'MEGA-Drill-Inox SCD120',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd121: construirFerramenta({
                linha: 'performance', categoria: 'solid', temRefrigInt: true,
                nome: 'MEGA-Drill-Inox SCD121',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
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
            }),
            scd350: construirFerramenta({
                linha: 'basic', categoria: 'solid', temRefrigInt: false,
                nome: 'ECU-Drill-Uni SCD350 (Sem Refrig. Interna)',
                variantes: { '4xD': { ratio: 4 }, '6xD': { ratio: 6 } },
                diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
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
            }),
            scd351: construirFerramenta({
                linha: 'basic', categoria: 'solid', temRefrigInt: true,
                nome: 'ECU-Drill-Uni SCD351',
                variantes: { '4xD': { ratio: 4 }, '6xD': { ratio: 6 } },
                diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
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
            }),
            scd360: construirFerramenta({
                linha: 'basic', categoria: 'solid', temRefrigInt: false,
                nome: 'ECU-Drill-Steel SCD360',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
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
            }),
            scd361: construirFerramenta({
                linha: 'basic', categoria: 'solid', temRefrigInt: true,
                nome: 'ECU-Drill-Steel SCD361',
                variantes: { '3xD': { ratio: 3 }, '5xD': { ratio: 5 }, '8xD': { ratio: 8 }, '12xD': { ratio: 12 } },
                diametros: [1.00, 1.82, 3.31, 6.03, 10.99, 20.00],
                grupos: {
                    "P1.1": { vc: {int:75, ext:70, mql:70, ar:70}, f: [0.04, 0.06, 0.08, 0.13, 0.20, 0.27] },
                    "P1.2": { vc: {int:70, ext:55, mql:55, ar:55}, f: [0.05, 0.07, 0.11, 0.16, 0.24, 0.33] },
                    "P2.1": { vc: {int:75, ext:65, mql:65, ar:65}, f: [0.05, 0.07, 0.10, 0.15, 0.23, 0.31] },
                    "P2.2": { vc: {int:55, ext:45, mql:45, ar:45}, f: [0.05, 0.06, 0.13, 0.09, 0.18, 0.25] },
                    "P3.1": { vc: {int:55, ext:50, mql:50, ar:50}, f: [0.04, 0.06, 0.14, 0.09, 0.21, 0.28] },
                    "P3.2": { vc: {int:45, ext:40, mql:40, ar:40}, f: [0.04, 0.05, 0.12, 0.08, 0.17, 0.23] },
                    "P3.3": { vc: {int:45, ext:40, mql:35, ar:35}, f: [0.04, 0.05, 0.06, 0.09, 0.13, 0.18] },
                    "P5.1": { vc: {int:75, ext:65, mql:65, ar:65}, f: [0.05, 0.07, 0.15, 0.10, 0.23, 0.31] },
                    "K1.1": { vc: {int:45, ext:40, mql:35, ar:35}, f: [0.03, 0.04, 0.09, 0.06, 0.14, 0.19] },
                    "K2.1": { vc: {int:80, ext:60, mql:60, ar:60}, f: [0.04, 0.07, 0.12, 0.20, 0.32, 0.44] },
                    "K2.2": { vc: {int:110, ext:80, mql:70, ar:80}, f: [0.05, 0.07, 0.12, 0.19, 0.30, 0.41] },
                    "K2.3": { vc: {int:70, ext:50, mql:50, ar:50}, f: [0.04, 0.07, 0.11, 0.17, 0.26, 0.35] },
                    "K3.1": { vc: {int:40, ext:35, mql:25, ar:25}, f: [0.04, 0.05, 0.08, 0.12, 0.17, 0.23] },
                    "K3.2": { vc: {int:60, ext:55, mql:55, ar:55}, f: [0.05, 0.07, 0.11, 0.18, 0.27, 0.38] }
                }
            }),
            scd211: construirFerramenta({
                linha: 'basic', categoria: 'solid', temRefrigInt: true,
                nome: 'ECU-G-Drill SCD211',
                variantes: { '5xD': { ratio: 5 }, '8xD': { ratio: 8 } },
                diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00],
                grupos: {
                    "K1.1": { vc: {int:90, ext:65, mql:65, ar:65}, f: [0.08, 0.12, 0.16, 0.22, 0.29, 0.34] },
                    "K2.1": { vc: {int:120, ext:90, mql:75, ar:90}, f: [0.08, 0.12, 0.16, 0.21, 0.27, 0.32] },
                    "K2.2": { vc: {int:75, ext:55, mql:55, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
                    "N1.2": { vc: {int:215, ext:155, mql:170, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
                    "N1.3": { vc: {int:185, ext:155, mql:130, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
                    "N1.4": { vc: {int:155, ext:100, mql:130, ar:0}, f: [0.08, 0.10, 0.14, 0.18, 0.23, 0.27] },
                    "N2.3": { vc: {int:160, ext:130, mql:130, ar:95}, f: [0.08, 0.12, 0.16, 0.22, 0.29, 0.34] }
                }
            })
        };

        const propriedadesGrupo = {
            'P': { kc: 2200, densidade: 7.85 },
            'M': { kc: 2800, densidade: 7.90 },
            'K': { kc: 1800, densidade: 7.20 },
            'N': { kc: 800,  densidade: 2.70 },
            'S': { kc: 3400, densidade: 4.50 },
            'H': { kc: 3200, densidade: 7.85 },
            'C': { kc: 1500, densidade: 1.60 }
        };

        function getKc(grupoKey) {
            const prefixo = grupoKey.charAt(0).toUpperCase();
            return propriedadesGrupo[prefixo] ? propriedadesGrupo[prefixo].kc : 2200;
        }

        function getDensidadePadrao(grupoKey) {
            const prefixo = grupoKey.charAt(0).toUpperCase();
            return propriedadesGrupo[prefixo] ? propriedadesGrupo[prefixo].densidade : 7.85;
        }

        function togglePilotoInputs() {
            const checked = document.getElementById('comp-requer-piloto').checked;
            const opcoes = document.getElementById('comp-piloto-opcoes');
            if (checked) {
                opcoes.classList.remove('hidden');
            } else {
                opcoes.classList.add('hidden');
                document.getElementById('comp-usa-broca-canhao').checked = false;
                document.getElementById('comp-canhao-opcoes').classList.add('hidden');
            }
            atualizarComparacao();
        }

        function toggleBrocaCanhaoInputs() {
            const checked = document.getElementById('comp-usa-broca-canhao').checked;
            const opcoes = document.getElementById('comp-canhao-opcoes');
            if (checked) {
                opcoes.classList.remove('hidden');
            } else {
                opcoes.classList.add('hidden');
            }
            atualizarComparacao();
        }

        function toggleCorteInterrompido() {
            corteInterrompidoAtivo = !corteInterrompidoAtivo;
            atualizarEstadoBotaoInterrompido();
            atualizarComparacao();
        }

        function atualizarEstadoBotaoInterrompido() {
            const btn = document.getElementById('btn-corte-interrompido');
            const icone = document.getElementById('icone-corte-interrompido');
            const nota = document.getElementById('comp-nota-interrompido');
            if (!btn || !icone || !nota) return;

            btn.setAttribute('aria-pressed', corteInterrompidoAtivo ? 'true' : 'false');
            if (corteInterrompidoAtivo) {
                btn.className = "w-full py-1.5 px-3 rounded-md text-xs font-semibold border transition flex items-center justify-center gap-1.5 bg-amber-600/25 border-amber-400 text-amber-200 shadow-sm";
                icone.innerText = "●";
                nota.classList.remove('hidden');
            } else {
                btn.className = "w-full py-1.5 px-3 rounded-md text-xs font-semibold border transition flex items-center justify-center gap-1.5 bg-slate-800 border-slate-600 text-slate-300 hover:border-amber-500 hover:text-amber-200";
                icone.innerText = "○";
                nota.classList.add('hidden');
            }
        }

        function toggleFullScreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    alert(`Erro ao tentar modo ecrã inteiro: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }

        function resetRapidoTudo() {
            if (fUnlocked) toggleLock('f');
            if (vcUnlocked) toggleLock('vc');
            if (rpmMaxUnlocked) toggleLock('rpm-max');

            document.getElementById('input-rpm-max').value = 8000;

            vcPct = 0;
            fPct = 0;
            document.getElementById('vc-slider').value = 0;
            document.getElementById('f-slider').value = 0;

            document.getElementById('pecking-check').checked = false;
            document.getElementById('pecking-options').classList.add('hidden');
            document.getElementById('pecking-unidade').value = 'xd';
            document.getElementById('pecking-passo').step = '0.5';
            document.getElementById('pecking-passo').value = '3.0';
            document.getElementById('pecking-retensao').value = '5000';

            atualizarCalculo();
        }

        function togglePeckingInputs() {
            const isChecked = document.getElementById('pecking-check').checked;
            const container = document.getElementById('pecking-options');
            if (isChecked) {
                container.classList.remove('hidden');
            } else {
                container.classList.add('hidden');
            }
            atualizarCalculo();
        }

        function onChangePeckingUnidade() {
            const unid = document.getElementById('pecking-unidade').value;
            const inputPasso = document.getElementById('pecking-passo');
            let diametro = parseFloat(document.getElementById('diametro').value);
            if (isNaN(diametro) || diametro <= 0) diametro = 12.00;

            let valAtual = parseFloat(inputPasso.value);
            if (isNaN(valAtual) || valAtual <= 0) valAtual = unid === 'xd' ? 3.0 : 36.0;

            if (unid === 'mm') {
                inputPasso.step = '1';
                inputPasso.value = (valAtual * diametro).toFixed(1);
            } else {
                inputPasso.step = '0.5';
                inputPasso.value = (valAtual / diametro).toFixed(2);
            }
            atualizarCalculo();
        }

        function obterLimiteNominal(toolData, varianteKey, diametro) {
            const varObj = toolData.variantes ? toolData.variantes[varianteKey] : null;
            const ratio = varObj ? varObj.ratio : 5;
            const maxNominalMm = ratio * diametro;
            return { ratio, maxNominalMm };
        }

        function calcularMetricasFerramenta(toolKey, varianteKey, grupoEfetivoKey, contexto) {
            const toolData = dados[toolKey];
            if (!toolData) return null;
            const grupoObj = toolData.grupos[grupoEfetivoKey];
            if (!grupoObj) return null;

            const {
                diametro, profundidade, qtdFuros, custoHora,
                refrigAtual, vcPct, fPct, rpmMaxUnlocked, rpmMaxVal,
                peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal
            } = contexto;

            const diametrosCat = toolData.diametros;
            const fCatArr = grupoObj.f;

            let idxInf = 0;
            for (let i = 0; i < diametrosCat.length; i++) {
                if (diametrosCat[i] <= diametro) {
                    idxInf = i;
                } else {
                    break;
                }
            }

            let estadoTexto = "Dentro da gama";
            let estadoCor = "text-emerald-400";
            let badgeMetodo = "Interpolação Linear";

            if (diametrosCat.length > 1) {
                if (idxInf >= diametrosCat.length - 1) {
                    idxInf = diametrosCat.length - 2;
                    estadoTexto = "Extrapolação Superior";
                    estadoCor = "text-amber-400";
                    badgeMetodo = "Extrapolação Superior";
                } else if (diametro < diametrosCat[0]) {
                    idxInf = 0;
                    estadoTexto = "Extrapolação Inferior";
                    estadoCor = "text-amber-400";
                    badgeMetodo = "Extrapolação Inferior";
                }
            }

            const x1 = diametrosCat[idxInf];
            const x2 = diametrosCat[idxInf + 1] !== undefined ? diametrosCat[idxInf + 1] : x1 + 1;
            const y1 = fCatArr[idxInf];
            const y2 = fCatArr[idxInf + 1] !== undefined ? fCatArr[idxInf + 1] : y1;

            const b = (x2 - x1) !== 0 ? (y2 - y1) / (x2 - x1) : 0;
            const a = y1 - b * x1;

            let fBase = a + b * diametro;
            if (fBase < 0.001) fBase = 0.001;
            let fFinal = fBase * (1 + fPct / 100);

            let vcBase = 100;
            if (grupoObj.vc) {
                if (grupoObj.vc[refrigAtual] !== undefined && grupoObj.vc[refrigAtual] > 0) {
                    vcBase = grupoObj.vc[refrigAtual];
                } else if (grupoObj.vc['int'] !== undefined && grupoObj.vc['int'] > 0) {
                    vcBase = grupoObj.vc['int'];
                } else if (grupoObj.vc['ext'] !== undefined) {
                    vcBase = grupoObj.vc['ext'];
                }
            }
            let vcFinal = vcBase * (1 + vcPct / 100);

            let n = diametro > 0 ? Math.round((vcFinal * 1000) / (Math.PI * diametro)) : 0;
            if (rpmMaxUnlocked && rpmMaxVal > 0 && n > rpmMaxVal) {
                n = rpmMaxVal;
                vcFinal = (n * Math.PI * diametro) / 1000;
                estadoTexto = "Limitado por RPM Máx.";
                estadoCor = "text-amber-400";
            }

            const vf = Math.round(fFinal * n);
            const cursoEfetivo = profundidade + (0.3 * diametro);
            let tempoFuroSeg = vf > 0 ? (cursoEfetivo / vf) * 60 : 0;

            const passoMm = peckingUnid === 'xd' ? (peckingInputVal * diametro) : peckingInputVal;
            const numPassos = Math.max(1, Math.ceil(profundidade / passoMm));

            if (peckingCheck) {
                const tempoCortePassos = vf > 0 ? (profundidade / vf) * 60 : 0;
                const tempoRetracaoSeg = (numPassos * (profundidade / peckingRetensaoVal)) * 60;
                const tempoEntradaSeg = vf > 0 ? ((0.3 * diametro / vf) * 60) : 0;
                tempoFuroSeg = tempoCortePassos + tempoRetracaoSeg + tempoEntradaSeg;
            }

            const custoHoraSeg = custoHora / 3600;
            const custoMaqFuro = tempoFuroSeg * custoHoraSeg;
            const tempoTotalMin = (tempoFuroSeg * qtdFuros) / 60;
            const custoMaqLote = custoMaqFuro * qtdFuros;

            const kc = getKc(grupoEfetivoKey);
            const forcaFf = 0.5 * kc * diametro * Math.pow(fFinal, 0.7);
            const binarioMc = (kc * Math.pow(diametro, 2) * Math.pow(fFinal, 0.8)) / 8000;
            const potenciaReqKw = (binarioMc * n) / (9550 * 0.85);
            const limiteInfo = obterLimiteNominal(toolData, varianteKey, diametro);

            return {
                toolKey,
                nome: toolData.nome,
                varianteKey,
                limiteNominalMm: limiteInfo.maxNominalMm,
                idxInf,
                estadoTexto,
                estadoCor,
                badgeMetodo,
                vcFinal,
                fFinal,
                n,
                vf,
                tempoFuroSeg,
                tempoTotalMin,
                custoMaqFuro,
                custoMaqLote,
                forcaFf,
                binarioMc,
                potenciaReqKw
            };
        }

        function calcularMetricasManualCliente(nomeCliente, vcManual, fManual, grupoEfetivoKey, contexto) {
            const {
                diametro, profundidade, qtdFuros, custoHora,
                rpmMaxUnlocked, rpmMaxVal,
                peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal,
                requerPiloto = false, tempoPilotoSeg = 0, custoPilotoFuro = 0,
                usaBrocaCanhao = false, tempoParagemAfiMin = 0, furosPorAfiação = 20
            } = contexto;

            let vcFinal = vcManual > 0 ? vcManual : 1;
            const fFinal = fManual > 0 ? fManual : 0.001;

            let n = diametro > 0 ? Math.round((vcFinal * 1000) / (Math.PI * diametro)) : 0;
            if (rpmMaxUnlocked && rpmMaxVal > 0 && n > rpmMaxVal) {
                n = rpmMaxVal;
                vcFinal = (n * Math.PI * diametro) / 1000;
            }

            const vf = Math.round(fFinal * n);
            const cursoEfetivo = profundidade + (0.3 * diametro);
            let tempoCorteFuroSeg = vf > 0 ? (cursoEfetivo / vf) * 60 : 0;

            const passoMm = peckingUnid === 'xd' ? (peckingInputVal * diametro) : peckingInputVal;
            const numPassos = Math.max(1, Math.ceil(profundidade / passoMm));

            if (peckingCheck) {
                const tempoCortePassos = vf > 0 ? (profundidade / vf) * 60 : 0;
                const tempoRetracaoSeg = (numPassos * (profundidade / peckingRetensaoVal)) * 60;
                const tempoEntradaSeg = vf > 0 ? ((0.3 * diametro / vf) * 60) : 0;
                tempoCorteFuroSeg = tempoCortePassos + tempoRetracaoSeg + tempoEntradaSeg;
            }

            const pilotoSegEfetivo = requerPiloto ? Math.max(0, tempoPilotoSeg) : 0;
            const custoPilotoEfetivo = requerPiloto ? Math.max(0, custoPilotoFuro) : 0;

            const canhaoAtivo = requerPiloto && usaBrocaCanhao;
            const vidaCicloCanhao = Math.max(1, furosPorAfiação || 20);
            const tempoParagemMinVal = Math.max(0, tempoParagemAfiMin || 0);
            const numParagensLote = canhaoAtivo ? Math.floor(Math.max(0, qtdFuros - 1) / vidaCicloCanhao) : 0;
            const tempoParagemCanhaoLoteMin = canhaoAtivo ? (numParagensLote * tempoParagemMinVal) : 0;
            const tempoParagemCanhaoFuroSeg = qtdFuros > 0 ? ((tempoParagemCanhaoLoteMin * 60) / qtdFuros) : 0;

            const tempoFuroSeg = tempoCorteFuroSeg + pilotoSegEfetivo + tempoParagemCanhaoFuroSeg;
            const tempoPilotoLoteMin = (pilotoSegEfetivo * qtdFuros) / 60;

            const custoHoraSeg = custoHora / 3600;
            const custoMaqFuro = tempoFuroSeg * custoHoraSeg;
            const tempoTotalMin = (tempoFuroSeg * qtdFuros) / 60;
            const custoMaqLote = custoMaqFuro * qtdFuros;
            const custoPilotoLote = custoPilotoEfetivo * qtdFuros;

            const kc = getKc(grupoEfetivoKey);
            const forcaFf = 0.5 * kc * diametro * Math.pow(fFinal, 0.7);
            const binarioMc = (kc * Math.pow(diametro, 2) * Math.pow(fFinal, 0.8)) / 8000;
            const potenciaReqKw = (binarioMc * n) / (9550 * 0.85);

            return {
                nome: nomeCliente || "Ferramenta do Cliente",
                vcFinal,
                fFinal,
                n,
                vf,
                tempoCorteFuroSeg,
                tempoFuroSeg,
                tempoPilotoLoteMin,
                pilotoSegEfetivo,
                custoPilotoEfetivo,
                custoPilotoLote,
                canhaoAtivo,
                numParagensLote,
                tempoParagemMinVal,
                tempoParagemCanhaoLoteMin,
                tempoTotalMin,
                custoMaqFuro,
                custoMaqLote,
                forcaFf,
                binarioMc,
                potenciaReqKw
            };
        }

        function atualizarFiltroBrocas(manterSelecao = false) {
            const linhaSel = document.getElementById('linha').value;
            const categoriaSel = document.getElementById('categoria').value;
            const refrigSel = document.getElementById('filtro-refrig').value;
            const brocaSelect = document.getElementById('broca');
            const atualBroca = manterSelecao ? brocaSelect.value : null;
            
            brocaSelect.innerHTML = '';
            let primeiraChave = null;

            for (const key in dados) {
                const ferramenta = dados[key];
                const matchLinha = ferramenta.linha === linhaSel;
                const matchCat = ferramenta.categoria === categoriaSel;
                const matchRefrig = (refrigSel === 'com' && ferramenta.temRefrigInt) || (refrigSel === 'sem' && !ferramenta.temRefrigInt);

                if (matchLinha && matchCat && matchRefrig) {
                    const opt = document.createElement('option');
                    opt.value = key;
                    opt.text = ferramenta.nome;
                    brocaSelect.appendChild(opt);
                    if (!primeiraChave) primeiraChave = key;
                }
            }

            if (!primeiraChave) {
                const opt = document.createElement('option');
                opt.value = "";
                opt.text = "Nenhuma ferramenta nesta categoria";
                brocaSelect.appendChild(opt);
            } else if (atualBroca && dados[atualBroca]) {
                brocaSelect.value = atualBroca;
            }

            mudarBroca();
        }

        function mudarBroca(variantePreferida = null) {
            const brocaKey = document.getElementById('broca').value;
            const grupoSelect = document.getElementById('grupo');
            const varSelect = document.getElementById('variante-xd');
            
            if (!brocaKey || !dados[brocaKey]) return;

            const toolData = dados[brocaKey];
            const grupoAnterior = grupoSelect.value;

            grupoSelect.innerHTML = '';
            toolData.gruposList.forEach((gKey, idx) => {
                const opt = document.createElement('option');
                opt.value = gKey;
                opt.text = toolData.gruposNames[gKey];
                if ((grupoAnterior && toolData.gruposList.includes(grupoAnterior) && gKey === grupoAnterior) || ((!grupoAnterior || !toolData.gruposList.includes(grupoAnterior)) && idx === 0)) {
                    opt.selected = true;
                }
                grupoSelect.appendChild(opt);
            });

            varSelect.innerHTML = '';
            const varKeys = Object.keys(toolData.variantes || { '5xD': { ratio: 5 } });
            varKeys.forEach((vk, idx) => {
                const opt = document.createElement('option');
                opt.value = vk;
                opt.text = vk;
                if ((variantePreferida && vk === variantePreferida) || (!variantePreferida && idx === 0)) {
                    opt.selected = true;
                }
                varSelect.appendChild(opt);
            });

            const btnInt = document.getElementById('ref-int');
            const avisoRefrig = document.getElementById('aviso-refrig');
            
            if (!toolData.temRefrigInt) {
                btnInt.disabled = true;
                btnInt.className = "py-1.5 rounded bg-slate-800 text-slate-600 cursor-not-allowed";
                avisoRefrig.classList.remove('hidden');
                if (refrigAtual === 'int') {
                    setRefrig('ext');
                }
            } else {
                btnInt.disabled = false;
                avisoRefrig.classList.add('hidden');
                setRefrig('int');
            }

            mudarGrupoMaterial();
        }

        function aplicarPesquisaReferencia() {
            const raw = document.getElementById('ref-pesquisa').value.trim().toUpperCase();
            const feedback = document.getElementById('ref-feedback');
            if (!raw) {
                feedback.innerText = "Escreva uma referência (ex: SCD661 12XD).";
                feedback.className = "text-[10px] text-slate-400 block";
                return;
            }

            let encontradaKey = null;
            for (const key in dados) {
                if (raw.includes(key.toUpperCase())) {
                    encontradaKey = key;
                    break;
                }
            }

            if (!encontradaKey) {
                feedback.innerText = `Referência "${raw}" não reconhecida nas famílias carregadas.`;
                feedback.className = "text-[10px] text-amber-400 block";
                return;
            }

            const toolData = dados[encontradaKey];
            document.getElementById('linha').value = toolData.linha;
            document.getElementById('categoria').value = toolData.categoria;
            document.getElementById('filtro-refrig').value = toolData.temRefrigInt ? 'com' : 'sem';
            atualizarFiltroBrocas(true);
            document.getElementById('broca').value = encontradaKey;

            const matchXd = raw.match(/(\d+)\s*X\s*D/);
            let varianteDetetada = null;
            if (matchXd && toolData.variantes) {
                const candidata = `${matchXd[1]}xD`;
                if (toolData.variantes[candidata]) {
                    varianteDetetada = candidata;
                }
            }

            mudarBroca(varianteDetetada);

            const varFinal = document.getElementById('variante-xd').value;
            feedback.innerText = `Selecionado: ${toolData.nome} (${varFinal})`;
            feedback.className = "text-[10px] text-emerald-400 block";
        }

        function mudarGrupoMaterial() {
            const grupoKey = document.getElementById('grupo').value;
            if (grupoKey) {
                const densidadeSugerida = getDensidadePadrao(grupoKey);
                document.getElementById('densidade').value = densidadeSugerida;
            }
            atualizarCalculo();
        }

        function setRefrig(tipo) {
            const brocaKey = document.getElementById('broca').value;
            const toolData = dados[brocaKey];
            if (toolData && !toolData.temRefrigInt && tipo === 'int') return;

            refrigAtual = tipo;
            ['int', 'ext', 'mql', 'ar'].forEach(t => {
                const btn = document.getElementById(`ref-${t}`);
                if (toolData && !toolData.temRefrigInt && t === 'int') {
                    btn.disabled = true;
                    btn.className = "py-1.5 rounded bg-slate-800 text-slate-600 cursor-not-allowed";
                    return;
                } else if (t === 'int') {
                    btn.disabled = false;
                }

                if(t === tipo) {
                    btn.className = "py-1.5 rounded bg-blue-600 text-white transition";
                } else {
                    btn.className = "py-1.5 rounded text-slate-400 hover:text-white transition";
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
                    card.className = 'bg-slate-800 p-2.5 rounded-lg border border-amber-500/80 transition-colors';
                    input.className = 'w-full bg-slate-900 text-xl font-bold text-amber-300 mt-0.5 focus:outline-none rounded px-1 -ml-1 border border-amber-500/40';
                    status.innerText = 'Manual';
                    status.className = 'text-[9px] text-amber-400 font-semibold';
                    input.focus();
                } else {
                    btn.innerText = '🔒';
                    card.className = 'bg-slate-800 p-2.5 rounded-lg border border-slate-700 transition-colors';
                    input.className = 'w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1';
                    status.innerText = 'Auto';
                    status.className = 'text-[9px] text-slate-500';
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
                    card.className = 'bg-slate-800 p-2.5 rounded-lg border border-amber-500/80 transition-colors';
                    input.className = 'w-full bg-slate-900 text-xl font-bold text-amber-300 mt-0.5 focus:outline-none rounded px-1 -ml-1 border border-amber-500/40';
                    status.innerText = 'Manual';
                    status.className = 'text-[9px] text-amber-400 font-semibold';
                    input.focus();
                } else {
                    btn.innerText = '🔒';
                    card.className = 'bg-slate-800 p-2.5 rounded-lg border border-slate-700 transition-colors';
                    input.className = 'w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1';
                    status.innerText = 'Auto';
                    status.className = 'text-[9px] text-slate-500';
                    atualizarCalculo();
                }
            } else if (tipo === 'rpm-max') {
                rpmMaxUnlocked = !rpmMaxUnlocked;
                const input = document.getElementById('input-rpm-max');
                const btn = document.getElementById('btn-lock-rpm-max');
                const card = document.getElementById('card-rpm-max');
                const status = document.getElementById('status-rpm-max');
                input.readOnly = !rpmMaxUnlocked;
                if (rpmMaxUnlocked) {
                    btn.innerText = '🔓';
                    card.className = 'bg-slate-800 p-2.5 rounded-lg border border-amber-500/80 transition-colors';
                    input.className = 'w-full bg-slate-900 text-xl font-bold text-amber-300 mt-0.5 focus:outline-none rounded px-1 -ml-1 border border-amber-500/40';
                    status.innerText = 'Ativo';
                    status.className = 'text-[9px] text-amber-400 font-semibold';
                    input.focus();
                } else {
                    btn.innerText = '🔒';
                    card.className = 'bg-slate-800 p-2.5 rounded-lg border border-slate-700 transition-colors';
                    input.className = 'w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1';
                    status.innerText = 'Inativo';
                    status.className = 'text-[9px] text-slate-500';
                    atualizarCalculo();
                }
            }
        }

        function ajustarDiametro(delta) {
            const input = document.getElementById('diametro');
            let val = parseFloat(input.value) + delta;
            if (val < 0.5) val = 0.5;
            if (val > 30) val = 30;
            input.value = val.toFixed(2);
            atualizarCalculo();
        }

        function ajustarPct(tipo, delta) {
            if (tipo === 'vc') {
                vcPct = Math.max(-50, Math.min(50, vcPct + delta));
                document.getElementById('vc-slider').value = vcPct;
            } else if (tipo === 'f') {
                fPct = Math.max(-50, Math.min(50, fPct + delta));
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
            } else if (tipo === 'f') {
                fPct = 0;
                document.getElementById('f-slider').value = 0;
            }
            atualizarCalculo();
        }

        function onManualInput(tipo) {
            if ((tipo === 'vc' && vcUnlocked) || (tipo === 'f' && fUnlocked) || (tipo === 'rpm-max' && rpmMaxUnlocked)) {
                atualizarCalculo();
            }
        }

        function atualizarGauge(val, maxVal, needleId, valElId, badgeElId, unidade) {
            const needle = document.getElementById(needleId);
            const valEl = document.getElementById(valElId);
            const badgeEl = document.getElementById(badgeElId);

            valEl.innerText = val.toFixed(2) + ' ' + unidade;

            if (!maxVal || maxVal <= 0) {
                needle.style.transform = `rotate(0deg)`;
                badgeEl.innerText = 'Standby';
                badgeEl.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400';
                return;
            }

            const pct = (val / maxVal) * 100;
            const clampedPct = Math.min(Math.max(pct, 0), 100);
            const angle = -90 + (clampedPct / 100) * 180;
            needle.style.transform = `rotate(${angle}deg)`;

            if (pct < 70) {
                badgeEl.innerText = pct.toFixed(0) + '% — Confortável';
                badgeEl.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-700/50';
            } else if (pct <= 90) {
                badgeEl.innerText = pct.toFixed(0) + '% — No Limite';
                badgeEl.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-700/50';
            } else {
                badgeEl.innerText = pct.toFixed(0) + '% — Risco Stall!';
                badgeEl.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-600/80';
            }
        }

        let cacheResultados = {};
        let cacheComparacao = null;

        function lerContextoAtual() {
            const brocaKey = document.getElementById('broca').value;
            const grupoKey = document.getElementById('grupo').value;
            const varianteKey = document.getElementById('variante-xd').value || '5xD';
            const ligaCheck = document.getElementById('liga-check').checked;
            const peckingCheck = document.getElementById('pecking-check').checked;
            const toolData = dados[brocaKey];

            let grupoEfetivoKey = grupoKey;
            if (ligaCheck && toolData) {
                const idxAtual = toolData.gruposList.indexOf(grupoKey);
                if (idxAtual !== -1 && idxAtual + 1 < toolData.gruposList.length) {
                    grupoEfetivoKey = toolData.gruposList[idxAtual + 1];
                }
            }

            let diametro = parseFloat(document.getElementById('diametro').value);
            if (isNaN(diametro) || diametro <= 0) diametro = 12.00;

            let profundidade = parseFloat(document.getElementById('profundidade').value);
            if (isNaN(profundidade) || profundidade <= 0) profundidade = 140.00;

            let qtdFuros = parseInt(document.getElementById('qtd-furos').value);
            if (isNaN(qtdFuros) || qtdFuros <= 0) qtdFuros = 50;

            let densidade = parseFloat(document.getElementById('densidade').value);
            if (isNaN(densidade) || densidade <= 0) densidade = 7.85;

            let precoSucataKg = parseFloat(document.getElementById('preco-sucata').value);
            if (isNaN(precoSucataKg) || precoSucataKg < 0) precoSucataKg = 0.35;

            let custoHora = parseFloat(document.getElementById('custo-hora').value);
            if (isNaN(custoHora) || custoHora <= 0) custoHora = 50.00;

            const peckingUnid = document.getElementById('pecking-unidade').value;
            let peckingInputVal = parseFloat(document.getElementById('pecking-passo').value);
            if (isNaN(peckingInputVal) || peckingInputVal <= 0) {
                peckingInputVal = peckingUnid === 'xd' ? 3.0 : (3.0 * diametro);
            }
            const peckingRetensaoVal = parseFloat(document.getElementById('pecking-retensao').value) || 5000;
            const rpmMaxVal = parseFloat(document.getElementById('input-rpm-max').value) || 0;

            return {
                brocaKey, grupoKey, grupoEfetivoKey, varianteKey, ligaCheck, peckingCheck,
                toolData, diametro, profundidade, qtdFuros, densidade, precoSucataKg, custoHora,
                peckingUnid, peckingInputVal, peckingRetensaoVal, rpmMaxVal
            };
        }

        function atualizarCalculo() {
            const ctx = lerContextoAtual();
            if (!ctx.brocaKey || !ctx.toolData) return;

            const grupoObj = ctx.toolData.grupos[ctx.grupoEfetivoKey];
            if (!grupoObj) return;

            const baseCalc = calcularMetricasFerramenta(ctx.brocaKey, ctx.varianteKey, ctx.grupoEfetivoKey, {
                diametro: ctx.diametro,
                profundidade: ctx.profundidade,
                qtdFuros: ctx.qtdFuros,
                custoHora: ctx.custoHora,
                refrigAtual,
                vcPct,
                fPct,
                rpmMaxUnlocked,
                rpmMaxVal: ctx.rpmMaxVal,
                peckingCheck: ctx.peckingCheck,
                peckingUnid: ctx.peckingUnid,
                peckingInputVal: ctx.peckingInputVal,
                peckingRetensaoVal: ctx.peckingRetensaoVal
            });
            if (!baseCalc) return;

            const excedeNominal = ctx.profundidade > baseCalc.limiteNominalMm;
            const alertaBox = document.getElementById('alerta-profundidade');
            const textoLimite = document.getElementById('texto-limite-prof');
            const badgeLimite = document.getElementById('badge-limite-prof');

            textoLimite.innerText = `Profundidade a validar com catálogo (${ctx.varianteKey} @ Ø${ctx.diametro.toFixed(1)} | Lim. nom.: ${baseCalc.limiteNominalMm.toFixed(0)} mm)`;
            if (excedeNominal) {
                alertaBox.className = "bg-red-950/60 px-2.5 py-1.5 rounded-md border border-red-700/80 text-[10px] text-red-200 flex justify-between items-center gap-2 shrink-0";
                badgeLimite.innerText = `FORA DO LIMITE (+${(ctx.profundidade - baseCalc.limiteNominalMm).toFixed(0)} mm)`;
                badgeLimite.className = "font-bold text-red-400 shrink-0";
            } else {
                alertaBox.className = "bg-slate-900 px-2.5 py-1.5 rounded-md border border-amber-700/50 text-[10px] text-slate-200 flex justify-between items-center gap-2 shrink-0";
                badgeLimite.innerText = "VALIDAR CATÁLOGO";
                badgeLimite.className = "font-bold text-amber-400 shrink-0";
            }

            let vcFinal = baseCalc.vcFinal;
            let fFinal = baseCalc.fFinal;
            let n = baseCalc.n;
            let estadoTexto = baseCalc.estadoTexto;
            let estadoCor = baseCalc.estadoCor;

            if (!vcUnlocked) {
                document.getElementById('input-vc').value = Math.round(vcFinal);
            } else {
                vcFinal = parseFloat(document.getElementById('input-vc').value) || vcFinal;
                n = ctx.diametro > 0 ? Math.round((vcFinal * 1000) / (Math.PI * ctx.diametro)) : 0;
                if (rpmMaxUnlocked && ctx.rpmMaxVal > 0 && n > ctx.rpmMaxVal) {
                    n = ctx.rpmMaxVal;
                    vcFinal = (n * Math.PI * ctx.diametro) / 1000;
                    estadoTexto = "Limitado por RPM Máx.";
                    estadoCor = "text-amber-400";
                }
            }

            if (!fUnlocked) {
                document.getElementById('input-f').value = fFinal.toFixed(4);
            } else {
                fFinal = parseFloat(document.getElementById('input-f').value) || fFinal;
            }

            const vf = Math.round(fFinal * n);
            const cursoEfetivo = ctx.profundidade + (0.3 * ctx.diametro);
            let tempoFuroSeg = vf > 0 ? (cursoEfetivo / vf) * 60 : 0;

            let peckingStrDescricao = "Não (Direto)";
            const passoMm = ctx.peckingUnid === 'xd' ? (ctx.peckingInputVal * ctx.diametro) : ctx.peckingInputVal;
            const numPassos = Math.max(1, Math.ceil(ctx.profundidade / passoMm));

            const equivEl = document.getElementById('pecking-equiv');
            if (ctx.peckingUnid === 'xd') {
                equivEl.innerText = `Equiv: ${passoMm.toFixed(1)} mm (${numPassos} passos)`;
            } else {
                const equivXd = passoMm / ctx.diametro;
                equivEl.innerText = `Equiv: ${equivXd.toFixed(2)}×D (${numPassos} passos)`;
            }

            if (ctx.peckingCheck) {
                const passoFormatado = ctx.peckingUnid === 'xd'
                    ? `${ctx.peckingInputVal.toFixed(2)}×D (${passoMm.toFixed(1)} mm)`
                    : `${passoMm.toFixed(1)} mm (${(passoMm / ctx.diametro).toFixed(2)}×D)`;
                peckingStrDescricao = `Sim (Passo: ${passoFormatado} | ${numPassos} passos | Retração: ${ctx.peckingRetensaoVal} mm/min)`;

                const tempoCortePassos = vf > 0 ? (ctx.profundidade / vf) * 60 : 0;
                const tempoRetracaoSeg = (numPassos * (ctx.profundidade / ctx.peckingRetensaoVal)) * 60;
                const tempoEntradaSeg = vf > 0 ? ((0.3 * ctx.diametro / vf) * 60) : 0;
                tempoFuroSeg = tempoCortePassos + tempoRetracaoSeg + tempoEntradaSeg;
            }

            const raio = ctx.diametro / 2;
            const volumeMm3Furo = Math.PI * Math.pow(raio, 2) * ctx.profundidade;
            const volumeCm3Furo = volumeMm3Furo / 1000;

            const massaGramsFuro = volumeCm3Furo * ctx.densidade;
            const massaKgFuro = massaGramsFuro / 1000;
            const valorSucataFuro = massaKgFuro * ctx.precoSucataKg;

            const custoHoraSeg = ctx.custoHora / 3600;
            const custoFuro = tempoFuroSeg * custoHoraSeg;

            const tempoTotalSeg = tempoFuroSeg * ctx.qtdFuros;
            const tempoTotalMin = tempoTotalSeg / 60;
            const volumeTotalCm3 = volumeCm3Furo * ctx.qtdFuros;
            const massaTotalKg = massaKgFuro * ctx.qtdFuros;
            const valorTotalSucata = valorSucataFuro * ctx.qtdFuros;
            const custoTotalLote = custoFuro * ctx.qtdFuros;
            const metragemLinearM = (ctx.profundidade * ctx.qtdFuros) / 1000;

            const tempoMinUnit = tempoFuroSeg / 60;
            const taxaRemocao = tempoMinUnit > 0 ? volumeCm3Furo / tempoMinUnit : 0;

            const kc = getKc(ctx.grupoEfetivoKey);
            const forcaFf = 0.5 * kc * ctx.diametro * Math.pow(fFinal, 0.7);
            const forcaKgf = forcaFf / 9.81;
            const binarioMc = (kc * Math.pow(ctx.diametro, 2) * Math.pow(fFinal, 0.8)) / 8000;
            const rendimentoSpindle = 0.85;
            const potenciaReqKw = (binarioMc * n) / (9550 * rendimentoSpindle);

            const potMaxInput = parseFloat(document.getElementById('spindle-potencia').value);
            const unidPot = document.getElementById('unidade-potencia').value;
            let potMaxKw = (!isNaN(potMaxInput) && potMaxInput > 0) ? (unidPot === 'cv' ? potMaxInput * 0.7355 : potMaxInput) : null;

            const binMaxInput = parseFloat(document.getElementById('spindle-binario').value);
            let binMaxNm = (!isNaN(binMaxInput) && binMaxInput > 0) ? binMaxInput : null;

            atualizarGauge(potenciaReqKw, potMaxKw, 'needle-potencia', 'val-gauge-pot', 'badge-gauge-pot', 'kW');
            atualizarGauge(binarioMc, binMaxNm, 'needle-binario', 'val-gauge-bin', 'badge-gauge-bin', 'N·m');

            cacheResultados = {
                ferramenta: `${ctx.toolData.nome} (${ctx.varianteKey})`,
                linha: ctx.toolData.linha.toUpperCase(),
                grupo: ctx.grupoEfetivoKey,
                diametro: ctx.diametro.toFixed(2),
                profundidade: ctx.profundidade.toFixed(1),
                limiteNominalMm: baseCalc.limiteNominalMm.toFixed(0),
                estadoProfundidade: excedeNominal ? `Fora do limite nominal (+${(ctx.profundidade - baseCalc.limiteNominalMm).toFixed(0)} mm) — Validar com catálogo` : "A validar com catálogo",
                qtdFuros: ctx.qtdFuros,
                metragemLinearM: metragemLinearM.toFixed(2),
                refrig: refrigAtual.toUpperCase(),
                pecking: peckingStrDescricao,
                vc: Math.round(vcFinal),
                f: fFinal.toFixed(4),
                n,
                vf,
                tempoFuroSeg: tempoFuroSeg.toFixed(1),
                tempoTotalMin: tempoTotalMin.toFixed(1),
                volumeTotalCm3: volumeTotalCm3.toFixed(1),
                massaTotalKg: massaTotalKg.toFixed(3),
                valorTotalSucata: valorTotalSucata.toFixed(2),
                custoTotalLote: custoTotalLote.toFixed(2),
                custoFuro: custoFuro.toFixed(2),
                custoHora: ctx.custoHora.toFixed(2),
                forcaN: Math.round(forcaFf).toLocaleString(),
                forcaKgf: Math.round(forcaKgf),
                binarioNm: binarioMc.toFixed(1),
                potenciaKw: potenciaReqKw.toFixed(2)
            };

            document.getElementById('res-n').innerText = n;
            document.getElementById('res-vf').innerText = vf;
            document.getElementById('res-tempo-total').innerHTML = tempoTotalMin.toFixed(1) + ' min <span class="text-xs font-normal text-slate-300">(' + tempoFuroSeg.toFixed(1) + ' seg/furo)</span>';
            document.getElementById('res-metragem').innerText = metragemLinearM.toFixed(2) + ' metros';
            document.getElementById('res-volume-total').innerHTML = volumeTotalCm3.toFixed(1) + ' cm³ <span class="text-xs font-normal text-slate-300">(' + volumeCm3Furo.toFixed(1) + ' cm³/furo)</span>';
            document.getElementById('res-taxa').innerText = taxaRemocao.toFixed(1) + ' cm³/min';
            document.getElementById('res-peso').innerHTML = massaTotalKg < 1 ? (massaTotalKg * 1000).toFixed(1) + ' <span class="text-sm font-normal text-slate-300">g</span>' : massaTotalKg.toFixed(3) + ' <span class="text-sm font-normal text-slate-300">kg</span>';
            document.getElementById('res-peso-g').innerText = massaGramsFuro.toFixed(1) + ' g/furo';
            document.getElementById('res-sucata-val').innerHTML = valorTotalSucata.toFixed(2) + ' <span class="text-sm font-normal text-slate-300">€</span>';
            document.getElementById('res-sucata-furo').innerText = valorSucataFuro.toFixed(3) + ' € / furo';
            document.getElementById('res-custo-total').innerHTML = custoTotalLote.toFixed(2) + ' € <span class="text-[10px] font-normal text-slate-300">(' + custoFuro.toFixed(2) + ' €/furo)</span>';
            document.getElementById('res-custo-hora-ref').innerText = ctx.custoHora.toFixed(2) + ' €/h';
            document.getElementById('res-forca').innerHTML = Math.round(forcaFf).toLocaleString() + ' <span class="text-sm font-normal text-slate-300">N</span>';
            document.getElementById('res-forca-kgf').innerText = Math.round(forcaKgf) + ' kgf';
            document.getElementById('res-binario-card').innerHTML = binarioMc.toFixed(1) + ' <span class="text-sm font-normal text-slate-300">N·m</span>';

            const elEstado = document.getElementById('val-estado');
            elEstado.innerText = estadoTexto;
            elEstado.className = "text-[9px] font-bold " + estadoCor;
            document.getElementById('badge-metodo').innerText = baseCalc.badgeMetodo;

            document.getElementById('vc-pct-val').innerText = (vcPct > 0 ? "+" : "") + vcPct + "%";
            document.getElementById('f-pct-val').innerText = (fPct > 0 ? "+" : "") + fPct + "%";

            const diametrosCat = ctx.toolData.diametros;
            const fCatArr = grupoObj.f;
            const tbody = document.getElementById('tabela-ref');
            tbody.innerHTML = '';
            for (let i = 0; i < diametrosCat.length; i++) {
                const dCat = diametrosCat[i];
                const fCat = fCatArr[i];
                let nCat = Math.round((vcFinal * 1000) / (Math.PI * dCat));
                if (rpmMaxUnlocked && ctx.rpmMaxVal > 0 && nCat > ctx.rpmMaxVal) nCat = ctx.rpmMaxVal;
                const vfCat = Math.round(fCat * nCat);
                const tr = document.createElement('tr');
                tr.className = i === baseCalc.idxInf || i === baseCalc.idxInf + 1 ? "bg-blue-900/30 font-medium text-white" : "text-slate-300";
                tr.innerHTML = `
                    <td class="py-1">${dCat.toFixed(2)}</td>
                    <td class="py-1">${fCat.toFixed(2)}</td>
                    <td class="py-1">${nCat}</td>
                    <td class="py-1">${vfCat}</td>
                `;
                tbody.appendChild(tr);
            }

            desenharGrafico(diametrosCat, fCatArr, ctx.diametro, fFinal);

            if (!document.getElementById('modal-resultado-comparacao').classList.contains('hidden')) {
                atualizarComparacao();
            }
        }

        function abrirModalComparacao() {
            const ctx = lerContextoAtual();
            if (!ctx.brocaKey) return;

            document.getElementById('comp-custo-hora').value = ctx.custoHora.toFixed(2);
            atualizarEstadoBotaoInterrompido();

            const selFerramenta = document.getElementById('comp-ferramenta');
            const anterior = selFerramenta.value;
            selFerramenta.innerHTML = '';

            const optCliente = document.createElement('option');
            optCliente.value = "__CLIENTE__";
            optCliente.text = "🛠️ Ferramenta do Cliente (Inserir Vc e f)";
            selFerramenta.appendChild(optCliente);

            const keys = Object.keys(dados);
            keys.forEach(k => {
                const opt = document.createElement('option');
                opt.value = k;
                const linhaLabel = dados[k].linha.toUpperCase();
                opt.text = `${dados[k].nome} [${linhaLabel}]`;
                selFerramenta.appendChild(opt);
            });

            if (anterior && (anterior === "__CLIENTE__" || (dados[anterior] && anterior !== ctx.brocaKey))) {
                selFerramenta.value = anterior;
            } else {
                const outra = keys.find(k => k !== ctx.brocaKey);
                if (outra) selFerramenta.value = outra;
            }

            document.getElementById('modal-resultado-comparacao').classList.add('hidden');
            onChangeFonteComparacao();
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function fecharModalComparacao() {
            document.getElementById('modal-comparacao').classList.add('hidden');
        }

        function abrirJanelaResultadoComparacao() {
            atualizarComparacao();
            const incluirFlag = document.getElementById('comp-incluir-pdf').checked;
            document.getElementById('comp-incluir-pdf-res').checked = incluirFlag;
            document.getElementById('modal-comparacao').classList.add('hidden');
            document.getElementById('modal-resultado-comparacao').classList.remove('hidden');
        }

        function voltarParaInputsComparacao() {
            const incluirFlag = document.getElementById('comp-incluir-pdf-res').checked;
            document.getElementById('comp-incluir-pdf').checked = incluirFlag;
            document.getElementById('modal-resultado-comparacao').classList.add('hidden');
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function fecharJanelaResultadoComparacao() {
            const incluirFlag = document.getElementById('comp-incluir-pdf-res').checked;
            document.getElementById('comp-incluir-pdf').checked = incluirFlag;
            document.getElementById('modal-resultado-comparacao').classList.add('hidden');
        }

        function sincronizarCustoHoraComparacao() {
            const valHora = parseFloat(document.getElementById('comp-custo-hora').value);
            if (!isNaN(valHora) && valHora > 0) {
                document.getElementById('custo-hora').value = valHora.toFixed(2);
                atualizarCalculo();
            } else {
                atualizarComparacao();
            }
        }

        function onChangeFonteComparacao() {
            const compKey = document.getElementById('comp-ferramenta').value;
            const blocoVar = document.getElementById('comp-bloco-variante');
            const blocoCli = document.getElementById('comp-bloco-cliente');
            const btnUsar = document.getElementById('btn-usar-comparada');

            if (compKey === "__CLIENTE__") {
                blocoVar.classList.add('hidden');
                blocoCli.classList.remove('hidden');
                btnUsar.classList.add('hidden');
                atualizarComparacao();
            } else {
                blocoVar.classList.remove('hidden');
                blocoCli.classList.add('hidden');
                btnUsar.classList.remove('hidden');
                popularVariantesComparacao();
            }
        }

        function popularVariantesComparacao() {
            const compKey = document.getElementById('comp-ferramenta').value;
            const selVar = document.getElementById('comp-variante');
            const varAtual = document.getElementById('variante-xd').value;
            selVar.innerHTML = '';

            if (!compKey || compKey === "__CLIENTE__" || !dados[compKey]) return;
            const vars = Object.keys(dados[compKey].variantes || { '5xD': { ratio: 5 } });
            vars.forEach((v, idx) => {
                const opt = document.createElement('option');
                opt.value = v;
                opt.text = v;
                if ((varAtual && v === varAtual) || (!varAtual && idx === 0)) {
                    opt.selected = true;
                }
                selVar.appendChild(opt);
            });
            atualizarComparacao();
        }

        function calcularEconomiaFerramenta(precoBroca, vidaPorCicloVal, vidaUnid, qtdReaf, custoReaf, profundidadeMm, qtdFuros, custoAdicionalFuro = 0) {
            const preco = isNaN(precoBroca) || precoBroca < 0 ? 0 : precoBroca;
            const vidaCiclo = isNaN(vidaPorCicloVal) || vidaPorCicloVal <= 0 ? 1 : vidaPorCicloVal;
            const numReaf = Math.max(0, Math.floor(isNaN(qtdReaf) ? 0 : qtdReaf));
            const custoAf = isNaN(custoReaf) || custoReaf < 0 ? 0 : custoReaf;
            const custoExtraFuro = isNaN(custoAdicionalFuro) || custoAdicionalFuro < 0 ? 0 : custoAdicionalFuro;

            const furosPorCiclo = vidaUnid === 'metros'
                ? Math.max(0.01, (vidaCiclo * 1000) / Math.max(0.1, profundidadeMm))
                : vidaCiclo;

            const ciclosPorFerramenta = 1 + numReaf;
            const furosTotaisPorFerramenta = furosPorCiclo * ciclosPorFerramenta;
            const custoTotalPorFerramenta = preco + (numReaf * custoAf);

            const custoFerramentaPorFuro = (custoTotalPorFerramenta / furosTotaisPorFerramenta) + custoExtraFuro;
            const fracaoFerramentaLote = qtdFuros / furosTotaisPorFerramenta;
            const custoFerramentaLote = (fracaoFerramentaLote * custoTotalPorFerramenta) + (custoExtraFuro * qtdFuros);

            return {
                furosPorCiclo,
                ciclosPorFerramenta,
                furosTotaisPorFerramenta,
                custoTotalPorFerramenta,
                custoFerramentaPorFuro,
                fracaoFerramentaLote,
                custoFerramentaLote
            };
        }

        function atualizarComparacao() {
            const ctx = lerContextoAtual();
            if (!ctx.brocaKey || !ctx.toolData) return;

            const metrosContinuoInput = parseFloat(document.getElementById('comp-metros-continuo').value);
            const metrosContinuo = (!isNaN(metrosContinuoInput) && metrosContinuoInput > 0) ? metrosContinuoInput : 90;
            const furosEquivContinuo = Math.max(1, Math.round((metrosContinuo * 1000) / Math.max(0.1, ctx.profundidade)));
            const resumoContinuoStr = `${metrosContinuo} m (~${furosEquivContinuo} furos a ${ctx.profundidade.toFixed(1)} mm)`;
            document.getElementById('comp-equiv-continuo').innerText = `(~${furosEquivContinuo} furos)`;

            const compKey = document.getElementById('comp-ferramenta').value;
            const avisoEl = document.getElementById('comp-aviso-grupo');
            const tbody = document.getElementById('comp-tabela-corpo');

            const custoHoraCompInput = parseFloat(document.getElementById('comp-custo-hora').value);
            const custoHoraEfetivo = (!isNaN(custoHoraCompInput) && custoHoraCompInput > 0) ? custoHoraCompInput : ctx.custoHora;

            const mAtual = calcularMetricasFerramenta(ctx.brocaKey, ctx.varianteKey, ctx.grupoEfetivoKey, {
                diametro: ctx.diametro, profundidade: ctx.profundidade, qtdFuros: ctx.qtdFuros,
                custoHora: custoHoraEfetivo, refrigAtual, vcPct, fPct, rpmMaxUnlocked,
                rpmMaxVal: ctx.rpmMaxVal, peckingCheck: ctx.peckingCheck,
                peckingUnid: ctx.peckingUnid, peckingInputVal: ctx.peckingInputVal,
                peckingRetensaoVal: ctx.peckingRetensaoVal
            });
            if (!mAtual) return;

            const tituloAtualStr = `${ctx.toolData.nome} (${ctx.varianteKey})`;
            document.getElementById('comp-th-atual').innerText = tituloAtualStr;

            const precoAtual = parseFloat(document.getElementById('comp-preco-atual').value) || 0;
            const vidaAtual = parseFloat(document.getElementById('comp-vida-atual').value) || 1;
            const vidaUnidAtual = document.getElementById('comp-vida-unid-atual').value;
            const afiQtdAtual = parseInt(document.getElementById('comp-afi-qtd-atual').value) || 0;
            const afiCustoAtual = parseFloat(document.getElementById('comp-afi-custo-atual').value) || 0;

            const precoAlvo = parseFloat(document.getElementById('comp-preco-alvo').value) || 0;
            const vidaAlvo = parseFloat(document.getElementById('comp-vida-alvo').value) || 1;
            const vidaUnidAlvo = document.getElementById('comp-vida-unid-alvo').value;
            const afiQtdAlvo = parseInt(document.getElementById('comp-afi-qtd-alvo').value) || 0;
            const afiCustoAlvo = parseFloat(document.getElementById('comp-afi-custo-alvo').value) || 0;

            let mComp = null;
            let tituloComp = '';
            let grupoComparacao = ctx.grupoEfetivoKey;
            let requerPilotoAtivo = false;
            let tempoPilotoSegVal = 0;
            let custoPilotoFuroVal = 0;
            let usaBrocaCanhaoAtivo = false;
            let tempoParagemAfiMinVal = 0;
            let furosPorAfiaçãoAlvo = vidaAlvo;

            if (compKey === "__CLIENTE__") {
                const nomeCli = document.getElementById('comp-cliente-nome').value.trim() || "Ferramenta do Cliente";
                const vcCli = parseFloat(document.getElementById('comp-cliente-vc').value);
                const fCli = parseFloat(document.getElementById('comp-cliente-f').value);
                requerPilotoAtivo = document.getElementById('comp-requer-piloto').checked;
                tempoPilotoSegVal = requerPilotoAtivo ? (parseFloat(document.getElementById('comp-tempo-piloto-seg').value) || 0) : 0;
                custoPilotoFuroVal = requerPilotoAtivo ? (parseFloat(document.getElementById('comp-custo-piloto-furo').value) || 0) : 0;

                usaBrocaCanhaoAtivo = requerPilotoAtivo && document.getElementById('comp-usa-broca-canhao').checked;
                tempoParagemAfiMinVal = usaBrocaCanhaoAtivo ? (parseFloat(document.getElementById('comp-tempo-paragem-afi-min').value) || 0) : 0;

                const ePrevia = calcularEconomiaFerramenta(precoAlvo, vidaAlvo, vidaUnidAlvo, afiQtdAlvo, afiCustoAlvo, ctx.profundidade, ctx.qtdFuros, custoPilotoFuroVal);
                furosPorAfiaçãoAlvo = ePrevia.furosPorCiclo;

                const sufixos = [];
                if (requerPilotoAtivo) sufixos.push("Piloto");
                if (usaBrocaCanhaoAtivo) sufixos.push("Canhão");
                tituloComp = `${nomeCli} (Manual${sufixos.length ? ' + ' + sufixos.join(' + ') : ''})`;
                document.getElementById('comp-th-alvo').innerText = tituloComp;
                avisoEl.classList.add('hidden');

                mComp = calcularMetricasManualCliente(nomeCli, vcCli, fCli, ctx.grupoEfetivoKey, {
                    diametro: ctx.diametro, profundidade: ctx.profundidade, qtdFuros: ctx.qtdFuros,
                    custoHora: custoHoraEfetivo, rpmMaxUnlocked, rpmMaxVal: ctx.rpmMaxVal,
                    peckingCheck: ctx.peckingCheck, peckingUnid: ctx.peckingUnid,
                    peckingInputVal: ctx.peckingInputVal, peckingRetensaoVal: ctx.peckingRetensaoVal,
                    requerPiloto: requerPilotoAtivo, tempoPilotoSeg: tempoPilotoSegVal, custoPilotoFuro: custoPilotoFuroVal,
                    usaBrocaCanhao: usaBrocaCanhaoAtivo, tempoParagemAfiMin: tempoParagemAfiMinVal,
                    furosPorAfiação: furosPorAfiaçãoAlvo
                });

                const canhaoResumoEl = document.getElementById('comp-canhao-resumo');
                if (canhaoResumoEl) {
                    if (usaBrocaCanhaoAtivo) {
                        const custoParagensEur = (mComp.tempoParagemCanhaoLoteMin / 60) * custoHoraEfetivo;
                        canhaoResumoEl.innerText = `${mComp.numParagensLote} paragens (cada ~${furosPorAfiaçãoAlvo.toFixed(0)} furos) · +${mComp.tempoParagemCanhaoLoteMin.toFixed(0)} min (+${custoParagensEur.toFixed(2)} €)`;
                    } else {
                        canhaoResumoEl.innerText = "0 paragens · +0.0 min";
                    }
                }
            } else {
                const compVar = document.getElementById('comp-variante').value || '5xD';
                const compTool = dados[compKey];
                tituloComp = compTool ? `${compTool.nome} (${compVar})` : 'Ferramenta Comparada';
                document.getElementById('comp-th-alvo').innerText = tituloComp;
                if (!compTool) return;

                let mensagemAviso = '';
                if (!compTool.grupos[grupoComparacao]) {
                    const prefixo = ctx.grupoEfetivoKey.charAt(0);
                    const mesmoPrefixo = compTool.gruposList.find(g => g.startsWith(prefixo));
                    if (mesmoPrefixo) {
                        grupoComparacao = mesmoPrefixo;
                        mensagemAviso = `Nota: O grupo ${ctx.grupoEfetivoKey} não consta nesta família; comparação feita com ${grupoComparacao}.`;
                    } else if (compTool.gruposList.length > 0) {
                        grupoComparacao = compTool.gruposList[0];
                        mensagemAviso = `Nota: O grupo ${ctx.grupoEfetivoKey} não é coberto por esta ferramenta; comparação feita com o 1.º grupo disponível (${grupoComparacao}).`;
                    }
                }

                if (mensagemAviso) {
                    avisoEl.innerText = mensagemAviso;
                    avisoEl.classList.remove('hidden');
                } else {
                    avisoEl.classList.add('hidden');
                }

                mComp = calcularMetricasFerramenta(compKey, compVar, grupoComparacao, {
                    diametro: ctx.diametro, profundidade: ctx.profundidade, qtdFuros: ctx.qtdFuros,
                    custoHora: custoHoraEfetivo, refrigAtual, vcPct, fPct, rpmMaxUnlocked,
                    rpmMaxVal: ctx.rpmMaxVal, peckingCheck: ctx.peckingCheck,
                    peckingUnid: ctx.peckingUnid, peckingInputVal: ctx.peckingInputVal,
                    peckingRetensaoVal: ctx.peckingRetensaoVal
                });
            }

            if (!mComp) return;

            const eAtual = calcularEconomiaFerramenta(precoAtual, vidaAtual, vidaUnidAtual, afiQtdAtual, afiCustoAtual, ctx.profundidade, ctx.qtdFuros, 0);
            const eComp = calcularEconomiaFerramenta(precoAlvo, vidaAlvo, vidaUnidAlvo, afiQtdAlvo, afiCustoAlvo, ctx.profundidade, ctx.qtdFuros, custoPilotoFuroVal);

            const custoTotalFuroAtual = mAtual.custoMaqFuro + eAtual.custoFerramentaPorFuro;
            const custoTotalFuroComp = mComp.custoMaqFuro + eComp.custoFerramentaPorFuro;

            const custoTotalLoteAtual = mAtual.custoMaqLote + eAtual.custoFerramentaLote;
            const custoTotalLoteComp = mComp.custoMaqLote + eComp.custoFerramentaLote;

            const diffTempoFuro = mAtual.tempoFuroSeg - mComp.tempoFuroSeg;
            const pctTempo = mComp.tempoFuroSeg > 0 ? ((mComp.tempoFuroSeg - mAtual.tempoFuroSeg) / mComp.tempoFuroSeg) * 100 : 0;
            const diffCustoFuro = custoTotalFuroAtual - custoTotalFuroComp;
            const diffCustoLote = custoTotalLoteAtual - custoTotalLoteComp;

            document.getElementById('res-comp-subtitulo').innerText =
                `${tituloAtualStr} vs. ${tituloComp} · Grupo ${ctx.grupoEfetivoKey} · Ø${ctx.diametro.toFixed(1)} mm · L=${ctx.profundidade.toFixed(0)} mm · Lote ${ctx.qtdFuros} furos${corteInterrompidoAtivo ? ' · Corte Interrompido' : ''}`;

            const capEl = document.getElementById('comp-capacidade-texto');
            const beEl = document.getElementById('comp-breakeven-texto');
            const destEl = document.getElementById('comp-resumo-lote-destaque');

            if (mAtual.tempoFuroSeg < mComp.tempoFuroSeg) {
                const ganhoPct = Math.abs(pctTempo).toFixed(1);
                const minGanhos = Math.abs(mComp.tempoTotalMin - mAtual.tempoTotalMin).toFixed(1);
                capEl.innerHTML = `<span class="text-emerald-400 font-bold">MAPAL é ${ganhoPct}% mais rápido</span> (${Math.abs(diffTempoFuro).toFixed(1)} seg/furo menos · <strong>-${minGanhos} min</strong> no lote).`;
            } else if (mAtual.tempoFuroSeg > mComp.tempoFuroSeg) {
                capEl.innerHTML = `<span class="text-amber-300 font-bold">Comparada é ${Math.abs(pctTempo).toFixed(1)}% mais rápida</span> (${Math.abs(diffTempoFuro).toFixed(1)} seg/furo a mais na MAPAL).`;
            } else {
                capEl.innerHTML = `<span class="text-slate-300 font-bold">Tempos equivalentes</span> por furo.`;
            }

            const custoFixoFuroAtual = mAtual.custoMaqFuro;
            const custoVarFuroAtual = eAtual.custoFerramentaPorFuro;
            const custoFixoFuroComp = mComp.custoMaqFuro;
            const custoVarFuroComp = eComp.custoFerramentaPorFuro;

            const slopeAtual = custoFixoFuroAtual + custoVarFuroAtual;
            const slopeComp = custoFixoFuroComp + custoVarFuroComp;
            const custoInicialAtual = eAtual.custoTotalPorFerramenta;
            const custoInicialComp = eComp.custoTotalPorFerramenta;

            let pontoEquilibrioFuros = null;
            if (Math.abs(slopeAtual - slopeComp) > 0.00001) {
                const nBe = (custoInicialAtual - custoInicialComp) / (slopeComp - slopeAtual);
                if (nBe > 0 && isFinite(nBe)) {
                    pontoEquilibrioFuros = nBe;
                    beEl.innerHTML = `Custo acumulado iguala-se aos <span class="text-amber-300 font-bold">${Math.ceil(nBe).toLocaleString()} furos</span> (${((Math.ceil(nBe) * ctx.profundidade) / 1000).toFixed(1)} m).`;
                } else if (diffCustoFuro < 0) {
                    beEl.innerHTML = `<span class="text-emerald-400 font-bold">Vantagem imediata desde o 1.º furo</span> (menor custo unitário e menor investimento inicial).`;
                } else {
                    beEl.innerHTML = `<span class="text-rose-400 font-bold">Sem cruzamento favorável</span> no horizonte analisado.`;
                }
            } else {
                beEl.innerHTML = `Custos unitários idênticos (sem ponto de equilíbrio distinto).`;
            }

            if (diffCustoLote > 0.005) {
                destEl.innerHTML = `<span class="text-rose-400 font-bold">Custo adicional de +${diffCustoLote.toFixed(2)} €</span> no lote com a MAPAL (${custoTotalLoteAtual.toFixed(2)} € vs. ${custoTotalLoteComp.toFixed(2)} €).`;
            } else if (diffCustoLote < -0.005) {
                destEl.innerHTML = `<span class="text-emerald-400 font-bold">Poupança de ${Math.abs(diffCustoLote).toFixed(2)} €</span> no lote com a MAPAL (${custoTotalLoteAtual.toFixed(2)} € vs. ${custoTotalLoteComp.toFixed(2)} €).`;
            } else {
                destEl.innerHTML = `<span class="text-slate-300 font-bold">Custo total equivalente</span> no lote (${custoTotalLoteAtual.toFixed(2)} €).`;
            }

            function formatDiff(val, sufixo = '', inverterCor = false) {
                if (Math.abs(val) < 0.0005) return `<span class="text-slate-400">0${sufixo}</span>`;
                const maior = val > 0;
                const favoravel = inverterCor ? !maior : maior;
                const cor = favoravel ? 'text-emerald-400' : 'text-rose-400';
                const sinal = maior ? '+' : '';
                return `<span class="${cor} font-semibold">${sinal}${val.toFixed(sufixo === ' €' ? 2 : 1)}${sufixo}</span>`;
            }

            const vidaFmtAtual = `${vidaAtual} ${vidaUnidAtual} × ${eAtual.ciclosPorFerramenta} ciclo(s) = ${eAtual.furosTotaisPorFerramenta.toFixed(0)} furos`;
            const vidaFmtComp = `${vidaAlvo} ${vidaUnidAlvo} × ${eComp.ciclosPorFerramenta} ciclo(s) = ${eComp.furosTotaisPorFerramenta.toFixed(0)} furos`;

            const linhas = [
                {
                    label: 'Velocidade de Corte (Vc)',
                    a: `${Math.round(mAtual.vcFinal)} m/min`,
                    b: `${Math.round(mComp.vcFinal)} m/min`,
                    d: formatDiff(mAtual.vcFinal - mComp.vcFinal, ' m/min', false)
                },
                {
                    label: 'Avanço (f)',
                    a: `${mAtual.fFinal.toFixed(4)} mm/rot`,
                    b: `${mComp.fFinal.toFixed(4)} mm/rot`,
                    d: formatDiff(mAtual.fFinal - mComp.fFinal, '', false)
                },
                {
                    label: 'Rotações (n) / Avanço (vf)',
                    a: `${mAtual.n} rpm / ${mAtual.vf} mm/min`,
                    b: `${mComp.n} rpm / ${mComp.vf} mm/min`,
                    d: formatDiff(mAtual.vf - mComp.vf, ' mm/min', false)
                },
                {
                    label: 'Furo-Piloto Prévio',
                    a: 'Não requerido',
                    b: requerPilotoAtivo ? `Sim (+${tempoPilotoSegVal.toFixed(0)} s/furo | +${custoPilotoFuroVal.toFixed(2)} €/furo)` : 'Não requerido',
                    d: requerPilotoAtivo ? `<span class="text-emerald-400 font-semibold">-${tempoPilotoSegVal.toFixed(0)} s/furo na MAPAL</span>` : `<span class="text-slate-400">Igual</span>`
                },
                {
                    label: 'Paragem Máquina p/ Afiar (Canhão)',
                    a: '0 paragens (ferramenta gémea)',
                    b: usaBrocaCanhaoAtivo ? `${mComp.numParagensLote} paragens × ${tempoParagemAfiMinVal.toFixed(0)} min = +${mComp.tempoParagemCanhaoLoteMin.toFixed(0)} min` : 'Sem paragem extra',
                    d: usaBrocaCanhaoAtivo ? `<span class="text-emerald-400 font-semibold">-${mComp.tempoParagemCanhaoLoteMin.toFixed(0)} min no lote</span>` : `<span class="text-slate-400">Igual</span>`
                },
                {
                    label: 'Tempo por Furo (Efetivo)',
                    a: `${mAtual.tempoFuroSeg.toFixed(1)} seg`,
                    b: `${mComp.tempoFuroSeg.toFixed(1)} seg`,
                    d: formatDiff(mAtual.tempoFuroSeg - mComp.tempoFuroSeg, ' seg', true)
                },
                {
                    label: `Tempo Total do Lote (${ctx.qtdFuros} furos)`,
                    a: `${mAtual.tempoTotalMin.toFixed(1)} min`,
                    b: `${mComp.tempoTotalMin.toFixed(1)} min`,
                    d: formatDiff(mAtual.tempoTotalMin - mComp.tempoTotalMin, ' min', true)
                },
                {
                    label: 'Vida Útil Total c/ Reafiações',
                    a: vidaFmtAtual,
                    b: vidaFmtComp,
                    d: `<span class="text-slate-400">${eAtual.furosTotaisPorFerramenta.toFixed(0)} vs ${eComp.furosTotaisPorFerramenta.toFixed(0)} furos</span>`
                },
                {
                    label: 'Custo Ferramenta + Reaf. / Furo',
                    a: `${eAtual.custoFerramentaPorFuro.toFixed(3)} €`,
                    b: `${eComp.custoFerramentaPorFuro.toFixed(3)} €`,
                    d: formatDiff(eAtual.custoFerramentaPorFuro - eComp.custoFerramentaPorFuro, ' €', true)
                },
                {
                    label: 'Custo Máquina / Furo',
                    a: `${mAtual.custoMaqFuro.toFixed(3)} €`,
                    b: `${mComp.custoMaqFuro.toFixed(3)} €`,
                    d: formatDiff(mAtual.custoMaqFuro - mComp.custoMaqFuro, ' €', true)
                },
                {
                    label: 'Custo Total / Furo (Máq. + Ferr.)',
                    a: `${custoTotalFuroAtual.toFixed(3)} €`,
                    b: `${custoTotalFuroComp.toFixed(3)} €`,
                    d: formatDiff(diffCustoFuro, ' €', true)
                },
                {
                    label: `Custo Total do Lote (${ctx.qtdFuros} furos)`,
                    a: `${custoTotalLoteAtual.toFixed(2)} €`,
                    b: `${custoTotalLoteComp.toFixed(2)} €`,
                    d: formatDiff(diffCustoLote, ' €', true)
                }
            ];

            tbody.innerHTML = '';
            linhas.forEach(l => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/60';
                tr.innerHTML = `
                    <td class="py-2 px-3 font-medium text-slate-200">${l.label}</td>
                    <td class="py-2 px-3 text-slate-300">${l.a}</td>
                    <td class="py-2 px-3 text-slate-300">${l.b}</td>
                    <td class="py-2 px-3">${l.d}</td>
                `;
                tbody.appendChild(tr);
            });

            desenharGraficosComparacao({
                custoMaqAtual: mAtual.custoMaqLote,
                custoFerrAtual: eAtual.custoFerramentaLote,
                custoMaqComp: mComp.custoMaqLote,
                custoFerrComp: eComp.custoFerramentaLote,
                tempoCorteAtual: mAtual.tempoTotalMin,
                tempoExtrasAtual: 0,
                tempoCorteComp: Math.max(0, mComp.tempoTotalMin - (mComp.tempoPilotoLoteMin || 0) - (mComp.tempoParagemCanhaoLoteMin || 0)),
                tempoExtrasComp: (mComp.tempoPilotoLoteMin || 0) + (mComp.tempoParagemCanhaoLoteMin || 0),
                qtdFuros: ctx.qtdFuros,
                custoInicialAtual,
                custoInicialComp,
                slopeAtual,
                slopeComp
            });

            cacheComparacao = {
                tituloAtual: tituloAtualStr,
                tituloComp,
                grupo: ctx.grupoEfetivoKey,
                corteInterrompido: corteInterrompidoAtivo,
                refContinuo: corteInterrompidoAtivo ? resumoContinuoStr : 'N/A',
                custoHora: custoHoraEfetivo.toFixed(2),
                requerPiloto: requerPilotoAtivo,
                tempoPilotoSeg: tempoPilotoSegVal.toFixed(0),
                custoPilotoFuro: custoPilotoFuroVal.toFixed(2),
                usaBrocaCanhao: usaBrocaCanhaoAtivo,
                numParagensCanhao: mComp.numParagensLote || 0,
                tempoParagemCanhaoMin: (mComp.tempoParagemCanhaoLoteMin || 0).toFixed(1),
                vcAtual: Math.round(mAtual.vcFinal),
                vcComp: Math.round(mComp.vcFinal),
                fAtual: mAtual.fFinal.toFixed(4),
                fComp: mComp.fFinal.toFixed(4),
                tempoFuroAtual: mAtual.tempoFuroSeg.toFixed(1),
                tempoFuroComp: mComp.tempoFuroSeg.toFixed(1),
                tempoLoteAtual: mAtual.tempoTotalMin.toFixed(1),
                tempoLoteComp: mComp.tempoTotalMin.toFixed(1),
                vidaTotalAtual: `${eAtual.furosTotaisPorFerramenta.toFixed(0)} furos (${eAtual.ciclosPorFerramenta} ciclo(s))`,
                vidaTotalComp: `${eComp.furosTotaisPorFerramenta.toFixed(0)} furos (${eComp.ciclosPorFerramenta} ciclo(s))`,
                custoFerrFuroAtual: eAtual.custoFerramentaPorFuro.toFixed(3),
                custoFerrFuroComp: eComp.custoFerramentaPorFuro.toFixed(3),
                custoTotalFuroAtual: custoTotalFuroAtual.toFixed(3),
                custoTotalFuroComp: custoTotalFuroComp.toFixed(3),
                custoTotalLoteAtual: custoTotalLoteAtual.toFixed(2),
                custoTotalLoteComp: custoTotalLoteComp.toFixed(2),
                diffCustoLote: diffCustoLote.toFixed(2),
                pontoEquilibrio: pontoEquilibrioFuros ? `${Math.ceil(pontoEquilibrioFuros)} furos` : 'N/A'
            };
        }

        function desenharGraficosComparacao(data) {
            const svgCusto = document.getElementById('svg-comp-custo');
            const svgTempo = document.getElementById('svg-comp-tempo');
            const svgBe = document.getElementById('svg-comp-breakeven');

            const totAtualCusto = data.custoMaqAtual + data.custoFerrAtual;
            const totCompCusto = data.custoMaqComp + data.custoFerrComp;
            const maxCusto = Math.max(totAtualCusto, totCompCusto, 1) * 1.15;

            const hAtualMaq = (data.custoMaqAtual / maxCusto) * 95;
            const hAtualFerr = (data.custoFerrAtual / maxCusto) * 95;
            const hCompMaq = (data.custoMaqComp / maxCusto) * 95;
            const hCompFerr = (data.custoFerrComp / maxCusto) * 95;

            svgCusto.innerHTML = `
                <line x1="35" y1="135" x2="275" y2="135" stroke="#334155" stroke-width="1.5" />
                <rect x="65" y="${135 - hAtualMaq}" width="55" height="${hAtualMaq}" fill="#3b82f6" rx="3" />
                <rect x="65" y="${135 - hAtualMaq - hAtualFerr}" width="55" height="${hAtualFerr}" fill="#93c5fd" rx="2" />
                <text x="92.5" y="${Math.max(14, 130 - hAtualMaq - hAtualFerr)}" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="bold">${totAtualCusto.toFixed(0)}€</text>
                <text x="92.5" y="150" text-anchor="middle" fill="#94a3b8" font-size="9">MAPAL</text>

                <rect x="175" y="${135 - hCompMaq}" width="55" height="${hCompMaq}" fill="#f43f5e" rx="3" />
                <rect x="175" y="${135 - hCompMaq - hCompFerr}" width="55" height="${hCompFerr}" fill="#fda4af" rx="2" />
                <text x="202.5" y="${Math.max(14, 130 - hCompMaq - hCompFerr)}" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="bold">${totCompCusto.toFixed(0)}€</text>
                <text x="202.5" y="150" text-anchor="middle" fill="#94a3b8" font-size="9">Comparada</text>
                <text x="150" y="166" text-anchor="middle" fill="#64748b" font-size="8">Base escura: Máquina | Topo claro: Ferramenta</text>
            `;

            const totAtualTempo = data.tempoCorteAtual + data.tempoExtrasAtual;
            const totCompTempo = data.tempoCorteComp + data.tempoExtrasComp;
            const maxTempo = Math.max(totAtualTempo, totCompTempo, 1) * 1.15;

            const tAtualCorte = (data.tempoCorteAtual / maxTempo) * 95;
            const tCompCorte = (data.tempoCorteComp / maxTempo) * 95;
            const tCompExtras = (data.tempoExtrasComp / maxTempo) * 95;

            svgTempo.innerHTML = `
                <line x1="35" y1="135" x2="275" y2="135" stroke="#334155" stroke-width="1.5" />
                <rect x="65" y="${135 - tAtualCorte}" width="55" height="${tAtualCorte}" fill="#10b981" rx="3" />
                <text x="92.5" y="${Math.max(14, 130 - tAtualCorte)}" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="bold">${totAtualTempo.toFixed(1)}m</text>
                <text x="92.5" y="150" text-anchor="middle" fill="#94a3b8" font-size="9">MAPAL</text>

                <rect x="175" y="${135 - tCompCorte}" width="55" height="${tCompCorte}" fill="#f59e0b" rx="3" />
                <rect x="175" y="${135 - tCompCorte - tCompExtras}" width="55" height="${tCompExtras}" fill="#ef4444" rx="2" />
                <text x="202.5" y="${Math.max(14, 130 - tCompCorte - tCompExtras)}" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="bold">${totCompTempo.toFixed(1)}m</text>
                <text x="202.5" y="150" text-anchor="middle" fill="#94a3b8" font-size="9">Comparada</text>
                <text x="150" y="166" text-anchor="middle" fill="#64748b" font-size="8">Base: Corte | Topo vermelho: Piloto / Canhão</text>
            `;

            const horizonteFuros = Math.max(data.qtdFuros, 100);
            const steps = 20;
            let ptsAtual = [];
            let ptsComp = [];
            let maxY = 1;

            for (let i = 0; i <= steps; i++) {
                const xFuro = (horizonteFuros / steps) * i;
                const yA = data.custoInicialAtual + (data.slopeAtual * xFuro);
                const yC = data.custoInicialComp + (data.slopeComp * xFuro);
                maxY = Math.max(maxY, yA, yC);
                ptsAtual.push({ xFuro, y: yA });
                ptsComp.push({ xFuro, y: yC });
            }

            const padL = 42, padR = 16, padT = 16, padB = 32;
            const wPlot = 300 - padL - padR;
            const hPlot = 175 - padT - padB;

            const toSvgX = (f) => padL + (f / horizonteFuros) * wPlot;
            const toSvgY = (v) => padT + hPlot - (v / (maxY * 1.08)) * hPlot;

            const pathAtual = ptsAtual.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${toSvgX(p.xFuro).toFixed(1)} ${toSvgY(p.y).toFixed(1)}`).join(' ');
            const pathComp = ptsComp.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${toSvgX(p.xFuro).toFixed(1)} ${toSvgY(p.y).toFixed(1)}`).join(' ');

            svgBe.innerHTML = `
                <line x1="${padL}" y1="${padT + hPlot}" x2="${padL + wPlot}" y2="${padT + hPlot}" stroke="#334155" stroke-width="1.2" />
                <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${padT + hPlot}" stroke="#334155" stroke-width="1.2" />
                <text x="${padL - 5}" y="${padT + 8}" text-anchor="end" fill="#64748b" font-size="8">${Math.round(maxY)}€</text>
                <text x="${padL - 5}" y="${padT + hPlot}" text-anchor="end" fill="#64748b" font-size="8">0€</text>
                <text x="${padL + wPlot / 2}" y="164" text-anchor="middle" fill="#94a3b8" font-size="8">0 → ${horizonteFuros} furos</text>
                <path d="${pathAtual}" fill="none" stroke="#38bdf8" stroke-width="2.2" />
                <path d="${pathComp}" fill="none" stroke="#fbbf24" stroke-width="2.2" stroke-dasharray="4,2" />
            `;
        }

        function aplicarFerramentaComparada() {
            const compKey = document.getElementById('comp-ferramenta').value;
            if (!compKey || compKey === "__CLIENTE__" || !dados[compKey]) return;

            const compVar = document.getElementById('comp-variante').value;
            const tool = dados[compKey];

            document.getElementById('linha').value = tool.linha;
            document.getElementById('categoria').value = tool.categoria;
            document.getElementById('filtro-refrig').value = tool.temRefrigInt ? 'com' : 'sem';
            atualizarFiltroBrocas(true);
            document.getElementById('broca').value = compKey;
            mudarBroca(compVar);
            fecharJanelaResultadoComparacao();
        }

        function desenharGrafico(diametros, fArr, dAtual, fAtual) {
            const svg = document.getElementById('svg-grafico');
            svg.innerHTML = '';

            const width = 400;
            const height = 180;
            const padLeft = 45;
            const padRight = 20;
            const padTop = 20;
            const padBottom = 35;

            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;

            let minX = Math.min(...diametros, dAtual);
            let maxX = Math.max(...diametros, dAtual);
            let minY = Math.min(...fArr, fAtual);
            let maxY = Math.max(...fArr, fAtual);

            const rangeX = (maxX - minX) || 1;
            const rangeY = (maxY - minY) || 0.1;

            minX -= rangeX * 0.05;
            maxX += rangeX * 0.05;
            minY = Math.max(0, minY - rangeY * 0.15);
            maxY += rangeY * 0.15;

            const xScale = (val) => padLeft + ((val - minX) / (maxX - minX)) * plotW;
            const yScale = (val) => padTop + plotH - ((val - minY) / (maxY - minY)) * plotH;

            for(let i=0; i<=4; i++) {
                const yVal = minY + (maxY - minY) * (i/4);
                const yPos = yScale(yVal);
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", padLeft);
                line.setAttribute("y1", yPos);
                line.setAttribute("x2", width - padRight);
                line.setAttribute("y2", yPos);
                line.setAttribute("stroke", "#1e293b");
                line.setAttribute("stroke-width", "1");
                svg.appendChild(line);

                const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                txt.setAttribute("x", padLeft - 6);
                txt.setAttribute("y", yPos + 3);
                txt.setAttribute("fill", "#94a3b8");
                txt.setAttribute("font-size", "9");
                txt.setAttribute("text-anchor", "end");
                txt.textContent = yVal.toFixed(2);
                svg.appendChild(txt);
            }

            const axisX = document.createElementNS("http://www.w3.org/2000/svg", "line");
            axisX.setAttribute("x1", padLeft);
            axisX.setAttribute("y1", padTop + plotH);
            axisX.setAttribute("x2", width - padRight);
            axisX.setAttribute("y2", padTop + plotH);
            axisX.setAttribute("stroke", "#475569");
            axisX.setAttribute("stroke-width", "1.5");
            svg.appendChild(axisX);

            const axisY = document.createElementNS("http://www.w3.org/2000/svg", "line");
            axisY.setAttribute("x1", padLeft);
            axisY.setAttribute("y1", padTop);
            axisY.setAttribute("x2", padLeft);
            axisY.setAttribute("y2", padTop + plotH);
            axisY.setAttribute("stroke", "#475569");
            axisY.setAttribute("stroke-width", "1.5");
            svg.appendChild(axisY);

            let pathD = "";
            diametros.forEach((d, idx) => {
                const px = xScale(d);
                const py = yScale(fArr[idx]);
                pathD += (idx === 0 ? "M " : "L ") + px + " " + py;
            });

            const pathEl = document.createElementNS("http://www.w3.org/2000/svg", "path");
            pathEl.setAttribute("d", pathD);
            pathEl.setAttribute("fill", "none");
            pathEl.setAttribute("stroke", "#3b82f6");
            pathEl.setAttribute("stroke-width", "2.5");
            svg.appendChild(pathEl);

            diametros.forEach((d, idx) => {
                const px = xScale(d);
                const py = yScale(fArr[idx]);
                const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                circle.setAttribute("cx", px);
                circle.setAttribute("cy", py);
                circle.setAttribute("r", "3.5");
                circle.setAttribute("fill", "#60a5fa");
                svg.appendChild(circle);

                const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
                lbl.setAttribute("x", px);
                lbl.setAttribute("y", padTop + plotH + 14);
                lbl.setAttribute("fill", "#94a3b8");
                lbl.setAttribute("font-size", "9");
                lbl.setAttribute("text-anchor", "middle");
                lbl.textContent = d.toFixed(1);
                svg.appendChild(lbl);
            });

            const pxAtual = xScale(dAtual);
            const pyAtual = yScale(fAtual);

            const circleAtual = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circleAtual.setAttribute("cx", pxAtual);
            circleAtual.setAttribute("cy", pyAtual);
            circleAtual.setAttribute("r", "5.5");
            circleAtual.setAttribute("fill", "#f97316");
            circleAtual.setAttribute("stroke", "#ffffff");
            circleAtual.setAttribute("stroke-width", "1.5");
            svg.appendChild(circleAtual);

            const txtAtual = document.createElementNS("http://www.w3.org/2000/svg", "text");
            txtAtual.setAttribute("x", pxAtual);
            txtAtual.setAttribute("y", pyAtual - 9);
            txtAtual.setAttribute("fill", "#fb923c");
            txtAtual.setAttribute("font-size", "10");
            txtAtual.setAttribute("font-weight", "bold");
            txtAtual.setAttribute("text-anchor", "middle");
            txtAtual.textContent = `Ø${dAtual.toFixed(1)} (${fAtual.toFixed(3)})`;
            svg.appendChild(txtAtual);

            const labelX = document.createElementNS("http://www.w3.org/2000/svg", "text");
            labelX.setAttribute("x", padLeft + plotW / 2);
            labelX.setAttribute("y", height - 4);
            labelX.setAttribute("fill", "#64748b");
            labelX.setAttribute("font-size", "9");
            labelX.setAttribute("text-anchor", "middle");
            labelX.textContent = "Diâmetro (mm)";
            svg.appendChild(labelX);

            const labelY = document.createElementNS("http://www.w3.org/2000/svg", "text");
            labelY.setAttribute("x", 12);
            labelY.setAttribute("y", padTop + plotH / 2);
            labelY.setAttribute("fill", "#64748b");
            labelY.setAttribute("font-size", "9");
            labelY.setAttribute("text-anchor", "middle");
            labelY.setAttribute("transform", `rotate(-90, 12, ${padTop + plotH / 2})`);
            labelY.textContent = "Avanço f (mm/rot)";
            svg.appendChild(labelY);
        }

        function abrirModalExportacao() {
            document.getElementById('modal-export').classList.remove('hidden');
        }

        function fecharModalExportacao() {
            document.getElementById('modal-export').classList.add('hidden');
        }

        function gerarPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            const tipo = document.querySelector('input[name="tipo-relatorio"]:checked').value;
            const d = cacheResultados;
            const incluirComp = document.getElementById('comp-incluir-pdf') ? document.getElementById('comp-incluir-pdf').checked : false;

            doc.setFillColor(15, 23, 42);
            doc.rect(0, 0, 210, 28, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(15);
            doc.setFont(undefined, 'bold');
            doc.text("MAPAL — Proposta Técnico-Comercial de Furação", 14, 13);
            doc.setFontSize(9);
            doc.setFont(undefined, 'normal');
            doc.text(tipo === 'completo' ? "Relatório Técnico Completo" : "Proposta Comercial Resumida", 14, 21);
            doc.text(`Data: ${new Date().toLocaleDateString('pt-PT')}`, 170, 21);

            let y = 38;
            doc.setTextColor(30, 41, 59);
            doc.setFontSize(11);
            doc.setFont(undefined, 'bold');
            doc.text("1. Ferramenta e Aplicação", 14, y);
            y += 6;
            doc.setFontSize(10);
            doc.setFont(undefined, 'normal');
            doc.text(`Ferramenta: ${d.ferramenta || ''} (${d.linha || ''})`, 14, y); y += 6;
            doc.text(`Material (MMG): ${d.grupo || ''} | Refrigeração: ${d.refrig || ''} | Lote: ${d.qtdFuros || 0} furos (${d.metragemLinearM || 0} m)`, 14, y); y += 6;
            doc.text(`Diâmetro: Ø${d.diametro || 0} mm | Profundidade: ${d.profundidade || 0} mm | Lim. nom.: ${d.limiteNominalMm || 0} mm`, 14, y); y += 6;
            doc.text(`Validação Profundidade: ${d.estadoProfundidade || ''}`, 14, y); y += 8;

            doc.setFontSize(11);
            doc.setFont(undefined, 'bold');
            doc.text("2. Parâmetros de Corte Recomendados", 14, y);
            y += 6;
            doc.setFontSize(10);
            doc.setFont(undefined, 'normal');
            doc.text(`Velocidade de Corte (Vc): ${d.vc || 0} m/min | Rotações (n): ${d.n || 0} rpm`, 14, y); y += 6;
            doc.text(`Avanço (f): ${d.f || 0} mm/rot | Avanço de Trabalho (vf): ${d.vf || 0} mm/min`, 14, y); y += 8;

            doc.setFontSize(11);
            doc.setFont(undefined, 'bold');
            doc.text("3. Tempos e Custos de Maquinação", 14, y);
            y += 6;
            doc.setFontSize(10);
            doc.setFont(undefined, 'normal');
            doc.text(`Tempo Unitário: ${d.tempoFuroSeg || 0} seg/furo | Tempo Total Lote: ${d.tempoTotalMin || 0} min`, 14, y); y += 6;
            doc.text(`Custo Hora Máquina: ${d.custoHora || 0} €/h | Custo por Furo: ${d.custoFuro || 0} € | Custo Total Lote: ${d.custoTotalLote || 0} €`, 14, y); y += 8;

            if (tipo === 'completo') {
                doc.setFontSize(11);
                doc.setFont(undefined, 'bold');
                doc.text("4. Ciclo, Volume, Sucata e Esforços", 14, y);
                y += 6;
                doc.setFontSize(10);
                doc.setFont(undefined, 'normal');
                doc.text(`Ciclo Pecking: ${d.pecking || ''}`, 14, y); y += 6;
                doc.text(`Volume Lote: ${d.volumeTotalCm3 || 0} cm³ | Massa Limalha: ${d.massaTotalKg || 0} kg | Valor Sucata: ${d.valorTotalSucata || 0} €`, 14, y); y += 6;
                doc.text(`Força Axial (Ff): ${d.forcaN || 0} N (${d.forcaKgf || 0} kgf) | Binário (Mc): ${d.binarioNm || 0} N·m | Potência: ${d.potenciaKw || 0} kW`, 14, y); y += 8;
            }

            if (incluirComp && cacheComparacao) {
                if (y > 225) {
                    doc.addPage();
                    y = 20;
                }
                const c = cacheComparacao;
                doc.setFontSize(11);
                doc.setFont(undefined, 'bold');
                doc.text("5. Comparativo Técnico-Comercial", 14, y);
                y += 6;
                doc.setFontSize(9.5);
                doc.setFont(undefined, 'normal');
                doc.text(`Comparação: ${c.tituloAtual} vs. ${c.tituloComp} (Grupo ${c.grupo})`, 14, y); y += 5;
                if (c.corteInterrompido) {
                    doc.text(`Condição: Corte Interrompido (Interceções / Cascatas) | Ref. contínuo: ${c.refContinuo}`, 14, y); y += 5;
                }
                if (c.requerPiloto) {
                    doc.text(`Furo-Piloto Prévio: Sim (+${c.tempoPilotoSeg} s/furo | +${c.custoPilotoFuro} €/furo)`, 14, y); y += 5;
                    if (c.usaBrocaCanhao) {
                        doc.text(`Broca Canhão (Paragem p/ Afiar): ${c.numParagensCanhao} paragens (+${c.tempoParagemCanhaoMin} min no lote)`, 14, y); y += 5;
                    }
                }
                doc.text(`Vc: ${c.vcAtual} vs ${c.vcComp} m/min | Avanço f: ${c.fAtual} vs ${c.fComp} mm/rot | Tempo/furo: ${c.tempoFuroAtual} vs ${c.tempoFuroComp} seg`, 14, y); y += 5;
                doc.text(`Tempo Lote: ${c.tempoLoteAtual} vs ${c.tempoLoteComp} min | Vida Total: ${c.vidaTotalAtual} vs ${c.vidaTotalComp}`, 14, y); y += 5;
                doc.text(`Custo Ferramenta/Furo: ${c.custoFerrFuroAtual} vs ${c.custoFerrFuroComp} € | Custo Total/Furo: ${c.custoTotalFuroAtual} vs ${c.custoTotalFuroComp} €`, 14, y); y += 5;
                doc.text(`Custo Total Lote: ${c.custoTotalLoteAtual} vs ${c.custoTotalLoteComp} € | Dif. Lote: ${c.diffCustoLote} € | Break-Even: ${c.pontoEquilibrio}`, 14, y); y += 8;
            }

            doc.setDrawColor(203, 213, 225);
            doc.line(14, 272, 196, 272);
            doc.setFontSize(8.5);
            doc.setTextColor(100, 116, 139);
            doc.text("Bruno Pinto — bruno.pinto@alamo-ferramentas.com | +351 936 959 415", 14, 279);

            doc.save(`Proposta_MAPAL_${d.ferramenta ? d.ferramenta.split(' ')[0] : 'Calculo'}_${tipo}.pdf`);
            fecharModalExportacao();
        }

        atualizarFiltroBrocas();
    </script>
</body>
</html>
'''

components.html(html_content, height=960, scrolling=True)
