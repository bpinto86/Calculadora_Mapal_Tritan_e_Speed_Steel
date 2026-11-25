import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import base64

def load_image_base64(filename: str) -> str:
    p = Path(filename)
    if not p.exists():
        return ""
    ext = p.suffix.lower().lstrip(".") or "png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/{ext};base64,{b64}"

logo_alamo_b64 = load_image_base64("Logotipo Alamo.png")
logo_mapal_b64 = load_image_base64("Logotipo Mapal.png")

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


familias_catalogo = load_json_safe("dados/familias.json")
referencias_catalogo = load_json_safe("dados/referencias.json")
parametros_furacao_json = load_json_safe("dados/furacao_parametros.json")
grupos_mmg_json = load_json_safe("dados/grupos_mmg.json")

pro_password_js = json.dumps(pro_password)
familias_js = json.dumps(familias_catalogo, ensure_ascii=False)
referencias_js = json.dumps(referencias_catalogo, ensure_ascii=False)
parametros_json_js = json.dumps(parametros_furacao_json, ensure_ascii=False)
grupos_mmg_js = json.dumps(grupos_mmg_json, ensure_ascii=False)

html_content = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Parâmetros de Corte MAPAL & Proposta Comercial PDF</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 0; height: 100vh; overflow: hidden; }
        .iso-btn {
            font-weight: 800;
            border-radius: 7px;
            padding: 6px 4px;
            font-size: 12px;
            line-height: 1;
            transition: all 0.14s ease;
            border: 1.5px solid #334155;
            background-color: #0f172a;
            cursor: pointer;
            text-align: center;
        }
        .iso-btn:hover:not(:disabled) {
            transform: translateY(-1px);
            filter: brightness(1.12);
        }
        .iso-btn:disabled {
            opacity: 0.25;
            cursor: not-allowed;
        }
        .sub-btn {
            font-weight: 700;
            border-radius: 6px;
            padding: 4px 6px;
            font-size: 10.5px;
            line-height: 1.1;
            transition: all 0.12s ease;
            border: 1px solid #334155;
            background-color: #0f172a;
            cursor: pointer;
            text-align: center;
        }
        .sub-btn:hover:not(:disabled) {
            filter: brightness(1.15);
        }
        .sub-btn:disabled {
            opacity: 0.25;
            cursor: not-allowed;
        }
        .mmg-code-btn {
            font-weight: 700;
            border-radius: 6px;
            padding: 4px 7px;
            font-size: 10px;
            line-height: 1.15;
            transition: all 0.12s ease;
            border: 1px solid #334155;
            background-color: #0f172a;
            cursor: pointer;
            text-align: left;
        }
        .mmg-code-btn:hover:not(:disabled) {
            filter: brightness(1.15);
        }
        .mmg-code-btn:disabled {
            opacity: 0.25;
            cursor: not-allowed;
        }
        .gauge-needle {
            transform-box: view-box;
            transform-origin: 100px 100px;
            transform: rotate(-90deg);
            transition: transform 0.35s ease-out;
        }
    </style>
