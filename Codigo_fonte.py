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
                        <input type="text" id="ref-pesquisa" placeholder="Ex: 30902099, 135HA08, -HB, SCD661 12XD..." class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500" oninput="filtrarCatalogoCascata()" onkeydown="if(event.key==='Enter') aplicarPesquisaReferencia()">
                        <button type="button" onclick="aplicarPesquisaReferencia()" class="bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white transition shrink-0">Aplicar</button>
                    </div>
                    <span id="ref-feedback" class="text-[10px] text-slate-400 block">Filtros vazios por defeito: selecione Gama, Encabadouro DIN 6535, Refrigeração, Ø d1 ou ×D.</span>
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
                            <label class="text-[10px] font-medium text-slate-300 block">2. Encabadouro DIN 6535</label>
                            <select id="filtro-encabadouro-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-amber-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('encabadouro')">
                                <option value="">Todos (HA/HB/HE)</option>
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-3 gap-1.5">
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">3. Refrigeração</label>
                            <select id="filtro-refrig-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-sky-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('refrig')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">4. Diâmetro d1</label>
                            <select id="filtro-d1" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('d1')">
                                <option value="">Todos</option>
                            </select>
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

                <!-- 1. Tipo de Operação / Categoria -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">1. TIPO DE OPERAÇÃO / CATEGORIA</label>
                    <select id="categoria" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="onCategoriaChange()">
                        <option value="furacao_inteirica">Furação Inteirica Metal Duro (MEGA-Drill / UNI-Drill)</option>
                        <option value="fresagem_aco_duro">Fresagem Aços Endurecidos até 68 HRC (OptiMill-3D-HF / Toroidal)</option>
                        <option value="fresagem_alto_avanco">Fresagem Alto Avanço (OptiMill-3D-HFC / HFM)</option>
                        <option value="fresagem_trocoide">Fresagem Trocoidal / Desbaste Dinâmico (OptiMill-Trochoid)</option>
                        <option value="fresagem_aluminio">Fresagem Alumínio e Ligas Leves (OptiMill-Alu)</option>
                        <option value="alargamento">Alargamento de Precisão (HPR / FixReam)</option>
                    </select>
                </div>

                <!-- 2. Ferramenta / Modelo -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">2. MODELO / SÉRIE DA FERRAMENTA</label>
                    <select id="ferramenta" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="onFerramentaChange()"></select>
                </div>

                <!-- 3. Grupo ISO 513 -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">3. GRUPO DE MATERIAL (ISO 513)</label>
                    <div class="grid grid-cols-6 gap-1" id="iso-buttons">
                        <button type="button" onclick="selectISO('P')" data-iso="P" class="iso-btn py-1 rounded text-xs font-bold border border-slate-600 bg-blue-600 text-white">P</button>
                        <button type="button" onclick="selectISO('M')" data-iso="M" class="iso-btn py-1 rounded text-xs font-bold border border-slate-600 bg-slate-900 text-yellow-400">M</button>
                        <button type="button" onclick="selectISO('K')" data-iso="K" class="iso-btn py-1 rounded text-xs font-bold border border-slate-600 bg-slate-900 text-red-400">K</button>
                        <button type="button" onclick="selectISO('N')" data-iso="N" class="iso-btn py-1 rounded text-xs font-bold border border-slate-600 bg-slate-900 text-emerald-400">N</button>
                        <button type="button" onclick="selectISO('S')" data-iso="S" class="iso-btn py-1 rounded text-xs font-bold border border-slate-600 bg-slate-900 text-orange-400">S</button>
                        <button type="button" onclick="selectISO('H')" data-iso="H" class="iso-btn py-1 rounded text-xs font-bold border border-slate-600 bg-slate-900 text-purple-400">H</button>
                    </div>
                </div>

                <!-- 4. Subgrupo Material MAPAL MMG -->
                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">4. SUBGRUPO MATERIAL (MAPAL MMG)</label>
                    <select id="material" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-white focus:outline-none focus:border-blue-500" onchange="onMaterialChange()"></select>
                </div>

                <!-- 5. Diâmetro (oculto automaticamente quando Ø já está selecionado no catálogo) -->
                <div id="bloco-diametro-manual" class="space-y-1 shrink-0">
                    <div class="flex justify-between items-center">
                        <label class="text-[11px] font-medium text-slate-300">5. DIÂMETRO (Ø)</label>
                        <span id="lbl-diametro" class="text-xs font-bold text-blue-400">8.0 mm</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <input type="range" id="diametro-slider" min="0.5" max="32" step="0.1" value="8.0" class="w-full accent-blue-500 cursor-pointer" oninput="syncDiametro('slider')">
                        <input type="number" id="diametro-input" min="0.5" max="63" step="0.05" value="8.0" class="w-20 bg-slate-900 border border-slate-700 rounded-md p-1 text-xs text-right text-white font-semibold focus:outline-none focus:border-blue-500" oninput="syncDiametro('input')">
                    </div>
                </div>

                <!-- 6. Profundidade de Furo / Corte & Refrigeração -->
                <div class="grid grid-cols-2 gap-2 shrink-0">
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300" id="lbl-profundidade">PROFUNDIDADE (Z)</label>
                        <div class="flex items-center gap-1">
                            <input type="number" id="profundidade" min="1" max="400" step="1" value="24" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1 text-xs text-white font-semibold focus:outline-none focus:border-blue-500" oninput="calcular()">
                            <span class="text-[11px] text-slate-400">mm</span>
                        </div>
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">REFRIGERAÇÃO</label>
                        <select id="refrigeracao" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1 text-xs text-white focus:outline-none focus:border-blue-500" onchange="calcular()">
                            <option value="int">Interna (Emulsão)</option>
                            <option value="ext">Externa (Emulsão)</option>
                            <option value="mql">MQL / Névoa Óleo</option>
                            <option value="ar">Ar Comprimido / Seco</option>
                        </select>
                    </div>
                </div>

                <!-- 7. Limite RPM Máquina e Ajuste Fino -->
                <div class="grid grid-cols-2 gap-2 shrink-0">
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">LIMITE RPM MÁQUINA</label>
                        <input type="number" id="max-rpm" min="1000" max="60000" step="500" value="18000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1 text-xs text-white font-semibold focus:outline-none focus:border-blue-500" oninput="calcular()">
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">FATOR ESTABILIDADE</label>
                        <select id="estabilidade" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1 text-xs text-white focus:outline-none focus:border-blue-500" onchange="calcular()">
                            <option value="1.0">Normal (100%)</option>
                            <option value="1.15">Rígido / Cone HSK (+15%)</option>
                            <option value="0.8">Instável / Balanço Longo (-20%)</option>
                        </select>
                    </div>
                </div>

                <!-- 8. Ajustes Finos % + Botão Reset -->
                <div class="bg-slate-900/70 p-2 rounded-md border border-slate-700/80 space-y-2 shrink-0">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-slate-300 uppercase">Ajuste Fino em Máquina</span>
                        <button type="button" onclick="resetAjustes()" class="text-[10px] text-amber-400 hover:text-amber-300 underline font-medium">Repor 100%</button>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <div class="flex justify-between text-[10px] text-slate-400">
                                <span>Vc (%)</span>
                                <span id="lbl-adj-vc" class="text-blue-400 font-bold">100%</span>
                            </div>
                            <input type="range" id="adj-vc" min="50" max="150" step="5" value="100" class="w-full accent-blue-500 cursor-pointer" oninput="calcular()">
                        </div>
                        <div>
                            <div class="flex justify-between text-[10px] text-slate-400">
                                <span>Avanço f/fz (%)</span>
                                <span id="lbl-adj-f" class="text-emerald-400 font-bold">100%</span>
                            </div>
                            <input type="range" id="adj-f" min="50" max="150" step="5" value="100" class="w-full accent-emerald-500 cursor-pointer" oninput="calcular()">
                        </div>
                    </div>
                </div>
            </div>

            <!-- Painel de Resultados (Direita) -->
            <div class="lg:col-span-8 flex flex-col gap-2.5 overflow-y-auto min-h-0">
                <!-- Ficha Técnica da Referência MAPAL Selecionada -->
                <div id="card-ficha-referencia" class="hidden bg-slate-800/95 p-3 rounded-lg border border-cyan-600/70 shrink-0">
                    <div class="flex flex-wrap justify-between items-start gap-2 mb-2">
                        <div>
                            <div class="flex items-center gap-2 flex-wrap">
                                <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-700">Catálogo MAPAL</span>
                                <span id="ref-badge-gama" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700"></span>
                                <span id="ref-badge-encabadouro" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700"></span>
                                <span id="ref-badge-refrig" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-700"></span>
                                <span id="ref-badge-xd" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-700"></span>
                            </div>
                            <h3 id="ref-titulo-spec" class="text-sm font-bold text-white mt-1 font-mono"></h3>
                            <p id="ref-subtitulo-desc" class="text-xs text-slate-300"></p>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-slate-400 uppercase block">Order No.</span>
                            <span id="ref-order-no-destaque" class="text-base font-extrabold text-cyan-400 font-mono"></span>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-6 gap-2 text-xs bg-slate-900/80 p-2 rounded border border-slate-700/80">
                        <div><span class="text-[10px] text-slate-400 block">d1 (Corte)</span><span id="ref-cota-d1" class="font-bold text-white">—</span></div>
                        <div><span class="text-[10px] text-slate-400 block">d2 (Haste)</span><span id="ref-cota-d2" class="font-bold text-white">—</span></div>
                        <div><span class="text-[10px] text-slate-400 block">l1 (Total)</span><span id="ref-cota-l1" class="font-bold text-white">—</span></div>
                        <div><span class="text-[10px] text-slate-400 block">l2 (Canal)</span><span id="ref-cota-l2" class="font-bold text-white">—</span></div>
                        <div><span class="text-[10px] text-slate-400 block">l3 (Útil)</span><span id="ref-cota-l3" class="font-bold text-white">—</span></div>
                        <div><span class="text-[10px] text-slate-400 block">Encabadouro</span><span id="ref-cota-shank" class="font-bold text-amber-300">—</span></div>
                    </div>
                </div>

                <!-- Cartões Principais de Parâmetros -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 shrink-0">
                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700">
                        <span class="text-[10px] font-semibold text-slate-400 uppercase">Rotação (n)</span>
                        <div class="flex items-baseline gap-1 mt-0.5">
                            <span id="res-rpm" class="text-2xl font-extrabold text-white">0</span>
                            <span class="text-xs text-slate-400">rpm</span>
                        </div>
                        <span id="alerta-rpm" class="text-[10px] text-amber-400 hidden block mt-0.5">⚠️ Limitado pela máquina</span>
                    </div>

                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700">
                        <span class="text-[10px] font-semibold text-slate-400 uppercase">Avanço Mesa (Vf)</span>
                        <div class="flex items-baseline gap-1 mt-0.5">
                            <span id="res-vf" class="text-2xl font-extrabold text-emerald-400">0</span>
                            <span class="text-xs text-slate-400">mm/min</span>
                        </div>
                        <span id="res-f-rev" class="text-[10px] text-slate-400 block mt-0.5">f = 0.00 mm/rot</span>
                    </div>

                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700">
                        <span class="text-[10px] font-semibold text-slate-400 uppercase">Velocidade Corte (Vc)</span>
                        <div class="flex items-baseline gap-1 mt-0.5">
                            <span id="res-vc" class="text-2xl font-extrabold text-blue-400">0</span>
                            <span class="text-xs text-slate-400">m/min</span>
                        </div>
                        <span id="res-vc-range" class="text-[10px] text-slate-400 block mt-0.5">Faixa: 0 - 0 m/min</span>
                    </div>

                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700">
                        <span class="text-[10px] font-semibold text-slate-400 uppercase" id="lbl-avanco-unit">Avanço / Rotação (f)</span>
                        <div class="flex items-baseline gap-1 mt-0.5">
                            <span id="res-fz" class="text-2xl font-extrabold text-cyan-400">0.000</span>
                            <span class="text-xs text-slate-400" id="unit-fz">mm/rot</span>
                        </div>
                        <span id="res-z-info" class="text-[10px] text-slate-400 block mt-0.5">Z = 2 arestas</span>
                    </div>
                </div>

                <!-- Profundidades / Empeno / Tempo / Potência -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 space-y-2">
                        <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider">Empeno & Geometria de Corte</h3>
                        <div class="grid grid-cols-2 gap-2 text-xs">
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block" id="lbl-ap">Profundidade Axial (ap)</span>
                                <span id="res-ap" class="text-sm font-bold text-white">—</span>
                            </div>
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block" id="lbl-ae">Largura Radial (ae)</span>
                                <span id="res-ae" class="text-sm font-bold text-white">—</span>
                            </div>
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block">Relação L/D</span>
                                <span id="res-ld" class="text-sm font-bold text-amber-300">3.0 × D</span>
                            </div>
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block">Taxa Remoção (Q)</span>
                                <span id="res-q" class="text-sm font-bold text-emerald-300">0.0 cm³/min</span>
                            </div>
                        </div>
                    </div>

                    <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 space-y-2">
                        <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider">Estimativa de Processo & Máquina</h3>
                        <div class="grid grid-cols-2 gap-2 text-xs">
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block">Potência Corte Est. (Pc)</span>
                                <span id="res-potencia" class="text-sm font-bold text-rose-400">0.00 kW</span>
                            </div>
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block">Binário Est. (Mc)</span>
                                <span id="res-binario" class="text-sm font-bold text-purple-300">0.0 Nm</span>
                            </div>
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block">Tempo Corte (100 mm)</span>
                                <span id="res-tempo" class="text-sm font-bold text-cyan-300">0.0 s</span>
                            </div>
                            <div class="bg-slate-900/80 p-2 rounded border border-slate-700/60">
                                <span class="text-[10px] text-slate-400 block">Pressão Refrig. Rec.</span>
                                <span id="res-pressao" class="text-sm font-bold text-blue-300">20 - 40 bar</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Notas Técnicas & Estratégia CNC -->
                <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 flex-1 flex flex-col justify-between gap-2">
                    <div>
                        <div class="flex justify-between items-center mb-1.5">
                            <h3 class="text-xs font-bold text-amber-400 uppercase tracking-wider">Recomendações Técnicas & Estratégia CAM</h3>
                            <span id="badge-revestimento" class="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-700">Revestimento: HP / TiAlN</span>
                        </div>
                        <ul id="lista-notas" class="text-xs text-slate-300 space-y-1 list-disc pl-4"></ul>
                    </div>
                    <div id="alerta-furo-piloto" class="hidden bg-amber-950/60 border border-amber-600/70 rounded p-2 text-xs text-amber-200"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Nível Pro -->
    <div id="modal-pro" class="hidden fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4">
        <div class="bg-slate-800 border border-purple-500/60 rounded-xl max-w-md w-full p-5 space-y-4">
            <div class="flex justify-between items-center">
                <h3 class="text-base font-bold text-white">🔐 Ativar Nível Pro</h3>
                <button onclick="fecharModal('modal-pro')" class="text-slate-400 hover:text-white text-lg">✕</button>
            </div>
            <p class="text-xs text-slate-300">Introduza a palavra-passe comercial para desbloquear comparação entre famílias MAPAL e proposta comercial personalizada em PDF.</p>
            <input type="password" id="input-pro-pass" placeholder="Palavra-passe Pro..." class="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-xs text-white focus:outline-none focus:border-purple-500" onkeydown="if(event.key==='Enter') validarPro()">
            <p id="erro-pro-pass" class="text-xs text-rose-400 hidden">Palavra-passe incorreta.</p>
            <div class="flex justify-end gap-2">
                <button onclick="fecharModal('modal-pro')" class="px-3 py-1.5 rounded bg-slate-700 text-xs text-white">Cancelar</button>
                <button onclick="validarPro()" class="px-3 py-1.5 rounded bg-purple-600 hover:bg-purple-500 text-xs font-semibold text-white">Desbloquear</button>
            </div>
        </div>
    </div>

    <!-- Modal Comparação -->
    <div id="modal-comparacao" class="hidden fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4">
        <div class="bg-slate-800 border border-emerald-500/60 rounded-xl max-w-3xl w-full p-5 space-y-4 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center">
                <h3 class="text-base font-bold text-white">⚖️ Comparação de Produtividade MAPAL</h3>
                <button onclick="fecharModal('modal-comparacao')" class="text-slate-400 hover:text-white text-lg">✕</button>
            </div>
            <div id="conteudo-comparacao" class="text-xs text-slate-200"></div>
        </div>
    </div>

    <!-- Modal Exportação PDF -->
    <div id="modal-export" class="hidden fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4">
        <div class="bg-slate-800 border border-blue-500/60 rounded-xl max-w-md w-full p-5 space-y-3">
            <div class="flex justify-between items-center">
                <h3 class="text-base font-bold text-white">📄 Exportar Ficha Técnica PDF</h3>
                <button onclick="fecharModal('modal-export')" class="text-slate-400 hover:text-white text-lg">✕</button>
            </div>
            <div class="space-y-2 text-xs">
                <div>
                    <label class="text-slate-300 block mb-1">Cliente / Empresa</label>
                    <input type="text" id="pdf-cliente" placeholder="Ex: Moldes Exemplo, Lda." class="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-white">
                </div>
                <div>
                    <label class="text-slate-300 block mb-1">Projeto / Molde / Peça</label>
                    <input type="text" id="pdf-projeto" placeholder="Ex: Cavidade Molde 2026-04" class="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-white">
                </div>
                <div>
                    <label class="text-slate-300 block mb-1">Observações Técnicas</label>
                    <textarea id="pdf-notas" rows="2" placeholder="Ex: Ensaio em máquina CNC 5 eixos, emulsão 8%..." class="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-white"></textarea>
                </div>
            </div>
            <div class="flex justify-end gap-2 pt-2">
                <button onclick="fecharModal('modal-export')" class="px-3 py-1.5 rounded bg-slate-700 text-xs text-white">Cancelar</button>
                <button onclick="gerarPDF()" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white">Gerar PDF</button>
            </div>
        </div>
    </div>

    <script>
        const PRO_PASSWORD = ''' + pro_password_js + ''';
        const CATALOGO_JSON = ''' + referencias_js + ''';
        const PARAMETROS_FURACAO_JSON = ''' + parametros_json_js + ''';

        const CATALOGO_BASE_EMBUTIDO = [
            { order_no: "30902099", spec: "135HA0800-03-HP", gama: "MEGA-Drill-Steel", familia: "MEGA-Drill-Steel 3xD", encabadouro: "HA", refrig: "int", xd: "3xD", d1: 8.0, d2: 8.0, l1: 79, l2: 41, l3: 32, z: 2, categoria: "furacao_inteirica", ferramenta_id: "mega_drill_steel", desc: "Broca MD inteiriça 3xD com refrigeração interna" },
            { order_no: "30902115", spec: "135HB0800-03-HP", gama: "MEGA-Drill-Steel", familia: "MEGA-Drill-Steel 3xD", encabadouro: "HB", refrig: "int", xd: "3xD", d1: 8.0, d2: 8.0, l1: 79, l2: 41, l3: 32, z: 2, categoria: "furacao_inteirica", ferramenta_id: "mega_drill_steel", desc: "Broca MD inteiriça 3xD Weldon HB com refrigeração interna" },
            { order_no: "30902210", spec: "135HA0800-05-HP", gama: "MEGA-Drill-Steel", familia: "MEGA-Drill-Steel 5xD", encabadouro: "HA", refrig: "int", xd: "5xD", d1: 8.0, d2: 8.0, l1: 91, l2: 53, l3: 43, z: 2, categoria: "furacao_inteirica", ferramenta_id: "mega_drill_steel", desc: "Broca MD inteiriça 5xD com refrigeração interna" },
            { order_no: "30902305", spec: "135HA0800-08-HP", gama: "MEGA-Drill-Steel", familia: "MEGA-Drill-Steel 8xD", encabadouro: "HA", refrig: "int", xd: "8xD", d1: 8.0, d2: 8.0, l1: 114, l2: 76, l3: 65, z: 2, categoria: "furacao_inteirica", ferramenta_id: "mega_drill_steel", desc: "Broca MD inteiriça 8xD com refrigeração interna" },
            { order_no: "30902412", spec: "135HA0800-12-HP", gama: "MEGA-Drill-Steel", familia: "MEGA-Drill-Steel 12xD", encabadouro: "HA", refrig: "int", xd: "12xD", d1: 8.0, d2: 8.0, l1: 146, l2: 108, l3: 96, z: 2, categoria: "furacao_inteirica", ferramenta_id: "mega_drill_steel", desc: "Broca MD inteiriça 12xD furo profundo com refrigeração interna" },
            { order_no: "30903044", spec: "135HA1000-05-HP", gama: "MEGA-Drill-Steel", familia: "MEGA-Drill-Steel 5xD", encabadouro: "HA", refrig: "int", xd: "5xD", d1: 10.0, d2: 10.0, l1: 103, l2: 61, l3: 50, z: 2, categoria: "furacao_inteirica", ferramenta_id: "mega_drill_steel", desc: "Broca MD inteiriça 5xD Ø10 com refrigeração interna" },
            { order_no: "30904018", spec: "130HA0800-03-HP", gama: "UNI-Drill", familia: "UNI-Drill 3xD", encabadouro: "HA", refrig: "ext", xd: "3xD", d1: 8.0, d2: 8.0, l1: 79, l2: 41, l3: 32, z: 2, categoria: "furacao_inteirica", ferramenta_id: "uni_drill", desc: "Broca MD universal 3xD sem furo de refrigeração (externa)" },
            { order_no: "30905088", spec: "SCD661-0800-12XD-HA", gama: "MEGA-Deep-Drill", familia: "MEGA-Deep-Drill 12xD", encabadouro: "HA", refrig: "int", xd: "12xD", d1: 8.0, d2: 8.0, l1: 152, l2: 112, l3: 98, z: 2, categoria: "furacao_inteirica", ferramenta_id: "mega_deep_drill", desc: "Broca furação profunda 12xD com dupla guia" },
            { order_no: "30906102", spec: "OM-3D-HF-0800-Z4-HA", gama: "OptiMill-3D-HF", familia: "OptiMill-3D-HF", encabadouro: "HA", refrig: "ar", xd: "3xD", d1: 8.0, d2: 8.0, l1: 63, l2: 16, l3: 24, z: 4, categoria: "fresagem_aco_duro", ferramenta_id: "optimill_3d_hf", desc: "Fresa acabamento aços endurecidos até 68 HRC" },
            { order_no: "30907150", spec: "OM-HFC-1000-Z5-HB", gama: "OptiMill-3D-HFC", familia: "OptiMill-3D-HFC", encabadouro: "HB", refrig: "ar", xd: "2xD", d1: 10.0, d2: 10.0, l1: 72, l2: 12, l3: 25, z: 5, categoria: "fresagem_alto_avanco", ferramenta_id: "optimill_hfc", desc: "Fresa alto avanço 5 cortes para desbaste rápido em moldes" },
            { order_no: "30908201", spec: "OM-TRO-1200-Z5-HB", gama: "OptiMill-Trochoid", familia: "OptiMill-Trochoid", encabadouro: "HB", refrig: "int", xd: "3xD", d1: 12.0, d2: 12.0, l1: 83, l2: 36, l3: 38, z: 5, categoria: "fresagem_trocoide", ferramenta_id: "optimill_trochoid", desc: "Fresa trocoidal com quebra-aparas e refrigeração interna" },
            { order_no: "30909310", spec: "OM-ALU-1200-Z3-HA", gama: "OptiMill-Alu", familia: "OptiMill-Alu", encabadouro: "HA", refrig: "int", xd: "3xD", d1: 12.0, d2: 12.0, l1: 83, l2: 36, l3: 38, z: 3, categoria: "fresagem_aluminio", ferramenta_id: "optimill_alu", desc: "Fresa 3 cortes polida para alumínio aeroespacial e moldes" },
            { order_no: "30910405", spec: "HPR400-0800-Z6-HA", gama: "HPR400", familia: "HPR400", encabadouro: "HA", refrig: "int", xd: "4xD", d1: 8.0, d2: 8.0, l1: 90, l2: 18, l3: 36, z: 6, categoria: "alargamento", ferramenta_id: "hpr400", desc: "Alargador de alta precisão H7 6 navalhas" }
        ];

        function normalizarItemCatalogo(raw) {
            const orderNo = String(raw.order_no || raw.orderNo || raw.codigo || raw.ref || "").trim();
            const spec = String(raw.spec || raw.specification || raw.referencia || raw.designation || orderNo).trim();
            const gama = String(raw.gama || raw.linha || raw.serie || raw.series || raw.familia || "MAPAL").trim();
            const familia = String(raw.familia || raw.family || gama).trim();
            let enc = String(raw.encabadouro || raw.shank || raw.din6535 || "").toUpperCase().trim();
            if (!enc) {
                const mEnc = spec.match(/(?:^|[^A-Z])(HA|HB|HE)(?:[^A-Z]|$)/i);
                enc = mEnc ? mEnc[1].toUpperCase() : "HA";
            }
            let refrig = String(raw.refrig || raw.refrigeracao || raw.cooling || "").toLowerCase().trim();
            if (!refrig) {
                if (raw.ik === true || raw.internal_cooling === true || /\b(IK|INT)\b/i.test(spec)) refrig = "int";
                else if (raw.ik === false || raw.internal_cooling === false) refrig = "ext";
                else refrig = "int";
            } else if (["sim", "yes", "true", "ik", "interna"].includes(refrig)) {
                refrig = "int";
            } else if (["nao", "não", "no", "false", "externa"].includes(refrig)) {
                refrig = "ext";
            }
            let xd = String(raw.xd || raw.ld || raw.comprimento_rel || "").trim();
            if (!xd) {
                const mXd = spec.match(/(\d+)\s*[xX×][dD]/);
                if (mXd) xd = `${mXd[1]}xD`;
                else {
                    const mCodeXd = spec.match(/-(03|05|08|12|15|20|25|30)-/);
                    if (mCodeXd) xd = `${parseInt(mCodeXd[1], 10)}xD`;
                }
            }
            const d1 = parseFloat(raw.d1 ?? raw.diametro ?? raw.diameter ?? 0) || 0;
            const d2 = parseFloat(raw.d2 ?? raw.shank_diameter ?? d1) || d1;
            const l1 = parseFloat(raw.l1 ?? raw.overall_length ?? 0) || 0;
            const l2 = parseFloat(raw.l2 ?? raw.flute_length ?? 0) || 0;
            const l3 = parseFloat(raw.l3 ?? raw.usable_length ?? l2) || l2;
            const z = parseInt(raw.z ?? raw.flutes ?? 2, 10) || 2;
            const categoria = raw.categoria || "furacao_inteirica";
            const ferramenta_id = raw.ferramenta_id || "mega_drill_steel";
            const desc = raw.desc || raw.descricao || `${gama} ${xd} Ø${d1}mm (${enc})`;

            return { order_no: orderNo, spec, gama, familia, encabadouro: enc, refrig, xd, d1, d2, l1, l2, l3, z, categoria, ferramenta_id, desc };
        }

        const CATALOGO_COMPLETO = (Array.isArray(CATALOGO_JSON) && CATALOGO_JSON.length > 0 ? CATALOGO_JSON : CATALOGO_BASE_EMBUTIDO)
            .map(normalizarItemCatalogo)
            .filter(item => item.order_no || item.spec);

        const FERRAMENTAS_DB = {
            furacao_inteirica: [
                { id: "mega_drill_steel", nome: "MEGA-Drill-Steel (Aços / Moldes 3xD–12xD)", z: 2, tipo: "broca", ap_factor: 1.0, ae_factor: 1.0, revest: "HP / AlTiSiN", vc_mult: 1.05, f_mult: 1.05 },
                { id: "uni_drill", nome: "UNI-Drill (Universal Multi-Material 3xD–5xD)", z: 2, tipo: "broca", ap_factor: 1.0, ae_factor: 1.0, revest: "TiAlN", vc_mult: 0.92, f_mult: 0.95 },
                { id: "mega_deep_drill", nome: "MEGA-Deep-Drill (Furação Profunda 12xD–30xD)", z: 2, tipo: "broca", ap_factor: 1.0, ae_factor: 1.0, revest: "HP", vc_mult: 0.90, f_mult: 0.88 }
            ],
            fresagem_aco_duro: [
                { id: "optimill_3d_hf", nome: "OptiMill-3D-HF (Acabamento até 68 HRC)", z: 4, tipo: "fresa", ap_factor: 0.05, ae_factor: 0.08, revest: "AlCrSiN", vc_mult: 1.15, f_mult: 1.0 },
                { id: "optimill_3d_cr", nome: "OptiMill-3D-CR (Tórica Cantos / Semi-Acab.)", z: 4, tipo: "fresa", ap_factor: 0.12, ae_factor: 0.25, revest: "AlTiSiN", vc_mult: 1.0, f_mult: 1.0 }
            ],
            fresagem_alto_avanco: [
                { id: "optimill_hfc", nome: "OptiMill-3D-HFC (Alto Avanço 4-6 Cortes)", z: 5, tipo: "fresa", ap_factor: 0.06, ae_factor: 0.65, revest: "AlTiSiN", vc_mult: 1.10, f_mult: 2.8 }
            ],
            fresagem_trocoide: [
                { id: "optimill_trochoid", nome: "OptiMill-Trochoid (Desbaste Dinâmico 2xD-3xD)", z: 5, tipo: "fresa", ap_factor: 2.0, ae_factor: 0.10, revest: "AlTiSiN", vc_mult: 1.25, f_mult: 1.35 }
            ],
            fresagem_aluminio: [
                { id: "optimill_alu", nome: "OptiMill-Alu (3 Cortes Polida Alta Velocidade)", z: 3, tipo: "fresa", ap_factor: 1.2, ae_factor: 0.45, revest: "DLC / Não Revestida", vc_mult: 1.20, f_mult: 1.25 }
            ],
            alargamento: [
                { id: "hpr400", nome: "HPR400 (Alargador Alta Precisão H7)", z: 6, tipo: "alargador", ap_factor: 1.0, ae_factor: 0.03, revest: "TiAlN / Cermet", vc_mult: 1.15, f_mult: 1.6 }
            ]
        };

        const MATERIAIS_ISO = {
            P: [
                { code: "P1.1", nome: "P1.1 - Aço construção não ligado (< 600 N/mm² | St37, C45)", vc_broca: 115, f_broca: 0.22, vc_fresa: 180, fz_fresa: 0.065, kc: 1800 },
                { code: "P2.1", nome: "P2.1 - Aço pré-tratado moldes (950-1150 N/mm² | 1.2311 / 1.2738 / P20)", vc_broca: 85, f_broca: 0.18, vc_fresa: 145, fz_fresa: 0.055, kc: 2250 },
                { code: "P3.1", nome: "P3.1 - Aço ferramenta trabalho a frio/quente (1.2343 / H13 / 1.2379)", vc_broca: 70, f_broca: 0.15, vc_fresa: 120, fz_fresa: 0.048, kc: 2500 }
            ],
            M: [
                { code: "M1.1", nome: "M1.1 - Aço inoxidável austenítico (1.4301 / AISI 304)", vc_broca: 62, f_broca: 0.14, vc_fresa: 105, fz_fresa: 0.045, kc: 2350 },
                { code: "M2.1", nome: "M2.1 - Inox ácido/refratário (1.4404 / AISI 316L / Duplex)", vc_broca: 48, f_broca: 0.12, vc_fresa: 85, fz_fresa: 0.038, kc: 2600 }
            ],
            K: [
                { code: "K1.1", nome: "K1.1 - Ferro fundido cinzento (GG25 / EN-GJL-250)", vc_broca: 125, f_broca: 0.26, vc_fresa: 210, fz_fresa: 0.075, kc: 1350 },
                { code: "K2.1", nome: "K2.1 - Ferro fundido nodular (GGG40 / GGG60)", vc_broca: 95, f_broca: 0.21, vc_fresa: 165, fz_fresa: 0.062, kc: 1650 }
            ],
            N: [
                { code: "N1.1", nome: "N1.1 - Alumínio forjado / aeronáutico (6082 / 7075)", vc_broca: 240, f_broca: 0.30, vc_fresa: 480, fz_fresa: 0.095, kc: 750 },
                { code: "N2.1", nome: "N2.1 - Alumínio fundido com Silício (AlSi10Mg / AlSi12)", vc_broca: 190, f_broca: 0.26, vc_fresa: 360, fz_fresa: 0.080, kc: 880 },
                { code: "N3.1", nome: "N3.1 - Cobre eletrolítico / Latão / Bronze (Elétrodos)", vc_broca: 150, f_broca: 0.20, vc_fresa: 280, fz_fresa: 0.065, kc: 950 }
            ],
            S: [
                { code: "S1.1", nome: "S1.1 - Ligas de Titânio (Ti6Al4V / Grau 5)", vc_broca: 38, f_broca: 0.10, vc_fresa: 65, fz_fresa: 0.035, kc: 2100 },
                { code: "S2.1", nome: "S2.1 - Superligas Níquel (Inconel 718 / Hastelloy)", vc_broca: 26, f_broca: 0.08, vc_fresa: 42, fz_fresa: 0.028, kc: 3100 }
            ],
            H: [
                { code: "H1.1", nome: "H1.1 - Aço temperado (48 - 55 HRC | Stavax / Orvar)", vc_broca: 45, f_broca: 0.09, vc_fresa: 135, fz_fresa: 0.035, kc: 3300 },
                { code: "H2.1", nome: "H2.1 - Aço endurecido (56 - 62 HRC | 1.2379 / Calmax)", vc_broca: 32, f_broca: 0.07, vc_fresa: 105, fz_fresa: 0.028, kc: 3800 },
                { code: "H3.1", nome: "H3.1 - Aço ultra-duro (63 - 68 HRC | PM / Vanadis)", vc_broca: 22, f_broca: 0.05, vc_fresa: 78, fz_fresa: 0.022, kc: 4300 }
            ]
        };

        const REFRIG_LABELS = {
            int: "Interna (IK)",
            ext: "Externa",
            mql: "MQL / Névoa",
            ar: "Ar / Seco"
        };

        let isoAtual = "P";
        let referenciaAtiva = null;
        let modoProAtivo = false;

        function inicializarCatalogo() {
            atualizarDropdownsCascata();
            document.getElementById("contador-referencias").textContent = `${CATALOGO_COMPLETO.length} ref.`;
        }

        function obterTextoPesquisa() {
            return (document.getElementById("ref-pesquisa").value || "").trim().toLowerCase();
        }

        function filtrarListaComExcecao(ignorarCampo = "") {
            const q = obterTextoPesquisa();
            const gama = ignorarCampo === "gama" ? "" : document.getElementById("filtro-gama-cat").value;
            const enc = ignorarCampo === "encabadouro" ? "" : document.getElementById("filtro-encabadouro-cat").value;
            const refrig = ignorarCampo === "refrig" ? "" : document.getElementById("filtro-refrig-cat").value;
            const d1 = ignorarCampo === "d1" ? "" : document.getElementById("filtro-d1").value;
            const xd = ignorarCampo === "xd" ? "" : document.getElementById("filtro-xd").value;

            return CATALOGO_COMPLETO.filter(item => {
                if (gama && item.gama !== gama) return false;
                if (enc && item.encabadouro !== enc) return false;
                if (refrig && item.refrig !== refrig) return false;
                if (d1 && String(item.d1) !== d1) return false;
                if (xd && item.xd !== xd) return false;
                if (q) {
                    const blob = `${item.order_no} ${item.spec} ${item.gama} ${item.familia} ${item.encabadouro} ${item.refrig} ${item.xd} ${item.d1} ${item.desc}`.toLowerCase();
                    const tokens = q.split(/\s+/).filter(Boolean);
                    if (!tokens.every(t => blob.includes(t))) return false;
                }
                return true;
            });
        }

        function atualizarVisibilidadeDiametroManual() {
            const d1Filtro = document.getElementById("filtro-d1").value;
            const temDiametroNoCatalogo = Boolean(d1Filtro) || Boolean(referenciaAtiva && referenciaAtiva.d1 > 0);
            const bloco = document.getElementById("bloco-diametro-manual");
            if (temDiametroNoCatalogo) {
                bloco.classList.add("hidden");
            } else {
                bloco.classList.remove("hidden");
            }
        }

        function atualizarDropdownsCascata() {
            const selGama = document.getElementById("filtro-gama-cat");
            const selEnc = document.getElementById("filtro-encabadouro-cat");
            const selRefrig = document.getElementById("filtro-refrig-cat");
            const selD1 = document.getElementById("filtro-d1");
            const selXd = document.getElementById("filtro-xd");
            const selOrder = document.getElementById("filtro-order-no");

            const valGama = selGama.value;
            const valEnc = selEnc.value;
            const valRefrig = selRefrig.value;
            const valD1 = selD1.value;
            const valXd = selXd.value;
            const valOrder = selOrder.value;

            const gamasDisp = [...new Set(filtrarListaComExcecao("gama").map(i => i.gama).filter(Boolean))].sort();
            selGama.innerHTML = `<option value="">Todas (${gamasDisp.length})</option>` +
                gamasDisp.map(g => `<option value="${g}" ${g === valGama ? "selected" : ""}>${g}</option>`).join("");

            const encDisp = [...new Set(filtrarListaComExcecao("encabadouro").map(i => i.encabadouro).filter(Boolean))].sort();
            selEnc.innerHTML = `<option value="">Todos (HA/HB/HE)</option>` +
                encDisp.map(e => `<option value="${e}" ${e === valEnc ? "selected" : ""}>DIN 6535 ${e}</option>`).join("");

            const refrigDisp = [...new Set(filtrarListaComExcecao("refrig").map(i => i.refrig).filter(Boolean))];
            selRefrig.innerHTML = `<option value="">Todas</option>` +
                refrigDisp.map(r => `<option value="${r}" ${r === valRefrig ? "selected" : ""}>${REFRIG_LABELS[r] || r.toUpperCase()}</option>`).join("");

            const d1Disp = [...new Set(filtrarListaComExcecao("d1").map(i => i.d1).filter(v => v > 0))].sort((a, b) => a - b);
            selD1.innerHTML = `<option value="">Todos</option>` +
                d1Disp.map(d => `<option value="${d}" ${String(d) === valD1 ? "selected" : ""}>Ø ${d.toFixed(2).replace(/\.00$/, ".0")} mm</option>`).join("");

            const xdDisp = [...new Set(filtrarListaComExcecao("xd").map(i => i.xd).filter(Boolean))]
                .sort((a, b) => (parseInt(a, 10) || 0) - (parseInt(b, 10) || 0));
            selXd.innerHTML = `<option value="">Todas</option>` +
                xdDisp.map(x => `<option value="${x}" ${x === valXd ? "selected" : ""}>${x}</option>`).join("");

            const filtrados = filtrarListaComExcecao("");
            document.getElementById("contador-referencias").textContent = `${filtrados.length} ref.`;

            selOrder.innerHTML = `<option value="">— Selecionar referência (${filtrados.length}) —</option>` +
                filtrados.slice(0, 250).map(item => {
                    const labelRefrig = item.refrig === "int" ? "IK" : "EXT";
                    return `<option value="${item.order_no}" ${item.order_no === valOrder ? "selected" : ""}>${item.order_no} | ${item.spec} | Ø${item.d1} | ${item.encabadouro} | ${labelRefrig}</option>`;
                }).join("");

            atualizarVisibilidadeDiametroManual();
        }

        function onFiltroCatalogoChange(origem) {
            if (origem === "d1") {
                const d1Val = parseFloat(document.getElementById("filtro-d1").value);
                if (!isNaN(d1Val) && d1Val > 0) {
                    document.getElementById("diametro-input").value = d1Val;
                    document.getElementById("diametro-slider").value = Math.min(32, Math.max(0.5, d1Val));
                    document.getElementById("lbl-diametro").textContent = `${d1Val.toFixed(2).replace(/\.00$/, ".0")} mm`;
                }
            }
            if (origem === "refrig") {
                const rVal = document.getElementById("filtro-refrig-cat").value;
                if (rVal) {
                    document.getElementById("refrigeracao").value = rVal;
                }
            }
            atualizarDropdownsCascata();
            const filtrados = filtrarListaComExcecao("");
            if (filtrados.length === 1) {
                document.getElementById("filtro-order-no").value = filtrados[0].order_no;
                aplicarItemCatalogo(filtrados[0]);
            } else {
                calcular();
            }
        }

        function filtrarCatalogoCascata() {
            atualizarDropdownsCascata();
        }

        function aplicarPesquisaReferencia() {
            const filtrados = filtrarListaComExcecao("");
            const fb = document.getElementById("ref-feedback");
            if (filtrados.length === 0) {
                fb.textContent = "Nenhuma referência encontrada com os filtros atuais.";
                fb.className = "text-[10px] text-rose-400 block";
                return;
            }
            const selecionado = filtrados[0];
            document.getElementById("filtro-order-no").value = selecionado.order_no;
            aplicarItemCatalogo(selecionado);
            fb.textContent = `Referência aplicada: ${selecionado.order_no} (${selecionado.spec})`;
            fb.className = "text-[10px] text-emerald-400 block";
        }

        function onSelecionarOrderCatalogo() {
            const orderNo = document.getElementById("filtro-order-no").value;
            if (!orderNo) {
                referenciaAtiva = null;
                document.getElementById("card-ficha-referencia").classList.add("hidden");
                atualizarVisibilidadeDiametroManual();
                calcular();
                return;
            }
            const item = CATALOGO_COMPLETO.find(i => i.order_no === orderNo);
            if (item) {
                aplicarItemCatalogo(item);
            }
        }

        function aplicarItemCatalogo(item) {
            referenciaAtiva = item;

            if (item.categoria && FERRAMENTAS_DB[item.categoria]) {
                document.getElementById("categoria").value = item.categoria;
                popularFerramentas();
                if (item.ferramenta_id) {
                    const selF = document.getElementById("ferramenta");
                    if ([...selF.options].some(o => o.value === item.ferramenta_id)) {
                        selF.value = item.ferramenta_id;
                    }
                }
            }

            if (item.d1 > 0) {
                document.getElementById("diametro-input").value = item.d1;
                document.getElementById("diametro-slider").value = Math.min(32, Math.max(0.5, item.d1));
                document.getElementById("lbl-diametro").textContent = `${item.d1.toFixed(2).replace(/\.00$/, ".0")} mm`;
            }

            if (item.refrig) {
                document.getElementById("refrigeracao").value = item.refrig;
            }

            const multXd = parseInt(item.xd, 10);
            if (!isNaN(multXd) && multXd > 0 && item.d1 > 0) {
                document.getElementById("profundidade").value = Math.round(item.d1 * multXd);
            } else if (item.l3 > 0) {
                document.getElementById("profundidade").value = Math.round(item.l3);
            }

            const card = document.getElementById("card-ficha-referencia");
            card.classList.remove("hidden");
            document.getElementById("ref-badge-gama").textContent = item.gama;
            document.getElementById("ref-badge-encabadouro").textContent = `DIN 6535 ${item.encabadouro}`;
            document.getElementById("ref-badge-refrig").textContent = item.refrig === "int" ? "Refrig. Interna (IK)" : "Refrig. Externa";
            document.getElementById("ref-badge-xd").textContent = item.xd || "Standard";
            document.getElementById("ref-titulo-spec").textContent = item.spec;
            document.getElementById("ref-subtitulo-desc").textContent = item.desc;
            document.getElementById("ref-order-no-destaque").textContent = item.order_no;

            document.getElementById("ref-cota-d1").textContent = item.d1 ? `${item.d1} mm` : "—";
            document.getElementById("ref-cota-d2").textContent = item.d2 ? `${item.d2} mm` : "—";
            document.getElementById("ref-cota-l1").textContent = item.l1 ? `${item.l1} mm` : "—";
            document.getElementById("ref-cota-l2").textContent = item.l2 ? `${item.l2} mm` : "—";
            document.getElementById("ref-cota-l3").textContent = item.l3 ? `${item.l3} mm` : "—";
            document.getElementById("ref-cota-shank").textContent = `DIN 6535 ${item.encabadouro}`;

            atualizarVisibilidadeDiametroManual();
            calcular();
        }

        function limparFiltrosCatalogo() {
            document.getElementById("ref-pesquisa").value = "";
            document.getElementById("filtro-gama-cat").value = "";
            document.getElementById("filtro-encabadouro-cat").value = "";
            document.getElementById("filtro-refrig-cat").value = "";
            document.getElementById("filtro-d1").value = "";
            document.getElementById("filtro-xd").value = "";
            document.getElementById("filtro-order-no").value = "";
            referenciaAtiva = null;
            document.getElementById("card-ficha-referencia").classList.add("hidden");
            document.getElementById("ref-feedback").textContent = "Filtros limpos. Selecione pelo catálogo ou configure manualmente.";
            document.getElementById("ref-feedback").className = "text-[10px] text-slate-400 block";
            atualizarDropdownsCascata();
            calcular();
        }

        function popularFerramentas() {
            const cat = document.getElementById("categoria").value;
            const lista = FERRAMENTAS_DB[cat] || [];
            const sel = document.getElementById("ferramenta");
            sel.innerHTML = lista.map(f => `<option value="${f.id}">${f.nome}</option>`).join("");
        }

        function onCategoriaChange() {
            popularFerramentas();
            calcular();
        }

        function onFerramentaChange() {
            calcular();
        }

        function selectISO(iso) {
            isoAtual = iso;
            document.querySelectorAll(".iso-btn").forEach(btn => {
                const active = btn.dataset.iso === iso;
                btn.className = active
                    ? "iso-btn py-1 rounded text-xs font-bold border border-blue-400 bg-blue-600 text-white"
                    : "iso-btn py-1 rounded text-xs font-bold border border-slate-600 bg-slate-900 text-slate-300";
            });
            popularMateriais();
            calcular();
        }

        function popularMateriais() {
            const lista = MATERIAIS_ISO[isoAtual] || [];
            const sel = document.getElementById("material");
            sel.innerHTML = lista.map((m, idx) => `<option value="${idx}">${m.nome}</option>`).join("");
        }

        function onMaterialChange() {
            calcular();
        }

        function syncDiametro(origem) {
            const slider = document.getElementById("diametro-slider");
            const input = document.getElementById("diametro-input");
            let val = origem === "slider" ? parseFloat(slider.value) : parseFloat(input.value);
            if (isNaN(val) || val <= 0) val = 1.0;
            if (origem === "slider") input.value = val;
            else slider.value = Math.min(32, Math.max(0.5, val));
            document.getElementById("lbl-diametro").textContent = `${val.toFixed(2).replace(/\.00$/, ".0")} mm`;
            calcular();
        }

        function resetAjustes() {
            document.getElementById("adj-vc").value = 100;
            document.getElementById("adj-f").value = 100;
            calcular();
        }

        function resetRapidoTudo() {
            resetAjustes();
            document.getElementById("max-rpm").value = 18000;
            document.getElementById("estabilidade").value = "1.0";
            calcular();
        }

        function obterFerramentaAtual() {
            const cat = document.getElementById("categoria").value;
            const fId = document.getElementById("ferramenta").value;
            const lista = FERRAMENTAS_DB[cat] || [];
            return lista.find(f => f.id === fId) || lista[0];
        }

        function calcular() {
            const ferr = obterFerramentaAtual();
            const matLista = MATERIAIS_ISO[isoAtual] || MATERIAIS_ISO.P;
            const matIdx = parseInt(document.getElementById("material").value, 10) || 0;
            const mat = matLista[matIdx] || matLista[0];

            const d = referenciaAtiva && referenciaAtiva.d1 > 0
                ? referenciaAtiva.d1
                : (parseFloat(document.getElementById("diametro-input").value) || 8.0);
            const prof = parseFloat(document.getElementById("profundidade").value) || 24;
            const refrig = document.getElementById("refrigeracao").value;
            const maxRpm = parseFloat(document.getElementById("max-rpm").value) || 18000;
            const estab = parseFloat(document.getElementById("estabilidade").value) || 1.0;
            const adjVc = (parseFloat(document.getElementById("adj-vc").value) || 100) / 100;
            const adjF = (parseFloat(document.getElementById("adj-f").value) || 100) / 100;

            document.getElementById("lbl-adj-vc").textContent = `${Math.round(adjVc * 100)}%`;
            document.getElementById("lbl-adj-f").textContent = `${Math.round(adjF * 100)}%`;

            const z = referenciaAtiva && referenciaAtiva.z ? referenciaAtiva.z : ferr.z;
            const isBroca = ferr.tipo === "broca" || ferr.tipo === "alargador";

            let vcBase = isBroca ? mat.vc_broca : mat.vc_fresa;
            let fBase = isBroca ? mat.f_broca * (d / 8.0) ** 0.55 : mat.fz_fresa * (d / 8.0) ** 0.35;

            const refrigMultVc = refrig === "int" ? 1.05 : refrig === "ext" ? 0.90 : refrig === "mql" ? 0.95 : 0.85;
            const refrigMultF = refrig === "int" ? 1.0 : refrig === "ext" ? 0.88 : 0.92;

            const ld = prof / d;
            const ldMult = ld > 8 ? 0.78 : ld > 5 ? 0.88 : 1.0;

            const vc = Math.max(8, vcBase * ferr.vc_mult * refrigMultVc * ldMult * estab * adjVc);
            const fUnit = Math.max(0.008, fBase * ferr.f_mult * refrigMultF * ldMult * estab * adjF);

            const rpmCalc = (vc * 1000) / (Math.PI * d);
            const rpmFinal = Math.min(rpmCalc, maxRpm);
            const limitado = rpmCalc > maxRpm;

            const fRev = isBroca ? fUnit : fUnit * z;
            const vf = rpmFinal * fRev;

            const ap = isBroca ? prof : +(d * ferr.ap_factor).toFixed(2);
            const ae = isBroca ? d : +(d * ferr.ae_factor).toFixed(2);

            const qCm3 = isBroca
                ? ((Math.PI * (d ** 2) / 4) * vf) / 1000
                : (ap * ae * vf) / 1000;

            const pcKw = (qCm3 * mat.kc) / (60000 * 0.82);
            const mcNm = rpmFinal > 0 ? (pcKw * 9550) / rpmFinal : 0;
            const tempo100s = vf > 0 ? (100 / vf) * 60 : 0;

            document.getElementById("res-rpm").textContent = Math.round(rpmFinal).toLocaleString("pt-PT");
            document.getElementById("alerta-rpm").classList.toggle("hidden", !limitado);

            document.getElementById("res-vf").textContent = Math.round(vf).toLocaleString("pt-PT");
            document.getElementById("res-f-rev").textContent = `f = ${fRev.toFixed(3)} mm/rot`;

            document.getElementById("res-vc").textContent = vc.toFixed(1);
            document.getElementById("res-vc-range").textContent = `Faixa base: ${(vc * 0.85).toFixed(0)} - ${(vc * 1.15).toFixed(0)} m/min`;

            document.getElementById("lbl-avanco-unit").textContent = isBroca ? "Avanço / Rotação (f)" : "Avanço / Dente (fz)";
            document.getElementById("unit-fz").textContent = isBroca ? "mm/rot" : "mm/dente";
            document.getElementById("res-fz").textContent = fUnit.toFixed(3);
            document.getElementById("res-z-info").textContent = `Z = ${z} arestas | Ø ${d.toFixed(2).replace(/\.00$/, ".0")} mm`;

            document.getElementById("lbl-ap").textContent = isBroca ? "Profundidade Furo (Z)" : "Profundidade Axial (ap)";
            document.getElementById("res-ap").textContent = `${ap} mm`;
            document.getElementById("lbl-ae").textContent = isBroca ? "Diâmetro Furo (Ø)" : "Largura Radial (ae)";
            document.getElementById("res-ae").textContent = `${ae} mm`;
            document.getElementById("res-ld").textContent = `${ld.toFixed(1)} × D`;
            document.getElementById("res-q").textContent = `${qCm3.toFixed(1)} cm³/min`;

            document.getElementById("res-potencia").textContent = `${pcKw.toFixed(2)} kW`;
            document.getElementById("res-binario").textContent = `${mcNm.toFixed(1)} Nm`;
            document.getElementById("res-tempo").textContent = `${tempo100s.toFixed(1)} s`;
            document.getElementById("res-pressao").textContent = refrig === "int" ? (d < 5 ? "40 - 70 bar" : "20 - 40 bar") : "Jato direcionado";
            document.getElementById("badge-revestimento").textContent = `Revestimento: ${ferr.revest}`;

            const notas = [
                `Material ISO ${isoAtual} (${mat.code}): aplicar avanço constante sem paragens no fundo do furo/corte.`,
                refrig === "int"
                    ? "Refrigeração interna ativa: garantir filtragem ≤ 20 µm para evitar entupimento dos canais."
                    : "Sem refrigeração interna: reduzir profundidade contínua e garantir evacuação de apara.",
                isBroca
                    ? (ld <= 5 ? "Furação direta sem descarga (pecking) recomendada até 5×D com refrigeração interna." : "Furo profundo (>5×D): executar furo piloto 1.5×D a 2×D antes da broca longa.")
                    : "Entrada em rampa helicoidal ou arco tangencial para proteger as arestas de corte."
            ];
            document.getElementById("lista-notas").innerHTML = notas.map(n => `<li>${n}</li>`).join("");

            const alertaPiloto = document.getElementById("alerta-furo-piloto");
            if (isBroca && ld > 5.5) {
                alertaPiloto.classList.remove("hidden");
                alertaPiloto.innerHTML = `<strong>⚠️ Atenção Furação Profunda (${ld.toFixed(1)}×D):</strong> Executar furo piloto prévio Ø ${d.toFixed(2)} mm (prof. ${(d * 2).toFixed(1)} mm) com broca 3×D da mesma família, entrar a 300–500 rpm sem refrigeração de alta pressão e ligar IK 1–2 mm antes do fundo do piloto.`;
            } else {
                alertaPiloto.classList.add("hidden");
            }
        }

        function gerirModoPro() {
            if (modoProAtivo) {
                modoProAtivo = false;
                atualizarUIPro();
                return;
            }
            document.getElementById("erro-pro-pass").classList.add("hidden");
            document.getElementById("input-pro-pass").value = "";
            document.getElementById("modal-pro").classList.remove("hidden");
        }

        function validarPro() {
            const val = document.getElementById("input-pro-pass").value;
            if (!PRO_PASSWORD || val === PRO_PASSWORD) {
                modoProAtivo = true;
                fecharModal("modal-pro");
                atualizarUIPro();
            } else {
                document.getElementById("erro-pro-pass").classList.remove("hidden");
            }
        }

        function atualizarUIPro() {
            const badge = document.getElementById("badge-nivel-ativo");
            const btn = document.getElementById("btn-modo-pro");
            const btnComp = document.getElementById("btn-comparar-familia");
            const lblExp = document.getElementById("lbl-btn-export");
            if (modoProAtivo) {
                badge.textContent = "Nível Pro Ativo";
                badge.className = "text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-500";
                btn.innerHTML = "<span>🔓</span> Sair Modo Pro";
                btnComp.classList.remove("hidden");
                lblExp.textContent = "Proposta Comercial PDF";
            } else {
                badge.textContent = "Nível Básico";
                badge.className = "text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-700 text-cyan-300 border border-slate-600";
                btn.innerHTML = "<span>🔒</span> Aderir Nível Pro";
                btnComp.classList.add("hidden");
                lblExp.textContent = "Exportar PDF";
            }
        }

        function abrirModalComparacao() {
            const ferr = obterFerramentaAtual();
            const rpm = document.getElementById("res-rpm").textContent;
            const vf = document.getElementById("res-vf").textContent;
            const vc = document.getElementById("res-vc").textContent;
            const q = document.getElementById("res-q").textContent;
            document.getElementById("conteudo-comparacao").innerHTML = `
                <table class="w-full border-collapse text-left">
                    <thead>
                        <tr class="border-b border-slate-700 text-slate-400">
                            <th class="py-2">Parâmetro</th>
                            <th class="py-2 text-emerald-400">MAPAL (${ferr.nome})</th>
                            <th class="py-2 text-slate-400">Solução Standard (-22%)</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-700/70">
                        <tr><td class="py-2">Velocidade de Corte (Vc)</td><td class="font-bold text-white">${vc} m/min</td><td>${(parseFloat(vc) * 0.78).toFixed(1)} m/min</td></tr>
                        <tr><td class="py-2">Rotação (n)</td><td class="font-bold text-white">${rpm} rpm</td><td>~78%</td></tr>
                        <tr><td class="py-2">Avanço de Mesa (Vf)</td><td class="font-bold text-emerald-400">${vf} mm/min</td><td>~72%</td></tr>
                        <tr><td class="py-2">Taxa Remoção (Q)</td><td class="font-bold text-cyan-300">${q}</td><td>~72%</td></tr>
                    </tbody>
                </table>
            `;
            document.getElementById("modal-comparacao").classList.remove("hidden");
        }

        function abrirModalExportacao() {
            document.getElementById("modal-export").classList.remove("hidden");
        }

        function fecharModal(id) {
            document.getElementById(id).classList.add("hidden");
        }

        function gerarPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            const ferr = obterFerramentaAtual();
            const cliente = document.getElementById("pdf-cliente").value || "Cliente Industrial";
            const projeto = document.getElementById("pdf-projeto").value || "Aplicação CNC";
            const notas = document.getElementById("pdf-notas").value || "";

            doc.setFontSize(16);
            doc.text(modoProAtivo ? "PROPOSTA TÉCNICA & PARÂMETROS MAPAL" : "FICHA DE PARÂMETROS DE CORTE MAPAL", 14, 18);
            doc.setFontSize(10);
            doc.text(`Álamo Ferramentas | Representante Exclusivo MAPAL Portugal`, 14, 25);
            doc.text(`Cliente: ${cliente}   |   Projeto: ${projeto}`, 14, 33);
            if (referenciaAtiva) {
                doc.text(`Referência MAPAL: ${referenciaAtiva.order_no} - ${referenciaAtiva.spec} (${referenciaAtiva.gama})`, 14, 40);
            } else {
                doc.text(`Ferramenta: ${ferr.nome}`, 14, 40);
            }
            doc.text(`Rotação (n): ${document.getElementById("res-rpm").textContent} rpm`, 14, 52);
            doc.text(`Avanço Mesa (Vf): ${document.getElementById("res-vf").textContent} mm/min`, 14, 59);
            doc.text(`Velocidade Corte (Vc): ${document.getElementById("res-vc").textContent} m/min`, 14, 66);
            doc.text(`Avanço Unitário: ${document.getElementById("res-fz").textContent} ${document.getElementById("unit-fz").textContent}`, 14, 73);
            doc.text(`Taxa Remoção (Q): ${document.getElementById("res-q").textContent}   |   Potência: ${document.getElementById("res-potencia").textContent}`, 14, 80);
            if (notas) {
                doc.text(`Notas: ${notas}`, 14, 92, { maxWidth: 180 });
            }
            doc.save(`MAPAL_Parametros_${referenciaAtiva ? referenciaAtiva.order_no : "CNC"}.pdf`);
            fecharModal("modal-export");
        }

        function toggleFullScreen() {
            if (!document.fullscreenElement) document.documentElement.requestFullscreen();
            else if (document.exitFullscreen) document.exitFullscreen();
        }

        // Inicialização
        popularFerramentas();
        popularMateriais();
        inicializarCatalogo();
        calcular();
    </script>
</body>
</html>
'''

components.html(html_content, height=900, scrolling=False)