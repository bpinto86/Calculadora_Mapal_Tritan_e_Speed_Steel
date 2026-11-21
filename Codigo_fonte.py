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

                <!-- Pesquisa Rápida por Order no. / Specification / Família / Diâmetro / Encabadouro -->
                <div class="space-y-1 shrink-0 bg-slate-900/90 p-2 rounded-md border border-cyan-800/60">
                    <div class="flex justify-between items-center">
                        <label class="text-[11px] font-medium text-cyan-300">PESQUISA RÁPIDA (ORDER NO. / REF. / ×D / HA-HB-HE)</label>
                        <button type="button" onclick="limparFiltrosCatalogo()" class="text-[10px] text-slate-400 hover:text-cyan-300 underline">Limpar filtros</button>
                    </div>
                    <div class="flex gap-1.5">
                        <input type="text" id="ref-pesquisa" placeholder="Ex: 30902099, 135HA08, -HB, SCD661 12XD..." class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500" oninput="filtrarCatalogoCascata('pesquisa')" onkeydown="if(event.key==='Enter') aplicarPesquisaReferencia()">
                        <button type="button" onclick="aplicarPesquisaReferencia()" class="bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white transition shrink-0">Aplicar</button>
                    </div>
                    <span id="ref-feedback" class="text-[10px] text-slate-400 block">Se souber a referência, pesquise acima; se não souber, filtre abaixo.</span>
                </div>

                <!-- Filtros em Cascata Interligados -->
                <div class="bg-slate-900/70 p-2.5 rounded-md border border-slate-700/80 space-y-2 shrink-0">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Seleção Progressiva do Catálogo</span>
                        <span id="contador-referencias" class="text-[10px] text-slate-400 font-mono">0 ref.</span>
                    </div>
                    <div class="grid grid-cols-2 gap-1.5">
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">1. Gama / Linha</label>
                            <select id="filtro-gama-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('gama')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">2. Refrigeração</label>
                            <select id="filtro-refrig-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-sky-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('refrig')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-3 gap-1.5">
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">3. DIN 6535</label>
                            <select id="filtro-encabadouro-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-amber-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('encabadouro')">
                                <option value="">Todos</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">4. Diâmetro d1</label>
                            <input type="number" id="filtro-d1" list="lista-d1-sugestoes" step="0.01" min="0.1" max="100" placeholder="Ex: 10.00" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" oninput="onFiltroCatalogoChange('d1')" onchange="onFiltroCatalogoChange('d1')">
                            <datalist id="lista-d1-sugestoes"></datalist>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">5. Variante ×D</label>
                            <select id="filtro-xd" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-cyan-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('xd')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                    </div>
                    <div class="space-y-0.5">
                        <label class="text-[10px] font-medium text-slate-300 block">6. Referência / Order no.</label>
                        <select id="filtro-order-no" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onSelecionarOrderCatalogo()">
                            <option value="">— Selecionar referência compatível —</option>
                        </select>
                    </div>
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

                <!-- 3. Modelo de Ferramenta -->
                <div class="space-y-1 shrink-0">
                    <div class="flex justify-between items-center">
                        <label class="text-[11px] font-medium text-slate-300">3. MODELO DE FERRAMENTA</label>
                        <span id="info-modelo-filtro" class="text-[9px] text-cyan-400 font-mono"></span>
                    </div>
                    <select id="broca" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="onMudarModeloFerramenta()">
                    </select>
                </div>

                <!-- 4. Grupo de Materiais -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">4. GRUPO DE MATERIAIS (MMG)</label>
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

                <!-- 5. Método de Refrigeração -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">5. MÉTODO DE REFRIGERAÇÃO A USAR</label>
                    <div class="grid grid-cols-4 gap-1 bg-slate-900 p-1 rounded-md border border-slate-700 text-[11px] text-center font-medium">
                        <button type="button" onclick="setRefrig('int')" id="ref-int" class="py-1.5 rounded bg-blue-600 text-white transition">Interna</button>
                        <button type="button" onclick="setRefrig('ext')" id="ref-ext" class="py-1.5 rounded text-slate-400 hover:text-white transition">Externa</button>
                        <button type="button" onclick="setRefrig('mql')" id="ref-mql" class="py-1.5 rounded text-slate-400 hover:text-white transition">MQL</button>
                        <button type="button" onclick="setRefrig('ar')" id="ref-ar" class="py-1.5 rounded text-slate-400 hover:text-white transition">Ar</button>
                    </div>
                    <p id="aviso-refrig" class="text-[9px] text-amber-400 hidden">Nota: Esta ferramenta não permite refrigeração interna.</p>
                </div>

                <!-- 6. Dimensões -->
                <div class="grid grid-cols-2 gap-2 shrink-0">
                    <div id="bloco-diametro-manual" class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">6. DIÂMETRO (Ø)</label>
                        <div class="flex items-center gap-1">
                            <button onclick="ajustarDiametro(-0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">-</button>
                            <input type="number" id="diametro" value="12.00" step="0.1" min="0.5" max="30" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white focus:outline-none focus:border-blue-500" oninput="onDiametroPrincipalChange()">
                            <button onclick="ajustarDiametro(0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">+</button>
                        </div>
                    </div>
                    <div id="bloco-diametro-catalogo" class="space-y-1 hidden">
                        <label class="text-[11px] font-medium text-emerald-400">6. DIÂMETRO (Ø) — d1</label>
                        <div class="bg-slate-900/90 border border-emerald-700/60 rounded-md p-1.5 text-center flex items-center justify-between px-2">
                            <div id="diametro-catalogo-valor" class="text-sm font-bold text-emerald-300">Ø 12.00 mm</div>
                            <button type="button" onclick="limparDiametroD1()" title="Limpar d1 e voltar ao Ø livre" class="text-[10px] text-slate-400 hover:text-white underline">Livre</button>
                        </div>
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">7. PROFUNDIDADE/FURO (L)</label>
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
                            <label class="text-[11px] font-medium text-slate-300">8. QTD. FUROS (LOTE)</label>
                            <input type="number" id="qtd-furos" value="50" step="1" min="1" max="100000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">9. DENSIDADE (g/cm³)</label>
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
                            <label class="text-[11px] font-medium text-slate-300">10. VALOR SUCATA (€/kg)</label>
                            <input type="number" id="preco-sucata" value="0.35" step="0.05" min="0" max="50" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">11. CUSTO HORA MÁQUINA (€/h)</label>
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
                        <span id="meta-referencia-ativa" class="text-[10px] text-slate-400 font-mono">Order: — | Spec: — | DIN 6535: —</span>
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
                                    <g id="needle-potencia" transform="rotate(-90, 100, 100)" style="transform-origin: 100px 100px; transition: transform 0.4s ease-in-out;">
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
                                    <g id="needle-binario" transform="rotate(-90, 100, 100)" style="transform-origin: 100px 100px; transition: transform 0.4s ease-in-out;">
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
                <div class="pro-only hidden grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
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
                <div class="pro-only hidden grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
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
        let linhaAtivaInterna = 'expert';

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

        function extrairEncabadouroDIN6535(item) {
            if (!item) return '';
            if (item.encabadouro) {
                const normExplicit = String(item.encabadouro).trim().toUpperCase();
                if (['HA', 'HB', 'HE'].includes(normExplicit)) return normExplicit;
            }
            const texto = [
                item.specification || '',
                item.designacao || '',
                item.nome || '',
                item.order_no || ''
            ].join(' ').toUpperCase();

            const match = texto.match(/(?:^|[^A-Z0-9])(HA|HB|HE)(?:[^A-Z0-9]|$|\d)/) ||
                          texto.match(/(?:-|_|\/|\s|\d)(HA|HB|HE)(?=\d|\b|$)/);
            if (match && match[1] && ['HA', 'HB', 'HE'].includes(match[1])) {
                return match[1];
            }
            return '';
        }

        function normalizarRefrigCatalogo(item) {
            if (!item) return '';
            const raw = String(item.refrigeracao || item.refrig || '').trim().toLowerCase();
            if (!raw) return '';
            if (raw.includes('int') || raw === 'ik' || raw === 'ic') return 'int';
            if (raw.includes('mql') || raw.includes('mms')) return 'mql';
            if (raw === 'ar' || raw.includes('air') || raw.includes('ar ')) return 'ar';
            if (raw.includes('ext') || raw.includes('sem')) return 'ext';
            return raw;
        }

        function fmtRefrigCatalogo(code) {
            const map = { int: 'Interna (INT)', ext: 'Externa (EXT)', mql: 'MQL', ar: 'Ar' };
            return map[code] || String(code).toUpperCase();
        }

        function obterGamaCatalogo(item) {
            if (!item) return '';
            const famKey = String(item.familia || '').trim().toLowerCase();
            if (famKey && dados[famKey] && dados[famKey].linha) {
                return dados[famKey].linha;
            }
            const gRaw = String(item.linha || item.gama || '').trim().toLowerCase();
            if (gRaw.includes('expert')) return 'expert';
            if (gRaw.includes('performance')) return 'performance';
            if (gRaw.includes('basic')) return 'basic';
            return gRaw;
        }

        function fmtGamaLabel(gamaKey) {
            if (gamaKey === 'expert') return 'Expert Line';
            if (gamaKey === 'performance') return 'Performance Line';
            if (gamaKey === 'basic') return 'Basic Line';
            return gamaKey || '—';
        }

        function fmtCota(val, dec = 0, unit = ' mm') {
            if (val === null || val === undefined || val === '' || isNaN(Number(val))) return '—';
            return `${Number(val).toFixed(dec)}${unit}`;
        }

        function obterD1Digitado() {
            const raw = (document.getElementById('filtro-d1').value || '').trim().replace(',', '.');
            if (!raw) return null;
            const num = parseFloat(raw);
            return (!isNaN(num) && num > 0) ? num : null;
        }

        function limparDiametroD1() {
            document.getElementById('filtro-d1').value = '';
            referenciaAtivaObj = null;
            filtrarCatalogoCascata('d1');
            atualizarPainelCotas();
            atualizarCalculo();
        }

        function onDiametroPrincipalChange() {
            const dNum = parseFloat(document.getElementById('diametro').value);
            if (!isNaN(dNum) && dNum > 0) {
                const inpD1 = document.getElementById('filtro-d1');
                if (inpD1 && inpD1.value.trim() !== '') {
                    inpD1.value = dNum.toFixed(2);
                }
                if (referenciaAtivaObj && referenciaAtivaObj.d1 !== undefined && Math.abs(Number(referenciaAtivaObj.d1) - dNum) > 0.001) {
                    referenciaAtivaObj = null;
                }
            }
            atualizarCalculo();
        }

        function atualizarVisibilidadeDiametroManual() {
            const d1Num = obterD1Digitado();
            const refTemD1 = Boolean(referenciaAtivaObj && referenciaAtivaObj.d1 !== null && referenciaAtivaObj.d1 !== undefined && !isNaN(Number(referenciaAtivaObj.d1)));
            const bloqueadoPorCatalogo = Boolean(d1Num !== null || refTemD1);

            const blocoManual = document.getElementById('bloco-diametro-manual');
            const blocoCat = document.getElementById('bloco-diametro-catalogo');
            const valCatEl = document.getElementById('diametro-catalogo-valor');

            if (bloqueadoPorCatalogo) {
                blocoManual.classList.add('hidden');
                blocoCat.classList.remove('hidden');
                const dNum = parseFloat(document.getElementById('diametro').value);
                valCatEl.innerText = `Ø ${!isNaN(dNum) ? dNum.toFixed(2) : '—'} mm`;
            } else {
                blocoManual.classList.remove('hidden');
                blocoCat.classList.add('hidden');
            }
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
                const din6535 = extrairEncabadouroDIN6535(r) || '—';
                const refCode = normalizarRefrigCatalogo(r);
                const refTxt = refCode ? ` | Refrig: ${fmtRefrigCatalogo(refCode)}` : '';
                metaEl.innerText = `Order: ${r.order_no || '—'} | Spec: ${r.specification || '—'} | DIN 6535: ${din6535}${refTxt}`;
            } else {
                const brocaKey = document.getElementById('broca').value;
                const varFiltro = document.getElementById('filtro-xd').value;
                const varKey = varFiltro || (brocaKey && dados[brocaKey] ? Object.keys(dados[brocaKey].variantes)[0] : '—');
                metaEl.innerText = `Família: ${(brocaKey || '—').toUpperCase()} (${varKey}) | DIN 6535: —`;
            }
            atualizarVisibilidadeDiametroManual();
        }

        function limparFiltrosCatalogo() {
            document.getElementById('ref-pesquisa').value = '';
            document.getElementById('filtro-gama-cat').value = '';
            document.getElementById('filtro-refrig-cat').value = '';
            document.getElementById('filtro-encabadouro-cat').value = '';
            document.getElementById('filtro-d1').value = '';
            document.getElementById('filtro-xd').value = '';
            document.getElementById('filtro-order-no').value = '';
            document.getElementById('ref-feedback').innerText = "Se souber a referência, pesquise acima; se não souber, filtre abaixo.";
            document.getElementById('ref-feedback').className = "text-[10px] text-slate-400 block";
            referenciaAtivaObj = null;
            filtrarCatalogoCascata('reset');
            atualizarFiltroBrocas(false);
            atualizarPainelCotas();
            atualizarCalculo();
        }

        function getCandidatosCatalogoBase() {
            const q = (document.getElementById('ref-pesquisa').value || '').trim().toLowerCase();
            if (!Array.isArray(REFERENCIAS_JSON)) return [];
            if (!q) return REFERENCIAS_JSON;
            const tokens = q.split(/\s+/).filter(Boolean);
            return REFERENCIAS_JSON.filter(item => {
                const din6535 = extrairEncabadouroDIN6535(item).toLowerCase();
                const gama = obterGamaCatalogo(item).toLowerCase();
                const refCode = normalizarRefrigCatalogo(item).toLowerCase();
                const hay = [
                    item.order_no,
                    item.specification,
                    item.designacao,
                    item.familia,
                    item.variante,
                    item.refrigeracao,
                    refCode,
                    din6535,
                    gama,
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

        function matchD1Item(item, d1Num) {
            if (d1Num === null || d1Num === undefined || isNaN(d1Num)) return true;
            if (item.d1 === null || item.d1 === undefined || isNaN(Number(item.d1))) return false;
            return Math.abs(Number(item.d1) - d1Num) <= 0.015;
        }

        function filtrarCatalogoCascata(origem = null) {
            const selGama = document.getElementById('filtro-gama-cat');
            const selRefrig = document.getElementById('filtro-refrig-cat');
            const selEnc = document.getElementById('filtro-encabadouro-cat');
            const inpD1 = document.getElementById('filtro-d1');
            const datalistD1 = document.getElementById('lista-d1-sugestoes');
            const selXd = document.getElementById('filtro-xd');
            const selOrder = document.getElementById('filtro-order-no');
            const selModelo = document.getElementById('broca');

            let valGama = selGama.value;
            let valRefrig = selRefrig.value;
            let valEnc = selEnc.value;
            const d1Num = obterD1Digitado();
            let valXd = selXd.value;
            const valModeloAtual = (origem === 'modelo' && selModelo && selModelo.value) ? selModelo.value.toLowerCase() : '';

            const base = getCandidatosCatalogoBase();

            // 1. Gama / Linha interligada
            const candGama = base.filter(c =>
                obterGamaCatalogo(c) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                matchD1Item(c, d1Num) &&
                (!valXd || String(c.variante || '').trim() === valXd) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
            );
            const ordemGama = ['expert', 'performance', 'basic'];
            const gamaList = [...new Set(candGama.map(c => obterGamaCatalogo(c)))].sort((a, b) => {
                const ia = ordemGama.indexOf(a);
                const ib = ordemGama.indexOf(b);
                if (ia !== -1 && ib !== -1) return ia - ib;
                if (ia !== -1) return -1;
                if (ib !== -1) return 1;
                return a.localeCompare(b);
            });
            if (valGama && !gamaList.includes(valGama)) valGama = '';
            preencherSelectOpcoes(selGama, gamaList, 'Todas Gamas', fmtGamaLabel, valGama);

            // 2. Refrigeração interligada
            const candRefrig = base.filter(c =>
                normalizarRefrigCatalogo(c) &&
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                matchD1Item(c, d1Num) &&
                (!valXd || String(c.variante || '').trim() === valXd) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
            );
            const ordemRefrig = ['int', 'ext', 'mql', 'ar'];
            const refrigList = [...new Set(candRefrig.map(c => normalizarRefrigCatalogo(c)))].sort((a, b) => {
                const ia = ordemRefrig.indexOf(a);
                const ib = ordemRefrig.indexOf(b);
                return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
            });
            if (valRefrig && !refrigList.includes(valRefrig)) valRefrig = '';
            preencherSelectOpcoes(selRefrig, refrigList, 'Todas Refrig.', fmtRefrigCatalogo, valRefrig);

            // 3. Encabadouro DIN 6535 (HA, HB, HE) interligado
            const candEnc = base.filter(c =>
                extrairEncabadouroDIN6535(c) &&
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                matchD1Item(c, d1Num) &&
                (!valXd || String(c.variante || '').trim() === valXd) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
            );
            const ordemEnc = ['HA', 'HB', 'HE'];
            const encList = [...new Set(candEnc.map(c => extrairEncabadouroDIN6535(c)))].sort((a, b) => {
                const ia = ordemEnc.indexOf(a);
                const ib = ordemEnc.indexOf(b);
                return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
            });
            if (valEnc && !encList.includes(valEnc)) valEnc = '';
            preencherSelectOpcoes(selEnc, encList, 'Todos DIN', e => `DIN ${e}`, valEnc);

            // 4. Sugestões de Diâmetro d1 para digitação assistida (datalist)
            const candD1 = base.filter(c =>
                (c.d1 !== null && c.d1 !== undefined && !isNaN(Number(c.d1))) &&
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                (!valXd || String(c.variante || '').trim() === valXd) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
            );
            const d1Sugestoes = [...new Set(candD1.map(c => Number(c.d1).toFixed(2)))].sort((a, b) => parseFloat(a) - parseFloat(b));
            if (datalistD1) {
                datalistD1.innerHTML = '';
                d1Sugestoes.forEach(dStr => {
                    const op = document.createElement('option');
                    op.value = dStr;
                    datalistD1.appendChild(op);
                });
            }

            // 5. Variante ×D interligada com o d1 digitado
            const candXd = base.filter(c =>
                c.variante &&
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                matchD1Item(c, d1Num) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
            );
            const xdList = [...new Set(candXd.map(c => String(c.variante).trim()))].sort();
            if (valXd && !xdList.includes(valXd)) valXd = '';
            preencherSelectOpcoes(selXd, xdList, 'Todas ×D', x => x, valXd);

            const finais = base.filter(c =>
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                matchD1Item(c, d1Num) &&
                (!valXd || String(c.variante || '').trim() === valXd) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
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
                const encTxt = extrairEncabadouroDIN6535(item);
                const encPart = encTxt ? ` | ${encTxt}` : '';
                const refCode = normalizarRefrigCatalogo(item);
                const refPart = refCode ? ` | ${refCode.toUpperCase()}` : '';
                const l3Txt = item.l3 !== null && item.l3 !== undefined ? `l3:${Number(item.l3).toFixed(0)}mm` : 'l3:—';
                opt.text = `${item.order_no} | ${item.familia || '—'} | ${dTxt} (${item.variante || '—'})${refPart}${encPart} | ${l3Txt}`;
                selOrder.appendChild(opt);
            });

            window._finaisCatalogoAtuais = finais;

            if (d1Num !== null) {
                document.getElementById('diametro').value = d1Num.toFixed(2);
            }

            if (valRefrig && ['int', 'ext', 'mql', 'ar'].includes(valRefrig) && origem === 'refrig') {
                setRefrig(valRefrig);
            }

            if (valGama && ['expert', 'performance', 'basic'].includes(valGama) && origem !== 'order' && origem !== 'modelo') {
                if (linhaAtivaInterna !== valGama) {
                    linhaAtivaInterna = valGama;
                    atualizarFiltroBrocas(false);
                }
            }

            const temFiltroAtivo = Boolean(valGama || valRefrig || valEnc || (d1Num !== null) || valXd || (document.getElementById('ref-pesquisa').value || '').trim());
            if (temFiltroAtivo && origem !== 'order' && origem !== 'modelo') {
                atualizarFiltroBrocas(false);
            }

            if (finais.length === 1 && temFiltroAtivo && origem !== 'order') {
                selOrder.value = '0';
                onSelecionarOrderCatalogo();
            } else if (!temFiltroAtivo && origem !== 'order') {
                referenciaAtivaObj = null;
                atualizarPainelCotas();
            } else if (temFiltroAtivo && origem !== 'order') {
                if (referenciaAtivaObj && !finais.includes(referenciaAtivaObj)) {
                    referenciaAtivaObj = null;
                }
                atualizarPainelCotas();
                atualizarCalculo();
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
                linhaAtivaInterna = toolData.linha;
                document.getElementById('categoria').value = toolData.categoria;
                atualizarFiltroBrocas(true);
                document.getElementById('broca').value = famKey;

                const varNorm = String(item.variante || '').trim();
                const matchVar = Object.keys(toolData.variantes || {}).find(k => k.toLowerCase() === varNorm.toLowerCase());
                mudarBroca(matchVar || null);
            }

            const refCode = normalizarRefrigCatalogo(item);
            if (refCode && ['int', 'ext', 'mql', 'ar'].includes(refCode)) {
                setRefrig(refCode);
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
                feedback.innerText = "Se souber a referência, pesquise acima; se não souber, filtre abaixo.";
                feedback.className = "text-[10px] text-slate-400 block";
                return;
            }

            if (lista.length > 0) {
                document.getElementById('filtro-order-no').value = '0';
                onSelecionarOrderCatalogo();
                const encDet = extrairEncabadouroDIN6535(lista[0]);
                const encMsg = encDet ? ` [DIN 6535-${encDet}]` : '';
                feedback.innerText = `Encontradas ${lista.length} referência(s) para "${raw}". Selecionada: ${lista[0].order_no}${encMsg}.`;
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
            linhaAtivaInterna = toolData.linha;
            document.getElementById('categoria').value = toolData.categoria;
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
            const varFinal = getVarianteAtiva();
            const encLivre = extrairEncabadouroDIN6535({ specification: upper, order_no: upper });
            feedback.innerText = `Selecionado: ${toolData.nome} (${varFinal})${encLivre ? ` · DIN 6535-${encLivre}` : ''}`;
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

        function getVarianteAtiva() {
            if (referenciaAtivaObj && referenciaAtivaObj.variante) {
                return String(referenciaAtivaObj.variante).trim();
            }
            const selXd = document.getElementById('filtro-xd');
            if (selXd && selXd.value) {
                return String(selXd.value).trim();
            }
            const brocaKey = document.getElementById('broca').value;
            if (brocaKey && dados[brocaKey] && dados[brocaKey].variantes) {
                const keys = Object.keys(dados[brocaKey].variantes);
                if (keys.length > 0) return keys[0];
            }
            return '5xD';
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

        function obterFamiliasCompativeisCatalogo() {
            const valGama = document.getElementById('filtro-gama-cat').value;
            const valRefrig = document.getElementById('filtro-refrig-cat').value;
            const valEnc = document.getElementById('filtro-encabadouro-cat').value;
            const d1Num = obterD1Digitado();
            const valXd = document.getElementById('filtro-xd').value;
            const qPesquisa = (document.getElementById('ref-pesquisa').value || '').trim();

            const temFiltroCatalogo = Boolean(valGama || valRefrig || valEnc || (d1Num !== null) || valXd || qPesquisa);
            if (!temFiltroCatalogo || !Array.isArray(REFERENCIAS_JSON) || REFERENCIAS_JSON.length === 0) {
                return null;
            }

            const base = getCandidatosCatalogoBase();
            const compativeis = base.filter(c =>
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                matchD1Item(c, d1Num) &&
                (!valXd || String(c.variante || '').trim() === valXd)
            );

            const famSet = new Set();
            compativeis.forEach(c => {
                const fk = String(c.familia || '').trim().toLowerCase();
                if (fk && dados[fk]) famSet.add(fk);
            });
            return famSet;
        }

        function atualizarFiltroBrocas(manterSelecao = false) {
            const linhaSel = linhaAtivaInterna || 'expert';
            const categoriaSel = document.getElementById('categoria').value;
            const brocaSelect = document.getElementById('broca');
            const infoModelo = document.getElementById('info-modelo-filtro');
            const atualBroca = manterSelecao ? brocaSelect.value : null;
            const famsCatalogo = obterFamiliasCompativeisCatalogo();

            brocaSelect.innerHTML = '';
            let primeiraChave = null;

            const matchesCatalogo = (key) => !famsCatalogo || famsCatalogo.has(key.toLowerCase());

            // 1. Prioridade: mesma linha + mesma categoria + compatível com filtros do catálogo
            for (const key in dados) {
                const ferramenta = dados[key];
                if (ferramenta.linha === linhaSel && ferramenta.categoria === categoriaSel && matchesCatalogo(key)) {
                    const opt = document.createElement('option');
                    opt.value = key;
                    opt.text = ferramenta.nome;
                    brocaSelect.appendChild(opt);
                    if (!primeiraChave) primeiraChave = key;
                }
            }

            // 2. Se os filtros do catálogo apontam para outras linhas/categorias, listar também as compatíveis no catálogo
            if (famsCatalogo && famsCatalogo.size > 0) {
                for (const key in dados) {
                    const ferramenta = dados[key];
                    const jaExiste = Array.from(brocaSelect.options).some(o => o.value === key);
                    if (!jaExiste && matchesCatalogo(key)) {
                        const opt = document.createElement('option');
                        opt.value = key;
                        opt.text = `${ferramenta.nome} (${fmtGamaLabel(ferramenta.linha)})`;
                        brocaSelect.appendChild(opt);
                        if (!primeiraChave) primeiraChave = key;
                    }
                }
                if (infoModelo) {
                    infoModelo.innerText = `${brocaSelect.options.length} compatível(is)`;
                }
            } else {
                if (!primeiraChave) {
                    for (const key in dados) {
                        if (dados[key].linha === linhaSel) {
                            const opt = document.createElement('option');
                            opt.value = key;
                            opt.text = dados[key].nome;
                            brocaSelect.appendChild(opt);
                            if (!primeiraChave) primeiraChave = key;
                        }
                    }
                }
                if (infoModelo) {
                    infoModelo.innerText = `${brocaSelect.options.length} modelo(s)`;
                }
            }

            if (!primeiraChave) {
                const opt = document.createElement('option');
                opt.value = "";
                opt.text = "Nenhuma ferramenta compatível";
                brocaSelect.appendChild(opt);
            } else if (atualBroca && dados[atualBroca] && Array.from(brocaSelect.options).some(o => o.value === atualBroca)) {
                brocaSelect.value = atualBroca;
            }

            mudarBroca();
        }

        function onMudarModeloFerramenta() {
            const brocaKey = document.getElementById('broca').value;
            if (brocaKey && dados[brocaKey]) {
                const toolData = dados[brocaKey];
                linhaAtivaInterna = toolData.linha;
                const selCat = document.getElementById('categoria');
                if (selCat && selCat.value !== toolData.categoria) {
                    selCat.value = toolData.categoria;
                }
                if (referenciaAtivaObj && String(referenciaAtivaObj.familia || '').trim().toLowerCase() !== brocaKey.toLowerCase()) {
                    referenciaAtivaObj = null;
                }
            }
            mudarBroca();
            filtrarCatalogoCascata('modelo');
        }

        function mudarBroca(variantePreferida = null) {
            const brocaKey = document.getElementById('broca').value;
            const grupoSelect = document.getElementById('grupo');
            
            if (!brocaKey || !dados[brocaKey]) return;

            const toolData = dados[brocaKey];

            const btnInt = document.getElementById('ref-int');
            const avisoRefrig = document.getElementById('aviso-refrig');
            if (toolData.temRefrigInt === false) {
                btnInt.disabled = true;
                btnInt.classList.add('opacity-40', 'cursor-not-allowed');
                avisoRefrig.classList.remove('hidden');
                if (refrigAtual === 'int') {
                    setRefrig('ext');
                }
            } else {
                btnInt.disabled = false;
                btnInt.classList.remove('opacity-40', 'cursor-not-allowed');
                avisoRefrig.classList.add('hidden');
            }

            const atualGrupo = grupoSelect.value;
            grupoSelect.innerHTML = '';

            toolData.gruposList.forEach(g => {
                const opt = document.createElement('option');
                opt.value = g;
                opt.text = toolData.gruposNames[g] || g;
                grupoSelect.appendChild(opt);
            });

            if (atualGrupo && toolData.grupos[atualGrupo]) {
                grupoSelect.value = atualGrupo;
            } else if (toolData.gruposList.length > 0) {
                grupoSelect.value = toolData.gruposList[0];
            }

            if (variantePreferida && toolData.variantes && toolData.variantes[variantePreferida]) {
                const selXd = document.getElementById('filtro-xd');
                if (selXd && Array.from(selXd.options).some(o => o.value === variantePreferida)) {
                    selXd.value = variantePreferida;
                }
            }

            mudarGrupoMaterial();
        }

        function mudarGrupoMaterial() {
            const grupoKey = document.getElementById('grupo').value;
            if (grupoKey) {
                const prefixo = grupoKey.charAt(0).toUpperCase();
                if (propriedadesGrupo[prefixo]) {
                    document.getElementById('densidade').value = propriedadesGrupo[prefixo].densidade.toFixed(2);
                }
            }
            atualizarCalculo();
        }

        function setRefrig(tipo) {
            const brocaKey = document.getElementById('broca').value;
            if (tipo === 'int' && brocaKey && dados[brocaKey] && dados[brocaKey].temRefrigInt === false) {
                return;
            }

            refrigAtual = tipo;
            ['int', 'ext', 'mql', 'ar'].forEach(t => {
                const btn = document.getElementById(`ref-${t}`);
                if (t === tipo) {
                    btn.className = "py-1.5 rounded bg-blue-600 text-white transition";
                } else {
                    btn.className = "py-1.5 rounded text-slate-400 hover:text-white transition";
                }
            });
            atualizarCalculo();
        }

        function ajustarDiametro(delta) {
            const input = document.getElementById('diametro');
            let val = parseFloat(input.value) || 12.00;
            val = Math.min(30, Math.max(0.5, val + delta));
            input.value = val.toFixed(2);
            onDiametroPrincipalChange();
        }

        function ajustarPct(tipo, delta) {
            if (tipo === 'vc') {
                vcPct = Math.min(50, Math.max(-50, vcPct + delta));
                document.getElementById('vc-slider').value = vcPct;
            } else {
                fPct = Math.min(50, Math.max(-50, fPct + delta));
                document.getElementById('f-slider').value = fPct;
            }
            atualizarCalculo();
        }

        function onSliderVc() {
            vcPct = parseInt(document.getElementById('vc-slider').value, 10) || 0;
            atualizarCalculo();
        }

        function onSliderF() {
            fPct = parseInt(document.getElementById('f-slider').value, 10) || 0;
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

        function toggleLock(campo) {
            if (campo === 'f') {
                fUnlocked = !fUnlocked;
                const inp = document.getElementById('input-f');
                const btn = document.getElementById('btn-lock-f');
                const card = document.getElementById('card-f');
                const stEl = document.getElementById('status-f');
                inp.readOnly = !fUnlocked;
                if (fUnlocked) {
                    btn.innerText = '🔓';
                    card.classList.add('border-amber-500/80', 'bg-slate-800/95');
                    card.classList.remove('border-slate-700');
                    inp.classList.add('text-amber-300', 'bg-slate-900/70');
                    inp.classList.remove('text-white', 'bg-transparent');
                    stEl.innerText = 'Manual';
                    stEl.className = 'text-[9px] text-amber-400 font-semibold';
                    inp.focus();
                } else {
                    btn.innerText = '🔒';
                    card.classList.remove('border-amber-500/80', 'bg-slate-800/95');
                    card.classList.add('border-slate-700');
                    inp.classList.remove('text-amber-300', 'bg-slate-900/70');
                    inp.classList.add('text-white', 'bg-transparent');
                    stEl.innerText = 'Auto';
                    stEl.className = 'text-[9px] text-slate-500';
                }
            } else if (campo === 'vc') {
                vcUnlocked = !vcUnlocked;
                const inp = document.getElementById('input-vc');
                const btn = document.getElementById('btn-lock-vc');
                const card = document.getElementById('card-vc');
                const stEl = document.getElementById('status-vc');
                inp.readOnly = !vcUnlocked;
                if (vcUnlocked) {
                    btn.innerText = '🔓';
                    card.classList.add('border-amber-500/80', 'bg-slate-800/95');
                    card.classList.remove('border-slate-700');
                    inp.classList.add('text-amber-300', 'bg-slate-900/70');
                    inp.classList.remove('text-white', 'bg-transparent');
                    stEl.innerText = 'Manual';
                    stEl.className = 'text-[9px] text-amber-400 font-semibold';
                    inp.focus();
                } else {
                    btn.innerText = '🔒';
                    card.classList.remove('border-amber-500/80', 'bg-slate-800/95');
                    card.classList.add('border-slate-700');
                    inp.classList.remove('text-amber-300', 'bg-slate-900/70');
                    inp.classList.add('text-white', 'bg-transparent');
                    stEl.innerText = 'Auto';
                    stEl.className = 'text-[9px] text-slate-500';
                }
            } else if (campo === 'rpm-max') {
                rpmMaxUnlocked = !rpmMaxUnlocked;
                const inp = document.getElementById('input-rpm-max');
                const btn = document.getElementById('btn-lock-rpm-max');
                const card = document.getElementById('card-rpm-max');
                const stEl = document.getElementById('status-rpm-max');
                inp.readOnly = !rpmMaxUnlocked;
                if (rpmMaxUnlocked) {
                    btn.innerText = '🔓';
                    card.classList.add('border-cyan-500/80', 'bg-slate-800/95');
                    card.classList.remove('border-slate-700');
                    inp.classList.add('text-cyan-300', 'bg-slate-900/70');
                    inp.classList.remove('text-white', 'bg-transparent');
                    stEl.innerText = 'Ativo';
                    stEl.className = 'text-[9px] text-cyan-400 font-semibold';
                    inp.focus();
                } else {
                    btn.innerText = '🔒';
                    card.classList.remove('border-cyan-500/80', 'bg-slate-800/95');
                    card.classList.add('border-slate-700');
                    inp.classList.remove('text-cyan-300', 'bg-slate-900/70');
                    inp.classList.add('text-white', 'bg-transparent');
                    stEl.innerText = 'Inativo';
                    stEl.className = 'text-[9px] text-slate-500';
                }
            }
            atualizarCalculo();
        }

        function onManualInput(campo) {
            atualizarCalculo();
        }

        function getGrupoEfetivo() {
            const brocaKey = document.getElementById('broca').value;
            const grupoKey = document.getElementById('grupo').value;
            const ligaCheck = document.getElementById('liga-check').checked;

            if (!brocaKey || !dados[brocaKey] || !grupoKey) return grupoKey;
            if (!ligaCheck) return grupoKey;

            const lista = dados[brocaKey].gruposList;
            const idx = lista.indexOf(grupoKey);
            if (idx !== -1 && idx < lista.length - 1) {
                return lista[idx + 1];
            }
            return grupoKey;
        }

        function atualizarGauge(tipo, valor, maxCap, unidade) {
            const needle = document.getElementById(tipo === 'pot' ? 'needle-potencia' : 'needle-binario');
            const valLabel = document.getElementById(tipo === 'pot' ? 'val-gauge-pot' : 'val-gauge-bin');
            const badge = document.getElementById(tipo === 'pot' ? 'badge-gauge-pot' : 'badge-gauge-bin');

            valLabel.innerText = `${valor.toFixed(tipo === 'pot' ? 2 : 1)} ${unidade}`;

            if (!maxCap || maxCap <= 0) {
                needle.setAttribute('transform', 'rotate(-90, 100, 100)');
                badge.innerText = 'Sem Limite Definido';
                badge.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400';
                return null;
            }

            const ratio = valor / maxCap;
            const clampedRatio = Math.min(1.15, Math.max(0, ratio));
            const angle = -90 + (clampedRatio * 180);
            needle.setAttribute('transform', `rotate(${angle.toFixed(1)}, 100, 100)`);

            if (ratio < 0.70) {
                badge.innerText = `Seguro (${(ratio * 100).toFixed(0)}%)`;
                badge.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-700/50';
                return null;
            } else if (ratio <= 0.90) {
                badge.innerText = `Atenção (${(ratio * 100).toFixed(0)}%)`;
                badge.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-700/50';
                return null;
            } else if (ratio <= 1.0) {
                badge.innerText = `Crítico (${(ratio * 100).toFixed(0)}%)`;
                badge.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-700/50';
                return null;
            } else {
                const excessoPct = ((ratio - 1) * 100).toFixed(0);
                badge.innerText = `STALL +${excessoPct}%`;
                badge.className = 'text-[9px] font-extrabold px-2 py-0.5 rounded bg-red-600 text-white animate-pulse';
                const nomeParam = tipo === 'pot' ? 'Potência' : 'Binário';
                return `${nomeParam} excede a capacidade do spindle em +${excessoPct}% (${valor.toFixed(tipo === 'pot' ? 2 : 1)} ${unidade} vs máx. ${maxCap.toFixed(tipo === 'pot' ? 2 : 1)} ${unidade})`;
            }
        }

        function atualizarAlertaProfundidade(diametro, profundidade, toolData, varianteKey) {
            const box = document.getElementById('alerta-profundidade');
            const txt = document.getElementById('texto-limite-prof');
            const badge = document.getElementById('badge-limite-prof');

            const l3Catalogo = (referenciaAtivaObj && referenciaAtivaObj.l3 !== null && referenciaAtivaObj.l3 !== undefined && !isNaN(Number(referenciaAtivaObj.l3)))
                ? Number(referenciaAtivaObj.l3)
                : null;
            const nomInfo = toolData ? obterLimiteNominal(toolData, varianteKey, diametro) : { ratio: 5, maxNominalMm: 5 * diametro };

            if (l3Catalogo !== null) {
                const margem = l3Catalogo - profundidade;
                if (profundidade <= l3Catalogo) {
                    box.className = 'bg-emerald-950/40 px-2.5 py-1.5 rounded-md border border-emerald-700/60 text-[10px] text-emerald-200 flex justify-between items-center gap-2 shrink-0';
                    txt.innerText = `Dentro do limite real l3 (${l3Catalogo.toFixed(0)} mm máx. catálogo | margem ${margem.toFixed(1)} mm)`;
                    badge.innerText = 'OK (l3)';
                    badge.className = 'font-bold text-emerald-300 shrink-0';
                } else {
                    const excesso = profundidade - l3Catalogo;
                    box.className = 'bg-red-950/70 px-2.5 py-1.5 rounded-md border border-red-500/80 text-[10px] text-red-200 flex justify-between items-center gap-2 shrink-0';
                    txt.innerText = `EXCEDE l3 (${l3Catalogo.toFixed(0)} mm máx. real) em +${excesso.toFixed(1)} mm! Risco de colisão/encabadouro.`;
                    badge.innerText = 'EXCEDE l3';
                    badge.className = 'font-extrabold text-red-300 shrink-0';
                }
            } else {
                box.className = 'bg-slate-900 px-2.5 py-1.5 rounded-md border border-amber-600/50 text-[10px] text-amber-200 flex justify-between items-center gap-2 shrink-0';
                txt.innerText = `Sem cota l3 na ref. ativa · Nominal ${varianteKey} ≈ ${nomInfo.maxNominalMm.toFixed(1)} mm (selecione referência p/ validar l3)`;
                badge.innerText = 'SEM l3';
                badge.className = 'font-bold text-amber-300 shrink-0';
            }
        }

        function atualizarCalculo() {
            const brocaKey = document.getElementById('broca').value;
            const grupoKey = document.getElementById('grupo').value;
            const grupoEfetivoKey = getGrupoEfetivo();

            let diametro = parseFloat(document.getElementById('diametro').value);
            let profundidade = parseFloat(document.getElementById('profundidade').value);
            let qtdFuros = parseInt(document.getElementById('qtd-furos').value, 10);
            let densidade = parseFloat(document.getElementById('densidade').value);
            let precoSucata = parseFloat(document.getElementById('preco-sucata').value);
            let custoHora = parseFloat(document.getElementById('custo-hora').value);

            if (isNaN(diametro) || diametro <= 0) diametro = 12.00;
            if (isNaN(profundidade) || profundidade <= 0) profundidade = 31.0;
            if (isNaN(qtdFuros) || qtdFuros < 1) qtdFuros = 50;
            if (isNaN(densidade) || densidade <= 0) densidade = 7.85;
            if (isNaN(precoSucata) || precoSucata < 0) precoSucata = 0.35;
            if (isNaN(custoHora) || custoHora < 0) custoHora = 50.00;

            document.getElementById('vc-pct-val').innerText = `${vcPct > 0 ? '+' : ''}${vcPct}%`;
            document.getElementById('f-pct-val').innerText = `${fPct > 0 ? '+' : ''}${fPct}%`;

            if (!brocaKey || !dados[brocaKey] || !grupoEfetivoKey || !dados[brocaKey].grupos[grupoEfetivoKey]) return;

            const toolData = dados[brocaKey];
            const grupoObj = toolData.grupos[grupoEfetivoKey];
            const diametrosCat = toolData.diametros;
            const fCatArr = grupoObj.f;
            const varianteAtiva = getVarianteAtiva();

            atualizarPainelCotas();
            atualizarAlertaProfundidade(diametro, profundidade, toolData, varianteAtiva);

            const peckingCheck = document.getElementById('pecking-check').checked;
            const peckingUnid = document.getElementById('pecking-unidade').value;
            let peckingInputVal = parseFloat(document.getElementById('pecking-passo').value);
            let peckingRetensaoVal = parseFloat(document.getElementById('pecking-retensao').value);

            if (isNaN(peckingInputVal) || peckingInputVal <= 0) peckingInputVal = peckingUnid === 'xd' ? 3.0 : 36.0;
            if (isNaN(peckingRetensaoVal) || peckingRetensaoVal <= 0) peckingRetensaoVal = 5000;

            const passoMm = peckingUnid === 'xd' ? (peckingInputVal * diametro) : peckingInputVal;
            const numPassos = Math.max(1, Math.ceil(profundidade / passoMm));
            const equivTexto = peckingUnid === 'xd'
                ? `Equiv: ${passoMm.toFixed(1)} mm (${numPassos} passo${numPassos > 1 ? 's' : ''})`
                : `Equiv: ${(passoMm / diametro).toFixed(2)}×D (${numPassos} passo${numPassos > 1 ? 's' : ''})`;
            document.getElementById('pecking-equiv').innerText = equivTexto;

            const rpmMaxVal = parseFloat(document.getElementById('input-rpm-max').value) || 8000;

            const calc = calcularMetricasFerramenta(brocaKey, varianteAtiva, grupoEfetivoKey, {
                diametro, profundidade, qtdFuros, custoHora,
                refrigAtual, vcPct, fPct, rpmMaxUnlocked, rpmMaxVal,
                peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal
            });

            let fFinal = calc.fFinal;
            let vcFinal = calc.vcFinal;

            const inputF = document.getElementById('input-f');
            const inputVc = document.getElementById('input-vc');

            if (fUnlocked) {
                const manualF = parseFloat(inputF.value);
                if (!isNaN(manualF) && manualF > 0) {
                    fFinal = manualF;
                }
            } else {
                inputF.value = fFinal.toFixed(4);
            }

            if (vcUnlocked) {
                const manualVc = parseFloat(inputVc.value);
                if (!isNaN(manualVc) && manualVc > 0) {
                    vcFinal = manualVc;
                }
            } else {
                inputVc.value = Math.round(vcFinal);
            }

            let n = diametro > 0 ? Math.round((vcFinal * 1000) / (Math.PI * diametro)) : 0;
            let estadoTexto = calc.estadoTexto;
            let estadoCor = calc.estadoCor;

            if (rpmMaxUnlocked && rpmMaxVal > 0 && n > rpmMaxVal) {
                n = rpmMaxVal;
                vcFinal = (n * Math.PI * diametro) / 1000;
                if (!vcUnlocked) {
                    inputVc.value = Math.round(vcFinal);
                }
                estadoTexto = "Limitado por RPM Máx.";
                estadoCor = "text-amber-400";
            }

            const vf = Math.round(fFinal * n);

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

            let potMaxInput = parseFloat(document.getElementById('spindle-potencia').value);
            const unidPot = document.getElementById('unidade-potencia').value;
            let potMaxKw = null;
            if (!isNaN(potMaxInput) && potMaxInput > 0) {
                potMaxKw = unidPot === 'cv' ? (potMaxInput * 0.735499) : potMaxInput;
            }

            let binMaxNm = parseFloat(document.getElementById('spindle-binario').value);
            if (isNaN(binMaxNm) || binMaxNm <= 0) {
                binMaxNm = null;
            }

            const alertaPot = atualizarGauge('pot', potenciaReqKw, potMaxKw, 'kW');
            const alertaBin = atualizarGauge('bin', binarioMc, binMaxNm, 'N·m');

            const boxSobrecarga = document.getElementById('alerta-sobrecarga-spindle');
            const textoSobrecarga = document.getElementById('texto-sobrecarga-spindle');
            const alertasAtivos = [alertaPot, alertaBin].filter(Boolean);
            if (alertasAtivos.length > 0) {
                textoSobrecarga.innerText = alertasAtivos.join(' | ');
                boxSobrecarga.classList.remove('hidden');
            } else {
                boxSobrecarga.classList.add('hidden');
            }

            const areaMm2 = Math.PI * Math.pow(diametro / 2, 2);
            const volumeFuroCm3 = (areaMm2 * profundidade) / 1000;
            const volumeTotalCm3 = volumeFuroCm3 * qtdFuros;

            const massaFuroG = volumeFuroCm3 * densidade;
            const pesoTotalKg = (massaFuroG * qtdFuros) / 1000;

            const valorSucataFuro = (massaFuroG / 1000) * precoSucata;
            const valorSucataTotal = pesoTotalKg * precoSucata;

            const metragemTotalM = (profundidade * qtdFuros) / 1000;
            const taxaRemocaoCm3Min = (areaMm2 * vf) / 1000;

            document.getElementById('res-n').innerText = n;
            document.getElementById('res-vf').innerText = vf;

            document.getElementById('res-tempo-total').innerHTML = `${tempoTotalMin.toFixed(1)} min <span class="text-xs font-normal text-slate-300" id="res-tempo-unit">(${tempoFuroSeg.toFixed(1)} seg/furo)</span>`;
            document.getElementById('res-metragem').innerText = `${metragemTotalM.toFixed(2)} metros`;

            document.getElementById('res-volume-total').innerText = `${volumeTotalCm3.toFixed(1)} cm³`;
            document.getElementById('res-taxa').innerText = `${taxaRemocaoCm3Min.toFixed(1)} cm³/min`;

            document.getElementById('res-peso').innerHTML = `${pesoTotalKg.toFixed(3)} <span class="text-sm font-normal text-slate-300">kg</span>`;
            document.getElementById('res-peso-g').innerText = `${massaFuroG.toFixed(2)} g / furo`;

            document.getElementById('res-sucata-val').innerHTML = `${valorSucataTotal.toFixed(2)} <span class="text-sm font-normal text-slate-300">€</span>`;
            document.getElementById('res-sucata-furo').innerText = `${valorSucataFuro.toFixed(4)} € / furo`;

            document.getElementById('res-custo-total').innerHTML = `${custoMaqLote.toFixed(2)} € <span class="text-[10px] font-normal text-slate-300" id="res-custo-furo">(${custoMaqFuro.toFixed(3)} €/furo)</span>`;
            document.getElementById('res-custo-hora-ref').innerText = `${custoHora.toFixed(2)} €/h`;

            document.getElementById('res-forca').innerHTML = `${Math.round(forcaFf)} <span class="text-sm font-normal text-slate-300">N</span>`;
            document.getElementById('res-forca-kgf').innerText = `${(forcaFf / 9.80665).toFixed(1)} kgf`;

            document.getElementById('res-binario-card').innerHTML = `${binarioMc.toFixed(1)} <span class="text-sm font-normal text-slate-300">N·m</span>`;

            document.getElementById('val-estado').innerText = estadoTexto;
            document.getElementById('val-estado').className = `text-[9px] font-bold ${estadoCor}`;
            document.getElementById('badge-metodo').innerText = calc.badgeMetodo;

            const tbody = document.getElementById('tabela-ref');
            tbody.innerHTML = '';
            diametrosCat.forEach((dCat, i) => {
                const fCat = fCatArr[i];
                const nCat = dCat > 0 ? Math.round((vcFinal * 1000) / (Math.PI * dCat)) : 0;
                const vfCat = Math.round(fCat * nCat);
                const tr = document.createElement('tr');
                tr.className = i === calc.idxInf ? 'bg-blue-900/30 font-semibold text-white' : 'text-slate-300';
                tr.innerHTML = `
                    <td class="py-1">${dCat.toFixed(2)}</td>
                    <td class="py-1">${fCat.toFixed(3)}</td>
                    <td class="py-1">${nCat}</td>
                    <td class="py-1">${vfCat}</td>
                `;
                tbody.appendChild(tr);
            });

            desenharGrafico(diametrosCat, fCatArr, diametro, fFinal);

            if (!document.getElementById('modal-comparacao').classList.contains('hidden') || !document.getElementById('modal-resultado-comparacao').classList.contains('hidden')) {
                atualizarComparacao();
            }
        }

        function desenharGrafico(diametrosCat, fCatArr, dCalc, fCalc) {
            const svg = document.getElementById('svg-grafico');
            svg.innerHTML = '';

            const width = 400;
            const height = 180;
            const padLeft = 42;
            const padRight = 18;
            const padTop = 18;
            const padBottom = 28;
            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;

            const allD = [...diametrosCat, dCalc];
            const allF = [...fCatArr, fCalc];

            let minD = Math.min(...allD);
            let maxD = Math.max(...allD);
            if (minD === maxD) { minD -= 1; maxD += 1; }
            const dMargin = (maxD - minD) * 0.08;
            minD -= dMargin;
            maxD += dMargin;

            let minF = Math.min(...allF);
            let maxF = Math.max(...allF);
            if (minF === maxF) { minF = 0; maxF += 0.1; }
            const fMargin = (maxF - minF) * 0.12;
            minF = Math.max(0, minF - fMargin);
            maxF += fMargin;

            const xScale = d => padLeft + ((d - minD) / (maxD - minD)) * plotW;
            const yScale = f => padTop + plotH - ((f - minF) / (maxF - minF)) * plotH;

            for (let i = 0; i <= 4; i++) {
                const fTick = minF + (i / 4) * (maxF - minF);
                const yPos = yScale(fTick);

                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', padLeft);
                line.setAttribute('y1', yPos);
                line.setAttribute('x2', width - padRight);
                line.setAttribute('y2', yPos);
                line.setAttribute('stroke', '#1e293b');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);

                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.setAttribute('x', padLeft - 6);
                label.setAttribute('y', yPos + 3);
                label.setAttribute('text-anchor', 'end');
                label.setAttribute('fill', '#94a3b8');
                label.setAttribute('font-size', '9');
                label.textContent = fTick.toFixed(2);
                svg.appendChild(label);
            }

            const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            xAxis.setAttribute('x1', padLeft);
            xAxis.setAttribute('y1', padTop + plotH);
            xAxis.setAttribute('x2', width - padRight);
            xAxis.setAttribute('y2', padTop + plotH);
            xAxis.setAttribute('stroke', '#475569');
            xAxis.setAttribute('stroke-width', '1');
            svg.appendChild(xAxis);

            const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            yAxis.setAttribute('x1', padLeft);
            yAxis.setAttribute('y1', padTop);
            yAxis.setAttribute('x2', padLeft);
            yAxis.setAttribute('y2', padTop + plotH);
            yAxis.setAttribute('stroke', '#475569');
            yAxis.setAttribute('stroke-width', '1');
            svg.appendChild(yAxis);

            for (let i = 0; i < diametrosCat.length; i++) {
                const xPos = xScale(diametrosCat[i]);
                const tick = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                tick.setAttribute('x', xPos);
                tick.setAttribute('y', padTop + plotH + 13);
                tick.setAttribute('text-anchor', 'middle');
                tick.setAttribute('fill', '#94a3b8');
                tick.setAttribute('font-size', '9');
                tick.textContent = diametrosCat[i].toFixed(1);
                svg.appendChild(tick);
            }

            const xTitle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            xTitle.setAttribute('x', padLeft + plotW / 2);
            xTitle.setAttribute('y', height - 3);
            xTitle.setAttribute('text-anchor', 'middle');
            xTitle.setAttribute('fill', '#64748b');
            xTitle.setAttribute('font-size', '9');
            xTitle.textContent = 'Diâmetro Ø (mm)';
            svg.appendChild(xTitle);

            let pathD = '';
            diametrosCat.forEach((dVal, i) => {
                const px = xScale(dVal);
                const py = yScale(fCatArr[i]);
                pathD += (i === 0 ? `M ${px} ${py}` : ` L ${px} ${py}`);
            });

            const curve = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            curve.setAttribute('d', pathD);
            curve.setAttribute('fill', 'none');
            curve.setAttribute('stroke', '#3b82f6');
            curve.setAttribute('stroke-width', '2');
            svg.appendChild(curve);

            diametrosCat.forEach((dVal, i) => {
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', xScale(dVal));
                circle.setAttribute('cy', yScale(fCatArr[i]));
                circle.setAttribute('r', '3.5');
                circle.setAttribute('fill', '#3b82f6');
                svg.appendChild(circle);
            });

            const cx = xScale(dCalc);
            const cy = yScale(fCalc);

            const vLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            vLine.setAttribute('x1', cx);
            vLine.setAttribute('y1', cy);
            vLine.setAttribute('x2', cx);
            vLine.setAttribute('y2', padTop + plotH);
            vLine.setAttribute('stroke', '#f97316');
            vLine.setAttribute('stroke-width', '1');
            vLine.setAttribute('stroke-dasharray', '3,2');
            svg.appendChild(vLine);

            const hLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            hLine.setAttribute('x1', padLeft);
            hLine.setAttribute('y1', cy);
            hLine.setAttribute('x2', cx);
            hLine.setAttribute('y2', cy);
            hLine.setAttribute('stroke', '#f97316');
            hLine.setAttribute('stroke-width', '1');
            hLine.setAttribute('stroke-dasharray', '3,2');
            svg.appendChild(hLine);

            const calcDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            calcDot.setAttribute('cx', cx);
            calcDot.setAttribute('cy', cy);
            calcDot.setAttribute('r', '5');
            calcDot.setAttribute('fill', '#f97316');
            calcDot.setAttribute('stroke', '#ffffff');
            calcDot.setAttribute('stroke-width', '1.5');
            svg.appendChild(calcDot);
        }

        function obterContextoCalculoAtual() {
            let diametro = parseFloat(document.getElementById('diametro').value);
            let profundidade = parseFloat(document.getElementById('profundidade').value);
            let qtdFuros = parseInt(document.getElementById('qtd-furos').value, 10);
            let densidade = parseFloat(document.getElementById('densidade').value);
            let precoSucata = parseFloat(document.getElementById('preco-sucata').value);
            let custoHora = parseFloat(document.getElementById('custo-hora').value);

            if (isNaN(diametro) || diametro <= 0) diametro = 12.00;
            if (isNaN(profundidade) || profundidade <= 0) profundidade = 31.0;
            if (isNaN(qtdFuros) || qtdFuros < 1) qtdFuros = 50;
            if (isNaN(densidade) || densidade <= 0) densidade = 7.85;
            if (isNaN(precoSucata) || precoSucata < 0) precoSucata = 0.35;
            if (isNaN(custoHora) || custoHora < 0) custoHora = 50.00;

            const peckingCheck = document.getElementById('pecking-check').checked;
            const peckingUnid = document.getElementById('pecking-unidade').value;
            let peckingInputVal = parseFloat(document.getElementById('pecking-passo').value);
            let peckingRetensaoVal = parseFloat(document.getElementById('pecking-retensao').value);
            if (isNaN(peckingInputVal) || peckingInputVal <= 0) peckingInputVal = peckingUnid === 'xd' ? 3.0 : 36.0;
            if (isNaN(peckingRetensaoVal) || peckingRetensaoVal <= 0) peckingRetensaoVal = 5000;

            const rpmMaxVal = parseFloat(document.getElementById('input-rpm-max').value) || 8000;

            const requerPiloto = Boolean(document.getElementById('comp-requer-piloto')?.checked);
            let tempoPilotoSeg = parseFloat(document.getElementById('comp-tempo-piloto-seg')?.value);
            let custoPilotoFuro = parseFloat(document.getElementById('comp-custo-piloto-furo')?.value);
            if (isNaN(tempoPilotoSeg) || tempoPilotoSeg < 0) tempoPilotoSeg = 0;
            if (isNaN(custoPilotoFuro) || custoPilotoFuro < 0) custoPilotoFuro = 0;

            const usaBrocaCanhao = Boolean(document.getElementById('comp-usa-broca-canhao')?.checked);
            let tempoParagemAfiMin = parseFloat(document.getElementById('comp-tempo-paragem-afi-min')?.value);
            if (isNaN(tempoParagemAfiMin) || tempoParagemAfiMin < 0) tempoParagemAfiMin = 0;

            return {
                diametro, profundidade, qtdFuros, densidade, precoSucata, custoHora,
                refrigAtual, vcPct, fPct, rpmMaxUnlocked, rpmMaxVal,
                peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal,
                requerPiloto, tempoPilotoSeg, custoPilotoFuro,
                usaBrocaCanhao, tempoParagemAfiMin
            };
        }

        function obterCustoHoraComparacao() {
            const inpComp = document.getElementById('comp-custo-hora');
            const inpMain = document.getElementById('custo-hora');
            let val = parseFloat(inpComp ? inpComp.value : inpMain.value);
            if (isNaN(val) || val < 0) {
                val = parseFloat(inpMain.value);
                if (isNaN(val) || val < 0) val = 50.00;
            }
            return val;
        }

        function sincronizarCustoHoraComparacao() {
            const inpComp = document.getElementById('comp-custo-hora');
            const inpMain = document.getElementById('custo-hora');
            let val = parseFloat(inpComp.value);
            if (isNaN(val) || val < 0) return;
            inpMain.value = val.toFixed(2);
            atualizarCalculo();
        }

        function abrirModalComparacao() {
            if (!isProMode) return;
            const atualBroca = document.getElementById('broca').value;
            const selComp = document.getElementById('comp-ferramenta');
            const inpCompHora = document.getElementById('comp-custo-hora');
            const inpMainHora = document.getElementById('custo-hora');
            if (inpCompHora && inpMainHora) {
                const mainVal = parseFloat(inpMainHora.value);
                if (!isNaN(mainVal) && mainVal >= 0) {
                    inpCompHora.value = mainVal.toFixed(2);
                }
            }

            selComp.innerHTML = '';

            const optCliente = document.createElement('option');
            optCliente.value = '__CLIENTE_MANUAL__';
            optCliente.text = 'Ferramenta do Cliente (Vc e f manuais)';
            selComp.appendChild(optCliente);

            for (const key in dados) {
                const opt = document.createElement('option');
                opt.value = key;
                opt.text = `${dados[key].nome} (${dados[key].linha.toUpperCase()})`;
                selComp.appendChild(opt);
            }

            if (atualBroca && dados[atualBroca]) {
                selComp.value = atualBroca;
            } else {
                selComp.value = '__CLIENTE_MANUAL__';
            }

            onChangeFonteComparacao();
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function fecharModalComparacao() {
            const modal = document.getElementById('modal-comparacao');
            if (modal) modal.classList.add('hidden');
        }

        function abrirJanelaResultadoComparacao() {
            if (!isProMode) return;
            atualizarComparacao();
            const syncCb = document.getElementById('comp-incluir-pdf-res');
            const mainCb = document.getElementById('comp-incluir-pdf');
            if (syncCb && mainCb) {
                syncCb.checked = mainCb.checked;
            }
            fecharModalComparacao();
            document.getElementById('modal-resultado-comparacao').classList.remove('hidden');
        }

        function fecharJanelaResultadoComparacao() {
            const modal = document.getElementById('modal-resultado-comparacao');
            if (modal) modal.classList.add('hidden');
        }

        function voltarParaInputsComparacao() {
            fecharJanelaResultadoComparacao();
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function onChangeFonteComparacao() {
            const compKey = document.getElementById('comp-ferramenta').value;
            const blocoCliente = document.getElementById('comp-bloco-cliente');
            const blocoVariante = document.getElementById('comp-bloco-variante');
            const selVar = document.getElementById('comp-variante');
            const btnUsar = document.getElementById('btn-usar-comparada');

            if (compKey === '__CLIENTE_MANUAL__') {
                blocoCliente.classList.remove('hidden');
                blocoVariante.classList.add('hidden');
                btnUsar.classList.add('hidden');
            } else {
                blocoCliente.classList.add('hidden');
                blocoVariante.classList.remove('hidden');
                btnUsar.classList.remove('hidden');

                const alvoData = dados[compKey];
                selVar.innerHTML = '';
                if (alvoData && alvoData.variantes) {
                    const varKeys = Object.keys(alvoData.variantes);
                    varKeys.forEach(vk => {
                        const opt = document.createElement('option');
                        opt.value = vk;
                        opt.text = vk;
                        selVar.appendChild(opt);
                    });
                    const varAtual = getVarianteAtiva();
                    if (alvoData.variantes[varAtual]) {
                        selVar.value = varAtual;
                    }
                }
            }
            atualizarComparacao();
        }

        function calcularCustoFerramentaLote(precoBroca, vidaPorAfiação, vidaUnidade, numReafiacoes, custoPorAfiação, qtdFuros, profundidadeMm) {
            const nReaf = Math.max(0, Math.floor(numReafiacoes || 0));
            const totalCiclosFerramenta = 1 + nReaf;
            const vidaUnidEfetiva = vidaUnidade === 'metros'
                ? Math.max(0.001, (vidaPorAfiação * 1000) / Math.max(0.1, profundidadeMm))
                : Math.max(0.001, vidaPorAfiação);
            const furosPorFerramentaCompleta = vidaUnidEfetiva * totalCiclosFerramenta;
            const qtdFerramentasNecessarias = Math.ceil(qtdFuros / furosPorFerramentaCompleta);
            const reafiacoesEfetuadas = Math.max(0, qtdFerramentasNecessarias * nReaf);

            const custoFerramentaLote = (qtdFerramentasNecessarias * precoBroca) + (reafiacoesEfetuadas * custoPorAfiação);
            const custoFerramentaPorFuro = custoFerramentaLote / Math.max(1, qtdFuros);

            return {
                qtdFerramentasNecessarias,
                furosPorFerramentaCompleta,
                vidaUnidEfetiva,
                reafiacoesEfetuadas,
                custoFerramentaLote,
                custoFerramentaPorFuro
            };
        }

        function desenharGraficoBarrasComparacao(svgId, labelA, valA, colorA, labelB, valB, colorB, unitSuffix, decimals = 2) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            svg.innerHTML = '';

            const width = 300;
            const height = 175;
            const padLeft = 44;
            const padRight = 16;
            const padTop = 24;
            const padBottom = 30;
            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;

            const maxVal = Math.max(valA, valB, 0.01) * 1.18;
            const yScale = v => padTop + plotH - (Math.max(0, v) / maxVal) * plotH;

            for (let i = 0; i <= 3; i++) {
                const tickVal = (i / 3) * maxVal;
                const yPos = yScale(tickVal);
                const grid = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                grid.setAttribute('x1', padLeft);
                grid.setAttribute('y1', yPos);
                grid.setAttribute('x2', width - padRight);
                grid.setAttribute('y2', yPos);
                grid.setAttribute('stroke', '#1e293b');
                grid.setAttribute('stroke-width', '1');
                svg.appendChild(grid);

                const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                txt.setAttribute('x', padLeft - 5);
                txt.setAttribute('y', yPos + 3);
                txt.setAttribute('text-anchor', 'end');
                txt.setAttribute('fill', '#94a3b8');
                txt.setAttribute('font-size', '8.5');
                txt.textContent = tickVal >= 1000 ? `${(tickVal / 1000).toFixed(1)}k` : tickVal.toFixed(tickVal >= 10 ? 0 : 1);
                svg.appendChild(txt);
            }

            const axisX = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            axisX.setAttribute('x1', padLeft);
            axisX.setAttribute('y1', padTop + plotH);
            axisX.setAttribute('x2', width - padRight);
            axisX.setAttribute('y2', padTop + plotH);
            axisX.setAttribute('stroke', '#475569');
            axisX.setAttribute('stroke-width', '1');
            svg.appendChild(axisX);

            const slotW = plotW / 2;
            const barW = Math.min(54, slotW * 0.52);

            const barras = [
                { label: labelA, val: valA, color: colorA, cx: padLeft + slotW * 0.5 },
                { label: labelB, val: valB, color: colorB, cx: padLeft + slotW * 1.5 }
            ];

            barras.forEach(b => {
                const topY = yScale(b.val);
                const barH = Math.max(2, (padTop + plotH) - topY);
                const xPos = b.cx - barW / 2;

                const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                rect.setAttribute('x', xPos);
                rect.setAttribute('y', topY);
                rect.setAttribute('width', barW);
                rect.setAttribute('height', barH);
                rect.setAttribute('rx', '4');
                rect.setAttribute('fill', b.color);
                svg.appendChild(rect);

                const valTxt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                valTxt.setAttribute('x', b.cx);
                valTxt.setAttribute('y', Math.max(12, topY - 5));
                valTxt.setAttribute('text-anchor', 'middle');
                valTxt.setAttribute('fill', '#f8fafc');
                valTxt.setAttribute('font-size', '9.5');
                valTxt.setAttribute('font-weight', 'bold');
                valTxt.textContent = `${b.val.toFixed(decimals)}${unitSuffix}`;
                svg.appendChild(valTxt);

                const lblTxt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                lblTxt.setAttribute('x', b.cx);
                lblTxt.setAttribute('y', padTop + plotH + 14);
                lblTxt.setAttribute('text-anchor', 'middle');
                lblTxt.setAttribute('fill', '#cbd5e1');
                lblTxt.setAttribute('font-size', '9');
                lblTxt.textContent = b.label;
                svg.appendChild(lblTxt);
            });
        }

        function desenharGraficoBreakEven(svgId, qtdFuros, custoFixoA, custoVarFuroA, custoFixoB, custoVarFuroB) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            svg.innerHTML = '';

            const width = 300;
            const height = 175;
            const padLeft = 44;
            const padRight = 14;
            const padTop = 16;
            const padBottom = 28;
            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;

            const nPontos = 20;
            const passos = Math.max(1, qtdFuros);
            const ptsA = [];
            const ptsB = [];

            for (let i = 0; i <= nPontos; i++) {
                const furos = Math.round((i / nPontos) * passos);
                const totA = custoFixoA + furos * custoVarFuroA;
                const totB = custoFixoB + furos * custoVarFuroB;
                ptsA.push({ furos, val: totA });
                ptsB.push({ furos, val: totB });
            }

            const maxVal = Math.max(...ptsA.map(p => p.val), ...ptsB.map(p => p.val), 1) * 1.12;
            const xScale = f => padLeft + (f / passos) * plotW;
            const yScale = v => padTop + plotH - (v / maxVal) * plotH;

            for (let i = 0; i <= 3; i++) {
                const tickVal = (i / 3) * maxVal;
                const yPos = yScale(tickVal);
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', padLeft);
                line.setAttribute('y1', yPos);
                line.setAttribute('x2', width - padRight);
                line.setAttribute('y2', yPos);
                line.setAttribute('stroke', '#1e293b');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);

                const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                txt.setAttribute('x', padLeft - 5);
                txt.setAttribute('y', yPos + 3);
                txt.setAttribute('text-anchor', 'end');
                txt.setAttribute('fill', '#94a3b8');
                txt.setAttribute('font-size', '8.5');
                txt.textContent = tickVal >= 1000 ? `${(tickVal / 1000).toFixed(1)}k€` : `${tickVal.toFixed(0)}€`;
                svg.appendChild(txt);
            }

            const axisX = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            axisX.setAttribute('x1', padLeft);
            axisX.setAttribute('y1', padTop + plotH);
            axisX.setAttribute('x2', width - padRight);
            axisX.setAttribute('y2', padTop + plotH);
            axisX.setAttribute('stroke', '#475569');
            axisX.setAttribute('stroke-width', '1');
            svg.appendChild(axisX);

            const axisY = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            axisY.setAttribute('x1', padLeft);
            axisY.setAttribute('y1', padTop);
            axisY.setAttribute('x2', padLeft);
            axisY.setAttribute('y2', padTop + plotH);
            axisY.setAttribute('stroke', '#475569');
            axisY.setAttribute('stroke-width', '1');
            svg.appendChild(axisY);

            [0, Math.round(passos / 2), passos].forEach(fVal => {
                const xPos = xScale(fVal);
                const lbl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                lbl.setAttribute('x', xPos);
                lbl.setAttribute('y', padTop + plotH + 14);
                lbl.setAttribute('text-anchor', 'middle');
                lbl.setAttribute('fill', '#94a3b8');
                lbl.setAttribute('font-size', '8.5');
                lbl.textContent = `${fVal}`;
                svg.appendChild(lbl);
            });

            const xTitle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            xTitle.setAttribute('x', padLeft + plotW / 2);
            xTitle.setAttribute('y', height - 2);
            xTitle.setAttribute('text-anchor', 'middle');
            xTitle.setAttribute('fill', '#64748b');
            xTitle.setAttribute('font-size', '8.5');
            xTitle.textContent = 'Furos Acumulados no Lote';
            svg.appendChild(xTitle);

            const buildPath = pts => pts.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${xScale(p.furos).toFixed(1)} ${yScale(p.val).toFixed(1)}`).join(' ');

            const pathA = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathA.setAttribute('d', buildPath(ptsA));
            pathA.setAttribute('fill', 'none');
            pathA.setAttribute('stroke', '#38bdf8');
            pathA.setAttribute('stroke-width', '2.2');
            svg.appendChild(pathA);

            const pathB = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathB.setAttribute('d', buildPath(ptsB));
            pathB.setAttribute('fill', 'none');
            pathB.setAttribute('stroke', '#fbbf24');
            pathB.setAttribute('stroke-width', '2.2');
            svg.appendChild(pathB);
        }

        function atualizarComparacao() {
            const atualBroca = document.getElementById('broca').value;
            const grupoEfetivoKey = getGrupoEfetivo();
            const compKey = document.getElementById('comp-ferramenta').value || '__CLIENTE_MANUAL__';
            const compVariante = document.getElementById('comp-variante').value || '5xD';
            const ctx = obterContextoCalculoAtual();
            const custoHoraComp = obterCustoHoraComparacao();
            ctx.custoHora = custoHoraComp;

            const varAtual = getVarianteAtiva();
            const metAtual = calcularMetricasFerramenta(atualBroca, varAtual, grupoEfetivoKey, ctx);
            if (!metAtual) return;

            let metrosRefContinuo = parseFloat(document.getElementById('comp-metros-continuo')?.value);
            if (isNaN(metrosRefContinuo) || metrosRefContinuo <= 0) metrosRefContinuo = 90;
            const furosEquivContinuo = Math.max(1, Math.round((metrosRefContinuo * 1000) / Math.max(0.1, ctx.profundidade)));
            const equivContinuoEl = document.getElementById('comp-equiv-continuo');
            if (equivContinuoEl) {
                equivContinuoEl.innerText = `(~${furosEquivContinuo} furos p/ ${ctx.profundidade.toFixed(0)} mm)`;
            }

            let precoAtual = parseFloat(document.getElementById('comp-preco-atual').value);
            let vidaAtual = parseFloat(document.getElementById('comp-vida-atual').value);
            const vidaUnidAtual = document.getElementById('comp-vida-unid-atual').value;
            let afiQtdAtual = parseInt(document.getElementById('comp-afi-qtd-atual').value, 10);
            let afiCustoAtual = parseFloat(document.getElementById('comp-afi-custo-atual').value);

            let precoAlvo = parseFloat(document.getElementById('comp-preco-alvo').value);
            let vidaAlvo = parseFloat(document.getElementById('comp-vida-alvo').value);
            const vidaUnidAlvo = document.getElementById('comp-vida-unid-alvo').value;
            let afiQtdAlvo = parseInt(document.getElementById('comp-afi-qtd-alvo').value, 10);
            let afiCustoAlvo = parseFloat(document.getElementById('comp-afi-custo-alvo').value);

            if (isNaN(precoAtual) || precoAtual < 0) precoAtual = 0;
            if (isNaN(vidaAtual) || vidaAtual <= 0) vidaAtual = 1;
            if (isNaN(afiQtdAtual) || afiQtdAtual < 0) afiQtdAtual = 0;
            if (isNaN(afiCustoAtual) || afiCustoAtual < 0) afiCustoAtual = 0;

            if (isNaN(precoAlvo) || precoAlvo < 0) precoAlvo = 0;
            if (isNaN(vidaAlvo) || vidaAlvo <= 0) vidaAlvo = 1;
            if (isNaN(afiQtdAlvo) || afiQtdAlvo < 0) afiQtdAlvo = 0;
            if (isNaN(afiCustoAlvo) || afiCustoAlvo < 0) afiCustoAlvo = 0;

            const avisoEl = document.getElementById('comp-aviso-grupo');
            let metAlvo = null;
            let nomeAlvo = "Ferramenta Comparada";

            if (compKey === '__CLIENTE_MANUAL__') {
                nomeAlvo = (document.getElementById('comp-cliente-nome').value || '').trim() || "Ferramenta do Cliente";
                let vcCliente = parseFloat(document.getElementById('comp-cliente-vc').value);
                let fCliente = parseFloat(document.getElementById('comp-cliente-f').value);
                if (isNaN(vcCliente) || vcCliente <= 0) vcCliente = 70;
                if (isNaN(fCliente) || fCliente <= 0) fCliente = 0.0200;

                const furosCicloCliente = vidaUnidAlvo === 'metros'
                    ? Math.max(1, Math.round((vidaAlvo * 1000) / Math.max(0.1, ctx.profundidade)))
                    : Math.max(1, Math.round(vidaAlvo));

                const ctxCliente = { ...ctx, furosPorAfiação: furosCicloCliente };
                metAlvo = calcularMetricasManualCliente(nomeAlvo, vcCliente, fCliente, grupoEfetivoKey, ctxCliente);

                const resumoCanhaoEl = document.getElementById('comp-canhao-resumo');
                if (resumoCanhaoEl) {
                    resumoCanhaoEl.innerText = metAlvo.canhaoAtivo
                        ? `${metAlvo.numParagensLote} paragem(ns) · +${metAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min (${metAlvo.tempoParagemMinVal} min/afiação)`
                        : '0 paragens · +0.0 min';
                }

                let msgExtras = [];
                if (corteInterrompidoAtivo) {
                    msgExtras.push(`corte interrompido ativo (ref. contínuo: ${metrosRefContinuo} m / ~${furosEquivContinuo} furos)`);
                }
                if (metAlvo.requerPiloto) {
                    msgExtras.push(`furo-piloto +${metAlvo.pilotoSegEfetivo.toFixed(0)} s/furo e +${metAlvo.custoPilotoEfetivo.toFixed(2)} €/furo`);
                }
                if (metAlvo.canhaoAtivo) {
                    msgExtras.push(`broca canhão: ${metAlvo.numParagensLote} paragem(ns) de ${metAlvo.tempoParagemMinVal} min (+${metAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min no lote)`);
                }
                if (msgExtras.length > 0) {
                    avisoEl.innerText = `Modo Cliente (${nomeAlvo}): ${msgExtras.join(' · ')}.`;
                    avisoEl.classList.remove('hidden');
                } else {
                    avisoEl.classList.add('hidden');
                }
            } else {
                metAlvo = calcularMetricasFerramenta(compKey, compVariante, grupoEfetivoKey, ctx);
                nomeAlvo = metAlvo ? `${metAlvo.nome} (${compVariante})` : compKey;

                let msgs = [];
                if (!metAlvo) {
                    msgs.push(`A ferramenta ${dados[compKey].nome} não possui dados para o grupo ${grupoEfetivoKey}. A usar parâmetros de referência equivalentes.`);
                    metAlvo = { ...metAtual, nome: dados[compKey].nome, varianteKey: compVariante };
                }
                if (corteInterrompidoAtivo) {
                    msgs.push(`Corte interrompido ativo: em interceções/cascatas, a estabilidade da aresta e o escoamento de cavaco favorecem ferramentas de maior robustez/geometria (ref. contínuo: ${metrosRefContinuo} m / ~${furosEquivContinuo} furos).`);
                }
                if (msgs.length > 0) {
                    avisoEl.innerText = msgs.join(' ');
                    avisoEl.classList.remove('hidden');
                } else {
                    avisoEl.classList.add('hidden');
                }
            }

            const ferrAtual = calcularCustoFerramentaLote(precoAtual, vidaAtual, vidaUnidAtual, afiQtdAtual, afiCustoAtual, ctx.qtdFuros, ctx.profundidade);
            const ferrAlvo = calcularCustoFerramentaLote(precoAlvo, vidaAlvo, vidaUnidAlvo, afiQtdAlvo, afiCustoAlvo, ctx.qtdFuros, ctx.profundidade);

            const custoPilotoAlvoLote = metAlvo.custoPilotoLote || 0;
            const custoTotalAtual = metAtual.custoMaqLote + ferrAtual.custoFerramentaLote;
            const custoTotalAlvo = metAlvo.custoMaqLote + ferrAlvo.custoFerramentaLote + custoPilotoAlvoLote;
            const difCustoTotal = custoTotalAlvo - custoTotalAtual;

            const custoFuroAtual = custoTotalAtual / ctx.qtdFuros;
            const custoFuroAlvo = custoTotalAlvo / ctx.qtdFuros;
            const difCustoFuro = custoFuroAlvo - custoFuroAtual;

            const difTempoMin = metAlvo.tempoTotalMin - metAtual.tempoTotalMin;

            document.getElementById('comp-th-atual').innerText = `${metAtual.nome} (${varAtual})`;
            document.getElementById('comp-th-alvo').innerText = nomeAlvo;

            const subtituloEl = document.getElementById('res-comp-subtitulo');
            if (subtituloEl) {
                const tagInter = corteInterrompidoAtivo ? ' · Corte Interrompido' : '';
                subtituloEl.innerText = `${metAtual.nome} (${varAtual}) vs. ${nomeAlvo} · Grupo ${grupoEfetivoKey} · Lote ${ctx.qtdFuros} furos${tagInter}`;
            }

            const difTempoAbsMin = Math.abs(difTempoMin);
            const difTempoStr = `${difTempoMin >= 0 ? '+' : '-'}${difTempoAbsMin.toFixed(1)} min`;
            const pctTempo = metAtual.tempoTotalMin > 0 ? ((difTempoMin / metAtual.tempoTotalMin) * 100) : 0;

            let capTexto = '';
            if (difTempoMin < -0.05) {
                capTexto = `${nomeAlvo} é mais rápida em ${difTempoAbsMin.toFixed(1)} min (${pctTempo.toFixed(1)}%) no lote de ${ctx.qtdFuros} furos.`;
            } else if (difTempoMin > 0.05) {
                capTexto = `${metAtual.nome} poupa ${difTempoAbsMin.toFixed(1)} min (${Math.abs(pctTempo).toFixed(1)}%) no lote de ${ctx.qtdFuros} furos.`;
            } else {
                capTexto = `Tempo de ciclo equivalente entre ferramentas no lote de ${ctx.qtdFuros} furos.`;
            }
            if (metAlvo.canhaoAtivo && metAlvo.tempoParagemCanhaoLoteMin > 0) {
                capTexto += ` Inclui +${metAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min de paragens (${metAlvo.numParagensLote}× ${metAlvo.tempoParagemMinVal} min) na broca canhão.`;
            }
            document.getElementById('comp-capacidade-texto').innerText = capTexto;

            const custoHoraSeg = custoHoraComp / 3600;
            const custoVarFuroAtual = (metAtual.tempoFuroSeg * custoHoraSeg) + (ferrAtual.custoFerramentaLote / Math.max(1, ferrAtual.furosPorFerramentaCompleta));
            const custoVarFuroAlvo = (metAlvo.tempoFuroSeg * custoHoraSeg) + (ferrAlvo.custoFerramentaLote / Math.max(1, ferrAlvo.furosPorFerramentaCompleta)) + (metAlvo.custoPilotoEfetivo || 0);

            const custoFixoCicloAtual = precoAtual + (afiQtdAtual * afiCustoAtual);
            const custoFixoCicloAlvo = precoAlvo + (afiQtdAlvo * afiCustoAlvo);
            const difCustoFixo = custoFixoCicloAtual - custoFixoCicloAlvo;
            const ganhoVariavelPorFuro = custoVarFuroAlvo - custoVarFuroAtual;

            let breakevenTexto = '';
            if (difCustoFixo > 0 && ganhoVariavelPorFuro > 0.0001) {
                const furosBe = Math.ceil(difCustoFixo / ganhoVariavelPorFuro);
                breakevenTexto = `Ferramenta mais cara compensa a partir de ~${furosBe} furos (custo fixo superior em +${difCustoFixo.toFixed(0)} €, mas poupa ${ganhoVariavelPorFuro.toFixed(3)} €/furo).`;
            } else if (difCustoFixo < 0 && ganhoVariavelPorFuro < -0.0001) {
                const furosBe = Math.ceil(Math.abs(difCustoFixo) / Math.abs(ganhoVariavelPorFuro));
                breakevenTexto = `Diferença inicial de ${Math.abs(difCustoFixo).toFixed(0)} € é absorvida em ~${furosBe} furos.`;
            } else if (difCustoTotal < 0) {
                breakevenTexto = `Vantagem acumulada desde o 1.º furo, atingindo ${Math.abs(difCustoTotal).toFixed(2)} € no lote.`;
            } else {
                breakevenTexto = `Sem ponto de inversão no lote atual (${ctx.qtdFuros} furos).`;
            }
            document.getElementById('comp-breakeven-texto').innerText = breakevenTexto;

            const destaqueLoteEl = document.getElementById('comp-resumo-lote-destaque');
            if (difCustoTotal < -0.01) {
                destaqueLoteEl.innerText = `Poupança de ${Math.abs(difCustoTotal).toFixed(2)} € no lote (${Math.abs(difCustoFuro).toFixed(3)} €/furo) com ${nomeAlvo}.`;
                destaqueLoteEl.className = 'text-xs text-emerald-300 font-semibold mt-1';
            } else if (difCustoTotal > 0.01) {
                destaqueLoteEl.innerText = `Poupança de ${difCustoTotal.toFixed(2)} € no lote (${Math.abs(difCustoFuro).toFixed(3)} €/furo) com ${metAtual.nome}.`;
                destaqueLoteEl.className = 'text-xs text-sky-300 font-semibold mt-1';
            } else {
                destaqueLoteEl.innerText = `Custo total equivalente no lote (${custoTotalAtual.toFixed(2)} €).`;
                destaqueLoteEl.className = 'text-xs text-white font-semibold mt-1';
            }

            desenharGraficoBarrasComparacao('svg-comp-custo', 'MAPAL', custoTotalAtual, '#3b82f6', 'Comparada', custoTotalAlvo, '#f43f5e', '€', 2);
            desenharGraficoBarrasComparacao('svg-comp-tempo', 'MAPAL', metAtual.tempoTotalMin, '#10b981', 'Comparada', metAlvo.tempoTotalMin, '#f59e0b', 'm', 1);
            desenharGraficoBreakEven('svg-comp-breakeven', ctx.qtdFuros, ferrAtual.custoFerramentaLote, metAtual.custoMaqFuro, ferrAlvo.custoFerramentaLote, metAlvo.custoMaqFuro + (metAlvo.custoPilotoEfetivo || 0));

            const linhas = [
                {
                    ind: 'Velocidade de Corte (Vc)',
                    a: `${metAtual.vcFinal.toFixed(0)} m/min`,
                    b: `${metAlvo.vcFinal.toFixed(0)} m/min`,
                    d: `${(metAlvo.vcFinal - metAtual.vcFinal) >= 0 ? '+' : ''}${(metAlvo.vcFinal - metAtual.vcFinal).toFixed(0)} m/min`
                },
                {
                    ind: 'Avanço por Rotação (f)',
                    a: `${metAtual.fFinal.toFixed(4)} mm/rot`,
                    b: `${metAlvo.fFinal.toFixed(4)} mm/rot`,
                    d: `${(metAlvo.fFinal - metAtual.fFinal) >= 0 ? '+' : ''}${(metAlvo.fFinal - metAtual.fFinal).toFixed(4)}`
                },
                {
                    ind: 'Rotações (n) / Avanço (vf)',
                    a: `${metAtual.n} rpm / ${metAtual.vf} mm/min`,
                    b: `${metAlvo.n} rpm / ${metAlvo.vf} mm/min`,
                    d: `${(metAlvo.vf - metAtual.vf) >= 0 ? '+' : ''}${metAlvo.vf - metAtual.vf} mm/min`
                },
                {
                    ind: 'Tempo Unitário / Furo',
                    a: `${metAtual.tempoFuroSeg.toFixed(1)} seg`,
                    b: `${metAlvo.tempoFuroSeg.toFixed(1)} seg`,
                    d: `${(metAlvo.tempoFuroSeg - metAtual.tempoFuroSeg) >= 0 ? '+' : ''}${(metAlvo.tempoFuroSeg - metAtual.tempoFuroSeg).toFixed(1)} seg`
                },
                {
                    ind: `Tempo Total (${ctx.qtdFuros} furos)`,
                    a: `${metAtual.tempoTotalMin.toFixed(1)} min`,
                    b: `${metAlvo.tempoTotalMin.toFixed(1)} min`,
                    d: `${difTempoStr} (${pctTempo >= 0 ? '+' : ''}${pctTempo.toFixed(1)}%)`
                },
                {
                    ind: 'Vida / Ferramentas / Reafiações',
                    a: `${ferrAtual.furosPorFerramentaCompleta.toFixed(0)} furos · ${ferrAtual.qtdFerramentasNecessarias} ferr. (${ferrAtual.reafiacoesEfetuadas} reaf.)`,
                    b: `${ferrAlvo.furosPorFerramentaCompleta.toFixed(0)} furos · ${ferrAlvo.qtdFerramentasNecessarias} ferr. (${ferrAlvo.reafiacoesEfetuadas} reaf.)`,
                    d: `${(ferrAlvo.qtdFerramentasNecessarias - ferrAtual.qtdFerramentasNecessarias) >= 0 ? '+' : ''}${ferrAlvo.qtdFerramentasNecessarias - ferrAtual.qtdFerramentasNecessarias} ferr.`
                },
                {
                    ind: 'Custo Ferramenta no Lote',
                    a: `${ferrAtual.custoFerramentaLote.toFixed(2)} €`,
                    b: `${ferrAlvo.custoFerramentaLote.toFixed(2)} €`,
                    d: `${(ferrAlvo.custoFerramentaLote - ferrAtual.custoFerramentaLote) >= 0 ? '+' : ''}${(ferrAlvo.custoFerramentaLote - ferrAtual.custoFerramentaLote).toFixed(2)} €`
                },
                {
                    ind: 'Custo Máquina no Lote',
                    a: `${metAtual.custoMaqLote.toFixed(2)} €`,
                    b: `${metAlvo.custoMaqLote.toFixed(2)} €`,
                    d: `${(metAlvo.custoMaqLote - metAtual.custoMaqLote) >= 0 ? '+' : ''}${(metAlvo.custoMaqLote - metAtual.custoMaqLote).toFixed(2)} €`
                },
                {
                    ind: 'Custo Total no Lote (Máq. + Ferr.)',
                    a: `${custoTotalAtual.toFixed(2)} €`,
                    b: `${custoTotalAlvo.toFixed(2)} €`,
                    d: `${difCustoTotal >= 0 ? '+' : ''}${difCustoTotal.toFixed(2)} €`,
                    destaque: true
                },
                {
                    ind: 'Custo Total por Furo',
                    a: `${custoFuroAtual.toFixed(3)} €`,
                    b: `${custoFuroAlvo.toFixed(3)} €`,
                    d: `${difCustoFuro >= 0 ? '+' : ''}${difCustoFuro.toFixed(3)} €`,
                    destaque: true
                }
            ];

            if (metAlvo.requerPiloto) {
                linhas.splice(4, 0, {
                    ind: 'Tempo Furo-Piloto (Lote)',
                    a: '0.0 min',
                    b: `+${metAlvo.tempoPilotoLoteMin.toFixed(1)} min (${metAlvo.pilotoSegEfetivo.toFixed(0)} s/furo)`,
                    d: `+${metAlvo.tempoPilotoLoteMin.toFixed(1)} min`
                });
                linhas.splice(8, 0, {
                    ind: 'Custo Piloto no Lote',
                    a: '0.00 €',
                    b: `${custoPilotoAlvoLote.toFixed(2)} € (${metAlvo.custoPilotoEfetivo.toFixed(2)} €/furo)`,
                    d: `+${custoPilotoAlvoLote.toFixed(2)} €`
                });
            }

            if (metAlvo.canhaoAtivo) {
                linhas.splice(5, 0, {
                    ind: 'Paragens Broca Canhão (Afiação)',
                    a: '0 paragens (0.0 min)',
                    b: `${metAlvo.numParagensLote} paragem(ns) (+${metAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min)`,
                    d: `+${metAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min`
                });
            }

            const tbodyComp = document.getElementById('comp-tabela-corpo');
            tbodyComp.innerHTML = '';
            linhas.forEach(l => {
                const tr = document.createElement('tr');
                tr.className = l.destaque ? 'bg-slate-800/80 font-bold text-white' : 'text-slate-300';
                tr.innerHTML = `
                    <td class="py-1.5 px-3">${l.ind}</td>
                    <td class="py-1.5 px-3 text-blue-300">${l.a}</td>
                    <td class="py-1.5 px-3 text-emerald-300">${l.b}</td>
                    <td class="py-1.5 px-3 text-amber-300">${l.d}</td>
                `;
                tbodyComp.appendChild(tr);
            });

            window._ultimoComparativo = {
                nomeAlvo,
                compKey,
                compVariante,
                corteInterrompidoAtivo,
                metrosRefContinuo,
                furosEquivContinuo,
                custoHoraComp,
                metAtual,
                metAlvo,
                ferrAtual,
                ferrAlvo,
                custoPilotoAlvoLote,
                custoTotalAtual,
                custoTotalAlvo,
                difCustoTotal,
                custoFuroAtual,
                custoFuroAlvo,
                difCustoFuro,
                difTempoMin,
                pctTempo,
                breakevenTexto,
                linhas
            };
        }

        function aplicarFerramentaComparada() {
            const compKey = document.getElementById('comp-ferramenta').value;
            const compVariante = document.getElementById('comp-variante').value;
            if (!compKey || compKey === '__CLIENTE_MANUAL__' || !dados[compKey]) return;

            const targetData = dados[compKey];
            linhaAtivaInterna = targetData.linha;
            document.getElementById('categoria').value = targetData.categoria;
            atualizarFiltroBrocas(true);
            document.getElementById('broca').value = compKey;
            mudarBroca(compVariante);
            fecharJanelaResultadoComparacao();
            fecharModalComparacao();
        }

        function abrirModalExportacao() {
            const radioResumido = document.getElementById('radio-pdf-resumido');
            const radioCompleto = document.getElementById('radio-pdf-completo');
            const descEl = document.getElementById('desc-modal-export');

            if (isProMode) {
                radioCompleto.checked = true;
                descEl.innerText = 'Nível Pro ativo: escolha entre a Proposta Completa ou a Ficha Técnica:';
            } else {
                radioResumido.checked = true;
                descEl.innerText = 'Nível Básico ativo: será gerada a Ficha Técnica / Parâmetros de Corte:';
            }
            document.getElementById('modal-export').classList.remove('hidden');
        }

        function fecharModalExportacao() {
            document.getElementById('modal-export').classList.add('hidden');
        }

        function gerarPDF() {
            const tipoSelecionado = isProMode
                ? (document.querySelector('input[name="tipo-relatorio"]:checked')?.value || 'completo')
                : 'resumido';
            const incluirComparativo = isProMode && Boolean(document.getElementById('comp-incluir-pdf')?.checked);

            fecharModalExportacao();

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

            const brocaKey = document.getElementById('broca').value;
            const grupoSelText = document.getElementById('grupo').options[document.getElementById('grupo').selectedIndex]?.text || '';
            const grupoEfetivoKey = getGrupoEfetivo();
            const ligaCheck = document.getElementById('liga-check').checked;
            const varianteAtiva = getVarianteAtiva();
            const ctx = obterContextoCalculoAtual();

            const nomeFerramenta = brocaKey && dados[brocaKey] ? dados[brocaKey].nome : 'Ferramenta MAPAL';
            const linhaLabel = fmtGamaLabel(linhaAtivaInterna);
            const refrigLabels = { int: 'Interna', ext: 'Externa', mql: 'MQL', ar: 'Ar' };
            const refrigLabel = refrigLabels[refrigAtual] || refrigAtual;

            const nText = document.getElementById('res-n').innerText;
            const vfText = document.getElementById('res-vf').innerText;
            const fText = parseFloat(document.getElementById('input-f').value || 0).toFixed(4);
            const vcText = parseFloat(document.getElementById('input-vc').value || 0).toFixed(0);
            const forcaText = document.getElementById('res-forca').innerText.replace('N', '').trim();
            const forcaKgfText = document.getElementById('res-forca-kgf').innerText;
            const binText = document.getElementById('res-binario-card').innerText.replace('N·m', '').trim();
            const potGaugeText = document.getElementById('val-gauge-pot').innerText;

            const dataAtual = new Date().toLocaleDateString('pt-PT');

            doc.setFillColor(15, 23, 42);
            doc.rect(0, 0, 210, 28, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(14);
            doc.text('MAPAL — Parâmetros de Corte & Análise Técnica', 14, 12);

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(148, 163, 184);
            const subTituloPdf = tipoSelecionado === 'completo'
                ? `Proposta Técnico-Comercial Completa (Pro) | Data: ${dataAtual}`
                : `Ficha Técnica de Parâmetros de Corte | Data: ${dataAtual}`;
            doc.text(subTituloPdf, 14, 20);

            let y = 36;

            doc.setTextColor(30, 41, 59);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.text('1. Configuração da Ferramenta e Operação', 14, y);
            y += 6;

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9.5);
            doc.text(`Ferramenta: ${nomeFerramenta} (${linhaLabel} - ${varianteAtiva})`, 14, y); y += 5;
            if (referenciaAtivaObj) {
                const dinPdf = extrairEncabadouroDIN6535(referenciaAtivaObj) || '—';
                doc.text(`Referência Catálogo: ${referenciaAtivaObj.order_no || '—'} | Spec: ${referenciaAtivaObj.specification || '—'} | DIN 6535: ${dinPdf} | l3: ${fmtCota(referenciaAtivaObj.l3, 0)}`, 14, y);
                y += 5;
            }
            doc.text(`Material (MMG): ${grupoSelText}${ligaCheck ? ` -> Grupo Efetivo: ${grupoEfetivoKey} (Liga > 8%)` : ''}`, 14, y); y += 5;
            doc.text(`Refrigeração: ${refrigLabel} | Diâmetro Ø: ${ctx.diametro.toFixed(2)} mm | Profundidade Furo L: ${ctx.profundidade.toFixed(1)} mm`, 14, y); y += 5;
            if (vcPct !== 0 || fPct !== 0) {
                doc.text(`Ajustes Aplicados: Ajuste Vc = ${vcPct > 0 ? '+' : ''}${vcPct}% | Ajuste Avanço f = ${fPct > 0 ? '+' : ''}${fPct}%`, 14, y);
                y += 5;
            }
            y += 3;

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.text('2. Parâmetros de Corte e Esforços', 14, y);
            y += 6;

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9.5);
            doc.text(`Velocidade de Corte (Vc): ${vcText} m/min   |   Rotações (n): ${nText} rpm`, 14, y); y += 5;
            doc.text(`Avanço por Rotação (f): ${fText} mm/rot   |   Avanço de Trabalho (vf): ${vfText} mm/min`, 14, y); y += 5;
            doc.text(`Força Axial (Ff): ${forcaText} N (${forcaKgfText})   |   Binário (Mc): ${binText} N·m   |   Potência: ${potGaugeText}`, 14, y); y += 8;

            if (tipoSelecionado === 'completo') {
                const tempoTotal = document.getElementById('res-tempo-total').innerText;
                const volumeTotal = document.getElementById('res-volume-total').innerText;
                const pesoTotal = document.getElementById('res-peso').innerText.replace(/\s+/g, ' ').trim();
                const sucataTotal = document.getElementById('res-sucata-val').innerText.replace(/\s+/g, ' ').trim();
                const custoTotal = document.getElementById('res-custo-total').innerText.replace(/\s+/g, ' ').trim();

                doc.setFont('helvetica', 'bold');
                doc.setFontSize(11);
                doc.text('3. Produção, Custos e Sucata (Lote)', 14, y);
                y += 6;

                doc.setFont('helvetica', 'normal');
                doc.setFontSize(9.5);
                doc.text(`Quantidade de Furos (Lote): ${ctx.qtdFuros}   |   Custo Hora Máquina: ${ctx.custoHora.toFixed(2)} €/h`, 14, y); y += 5;
                doc.text(`Tempo de Ciclo: ${tempoTotal}   |   Custo de Maquinação: ${custoTotal}`, 14, y); y += 5;
                doc.text(`Volume Removido: ${volumeTotal}   |   Peso Limalha: ${pesoTotal} (Densidade: ${ctx.densidade.toFixed(2)} g/cm³)`, 14, y); y += 5;
                doc.text(`Valor Sucata: ${sucataTotal} (Preço Sucata: ${ctx.precoSucata.toFixed(2)} €/kg)`, 14, y); y += 8;

                if (incluirComparativo) {
                    atualizarComparacao();
                    const compData = window._ultimoComparativo;
                    if (compData) {
                        if (y > 235) {
                            doc.addPage();
                            y = 18;
                        }
                        doc.setFont('helvetica', 'bold');
                        doc.setFontSize(11);
                        doc.text('4. Comparativo Técnico-Comercial', 14, y);
                        y += 6;

                        doc.setFont('helvetica', 'normal');
                        doc.setFontSize(9);
                        doc.text(`MAPAL (${varAtual}) vs. ${compData.nomeAlvo} | Lote: ${ctx.qtdFuros} furos | Custo Hora: ${compData.custoHoraComp.toFixed(2)} €/h`, 14, y);
                        y += 5;
                        doc.text(`Custo Total Lote: MAPAL ${compData.custoTotalAtual.toFixed(2)} € vs. ${compData.nomeAlvo} ${compData.custoTotalAlvo.toFixed(2)} € (Dif: ${compData.difCustoTotal >= 0 ? '+' : ''}${compData.difCustoTotal.toFixed(2)} €)`, 14, y);
                        y += 5;
                        doc.text(`Custo / Furo: MAPAL ${compData.custoFuroAtual.toFixed(3)} € vs. ${compData.nomeAlvo} ${compData.custoFuroAlvo.toFixed(3)} € (Dif: ${compData.difCustoFuro >= 0 ? '+' : ''}${compData.difCustoFuro.toFixed(3)} €)`, 14, y);
                        y += 5;
                        doc.text(`Tempo Total Lote: MAPAL ${compData.metAtual.tempoTotalMin.toFixed(1)} min vs. ${compData.nomeAlvo} ${compData.metAlvo.tempoTotalMin.toFixed(1)} min (${compData.difTempoMin >= 0 ? '+' : ''}${compData.difTempoMin.toFixed(1)} min)`, 14, y);
                        y += 5;
                        doc.text(`Payback / Break-Even: ${compData.breakevenTexto}`, 14, y);
                        y += 7;
                    }
                }
            }

            if (y > 250) {
                doc.addPage();
                y = 18;
            }
            doc.setDrawColor(203, 213, 225);
            doc.line(14, y, 196, y);
            y += 5;
            doc.setFont('helvetica', 'italic');
            doc.setFontSize(8);
            doc.setTextColor(100, 116, 139);
            doc.text('Nota: Parâmetros teóricos recomendados. Ajustar conforme rigidez da máquina, fixação e condições reais de corte.', 14, y);
            y += 4;
            doc.text('Contacto: Bruno Pinto | bruno.pinto@alamo-ferramentas.com | +351 936 959 415', 14, y);

            const nomeFicheiro = tipoSelecionado === 'completo'
                ? `MAPAL_Proposta_Completa_${brocaKey || 'ferramenta'}_${ctx.diametro.toFixed(1)}mm.pdf`
                : `MAPAL_Ficha_Tecnica_${brocaKey || 'ferramenta'}_${ctx.diametro.toFixed(1)}mm.pdf`;

            doc.save(nomeFicheiro);
        }

        filtrarCatalogoCascata('init');
        atualizarFiltroBrocas();
        atualizarEstadoBotaoInterrompido();
        aplicarModoUI();
    </script>
</body>
</html>
'''.replace('__PRO_PASSWORD_PLACEHOLDER__', pro_password_js) \
 .replace('__REFERENCIAS_JSON_PLACEHOLDER__', referencias_js) \
 .replace('__PARAMETROS_JSON_PLACEHOLDER__', parametros_json_js)

components.html(html_content, height=920, scrolling=False)