</head>
<body class="h-screen p-2 flex flex-col box-border">
    <div class="w-full h-full flex flex-col gap-2">
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
                <button onclick="abrirModalPdfParametros()" class="bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white transition flex items-center gap-1.5">
                    <span>📋</span> Gerar PDF com parâmetros de corte
                </button>
                <button onclick="abrirModalExportacao()" class="bg-blue-600 hover:bg-blue-500 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>📄</span> <span id="lbl-btn-export">Exportar PDF</span>
                </button>
                <button onclick="toggleFullScreen()" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded-md text-xs font-medium text-white transition flex items-center gap-1.5">
                    <span>⛶</span> Ecrã Inteiro
                </button>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0">
            <div class="lg:col-span-4 bg-slate-800 p-3.5 rounded-lg border border-slate-700 flex flex-col gap-2.5 overflow-y-auto min-h-0">
                <h2 class="text-xs font-semibold text-blue-400 uppercase tracking-wider shrink-0">Configuração da Operação</h2>

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

                <div class="bg-slate-900/70 p-2.5 rounded-md border border-slate-700/80 space-y-2 shrink-0">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Seleção Progressiva do Catálogo</span>
                        <span id="contador-referencias" class="text-[10px] text-slate-400 font-mono">0 ref.</span>
                    </div>

                    <div class="bg-slate-950/75 p-2 rounded-md border border-blue-900/50 space-y-1.5">
                        <div class="flex justify-between items-center gap-1">
                            <label class="text-[10px] font-semibold text-blue-300 uppercase tracking-wider">1. Grupo de Materiais (MMG)</label>
                            <span id="mmg-selecao-detalhe" class="text-[10px] font-mono text-slate-300 truncate max-w-[175px]">—</span>
                        </div>

                        <div id="mmg-botoes-grupo" class="grid grid-cols-6 gap-1"></div>

                        <div id="mmg-painel-subgrupo" class="hidden space-y-1 pt-1 border-t border-slate-800/90">
                            <div class="flex justify-between items-center">
                                <span id="mmg-label-subgrupo" class="text-[9.5px] font-semibold text-slate-400 uppercase">Subgrupo</span>
                                <span id="mmg-materiais-freq" class="text-[9px] text-slate-400 truncate max-w-[190px]"></span>
                            </div>
                            <div id="mmg-botoes-subgrupo" class="flex flex-wrap gap-1"></div>
                        </div>

                        <div id="mmg-painel-codigo" class="hidden space-y-1 pt-1 border-t border-slate-800/90">
                            <div class="flex justify-between items-center">
                                <span id="mmg-label-codigo" class="text-[9.5px] font-semibold text-slate-400 uppercase">Grupo MAPAL (MMG)</span>
                                <span id="mmg-detalhe-codigo" class="text-[9px] text-cyan-300 truncate max-w-[185px]"></span>
                            </div>
                            <div id="mmg-botoes-codigo" class="flex flex-wrap gap-1 max-h-24 overflow-y-auto"></div>
                        </div>

                        <select id="grupo" class="hidden" onchange="onSelectGrupoManual()"></select>
                    </div>

                    <div id="mmg2-box" class="bg-slate-950/75 p-2 rounded-md border border-teal-900/50 space-y-1.5">
                        <div class="flex justify-between items-center gap-1">
                            <label class="text-[10px] font-semibold text-teal-300 uppercase tracking-wider">2. Novo Grupo de Materiais (MMG) ISO DIN ISO 513</label>
                            <span id="mmg2-selecao-detalhe" class="text-[10px] font-mono text-slate-300 truncate max-w-[175px]">—</span>
                        </div>

                        <div id="mmg2-botoes-grupo" class="grid grid-cols-6 gap-1"></div>

                        <div id="mmg2-painel-subgrupo" class="hidden space-y-1 pt-1 border-t border-slate-800/90">
                            <div class="flex justify-between items-center">
                                <span id="mmg2-label-subgrupo" class="text-[9.5px] font-semibold text-slate-400 uppercase">Subgrupo</span>
                                <span id="mmg2-materiais-freq" class="text-[9px] text-slate-400 truncate max-w-[190px]"></span>
                            </div>
                            <div id="mmg2-botoes-subgrupo" class="flex flex-wrap gap-1"></div>
                        </div>

                        <div id="mmg2-painel-codigo" class="hidden space-y-1 pt-1 border-t border-slate-800/90">
                            <div class="flex justify-between items-center">
                                <span id="mmg2-label-codigo" class="text-[9.5px] font-semibold text-slate-400 uppercase">Grupo MAPAL (MMG)</span>
                                <span id="mmg2-detalhe-codigo" class="text-[9px] text-teal-300 truncate max-w-[185px]"></span>
                            </div>
                            <div id="mmg2-botoes-codigo" class="flex flex-wrap gap-1 max-h-24 overflow-y-auto"></div>
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-1.5">
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">1. Tipo Operação</label>
                            <select id="categoria" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-purple-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('categoria')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">2. Gama / Linha</label>
                            <select id="filtro-gama-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('gama')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">3. Refrigeração</label>
                            <select id="filtro-refrig-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-sky-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('refrig')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-3 gap-1.5">
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">4. DIN 6535</label>
                            <select id="filtro-encabadouro-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-amber-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('encabadouro')">
                                <option value="">Todos</option>
                            </select>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">5. Diâmetro d1</label>
                            <input type="number" id="filtro-d1" list="lista-d1-sugestoes" step="0.01" min="0.1" max="100" placeholder="Ex: 10.00" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" oninput="onFiltroCatalogoChange('d1')" onchange="onFiltroCatalogoChange('d1')">
                            <datalist id="lista-d1-sugestoes"></datalist>
                        </div>
                        <div class="space-y-0.5">
                            <label class="text-[10px] font-medium text-slate-300 block">6. Variante ×D</label>
                            <select id="filtro-xd" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-cyan-300 font-semibold focus:outline-none focus:border-emerald-500" onchange="onFiltroCatalogoChange('xd')">
                                <option value="">Todas</option>
                            </select>
                        </div>
                    </div>
                    <div class="space-y-0.5">
                        <div class="flex justify-between items-center">
                            <label class="text-[10px] font-medium text-slate-300 block">7. Modelo de Ferramenta</label>
                            <span id="info-modelo-filtro" class="text-[9px] text-cyan-400 font-mono"></span>
                        </div>
                        <select id="broca" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onMudarModeloFerramenta()">
                            <option value="">— Vazio (sem modelo selecionado) —</option>
                        </select>
                    </div>
                    <div class="space-y-0.5">
                        <label class="text-[10px] font-medium text-slate-300 block">8. Referência / Order no.</label>
                        <select id="filtro-order-no" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-emerald-500" onchange="onSelecionarOrderCatalogo()">
                            <option value="">— Selecionar referência compatível —</option>
                        </select>
                    </div>
                </div>

                <div class="bg-slate-900 p-2 rounded-md border border-slate-700/80 space-y-0.5 shrink-0">
                    <label class="flex items-start gap-1.5 cursor-pointer text-[11px] text-slate-300">
                        <input type="checkbox" id="liga-check" class="mt-0.5 rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-0" onchange="atualizarCalculo()">
                        <span><strong>Soma liga (Cr, Mo, Ni, V, W) &gt; 8%</strong><br><span class="text-[9px] text-amber-400">Regra MAPAL: avança para o grupo seguinte.</span></span>
                    </label>
                </div>

                <div class="space-y-1 shrink-0">
                    <label class="text-[11px] font-medium text-slate-300">3. MÉTODO DE REFRIGERAÇÃO A USAR</label>
                    <div class="grid grid-cols-4 gap-1 bg-slate-900 p-1 rounded-md border border-slate-700 text-[11px] text-center font-medium">
                        <button type="button" onclick="setRefrig('int')" id="ref-int" class="py-1.5 rounded bg-blue-600 text-white transition">Interna</button>
                        <button type="button" onclick="setRefrig('ext')" id="ref-ext" class="py-1.5 rounded text-slate-400 hover:text-white transition">Externa</button>
                        <button type="button" onclick="setRefrig('mql')" id="ref-mql" class="py-1.5 rounded text-slate-400 hover:text-white transition">MQL</button>
                        <button type="button" onclick="setRefrig('ar')" id="ref-ar" class="py-1.5 rounded text-slate-400 hover:text-white transition">Ar</button>
                    </div>
                    <p id="aviso-refrig" class="text-[9px] text-amber-400 hidden">Nota: Esta ferramenta não permite refrigeração interna.</p>
                </div>

                <div class="grid grid-cols-2 gap-2 shrink-0">
                    <div id="bloco-diametro-manual" class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">4. DIÂMETRO (Ø)</label>
                        <div class="flex items-center gap-1">
                            <button onclick="ajustarDiametro(-0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">-</button>
                            <input type="number" id="diametro" value="12.00" step="0.1" min="0.5" max="30" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white focus:outline-none focus:border-blue-500" oninput="onDiametroPrincipalChange()">
                            <button onclick="ajustarDiametro(0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">+</button>
                        </div>
                    </div>
                    <div id="bloco-diametro-catalogo" class="space-y-1 hidden">
                        <label class="text-[11px] font-medium text-emerald-400">4. DIÂMETRO (Ø) — d1</label>
                        <div class="bg-slate-900/90 border border-emerald-700/60 rounded-md p-1.5 text-center flex items-center justify-between px-2">
                            <div id="diametro-catalogo-valor" class="text-sm font-bold text-emerald-300">Ø 12.00 mm</div>
                            <button type="button" onclick="limparDiametroD1()" title="Limpar d1 e voltar ao Ø livre" class="text-[10px] text-slate-400 hover:text-white underline">Livre</button>
                        </div>
                    </div>
                    <div class="space-y-1">
                        <label class="text-[11px] font-medium text-slate-300">5. PROFUNDIDADE/FURO (L)</label>
                        <div class="flex items-center gap-1">
                            <input type="number" id="profundidade" value="31.0" step="1" min="0.1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                            <span class="text-[10px] text-slate-400 font-medium">mm</span>
                        </div>
                    </div>
                </div>

                <div id="alerta-profundidade" class="bg-slate-900 px-2.5 py-1.5 rounded-md border border-slate-700 text-[10px] text-slate-200 flex justify-between items-center gap-2 shrink-0">
                    <span id="texto-limite-prof">Profundidade a validar com catálogo</span>
                    <span id="badge-limite-prof" class="font-bold text-amber-400 shrink-0">VALIDAR</span>
                </div>

                <div class="pro-only hidden space-y-2.5 shrink-0">
                    <div class="grid grid-cols-2 gap-2 pt-1">
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">6. QTD. FUROS (LOTE)</label>
                            <input type="number" id="qtd-furos" value="50" step="1" min="1" max="100000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">7. DENSIDADE (g/cm³)</label>
                            <input type="number" id="densidade" value="7.85" step="0.01" min="0.5" max="25" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                    </div>

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
                            <label class="text-[11px] font-medium text-slate-300">8. VALOR SUCATA (€/kg)</label>
                            <input type="number" id="preco-sucata" value="0.35" step="0.05" min="0" max="50" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                        <div class="space-y-1">
                            <label class="text-[11px] font-medium text-slate-300">9. CUSTO HORA MÁQUINA (€/h)</label>
                            <input type="number" id="custo-hora" value="50.00" step="5" min="1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white focus:outline-none focus:border-blue-500" oninput="atualizarCalculo()">
                        </div>
                    </div>
                </div>

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

            <div class="lg:col-span-8 flex flex-col gap-2.5 min-h-0 overflow-y-auto">
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

                <div class="grid grid-cols-2 md:grid-cols-5 gap-2.5 shrink-0">
                    <div id="card-f" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="text-[11px] text-slate-400">Avanço (f)</span>
                            <button type="button" onclick="toggleLock('f')" id="btn-lock-f" title="Desbloquear para edição manual" class="text-xs px-1 py-0.5 rounded bg-slate-900/80 border border-slate-700 hover:border-slate-500 transition">🔒</button>
                        </div>
                        <input type="number" id="input-f" value="0.0000" step="0.005" min="0.001" readonly oninput="onManualInput('f')" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
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
                        <input type="number" id="input-vc" value="0" step="1" min="1" readonly oninput="onManualInput('vc')" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
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
                        <div class="text-xl font-bold text-white mt-0.5" id="res-n">0</div>
                        <span class="text-[9px] text-slate-400">rpm</span>
                    </div>

                    <div class="bg-slate-800 p-2.5 rounded-lg border border-slate-700">
                        <span class="text-[11px] text-slate-400">Avanço Trabalho</span>
                        <div class="text-xl font-bold text-white mt-0.5" id="res-vf">0</div>
                        <span class="text-[9px] text-slate-400">mm/min</span>
                    </div>
                </div>

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
                                    <g id="needle-potencia" class="gauge-needle">
                                        <line x1="100" y1="100" x2="100" y2="26" stroke="#ffffff" stroke-width="3" stroke-linecap="round" />
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
                                    <g id="needle-binario" class="gauge-needle">
                                        <line x1="100" y1="100" x2="100" y2="26" stroke="#ffffff" stroke-width="3" stroke-linecap="round" />
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

        <div id="modal-pdf-parametros" class="fixed inset-0 bg-black/75 flex items-center justify-center z-50 hidden p-3">
            <div class="bg-slate-800 border border-cyan-600/70 rounded-lg p-5 w-full max-w-md shadow-2xl flex flex-col gap-4">
                <div class="flex justify-between items-center border-b border-slate-700 pb-2.5">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2">
                        <span>📋</span> Gerar PDF com parâmetros de corte
                    </h3>
                    <button type="button" onclick="fecharModalPdfParametros()" class="text-slate-400 hover:text-white font-bold text-sm">✕</button>
                </div>
                <p class="text-xs text-slate-300">Escolha o âmbito dos parâmetros de corte a exportar em tabela:</p>
                <div class="flex flex-col gap-2.5">
                    <label class="flex items-start gap-2.5 bg-slate-900 p-3 rounded-md border border-slate-700 cursor-pointer hover:border-cyan-500 transition">
                        <input type="radio" name="escopo-pdf-parametros" id="radio-param-selecionados" value="selecionados" class="mt-0.5 accent-cyan-500" checked>
                        <div>
                            <strong class="text-xs text-white block">Só os parâmetros selecionados</strong>
                            <span class="text-[10px] text-slate-400">Exporta apenas o material/grupo ativo no Ø, VC, F, RPM (n) e Avanço (vf) atuais.</span>
                        </div>
                    </label>
                    <label class="flex items-start gap-2.5 bg-slate-900 p-3 rounded-md border border-slate-700 cursor-pointer hover:border-cyan-500 transition">
                        <input type="radio" name="escopo-pdf-parametros" id="radio-param-todos" value="todos" class="mt-0.5 accent-cyan-500">
                        <div>
                            <strong class="text-xs text-white block">Todos os parâmetros de corte suportados pela ferramenta</strong>
                            <span class="text-[10px] text-slate-400">Exporta todos os grupos/materiais suportados pela ferramenta selecionada para o Ø e refrigeração atuais.</span>
                        </div>
                    </label>
                </div>
                <p id="aviso-pdf-parametros" class="text-[11px] text-amber-300 hidden"></p>
                <div class="flex justify-end gap-2 pt-1">
                    <button type="button" onclick="fecharModalPdfParametros()" class="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-md text-xs font-medium text-white transition">Cancelar</button>
                    <button type="button" onclick="gerarPdfParametrosCorte()" class="bg-cyan-600 hover:bg-cyan-500 px-4 py-1.5 rounded-md text-xs font-bold text-white transition flex items-center gap-1.5">
                        <span>📥</span> Gerar PDF
                    </button>
                </div>
            </div>
        </div>

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
        const FAMILIAS_JSON = __FAMILIAS_JSON_PLACEHOLDER__;
        const REFERENCIAS_JSON = __REFERENCIAS_JSON_PLACEHOLDER__;
        const PARAMETROS_JSON = __PARAMETROS_JSON_PLACEHOLDER__;
        const GRUPOS_MMG_JSON = __GRUPOS_MMG_JSON_PLACEHOLDER__;
        const LOGO_ALAMO_B64 = __LOGO_ALAMO_PLACEHOLDER__;
        const LOGO_MAPAL_B64 = __LOGO_MAPAL_PLACEHOLDER__;
        const LINKEDIN_URL = "https://www.linkedin.com/in/bruno-pinto-2a5410143?utm_source=share_via&utm_content=profile&utm_medium=member_android";

        function gerarQrDataUrl(texto) {
            if (typeof qrcode !== 'function') return '';
            const qr = qrcode(0, 'M');
            qr.addData(texto);
            qr.make();
            return qr.createDataURL(4, 0);
        }
        let isProMode = false;
        let referenciaAtivaObj = null;
        let linhaAtivaInterna = '';

        let refrigAtual = 'int';
        let vcPct = 0;
        let fPct = 0;
        let fUnlocked = false;
        let vcUnlocked = false;
        let rpmMaxUnlocked = false;
        let corteInterrompidoAtivo = false;

        const ISO_PALETTE = {
            'P': { nome: 'Aços (P)',        cor: '#3b82f6', bgAtivo: '#2563eb', fgAtivo: '#ffffff' },
            'M': { nome: 'Inoxidáveis (M)', cor: '#facc15', bgAtivo: '#ca8a04', fgAtivo: '#0f172a' },
            'K': { nome: 'Fundições (K)',   cor: '#ef4444', bgAtivo: '#dc2626', fgAtivo: '#ffffff' },
            'N': { nome: 'Não Ferrosos (N)',cor: '#22c55e', bgAtivo: '#16a34a', fgAtivo: '#0f172a' },
            'S': { nome: 'Superligas (S)',  cor: '#f97316', bgAtivo: '#ea580c', fgAtivo: '#ffffff' },
            'H': { nome: 'Endurecidos (H)', cor: '#a855f7', bgAtivo: '#9333ea', fgAtivo: '#ffffff' },
            'C': { nome: 'Compósitos (C)',  cor: '#06b6d4', bgAtivo: '#0891b2', fgAtivo: '#0f172a' },
            'X': { nome: 'Misto (X*)',      cor: '#ec4899', bgAtivo: '#db2777', fgAtivo: '#ffffff' },
            'Y': { nome: 'Sinterizados (Y*)',cor:'#94a3b8', bgAtivo: '#64748b', fgAtivo: '#0f172a' }
        };

        let mmgGrupoSelecionado = null;
        let mmgSubgrupoSelecionado = null;
        let mmgSelecionadoManualmente = false;
        let mmg2GrupoSelecionado = null;
        let mmg2SubgrupoSelecionado = null;
        let mmg2CodigoSelecionado = '';
        let sincronizacaoInterna = false;
        const mmgMetaPorCodigo = {};
        const mmgSubgruposPorIso = {};
        const mmg2MetaPorCodigo = {};
        const mmg2SubgruposPorIso = {};

        function resolverGrupoTool(toolData, grpKey) {
            if (!toolData || !toolData.grupos || !grpKey) return null;
            const gNorm = normMmg(grpKey);
            if (toolData.grupos[gNorm]) return toolData.grupos[gNorm];
            if (toolData.grupos[grpKey]) return toolData.grupos[grpKey];
            const targetKey = normMmg(grpKey);
            for (const k of Object.keys(toolData.grupos)) {
                if (normMmg(k) === targetKey) {
                    return toolData.grupos[k];
                }
            }
            return null;
        }

        function normMmg(cod) {
            return String(cod || '').trim().toUpperCase();
        }



        function fecharAvisoInicial() {
            const modal = document.getElementById('modal-aviso-inicial');
            if (modal) modal.classList.add('hidden');
        }

        function abrirModalPdfParametros() {
            const aviso = document.getElementById('aviso-pdf-parametros');
            if (aviso) {
                aviso.classList.add('hidden');
                aviso.innerText = '';
            }
            document.getElementById('modal-pdf-parametros').classList.remove('hidden');
        }

        function fecharModalPdfParametros() {
            const modal = document.getElementById('modal-pdf-parametros');
            if (modal) modal.classList.add('hidden');
        }

        function formatPtNum(val, decimals = 2) {
            if (val === null || val === undefined || isNaN(Number(val))) return '—';
            return Number(val).toFixed(decimals).replace('.', ',');
        }

        function gerarPdfParametrosCorte() {
            if (!window.jspdf || !window.jspdf.jsPDF) {
                alert("Biblioteca jsPDF não carregada. Verifique a ligação à internet.");
                return;
            }

            const escopo = document.querySelector('input[name="escopo-pdf-parametros"]:checked')?.value || 'selecionados';
            const avisoEl = document.getElementById('aviso-pdf-parametros');
            const brocaKey = document.getElementById('broca').value;
            const grupoEfetivoKey = getGrupoEfetivo();

            let diametro = parseFloat(document.getElementById('diametro').value);
            if (isNaN(diametro) || diametro <= 0) diametro = 12.00;
            const rpmMaxVal = parseFloat(document.getElementById('input-rpm-max').value) || 8000;

            const linhasTabela = [];
            let designacaoFerramenta = referenciaAtivaObj?.specification || referenciaAtivaObj?.order_no || '';

            if (brocaKey && dados[brocaKey] && dados[brocaKey].grupos) {
                const toolData = dados[brocaKey];
                if (!designacaoFerramenta) {
                    designacaoFerramenta = toolData.nomeProduto || toolData.nome || toolData.familiaCode || brocaKey;
                }

                const gruposAlvo = escopo === 'todos'
                    ? (toolData.gruposList && toolData.gruposList.length > 0 ? toolData.gruposList : Object.keys(toolData.grupos))
                    : (grupoEfetivoKey && resolverGrupoTool(toolData, grupoEfetivoKey) ? [grupoEfetivoKey] : []);

                if (gruposAlvo.length === 0) {
                    if (avisoEl) {
                        avisoEl.innerText = "Selecione um grupo de materiais (MMG) ou escolha 'Todos os parâmetros de corte suportados pela ferramenta'.";
                        avisoEl.classList.remove('hidden');
                    }
                    return;
                }

                const ctxBase = obterContextoCalculoAtual();

                gruposAlvo.forEach((grpKey, idx) => {
                    if (!resolverGrupoTool(toolData, grpKey)) return;
                    const calc = calcularMetricasFerramenta(brocaKey, getVarianteAtiva(), grpKey, ctxBase);
                    if (!calc) return;

                    let fFinal = calc.fFinal;
                    let vcFinal = calc.vcFinal;
                    let nFinal = calc.n;
                    let vfFinal = calc.vf;

                    if (escopo === 'selecionados' && idx === 0) {
                        const fManual = parseFloat(document.getElementById('input-f').value);
                        const vcManual = parseFloat(document.getElementById('input-vc').value);
                        if (fUnlocked && !isNaN(fManual) && fManual > 0) fFinal = fManual;
                        if (vcUnlocked && !isNaN(vcManual) && vcManual > 0) vcFinal = vcManual;
                        nFinal = diametro > 0 ? Math.round((vcFinal * 1000) / (Math.PI * diametro)) : 0;
                        if (rpmMaxUnlocked && rpmMaxVal > 0 && nFinal > rpmMaxVal) {
                            nFinal = rpmMaxVal;
                            vcFinal = (nFinal * Math.PI * diametro) / 1000;
                        }
                        vfFinal = Math.round(fFinal * nFinal);
                    }

                    const metaGrp = mmgMetaPorCodigo[grpKey] || {};
                    const descMaterial = metaGrp.label
                        ? `${grpKey} — ${metaGrp.label}`
                        : (toolData.gruposNames?.[grpKey] || grpKey);

                    linhasTabela.push([
                        descMaterial,
                        formatPtNum(diametro, 2),
                        String(Math.round(vcFinal)),
                        formatPtNum(fFinal, 3),
                        String(Math.round(nFinal)),
                        String(Math.round(vfFinal))
                    ]);
                });
            } else {
                if (escopo === 'todos') {
                    if (avisoEl) {
                        avisoEl.innerText = "Selecione primeiro um modelo de ferramenta para listar todos os parâmetros suportados.";
                        avisoEl.classList.remove('hidden');
                    }
                    return;
                }
                const vcManual = parseFloat(document.getElementById('input-vc').value) || 0;
                const fManual = parseFloat(document.getElementById('input-f').value) || 0;
                const nManual = parseInt(document.getElementById('res-n').innerText, 10) || 0;
                const vfManual = parseInt(document.getElementById('res-vf').innerText, 10) || 0;
                const descGrp = grupoEfetivoKey ? obterLabelGrupoMmg(grupoEfetivoKey) : 'Material Selecionado';
                if (!designacaoFerramenta) designacaoFerramenta = 'Ferramenta';

                linhasTabela.push([
                    descGrp,
                    formatPtNum(diametro, 2),
                    String(Math.round(vcManual)),
                    formatPtNum(fManual, 3),
                    String(nManual),
                    String(vfManual)
                ]);
            }

            if (linhasTabela.length === 0) {
                if (avisoEl) {
                    avisoEl.innerText = "Não existem parâmetros disponíveis para a seleção atual.";
                    avisoEl.classList.remove('hidden');
                }
                return;
            }

const { jsPDF } = window.jspdf;
            const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
            const pageW = doc.internal.pageSize.getWidth();   // 297 mm
            const pageH = doc.internal.pageSize.getHeight();  // 210 mm

            // --- CABEÇALHO COM LOGÓTIPOS ---
            doc.setFillColor(15, 23, 42);
            doc.rect(14, 10, pageW - 28, 18, 'F');

            if (LOGO_MAPAL_B64) {
                doc.addImage(LOGO_MAPAL_B64, 'PNG', 18, 12.5, 28, 13);
            } else {
                doc.setTextColor(255, 255, 255);
                doc.setFont('helvetica', 'bold');
                doc.setFontSize(14);
                doc.text("MAPAL", 18, 21.5);
            }

            doc.setTextColor(255, 255, 255);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(12);
            doc.text("PARÂMETROS DE CORTE", pageW / 2, 21, { align: 'center' });

            if (LOGO_ALAMO_B64) {
                doc.addImage(LOGO_ALAMO_B64, 'PNG', pageW - 46, 12.5, 28, 13);
            } else {
                doc.setFontSize(11);
                doc.text("ÁLAMO", pageW - 18, 21.5, { align: 'right' });
            }

            // --- INFORMAÇÃO DA FERRAMENTA ---
            doc.setTextColor(15, 23, 42);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(10);
            doc.text(`Designação da Ferramenta: ${designacaoFerramenta}`, 14, 35);

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.text(
                `Refrigeração: ${refrigAtual.toUpperCase()}   |   Ajuste VC: ${vcPct >= 0 ? '+' : ''}${vcPct}%   |   Ajuste F: ${fPct >= 0 ? '+' : ''}${fPct}%`,
                14,
                40.5
            );

            // --- TABELA COM DESTAQUE VERDE-LIMA NAS COLUNAS DE CÁLCULO ---
            const headRow = [['Material', 'Ø (mm)', 'VC (m/min)', 'f (mm/rot)', 'RPM (n)', 'Avanço Vf (mm/min)']];

            if (typeof doc.autoTable === 'function') {
                doc.autoTable({
                    startY: 45,
                    head: headRow,
                    body: linhasTabela,
                    theme: 'grid',
                    styles: {
                        font: 'helvetica',
                        fontSize: 8.5,
                        cellPadding: 2.3,
                        textColor: [15, 23, 42],
                        lineColor: [203, 213, 225],
                        lineWidth: 0.2
                    },
                    headStyles: {
                        fillColor: [30, 41, 59],
                        textColor: [255, 255, 255],
                        fontStyle: 'bold',
                        halign: 'center'
                    },
                    columnStyles: {
                        0: { cellWidth: 139, halign: 'left' },
                        1: { halign: 'right', cellWidth: 22 },
                        2: { halign: 'right', cellWidth: 24, fillColor: [217, 249, 157], fontStyle: 'bold' }, // Verde-lima suave
                        3: { halign: 'right', cellWidth: 26, fillColor: [217, 249, 157], fontStyle: 'bold' }, // Verde-lima suave
                        4: { halign: 'right', cellWidth: 24, fillColor: [190, 242, 100], fontStyle: 'bold' }, // Verde-lima destaque
                        5: { halign: 'right', cellWidth: 34, fillColor: [190, 242, 100], fontStyle: 'bold' }  // Verde-lima destaque
                    },
                    margin: { left: 14, right: 14, bottom: 26 }
                });
            }

            // --- RODAPÉ COM CONTACTOS + QR CODE LINKEDIN ---
            const qrDataUrl = gerarQrDataUrl(LINKEDIN_URL);
            const totalPages = doc.internal.getNumberOfPages();

            for (let p = 1; p <= totalPages; p++) {
                doc.setPage(p);
                doc.setDrawColor(203, 213, 225);
                doc.line(14, pageH - 22, pageW - 14, pageH - 22);

                doc.setFont('helvetica', 'bold');
                doc.setFontSize(9);
                doc.setTextColor(15, 23, 42);
                doc.text("ÁLAMO FERRAMENTAS", 14, pageH - 16.5);

                doc.setFont('helvetica', 'normal');
                doc.setFontSize(8.5);
                doc.text("Bruno Pinto  |  bruno.pinto@alamo-ferramentas.com  |  Tlf.: +351 936 959 415", 14, pageH - 11.5);
                doc.text(`Página ${p} de ${totalPages}`, 14, pageH - 6.5);

                if (qrDataUrl) {
                    doc.addImage(qrDataUrl, 'PNG', pageW - 31, pageH - 20.5, 17, 17);
                    doc.setFontSize(7);
                    doc.setTextColor(71, 85, 105);
                    doc.text("LinkedIn", pageW - 33, pageH - 11, { align: 'right' });
                }
            }

            const sufixoEscopo = escopo === 'todos' ? 'Todos' : 'Selecionados';
            doc.save(`Parametros_Corte_${sufixoEscopo}_${diametro.toFixed(1)}mm.pdf`);
            fecharModalPdfParametros();
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

        const gruposMmgMap = {};
        const gruposMmgOrdem = [];

        function extrairIsoDeCodigo(cod) {
            const m = normMmg(cod).match(/^([A-Z])/);
            return m ? m[1] : '';
        }

        function extrairSubgrupoDeCodigo(cod) {
            const m = normMmg(cod).match(/^([A-Z]+\d+)/);
            return m ? m[1] : '';
        }

        function construirCatalogoGruposMmg() {
            Object.keys(gruposMmgMap).forEach(k => delete gruposMmgMap[k]);
            Object.keys(mmgMetaPorCodigo).forEach(k => delete mmgMetaPorCodigo[k]);
            Object.keys(mmgSubgruposPorIso).forEach(k => delete mmgSubgruposPorIso[k]);
            Object.keys(mmg2MetaPorCodigo).forEach(k => delete mmg2MetaPorCodigo[k]);
            Object.keys(mmg2SubgruposPorIso).forEach(k => delete mmg2SubgruposPorIso[k]);
            gruposMmgOrdem.length = 0;

            if (!Array.isArray(GRUPOS_MMG_JSON)) return;
            GRUPOS_MMG_JSON.forEach(item => {
                if (!item || typeof item !== 'object') return;
                const cod = normMmg(item.codigo || item.Grupo || item.grupo || '');
                if (!cod) return;
                const origem = String(item.origem || '').trim().toUpperCase();
                const label = String(item.label || item.descricao || cod).trim();
                const iso = String(item.iso || '').replace('*', '').trim().toUpperCase() || extrairIsoDeCodigo(cod);
                const sub = normMmg(item.subgrupo || '') || extrairSubgrupoDeCodigo(cod);
                const freq = String(item.materiais_frequentes || '').trim();
                const dureza = String(item.dureza || '').trim();

                if (origem === 'MAPAL_MMG_NEW') {
                    if (!mmg2MetaPorCodigo[cod]) {
                        mmg2MetaPorCodigo[cod] = { codigo: cod, label, iso, subgrupo: sub, freq, dureza, origem };
                    }
                    if (iso && sub) {
                        if (!mmg2SubgruposPorIso[iso]) mmg2SubgruposPorIso[iso] = [];
                        if (!mmg2SubgruposPorIso[iso].includes(sub)) {
                            mmg2SubgruposPorIso[iso].push(sub);
                        }
                    }
                } else {
                    if (!gruposMmgMap[cod]) {
                        gruposMmgMap[cod] = label;
                        gruposMmgOrdem.push(cod);
                    }
                    if (!mmgMetaPorCodigo[cod]) {
                        mmgMetaPorCodigo[cod] = { codigo: cod, label, iso, subgrupo: sub, freq, dureza, origem: origem || 'MAPAL_MMG' };
                    }
                    if (iso && sub) {
                        if (!mmgSubgruposPorIso[iso]) mmgSubgruposPorIso[iso] = [];
                        if (!mmgSubgruposPorIso[iso].includes(sub)) {
                            mmgSubgruposPorIso[iso].push(sub);
                        }
                    }
                }
            });
        }

        function selecionarGrupo2Botao(isoCode) {
            if (mmg2GrupoSelecionado === isoCode) {
                mmg2GrupoSelecionado = null;
                mmg2SubgrupoSelecionado = null;
                mmg2CodigoSelecionado = '';
            } else {
                mmg2GrupoSelecionado = isoCode;
                mmg2SubgrupoSelecionado = null;
                mmg2CodigoSelecionado = '';
            }
            renderBotoesMmg2();
        }

        function selecionarSubgrupo2Botao(subCode) {
            mmg2SubgrupoSelecionado = subCode ? normMmg(subCode) : null;
            mmg2CodigoSelecionado = '';
            renderBotoesMmg2();
        }

        function selecionarCodigo2Botao(cod) {
            const codNorm = normMmg(cod);
            mmg2CodigoSelecionado = (mmg2CodigoSelecionado === codNorm) ? '' : codNorm;
            renderBotoesMmg2();
        }

        function renderBotoesCodigoMmg2() {
            const painelCod = document.getElementById('mmg2-painel-codigo');
            const contCod = document.getElementById('mmg2-botoes-codigo');
            const lblCod = document.getElementById('mmg2-label-codigo');
            const detCod = document.getElementById('mmg2-detalhe-codigo');
            if (!painelCod || !contCod) return;

            if (!mmg2GrupoSelecionado) {
                painelCod.classList.add('hidden');
                contCod.innerHTML = '';
                if (detCod) detCod.innerText = '';
                return;
            }

            painelCod.classList.remove('hidden');
            const palSel = ISO_PALETTE[mmg2GrupoSelecionado] || { nome: mmg2GrupoSelecionado, cor: '#2dd4bf', bgAtivo: '#0d9488', fgAtivo: '#0f172a' };
            if (lblCod) {
                lblCod.innerText = mmg2SubgrupoSelecionado ? `ISO 513 (${mmg2SubgrupoSelecionado})` : `ISO 513 (${palSel.nome})`;
                lblCod.style.color = palSel.cor;
            }

            const candidatos = Object.keys(mmg2MetaPorCodigo).filter(cod => {
                const meta = mmg2MetaPorCodigo[cod] || {};
                const iso = (meta.iso || extrairIsoDeCodigo(cod)).toUpperCase();
                const sub = normMmg(meta.subgrupo || extrairSubgrupoDeCodigo(cod));
                if (iso !== mmg2GrupoSelecionado) return false;
                if (mmg2SubgrupoSelecionado && sub !== mmg2SubgrupoSelecionado && !cod.startsWith(mmg2SubgrupoSelecionado)) {
                    return false;
                }
                return true;
            }).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

            contCod.innerHTML = '';
            candidatos.forEach(cod => {
                const ativo = mmg2CodigoSelecionado === cod;
                const meta = mmg2MetaPorCodigo[cod] || {};
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'mmg-code-btn';
                btn.title = meta.label || cod;
                btn.innerText = cod;
                btn.style.color = ativo ? palSel.fgAtivo : palSel.cor;
                btn.style.backgroundColor = ativo ? palSel.bgAtivo : '#0f172a';
                btn.style.borderColor = palSel.cor;
                if (ativo) {
                    btn.style.boxShadow = `0 0 0 1px ${palSel.cor}`;
                }
                btn.onclick = () => selecionarCodigo2Botao(cod);
                contCod.appendChild(btn);
            });

            if (detCod) {
                const metaAtiva = mmg2CodigoSelecionado ? mmg2MetaPorCodigo[mmg2CodigoSelecionado] : null;
                detCod.innerText = metaAtiva ? (metaAtiva.label || mmg2CodigoSelecionado) : (mmg2CodigoSelecionado || '');
            }
        }

        function renderBotoesMmg2() {
            const contGrupo = document.getElementById('mmg2-botoes-grupo');
            const painelSub = document.getElementById('mmg2-painel-subgrupo');
            const contSub = document.getElementById('mmg2-botoes-subgrupo');
            const lblSub = document.getElementById('mmg2-label-subgrupo');
            const freqEl = document.getElementById('mmg2-materiais-freq');
            const detEl = document.getElementById('mmg2-selecao-detalhe');
            if (!contGrupo || !painelSub || !contSub) return;

            const isosDisponiveis = new Set();
            Object.values(mmg2MetaPorCodigo).forEach(m => {
                const iso = (m.iso || extrairIsoDeCodigo(m.codigo)).toUpperCase();
                if (iso) isosDisponiveis.add(iso);
            });

            const ordemBotoes = ['P', 'M', 'K', 'N', 'S', 'H', 'C', 'X', 'Y'];
            contGrupo.innerHTML = '';

            ordemBotoes.forEach(isoCode => {
                const pal = ISO_PALETTE[isoCode] || { nome: isoCode, cor: '#2dd4bf', bgAtivo: '#0d9488', fgAtivo: '#0f172a' };
                const ativo = mmg2GrupoSelecionado === isoCode;
                const habilitado = isosDisponiveis.has(isoCode);

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'iso-btn';
                btn.disabled = !habilitado;
                btn.title = pal.nome;
                btn.innerText = isoCode;
                btn.style.color = ativo ? pal.fgAtivo : pal.cor;
                btn.style.backgroundColor = ativo ? pal.bgAtivo : '#0f172a';
                btn.style.borderColor = pal.cor;
                if (ativo) {
                    btn.style.boxShadow = `0 0 0 1.5px ${pal.cor}`;
                }
                btn.onclick = () => selecionarGrupo2Botao(isoCode);
                contGrupo.appendChild(btn);
            });

            if (!mmg2GrupoSelecionado) {
                painelSub.classList.add('hidden');
                contSub.innerHTML = '';
                if (freqEl) freqEl.innerText = '';
                renderBotoesCodigoMmg2();
                if (detEl) detEl.innerText = mmg2CodigoSelecionado ? (mmg2MetaPorCodigo[mmg2CodigoSelecionado]?.label || mmg2CodigoSelecionado) : '—';
                return;
            }

            painelSub.classList.remove('hidden');
            const palSel = ISO_PALETTE[mmg2GrupoSelecionado] || { nome: mmg2GrupoSelecionado, cor: '#2dd4bf', bgAtivo: '#0d9488', fgAtivo: '#0f172a' };
            if (lblSub) {
                lblSub.innerText = `Subgrupo ISO 513 (${palSel.nome})`;
                lblSub.style.color = palSel.cor;
            }

            const subsRender = (mmg2SubgruposPorIso[mmg2GrupoSelecionado] || []).map(normMmg);
            contSub.innerHTML = '';

            const btnTodos = document.createElement('button');
            btnTodos.type = 'button';
            btnTodos.className = 'sub-btn';
            const todosAtivo = !mmg2SubgrupoSelecionado;
            btnTodos.innerText = `${mmg2GrupoSelecionado} (Todos)`;
            btnTodos.style.color = todosAtivo ? palSel.fgAtivo : palSel.cor;
            btnTodos.style.backgroundColor = todosAtivo ? palSel.bgAtivo : '#0f172a';
            btnTodos.style.borderColor = palSel.cor;
            btnTodos.onclick = () => selecionarSubgrupo2Botao(null);
            contSub.appendChild(btnTodos);

            subsRender.forEach(subCode => {
                const subAtivo = mmg2SubgrupoSelecionado === subCode;
                const bSub = document.createElement('button');
                bSub.type = 'button';
                bSub.className = 'sub-btn';
                bSub.innerText = subCode;
                bSub.style.color = subAtivo ? palSel.fgAtivo : palSel.cor;
                bSub.style.backgroundColor = subAtivo ? palSel.bgAtivo : '#0f172a';
                bSub.style.borderColor = palSel.cor;
                bSub.onclick = () => selecionarSubgrupo2Botao(subCode);
                contSub.appendChild(bSub);
            });

            const freqs = [];
            Object.values(mmg2MetaPorCodigo).forEach(m => {
                const matchIso = m.iso === mmg2GrupoSelecionado;
                const matchSub = !mmg2SubgrupoSelecionado || normMmg(m.subgrupo) === mmg2SubgrupoSelecionado;
                if (matchIso && matchSub && m.freq && m.freq !== '-') {
                    freqs.push(m.freq);
                }
            });
            if (freqEl) {
                freqEl.innerText = freqs.length > 0 ? freqs.slice(0, 2).join(' · ') : '';
                freqEl.title = freqs.join(' | ');
            }

            renderBotoesCodigoMmg2();

            if (detEl) {
                detEl.innerText = mmg2CodigoSelecionado
                    ? (mmg2MetaPorCodigo[mmg2CodigoSelecionado]?.label || mmg2CodigoSelecionado)
                    : (mmg2SubgrupoSelecionado || mmg2GrupoSelecionado);
            }
        }

        function obterLabelGrupoMmg(cod) {
            const k = normMmg(cod);
            return gruposMmgMap[k] || gruposMmgMap[cod] || cod;
        }

        function ferramentaSuportaFiltroMmg(tool, isoSel, subSel, codSel) {
            if (!tool || !tool.grupos) return true;
            const grps = tool.gruposList && tool.gruposList.length > 0 ? tool.gruposList : Object.keys(tool.grupos);
            if (!grps || grps.length === 0) return true;
            if (!isoSel && !subSel && !codSel) return true;

            const codKey = normMmg(codSel);
            const subKey = normMmg(subSel);
            const isoNorm = String(isoSel || '').trim().toUpperCase();

            return grps.some(g => {
                const gNorm = normMmg(g);
                const gKey = normMmg(g);
                if (codKey) {
                    return gKey === codKey;
                }
                const gIso = (mmgMetaPorCodigo[gNorm]?.iso || mmgMetaPorCodigo[gKey]?.iso || extrairIsoDeCodigo(gNorm)).toUpperCase();
                const gSub = normMmg(mmgMetaPorCodigo[gNorm]?.subgrupo || mmgMetaPorCodigo[gKey]?.subgrupo || extrairSubgrupoDeCodigo(gNorm));
                if (subKey) {
                    return gSub === subKey || gKey.startsWith(subKey + '.');
                }
                if (isoNorm) {
                    return gIso === isoNorm;
                }
                return true;
            });
        }

        function renderBotoesCodigoMmg(gruposDisponiveisFerramenta = [], filtrarPorFerramenta = false) {
            const painelCod = document.getElementById('mmg-painel-codigo');
            const contCod = document.getElementById('mmg-botoes-codigo');
            const lblCod = document.getElementById('mmg-label-codigo');
            const detCod = document.getElementById('mmg-detalhe-codigo');
            const selG = document.getElementById('grupo');
            if (!painelCod || !contCod || !selG) return;

            if (!mmgGrupoSelecionado) {
                painelCod.classList.add('hidden');
                contCod.innerHTML = '';
                if (detCod) detCod.innerText = '';
                return;
            }

            painelCod.classList.remove('hidden');
            const palSel = ISO_PALETTE[mmgGrupoSelecionado] || { nome: mmgGrupoSelecionado, cor: '#38bdf8', bgAtivo: '#0284c7', fgAtivo: '#ffffff' };
            if (lblCod) {
                lblCod.innerText = mmgSubgrupoSelecionado ? `Grupo MAPAL (${mmgSubgrupoSelecionado})` : `Grupo MAPAL (${palSel.nome})`;
                lblCod.style.color = palSel.cor;
            }

            const dispNormList = (gruposDisponiveisFerramenta || []).map(g => normMmg(g)).filter(Boolean);
            const mapaDispPorChave = {};
            dispNormList.forEach(g => {
                mapaDispPorChave[normMmg(g)] = g;
            });
            const dispSet = new Set(Object.keys(mapaDispPorChave));

            const baseCodigos = new Set([
                ...(gruposMmgOrdem.length > 0 ? gruposMmgOrdem : Object.keys(gruposMmgMap)).map(normMmg),
                ...dispNormList
            ]);

            const candidatos = Array.from(baseCodigos).filter(cod => {
                const meta = mmgMetaPorCodigo[cod] || {};
                const iso = (meta.iso || extrairIsoDeCodigo(cod)).toUpperCase();
                const sub = normMmg(meta.subgrupo || extrairSubgrupoDeCodigo(cod));
                if (iso !== mmgGrupoSelecionado) return false;
                if (mmgSubgrupoSelecionado && sub !== mmgSubgrupoSelecionado && !cod.startsWith(mmgSubgrupoSelecionado)) {
                    return false;
                }
                return true;
            }).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

            contCod.innerHTML = '';
            const codigoAtivo = normMmg(selG.value);

            candidatos.forEach(cod => {
                const kChave = normMmg(cod);
                const habilitado = !filtrarPorFerramenta || dispSet.has(kChave);
                const codReal = (filtrarPorFerramenta && mapaDispPorChave[kChave]) ? mapaDispPorChave[kChave] : cod;
                const ativo = normMmg(codigoAtivo) === kChave && Boolean(codigoAtivo);
                const meta = mmgMetaPorCodigo[cod] || mmgMetaPorCodigo[codReal] || {};
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'mmg-code-btn';
                btn.disabled = !habilitado;
                btn.title = meta.label || codReal;
                btn.innerText = codReal;
                btn.style.color = ativo ? palSel.fgAtivo : palSel.cor;
                btn.style.backgroundColor = ativo ? palSel.bgAtivo : '#0f172a';
                btn.style.borderColor = palSel.cor;
                if (ativo) {
                    btn.style.boxShadow = `0 0 0 1px ${palSel.cor}`;
                }
                btn.onclick = () => selecionarCodigoBotaoMmg(codReal);
                contCod.appendChild(btn);
            });

            if (detCod) {
                const metaAtiva = codigoAtivo ? mmgMetaPorCodigo[codigoAtivo] : null;
                detCod.innerText = metaAtiva ? (metaAtiva.dureza || metaAtiva.label || codigoAtivo) : (codigoAtivo || '');
            }
        }

        function selecionarCodigoBotaoMmg(cod) {
            const selG = document.getElementById('grupo');
            if (!selG) return;
            const codNorm = normMmg(cod);
            if (!Array.from(selG.options).some(o => normMmg(o.value) === codNorm)) {
                const opt = document.createElement('option');
                opt.value = codNorm;
                opt.text = obterLabelGrupoMmg(codNorm);
                selG.appendChild(opt);
            }
            selG.value = codNorm;
            onSelectGrupoManual();
        }

        function renderBotoesMmg(gruposDisponiveisFerramenta = []) {
            const contGrupo = document.getElementById('mmg-botoes-grupo');
            const painelSub = document.getElementById('mmg-painel-subgrupo');
            const contSub = document.getElementById('mmg-botoes-subgrupo');
            const lblSub = document.getElementById('mmg-label-subgrupo');
            const freqEl = document.getElementById('mmg-materiais-freq');
            const detEl = document.getElementById('mmg-selecao-detalhe');
            if (!contGrupo || !painelSub || !contSub) return;

            const dispNormList = (gruposDisponiveisFerramenta || []).map(g => normMmg(g)).filter(Boolean);
            const dispSet = new Set(dispNormList);
            const isosDisponiveis = new Set();
            const subsDisponiveis = new Set();

            dispSet.forEach(g => {
                const iso = (mmgMetaPorCodigo[g]?.iso || extrairIsoDeCodigo(g)).toUpperCase();
                const sub = normMmg(mmgMetaPorCodigo[g]?.subgrupo || extrairSubgrupoDeCodigo(g));
                if (iso) isosDisponiveis.add(iso);
                if (sub) subsDisponiveis.add(sub);
            });

            const filtrarPorFerramenta = dispSet.size > 0 && isosDisponiveis.size > 0;

            const ordemBotoes = ['P', 'M', 'K', 'N', 'S', 'H', 'C', 'X', 'Y'];
            contGrupo.innerHTML = '';

            ordemBotoes.forEach(isoCode => {
                const pal = ISO_PALETTE[isoCode] || { nome: isoCode, cor: '#38bdf8', bgAtivo: '#0284c7', fgAtivo: '#ffffff' };
                const ativo = mmgGrupoSelecionado === isoCode;
                const habilitado = !filtrarPorFerramenta || isosDisponiveis.has(isoCode);

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'iso-btn';
                btn.disabled = !habilitado;
                btn.title = pal.nome;
                btn.innerText = isoCode;
                btn.style.color = ativo ? pal.fgAtivo : pal.cor;
                btn.style.backgroundColor = ativo ? pal.bgAtivo : '#0f172a';
                btn.style.borderColor = pal.cor;
                if (ativo) {
                    btn.style.boxShadow = `0 0 0 1.5px ${pal.cor}`;
                }
                btn.onclick = () => selecionarGrupoBotao(isoCode);
                contGrupo.appendChild(btn);
            });

            if (!mmgGrupoSelecionado) {
                painelSub.classList.add('hidden');
                contSub.innerHTML = '';
                if (freqEl) freqEl.innerText = '';
                renderBotoesCodigoMmg(dispNormList, filtrarPorFerramenta);
                const selG = document.getElementById('grupo');
                if (detEl) detEl.innerText = selG && selG.value ? obterLabelGrupoMmg(selG.value) : '—';
                return;
            }

            painelSub.classList.remove('hidden');
            const palSel = ISO_PALETTE[mmgGrupoSelecionado] || { nome: mmgGrupoSelecionado, cor: '#38bdf8', bgAtivo: '#0284c7', fgAtivo: '#ffffff' };
            if (lblSub) {
                lblSub.innerText = `Subgrupo (${palSel.nome})`;
                lblSub.style.color = palSel.cor;
            }

            const baseSubs = (mmgSubgruposPorIso[mmgGrupoSelecionado] || []).map(normMmg);
            const subsRender = filtrarPorFerramenta
                ? baseSubs.filter(s => subsDisponiveis.has(s))
                : baseSubs;

            contSub.innerHTML = '';

            const btnTodos = document.createElement('button');
            btnTodos.type = 'button';
            btnTodos.className = 'sub-btn';
            const todosAtivo = !mmgSubgrupoSelecionado;
            btnTodos.innerText = `${mmgGrupoSelecionado} (Todos)`;
            btnTodos.style.color = todosAtivo ? palSel.fgAtivo : palSel.cor;
            btnTodos.style.backgroundColor = todosAtivo ? palSel.bgAtivo : '#0f172a';
            btnTodos.style.borderColor = palSel.cor;
            btnTodos.onclick = () => selecionarSubgrupoBotao(null);
            contSub.appendChild(btnTodos);

            subsRender.forEach(subCode => {
                const subAtivo = mmgSubgrupoSelecionado === subCode;
                const bSub = document.createElement('button');
                bSub.type = 'button';
                bSub.className = 'sub-btn';
                bSub.innerText = subCode;
                bSub.style.color = subAtivo ? palSel.fgAtivo : palSel.cor;
                bSub.style.backgroundColor = subAtivo ? palSel.bgAtivo : '#0f172a';
                bSub.style.borderColor = palSel.cor;
                bSub.onclick = () => selecionarSubgrupoBotao(subCode);
                contSub.appendChild(bSub);
            });

            const freqs = [];
            Object.values(mmgMetaPorCodigo).forEach(m => {
                const matchIso = m.iso === mmgGrupoSelecionado;
                const matchSub = !mmgSubgrupoSelecionado || normMmg(m.subgrupo) === mmgSubgrupoSelecionado;
                if (matchIso && matchSub && m.freq && m.freq !== '-') {
                    freqs.push(m.freq);
                }
            });
            if (freqEl) {
                freqEl.innerText = freqs.length > 0 ? freqs.slice(0, 2).join(' · ') : '';
                freqEl.title = freqs.join(' | ');
            }

            renderBotoesCodigoMmg(dispNormList, filtrarPorFerramenta);

            const selG = document.getElementById('grupo');
            if (detEl) {
                detEl.innerText = selG && selG.value ? obterLabelGrupoMmg(selG.value) : (mmgSubgrupoSelecionado || mmgGrupoSelecionado);
            }
        }

        function selecionarGrupoBotao(isoCode) {
            if (mmgGrupoSelecionado === isoCode) {
                mmgGrupoSelecionado = null;
                mmgSubgrupoSelecionado = null;
                mmgSelecionadoManualmente = false;
                const selG = document.getElementById('grupo');
                if (selG) selG.value = '';
            } else {
                mmgGrupoSelecionado = isoCode;
                mmgSubgrupoSelecionado = null;
                mmgSelecionadoManualmente = true;
                aplicarFiltroMmgNaFerramenta();
            }
            sincronizarSelecaoComCatalogo('mmg');
        }

        function selecionarSubgrupoBotao(subCode) {
            mmgSelecionadoManualmente = Boolean(subCode);
            mmgSubgrupoSelecionado = subCode ? normMmg(subCode) : null;
            aplicarFiltroMmgNaFerramenta();
            sincronizarSelecaoComCatalogo('mmg');
        }

        function aplicarFiltroMmgNaFerramenta() {
            const brocaKey = document.getElementById('broca').value;
            const grupoSelect = document.getElementById('grupo');
            if (!grupoSelect) return;

            const disp = ((brocaKey && dados[brocaKey])
                ? (dados[brocaKey].gruposList || [])
                : (gruposMmgOrdem.length > 0 ? gruposMmgOrdem : Object.keys(gruposMmgMap))).map(normMmg);
            if (disp.length === 0) return;

            if (mmgSubgrupoSelecionado) {
                const subKey = normMmg(mmgSubgrupoSelecionado);
                const matchExato = disp.find(g => {
                    const metaSub = normMmg(mmgMetaPorCodigo[g]?.subgrupo || mmgMetaPorCodigo[normMmg(g)]?.subgrupo || extrairSubgrupoDeCodigo(g));
                    return metaSub === subKey || normMmg(g).startsWith(subKey + '.');
                });
                if (matchExato) {
                    if (!mmgSelecionadoManualmente && !grupoSelect.value) {
                        sincronizacaoInterna = true;
                        grupoSelect.value = matchExato;
                        sincronizacaoInterna = false;
                    }
                    return;
                }
            }

            if (mmgGrupoSelecionado) {
                const isoUpper = mmgGrupoSelecionado.toUpperCase();
                const matchIso = disp.find(g => {
                    const metaIso = (mmgMetaPorCodigo[g]?.iso || extrairIsoDeCodigo(g)).toUpperCase();
                    return metaIso === isoUpper;
                });
                if (matchIso) {
                    if (!mmgSelecionadoManualmente && !grupoSelect.value) {
                        sincronizacaoInterna = true;
                        grupoSelect.value = matchIso;
                        sincronizacaoInterna = false;
                    }
                    return;
                }
            }

            if (!mmgGrupoSelecionado && !mmgSubgrupoSelecionado) {
                sincronizacaoInterna = true;
                grupoSelect.value = '';
                sincronizacaoInterna = false;
            }
        }

        function onSelectGrupoManual() {
            if (sincronizacaoInterna) return;
            const grupoSelect = document.getElementById('grupo');
            const val = grupoSelect ? normMmg(grupoSelect.value) : '';
            if (val) {
                mmgSelecionadoManualmente = true;
                if (grupoSelect) grupoSelect.value = val;
                const iso = (mmgMetaPorCodigo[val]?.iso || extrairIsoDeCodigo(val)).toUpperCase();
                const sub = normMmg(mmgMetaPorCodigo[val]?.subgrupo || extrairSubgrupoDeCodigo(val));
                if (iso) mmgGrupoSelecionado = iso;
                if (sub) mmgSubgrupoSelecionado = sub;
            } else {
                mmgSelecionadoManualmente = false;
            }
            sincronizarSelecaoComCatalogo('mmg');
        }

        function sincronizarSelecaoComCatalogo(origem = 'mmg') {
            const grupoKey = normMmg(document.getElementById('grupo').value || '');
            if (grupoKey) {
                const prefixo = grupoKey.charAt(0).toUpperCase();
                if (propriedadesGrupo[prefixo]) {
                    document.getElementById('densidade').value = propriedadesGrupo[prefixo].densidade.toFixed(2);
                }
            }

            const brocaEl = document.getElementById('broca');
            const brocaAtual = brocaEl ? brocaEl.value : '';
            if (brocaAtual && dados[brocaAtual]) {
                const compAtual = ferramentaSuportaFiltroMmg(dados[brocaAtual], mmgGrupoSelecionado, mmgSubgrupoSelecionado, grupoKey);
                if (!compAtual) {
                    console.warn('Ferramenta incompatível com MMG selecionado');
                }
            }

            filtrarCatalogoCascata(origem);
            atualizarFiltroBrocas(true);

            const brocaFinal = document.getElementById('broca').value;
            const gruposDisp = (brocaFinal && dados[brocaFinal]) ? dados[brocaFinal].gruposList : [];
            renderBotoesMmg(gruposDisp);
            renderBotoesMmg2();

            const detEl = document.getElementById('mmg-selecao-detalhe');
            if (detEl) {
                detEl.innerText = grupoKey ? obterLabelGrupoMmg(grupoKey) : (mmgSubgrupoSelecionado || mmgGrupoSelecionado || '—');
            }
            atualizarPainelCotas();
            atualizarCalculo();
        }

        function construirFerramenta(cfg) {
            const famCode = cfg.familiaCode || '';
            const prodNome = cfg.nomeProduto || '';
            const labelModelo = (famCode && prodNome) ? `${famCode} — ${prodNome}` : (cfg.nome || famCode || prodNome);
            return {
                familiaCode: famCode,
                nomeProduto: prodNome,
                linha: cfg.linha || '',
                categoria: cfg.categoria || '',
                temRefrigInt: cfg.temRefrigInt !== undefined ? cfg.temRefrigInt : true,
                nome: labelModelo,
                variantes: cfg.variantes || {},
                diametros: cfg.diametros || [],
                gruposList: [],
                gruposNames: {},
                grupos: {}
            };
        }

        const dados = {};
        const mapaFamiliasExcel = {};

        function numSafe(v, fallback = 0) {
            if (v === null || v === undefined || v === '') return fallback;
            const n = parseFloat(String(v).replace(',', '.').trim());
            return isNaN(n) ? fallback : n;
        }

        function normalizarGamaValor(rawGama) {
            const g = String(rawGama || '').trim().toLowerCase();
            if (!g) return '';
            if (g.includes('expert')) return 'expert';
            if (g.includes('performance')) return 'performance';
            if (g.includes('basic')) return 'basic';
            return g;
        }

        function preencherSelectCategoriasFamilias() {
            const selCat = document.getElementById('categoria');
            if (!selCat) return;
            const valorAtual = selCat.value;

            const categoriasUnicas = [];
            const vistos = new Set();

            if (Array.isArray(FAMILIAS_JSON)) {
                FAMILIAS_JSON.forEach(f => {
                    const cat = String(f.categoria || f.Categoria || '').trim();
                    if (cat && !vistos.has(cat)) {
                        vistos.add(cat);
                        categoriasUnicas.push(cat);
                    }
                });
            }

            if (categoriasUnicas.length === 0) {
                Object.values(dados).forEach(tool => {
                    const cat = String(tool.categoria || '').trim();
                    if (cat && !vistos.has(cat)) {
                        vistos.add(cat);
                        categoriasUnicas.push(cat);
                    }
                });
            }

            selCat.innerHTML = '';
            const optVazio = document.createElement('option');
            optVazio.value = '';
            optVazio.text = 'Todas';
            selCat.appendChild(optVazio);

            categoriasUnicas.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.text = cat;
                selCat.appendChild(opt);
            });

            if (valorAtual && categoriasUnicas.includes(valorAtual)) {
                selCat.value = valorAtual;
            } else {
                selCat.value = '';
            }
        }

        function carregarCatalogoEParametrosJson() {
            construirCatalogoGruposMmg();

            if (Array.isArray(FAMILIAS_JSON)) {
                FAMILIAS_JSON.forEach(f => {
                    if (!f || typeof f !== 'object') return;
                    const famRaw = String(f.familia || f.Familia || '').trim();
                    if (!famRaw) return;
                    const famKey = famRaw.toLowerCase();
                    const prodNome = String(f.nome_produto || f['Nome do produto'] || '').trim();
                    const gamaNorm = normalizarGamaValor(f.gama || f.Gama);
                    const catRaw = String(f.categoria || f.Categoria || '').trim();

                    mapaFamiliasExcel[famKey] = {
                        familia: famRaw,
                        nomeProduto: prodNome,
                        gama: gamaNorm,
                        categoria: catRaw
                    };

                    if (!dados[famKey]) {
                        dados[famKey] = construirFerramenta({
                            familiaCode: famRaw,
                            nomeProduto: prodNome,
                            linha: gamaNorm || 'expert',
                            categoria: catRaw,
                            temRefrigInt: true,
                            variantes: {},
                            diametros: []
                        });
                    } else {
                        dados[famKey].familiaCode = famRaw;
                        if (prodNome) dados[famKey].nomeProduto = prodNome;
                        if (gamaNorm) dados[famKey].linha = gamaNorm;
                        if (catRaw) dados[famKey].categoria = catRaw;
                        dados[famKey].nome = (famRaw && dados[famKey].nomeProduto)
                            ? `${famRaw} — ${dados[famKey].nomeProduto}`
                            : (famRaw || dados[famKey].nomeProduto);
                    }
                });
            }

            if (Array.isArray(REFERENCIAS_JSON)) {
                REFERENCIAS_JSON.forEach(item => {
                    if (!item || typeof item !== 'object') return;
                    const famRaw = String(item.familia || item.Familia || '').trim();
                    if (!famRaw) return;
                    const famKey = famRaw.toLowerCase();
                    const famMeta = mapaFamiliasExcel[famKey] || {};

                    const prodNome = String(item.nome_produto || item['Nome do produto'] || famMeta.nomeProduto || '').trim();
                    const gamaNorm = normalizarGamaValor(item.gama || item.Gama || item.linha || famMeta.gama);
                    const catRaw = String(item.categoria || item.Categoria || item.operacao || famMeta.categoria || '').trim();
                    const varStr = String(item.variante || item.Variante || '').trim();
                    const refCode = normalizarRefrigCatalogo(item);
                    const d1Val = parseFloat(item.d1);

                    if (!dados[famKey]) {
                        dados[famKey] = construirFerramenta({
                            familiaCode: famRaw,
                            nomeProduto: prodNome,
                            linha: gamaNorm || 'expert',
                            categoria: catRaw,
                            temRefrigInt: true,
                            variantes: {},
                            diametros: []
                        });
                    }

                    const tool = dados[famKey];
                    if (prodNome) tool.nomeProduto = prodNome;
                    tool.nome = (famRaw && tool.nomeProduto) ? `${famRaw} — ${tool.nomeProduto}` : (famRaw || tool.nomeProduto);
                    if (gamaNorm) tool.linha = gamaNorm;
                    if (catRaw) tool.categoria = catRaw;

                    if (varStr) {
                        const matchRatio = varStr.match(/(\d+(?:\.\d+)?)\s*x\s*d/i);
                        const ratioNum = matchRatio ? parseFloat(matchRatio[1]) : 5;
                        if (!tool.variantes[varStr]) {
                            tool.variantes[varStr] = { ratio: ratioNum };
                        }
                    }

                    if (!isNaN(d1Val) && d1Val > 0) {
                        if (!tool.diametros.some(d => Math.abs(d - d1Val) < 0.001)) {
                            tool.diametros.push(d1Val);
                            tool.diametros.sort((a, b) => a - b);
                        }
                    }

                    if (!tool._refrigsSet) tool._refrigsSet = new Set();
                    if (refCode) tool._refrigsSet.add(refCode);
                });
            }

            if (Array.isArray(PARAMETROS_JSON) && PARAMETROS_JSON.length > 0) {
                PARAMETROS_JSON.forEach(row => {
                    if (!row || typeof row !== 'object' || row.suportado === false) return;
                    const famRaw = String(row.familia || row.Familia || '').trim();
                    if (!famRaw) return;
                    const famKey = famRaw.toLowerCase();
                    const famMeta = mapaFamiliasExcel[famKey] || {};

                    const prodNome = String(row.nome_produto || row['Nome do produto'] || famMeta.nomeProduto || '').trim();
                    const gamaRow = normalizarGamaValor(row.gama || row.Gama || row.linha || famMeta.gama);
                    const catRow = String(row.categoria || row.Categoria || row.operacao || famMeta.categoria || '').trim();

                    if (!dados[famKey]) {
                        dados[famKey] = construirFerramenta({
                            familiaCode: famRaw,
                            nomeProduto: prodNome,
                            linha: gamaRow || 'expert',
                            categoria: catRow,
                            temRefrigInt: true,
                            variantes: { '5xD': { ratio: 5 } },
                            diametros: [3.00, 4.50, 6.50, 9.50, 14.00, 20.00]
                        });
                    } else {
                        if (prodNome) dados[famKey].nomeProduto = prodNome;
                        dados[famKey].nome = (famRaw && dados[famKey].nomeProduto) ? `${famRaw} — ${dados[famKey].nomeProduto}` : (famRaw || dados[famKey].nomeProduto);
                        if (gamaRow) dados[famKey].linha = gamaRow;
                        if (catRow) dados[famKey].categoria = catRow;
                    }

                    const tool = dados[famKey];
                    if (Object.keys(tool.variantes).length === 0) {
                        tool.variantes = { '5xD': { ratio: 5 } };
                    }
                    if (!Array.isArray(tool.diametros) || tool.diametros.length === 0) {
                        tool.diametros = [3.00, 4.50, 6.50, 9.50, 14.00, 20.00];
                    }

                    const grp = normMmg(row.grupo || row.Grupo || row.mmg || row.MMG || '');
                    if (!grp) return;

                    const vcSrc = (row.vc && typeof row.vc === 'object') ? row.vc : {};
                    const vcObj = {
                        int: numSafe(row.Vc_Int ?? row.vc_int ?? vcSrc.interna ?? vcSrc.int ?? row.vc, 0),
                        ext: numSafe(row.Vc_Ext ?? row.vc_ext ?? vcSrc.externa ?? vcSrc.ext ?? row.vc, 0),
                        mql: numSafe(row.Vc_MQL ?? row.vc_mql ?? vcSrc.mql ?? vcSrc.vc, 0),
                        ar:  numSafe(row.Vc_Ar  ?? row.vc_ar  ?? vcSrc.ar  ?? 0, 0)
                    };

                    const mapaAvancos = row.avancos_f || row.f_by_d;
                    let fArr = [];
                    if (Array.isArray(row.f) && row.f.length > 0) {
                        fArr = row.f.map(x => numSafe(x, 0.05));
                    } else if (mapaAvancos && typeof mapaAvancos === 'object') {
                        const diamsJson = Object.keys(mapaAvancos)
                            .map(k => parseFloat(String(k).replace(',', '.')))
                            .filter(d => !isNaN(d))
                            .sort((a, b) => a - b);
                        if (diamsJson.length > 0) {
                            tool.diametros = diamsJson;
                        }
                        fArr = tool.diametros.map(d => {
                            const matchKey = Object.keys(mapaAvancos).find(k => Math.abs(parseFloat(String(k).replace(',', '.')) - d) < 0.02);
                            return matchKey !== undefined ? numSafe(mapaAvancos[matchKey], 0.05) : 0.05;
                        });
                    } else {
                        const fSingle = numSafe(row.f, 0.05);
                        fArr = tool.diametros.map(() => fSingle);
                    }

                    tool.grupos[grp] = { vc: vcObj, f: fArr };
                    if (!tool.gruposList.includes(grp)) {
                        tool.gruposList.push(grp);
                    }
                    tool.gruposNames[grp] = obterLabelGrupoMmg(grp);
                });
            }

            Object.values(dados).forEach(tool => {
                if (tool._refrigsSet && tool._refrigsSet.size > 0 && !tool._refrigsSet.has('int')) {
                    tool.temRefrigInt = false;
                }
            });

            preencherSelectCategoriasFamilias();
            renderBotoesMmg([]);
            renderBotoesMmg2();
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
            const gCat = normalizarGamaValor(item.gama || item.linha);
            if (gCat) return gCat;
            const famKey = String(item.familia || '').trim().toLowerCase();
            if (famKey && mapaFamiliasExcel[famKey] && mapaFamiliasExcel[famKey].gama) {
                return mapaFamiliasExcel[famKey].gama;
            }
            if (famKey && dados[famKey] && dados[famKey].linha) {
                return dados[famKey].linha;
            }
            return '';
        }

        function obterCategoriaCatalogo(item) {
            if (!item) return '';
            const cCat = String(item.categoria || item.operacao || '').trim();
            if (cCat) return cCat;
            const famKey = String(item.familia || '').trim().toLowerCase();
            if (famKey && mapaFamiliasExcel[famKey] && mapaFamiliasExcel[famKey].categoria) {
                return mapaFamiliasExcel[famKey].categoria;
            }
            if (famKey && dados[famKey] && dados[famKey].categoria) {
                return dados[famKey].categoria;
            }
            return '';
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
                const gamaTxt = obterGamaCatalogo(r) ? ` | Gama: ${fmtGamaLabel(obterGamaCatalogo(r))}` : '';
                const catTxt = obterCategoriaCatalogo(r) ? ` | Cat: ${obterCategoriaCatalogo(r)}` : '';
                metaEl.innerText = `Order: ${r.order_no || '—'} | Spec: ${r.specification || '—'} | DIN 6535: ${din6535}${refTxt}${gamaTxt}${catTxt}`;
            } else {
                const brocaKey = document.getElementById('broca').value;
                const varFiltro = document.getElementById('filtro-xd').value;
                const varKey = varFiltro || (brocaKey && dados[brocaKey] ? Object.keys(dados[brocaKey].variantes)[0] : '—');
                const nomeExib = (brocaKey && dados[brocaKey]) ? dados[brocaKey].nome : 'Sem modelo selecionado';
                metaEl.innerText = `Família: ${nomeExib}${brocaKey ? ` (${varKey})` : ''} | DIN 6535: —`;
            }
            atualizarVisibilidadeDiametroManual();
        }

        function limparFiltrosCatalogo() {
            document.getElementById('ref-pesquisa').value = '';
            document.getElementById('categoria').value = '';
            document.getElementById('filtro-gama-cat').value = '';
            document.getElementById('filtro-refrig-cat').value = '';
            document.getElementById('filtro-encabadouro-cat').value = '';
            document.getElementById('filtro-d1').value = '';
            document.getElementById('filtro-xd').value = '';
            document.getElementById('filtro-order-no').value = '';
            document.getElementById('broca').value = '';
            document.getElementById('grupo').value = '';
            mmgGrupoSelecionado = null;
            mmgSubgrupoSelecionado = null;
            mmg2GrupoSelecionado = null;
            mmg2SubgrupoSelecionado = null;
            mmg2CodigoSelecionado = '';
            linhaAtivaInterna = '';
            document.getElementById('ref-feedback').innerText = "Se souber a referência, pesquise acima; se não souber, filtre abaixo.";
            document.getElementById('ref-feedback').className = "text-[10px] text-slate-400 block";
            referenciaAtivaObj = null;
            filtrarCatalogoCascata('reset');
            atualizarFiltroBrocas(false);
            renderBotoesMmg([]);
            renderBotoesMmg2();
            atualizarPainelCotas();
            atualizarCalculo();
        }

        function getCandidatosCatalogoBase() {
            const q = (document.getElementById('ref-pesquisa').value || '').trim().toLowerCase();
            if (!Array.isArray(REFERENCIAS_JSON)) return [];
            if (!q) return REFERENCIAS_JSON;
            const tokens = q.split(/\s+/).filter(Boolean);
            return REFERENCIAS_JSON.filter(item => {
                const famKey = String(item.familia || '').trim().toLowerCase();
                const prodNome = item.nome_produto || (mapaFamiliasExcel[famKey]?.nomeProduto || '');
                const din6535 = extrairEncabadouroDIN6535(item).toLowerCase();
                const gama = obterGamaCatalogo(item).toLowerCase();
                const categoria = obterCategoriaCatalogo(item).toLowerCase();
                const refCode = normalizarRefrigCatalogo(item).toLowerCase();
                const hay = [
                    item.order_no,
                    item.specification,
                    item.designacao,
                    item.nome,
                    item.familia,
                    prodNome,
                    item.variante,
                    item.refrigeracao,
                    item.refrig,
                    refCode,
                    din6535,
                    gama,
                    categoria,
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

        function obterTodasCategoriasUnicas() {
            const categoriasUnicas = [];
            const vistos = new Set();

            if (Array.isArray(FAMILIAS_JSON)) {
                FAMILIAS_JSON.forEach(f => {
                    const cat = String(f.categoria || f.Categoria || '').trim();
                    if (cat && !vistos.has(cat)) {
                        vistos.add(cat);
                        categoriasUnicas.push(cat);
                    }
                });
            }

            if (Array.isArray(REFERENCIAS_JSON)) {
                REFERENCIAS_JSON.forEach(item => {
                    const cat = obterCategoriaCatalogo(item);
                    if (cat && !vistos.has(cat)) {
                        vistos.add(cat);
                        categoriasUnicas.push(cat);
                    }
                });
            }

            Object.values(dados).forEach(tool => {
                const cat = String(tool.categoria || '').trim();
                if (cat && !vistos.has(cat)) {
                    vistos.add(cat);
                    categoriasUnicas.push(cat);
                }
            });

            return categoriasUnicas;
        }

        function filtrarCatalogoCascata(origem = null) {
            const selCat = document.getElementById('categoria');
            const selGama = document.getElementById('filtro-gama-cat');
            const selRefrig = document.getElementById('filtro-refrig-cat');
            const selEnc = document.getElementById('filtro-encabadouro-cat');
            const datalistD1 = document.getElementById('lista-d1-sugestoes');
            const selXd = document.getElementById('filtro-xd');
            const selOrder = document.getElementById('filtro-order-no');
            const selModelo = document.getElementById('broca');
            const grupoCodSel = normMmg(document.getElementById('grupo')?.value || '');

            let valCat = selCat ? selCat.value : '';
            let valGama = selGama.value;
            let valRefrig = selRefrig.value;
            let valEnc = selEnc.value;
            const d1Num = obterD1Digitado();
            let valXd = selXd.value;
            const valModeloAtual = (origem === 'modelo' && selModelo && selModelo.value) ? selModelo.value.toLowerCase() : '';

            const matchMmgItem = (c) => {
                const fk = String(c.familia || '').trim().toLowerCase();
                const tool = fk ? dados[fk] : null;
                return ferramentaSuportaFiltroMmg(tool, mmgGrupoSelecionado, mmgSubgrupoSelecionado, grupoCodSel);
            };

            const base = getCandidatosCatalogoBase().filter(matchMmgItem);

            const candCat = base.filter(c =>
                obterCategoriaCatalogo(c) &&
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                matchD1Item(c, d1Num) &&
                (!valXd || String(c.variante || '').trim() === valXd) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
            );
            let catList = [...new Set(candCat.map(c => obterCategoriaCatalogo(c)))];
            if (catList.length === 0) {
                catList = obterTodasCategoriasUnicas();
            }
            if (valCat && !catList.includes(valCat)) valCat = '';
            if (selCat) {
                preencherSelectOpcoes(selCat, catList, 'Todas', c => c, valCat);
            }

            const candGama = base.filter(c =>
                obterGamaCatalogo(c) &&
                (!valCat || obterCategoriaCatalogo(c) === valCat) &&
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
            preencherSelectOpcoes(selGama, gamaList, 'Todas', fmtGamaLabel, valGama);

            const candRefrig = base.filter(c =>
                normalizarRefrigCatalogo(c) &&
                (!valCat || obterCategoriaCatalogo(c) === valCat) &&
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
            preencherSelectOpcoes(selRefrig, refrigList, 'Todas', fmtRefrigCatalogo, valRefrig);

            const candEnc = base.filter(c =>
                extrairEncabadouroDIN6535(c) &&
                (!valCat || obterCategoriaCatalogo(c) === valCat) &&
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
            preencherSelectOpcoes(selEnc, encList, 'Todos', e => `DIN ${e}`, valEnc);

            const candD1 = base.filter(c =>
                (c.d1 !== null && c.d1 !== undefined && !isNaN(Number(c.d1))) &&
                (!valCat || obterCategoriaCatalogo(c) === valCat) &&
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

            const candXd = base.filter(c =>
                c.variante &&
                (!valCat || obterCategoriaCatalogo(c) === valCat) &&
                (!valGama || obterGamaCatalogo(c) === valGama) &&
                (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                matchD1Item(c, d1Num) &&
                (!valModeloAtual || String(c.familia || '').trim().toLowerCase() === valModeloAtual)
            );
            const xdList = [...new Set(candXd.map(c => String(c.variante).trim()))].sort();
            if (valXd && !xdList.includes(valXd)) valXd = '';
            preencherSelectOpcoes(selXd, xdList, 'Todas', x => x, valXd);

            const finais = base.filter(c =>
                (!valCat || obterCategoriaCatalogo(c) === valCat) &&
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

            if (origem !== 'order' && origem !== 'modelo') {
                linhaAtivaInterna = valGama || '';
                atualizarFiltroBrocas(true);
            }

            const temFiltroAtivo = Boolean(valCat || valGama || valRefrig || valEnc || (d1Num !== null) || valXd || (document.getElementById('ref-pesquisa').value || '').trim() || mmgGrupoSelecionado || mmgSubgrupoSelecionado || grupoCodSel);

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
            const gamaItem = obterGamaCatalogo(item);
            const catItem = obterCategoriaCatalogo(item);

            if (famKey && dados[famKey]) {
                const toolData = dados[famKey];
                if (gamaItem) toolData.linha = gamaItem;
                if (catItem) toolData.categoria = catItem;

                linhaAtivaInterna = toolData.linha;
                if (toolData.categoria) {
                    document.getElementById('categoria').value = toolData.categoria;
                }
                atualizarFiltroBrocas(true);
                document.getElementById('broca').value = famKey;

                const varNorm = String(item.variante || '').trim();
                const matchVar = Object.keys(toolData.variantes || {}).find(k => k.toLowerCase() === varNorm.toLowerCase());
                const bloqueioMmg = mmgSelecionadoManualmente;
                mudarBroca(matchVar || null);
                mmgSelecionadoManualmente = bloqueioMmg;
            } else {
                if (gamaItem) linhaAtivaInterna = gamaItem;
                if (catItem) document.getElementById('categoria').value = catItem;
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
                const t = dados[key];
                const haystack = `${key} ${t.nomeProduto || ''} ${t.nome || ''}`.toUpperCase();
                if (haystack.includes(upper)) {
                    encontradaKey = key;
                    break;
                }
            }

            if (!encontradaKey) {
                feedback.innerText = `Nenhuma referência ou família encontrada para "${raw}".`;
                feedback.className = "text-[10px] text-amber-400 block";
                return;
            }

            const toolData = dados[encontradaKey];
            linhaAtivaInterna = toolData.linha;
            if (toolData.categoria) {
                document.getElementById('categoria').value = toolData.categoria;
            }
            atualizarFiltroBrocas(true);
            document.getElementById('broca').value = encontradaKey;

            let varianteDetetada = null;
            const matchXd = upper.match(/(\d+)\s*X\s*D/);
            if (matchXd) {
                const candidata = `${matchXd[1]}xD`;
                if (toolData.variantes && toolData.variantes[candidata]) {
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
            'C': { kc: 1500, densidade: 1.60 },
            'X': { kc: 2000, densidade: 5.50 },
            'Y': { kc: 2400, densidade: 7.50 }
        };

        function getKc(grupoKey) {
            const prefixo = normMmg(grupoKey).charAt(0).toUpperCase();
            return propriedadesGrupo[prefixo] ? propriedadesGrupo[prefixo].kc : 2200;
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
            const gKey = normMmg(grupoEfetivoKey);
            const grupoObj = resolverGrupoTool(toolData, grupoEfetivoKey);
            if (!grupoObj) return null;

            const {
                diametro, profundidade, qtdFuros, custoHora,
                refrigAtual, vcPct, fPct, rpmMaxUnlocked, rpmMaxVal,
                peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal
            } = contexto;

            const diametrosCat = toolData.diametros || [3.0, 4.5, 6.5, 9.5, 14.0, 20.0];
            const fCatArr = Array.isArray(grupoObj.f) && grupoObj.f.length > 0 ? grupoObj.f : diametrosCat.map(() => 0.05);

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
            const y1 = fCatArr[idxInf] !== undefined ? fCatArr[idxInf] : 0.05;
            const y2 = fCatArr[idxInf + 1] !== undefined ? fCatArr[idxInf + 1] : y1;

            const b = (x2 - x1) !== 0 ? (y2 - y1) / (x2 - x1) : 0;
            const a = y1 - b * x1;

            let fBase = a + b * diametro;
            if (fBase < 0.001) fBase = 0.001;
            let fFinal = fBase * (1 + fPct / 100);

            let vcBase = 0;
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

            const kc = getKc(gKey);
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
            const valCat = document.getElementById('categoria').value;
            const valGama = document.getElementById('filtro-gama-cat').value;
            const valRefrig = document.getElementById('filtro-refrig-cat').value;
            const valEnc = document.getElementById('filtro-encabadouro-cat').value;
            const d1Num = obterD1Digitado();
            const valXd = document.getElementById('filtro-xd').value;
            const qPesquisa = (document.getElementById('ref-pesquisa').value || '').trim();
            const grupoCodSel = normMmg(document.getElementById('grupo')?.value || '');

            const temFiltroCatalogo = Boolean(valCat || valGama || valRefrig || valEnc || (d1Num !== null) || valXd || qPesquisa || mmgGrupoSelecionado || mmgSubgrupoSelecionado || grupoCodSel);
            if (!temFiltroCatalogo) {
                return null;
            }

            const famSet = new Set();
            Object.entries(dados).forEach(([fk, tool]) => {
                if (ferramentaSuportaFiltroMmg(tool, mmgGrupoSelecionado, mmgSubgrupoSelecionado, grupoCodSel)) {
                    famSet.add(fk.toLowerCase());
                }
            });

            if (Array.isArray(REFERENCIAS_JSON) && REFERENCIAS_JSON.length > 0) {
                const base = getCandidatosCatalogoBase().filter(c => {
                    const fk = String(c.familia || '').trim().toLowerCase();
                    const tool = fk ? dados[fk] : null;
                    return ferramentaSuportaFiltroMmg(tool, mmgGrupoSelecionado, mmgSubgrupoSelecionado, grupoCodSel);
                });
                const compativeis = base.filter(c =>
                    (!valCat || obterCategoriaCatalogo(c) === valCat) &&
                    (!valGama || obterGamaCatalogo(c) === valGama) &&
                    (!valRefrig || normalizarRefrigCatalogo(c) === valRefrig) &&
                    (!valEnc || extrairEncabadouroDIN6535(c) === valEnc) &&
                    matchD1Item(c, d1Num) &&
                    (!valXd || String(c.variante || '').trim() === valXd)
                );
                const temFiltroRefEspecifico = Boolean(valCat || valGama || valRefrig || valEnc || (d1Num !== null) || valXd || qPesquisa);
                if (temFiltroRefEspecifico) {
                    const refFamSet = new Set();
                    compativeis.forEach(c => {
                        const fk = String(c.familia || '').trim().toLowerCase();
                        if (fk && dados[fk]) refFamSet.add(fk);
                    });
                    return refFamSet;
                }
            }

            return famSet;
        }

        function atualizarFiltroBrocas(manterSelecao = false) {
            const linhaSel = linhaAtivaInterna || '';
            const categoriaSel = document.getElementById('categoria').value;
            const brocaSelect = document.getElementById('broca');
            const infoModelo = document.getElementById('info-modelo-filtro');
            const atualBroca = manterSelecao ? brocaSelect.value : '';
            const famsCatalogo = obterFamiliasCompativeisCatalogo();

            brocaSelect.innerHTML = '';

            const optVazio = document.createElement('option');
            optVazio.value = '';
            optVazio.text = '— Vazio (sem modelo selecionado) —';
            brocaSelect.appendChild(optVazio);

            const matchesCatalogo = (key) => !famsCatalogo || famsCatalogo.has(key.toLowerCase());

            for (const key in dados) {
                const ferramenta = dados[key];
                const matchLinha = !linhaSel || ferramenta.linha === linhaSel;
                const matchCat = !categoriaSel || ferramenta.categoria === categoriaSel;
                if (matchLinha && matchCat && matchesCatalogo(key)) {
                    const opt = document.createElement('option');
                    opt.value = key;
                    opt.text = ferramenta.nome;
                    brocaSelect.appendChild(opt);
                }
            }

            if (famsCatalogo && famsCatalogo.size > 0) {
                for (const key in dados) {
                    const ferramenta = dados[key];
                    const jaExiste = Array.from(brocaSelect.options).some(o => o.value === key);
                    if (!jaExiste && matchesCatalogo(key)) {
                        const opt = document.createElement('option');
                        opt.value = key;
                        opt.text = `${ferramenta.nome} (${fmtGamaLabel(ferramenta.linha)})`;
                        brocaSelect.appendChild(opt);
                    }
                }
            }

            const totalModelos = Math.max(0, brocaSelect.options.length - 1);
            if (infoModelo) {
                infoModelo.innerText = famsCatalogo ? `${totalModelos} compatível(is)` : `${totalModelos} modelo(s)`;
            }

            if (atualBroca && dados[atualBroca] && Array.from(brocaSelect.options).some(o => o.value === atualBroca)) {
                brocaSelect.value = atualBroca;
            } else {
                brocaSelect.value = '';
            }

            mudarBroca();
        }

        function onMudarModeloFerramenta() {
            const brocaKey = document.getElementById('broca').value;
            if (brocaKey && dados[brocaKey]) {
                const toolData = dados[brocaKey];
                linhaAtivaInterna = toolData.linha;
                const selCat = document.getElementById('categoria');
                if (selCat && toolData.categoria && selCat.value !== toolData.categoria) {
                    selCat.value = toolData.categoria;
                }
                if (referenciaAtivaObj && String(referenciaAtivaObj.familia || '').trim().toLowerCase() !== brocaKey.toLowerCase()) {
                    referenciaAtivaObj = null;
                }
            } else {
                referenciaAtivaObj = null;
            }
            mudarBroca();
            filtrarCatalogoCascata('modelo');
        }

        function mudarBroca(variantePreferida = null) {
            const brocaKey = document.getElementById('broca').value;
            const grupoSelect = document.getElementById('grupo');
            const btnInt = document.getElementById('ref-int');
            const avisoRefrig = document.getElementById('aviso-refrig');

            if (!brocaKey || !dados[brocaKey]) {
                btnInt.disabled = false;
                btnInt.classList.remove('opacity-40', 'cursor-not-allowed');
                avisoRefrig.classList.add('hidden');

                const todosGrupos = (gruposMmgOrdem.length > 0 ? gruposMmgOrdem : Object.keys(gruposMmgMap)).map(normMmg);
                const atualGrp = normMmg(grupoSelect.value);
                grupoSelect.innerHTML = '';
                const optEmpty = document.createElement('option');
                optEmpty.value = '';
                optEmpty.text = todosGrupos.length > 0 ? '— Todos os grupos MMG disponíveis —' : 'Sem grupos MMG';
                grupoSelect.appendChild(optEmpty);

                todosGrupos.forEach(g => {
                    const opt = document.createElement('option');
                    opt.value = g;
                    opt.text = obterLabelGrupoMmg(g);
                    grupoSelect.appendChild(opt);
                });

                if (atualGrp && todosGrupos.includes(atualGrp)) {
                    grupoSelect.value = atualGrp;
                } else {
                    grupoSelect.value = '';
                }

                renderBotoesMmg([]);
            renderBotoesMmg2();
                atualizarPainelCotas();
                atualizarCalculo();
                return;
            }

            const toolData = dados[brocaKey];

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

            const atualGrupo = normMmg(grupoSelect.value);
            grupoSelect.innerHTML = '';

            const gruposDisponiveis = (toolData.gruposList.length > 0 ? toolData.gruposList : Object.keys(toolData.grupos)).map(normMmg);
            gruposDisponiveis.forEach(g => {
                const opt = document.createElement('option');
                opt.value = g;
                opt.text = toolData.gruposNames[g] || obterLabelGrupoMmg(g);
                grupoSelect.appendChild(opt);
            });

            if (gruposDisponiveis.length === 0) {
                const opt = document.createElement('option');
                opt.value = "";
                opt.text = "Sem parâmetros no JSON";
                grupoSelect.appendChild(opt);
            } else if (atualGrupo && gruposDisponiveis.includes(atualGrupo)) {
                grupoSelect.value = atualGrupo;
            } else {
                grupoSelect.value = gruposDisponiveis[0];
            }

            if (mmgGrupoSelecionado || mmgSubgrupoSelecionado) {
                aplicarFiltroMmgNaFerramenta();
            }
            renderBotoesMmg(gruposDisponiveis);
            renderBotoesMmg2();

            if (variantePreferida && toolData.variantes && toolData.variantes[variantePreferida]) {
                const selXd = document.getElementById('filtro-xd');
                if (selXd && Array.from(selXd.options).some(o => o.value === variantePreferida)) {
                    selXd.value = variantePreferida;
                }
            }

            mudarGrupoMaterial();
        }

        function mudarGrupoMaterial() {
            const grupoKey = normMmg(document.getElementById('grupo').value);
            if (grupoKey) {
                const prefixo = grupoKey.charAt(0).toUpperCase();
                if (propriedadesGrupo[prefixo]) {
                    document.getElementById('densidade').value = propriedadesGrupo[prefixo].densidade.toFixed(2);
                }
            }
            const detEl = document.getElementById('mmg-selecao-detalhe');
            if (detEl) {
                detEl.innerText = grupoKey ? obterLabelGrupoMmg(grupoKey) : (mmgSubgrupoSelecionado || mmgGrupoSelecionado || '—');
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
            const grupoKey = normMmg(document.getElementById('grupo').value);
            const ligaCheck = document.getElementById('liga-check').checked;

            if (!brocaKey || !dados[brocaKey] || !grupoKey) return grupoKey;
            if (!ligaCheck) return grupoKey;

            const lista = (dados[brocaKey].gruposList || []).map(normMmg);
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
                needle.style.transform = 'rotate(-90deg)';
                badge.innerText = 'Sem Limite Definido';
                badge.className = 'text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400';
                return null;
            }

            const ratio = valor / maxCap;
            const clampedRatio = Math.min(1, Math.max(0, ratio));
            const angle = -90 + (clampedRatio * 180);
            needle.style.transform = `rotate(${angle.toFixed(1)}deg)`;

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
            } else if (toolData) {
                box.className = 'bg-slate-900 px-2.5 py-1.5 rounded-md border border-amber-600/50 text-[10px] text-amber-200 flex justify-between items-center gap-2 shrink-0';
                txt.innerText = `Sem cota l3 na ref. ativa · Nominal ${varianteKey} ≈ ${nomInfo.maxNominalMm.toFixed(1)} mm (selecione referência p/ validar l3)`;
                badge.innerText = 'SEM l3';
                badge.className = 'font-bold text-amber-300 shrink-0';
            } else {
                box.className = 'bg-slate-900 px-2.5 py-1.5 rounded-md border border-slate-700 text-[10px] text-slate-300 flex justify-between items-center gap-2 shrink-0';
                txt.innerText = 'Selecione um modelo de ferramenta ou referência para validar profundidade';
                badge.innerText = 'AGUARDAR';
                badge.className = 'font-bold text-slate-400 shrink-0';
            }
        }

        function atualizarCalculo() {
            const brocaKey = document.getElementById('broca').value;
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

            if (!brocaKey || !dados[brocaKey] || !grupoEfetivoKey || !resolverGrupoTool(dados[brocaKey], grupoEfetivoKey)) {
                atualizarPainelCotas();
                atualizarAlertaProfundidade(diametro, profundidade, null, '5xD');
                document.getElementById('val-estado').innerText = !brocaKey ? 'Sem modelo selecionado' : 'Sem dados JSON';
                document.getElementById('val-estado').className = 'text-[9px] font-bold text-slate-400';
                document.getElementById('tabela-ref').innerHTML = '';
                document.getElementById('svg-grafico').innerHTML = '';
                return;
            }

            const toolData = dados[brocaKey];
            const grupoObj = resolverGrupoTool(toolData, grupoEfetivoKey);
            const diametrosCat = toolData.diametros || [3.0, 4.5, 6.5, 9.5, 14.0, 20.0];
            const fCatArr = Array.isArray(grupoObj.f) && grupoObj.f.length > 0 ? grupoObj.f : diametrosCat.map(() => 0.05);
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
                const fCat = fCatArr[i] !== undefined ? fCatArr[i] : 0.05;
                let nCat = dCat > 0 ? Math.round((vcFinal * 1000) / (Math.PI * dCat)) : 0;
                if (rpmMaxUnlocked && rpmMaxVal > 0 && nCat > rpmMaxVal) {
                    nCat = rpmMaxVal;
                }
                const vfCat = Math.round(fCat * nCat);
                const tr = document.createElement('tr');
                if (i === calc.idxInf || i === calc.idxInf + 1) {
                    tr.className = "bg-blue-900/20 font-medium text-blue-200";
                }
                tr.innerHTML = `
                    <td class="py-1">${dCat.toFixed(2)}</td>
                    <td class="py-1">${fCat.toFixed(3)}</td>
                    <td class="py-1">${nCat}</td>
                    <td class="py-1">${vfCat}</td>
                `;
                tbody.appendChild(tr);
            });

            renderGrafico(diametrosCat, fCatArr, diametro, fFinal, calc.idxInf);

            if (!document.getElementById('modal-comparacao').classList.contains('hidden')) {
                atualizarComparacao();
            }
        }

        function renderGrafico(diametros, fArr, dCalc, fCalc, idxInf) {
            const svg = document.getElementById('svg-grafico');
            svg.innerHTML = '';

            const width = 400;
            const height = 180;
            const padLeft = 40;
            const padRight = 20;
            const padTop = 18;
            const padBottom = 30;

            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;

            const allX = [...diametros, dCalc];
            const allY = [...fArr, fCalc];

            let minX = Math.min(...allX);
            let maxX = Math.max(...allX);
            let minY = Math.min(...allY) * 0.85;
            let maxY = Math.max(...allY) * 1.15;

            if (minX === maxX) { minX -= 1; maxX += 1; }
            if (minY === maxY) { minY -= 0.01; maxY += 0.01; }

            const scaleX = (x) => padLeft + ((x - minX) / (maxX - minX)) * plotW;
            const scaleY = (y) => padTop + plotH - ((y - minY) / (maxY - minY)) * plotH;

            for (let i = 0; i <= 4; i++) {
                const yVal = minY + (i / 4) * (maxY - minY);
                const yPos = scaleY(yVal);

                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", padLeft);
                line.setAttribute("y1", yPos);
                line.setAttribute("x2", width - padRight);
                line.setAttribute("y2", yPos);
                line.setAttribute("stroke", "#334155");
                line.setAttribute("stroke-width", "0.5");
                svg.appendChild(line);

                const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.setAttribute("x", padLeft - 5);
                text.setAttribute("y", yPos + 3);
                text.setAttribute("fill", "#94a3b8");
                text.setAttribute("font-size", "8");
                text.setAttribute("text-anchor", "end");
                text.textContent = yVal.toFixed(2);
                svg.appendChild(text);
            }

            diametros.forEach((dVal) => {
                const xPos = scaleX(dVal);
                const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.setAttribute("x", xPos);
                text.setAttribute("y", height - padBottom + 12);
                text.setAttribute("fill", "#94a3b8");
                text.setAttribute("font-size", "8");
                text.setAttribute("text-anchor", "middle");
                text.textContent = dVal.toFixed(1);
                svg.appendChild(text);
            });

            const xAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
            xAxis.setAttribute("x1", padLeft);
            xAxis.setAttribute("y1", padTop + plotH);
            xAxis.setAttribute("x2", width - padRight);
            xAxis.setAttribute("y2", padTop + plotH);
            xAxis.setAttribute("stroke", "#64748b");
            xAxis.setAttribute("stroke-width", "1");
            svg.appendChild(xAxis);

            const yAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
            yAxis.setAttribute("x1", padLeft);
            yAxis.setAttribute("y1", padTop);
            yAxis.setAttribute("x2", padLeft);
            yAxis.setAttribute("y2", padTop + plotH);
            yAxis.setAttribute("stroke", "#64748b");
            yAxis.setAttribute("stroke-width", "1");
            svg.appendChild(yAxis);

            if (diametros.length > 1) {
                let pointsStr = "";
                diametros.forEach((dVal, i) => {
                    const fVal = fArr[i] !== undefined ? fArr[i] : 0.05;
                    pointsStr += `${scaleX(dVal)},${scaleY(fVal)} `;
                });
                const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
                polyline.setAttribute("fill", "none");
                polyline.setAttribute("stroke", "#3b82f6");
                polyline.setAttribute("stroke-width", "2");
                polyline.setAttribute("points", pointsStr.trim());
                svg.appendChild(polyline);

                if (idxInf >= 0 && idxInf < diametros.length - 1) {
                    const segX1 = scaleX(diametros[idxInf]);
                    const segY1 = scaleY(fArr[idxInf]);
                    const segX2 = scaleX(diametros[idxInf + 1]);
                    const segY2 = scaleY(fArr[idxInf + 1]);
                    const segLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    segLine.setAttribute("x1", segX1);
                    segLine.setAttribute("y1", segY1);
                    segLine.setAttribute("x2", segX2);
                    segLine.setAttribute("y2", segY2);
                    segLine.setAttribute("stroke", "#60a5fa");
                    segLine.setAttribute("stroke-width", "3");
                    svg.appendChild(segLine);
                }
            }

            diametros.forEach((dVal, i) => {
                const fVal = fArr[i] !== undefined ? fArr[i] : 0.05;
                const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                circle.setAttribute("cx", scaleX(dVal));
                circle.setAttribute("cy", scaleY(fVal));
                circle.setAttribute("r", "3.5");
                circle.setAttribute("fill", "#3b82f6");
                circle.setAttribute("stroke", "#0f172a");
                circle.setAttribute("stroke-width", "1");
                svg.appendChild(circle);
            });

            const cx = scaleX(dCalc);
            const cy = scaleY(fCalc);

            const hLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
            hLine.setAttribute("x1", padLeft);
            hLine.setAttribute("y1", cy);
            hLine.setAttribute("x2", cx);
            hLine.setAttribute("y2", cy);
            hLine.setAttribute("stroke", "#f97316");
            hLine.setAttribute("stroke-width", "1");
            hLine.setAttribute("stroke-dasharray", "3,2");
            svg.appendChild(hLine);

            const vLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
            vLine.setAttribute("x1", cx);
            vLine.setAttribute("y1", cy);
            vLine.setAttribute("x2", cx);
            vLine.setAttribute("y2", padTop + plotH);
            vLine.setAttribute("stroke", "#f97316");
            vLine.setAttribute("stroke-width", "1");
            vLine.setAttribute("stroke-dasharray", "3,2");
            svg.appendChild(vLine);

            const calcCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            calcCircle.setAttribute("cx", cx);
            calcCircle.setAttribute("cy", cy);
            calcCircle.setAttribute("r", "5");
            calcCircle.setAttribute("fill", "#f97316");
            calcCircle.setAttribute("stroke", "#ffffff");
            calcCircle.setAttribute("stroke-width", "1.5");
            svg.appendChild(calcCircle);
        }

        function obterContextoCalculoAtual() {
            let diametro = parseFloat(document.getElementById('diametro').value);
            let profundidade = parseFloat(document.getElementById('profundidade').value);
            let qtdFuros = parseInt(document.getElementById('qtd-furos').value, 10);
            let custoHora = parseFloat(document.getElementById('custo-hora').value);

            if (isNaN(diametro) || diametro <= 0) diametro = 12.00;
            if (isNaN(profundidade) || profundidade <= 0) profundidade = 31.0;
            if (isNaN(qtdFuros) || qtdFuros < 1) qtdFuros = 50;
            if (isNaN(custoHora) || custoHora < 0) custoHora = 50.00;

            const peckingCheck = document.getElementById('pecking-check').checked;
            const peckingUnid = document.getElementById('pecking-unidade').value;
            let peckingInputVal = parseFloat(document.getElementById('pecking-passo').value);
            let peckingRetensaoVal = parseFloat(document.getElementById('pecking-retensao').value);

            if (isNaN(peckingInputVal) || peckingInputVal <= 0) peckingInputVal = peckingUnid === 'xd' ? 3.0 : 36.0;
            if (isNaN(peckingRetensaoVal) || peckingRetensaoVal <= 0) peckingRetensaoVal = 5000;

            const rpmMaxVal = parseFloat(document.getElementById('input-rpm-max').value) || 8000;

            return {
                diametro, profundidade, qtdFuros, custoHora,
                refrigAtual, vcPct, fPct, rpmMaxUnlocked, rpmMaxVal,
                peckingCheck, peckingUnid, peckingInputVal, peckingRetensaoVal
            };
        }

        function abrirModalComparacao() {
            if (!isProMode) {
                gerirModoPro();
                return;
            }
            document.getElementById('modal-resultado-comparacao').classList.add('hidden');
            const selectComp = document.getElementById('comp-ferramenta');
            const brocaAtual = document.getElementById('broca').value;
            const valorAnterior = selectComp.value;

            selectComp.innerHTML = '';

            const optCliente = document.createElement('option');
            optCliente.value = '__CLIENTE__';
            optCliente.text = '🛠️ Ferramenta do Cliente (Vc / f / Piloto / Canhão)';
            selectComp.appendChild(optCliente);

            for (const key in dados) {
                const opt = document.createElement('option');
                opt.value = key;
                opt.text = dados[key].nome;
                selectComp.appendChild(opt);
            }

            if (valorAnterior && (valorAnterior === '__CLIENTE__' || dados[valorAnterior])) {
                selectComp.value = valorAnterior;
            } else {
                selectComp.value = '__CLIENTE__';
            }

            document.getElementById('comp-custo-hora').value = parseFloat(document.getElementById('custo-hora').value) || 50.00;
            atualizarEstadoBotaoInterrompido();
            onChangeFonteComparacao();
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function fecharModalComparacao() {
            document.getElementById('modal-comparacao').classList.add('hidden');
        }

        function abrirJanelaResultadoComparacao() {
            if (!isProMode) return;
            atualizarComparacao();
            document.getElementById('comp-incluir-pdf-res').checked = document.getElementById('comp-incluir-pdf').checked;
            document.getElementById('modal-comparacao').classList.add('hidden');
            document.getElementById('modal-resultado-comparacao').classList.remove('hidden');
        }

        function fecharJanelaResultadoComparacao() {
            document.getElementById('modal-resultado-comparacao').classList.add('hidden');
        }

        function voltarParaInputsComparacao() {
            document.getElementById('modal-resultado-comparacao').classList.add('hidden');
            document.getElementById('modal-comparacao').classList.remove('hidden');
        }

        function onChangeFonteComparacao() {
            const val = document.getElementById('comp-ferramenta').value;
            const blocoCliente = document.getElementById('comp-bloco-cliente');
            const blocoVariante = document.getElementById('comp-bloco-variante');

            if (val === '__CLIENTE__') {
                blocoCliente.classList.remove('hidden');
                blocoVariante.classList.add('hidden');
            } else {
                blocoCliente.classList.add('hidden');
                blocoVariante.classList.remove('hidden');
                preencherVariantesComparacao(val);
            }
            atualizarComparacao();
        }

        function preencherVariantesComparacao(toolKey) {
            const selVar = document.getElementById('comp-variante');
            selVar.innerHTML = '';
            const tool = dados[toolKey];
            if (!tool || !tool.variantes) return;

            const varAtualPrincipal = getVarianteAtiva();
            Object.keys(tool.variantes).forEach(vKey => {
                const opt = document.createElement('option');
                opt.value = vKey;
                opt.text = vKey;
                if (vKey === varAtualPrincipal) opt.selected = true;
                selVar.appendChild(opt);
            });
        }

        function sincronizarCustoHoraComparacao() {
            const val = parseFloat(document.getElementById('comp-custo-hora').value);
            if (!isNaN(val) && val > 0) {
                document.getElementById('custo-hora').value = val.toFixed(2);
                atualizarCalculo();
            }
        }

        function calcularVidaTotalFuros(vidaBase, vidaUnid, afiQtd, profundidadeMm, fatorCorteInterrompido = 1.0) {
            const vidaEfetiva = Math.max(1, vidaBase || 1) * fatorCorteInterrompido;
            const usosTotais = 1 + Math.max(0, afiQtd || 0);
            if (vidaUnid === 'metros') {
                const profM = Math.max(0.001, (profundidadeMm || 31) / 1000);
                const furosPorUso = vidaEfetiva / profM;
                return Math.max(1, furosPorUso * usosTotais);
            }
            return Math.max(1, vidaEfetiva * usosTotais);
        }

        function calcularCustoFerramentaLote(precoFerramenta, vidaBase, vidaUnid, afiQtd, afiCusto, qtdFuros, profundidadeMm, fatorCorteInterrompido = 1.0) {
            const vidaTotalFuros = calcularVidaTotalFuros(vidaBase, vidaUnid, afiQtd, profundidadeMm, fatorCorteInterrompido);
            const custoCicloVida = (precoFerramenta || 0) + (Math.max(0, afiQtd || 0) * (afiCusto || 0));
            const custoFerramentaFuro = custoCicloVida / vidaTotalFuros;
            const custoFerramentaLote = custoFerramentaFuro * qtdFuros;
            return {
                vidaTotalFuros,
                vidaPorAfiaçãoFuros: vidaTotalFuros / (1 + Math.max(0, afiQtd || 0)),
                custoCicloVida,
                custoFerramentaFuro,
                custoFerramentaLote
            };
        }

        function renderGraficoBarrasComparacao(svgId, labelA, valA, corA, labelB, valB, corB, unidade) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            svg.innerHTML = '';

            const W = 300, H = 175;
            const padL = 46, padR = 16, padT = 22, padB = 28;
            const plotW = W - padL - padR;
            const plotH = H - padT - padB;

            const maxVal = Math.max(valA || 0, valB || 0, 0.01) * 1.18;
            const scaleY = (v) => padT + plotH - (Math.max(0, v) / maxVal) * plotH;

            for (let i = 0; i <= 3; i++) {
                const tickVal = (maxVal * i) / 3;
                const y = scaleY(tickVal);
                const gl = document.createElementNS("http://www.w3.org/2000/svg", "line");
                gl.setAttribute("x1", padL); gl.setAttribute("y1", y);
                gl.setAttribute("x2", W - padR); gl.setAttribute("y2", y);
                gl.setAttribute("stroke", "#1e293b"); gl.setAttribute("stroke-width", "1");
                svg.appendChild(gl);

                const tl = document.createElementNS("http://www.w3.org/2000/svg", "text");
                tl.setAttribute("x", padL - 5); tl.setAttribute("y", y + 3);
                tl.setAttribute("fill", "#94a3b8"); tl.setAttribute("font-size", "8.5");
                tl.setAttribute("text-anchor", "end");
                tl.textContent = tickVal >= 100 ? Math.round(tickVal) : tickVal.toFixed(1);
                svg.appendChild(tl);
            }

            const axis = document.createElementNS("http://www.w3.org/2000/svg", "line");
            axis.setAttribute("x1", padL); axis.setAttribute("y1", padT + plotH);
            axis.setAttribute("x2", W - padR); axis.setAttribute("y2", padT + plotH);
            axis.setAttribute("stroke", "#475569"); axis.setAttribute("stroke-width", "1");
            svg.appendChild(axis);

            const barW = Math.min(54, plotW / 4.2);
            const xA = padL + plotW * 0.27 - barW / 2;
            const xB = padL + plotW * 0.73 - barW / 2;

            const items = [
                { x: xA, val: valA, cor: corA, leg: labelA },
                { x: xB, val: valB, cor: corB, leg: labelB }
            ];

            items.forEach(it => {
                const yTop = scaleY(it.val);
                const hBar = Math.max(2, (padT + plotH) - yTop);

                const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                rect.setAttribute("x", it.x); rect.setAttribute("y", yTop);
                rect.setAttribute("width", barW); rect.setAttribute("height", hBar);
                rect.setAttribute("rx", "4");
                rect.setAttribute("fill", it.cor);
                svg.appendChild(rect);

                const vTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                vTxt.setAttribute("x", it.x + barW / 2); vTxt.setAttribute("y", Math.max(12, yTop - 5));
                vTxt.setAttribute("fill", "#f8fafc"); vTxt.setAttribute("font-size", "9.5");
                vTxt.setAttribute("font-weight", "bold"); vTxt.setAttribute("text-anchor", "middle");
                vTxt.textContent = `${it.val >= 100 ? it.val.toFixed(0) : it.val.toFixed(1)}${unidade}`;
                svg.appendChild(vTxt);

                const lTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                lTxt.setAttribute("x", it.x + barW / 2); lTxt.setAttribute("y", H - 9);
                lTxt.setAttribute("fill", "#cbd5e1"); lTxt.setAttribute("font-size", "9");
                lTxt.setAttribute("text-anchor", "middle");
                lTxt.textContent = it.leg;
                svg.appendChild(lTxt);
            });
        }

        function renderGraficoBreakEven(svgId, custoTotalA, custoTotalB, qtdFuros) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            svg.innerHTML = '';

            const W = 300, H = 175;
            const padL = 46, padR = 16, padT = 22, padB = 28;
            const plotW = W - padL - padR;
            const plotH = H - padT - padB;

            const passos = 10;
            const maxCusto = Math.max(custoTotalA || 0, custoTotalB || 0, 1) * 1.12;

            const scaleX = (idx) => padL + (idx / passos) * plotW;
            const scaleY = (v) => padT + plotH - (Math.max(0, v) / maxCusto) * plotH;

            for (let i = 0; i <= 3; i++) {
                const tickVal = (maxCusto * i) / 3;
                const y = scaleY(tickVal);
                const gl = document.createElementNS("http://www.w3.org/2000/svg", "line");
                gl.setAttribute("x1", padL); gl.setAttribute("y1", y);
                gl.setAttribute("x2", W - padR); gl.setAttribute("y2", y);
                gl.setAttribute("stroke", "#1e293b"); gl.setAttribute("stroke-width", "1");
                svg.appendChild(gl);

                const tl = document.createElementNS("http://www.w3.org/2000/svg", "text");
                tl.setAttribute("x", padL - 5); tl.setAttribute("y", y + 3);
                tl.setAttribute("fill", "#94a3b8"); tl.setAttribute("font-size", "8.5");
                tl.setAttribute("text-anchor", "end");
                tl.textContent = `${Math.round(tickVal)}€`;
                svg.appendChild(tl);
            }

            const axisX = document.createElementNS("http://www.w3.org/2000/svg", "line");
            axisX.setAttribute("x1", padL); axisX.setAttribute("y1", padT + plotH);
            axisX.setAttribute("x2", W - padR); axisX.setAttribute("y2", padT + plotH);
            axisX.setAttribute("stroke", "#475569"); axisX.setAttribute("stroke-width", "1");
            svg.appendChild(axisX);

            const axisY = document.createElementNS("http://www.w3.org/2000/svg", "line");
            axisY.setAttribute("x1", padL); axisY.setAttribute("y1", padT);
            axisY.setAttribute("x2", padL); axisY.setAttribute("y2", padT + plotH);
            axisY.setAttribute("stroke", "#475569"); axisY.setAttribute("stroke-width", "1");
            svg.appendChild(axisY);

            let ptsA = "", ptsB = "";
            for (let i = 0; i <= passos; i++) {
                const frac = i / passos;
                const px = scaleX(i);
                const pyA = scaleY(custoTotalA * frac);
                const pyB = scaleY(custoTotalB * frac);
                ptsA += `${px},${pyA} `;
                ptsB += `${px},${pyB} `;
            }

            const polyA = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
            polyA.setAttribute("fill", "none"); polyA.setAttribute("stroke", "#38bdf8");
            polyA.setAttribute("stroke-width", "2.2"); polyA.setAttribute("points", ptsA.trim());
            svg.appendChild(polyA);

            const polyB = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
            polyB.setAttribute("fill", "none"); polyB.setAttribute("stroke", "#fbbf24");
            polyB.setAttribute("stroke-width", "2.2"); polyB.setAttribute("stroke-dasharray", "4,2");
            polyB.setAttribute("points", ptsB.trim());
            svg.appendChild(polyB);

            const lblIni = document.createElementNS("http://www.w3.org/2000/svg", "text");
            lblIni.setAttribute("x", padL); lblIni.setAttribute("y", H - 9);
            lblIni.setAttribute("fill", "#94a3b8"); lblIni.setAttribute("font-size", "8.5");
            lblIni.textContent = "0 furos";
            svg.appendChild(lblIni);

            const lblFim = document.createElementNS("http://www.w3.org/2000/svg", "text");
            lblFim.setAttribute("x", W - padR); lblFim.setAttribute("y", H - 9);
            lblFim.setAttribute("fill", "#94a3b8"); lblFim.setAttribute("font-size", "8.5");
            lblFim.setAttribute("text-anchor", "end");
            lblFim.textContent = `${qtdFuros} furos`;
            svg.appendChild(lblFim);
        }

        function atualizarComparacao() {
            const brocaAtualKey = document.getElementById('broca').value;
            const grupoEfetivoKey = getGrupoEfetivo();
            const fonteComp = document.getElementById('comp-ferramenta').value;
            const varCompKey = document.getElementById('comp-variante').value;
            const avisoEl = document.getElementById('comp-aviso-grupo');
            const capEl = document.getElementById('comp-capacidade-texto');
            const beEl = document.getElementById('comp-breakeven-texto');
            const destEl = document.getElementById('comp-resumo-lote-destaque');
            const subEl = document.getElementById('res-comp-subtitulo');
            const corpo = document.getElementById('comp-tabela-corpo');
            const btnUsar = document.getElementById('btn-usar-comparada');

            const ctx = obterContextoCalculoAtual();
            const varAtualPrincipal = getVarianteAtiva();
            const calcAtual = (brocaAtualKey && dados[brocaAtualKey])
                ? calcularMetricasFerramenta(brocaAtualKey, varAtualPrincipal, grupoEfetivoKey, ctx)
                : null;

            const precoAtual = parseFloat(document.getElementById('comp-preco-atual').value) || 0;
            const vidaAtual = parseFloat(document.getElementById('comp-vida-atual').value) || 1;
            const vidaUnidAtual = document.getElementById('comp-vida-unid-atual').value;
            const afiQtdAtual = parseInt(document.getElementById('comp-afi-qtd-atual').value, 10) || 0;
            const afiCustoAtual = parseFloat(document.getElementById('comp-afi-custo-atual').value) || 0;

            const precoAlvo = parseFloat(document.getElementById('comp-preco-alvo').value) || 0;
            const vidaAlvo = parseFloat(document.getElementById('comp-vida-alvo').value) || 1;
            const vidaUnidAlvo = document.getElementById('comp-vida-unid-alvo').value;
            const afiQtdAlvo = parseInt(document.getElementById('comp-afi-qtd-alvo').value, 10) || 0;
            const afiCustoAlvo = parseFloat(document.getElementById('comp-afi-custo-alvo').value) || 0;

            const fatorCorteInterrompido = corteInterrompidoAtivo ? 0.70 : 1.0;

            const inpMetrosCont = document.getElementById('comp-metros-continuo');
            const spanEquivCont = document.getElementById('comp-equiv-continuo');
            let metrosContinuoRef = parseFloat(inpMetrosCont?.value) || 90;
            if (metrosContinuoRef <= 0) metrosContinuoRef = 90;
            const furosEquivContinuo = Math.max(1, Math.round((metrosContinuoRef * 1000) / Math.max(1, ctx.profundidade)));
            if (spanEquivCont) {
                spanEquivCont.innerText = `(~${furosEquivContinuo} furos)`;
            }

            const requerPiloto = document.getElementById('comp-requer-piloto')?.checked || false;
            const tempoPilotoSeg = parseFloat(document.getElementById('comp-tempo-piloto-seg')?.value) || 0;
            const custoPilotoFuro = parseFloat(document.getElementById('comp-custo-piloto-furo')?.value) || 0;
            const usaBrocaCanhao = document.getElementById('comp-usa-broca-canhao')?.checked || false;
            const tempoParagemAfiMin = parseFloat(document.getElementById('comp-tempo-paragem-afi-min')?.value) || 0;

            let calcAlvo = null;
            let nomeAlvoExib = 'Ferramenta Comparada';

            if (fonteComp === '__CLIENTE__') {
                nomeAlvoExib = (document.getElementById('comp-cliente-nome').value || '').trim() || 'Ferramenta do Cliente';
                const vcCli = parseFloat(document.getElementById('comp-cliente-vc').value) || 70;
                const fCli = parseFloat(document.getElementById('comp-cliente-f').value) || 0.02;

                const vidaEstimadaFurosAlvo = calcularVidaTotalFuros(vidaAlvo, vidaUnidAlvo, afiQtdAlvo, ctx.profundidade, fatorCorteInterrompido);
                const furosPorAfiaçãoCanhao = Math.max(1, Math.round(vidaEstimadaFurosAlvo / (1 + Math.max(0, afiQtdAlvo))));

                calcAlvo = calcularMetricasManualCliente(nomeAlvoExib, vcCli, fCli, grupoEfetivoKey, {
                    ...ctx,
                    requerPiloto,
                    tempoPilotoSeg,
                    custoPilotoFuro,
                    usaBrocaCanhao,
                    tempoParagemAfiMin,
                    furosPorAfiação: furosPorAfiaçãoCanhao
                });

                const resumoCanhaoEl = document.getElementById('comp-canhao-resumo');
                if (resumoCanhaoEl) {
                    resumoCanhaoEl.innerText = `${calcAlvo.numParagensLote} paragem(ns) · +${calcAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min`;
                }
                btnUsar.classList.add('hidden');
            } else {
                calcAlvo = (fonteComp && dados[fonteComp])
                    ? calcularMetricasFerramenta(fonteComp, varCompKey, grupoEfetivoKey, ctx)
                    : null;
                nomeAlvoExib = calcAlvo ? `${calcAlvo.nome} (${varCompKey})` : 'Ferramenta Comparada';
                btnUsar.classList.remove('hidden');
            }

            const nomeAtualExib = calcAtual ? `${calcAtual.nome} (${varAtualPrincipal})` : 'Ferramenta Atual';
            document.getElementById('comp-th-atual').innerText = nomeAtualExib;
            document.getElementById('comp-th-alvo').innerText = nomeAlvoExib;
            if (subEl) {
                subEl.innerText = `${nomeAtualExib}  vs.  ${nomeAlvoExib}  ·  Lote: ${ctx.qtdFuros} furos (Ø ${ctx.diametro.toFixed(2)} mm × ${ctx.profundidade.toFixed(0)} mm)`;
            }

            if (!calcAtual || !calcAlvo) {
                avisoEl.innerText = "Selecione um modelo de ferramenta válido e grupo de material para comparar.";
                avisoEl.classList.remove('hidden');
                corpo.innerHTML = '';
                return;
            }

            const avisos = [];
            if (ctx.profundidade > calcAtual.limiteNominalMm) {
                avisos.push(`Ferramenta atual excede o limite nominal (${calcAtual.limiteNominalMm.toFixed(1)} mm) para ${ctx.profundidade.toFixed(0)} mm.`);
            }
            if (fonteComp !== '__CLIENTE__' && ctx.profundidade > calcAlvo.limiteNominalMm) {
                avisos.push(`Ferramenta comparada excede o limite nominal (${calcAlvo.limiteNominalMm.toFixed(1)} mm) para ${ctx.profundidade.toFixed(0)} mm.`);
            }
            if (corteInterrompidoAtivo) {
                avisos.push(`Corte interrompido ativo (-30% de vida útil por impacto). Referência contínuo: ${metrosContinuoRef.toFixed(0)} m (~${furosEquivContinuo} furos).`);
            }
            if (fonteComp === '__CLIENTE__' && requerPiloto) {
                avisos.push(`Furo-piloto ativo: +${tempoPilotoSeg.toFixed(0)} s/furo e +${custoPilotoFuro.toFixed(3)} €/furo.`);
                if (usaBrocaCanhao) {
                    avisos.push(`Broca canhão sem gémea: ${calcAlvo.numParagensLote} paragem(ns) de ${tempoParagemAfiMin.toFixed(0)} min (+${calcAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min no lote).`);
                }
            }

            if (avisos.length > 0) {
                avisoEl.innerText = avisos.join(" | ");
                avisoEl.classList.remove('hidden');
            } else {
                avisoEl.classList.add('hidden');
            }

            const custoFerrAtual = calcularCustoFerramentaLote(precoAtual, vidaAtual, vidaUnidAtual, afiQtdAtual, afiCustoAtual, ctx.qtdFuros, ctx.profundidade, fatorCorteInterrompido);
            const custoFerrAlvo = calcularCustoFerramentaLote(precoAlvo, vidaAlvo, vidaUnidAlvo, afiQtdAlvo, afiCustoAlvo, ctx.qtdFuros, ctx.profundidade, fatorCorteInterrompido);

            const custoPilotoLoteAlvo = calcAlvo.custoPilotoLote || 0;
            const custoTotalAtual = calcAtual.custoMaqLote + custoFerrAtual.custoFerramentaLote;
            const custoTotalAlvo = calcAlvo.custoMaqLote + custoFerrAlvo.custoFerramentaLote + custoPilotoLoteAlvo;
            const custoTotalFuroAtual = custoTotalAtual / ctx.qtdFuros;
            const custoTotalFuroAlvo = custoTotalAlvo / ctx.qtdFuros;

            const diffTempoMin = calcAtual.tempoTotalMin - calcAlvo.tempoTotalMin;
            const diffCustoTotal = custoTotalAtual - custoTotalAlvo;

            if (Math.abs(diffTempoMin) < 0.05) {
                capEl.innerText = `Tempos equivalentes no lote (${calcAtual.tempoTotalMin.toFixed(1)} min).`;
            } else if (diffTempoMin > 0) {
                capEl.innerText = `MAPAL poupa ${diffTempoMin.toFixed(1)} min no lote (${calcAtual.tempoTotalMin.toFixed(1)} min vs ${calcAlvo.tempoTotalMin.toFixed(1)} min).`;
            } else {
                capEl.innerText = `Ferramenta comparada é ${Math.abs(diffTempoMin).toFixed(1)} min mais rápida no lote (${calcAlvo.tempoTotalMin.toFixed(1)} min vs ${calcAtual.tempoTotalMin.toFixed(1)} min).`;
            }

            const custoFixoPorFuroAtual = (calcAtual.custoMaqFuro) + (custoFerrAtual.custoFerramentaFuro);
            const custoFixoPorFuroAlvo = (calcAlvo.custoMaqFuro) + (custoFerrAlvo.custoFerramentaFuro) + (calcAlvo.custoPilotoEfetivo || 0);
            const diferencaCustoPorFuro = custoFixoPorFuroAlvo - custoFixoPorFuroAtual;
            const diferencaInvestimentoInicial = precoAtual - precoAlvo;

            if (diferencaInvestimentoInicial > 0 && diferencaCustoPorFuro > 0) {
                const furosBreakEven = diferencaInvestimentoInicial / diferencaCustoPorFuro;
                beEl.innerText = `MAPAL paga a diferença inicial aos ~${Math.ceil(furosBreakEven)} furos (custo/furo ${diferencaCustoPorFuro.toFixed(3)} € menor).`;
            } else if (diferencaInvestimentoInicial < 0 && diferencaCustoPorFuro < 0) {
                const furosBreakEven = Math.abs(diferencaInvestimentoInicial) / Math.abs(diferencaCustoPorFuro);
                beEl.innerText = `Ferramenta comparada paga a diferença inicial aos ~${Math.ceil(furosBreakEven)} furos.`;
            } else if (diffCustoTotal > 0.01) {
                beEl.innerText = `MAPAL já é mais económica no lote em ${diffCustoTotal.toFixed(2)} € (sem ponto de reversão desfavorável).`;
            } else if (diffCustoTotal < -0.01) {
                beEl.innerText = `Ferramenta comparada mantém menor custo no lote (${Math.abs(diffCustoTotal).toFixed(2)} € de vantagem).`;
            } else {
                beEl.innerText = `Custos empatados no lote de ${ctx.qtdFuros} furos.`;
            }

            if (destEl) {
                if (diffCustoTotal > 0.01) {
                    destEl.innerText = `Poupança de ${diffCustoTotal.toFixed(2)} € com MAPAL no lote (${custoTotalAtual.toFixed(2)} € vs ${custoTotalAlvo.toFixed(2)} €).`;
                } else if (diffCustoTotal < -0.01) {
                    destEl.innerText = `Ferramenta comparada fica ${Math.abs(diffCustoTotal).toFixed(2)} € mais barata no lote (${custoTotalAlvo.toFixed(2)} € vs ${custoTotalAtual.toFixed(2)} €).`;
                } else {
                    destEl.innerText = `Custo total idêntico no lote (${custoTotalAtual.toFixed(2)} €).`;
                }
            }

            renderGraficoBarrasComparacao('svg-comp-custo', 'MAPAL', custoTotalAtual, '#3b82f6', 'Comparada', custoTotalAlvo, '#f43f5e', '€');
            renderGraficoBarrasComparacao('svg-comp-tempo', 'MAPAL', calcAtual.tempoTotalMin, '#10b981', 'Comparada', calcAlvo.tempoTotalMin, '#f59e0b', 'm');
            renderGraficoBreakEven('svg-comp-breakeven', custoTotalAtual, custoTotalAlvo, ctx.qtdFuros);

            window._ultimoComparativo = {
                nomeAtual: nomeAtualExib,
                nomeAlvo: nomeAlvoExib,
                isCliente: fonteComp === '__CLIENTE__',
                corteInterrompido: corteInterrompidoAtivo,
                metrosContinuoRef,
                furosEquivContinuo,
                requerPiloto: fonteComp === '__CLIENTE__' ? requerPiloto : false,
                tempoPilotoSeg: fonteComp === '__CLIENTE__' ? tempoPilotoSeg : 0,
                custoPilotoFuro: fonteComp === '__CLIENTE__' ? custoPilotoFuro : 0,
                usaBrocaCanhao: fonteComp === '__CLIENTE__' ? usaBrocaCanhao : false,
                tempoParagemAfiMin: fonteComp === '__CLIENTE__' ? tempoParagemAfiMin : 0,
                numParagensCanhao: calcAlvo.numParagensLote || 0,
                tempoParagemCanhaoLoteMin: calcAlvo.tempoParagemCanhaoLoteMin || 0,
                custoPilotoLote: custoPilotoLoteAlvo,
                qtdFuros: ctx.qtdFuros,
                vcAtual: calcAtual.vcFinal, vcAlvo: calcAlvo.vcFinal,
                fAtual: calcAtual.fFinal, fAlvo: calcAlvo.fFinal,
                nAtual: calcAtual.n, nAlvo: calcAlvo.n,
                vfAtual: calcAtual.vf, vfAlvo: calcAlvo.vf,
                tempoFuroAtual: calcAtual.tempoFuroSeg, tempoFuroAlvo: calcAlvo.tempoFuroSeg,
                tempoTotalAtual: calcAtual.tempoTotalMin, tempoTotalAlvo: calcAlvo.tempoTotalMin,
                vidaFurosAtual: custoFerrAtual.vidaTotalFuros, vidaFurosAlvo: custoFerrAlvo.vidaTotalFuros,
                afiQtdAtual, afiQtdAlvo,
                custoFerrLoteAtual: custoFerrAtual.custoFerramentaLote, custoFerrLoteAlvo: custoFerrAlvo.custoFerramentaLote,
                custoMaqLoteAtual: calcAtual.custoMaqLote, custoMaqLoteAlvo: calcAlvo.custoMaqLote,
                custoTotalAtual, custoTotalAlvo,
                custoTotalFuroAtual, custoTotalFuroAlvo,
                diffTempoMin, diffCustoTotal
            };

            const fmtDiff = (vAtual, vAlvo, dec = 1, unit = '', inverterSinal = false) => {
                const d = inverterSinal ? (vAlvo - vAtual) : (vAtual - vAlvo);
                const sinal = d > 0 ? '+' : '';
                return `${sinal}${d.toFixed(dec)}${unit}`;
            };

            const rows = [
                ['Vc (m/min)', `${calcAtual.vcFinal.toFixed(0)} m/min`, `${calcAlvo.vcFinal.toFixed(0)} m/min`, fmtDiff(calcAtual.vcFinal, calcAlvo.vcFinal, 0, ' m/min')],
                ['Avanço f (mm/rot)', `${calcAtual.fFinal.toFixed(4)}`, `${calcAlvo.fFinal.toFixed(4)}`, fmtDiff(calcAtual.fFinal, calcAlvo.fFinal, 4, '')],
                ['Rotações (rpm)', `${calcAtual.n}`, `${calcAlvo.n}`, fmtDiff(calcAtual.n, calcAlvo.n, 0, ' rpm')],
                ['Avanço Trabalho vf (mm/min)', `${calcAtual.vf}`, `${calcAlvo.vf}`, fmtDiff(calcAtual.vf, calcAlvo.vf, 0, ' mm/min')],
                ['Vida Útil Estimada (c/ reaf.)', `${custoFerrAtual.vidaTotalFuros.toFixed(0)} furos (${afiQtdAtual} reaf.)`, `${custoFerrAlvo.vidaTotalFuros.toFixed(0)} furos (${afiQtdAlvo} reaf.)`, fmtDiff(custoFerrAtual.vidaTotalFuros, custoFerrAlvo.vidaTotalFuros, 0, ' furos')],
                ['Tempo / Furo (seg)', `${calcAtual.tempoFuroSeg.toFixed(1)} s`, `${calcAlvo.tempoFuroSeg.toFixed(1)} s`, fmtDiff(calcAtual.tempoFuroSeg, calcAlvo.tempoFuroSeg, 1, ' s')],
                ['Tempo Total Lote (min)', `${calcAtual.tempoTotalMin.toFixed(1)} min`, `${calcAlvo.tempoTotalMin.toFixed(1)} min`, fmtDiff(calcAtual.tempoTotalMin, calcAlvo.tempoTotalMin, 1, ' min')],
                ['Custo Ferramenta Lote (€)', `${custoFerrAtual.custoFerramentaLote.toFixed(2)} €`, `${custoFerrAlvo.custoFerramentaLote.toFixed(2)} €`, fmtDiff(custoFerrAtual.custoFerramentaLote, custoFerrAlvo.custoFerramentaLote, 2, ' €')],
                ['Custo Máquina Lote (€)', `${calcAtual.custoMaqLote.toFixed(2)} €`, `${calcAlvo.custoMaqLote.toFixed(2)} €`, fmtDiff(calcAtual.custoMaqLote, calcAlvo.custoMaqLote, 2, ' €')]
            ];

            if (fonteComp === '__CLIENTE__' && requerPiloto) {
                rows.push(['Custo Piloto Lote (€)', `0.00 €`, `${custoPilotoLoteAlvo.toFixed(2)} €`, `${(-custoPilotoLoteAlvo).toFixed(2)} €`]);
                if (usaBrocaCanhao) {
                    rows.push(['Paragens Afiação Canhão', `0 paragens`, `${calcAlvo.numParagensLote} paragens (+${calcAlvo.tempoParagemCanhaoLoteMin.toFixed(1)} min)`, `-${calcAlvo.numParagensLote} paragens`]);
                }
            }

            rows.push(['Custo Total Lote (€)', `<strong>${custoTotalAtual.toFixed(2)} €</strong>`, `<strong>${custoTotalAlvo.toFixed(2)} €</strong>`, `<strong>${fmtDiff(custoTotalAtual, custoTotalAlvo, 2, ' €')}</strong>`]);
            rows.push(['Custo Total / Furo (€)', `${custoTotalFuroAtual.toFixed(3)} €`, `${custoTotalFuroAlvo.toFixed(3)} €`, fmtDiff(custoTotalFuroAtual, custoTotalFuroAlvo, 3, ' €')]);

            corpo.innerHTML = '';
            rows.forEach(r => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="py-1.5 px-3 text-slate-300 font-medium">${r[0]}</td>
                    <td class="py-1.5 px-3 text-blue-300">${r[1]}</td>
                    <td class="py-1.5 px-3 text-emerald-300">${r[2]}</td>
                    <td class="py-1.5 px-3 text-amber-300">${r[3]}</td>
                `;
                corpo.appendChild(tr);
            });
        }

        function aplicarFerramentaComparada() {
            const fonteComp = document.getElementById('comp-ferramenta').value;
            const varCompKey = document.getElementById('comp-variante').value;
            if (!fonteComp || fonteComp === '__CLIENTE__' || !dados[fonteComp]) return;

            const toolComp = dados[fonteComp];
            linhaAtivaInterna = toolComp.linha;
            if (toolComp.categoria) {
                document.getElementById('categoria').value = toolComp.categoria;
            }
            atualizarFiltroBrocas(true);
            document.getElementById('broca').value = fonteComp;
            mudarBroca(varCompKey);
            fecharJanelaResultadoComparacao();
            fecharModalComparacao();
        }

        function abrirModalExportacao() {
            document.getElementById('modal-export').classList.remove('hidden');
        }

        function fecharModalExportacao() {
            document.getElementById('modal-export').classList.add('hidden');
        }

        function gerarPDF() {
            if (!window.jspdf || !window.jspdf.jsPDF) {
                alert("Biblioteca jsPDF não carregada. Verifique a ligação à internet.");
                return;
            }

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

            const tipoRelatorio = isProMode
                ? (document.querySelector('input[name="tipo-relatorio"]:checked')?.value || 'resumido')
                : 'resumido';
            const incluirComparativo = isProMode && document.getElementById('comp-incluir-pdf').checked && window._ultimoComparativo;

            const brocaKey = document.getElementById('broca').value;
            const grupoSelKey = normMmg(document.getElementById('grupo').value);
            const grupoEfetivoKey = getGrupoEfetivo();

            const toolNome = (brocaKey && dados[brocaKey]) ? dados[brocaKey].nome : 'Sem modelo selecionado';
            const linhaNome = linhaAtivaInterna ? fmtGamaLabel(linhaAtivaInterna) : 'Todas';
            const varianteNome = getVarianteAtiva();
            const grupoNome = grupoEfetivoKey ? obterLabelGrupoMmg(grupoEfetivoKey) : '—';
            const ligaAtiva = document.getElementById('liga-check').checked ? 'Sim (>8% liga -> avança grupo)' : 'Não';
            const corteIntTexto = corteInterrompidoAtivo ? 'Sim (Corte Interrompido -30% vida)' : 'Não (Corte Contínuo)';
            const refMap = { 'int': 'Refrigeração Interna', 'ext': 'Refrigeração Externa', 'mql': 'MQL', 'ar': 'Ar' };
            const refrigTexto = refMap[refrigAtual] || refrigAtual;

            const diametro = parseFloat(document.getElementById('diametro').value) || 12.00;
            const profundidade = parseFloat(document.getElementById('profundidade').value) || 31.0;
            const qtdFuros = parseInt(document.getElementById('qtd-furos').value, 10) || 50;
            const densidade = parseFloat(document.getElementById('densidade').value) || 7.85;
            const precoSucata = parseFloat(document.getElementById('preco-sucata').value) || 0.35;
            const custoHora = parseFloat(document.getElementById('custo-hora').value) || 50.00;

            const vcVal = document.getElementById('input-vc').value;
            const fVal = document.getElementById('input-f').value;
            const nVal = document.getElementById('res-n').innerText;
            const vfVal = document.getElementById('res-vf').innerText;
            const forcaVal = document.getElementById('res-forca').innerText;
            const forcaKgfVal = document.getElementById('res-forca-kgf').innerText;
            const binarioVal = document.getElementById('res-binario-card').innerText;
            const potVal = document.getElementById('val-gauge-pot').innerText;
            const badgePotVal = document.getElementById('badge-gauge-pot').innerText;
            const badgeBinVal = document.getElementById('badge-gauge-bin').innerText;

            const peckingAtivo = document.getElementById('pecking-check').checked;
            const peckingUnid = document.getElementById('pecking-unidade').value;
            const peckingPasso = parseFloat(document.getElementById('pecking-passo').value) || 3.0;
            const peckingRetensao = parseFloat(document.getElementById('pecking-retensao').value) || 5000;
            const passoMm = peckingUnid === 'xd' ? (peckingPasso * diametro) : peckingPasso;
            const numPassos = Math.max(1, Math.ceil(profundidade / passoMm));

            const dataAtual = new Date().toLocaleDateString('pt-PT');
            const horaAtual = new Date().toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });

            doc.setFillColor(15, 23, 42);
            doc.rect(0, 0, 210, 32, 'F');

            doc.setTextColor(255, 255, 255);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(15);
            doc.text("PARÂMETROS DE CORTE MAPAL", 14, 14);

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(148, 163, 184);
            const subtituloDoc = tipoRelatorio === 'completo'
                ? "Proposta Técnico-Comercial Completa & Análise de Custos (Nível Pro)"
                : "Ficha Técnica de Parâmetros de Corte (Nível Básico)";
            doc.text(subtituloDoc, 14, 21);

            doc.setFontSize(8.5);
            doc.setTextColor(203, 213, 225);
            doc.text(`Data: ${dataAtual} ${horaAtual}`, 196, 14, { align: 'right' });
            doc.text(`Gama: ${linhaNome} | Refrig.: ${refrigTexto}`, 196, 21, { align: 'right' });

            let y = 40;

            doc.setTextColor(15, 23, 42);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.text("1. Configuração da Ferramenta e Material", 14, y);
            y += 6;

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9.5);
            const configLines = [
                `Modelo / Família: ${toolNome} (${varianteNome})`,
                `Grupo de Material (MMG): ${grupoNome}${ligaAtiva === 'Sim (>8% liga -> avança grupo)' ? ` [Base: ${grupoSelKey}]` : ''}`,
                `Regra Liga > 8%: ${ligaAtiva}   |   Condição Corte: ${corteIntTexto}`,
                `Diâmetro (Ø): ${diametro.toFixed(2)} mm   |   Profundidade / Furo (L): ${profundidade.toFixed(1)} mm`
            ];
            if (referenciaAtivaObj) {
                configLines.push(`Referência Ativa: Order no. ${referenciaAtivaObj.order_no || '—'} | Spec: ${referenciaAtivaObj.specification || '—'} | l3 máx.: ${referenciaAtivaObj.l3 ?? '—'} mm`);
            }
            if (tipoRelatorio === 'completo') {
                configLines.push(`Quantidade (Lote): ${qtdFuros} furos   |   Densidade: ${densidade.toFixed(2)} g/cm³   |   Sucata: ${precoSucata.toFixed(2)} €/kg   |   Custo Hora: ${custoHora.toFixed(2)} €/h`);
                if (peckingAtivo) {
                    configLines.push(`Ciclo Pecking: Ativo — Passo Q = ${peckingPasso} ${peckingUnid.toUpperCase()} (${passoMm.toFixed(1)} mm, ${numPassos} passos) | Retração = ${peckingRetensao} mm/min`);
                } else {
                    configLines.push(`Ciclo Pecking: Desativado (furação contínua)`);
                }
            }

            configLines.forEach(line => {
                doc.text(line, 14, y);
                y += 5;
            });

            y += 3;

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.text("2. Parâmetros de Corte Calculados", 14, y);
            y += 6;

            doc.setFillColor(241, 245, 249);
            doc.rect(14, y - 4, 182, 16, 'F');
            doc.setDrawColor(203, 213, 225);
            doc.rect(14, y - 4, 182, 16, 'S');

            doc.setFontSize(9);
            doc.setTextColor(71, 85, 105);
            doc.text("Vc (m/min)", 20, y + 1);
            doc.text("Avanço f (mm/rot)", 62, y + 1);
            doc.text("Rotações (rpm)", 110, y + 1);
            doc.text("Avanço vf (mm/min)", 152, y + 1);

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.setTextColor(15, 23, 42);
            doc.text(`${vcVal} m/min`, 20, y + 8);
            doc.text(`${Number(fVal).toFixed(4)} mm/rot`, 62, y + 8);
            doc.text(`${nVal} rpm`, 110, y + 8);
            doc.text(`${vfVal} mm/min`, 152, y + 8);

            y += 22;

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.text("3. Esforços de Corte e Monitor do Spindle", 14, y);
            y += 6;

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9.5);
            doc.text(`Força Axial (Ff): ${forcaVal} (${forcaKgfVal})   |   Binário de Corte (Mc): ${binarioVal} [${badgeBinVal}]`, 14, y);
            y += 5;
            doc.text(`Potência de Corte Requerida: ${potVal} [${badgePotVal}]   |   Ajustes: Vc ${vcPct >= 0 ? '+' : ''}${vcPct}%, f ${fPct >= 0 ? '+' : ''}${fPct}%`, 14, y);
            y += 8;

            if (tipoRelatorio === 'completo') {
                const tempoTotalTxt = document.getElementById('res-tempo-total').innerText;
                const metragemTxt = document.getElementById('res-metragem').innerText;
                const volumeTxt = document.getElementById('res-volume-total').innerText;
                const taxaTxt = document.getElementById('res-taxa').innerText;
                const pesoTxt = document.getElementById('res-peso').innerText;
                const pesoGTxt = document.getElementById('res-peso-g').innerText;
                const sucataValTxt = document.getElementById('res-sucata-val').innerText;
                const sucataFuroTxt = document.getElementById('res-sucata-furo').innerText;
                const custoTotalTxt = document.getElementById('res-custo-total').innerText;

                doc.setFont('helvetica', 'bold');
                doc.setFontSize(11);
                doc.text("4. Indicadores de Produção, Material e Custos (Lote)", 14, y);
                y += 6;

                doc.setFont('helvetica', 'normal');
                doc.setFontSize(9.5);
                const prodLines = [
                    `Tempo de Ciclo: ${tempoTotalTxt}   |   Metragem Linear: ${metragemTxt}`,
                    `Volume Removido: ${volumeTxt}   |   Taxa de Remoção: ${taxaTxt}`,
                    `Peso Total de Limalha: ${pesoTxt} (${pesoGTxt})`,
                    `Valor Total de Sucata: ${sucataValTxt} (${sucataFuroTxt})`,
                    `Custo de Maquinação: ${custoTotalTxt}`
                ];
                prodLines.forEach(line => {
                    doc.text(line, 14, y);
                    y += 5;
                });
                y += 3;
            }

            if (incluirComparativo && window._ultimoComparativo) {
                const c = window._ultimoComparativo;
                if (y > 225) {
                    doc.addPage();
                    y = 20;
                }
                doc.setFont('helvetica', 'bold');
                doc.setFontSize(11);
                doc.setTextColor(15, 23, 42);
                doc.text("5. Comparação Técnico-Comercial", 14, y);
                y += 6;

                doc.setFont('helvetica', 'normal');
                doc.setFontSize(9);
                doc.text(`Atual: ${c.nomeAtual}   vs.   Comparada: ${c.nomeAlvo}`, 14, y);
                y += 5;
                if (c.corteInterrompido) {
                    doc.text(`Condição: Corte Interrompido (-30% vida) | Ref. contínuo: ${c.metrosContinuoRef.toFixed(0)} m (~${c.furosEquivContinuo} furos)`, 14, y);
                    y += 5;
                }
                if (c.isCliente && c.requerPiloto) {
                    doc.text(`Furo-Piloto: +${c.tempoPilotoSeg.toFixed(0)} s/furo, +${c.custoPilotoFuro.toFixed(3)} €/furo (${c.custoPilotoLote.toFixed(2)} € no lote)`, 14, y);
                    y += 5;
                    if (c.usaBrocaCanhao) {
                        doc.text(`Broca Canhão (s/ gémea): ${c.numParagensCanhao} paragem(ns) de ${c.tempoParagemAfiMin.toFixed(0)} min (+${c.tempoParagemCanhaoLoteMin.toFixed(1)} min no lote)`, 14, y);
                        y += 5;
                    }
                }
                doc.text(`Tempo Total Lote: Atual ${c.tempoTotalAtual.toFixed(1)} min vs. Comparada ${c.tempoTotalAlvo.toFixed(1)} min (Dif.: ${c.diffTempoMin >= 0 ? '+' : ''}${c.diffTempoMin.toFixed(1)} min)`, 14, y);
                y += 5;
                doc.text(`Custo Total Lote: Atual ${c.custoTotalAtual.toFixed(2)} € vs. Comparada ${c.custoTotalAlvo.toFixed(2)} € (Dif.: ${c.diffCustoTotal >= 0 ? '+' : ''}${c.diffCustoTotal.toFixed(2)} €)`, 14, y);
                y += 5;
                doc.text(`Custo Total / Furo: Atual ${c.custoTotalFuroAtual.toFixed(3)} € vs. Comparada ${c.custoTotalFuroAlvo.toFixed(3)} €`, 14, y);
                y += 7;
            }

            if (y > 245) {
                doc.addPage();
                y = 20;
            }
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(10);
            doc.setTextColor(15, 23, 42);
            doc.text("Tabela de Referência do Catálogo (Diâmetros)", 14, y);
            y += 5;

            const rows = Array.from(document.querySelectorAll('#tabela-ref tr'));
            if (rows.length > 0) {
                doc.setFillColor(30, 41, 59);
                doc.rect(14, y - 3.5, 182, 6, 'F');
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(8.5);
                doc.text("Ø (mm)", 18, y + 0.5);
                doc.text("f Cat. (mm/rot)", 58, y + 0.5);
                doc.text("RPM (n)", 108, y + 0.5);
                doc.text("Avanço vf (mm/min)", 150, y + 0.5);
                y += 6;

                doc.setTextColor(15, 23, 42);
                doc.setFont('helvetica', 'normal');
                rows.forEach((tr, idx) => {
                    if (y > 275) {
                        doc.addPage();
                        y = 20;
                    }
                    const cols = tr.querySelectorAll('td');
                    if (cols.length >= 4) {
                        if (idx % 2 === 1) {
                            doc.setFillColor(248, 250, 252);
                            doc.rect(14, y - 3.5, 182, 5.5, 'F');
                        }
                        doc.text(cols[0].innerText, 18, y + 0.5);
                        doc.text(cols[1].innerText, 58, y + 0.5);
                        doc.text(cols[2].innerText, 108, y + 0.5);
                        doc.text(cols[3].innerText, 150, y + 0.5);
                        y += 5.5;
                    }
                });
            }

            const pageCount = doc.internal.getNumberOfPages();
            for (let i = 1; i <= pageCount; i++) {
                doc.setPage(i);
                doc.setFontSize(8);
                doc.setTextColor(100, 116, 139);
                doc.text(`Created by Bruno Pinto | bruno.pinto@alamo-ferramentas.com | +351 936 959 415`, 14, 290);
                doc.text(`Página ${i} de ${pageCount}`, 196, 290, { align: 'right' });
            }

            const sufixoNome = tipoRelatorio === 'completo' ? 'Proposta_Completa' : 'Ficha_Tecnica';
            doc.save(`MAPAL_${sufixoNome}_${diametro.toFixed(1)}mm.pdf`);
            fecharModalExportacao();
        }

        carregarCatalogoEParametrosJson();
        aplicarModoUI();
        filtrarCatalogoCascata('init');
        atualizarFiltroBrocas(false);
        atualizarPainelCotas();
        atualizarCalculo();
    </script>
</body>
</html>
'''

html_final = (
    html_content
    .replace("__PRO_PASSWORD_PLACEHOLDER__", pro_password_js)
    .replace("__FAMILIAS_JSON_PLACEHOLDER__", familias_js)
    .replace("__REFERENCIAS_JSON_PLACEHOLDER__", referencias_js)
    .replace("__PARAMETROS_JSON_PLACEHOLDER__", parametros_json_js)
    .replace("__GRUPOS_MMG_JSON_PLACEHOLDER__", grupos_mmg_js)
    .replace("__LOGO_ALAMO_PLACEHOLDER__", json.dumps(logo_alamo_b64))
    .replace("__LOGO_MAPAL_PLACEHOLDER__", json.dumps(logo_mapal_b64))
)

components.html(html_final, height=920, scrolling=False)