import json
from pathlib import Path
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

pro_password = ""
try:
    pro_password = str(st.secrets.get("PRO_PASSWORD", ""))
except Exception:
    pro_password = ""


def load_json_safe(path: str):
    p = Path(path)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


referencias_catalogo = load_json_safe("dados/referencias.json")
parametros_furacao_json = load_json_safe("dados/furacao_parametros.json")

pro_password_js = json.dumps(pro_password)
referencias_js = json.dumps(referencias_catalogo, ensure_ascii=False)
parametros_json_js = json.dumps(parametros_furacao_json, ensure_ascii=False)

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
        <header class="bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 flex flex-wrap justify-between items-center gap-2 shrink-0">
            <div class="flex items-center gap-2.5">
                <h1 class="text-base font-bold text-white flex items-center gap-2">
                    <span>⚙️</span> Parâmetros de Corte MAPAL
                </h1>
                <span id="badge-nivel-ativo" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-700 text-cyan-300 border border-slate-600">
                    Nível Básico
                </span>
            </div>
            <div class="flex items-center gap-2">
                <button id="btn-modo-pro" onclick="gerirModoPro()" class="bg-purple-600 hover:bg-purple-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white transition flex items-center gap-1.5">
                    <span>🔒</span> Aderir Nível Pro
                </button>
                <button onclick="resetRapidoTudo()" title="Repor Vc, f, RPM máx., ajustes % e pecking" class="bg-amber-600 hover:bg-amber-500 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>↺</span> Reset Rápido
                </button>
                <button id="btn-comparar-familia" onclick="abrirModalComparacao()" class="pro-only hidden bg-emerald-600 hover:bg-emerald-500 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>⚖️</span> Comparar Família
                </button>
                <button onclick="abrirModalExportacao()" class="bg-blue-600 hover:bg-blue-500 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>📄</span> <span id="lbl-btn-export">Exportar PDF</span>
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

                <!-- Pesquisa Rápida por Order no. / Specification / Família / Diâmetro -->
                <div class="space-y-1 shrink-0 bg-slate-900/90 p-2 rounded-md border border-cyan-800/60">
                    <div class="flex justify-between items-center">
                        <label class="text-[11px] font-medium text-cyan-300">PESQUISA RÁPIDA (ORDER NO. / REF. / ×D)</label>
                        <button type="button" onclick="limparFiltrosCatalogo()" class="text-[10px] text-slate-400 hover:text-cyan-300 underline">Limpar filtros</button>
                    </div>
                    <div class="flex gap-1.5">
                        <input type="text" id="ref-pesquisa" placeholder="Ex: 30902099, SCD661 12XD, 10.00..." class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500" oninput="filtrarCatalogoCascata()" onkeydown="if(event.key==='Enter') aplicarPesquisaReferencia()">
                        <button type="button" onclick="aplicarPesquisaReferencia()" class="bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white transition shrink-0">Aplicar</button>
                    </div>
                    <span id="ref-feedback" class="text-[10px] text-slate-400 block">Filtros vazios por defeito: selecione Ø d1, ×D ou refrigeração.</span>
                </div>

                <!-- Filtros em Cascata (Vazios por defeito) -->
                <div class="bg-slate-900/70 p-2.5 rounded-md border border-slate-700/80 space-y-2 shrink-0">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Seleção Progressiva do Catálogo</span>
                        <span id="contador-referencias" class="text-[10px] text-slate-400 font-mono">0 ref.</span>
                    </div>
                    <div class="grid grid-cols-3 gap-1.5">
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">1. Diâmetro d1</label>
                            <select id="filtro-d1" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('d1')">
                                <option value="">Todos</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">2. Variante ×D</label>
                            <select id="filtro-xd" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-cyan-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('xd')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">3. Refrigeração</label>
                            <select id="filtro-refrig-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('refrig')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                    </div>
                    <div class="space-y-0.5">
                        <label class="text-[10px] font-medium text-slate-300 block">4. Referência / Order no.</label>
                        <select id="filtro-order-no" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onSelecionarOrderCatalogo()">
                            <option value="">— Selecionar referência compatível —</option>
                        </select>
                    </div>
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

                <!-- 7. Dimensões -->
                <div class="grid grid-cols-2 gap-2 shrink-0">
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">7. DIÂMETRO (Ø)</label>
                        <div class="flex items-center gap-1">
                            <button onclick="ajustarDiametro(-0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">-</button>
                            <input type="number" id="diametro" value="12.00" step="0.1" min="0.5" max="30" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                            <button onclick="ajustarDiametro(0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">+</button>
                        </div>
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">8. PROFUNDIDADE/FURO (L)</label>
                        <div class="flex items-center gap-1">
                            <input type="number" id="profundidade" value="31.0" step="1" min="0.1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                            <span class="text-[10px] text-slate-400 font-medium">mm</span>
                        </div>
                    </div>
                </div>

                <!-- Validação de Profundidade com l3 (Limite Máximo Real) -->
                <div id="alerta-profundidade" class="bg-slate-900 px-2.5 py-1.5 rounded-md border border-slate-700 text-[10px] text-slate-200 flex justify-between items-center gap-2 shrink-0">
                    <span id="texto-limite-prof">Profundidade a validar com catálogo</span>
                    <span id="badge-limite-prof" class="font-bold text-amber-400 shrink-0">VALIDAR</span>
                </div>

                <!-- [PRO] Lote, Densidade, Pecking, Sucata e Custo Hora -->
                <div class="pro-only hidden space-y-2.5 shrink-0">
                    <div class="grid grid-cols-2 gap-2 pt-1">
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">9. QTD. FUROS (LOTE)</label>
                            <input type="number" id="qtd-furos" value="50" step="1" min="1" max="100000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">10. DENSIDADE (g/cm³)</label>
                            <input type="number" id="densidade" value="7.85" step="0.01" min="0.5" max="25" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                    </div>

                    <!-- Configuração de Ciclo com Pecking (Quebra de Cavaco) -->
                    <div class="bg-slate-900 p-2.5 rounded-md border border-slate-700/80 space-y-2">
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

                    <div class="grid grid-cols-2 gap-2 pt-1">
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">11. VALOR SUCATA (€/kg)</label>
                            <input type="number" id="preco-sucata" value="0.35" step="0.05" min="0" max="50" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">12. CUSTO HORA MÁQUINA (€/h)</label>
                            <input type="number" id="custo-hora" value="50.00" step="5" min="1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                    </div>
                </div>

                <!-- Capacidade do Spindle da Máquina (Opcional — Básico + Pro) -->
                <div class="space-y-2 pt-2 border-t border-slate-700 shrink-0">
                    <div class="flex justify-between items-center">
                        <label class="text-[11px] font-medium text-amber-400 uppercase tracking-wider">Capacidade do Spindle (Opcional)</label>
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

                <!-- Ajustes Percentuais (%) — Básico + Pro -->
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
                <!-- Cotas Dimensionais Separadas da Referência (d1, d2, l1, l2, l3, l4) -->
                <div class="bg-slate-800/95 p-2.5 rounded-lg border border-slate-700 shrink-0">
                    <div class="flex flex-wrap justify-between items-center gap-1 mb-2">
                        <span class="text-[11px] font-semibold text-cyan-300 uppercase tracking-wider">Cotas da Ferramenta Selecionada</span>
                        <span id="meta-referencia-ativa" class="text-[10px] text-slate-400 font-mono">Order: — | Spec: —</span>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-center">
                        <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80">
                            <div class="text-[10px] text-slate-400">d1 (Ø corte)</div>
                            <div id="cota-d1" class="text-sm font-bold text-white mt-0.5">—</div>
                        </div>
                        <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80">
                            <div class="text-[10px] text-slate-400">d2 (Ø encabadouro)</div>
                            <div id="cota-d2" class="text-sm font-bold text-white mt-0.5">—</div>
                        </div>
                        <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80">
                            <div class="text-[10px] text-slate-400">l1 (Comp. total)</div>
                            <div id="cota-l1" class="text-sm font-bold text-white mt-0.5">—</div>
                        </div>
                        <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80">
                            <div class="text-[10px] text-slate-400">l2 (Comp. navalha)</div>
                            <div id="cota-l2" class="text-sm font-bold text-white mt-0.5">—</div>
                        </div>
                        <div class="bg-slate-900/90 p-2 rounded border border-emerald-700/60">
                            <div class="text-[10px] text-emerald-300 font-semibold">l3 (Útil corte)</div>
                            <div id="cota-l3" class="text-sm font-bold text-emerald-300 mt-0.5">—</div>
                        </div>
                        <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80">
                            <div class="text-[10px] text-slate-400">l4 (Comp. encab.)</div>
                            <div id="cota-l4" class="text-sm font-bold text-white mt-0.5">—</div>
                        </div>
                    </div>
                </div>

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

                <!-- Gráficos Visuais em Meia-Lua (Básico + Pro) -->
                <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 shrink-0">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[11px] font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                            <span>🎛️</span> Monitor Gráfico de Carga do Spindle (Conta-Rotações)
                        </span>
                        <span class="text-[10px] text-slate-400">Zona Verde (&lt;70%) | Amarela (70-90%) | Vermelha (&gt;90% Stall)</span>
                    </div>

                    <!-- Banner de Alerta Explícito >100% -->
                    <div id="alerta-sobrecarga-spindle" class="hidden mb-2 bg-red-950/80 border border-red-500/80 text-red-200 px-3 py-2 rounded-md text-xs flex items-center justify-between gap-2">
                        <div class="flex items-center gap-2">
                            <span class="text-sm font-bold text-red-400">⚠️</span>
                            <span id="texto-sobrecarga-spindle" class="font-semibold">Sobrecarga do Spindle (&gt;100%).</span>
                        </div>
                        <span id="badge-sobrecarga-spindle" class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-red-600 text-white shrink-0">SOBRECARGA</span>
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

                <!-- [PRO] Indicadores de Tempo e Volume -->
                <div class="pro-only hidden grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
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

                <!-- [PRO] Peso e Sucata -->
                <div class="pro-only hidden grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
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

                <!-- Custos [PRO], Força e Binário [Básico + Pro] -->
                <div id="grid-esforcos-custos" class="grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
                    <div class="pro-only hidden bg-gradient-to-r from-indigo-900/40 to-slate-800 p-2.5 rounded-lg border border-indigo-700/50 flex justify-between items-center">
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

        <!-- Aviso Inicial de Parâmetros Teóricos -->
        <div id="modal-aviso-inicial" class="fixed inset-0 bg-black/85 flex items-center justify-center z-50 p-3">
            <div class="bg-slate-800 border border-amber-500/70 rounded-lg p-5 w-full max-w-md shadow-2xl flex flex-col gap-4">
                <div class="flex items-center gap-2.5 border-b border-slate-700 pb-2.5">
                    <span class="text-xl">⚠️</span>
                    <h3 class="text-sm font-bold text-amber-300 uppercase tracking-wide">Aviso Técnico Importante</h3>
                </div>
                <div class="bg-slate-900/90 p-3.5 rounded-md border border-slate-700 text-xs text-slate-200 leading-relaxed space-y-2">
                    <p class="font-semibold text-white">Atenção: todos os parâmetros de corte são teóricos e poderão sofrer alterações no momento da usabilidade, consoante a máquina, aperto da peça, aperto da ferramenta e material a cortar.</p>
                </div>
                <div class="flex justify-end">
                    <button type="button" onclick="fecharAvisoInicial()" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-md text-xs font-bold text-white transition w-full sm:w-auto">
                        Compreendi, Continuar
                    </button>
                </div>
            </div>
        </div>

        <!-- Modal de Password para Nível Pro -->
        <div id="modal-password-pro" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 hidden p-3">
            <div class="bg-slate-800 border border-purple-500/70 rounded-lg p-5 w-full max-w-sm shadow-2xl flex flex-col gap-3.5">
                <div class="flex justify-between items-center border-b border-slate-700 pb-2">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2"><span>🔓</span> Acesso ao Nível Pro</h3>
                    <button type="button" onclick="fecharModalPassword()" class="text-slate-400 hover:text-white font-bold text-sm">✕</button>
                </div>
                <p class="text-xs text-slate-300">Introduza a password para desbloquear custos, lote/pecking, sucata, comparador comercial e relatório técnico completo:</p>
                <div class="space-y-1">
                    <input type="password" id="input-pro-password" placeholder="Password Nível Pro" class="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500" onkeydown="if(event.key==='Enter') validarPasswordPro()">
                    <p id="erro-pro-password" class="text-[11px] text-rose-400 hidden">Password incorreta.</p>
                </div>
                <div class="flex justify-end gap-2 pt-1">
                    <button type="button" onclick="fecharModalPassword()" class="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-md text-xs font-medium text-white transition">Cancelar</button>
                    <button type="button" onclick="validarPasswordPro()" class="bg-purple-600 hover:bg-purple-500 px-3.5 py-1.5 rounded-md text-xs font-bold text-white transition">Desbloquear Pro</button>
                </div>
            </div>
        </div>

        <!-- PASSO 1: Modal de Configuração da Comparação -->
        <div id="modal-comparacao" class="fixed inset-0 bg-black/75 flex items-center justify-center z-50 hidden p-3">
            <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 w-full max-w-3xl shadow-2xl flex flex-col gap-3.5 max-h-[92vh] overflow-y-auto">
                <div class="flex justify-between items-center border-b border-slate-700 pb-2.5">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2"><span>⚖️</span> Comparação Técnico-Comercial — Passo 1: Dados da Aplicação</h3>
                        <p class="text-[11px] text-slate-400">Preencha os parâmetros da ferramenta, reafiações e condições de oficina e clique em <strong>Ver Resultado &amp; Gráficos</strong>.</p>
                    </div>
                    <button onclick="fecharModalComparacao()" class="text-slate-400 hover:text-white font-bold text-sm px-2 py-1">✕</button>
                </div>

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

        <!-- PASSO 2: Janela Dedicada de Resultados Visuais -->
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

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
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
                    <h3 class="text-sm font-bold text-white flex items-center gap-2"><span>📄</span> Escolher Tipo de Relatório PDF</h3>
                    <button onclick="fecharModalExportacao()" class="text-slate-400 hover:text-white font-bold text-sm">✕</button>
                </div>
                <p id="desc-modal-export" class="text-xs text-slate-300">Selecione o nível de detalhe que pretende incluir no PDF:</p>
                <div class="flex flex-col gap-2">
                    <label class="flex items-start gap-2 bg-slate-900 p-2.5 rounded-md border border-slate-700 cursor-pointer hover:border-blue-500 transition">
                        <input type="radio" name="tipo-relatorio" id="radio-pdf-resumido" value="resumido" class="mt-0.5 accent-blue-500" checked>
                        <div>
                            <strong class="text-xs text-white block">Ficha Técnica / Parâmetros de Corte (Básico)</strong>
                            <span class="text-[10px] text-slate-400">Ferramenta, material, parâmetros de corte (Vc, RPM, f, vf) e esforços/spindle.</span>
                        </div>
                    </label>
                    <label id="opcao-pdf-completo" class="pro-only hidden flex items-start gap-2 bg-slate-900 p-2.5 rounded-md border border-slate-700 cursor-pointer hover:border-blue-500 transition">
                        <input type="radio" name="tipo-relatorio" id="radio-pdf-completo" value="completo" class="mt-0.5 accent-blue-500">
                        <div>
                            <strong class="text-xs text-white block">Proposta Técnico-Comercial Completa (Pro)</strong>
                            <span class="text-[10px] text-slate-400">Inclui lote, tempos, custos, limalha, sucata, pecking, esforços e comparativo.</span>
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
        const PRO_PASSWORD = __PRO_PASSWORD_PLACEHOLDER__;
        const REFERENCIAS_JSON = __REFERENCIAS_JSON_PLACEHOLDER__;
        const PARAMETROS_JSON = __PARAMETROS_JSON_PLACEHOLDER__;
        let isProMode = false;
        let referenciaAtivaObj = null;

        let refrigAtual = 'int';
        let vcPct = 0;
        let fPct = 0;
        let fUnlocked = false;
        let vcUnlocked = false;
        let rpmMaxUnlocked = false;
        let corteInterrompidoAtivo = false;

        function fecharAvisoInicial() {
            const modal = document.getElementById('modal-aviso-inicial');
            if (modal) modal.classList.add('hidden');
        }

        function aplicarModoUI() {
            const proEls = document.querySelectorAll('.pro-only');
            proEls.forEach(el => {
                if (isProMode) {
                    el.classList.remove('hidden');
                } else {
                    el.classList.add('hidden');
                }
            });

            const badge = document.getElementById('badge-nivel-ativo');
            const btnPro = document.getElementById('btn-modo-pro');
            const gridEsforcos = document.getElementById('grid-esforcos-custos');
            const lblExport = document.getElementById('lbl-btn-export');

            if (isProMode) {
                badge.innerText = 'Nível Pro';
                badge.className = 'text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-500/70';
                btnPro.innerHTML = '<span>🔓</span> Sair do Pro';
                btnPro.className = 'bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded-md text-xs font-semibold text-purple-200 border border-purple-500/50 transition flex items-center gap-1.5';
                gridEsforcos.className = 'grid grid-cols-1 md:grid-cols-3 gap-2.5 shrink-0';
                lblExport.innerText = 'Exportar Proposta PDF';
            } else {
                badge.innerText = 'Nível Básico';
                badge.className = 'text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-700 text-cyan-300 border border-slate-600';
                btnPro.innerHTML = '<span>🔒</span> Aderir Nível Pro';
                btnPro.className = 'bg-purple-600 hover:bg-purple-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white transition flex items-center gap-1.5';
                gridEsforcos.className = 'grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0';
                lblExport.innerText = 'Exportar PDF';
                document.getElementById('radio-pdf-resumido').checked = true;
                fecharModalComparacao();
                fecharJanelaResultadoComparacao();
            }
        }

        function gerirModoPro() {
            if (isProMode) {
                isProMode = false;
                aplicarModoUI();
                atualizarCalculo();
                return;
            }
            document.getElementById('erro-pro-password').classList.add('hidden');
            const inp = document.getElementById('input-pro-password');
            inp.value = '';
            document.getElementById('modal-password-pro').classList.remove('hidden');
            setTimeout(() => inp.focus(), 50);
        }

        function fecharModalPassword() {
            document.getElementById('modal-password-pro').classList.add('hidden');
        }

        function validarPasswordPro() {
            const inp = document.getElementById('input-pro-password');
            const erro = document.getElementById('erro-pro-password');
            const val = inp.value;

            if (!PRO_PASSWORD) {
                erro.innerText = 'Password Pro não configurada em st.secrets["PRO_PASSWORD"].';
                erro.classList.remove('hidden');
                return;
            }

            if (val === PRO_PASSWORD) {
                isProMode = true;
                fecharModalPassword();
                aplicarModoUI();
                atualizarCalculo();
            } else {
                erro.innerText = 'Password incorreta.';
                erro.classList.remove('hidden');
                inp.select();
            }
        }

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

        if (Array.isArray(PARAMETROS_JSON) && PARAMETROS_JSON.length > 0) {
            PARAMETROS_JSON.forEach(row => {
                const famRaw = String(row.familia || row.Familia || '').trim().toLowerCase();
                if (!famRaw || !dados[famRaw]) return;
                const grp = String(row.grupo || row.Grupo || '').trim();
                const vcVal = parseFloat(row.vc);
                const fVal = parseFloat(row.f);
                if (grp && !isNaN(vcVal) && !isNaN(fVal)) {
                    if (!dados[famRaw].grupos[grp]) {
                        dados[famRaw].grupos[grp] = { vc: { int: vcVal, ext: vcVal, mql: vcVal, ar: 0 }, f: [fVal, fVal, fVal, fVal, fVal, fVal] };
                        if (!dados[famRaw].gruposList.includes(grp)) {
                            dados[famRaw].gruposList.push(grp);
                            dados[famRaw].gruposNames[grp] = GRUPOS_MAPAL_PADRAO.gruposNames[grp] || grp;
                        }
                    }
                }
            });
        }

        function fmtCota(val, dec = 0, unit = ' mm') {
            if (val === null || val === undefined || val === '' || isNaN(Number(val))) return '—';
            return `${Number(val).toFixed(dec)}${unit}`;
        }

        function atualizarPainelCotas() {
            const r = referenciaAtivaObj;
            document.getElementById('cota-d1').innerText = r ? fmtCota(r.d1, 2) : fmtCota(parseFloat(document.getElementById('diametro').value), 2);
            document.getElementById('cota-d2').innerText = r ? fmtCota(r.d2, 1) : '—';
            document.getElementById('cota-l1').innerText = r ? fmtCota(r.l1, 0) : '—';
            document.getElementById('cota-l2').innerText = r ? fmtCota(r.l2, 0) : '—';
            document.getElementById('cota-l3').innerText = r ? fmtCota(r.l3, 0) : '—';
            document.getElementById('cota-l4').innerText = r ? fmtCota(r.l4, 0) : '—';

            const metaEl = document.getElementById('meta-referencia-ativa');
            if (r) {
                metaEl.innerText = `Order: ${r.order_no || '—'} | Spec: ${r.specification || '—'} | Refrig.: ${r.refrigeracao || '—'}`;
            } else {
                const brocaKey = document.getElementById('broca').value;
                const varKey = document.getElementById('variante-xd').value || '—';
                metaEl.innerText = `Família: ${(brocaKey || '—').toUpperCase()} (${varKey}) | Sem referência de catálogo selecionada`;
            }
        }

        function limparFiltrosCatalogo() {
            document.getElementById('ref-pesquisa').value = '';
            document.getElementById('filtro-d1').value = '';
            document.getElementById('filtro-xd').value = '';
            document.getElementById('filtro-refrig-cat').value = '';
            document.getElementById('filtro-order-no').value = '';
            referenciaAtivaObj = null;
            filtrarCatalogoCascata();
            atualizarPainelCotas();
            atualizarCalculo();
        }

        function getCandidatosCatalogoBase() {
            const q = (document.getElementById('ref-pesquisa').value || '').trim().toLowerCase();
            if (!Array.isArray(REFERENCIAS_JSON)) return [];
            if (!q) return REFERENCIAS_JSON;
            const tokens = q.split(/\s+/).filter(Boolean);
            return REFERENCIAS_JSON.filter(item => {
                const hay = [
                    item.order_no,
                    item.specification,
                    item.familia,
                    item.variante,
                    item.refrigeracao,
                    item.d1 !== null && item.d1 !== undefined ? Number(item.d1).toFixed(2) : ''
                ].join(' ').toLowerCase();
                return tokens.every(tok => hay.includes(tok));
            });
        }

        function preencherSelectOpcoes(selectEl, opcoes, placeholderText, formatFn, valorAtual) {
            selectEl.innerHTML = '';
            const optEmpty = document.createElement('option');
            optEmpty.value = '';
            optEmpty.text = placeholderText;
            selectEl.appendChild(optEmpty);

            opcoes.forEach(val => {
                const opt = document.createElement('option');
                opt.value = String(val);
                opt.text = formatFn ? formatFn(val) : String(val);
                if (valorAtual !== '' && String(val) === String(valorAtual)) {
                    opt.selected = true;
                }
                selectEl.appendChild(opt);
            });
        }

        function filtrarCatalogoCascata(origem = null) {
            const selD1 = document.getElementById('filtro-d1');
            const selXd = document.getElementById('filtro-xd');
            const selRefrig = document.getElementById('filtro-refrig-cat');
            const selOrder = document.getElementById('filtro-order-no');

            let valD1 = selD1.value;
            let valXd = selXd.value;
            let valRefrig = selRefrig.value;

            const base = getCandidatosCatalogoBase();

            const candD1 = base.filter(c =>
                (c.d1 !== null && c.d1 !== undefined && !isNaN(Number(c.d1))) &&
                (!valXd || String(c.variante || '') === valXd) &&
                (!valRefrig || String(c.refrigeracao || '') === valRefrig)
            );
            const d1List = [...new Set(candD1.map(c => Number(c.d1).toFixed(2)))].sort((a, b) => parseFloat(a) - parseFloat(b));
            if (valD1 && !d1List.includes(valD1)) valD1 = '';
            preencherSelectOpcoes(selD1, d1List, 'Todos Ø', d => `Ø ${d} mm`, valD1);

            const candXd = base.filter(c =>
                c.variante &&
                (!valD1 || (c.d1 !== null && Number(c.d1).toFixed(2) === valD1)) &&
                (!valRefrig || String(c.refrigeracao || '') === valRefrig)
            );
            const xdList = [...new Set(candXd.map(c => String(c.variante).trim()))].sort();
            if (valXd && !xdList.includes(valXd)) valXd = '';
            preencherSelectOpcoes(selXd, xdList, 'Todas ×D', x => x, valXd);

            const candRefrig = base.filter(c =>
                c.refrigeracao &&
                (!valD1 || (c.d1 !== null && Number(c.d1).toFixed(2) === valD1)) &&
                (!valXd || String(c.variante || '').trim() === valXd)
            );
            const refrigList = [...new Set(candRefrig.map(c => String(c.refrigeracao).trim()))].sort();
            if (valRefrig && !refrigList.includes(valRefrig)) valRefrig = '';
            preencherSelectOpcoes(selRefrig, refrigList, 'Interna / Ext.', r => r, valRefrig);

            const finais = base.filter(c =>
                (!valD1 || (c.d1 !== null && Number(c.d1).toFixed(2) === valD1)) &&
                (!valXd || String(c.variante || '').trim() === valXd) &&
                (!valRefrig || String(c.refrigeracao || '').trim() === valRefrig)
            );

            document.getElementById('contador-referencias').innerText = `${finais.length} ref.`;

            selOrder.innerHTML = '';
            const optDefault = document.createElement('option');
            optDefault.value = '';
            optDefault.text = finais.length > 0 ? `Escolher referência (${finais.length} disponíveis)...` : 'Sem referências com estes filtros';
            selOrder.appendChild(optDefault);

            finais.forEach((item, i) => {
                const opt = document.createElement('option');
                opt.value = String(i);
                const dTxt = item.d1 !== null && item.d1 !== undefined ? `Ø${Number(item.d1).toFixed(2)}` : 'Ø—';
                const l3Txt = item.l3 !== null && item.l3 !== undefined ? `l3:${Number(item.l3).toFixed(0)}mm` : 'l3:—';
                opt.text = `${item.order_no} | ${item.familia || '—'} | ${dTxt} (${item.variante || '—'}) | ${item.refrigeracao || '—'} | ${l3Txt}`;
                selOrder.appendChild(opt);
            });

            window._finaisCatalogoAtuais = finais;

            const temFiltroAtivo = Boolean(valD1 || valXd || valRefrig || (document.getElementById('ref-pesquisa').value || '').trim());
            if (finais.length === 1 && temFiltroAtivo) {
                selOrder.value = '0';
                onSelecionarOrderCatalogo();
            } else if (!temFiltroAtivo && origem !== 'order') {
                referenciaAtivaObj = null;
                atualizarPainelCotas();
            }
        }

        function onFiltroCatalogoChange(campo) {
            filtrarCatalogoCascata(campo);
        }

        function onSelecionarOrderCatalogo() {
            const selOrder = document.getElementById('filtro-order-no');
            const idx = parseInt(selOrder.value, 10);
            const lista = window._finaisCatalogoAtuais || [];
            if (isNaN(idx) || !lista[idx]) {
                referenciaAtivaObj = null;
                atualizarPainelCotas();
                atualizarCalculo();
                return;
            }
            aplicarReferenciaCatalogo(lista[idx]);
        }

        function aplicarReferenciaCatalogo(item) {
            referenciaAtivaObj = item;
            const famKey = String(item.familia || '').trim().toLowerCase();

            if (famKey && dados[famKey]) {
                const toolData = dados[famKey];
                document.getElementById('linha').value = toolData.linha;
                document.getElementById('categoria').value = toolData.categoria;
                const temIntCat = String(item.refrigeracao || '').toLowerCase().includes('int');
                document.getElementById('filtro-refrig').value = (temIntCat && toolData.temRefrigInt) ? 'com' : (toolData.temRefrigInt ? 'com' : 'sem');
                atualizarFiltroBrocas(true);
                document.getElementById('broca').value = famKey;

                const varNorm = String(item.variante || '').trim();
                const matchVar = Object.keys(toolData.variantes || {}).find(k => k.toLowerCase() === varNorm.toLowerCase());
                mudarBroca(matchVar || null);
            }

            if (item.d1 !== null && item.d1 !== undefined && !isNaN(Number(item.d1))) {
                document.getElementById('diametro').value = Number(item.d1).toFixed(2);
            }

            atualizarPainelCotas();
            atualizarCalculo();
        }

        function aplicarPesquisaReferencia() {
            const raw = document.getElementById('ref-pesquisa').value.trim();
            const feedback = document.getElementById('ref-feedback');
            filtrarCatalogoCascata('pesquisa');
            const lista = window._finaisCatalogoAtuais || [];

            if (!raw) {
                feedback.innerText = "Filtros vazios por defeito: selecione Ø d1, ×D ou refrigeração.";
                feedback.className = "text-[10px] text-slate-400 block";
                return;
            }

            if (lista.length > 0) {
                document.getElementById('filtro-order-no').value = '0';
                onSelecionarOrderCatalogo();
                feedback.innerText = `Encontradas ${lista.length} referência(s) para "${raw}". Selecionada: ${lista[0].order_no}.`;
                feedback.className = "text-[10px] text-emerald-400 block";
                return;
            }

            const upper = raw.toUpperCase();
            let encontradaKey = null;
            for (const key in dados) {
                if (upper.includes(key.toUpperCase())) {
                    encontradaKey = key;
                    break;
                }
            }

            if (!encontradaKey) {
                feedback.innerText = `Referência "${raw}" não encontrada no catálogo nem nas famílias.`;
                feedback.className = "text-[10px] text-amber-400 block";
                return;
            }

            const toolData = dados[encontradaKey];
            document.getElementById('linha').value = toolData.linha;
            document.getElementById('categoria').value = toolData.categoria;
            document.getElementById('filtro-refrig').value = toolData.temRefrigInt ? 'com' : 'sem';
            atualizarFiltroBrocas(true);
            document.getElementById('broca').value = encontradaKey;

            const matchXd = upper.match(/(\d+)\s*X\s*D/);
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
            atualizarPainelCotas();
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
                return null;
            }

            const pct = (val / maxVal) * 100;
            const clampedPct = Math.min(Math.max(pct, 0), 100);
            const angle = -90 + (clampedPct / 100) * 180;
            needle.style.transform = `rotate(${angle}deg)`;

            if (pct > 100) {
                badgeEl.innerText = pct.toFixed(0) + '% — Sobrecarga!';
                badgeEl.className = 'text-[9px] font-extrabold px-2 py-0.5 rounded bg-red-600 text-white border border-red-400';
            } else if (pct < 70) {
                badgeEl.innerText = pct.toFixed(0) + '% — Confortável';
                badgeEl.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-700/50';
            } else if (pct <= 90) {
                badgeEl.innerText = pct.toFixed(0) + '% — No Limite';
                badgeEl.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-700/50';
            } else {
                badgeEl.innerText = pct.toFixed(0) + '% — Risco Stall!';
                badgeEl.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-600/80';
            }

            return pct;
        }

        function atualizarAlertaSobrecarga(potReqKw, potMaxKw, pctPot, binReqNm, binMaxNm, pctBin) {
            const banner = document.getElementById('alerta-sobrecarga-spindle');
            const textoEl = document.getElementById('texto-sobrecarga-spindle');
            const badgeEl = document.getElementById('badge-sobrecarga-spindle');
            if (!banner || !textoEl || !badgeEl) return null;

            const sobrecargaPot = potMaxKw && potMaxKw > 0 && potReqKw > potMaxKw;
            const sobrecargaBin = binMaxNm && binMaxNm > 0 && binReqNm > binMaxNm;

            if (!sobrecargaPot && !sobrecargaBin) {
                banner.classList.add('hidden');
                return null;
            }

            const detalhes = [];
            let maxPct = 0;

            if (sobrecargaPot) {
                const pFmt = Math.round(pctPot);
                maxPct = Math.max(maxPct, pFmt);
                detalhes.push(`Potência a ${pFmt}% (${potReqKw.toFixed(2)} / ${potMaxKw.toFixed(2)} kW)`);
            }
            if (sobrecargaBin) {
                const bFmt = Math.round(pctBin);
                maxPct = Math.max(maxPct, bFmt);
                detalhes.push(`Binário a ${bFmt}% (${binReqNm.toFixed(1)} / ${binMaxNm.toFixed(1)} N·m)`);
            }

            textoEl.innerText = `Alerta de sobrecarga do spindle (>100%): ${detalhes.join(' · ')}.`;
            badgeEl.innerText = `CARGA REAL ${maxPct}%`;
            banner.classList.remove('hidden');

            return `Sobrecarga (${detalhes.join(' | ')})`;
        }

        let cacheResultados = {};
        let cacheComparacao = null;

        function lerContextoAtual() {
            const brocaKey = document.getElementById('broca').value;
            const grupoKey = document.getElementById('grupo').value;
            const varianteKey = document.getElementById('variante-xd').value || '5xD';
            const ligaCheck = document.getElementById('liga-check').checked;
            const peckingCheck = isProMode && document.getElementById('pecking-check').checked;
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
            if (isNaN(profundidade) || profundidade <= 0) profundidade = 31.00;

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
            if (isNaN(peckingInputVal) || peckingInputVal <= 0) peckingInputVal = peckingUnid === 'xd' ? 3.0 : 36.0;

            let peckingRetensaoVal = parseFloat(document.getElementById('pecking-retensao').value);
            if (isNaN(peckingRetensaoVal) || peckingRetensaoVal <= 0) peckingRetensaoVal = 5000;

            let rpmMaxVal = parseFloat(document.getElementById('input-rpm-max').value);
            if (isNaN(rpmMaxVal) || rpmMaxVal <= 0) rpmMaxVal = 8000;

            return {
                brocaKey, grupoKey, grupoEfetivoKey, varianteKey, ligaCheck,
                diametro, profundidade, qtdFuros, densidade, precoSucataKg, custoHora,
                refrigAtual, vcPct, fPct, rpmMaxUnlocked, rpmMaxVal,
                peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal
            };
        }

        function atualizarCalculo() {
            const ctx = lerContextoAtual();
            const { brocaKey, grupoKey, grupoEfetivoKey, varianteKey, ligaCheck, diametro, profundidade, qtdFuros, densidade, precoSucataKg, custoHora, peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal, rpmMaxUnlocked, rpmMaxVal } = ctx;

            if (!brocaKey || !dados[brocaKey] || !grupoKey) return;
            const toolData = dados[brocaKey];
            const grupoObj = toolData.grupos[grupoEfetivoKey];
            if (!grupoObj) return;

            document.getElementById('vc-pct-val').innerText = (vcPct > 0 ? '+' : '') + vcPct + '%';
            document.getElementById('f-pct-val').innerText = (fPct > 0 ? '+' : '') + fPct + '%';

            const passoMm = peckingUnid === 'xd' ? (peckingInputVal * diametro) : peckingInputVal;
            const numPassos = Math.max(1, Math.ceil(profundidade / passoMm));
            const equivEl = document.getElementById('pecking-equiv');
            if (peckingUnid === 'xd') {
                equivEl.innerText = `Equiv: ${passoMm.toFixed(1)} mm (${numPassos} passos)`;
            } else {
                equivEl.innerText = `Equiv: ${(passoMm / diametro).toFixed(2)} ×D (${numPassos} passos)`;
            }

            let m = calcularMetricasFerramenta(brocaKey, varianteKey, grupoEfetivoKey, ctx);
            if (!m) return;

            let vcFinal = m.vcFinal;
            let fFinal = m.fFinal;
            let n = m.n;
            let vf = m.vf;
            let estadoTexto = m.estadoTexto;
            let estadoCor = m.estadoCor;

            const inputVc = document.getElementById('input-vc');
            const inputF = document.getElementById('input-f');

            if (vcUnlocked) {
                let manualVc = parseFloat(inputVc.value);
                if (!isNaN(manualVc) && manualVc > 0) {
                    vcFinal = manualVc;
                    n = diametro > 0 ? Math.round((vcFinal * 1000) / (Math.PI * diametro)) : 0;
                    if (rpmMaxUnlocked && rpmMaxVal > 0 && n > rpmMaxVal) {
                        n = rpmMaxVal;
                        vcFinal = (n * Math.PI * diametro) / 1000;
                        estadoTexto = "Limitado por RPM Máx.";
                        estadoCor = "text-amber-400";
                    }
                }
            } else {
                inputVc.value = vcFinal.toFixed(1);
            }

            if (fUnlocked) {
                let manualF = parseFloat(inputF.value);
                if (!isNaN(manualF) && manualF > 0) {
                    fFinal = manualF;
                }
            } else {
                inputF.value = fFinal.toFixed(4);
            }

            vf = Math.round(fFinal * n);
            const cursoEfetivo = profundidade + (0.3 * diametro);
            let tempoFuroSeg = vf > 0 ? (cursoEfetivo / vf) * 60 : 0;

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

            document.getElementById('res-n').innerText = n;
            document.getElementById('res-vf').innerText = vf;
            document.getElementById('val-estado').innerText = estadoTexto;
            document.getElementById('val-estado').className = `text-[9px] font-bold ${estadoCor}`;
            document.getElementById('badge-metodo').innerText = m.badgeMetodo;

            // Validação de profundidade: l3 prevalece quando existe referência selecionada
            const alertaProf = document.getElementById('alerta-profundidade');
            const textoLimiteProf = document.getElementById('texto-limite-prof');
            const badgeLimiteProf = document.getElementById('badge-limite-prof');
            const limiteInfo = obterLimiteNominal(toolData, varianteKey, diametro);
            const maxNominalProf = limiteInfo.maxNominalMm;
            const l3Ref = (
                referenciaAtivaObj &&
                referenciaAtivaObj.l3 !== null &&
                referenciaAtivaObj.l3 !== undefined &&
                !isNaN(Number(referenciaAtivaObj.l3)) &&
                Number(referenciaAtivaObj.l3) > 0
            ) ? Number(referenciaAtivaObj.l3) : null;

            const limiteAtivo = l3Ref !== null ? l3Ref : maxNominalProf;
            const tol = 0.001;

            if (profundidade > limiteAtivo + tol) {
                const detalheLimite = l3Ref !== null
                    ? `Prof. ${profundidade.toFixed(2)} mm > l3 (${l3Ref.toFixed(1)} mm) [ref. ${varianteKey}: ${maxNominalProf.toFixed(1)} mm]`
                    : `Prof. ${profundidade.toFixed(2)} mm > ${varianteKey} (${maxNominalProf.toFixed(1)} mm)`;
                textoLimiteProf.innerText = `${detalheLimite} — validar com catálogo e descarga de cavaco`;
                badgeLimiteProf.innerText = l3Ref !== null ? "EXCEDE l3" : "EXCEDE ×D";
                badgeLimiteProf.className = "font-bold text-rose-400 shrink-0";
                alertaProf.className = "bg-rose-950/50 px-2.5 py-1.5 rounded-md border border-rose-500/70 text-[10px] text-rose-200 flex justify-between items-center gap-2 shrink-0";
            } else {
                const detalheOk = l3Ref !== null
                    ? `Dentro do útil l3 (${l3Ref.toFixed(1)} mm) — referência ${varianteKey} (${maxNominalProf.toFixed(1)} mm)`
                    : `Dentro da capacidade nominal ${varianteKey} (máx. ${maxNominalProf.toFixed(1)} mm)`;
                textoLimiteProf.innerText = detalheOk;
                badgeLimiteProf.innerText = "DENTRO DO LIMITE";
                badgeLimiteProf.className = "font-bold text-emerald-400 shrink-0";
                alertaProf.className = "bg-emerald-950/30 px-2.5 py-1.5 rounded-md border border-emerald-700/60 text-[10px] text-emerald-100 flex justify-between items-center gap-2 shrink-0";
            }

            const unidPot = document.getElementById('unidade-potencia').value;
            let potMaxInput = parseFloat(document.getElementById('spindle-potencia').value);
            let potMaxKw = null;
            if (!isNaN(potMaxInput) && potMaxInput > 0) {
                potMaxKw = unidPot === 'cv' ? (potMaxInput * 0.735499) : potMaxInput;
            }

            let binMaxNm = parseFloat(document.getElementById('spindle-binario').value);
            if (isNaN(binMaxNm) || binMaxNm <= 0) binMaxNm = null;

            const pctPot = atualizarGauge(potenciaReqKw, potMaxKw, 'needle-potencia', 'val-gauge-pot', 'badge-gauge-pot', 'kW');
            const pctBin = atualizarGauge(binarioMc, binMaxNm, 'needle-binario', 'val-gauge-bin', 'badge-gauge-bin', 'N·m');
            const alertaSobrecargaTexto = atualizarAlertaSobrecarga(potenciaReqKw, potMaxKw, pctPot, binarioMc, binMaxNm, pctBin);

            const areaFuroMm2 = Math.PI * Math.pow(diametro / 2, 2);
            const volumeFuroCm3 = (areaFuroMm2 * profundidade) / 1000;
            const volumeTotalCm3 = volumeFuroCm3 * qtdFuros;
            const taxaRemocaoCm3Min = (areaFuroMm2 * vf) / 1000;
            const metragemTotalM = (profundidade * qtdFuros) / 1000;

            const massaFuroG = volumeFuroCm3 * densidade;
            const pesoTotalKg = (massaFuroG * qtdFuros) / 1000;

            const valorSucataTotalEur = pesoTotalKg * precoSucataKg;
            const valorSucataFuroEur = qtdFuros > 0 ? (valorSucataTotalEur / qtdFuros) : 0;

            const forcaKgf = forcaFf / 9.80665;

            document.getElementById('res-tempo-total').innerHTML = `${tempoTotalMin.toFixed(1)} min <span class="text-xs font-normal text-slate-300" id="res-tempo-unit">(${tempoFuroSeg.toFixed(1)} seg/furo)</span>`;
            document.getElementById('res-metragem').innerText = `${metragemTotalM.toFixed(1)} metros`;
            document.getElementById('res-volume-total').innerText = `${volumeTotalCm3.toFixed(1)} cm³`;
            document.getElementById('res-taxa').innerText = `${taxaRemocaoCm3Min.toFixed(1)} cm³/min`;

            document.getElementById('res-peso').innerHTML = `${pesoTotalKg.toFixed(3)} <span class="text-sm font-normal text-slate-300">kg</span>`;
            document.getElementById('res-peso-g').innerText = `${massaFuroG.toFixed(2)} g`;
            document.getElementById('res-sucata-val').innerHTML = `${valorSucataTotalEur.toFixed(2)} <span class="text-sm font-normal text-slate-300">€</span>`;
            document.getElementById('res-sucata-furo').innerText = `${valorSucataFuroEur.toFixed(2)} € / furo`;

            document.getElementById('res-custo-total').innerHTML = `${custoMaqLote.toFixed(2)} € <span class="text-[10px] font-normal text-slate-300" id="res-custo-furo">(${custoMaqFuro.toFixed(2)} €/furo)</span>`;
            document.getElementById('res-custo-hora-ref').innerText = `${custoHora.toFixed(2)} €/h`;
            document.getElementById('res-forca').innerHTML = `${Math.round(forcaFf)} <span class="text-sm font-normal text-slate-300">N</span>`;
            document.getElementById('res-forca-kgf').innerText = `${forcaKgf.toFixed(1)} kgf`;
            document.getElementById('res-binario-card').innerHTML = `${binarioMc.toFixed(1)} <span class="text-sm font-normal text-slate-300">N·m</span>`;

            const tbody = document.getElementById('tabela-ref');
            tbody.innerHTML = '';
            const diametrosCat = toolData.diametros;
            const fCatArr = grupoObj.f;

            diametrosCat.forEach((d, i) => {
                const fCatVal = fCatArr[i];
                const nCat = d > 0 ? Math.round((vcFinal * 1000) / (Math.PI * d)) : 0;
                const vfCat = Math.round(fCatVal * nCat);

                const tr = document.createElement('tr');
                if (i === m.idxInf) {
                    tr.className = "bg-blue-900/30 text-blue-200 font-semibold";
                }
                tr.innerHTML = `
                    <td class="py-1">${d.toFixed(2)}</td>
                    <td class="py-1">${fCatVal.toFixed(3)}</td>
                    <td class="py-1">${nCat}</td>
                    <td class="py-1">${vfCat}</td>
                `;
                tbody.appendChild(tr);
            });

            atualizarGraficoSVG(diametrosCat, fCatArr, diametro, fFinal);

            cacheResultados = {
                linhaNome: document.getElementById('linha').options[document.getElementById('linha').selectedIndex].text,
                categoriaNome: document.getElementById('categoria').options[document.getElementById('categoria').selectedIndex].text,
                brocaNome: toolData.nome,
                varianteKey,
                limiteNominalMm: maxNominalProf,
                l3Ref,
                referenciaCatalogo: referenciaAtivaObj,
                grupoKey,
                grupoEfetivoKey,
                grupoNome: toolData.gruposNames[grupoEfetivoKey],
                ligaAplicada: ligaCheck,
                refrigNome: refrigAtual.toUpperCase(),
                diametro,
                profundidade,
                qtdFuros,
                densidade,
                precoSucataKg,
                custoHora,
                peckingCheck,
                peckingDesc: peckingCheck ? `Sim (Q = ${peckingInputVal.toFixed(1)} ${peckingUnid === 'xd' ? '×D' : 'mm'} / ${passoMm.toFixed(1)} mm, ${numPassos} passos, retração ${peckingRetensaoVal} mm/min)` : 'Não',
                vcPct,
                fPct,
                vcFinal,
                fFinal,
                n,
                vf,
                tempoFuroSeg,
                tempoTotalMin,
                metragemTotalM,
                volumeTotalCm3,
                taxaRemocaoCm3Min,
                massaFuroG,
                pesoTotalKg,
                valorSucataTotalEur,
                valorSucataFuroEur,
                custoMaqFuro,
                custoMaqLote,
                forcaFf,
                forcaKgf,
                binarioMc,
                potenciaReqKw,
                potMaxKw,
                binMaxNm,
                alertaSobrecargaTexto,
                estadoTexto
            };

            if (!document.getElementById('modal-comparacao').classList.contains('hidden') || !document.getElementById('modal-resultado-comparacao').classList.contains('hidden')) {
                atualizarComparacao();
            }
        }

        function atualizarGraficoSVG(diametrosCat, fCatArr, dCalc, fCalc) {
            const svg = document.getElementById('svg-grafico');
            svg.innerHTML = '';

            const width = 400;
            const height = 180;
            const padLeft = 40;
            const padRight = 20;
            const padTop = 20;
            const padBottom = 30;

            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;

            const allX = [...diametrosCat, dCalc];
            const allY = [...fCatArr, fCalc];

            let minX = Math.min(...allX);
            let maxX = Math.max(...allX);
            let minY = Math.min(...allY) * 0.85;
            let maxY = Math.max(...allY) * 1.1;

            if (minX === maxX) { minX -= 1; maxX += 1; }
            if (minY === maxY) { minY -= 0.1; maxY += 0.1; }

            const getX = (x) => padLeft + ((x - minX) / (maxX - minX)) * plotW;
            const getY = (y) => padTop + plotH - ((y - minY) / (maxY - minY)) * plotH;

            for (let i = 0; i <= 4; i++) {
                const yVal = minY + (i / 4) * (maxY - minY);
                const yPos = getY(yVal);
                
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", padLeft);
                line.setAttribute("y1", yPos);
                line.setAttribute("x2", width - padRight);
                line.setAttribute("y2", yPos);
                line.setAttribute("stroke", "#334155");
                line.setAttribute("stroke-width", "1");
                svg.appendChild(line);

                const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.setAttribute("x", padLeft - 5);
                text.setAttribute("y", yPos + 3);
                text.setAttribute("fill", "#94a3b8");
                text.setAttribute("font-size", "9");
                text.setAttribute("text-anchor", "end");
                text.textContent = yVal.toFixed(2);
                svg.appendChild(text);
            }

            const xAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
            xAxis.setAttribute("x1", padLeft);
            xAxis.setAttribute("y1", padTop + plotH);
            xAxis.setAttribute("x2", width - padRight);
            xAxis.setAttribute("y2", padTop + plotH);
            xAxis.setAttribute("stroke", "#64748b");
            xAxis.setAttribute("stroke-width", "1.5");
            svg.appendChild(xAxis);

            for (let i = 0; i <= 4; i++) {
                const xVal = minX + (i / 4) * (maxX - minX);
                const xPos = getX(xVal);
                const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.setAttribute("x", xPos);
                text.setAttribute("y", padTop + plotH + 14);
                text.setAttribute("fill", "#94a3b8");
                text.setAttribute("font-size", "9");
                text.setAttribute("text-anchor", "middle");
                text.textContent = xVal.toFixed(1);
                svg.appendChild(text);
            }

            let pathD = "";
            diametrosCat.forEach((d, idx) => {
                const px = getX(d);
                const py = getY(fCatArr[idx]);
                pathD += (idx === 0 ? "M " : " L ") + `${px} ${py}`;
            });

            const pathEl = document.createElementNS("http://www.w3.org/2000/svg", "path");
            pathEl.setAttribute("d", pathD);
            pathEl.setAttribute("fill", "none");
            pathEl.setAttribute("stroke", "#3b82f6");
            pathEl.setAttribute("stroke-width", "2.5");
            svg.appendChild(pathEl);

            diametrosCat.forEach((d, idx) => {
                const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                circle.setAttribute("cx", getX(d));
                circle.setAttribute("cy", getY(fCatArr[idx]));
                circle.setAttribute("r", "3.5");
                circle.setAttribute("fill", "#3b82f6");
                svg.appendChild(circle);
            });

            const calcCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            calcCircle.setAttribute("cx", getX(dCalc));
            calcCircle.setAttribute("cy", getY(fCalc));
            calcCircle.setAttribute("r", "5.5");
            calcCircle.setAttribute("fill", "#f97316");
            calcCircle.setAttribute("stroke", "#ffffff");
            calcCircle.setAttribute("stroke-width", "1.5");
            svg.appendChild(calcCircle);
        }

        function abrirModalComparacao() {
            if (!isProMode) {
                gerirModoPro();
                return;
            }
            const ctx = lerContextoAtual();
            document.getElementById('comp-custo-hora').value = ctx.custoHora.toFixed(2);

            const selectComp = document.getElementById('comp-ferramenta');
            selectComp.innerHTML = '';

            const optManual = document.createElement('option');
            optManual.value = '__manual_cliente__';
            optManual.text = "🛠️ Ferramenta do Cliente (Vc & f manuais)";
            selectComp.appendChild(optManual);

            const grupoEfetivo = ctx.grupoEfetivoKey;
            let primeiraCompat = null;

            for (const key in dados) {
                if (key === ctx.brocaKey) continue;
                const tool = dados[key];
                if (tool.grupos[grupoEfetivo]) {
                    const opt = document.createElement('option');
                    opt.value = key;
                    opt.text = `${tool.nome} (${key.toUpperCase()})`;
                    selectComp.appendChild(opt);
                    if (!primeiraCompat) primeiraCompat = key;
                }
            }

            if (primeiraCompat) {
                selectComp.value = primeiraCompat;
            } else {
                selectComp.value = '__manual_cliente__';
            }

            onChangeFonteComparacao();
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function fecharModalComparacao() {
            document.getElementById('modal-comparacao').classList.add('hidden');
        }

        function abrirJanelaResultadoComparacao() {
            atualizarComparacao();
            fecharModalComparacao();
            document.getElementById('comp-incluir-pdf-res').checked = document.getElementById('comp-incluir-pdf').checked;
            document.getElementById('modal-resultado-comparacao').classList.remove('hidden');
        }

        function fecharJanelaResultadoComparacao() {
            document.getElementById('modal-resultado-comparacao').classList.add('hidden');
        }

        function voltarParaInputsComparacao() {
            fecharJanelaResultadoComparacao();
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function onChangeFonteComparacao() {
            const fonteKey = document.getElementById('comp-ferramenta').value;
            const blocoCliente = document.getElementById('comp-bloco-cliente');
            const blocoVariante = document.getElementById('comp-bloco-variante');
            const selectVar = document.getElementById('comp-variante');

            if (fonteKey === '__manual_cliente__') {
                blocoCliente.classList.remove('hidden');
                blocoVariante.classList.add('hidden');
            } else {
                blocoCliente.classList.add('hidden');
                blocoVariante.classList.remove('hidden');
                const toolAlvo = dados[fonteKey];
                selectVar.innerHTML = '';
                if (toolAlvo && toolAlvo.variantes) {
                    Object.keys(toolAlvo.variantes).forEach(vk => {
                        const opt = document.createElement('option');
                        opt.value = vk;
                        opt.text = vk;
                        selectVar.appendChild(opt);
                    });
                }
            }
            atualizarComparacao();
        }

        function sincronizarCustoHoraComparacao() {
            const val = parseFloat(document.getElementById('comp-custo-hora').value);
            if (!isNaN(val) && val > 0) {
                document.getElementById('custo-hora').value = val.toFixed(2);
                atualizarCalculo();
            }
            atualizarComparacao();
        }

        function renderGraficoBarrasComparacao(svgId, labelA, valA, colorA, labelB, valB, colorB, unitSuffix) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            svg.innerHTML = '';

            const W = 300, H = 175;
            const padL = 42, padR = 16, padT = 22, padB = 28;
            const plotW = W - padL - padR;
            const plotH = H - padT - padB;

            const maxVal = Math.max(valA, valB, 0.01) * 1.22;
            const fmtTick = (v) => {
                if (maxVal >= 100) return v.toFixed(0);
                if (maxVal >= 10) return v.toFixed(1);
                return v.toFixed(2);
            };

            for (let i = 0; i <= 3; i++) {
                const tVal = (maxVal / 3) * i;
                const y = padT + plotH - (tVal / maxVal) * plotH;

                const grid = document.createElementNS("http://www.w3.org/2000/svg", "line");
                grid.setAttribute("x1", padL);
                grid.setAttribute("y1", y);
                grid.setAttribute("x2", W - padR);
                grid.setAttribute("y2", y);
                grid.setAttribute("stroke", "#1e293b");
                grid.setAttribute("stroke-width", "1");
                svg.appendChild(grid);

                const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
                lbl.setAttribute("x", padL - 5);
                lbl.setAttribute("y", y + 3);
                lbl.setAttribute("fill", "#64748b");
                lbl.setAttribute("font-size", "8.5");
                lbl.setAttribute("text-anchor", "end");
                lbl.textContent = fmtTick(tVal);
                svg.appendChild(lbl);
            }

            const axisX = document.createElementNS("http://www.w3.org/2000/svg", "line");
            axisX.setAttribute("x1", padL);
            axisX.setAttribute("y1", padT + plotH);
            axisX.setAttribute("x2", W - padR);
            axisX.setAttribute("y2", padT + plotH);
            axisX.setAttribute("stroke", "#475569");
            axisX.setAttribute("stroke-width", "1.2");
            svg.appendChild(axisX);

            const itens = [
                { label: labelA, val: valA, color: colorA },
                { label: labelB, val: valB, color: colorB }
            ];

            const colW = plotW / 2;
            const barW = Math.min(54, colW * 0.45);

            itens.forEach((it, idx) => {
                const cx = padL + colW * idx + colW / 2;
                const hBar = Math.max(2, (it.val / maxVal) * plotH);
                const yBar = padT + plotH - hBar;

                const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                rect.setAttribute("x", cx - barW / 2);
                rect.setAttribute("y", yBar);
                rect.setAttribute("width", barW);
                rect.setAttribute("height", hBar);
                rect.setAttribute("rx", "4");
                rect.setAttribute("fill", it.color);
                svg.appendChild(rect);

                const vTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                vTxt.setAttribute("x", cx);
                vTxt.setAttribute("y", Math.max(12, yBar - 5));
                vTxt.setAttribute("fill", "#f8fafc");
                vTxt.setAttribute("font-size", "9.5");
                vTxt.setAttribute("font-weight", "bold");
                vTxt.setAttribute("text-anchor", "middle");
                vTxt.textContent = `${fmtTick(it.val)}${unitSuffix}`;
                svg.appendChild(vTxt);

                const xTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                xTxt.setAttribute("x", cx);
                xTxt.setAttribute("y", padT + plotH + 13);
                xTxt.setAttribute("fill", "#cbd5e1");
                xTxt.setAttribute("font-size", "9");
                xTxt.setAttribute("text-anchor", "middle");
                xTxt.textContent = it.label;
                svg.appendChild(xTxt);
            });
        }

        function renderGraficoBreakEven(svgId, qtdFuros, custoFixoA, custoVarA, custoFixoB, custoVarB, beFuros) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            svg.innerHTML = '';

            const W = 300, H = 175;
            const padL = 42, padR = 14, padT = 18, padB = 28;
            const plotW = W - padL - padR;
            const plotH = H - padT - padB;

            const nFuros = Math.max(1, qtdFuros);
            const passos = 25;
            const ptsA = [];
            const ptsB = [];
            let maxY = Math.max(custoFixoA, custoFixoB, 1);

            for (let i = 0; i <= passos; i++) {
                const q = (nFuros * i) / passos;
                const yA = custoFixoA + custoVarA * q;
                const yB = custoFixoB + custoVarB * q;
                ptsA.push({ q, y: yA });
                ptsB.push({ q, y: yB });
                if (yA > maxY) maxY = yA;
                if (yB > maxY) maxY = yB;
            }
            maxY *= 1.12;

            const getX = (q) => padL + (q / nFuros) * plotW;
            const getY = (y) => padT + plotH - (y / maxY) * plotH;

            for (let i = 0; i <= 3; i++) {
                const tVal = (maxY / 3) * i;
                const y = getY(tVal);
                const grid = document.createElementNS("http://www.w3.org/2000/svg", "line");
                grid.setAttribute("x1", padL);
                grid.setAttribute("y1", y);
                grid.setAttribute("x2", W - padR);
                grid.setAttribute("y2", y);
                grid.setAttribute("stroke", "#1e293b");
                grid.setAttribute("stroke-width", "1");
                svg.appendChild(grid);

                const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
                lbl.setAttribute("x", padL - 5);
                lbl.setAttribute("y", y + 3);
                lbl.setAttribute("fill", "#64748b");
                lbl.setAttribute("font-size", "8.5");
                lbl.setAttribute("text-anchor", "end");
                lbl.textContent = `${tVal.toFixed(0)}€`;
                svg.appendChild(lbl);
            }

            const axisX = document.createElementNS("http://www.w3.org/2000/svg", "line");
            axisX.setAttribute("x1", padL);
            axisX.setAttribute("y1", padT + plotH);
            axisX.setAttribute("x2", W - padR);
            axisX.setAttribute("y2", padT + plotH);
            axisX.setAttribute("stroke", "#475569");
            axisX.setAttribute("stroke-width", "1.2");
            svg.appendChild(axisX);

            const dA = ptsA.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(p.q).toFixed(1)} ${getY(p.y).toFixed(1)}`).join(' ');
            const dB = ptsB.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(p.q).toFixed(1)} ${getY(p.y).toFixed(1)}`).join(' ');

            const pathA = document.createElementNS("http://www.w3.org/2000/svg", "path");
            pathA.setAttribute("d", dA);
            pathA.setAttribute("fill", "none");
            pathA.setAttribute("stroke", "#38bdf8");
            pathA.setAttribute("stroke-width", "2.2");
            svg.appendChild(pathA);

            const pathB = document.createElementNS("http://www.w3.org/2000/svg", "path");
            pathB.setAttribute("d", dB);
            pathB.setAttribute("fill", "none");
            pathB.setAttribute("stroke", "#fbbf24");
            pathB.setAttribute("stroke-width", "2.2");
            svg.appendChild(pathB);

            if (beFuros !== null && isFinite(beFuros) && beFuros > 0 && beFuros <= nFuros) {
                const yBe = custoFixoA + custoVarA * beFuros;
                const cx = getX(beFuros);
                const cy = getY(yBe);

                const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                dot.setAttribute("cx", cx);
                dot.setAttribute("cy", cy);
                dot.setAttribute("r", "4");
                dot.setAttribute("fill", "#34d399");
                dot.setAttribute("stroke", "#0f172a");
                dot.setAttribute("stroke-width", "1.2");
                svg.appendChild(dot);

                const beTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                beTxt.setAttribute("x", Math.min(W - padR - 24, Math.max(padL + 20, cx)));
                beTxt.setAttribute("y", Math.max(12, cy - 7));
                beTxt.setAttribute("fill", "#6ee7b7");
                beTxt.setAttribute("font-size", "8.5");
                beTxt.setAttribute("font-weight", "bold");
                beTxt.setAttribute("text-anchor", "middle");
                beTxt.textContent = `BE ~${Math.ceil(beFuros)}f`;
                svg.appendChild(beTxt);
            }

            [0, 0.5, 1].forEach(frac => {
                const qVal = Math.round(nFuros * frac);
                const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
                t.setAttribute("x", getX(qVal));
                t.setAttribute("y", padT + plotH + 13);
                t.setAttribute("fill", "#94a3b8");
                t.setAttribute("font-size", "8.5");
                t.setAttribute("text-anchor", "middle");
                t.textContent = `${qVal}f`;
                svg.appendChild(t);
            });
        }

        function atualizarComparacao() {
            const ctx = lerContextoAtual();
            const fonteKey = document.getElementById('comp-ferramenta').value;
            const esManualCliente = fonteKey === '__manual_cliente__';
            const varAlvoKey = document.getElementById('comp-variante').value || ctx.varianteKey;
            const grupoEfetivo = ctx.grupoEfetivoKey;

            const avisoEl = document.getElementById('comp-aviso-grupo');
            const btnUsar = document.getElementById('btn-usar-comparada');
            const thAlvo = document.getElementById('comp-th-alvo');
            const subtituloRes = document.getElementById('res-comp-subtitulo');

            const requerPiloto = esManualCliente && document.getElementById('comp-requer-piloto').checked;
            const tempoPilotoSeg = requerPiloto ? (parseFloat(document.getElementById('comp-tempo-piloto-seg').value) || 0) : 0;
            const custoPilotoFuro = requerPiloto ? (parseFloat(document.getElementById('comp-custo-piloto-furo').value) || 0) : 0;
            const usaBrocaCanhao = requerPiloto && document.getElementById('comp-usa-broca-canhao').checked;
            const tempoParagemAfiMin = usaBrocaCanhao ? (parseFloat(document.getElementById('comp-tempo-paragem-afi-min').value) || 0) : 0;

            const mAtual = calcularMetricasFerramenta(ctx.brocaKey, ctx.varianteKey, grupoEfetivo, ctx);
            if (!mAtual) return;

            let mAlvo = null;
            let nomeAlvo = "";
            let varAlvoLabel = "";

            const precoAtual = Math.max(0, parseFloat(document.getElementById('comp-preco-atual').value) || 0);
            const vidaAtual = Math.max(1, parseFloat(document.getElementById('comp-vida-atual').value) || 1);
            const vidaUnidAtual = document.getElementById('comp-vida-unid-atual').value;
            const afiQtdAtual = Math.max(0, parseInt(document.getElementById('comp-afi-qtd-atual').value) || 0);
            const afiCustoAtual = Math.max(0, parseFloat(document.getElementById('comp-afi-custo-atual').value) || 0);

            const precoAlvo = Math.max(0, parseFloat(document.getElementById('comp-preco-alvo').value) || 0);
            const vidaAlvo = Math.max(1, parseFloat(document.getElementById('comp-vida-alvo').value) || 1);
            const vidaUnidAlvo = document.getElementById('comp-vida-unid-alvo').value;
            const afiQtdAlvo = Math.max(0, parseInt(document.getElementById('comp-afi-qtd-alvo').value) || 0);
            const afiCustoAlvo = Math.max(0, parseFloat(document.getElementById('comp-afi-custo-alvo').value) || 0);

            const profMetros = Math.max(0.001, ctx.profundidade / 1000);
            const furosPorAfiaçãoAtual = vidaUnidAtual === 'metros' ? Math.max(1, vidaAtual / profMetros) : vidaAtual;
            const furosPorAfiaçãoAlvo = vidaUnidAlvo === 'metros' ? Math.max(1, vidaAlvo / profMetros) : vidaAlvo;

            const totalUsosAtual = 1 + afiQtdAtual;
            const custoTotalFerramentaCicloAtual = precoAtual + (afiQtdAtual * afiCustoAtual);
            const furosTotaisCicloAtual = furosPorAfiaçãoAtual * totalUsosAtual;
            const custoFerramentaFuroAtual = custoTotalFerramentaCicloAtual / furosTotaisCicloAtual;

            const totalUsosAlvo = 1 + afiQtdAlvo;
            const custoTotalFerramentaCicloAlvo = precoAlvo + (afiQtdAlvo * afiCustoAlvo);
            const furosTotaisCicloAlvo = furosPorAfiaçãoAlvo * totalUsosAlvo;
            const custoFerramentaFuroAlvo = custoTotalFerramentaCicloAlvo / furosTotaisCicloAlvo;

            const canhaoResumoEl = document.getElementById('comp-canhao-resumo');
            if (canhaoResumoEl) {
                const nParagensPrev = Math.floor(Math.max(0, ctx.qtdFuros - 1) / Math.max(1, furosPorAfiaçãoAlvo));
                const minParagensPrev = nParagensPrev * tempoParagemAfiMin;
                canhaoResumoEl.innerText = `${nParagensPrev} paragens · +${minParagensPrev.toFixed(1)} min`;
            }

            const equivContinuoEl = document.getElementById('comp-equiv-continuo');
            const inputMetrosContinuo = document.getElementById('comp-metros-continuo');
            let metrosContinuo = 90;
            if (corteInterrompidoAtivo && inputMetrosContinuo) {
                metrosContinuo = Math.max(1, parseFloat(inputMetrosContinuo.value) || 90);
                if (equivContinuoEl) {
                    const furosEquiv = Math.round(metrosContinuo / profMetros);
                    equivContinuoEl.innerText = `(~${furosEquiv} furos em corte contínuo)`;
                }
            }

            if (esManualCliente) {
                const nomeCli = (document.getElementById('comp-cliente-nome').value || '').trim() || "Ferramenta do Cliente";
                const vcCli = parseFloat(document.getElementById('comp-cliente-vc').value) || 70;
                const fCli = parseFloat(document.getElementById('comp-cliente-f').value) || 0.02;

                mAlvo = calcularMetricasManualCliente(nomeCli, vcCli, fCli, grupoEfetivo, {
                    ...ctx,
                    requerPiloto,
                    tempoPilotoSeg,
                    custoPilotoFuro,
                    usaBrocaCanhao,
                    tempoParagemAfiMin,
                    furosPorAfiação: furosPorAfiaçãoAlvo
                });
                nomeAlvo = mAlvo.nome;
                varAlvoLabel = "Manual";
                avisoEl.classList.add('hidden');
                btnUsar.disabled = true;
                btnUsar.className = "bg-slate-700 text-slate-500 cursor-not-allowed px-3 py-1.5 rounded-md text-xs font-semibold";
            } else {
                const toolAlvo = dados[fonteKey];
                if (!toolAlvo || !toolAlvo.grupos[grupoEfetivo]) return;
                mAlvo = calcularMetricasFerramenta(fonteKey, varAlvoKey, grupoEfetivo, ctx);
                if (!mAlvo) return;
                nomeAlvo = toolAlvo.nome;
                varAlvoLabel = varAlvoKey;
                avisoEl.classList.add('hidden');
                btnUsar.disabled = false;
                btnUsar.className = "bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded-md text-xs font-semibold text-white transition";
            }

            thAlvo.innerText = `${nomeAlvo} (${varAlvoLabel})`;
            subtituloRes.innerText = `${mAtual.nome} (${ctx.varianteKey})  vs.  ${nomeAlvo} (${varAlvoLabel}) · Grupo ${grupoEfetivo} · Ø ${ctx.diametro.toFixed(2)} mm · Lote ${ctx.qtdFuros} furos`;

            const custoFerramentaLoteAtual = custoFerramentaFuroAtual * ctx.qtdFuros;
            const custoFerramentaLoteAlvo = custoFerramentaFuroAlvo * ctx.qtdFuros;
            const custoPilotoLoteAlvo = mAlvo.custoPilotoLote || 0;
            const custoPilotoFuroAlvo = mAlvo.custoPilotoEfetivo || 0;

            const custoTotalAtual = mAtual.custoMaqLote + custoFerramentaLoteAtual;
            const custoTotalAlvo = mAlvo.custoMaqLote + custoFerramentaLoteAlvo + custoPilotoLoteAlvo;

            const custoTotalFuroAtual = ctx.qtdFuros > 0 ? custoTotalAtual / ctx.qtdFuros : 0;
            const custoTotalFuroAlvo = ctx.qtdFuros > 0 ? custoTotalAlvo / ctx.qtdFuros : 0;

            const ganhoTempoMin = mAlvo.tempoTotalMin - mAtual.tempoTotalMin;
            const ganhoCustoEur = custoTotalAlvo - custoTotalAtual;

            const pctTempo = mAlvo.tempoTotalMin > 0 ? ((ganhoTempoMin / mAlvo.tempoTotalMin) * 100) : 0;
            const pctCusto = custoTotalAlvo > 0 ? ((ganhoCustoEur / custoTotalAlvo) * 100) : 0;

            const varMaqFuro = mAlvo.custoMaqFuro - mAtual.custoMaqFuro;
            const varFerrFuro = custoFerramentaFuroAlvo - custoFerramentaFuroAtual;
            const varTotalFuro = varMaqFuro + varFerrFuro - custoPilotoFuroAlvo;
            const diffFixo = custoTotalFerramentaCicloAtual - custoTotalFerramentaCicloAlvo;

            let breakevenTexto = "";
            let beFurosNum = null;
            if (diffFixo <= 0 && varTotalFuro >= 0) {
                breakevenTexto = "MAPAL mais vantajosa desde o 1.º furo (menor custo inicial e por furo).";
            } else if (diffFixo > 0 && varTotalFuro > 0) {
                const furosBe = diffFixo / varTotalFuro;
                beFurosNum = furosBe;
                const metrosBe = furosBe * profMetros;
                breakevenTexto = `Equilíbrio em ~${Math.ceil(furosBe)} furos (${metrosBe.toFixed(1)} m). No lote de ${ctx.qtdFuros} furos, poupança líquida de ${ganhoCustoEur.toFixed(2)} €.`;
            } else if (diffFixo < 0 && varTotalFuro < 0) {
                const furosBe = Math.abs(diffFixo) / Math.abs(varTotalFuro);
                beFurosNum = furosBe;
                breakevenTexto = `Ferramenta comparada recupera investimento inicial em ~${Math.ceil(furosBe)} furos.`;
            } else {
                breakevenTexto = `Sem ponto de equilíbrio no intervalo atual (variação por furo: ${varTotalFuro >= 0 ? '+' : ''}${varTotalFuro.toFixed(3)} €/furo).`;
            }

            let capTexto = `MAPAL: ${mAtual.vf} mm/min (${mAtual.tempoFuroSeg.toFixed(1)} s/furo) vs. Comparada: ${mAlvo.vf} mm/min (${mAlvo.tempoFuroSeg.toFixed(1)} s/furo)`;
            if (requerPiloto) {
                capTexto += ` · Piloto +${tempoPilotoSeg.toFixed(0)} s/furo`;
            }
            if (mAlvo.canhaoAtivo) {
                capTexto += ` · Canhão: ${mAlvo.numParagensLote} paragens (+${mAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min)`;
            }
            if (corteInterrompidoAtivo) {
                capTexto += ` · Corte interrompido (ref. ${metrosContinuo.toFixed(0)} m contínuos)`;
            }

            document.getElementById('comp-capacidade-texto').innerText = capTexto;
            document.getElementById('comp-breakeven-texto').innerText = breakevenTexto;

            const resumoDestaqueEl = document.getElementById('comp-resumo-lote-destaque');
            if (ganhoCustoEur >= 0) {
                resumoDestaqueEl.innerHTML = `<span class="text-emerald-400 font-bold">Poupança de ${ganhoCustoEur.toFixed(2)} € (${pctCusto.toFixed(1)}%)</span> · <span class="text-cyan-300 font-semibold">${ganhoTempoMin.toFixed(1)} min (${pctTempo.toFixed(1)}%)</span>`;
            } else {
                resumoDestaqueEl.innerHTML = `<span class="text-rose-400 font-bold">Custo superior em ${Math.abs(ganhoCustoEur).toFixed(2)} €</span> · Tempo: ${ganhoTempoMin >= 0 ? '-' : '+'}${Math.abs(ganhoTempoMin).toFixed(1)} min`;
            }

            renderGraficoBarrasComparacao('svg-comp-custo', 'MAPAL', custoTotalAtual, '#3b82f6', 'Comparada', custoTotalAlvo, '#f43f5e', '€');
            renderGraficoBarrasComparacao('svg-comp-tempo', 'MAPAL', mAtual.tempoTotalMin, '#10b981', 'Comparada', mAlvo.tempoTotalMin, '#f59e0b', 'm');
            renderGraficoBreakEven('svg-comp-breakeven', ctx.qtdFuros, custoTotalFerramentaCicloAtual, mAtual.custoMaqFuro + custoFerramentaFuroAtual, custoTotalFerramentaCicloAlvo, mAlvo.custoMaqFuro + custoFerramentaFuroAlvo + custoPilotoFuroAlvo, beFurosNum);

            const tbody = document.getElementById('comp-tabela-corpo');
            tbody.innerHTML = '';

            const fmtVida = (val, unid) => unid === 'metros' ? `${val} m (~${Math.max(1, Math.round(val / profMetros))} furos)` : `${val} furos`;

            const linhas = [
                {
                    label: "Velocidade de Corte (Vc)",
                    vAtual: `${mAtual.vcFinal.toFixed(1)} m/min`,
                    vAlvo: `${mAlvo.vcFinal.toFixed(1)} m/min`,
                    diff: `${(mAtual.vcFinal - mAlvo.vcFinal) >= 0 ? '+' : ''}${(mAtual.vcFinal - mAlvo.vcFinal).toFixed(1)} m/min`
                },
                {
                    label: "Avanço por Rotação (f)",
                    vAtual: `${mAtual.fFinal.toFixed(4)} mm/rot`,
                    vAlvo: `${mAlvo.fFinal.toFixed(4)} mm/rot`,
                    diff: `${(mAtual.fFinal - mAlvo.fFinal) >= 0 ? '+' : ''}${(mAtual.fFinal - mAlvo.fFinal).toFixed(4)} mm/rot`
                },
                {
                    label: "Avanço de Trabalho (vf)",
                    vAtual: `${mAtual.vf} mm/min`,
                    vAlvo: `${mAlvo.vf} mm/min`,
                    diff: `${(mAtual.vf - mAlvo.vf) >= 0 ? '+' : ''}${mAtual.vf - mAlvo.vf} mm/min`
                },
                {
                    label: "Vida por Afiação",
                    vAtual: fmtVida(vidaAtual, vidaUnidAtual),
                    vAlvo: fmtVida(vidaAlvo, vidaUnidAlvo),
                    diff: `${Math.round(furosPorAfiaçãoAtual)} vs. ${Math.round(furosPorAfiaçãoAlvo)} furos/af.`
                },
                {
                    label: "Reafiações / Preço / Afiação",
                    vAtual: `${afiQtdAtual}× · ${precoAtual.toFixed(0)}€ · ${afiCustoAtual.toFixed(0)}€/af.`,
                    vAlvo: `${afiQtdAlvo}× · ${precoAlvo.toFixed(0)}€ · ${afiCustoAlvo.toFixed(0)}€/af.`,
                    diff: `Ciclo: ${custoTotalFerramentaCicloAtual.toFixed(0)}€ vs. ${custoTotalFerramentaCicloAlvo.toFixed(0)}€`
                },
                ...(requerPiloto ? [{
                    label: "Furo-Piloto / Broca Canhão",
                    vAtual: "Não requer",
                    vAlvo: mAlvo.canhaoAtivo
                        ? `+${tempoPilotoSeg.toFixed(0)}s + ${mAlvo.numParagensLote} paragens (${mAlvo.tempoParagemCanhaoLoteMin.toFixed(1)}m) + ${custoPilotoFuroAlvo.toFixed(2)}€/f`
                        : `+${tempoPilotoSeg.toFixed(0)} s/furo + ${custoPilotoFuroAlvo.toFixed(2)} €/furo`,
                    diff: `Tempo extra lote: +${(mAlvo.tempoPilotoLoteMin + mAlvo.tempoParagemCanhaoLoteMin).toFixed(1)} min`
                }] : []),
                {
                    label: "Tempo por Furo",
                    vAtual: `${mAtual.tempoFuroSeg.toFixed(1)} s`,
                    vAlvo: `${mAlvo.tempoFuroSeg.toFixed(1)} s`,
                    diff: `${(mAtual.tempoFuroSeg - mAlvo.tempoFuroSeg) <= 0 ? '' : '+'}${(mAtual.tempoFuroSeg - mAlvo.tempoFuroSeg).toFixed(1)} s/furo`
                },
                {
                    label: "Tempo Total no Lote",
                    vAtual: `${mAtual.tempoTotalMin.toFixed(1)} min`,
                    vAlvo: `${mAlvo.tempoTotalMin.toFixed(1)} min`,
                    diff: `${ganhoTempoMin >= 0 ? '-' : '+'}${Math.abs(ganhoTempoMin).toFixed(1)} min (${pctTempo >= 0 ? '-' : '+'}${Math.abs(pctTempo).toFixed(1)}%)`
                },
                {
                    label: "Custo Ferramenta / Furo",
                    vAtual: `${custoFerramentaFuroAtual.toFixed(3)} €`,
                    vAlvo: `${custoFerramentaFuroAlvo.toFixed(3)} €`,
                    diff: `${(custoFerramentaFuroAtual - custoFerramentaFuroAlvo) <= 0 ? '' : '+'}${(custoFerramentaFuroAtual - custoFerramentaFuroAlvo).toFixed(3)} €/furo`
                },
                {
                    label: "Custo Total / Furo (Máq. + Ferr." + (requerPiloto ? " + Piloto" : "") + ")",
                    vAtual: `${custoTotalFuroAtual.toFixed(2)} €`,
                    vAlvo: `${custoTotalFuroAlvo.toFixed(2)} €`,
                    diff: `${(custoTotalFuroAtual - custoTotalFuroAlvo) <= 0 ? '' : '+'}${(custoTotalFuroAtual - custoTotalFuroAlvo).toFixed(2)} €/furo`
                },
                {
                    label: "Custo Total no Lote",
                    vAtual: `${custoTotalAtual.toFixed(2)} €`,
                    vAlvo: `${custoTotalAlvo.toFixed(2)} €`,
                    diff: `${ganhoCustoEur >= 0 ? '-' : '+'}${Math.abs(ganhoCustoEur).toFixed(2)} € (${pctCusto >= 0 ? '-' : '+'}${Math.abs(pctCusto).toFixed(1)}%)`
                },
                {
                    label: "Força Axial (Ff)",
                    vAtual: `${Math.round(mAtual.forcaFf)} N`,
                    vAlvo: `${Math.round(mAlvo.forcaFf)} N`,
                    diff: `${(mAtual.forcaFf - mAlvo.forcaFf) >= 0 ? '+' : ''}${Math.round(mAtual.forcaFf - mAlvo.forcaFf)} N`
                },
                {
                    label: "Binário / Potência Req.",
                    vAtual: `${mAtual.binarioMc.toFixed(1)} N·m / ${mAtual.potenciaReqKw.toFixed(2)} kW`,
                    vAlvo: `${mAlvo.binarioMc.toFixed(1)} N·m / ${mAlvo.potenciaReqKw.toFixed(2)} kW`,
                    diff: `${(mAtual.potenciaReqKw - mAlvo.potenciaReqKw) >= 0 ? '+' : ''}${(mAtual.potenciaReqKw - mAlvo.potenciaReqKw).toFixed(2)} kW`
                }
            ];

            linhas.forEach(l => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="py-1.5 px-3 font-medium text-slate-300">${l.label}</td>
                    <td class="py-1.5 px-3 text-white font-semibold">${l.vAtual}</td>
                    <td class="py-1.5 px-3 text-slate-200">${l.vAlvo}</td>
                    <td class="py-1.5 px-3 font-bold text-amber-300">${l.diff}</td>
                `;
                tbody.appendChild(tr);
            });

            cacheComparacao = {
                nomeAtual: `${mAtual.nome} (${ctx.varianteKey})`,
                nomeAlvo: `${nomeAlvo} (${varAlvoLabel})`,
                esManualCliente,
                requerPiloto,
                tempoPilotoSeg,
                custoPilotoFuro: custoPilotoFuroAlvo,
                usaBrocaCanhao: mAlvo.canhaoAtivo,
                numParagensLote: mAlvo.numParagensLote,
                tempoParagemCanhaoLoteMin: mAlvo.tempoParagemCanhaoLoteMin,
                corteInterrompidoAtivo,
                metrosContinuo,
                vidaAtual,
                vidaUnidAtual,
                vidaAlvo,
                vidaUnidAlvo,
                afiQtdAtual,
                afiCustoAtual,
                afiQtdAlvo,
                afiCustoAlvo,
                custoFerramentaFuroAtual,
                custoFerramentaFuroAlvo,
                custoTotalFuroAtual,
                custoTotalFuroAlvo,
                custoTotalAtual,
                custoTotalAlvo,
                ganhoTempoMin,
                ganhoCustoEur,
                pctTempo,
                pctCusto,
                breakevenTexto,
                linhas
            };
        }

        function aplicarFerramentaComparada() {
            const fonteKey = document.getElementById('comp-ferramenta').value;
            if (!fonteKey || fonteKey === '__manual_cliente__' || !dados[fonteKey]) return;

            const toolAlvo = dados[fonteKey];
            const varAlvoKey = document.getElementById('comp-variante').value;
            document.getElementById('linha').value = toolAlvo.linha;
            document.getElementById('categoria').value = toolAlvo.categoria;
            document.getElementById('filtro-refrig').value = toolAlvo.temRefrigInt ? 'com' : 'sem';
            atualizarFiltroBrocas(true);
            document.getElementById('broca').value = fonteKey;
            mudarBroca(varAlvoKey || null);
            fecharJanelaResultadoComparacao();
            fecharModalComparacao();
        }

        function abrirModalExportacao() {
            const optCompleto = document.getElementById('opcao-pdf-completo');
            const radioResumido = document.getElementById('radio-pdf-resumido');
            const radioCompleto = document.getElementById('radio-pdf-completo');
            const descModal = document.getElementById('desc-modal-export');

            if (isProMode) {
                optCompleto.classList.remove('hidden');
                radioCompleto.checked = true;
                descModal.innerText = "Modo Pro ativo: pode gerar a proposta técnico-comercial completa ou a ficha técnica resumida:";
            } else {
                optCompleto.classList.add('hidden');
                radioResumido.checked = true;
                descModal.innerText = "Modo Básico: será gerada a ficha técnica com os parâmetros de corte e esforços:";
            }
            document.getElementById('modal-export').classList.remove('hidden');
        }

        function fecharModalExportacao() {
            document.getElementById('modal-export').classList.add('hidden');
        }

        function gerarPDF() {
            if (!window.jspdf || !window.jspdf.jsPDF) {
                alert("Erro: Biblioteca jsPDF não carregou corretamente.");
                return;
            }

            const tipoRelatorio = isProMode
                ? (document.querySelector('input[name="tipo-relatorio"]:checked')?.value || 'completo')
                : 'resumido';
            const incluirComparacao = isProMode && document.getElementById('comp-incluir-pdf')?.checked && cacheComparacao !== null;
            fecharModalExportacao();

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF('p', 'mm', 'a4');
            const r = cacheResultados;

            const margin = 14;
            const pageW = 210;
            const pageH = 297;
            const contentW = pageW - margin * 2;
            let y = 14;

            const corHeaderBg = [15, 23, 42];
            const corAccent = [37, 99, 235];
            const corSecBg = [241, 245, 249];
            const corBorder = [203, 213, 225];
            const corTexto = [30, 41, 59];
            const corMuted = [100, 116, 139];

            function ensureSpace(neededH) {
                if (y + neededH > pageH - 18) {
                    doc.addPage();
                    y = 14;
                }
            }

            function drawSectionTitle(title) {
                ensureSpace(10);
                doc.setFillColor(...corAccent);
                doc.rect(margin, y, 3, 5, 'F');
                doc.setFont("helvetica", "bold");
                doc.setFontSize(9.5);
                doc.setTextColor(...corHeaderBg);
                doc.text(title.toUpperCase(), margin + 5.5, y + 4);
                y += 7.5;
            }

            function drawCardGrid(cards, cols = 4, cardH = 14.5) {
                const gap = 2.5;
                const cardW = (contentW - gap * (cols - 1)) / cols;
                const rows = Math.ceil(cards.length / cols);

                for (let row = 0; row < rows; row++) {
                    ensureSpace(cardH + gap);
                    for (let col = 0; col < cols; col++) {
                        const idx = row * cols + col;
                        if (idx >= cards.length) break;
                        const c = cards[idx];
                        const x = margin + col * (cardW + gap);

                        doc.setFillColor(...corSecBg);
                        doc.setDrawColor(...corBorder);
                        doc.setLineWidth(0.25);
                        doc.roundedRect(x, y, cardW, cardH, 1.5, 1.5, 'FD');

                        doc.setFont("helvetica", "bold");
                        doc.setFontSize(6.5);
                        doc.setTextColor(...corMuted);
                        doc.text(String(c.label).toUpperCase(), x + 2.5, y + 4.2);

                        doc.setFont("helvetica", "bold");
                        doc.setFontSize(9.5);
                        doc.setTextColor(...corHeaderBg);
                        doc.text(String(c.value), x + 2.5, y + 9.2);

                        if (c.sub) {
                            doc.setFont("helvetica", "normal");
                            doc.setFontSize(6.5);
                            doc.setTextColor(...corMuted);
                            doc.text(String(c.sub), x + 2.5, y + 12.8);
                        }
                    }
                    y += cardH + gap;
                }
                y += 1.5;
            }

            function drawKeyValueTable(rowsData) {
                const rowH = 5.8;
                const col1W = 54;
                const col2W = contentW - col1W;

                rowsData.forEach((item, idx) => {
                    ensureSpace(rowH);
                    if (idx % 2 === 0) {
                        doc.setFillColor(248, 250, 252);
                        doc.rect(margin, y, contentW, rowH, 'F');
                    }
                    doc.setDrawColor(...corBorder);
                    doc.setLineWidth(0.15);
                    doc.line(margin, y + rowH, margin + contentW, y + rowH);

                    doc.setFont("helvetica", "bold");
                    doc.setFontSize(7.5);
                    doc.setTextColor(...corMuted);
                    doc.text(String(item[0]), margin + 2, y + 3.9);

                    doc.setFont("helvetica", "normal");
                    doc.setFontSize(7.8);
                    doc.setTextColor(...corTexto);
                    doc.text(String(item[1]), margin + col1W + 2, y + 3.9);

                    y += rowH;
                });
                y += 2.5;
            }

            doc.setFillColor(...corHeaderBg);
            doc.rect(0, 0, pageW, 24, 'F');
            doc.setFillColor(...corAccent);
            doc.rect(0, 24, pageW, 1.2, 'F');

            doc.setFont("helvetica", "bold");
            doc.setFontSize(13);
            doc.setTextColor(255, 255, 255);
            doc.text("MAPAL — PARÂMETROS DE CORTE", margin, 10.5);

            doc.setFont("helvetica", "normal");
            doc.setFontSize(8.5);
            doc.setTextColor(148, 163, 184);
            const subtituloDoc = tipoRelatorio === 'completo'
                ? "Proposta Técnico-Comercial e Análise de Custos / Produtividade"
                : "Ficha Técnica de Maquinação e Esforços de Corte";
            doc.text(subtituloDoc, margin, 16.5);

            const dataHoje = new Date().toLocaleDateString('pt-PT');
            doc.setFontSize(7.5);
            doc.setTextColor(203, 213, 225);
            doc.text(`Data: ${dataHoje}`, pageW - margin, 10.5, { align: 'right' });
            doc.text(`Modo: ${tipoRelatorio === 'completo' ? 'Pro' : 'Básico'}`, pageW - margin, 16.5, { align: 'right' });

            y = 30;

            if (r.alertaSobrecargaTexto) {
                ensureSpace(10);
                doc.setFillColor(254, 226, 226);
                doc.setDrawColor(220, 38, 38);
                doc.setLineWidth(0.4);
                doc.roundedRect(margin, y, contentW, 8, 1.5, 1.5, 'FD');
                doc.setFont("helvetica", "bold");
                doc.setFontSize(7.5);
                doc.setTextColor(153, 27, 27);
                doc.text(`ALERTA SPINDLE: ${r.alertaSobrecargaTexto}`, margin + 3, y + 5.1);
                y += 10.5;
            }

            drawSectionTitle("1. Identificação da Ferramenta, Material e Condições");
            const refCatTxt = r.referenciaCatalogo
                ? `${r.referenciaCatalogo.order_no} (${r.referenciaCatalogo.specification || '—'} | l3: ${r.referenciaCatalogo.l3 ?? '—'} mm)`
                : "Seleção manual por família";
            const infoRows = [
                ["Ferramenta", `${r.brocaNome} (${r.varianteKey}, máx. nominal ${r.limiteNominalMm.toFixed(1)} mm)`],
                ["Ref. Catálogo", refCatTxt],
                ["Linha / Categoria", `${r.linhaNome} — ${r.categoriaNome}`],
                ["Material (Grupo)", `${r.grupoNome}${r.ligaAplicada ? ` (Liga >8% -> ${r.grupoEfetivoKey})` : ''}`],
                ["Refrigeração / Estado", `${r.refrigNome}  |  ${r.estadoTexto}`],
                ["Geometria do Furo", `Ø ${r.diametro.toFixed(2)} mm  |  Profundidade: ${r.profundidade.toFixed(1)} mm`],
                ["Ajustes Aplicados", `Vc: ${r.vcPct > 0 ? '+' : ''}${r.vcPct}%  |  Avanço f: ${r.fPct > 0 ? '+' : ''}${r.fPct}%`]
            ];
            if (tipoRelatorio === 'completo') {
                infoRows.splice(6, 0, ["Lote / Densidade", `${r.qtdFuros} furos  |  Densidade: ${r.densidade.toFixed(2)} g/cm³  |  Sucata: ${r.precoSucataKg.toFixed(2)} €/kg`]);
                infoRows.push(["Pecking / Custo Hora", `${r.peckingDesc}  |  Máquina: ${r.custoHora.toFixed(2)} €/h`]);
            }
            drawKeyValueTable(infoRows);

            drawSectionTitle("2. Parâmetros de Corte Calculados");
            drawCardGrid([
                { label: "Velocidade Corte (Vc)", value: `${r.vcFinal.toFixed(1)} m/min`, sub: `Ajuste ${r.vcPct >= 0 ? '+' : ''}${r.vcPct}%` },
                { label: "Rotação (n)", value: `${r.n} rpm`, sub: "Spindle" },
                { label: "Avanço (f)", value: `${r.fFinal.toFixed(4)} mm/rot`, sub: `Ajuste ${r.fPct >= 0 ? '+' : ''}${r.fPct}%` },
                { label: "Avanço Trabalho (vf)", value: `${r.vf} mm/min`, sub: "Velocidade avanço" }
            ], 4, 14);

            drawSectionTitle("3. Esforços de Corte e Capacidade do Spindle");
            drawCardGrid([
                { label: "Força Axial (Ff)", value: `${Math.round(r.forcaFf)} N`, sub: `${r.forcaKgf.toFixed(1)} kgf` },
                { label: "Binário Corte (Mc)", value: `${r.binarioMc.toFixed(1)} N·m`, sub: r.binMaxNm ? `Máx: ${r.binMaxNm.toFixed(0)} N·m` : "Estimado por kc" },
                { label: "Potência Req.", value: `${r.potenciaReqKw.toFixed(2)} kW`, sub: r.potMaxKw ? `Máx: ${r.potMaxKw.toFixed(2)} kW` : "Spindle n/a" }
            ], 3, 14);

            if (tipoRelatorio === 'completo') {
                drawSectionTitle("4. Produtividade, Material e Custos do Lote");
                drawCardGrid([
                    { label: "Tempo Total Lote", value: `${r.tempoTotalMin.toFixed(1)} min`, sub: `${r.tempoFuroSeg.toFixed(1)} seg/furo` },
                    { label: "Volume / Taxa", value: `${r.volumeTotalCm3.toFixed(1)} cm³`, sub: `${r.taxaRemocaoCm3Min.toFixed(1)} cm³/min` },
                    { label: "Peso Limalha", value: `${r.pesoTotalKg.toFixed(3)} kg`, sub: `${r.massaFuroG.toFixed(2)} g/furo` },
                    { label: "Retorno Sucata", value: `${r.valorSucataTotalEur.toFixed(2)} €`, sub: `${r.valorSucataFuroEur.toFixed(2)} €/furo` }
                ], 4, 14);

                drawCardGrid([
                    { label: "Custo Máq. Lote", value: `${r.custoMaqLote.toFixed(2)} €`, sub: `${r.custoMaqFuro.toFixed(2)} €/furo` },
                    { label: "Metragem Linear", value: `${r.metragemTotalM.toFixed(1)} m`, sub: `${r.qtdFuros} furos × ${r.profundidade.toFixed(0)} mm` },
                    { label: "Custo Hora Ref.", value: `${r.custoHora.toFixed(2)} €/h`, sub: "Taxa oficina" }
                ], 3, 14);

                if (incluirComparacao && cacheComparacao) {
                    const c = cacheComparacao;
                    drawSectionTitle("5. Comparativo Técnico-Comercial (MAPAL vs. Comparada)");
                    drawCardGrid([
                        { label: "Custo Total MAPAL", value: `${c.custoTotalAtual.toFixed(2)} €`, sub: `${c.custoTotalFuroAtual.toFixed(2)} €/furo` },
                        { label: "Custo Total Comparada", value: `${c.custoTotalAlvo.toFixed(2)} €`, sub: `${c.custoTotalFuroAlvo.toFixed(2)} €/furo` },
                        { label: "Impacto Custo Lote", value: `${c.ganhoCustoEur >= 0 ? '-' : '+'}${Math.abs(c.ganhoCustoEur).toFixed(2)} €`, sub: `${c.pctCusto >= 0 ? '-' : '+'}${Math.abs(c.pctCusto).toFixed(1)}%` },
                        { label: "Impacto Tempo Lote", value: `${c.ganhoTempoMin >= 0 ? '-' : '+'}${Math.abs(c.ganhoTempoMin).toFixed(1)} min`, sub: `${c.pctTempo >= 0 ? '-' : '+'}${Math.abs(c.pctTempo).toFixed(1)}%` }
                    ], 4, 14);

                    const compRows = [
                        ["Ferramentas", c.nomeAtual, `vs. ${c.nomeAlvo}`],
                        ["Break-Even", c.breakevenTexto, ""]
                    ];
                    c.linhas.forEach(l => {
                        compRows.push([l.label, `${l.vAtual}  |  ${l.vAlvo}`, `Dif: ${l.diff}`]);
                    });
                    drawKeyValueTable(compRows.map(x => [x[0], `${x[1]}  ${x[2] ? '(' + x[2] + ')' : ''}`]));
                }
            }

            ensureSpace(12);
            doc.setFont("helvetica", "italic");
            doc.setFontSize(7);
            doc.setTextColor(...corMuted);
            doc.text("Nota: Valores teóricos de referência. Ajustar conforme rigidez da fixação, estado da máquina e condições reais de corte.", margin, y + 3);

            const totalPages = doc.internal.getNumberOfPages();
            for (let p = 1; p <= totalPages; p++) {
                doc.setPage(p);
                doc.setDrawColor(...corBorder);
                doc.setLineWidth(0.2);
                doc.line(margin, pageH - 12, pageW - margin, pageH - 12);

                doc.setFont("helvetica", "normal");
                doc.setFontSize(7.5);
                doc.setTextColor(...corMuted);
                doc.text("Created by Bruno Pinto  |  bruno.pinto@alamo-ferramentas.com  |  +351 936 959 415", margin, pageH - 7.5);
                doc.text(`Pág. ${p} / ${totalPages}`, pageW - margin, pageH - 7.5, { align: 'right' });
            }

            const nomeArquivo = `MAPAL_${tipoRelatorio === 'completo' ? 'Proposta_Pro' : 'Ficha_Tecnica'}_${r.brocaNome.replace(/[^a-zA-Z0-9]/g, '_')}_D${r.diametro.toFixed(1)}.pdf`;
            doc.save(nomeArquivo);
        }

        window.onload = function() {
            aplicarModoUI();
            atualizarEstadoBotaoInterrompido();
            filtrarCatalogoCascata();
            atualizarFiltroBrocas();
            atualizarPainelCotas();
        };
    </script>
</body>
</html>
'''

html_content = (
    html_content
    .replace("__PRO_PASSWORD_PLACEHOLDER__", pro_password_js)
    .replace("__REFERENCIAS_JSON_PLACEHOLDER__", referencias_js)
    .replace("__PARAMETROS_JSON_PLACEHOLDER__", parametros_json_js)
)

components.html(html_content, height=920, scrolling=True)