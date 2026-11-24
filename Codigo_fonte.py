import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Parâmetros de Corte MAPAL", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding: 0.5rem 0.75rem; max-width: 100% !important;}
iframe {height: 100vh !important;}
</style>
""", unsafe_allow_html=True)

def load_json(p: str):
    path = Path(p)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

pro_password = str(st.secrets.get("PRO_PASSWORD", "")) if hasattr(st, "secrets") else ""

payload = {
    "__PRO_PW__": json.dumps(pro_password),
    "__FAM__": json.dumps(load_json("dados/familias.json"), ensure_ascii=False),
    "__REF__": json.dumps(load_json("dados/referencias.json"), ensure_ascii=False),
    "__PAR__": json.dumps(load_json("dados/furacao_parametros.json"), ensure_ascii=False),
    "__MMG__": json.dumps(load_json("dados/grupos_mmg.json"), ensure_ascii=False),
}

HTML = r"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Parâmetros de Corte MAPAL</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
body {font-family:'Inter',sans-serif;background:#0f172a;color:#f8fafc;margin:0;height:100vh;overflow:hidden;}
.iso-btn,.sub-btn,.mmg-code-btn {font-weight:700;border-radius:6px;transition:.12s;border:1px solid #334155;background:#0f172a;cursor:pointer;}
.iso-btn {font-weight:800;border-radius:7px;padding:6px 4px;font-size:12px;border-width:1.5px;text-align:center;}
.sub-btn {padding:4px 6px;font-size:10.5px;text-align:center;}
.mmg-code-btn {padding:4px 7px;font-size:10px;text-align:left;}
.iso-btn:hover:not(:disabled),.sub-btn:hover:not(:disabled),.mmg-code-btn:hover:not(:disabled) {filter:brightness(1.15);}
.iso-btn:disabled,.sub-btn:disabled,.mmg-code-btn:disabled {opacity:.25;cursor:not-allowed;}
.gauge-needle {transform-box:view-box;transform-origin:100px 100px;transform:rotate(-90deg);transition:transform .35s ease-out;}
</style>
</head>
<body class="h-screen p-2 flex flex-col box-border">
<div class="w-full h-full flex flex-col gap-2">
  <header class="bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 flex flex-wrap justify-between items-center gap-2 shrink-0">
    <div class="flex items-center gap-2.5">
      <h1 class="text-base font-bold text-white">⚙️ Parâmetros de Corte MAPAL</h1>
      <span id="badge-nivel-ativo" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-700 text-cyan-300 border border-slate-600">Nível Básico</span>
    </div>
    <div class="flex items-center gap-2">
      <button id="btn-modo-pro" onclick="gerirModoPro()" class="bg-purple-600 hover:bg-purple-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white">🔒 Aderir Nível Pro</button>
      <button onclick="resetRapidoTudo()" title="Repor Vc, f, RPM máx., ajustes % e pecking" class="bg-amber-600 hover:bg-amber-500 px-2.5 py-1 rounded-md text-xs font-medium text-white">↺ Reset Rápido</button>
      <button id="btn-comparar-familia" onclick="abrirModalComparacao()" class="pro-only hidden bg-emerald-600 hover:bg-emerald-500 px-2.5 py-1 rounded-md text-xs font-medium text-white">⚖️ Comparar Família</button>
      <button onclick="abrirModalPdfParametros()" class="bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white">📋 Gerar PDF com parâmetros de corte</button>
      <button onclick="abrirModalExportacao()" class="bg-blue-600 hover:bg-blue-500 px-2.5 py-1 rounded-md text-xs font-medium text-white">📄 <span id="lbl-btn-export">Exportar PDF</span></button>
      <button onclick="toggleFullScreen()" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded-md text-xs font-medium text-white">⛶ Ecrã Inteiro</button>
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
          <input type="text" id="ref-pesquisa" placeholder="Ex: 30902099, 135HA08, -HB, SCD661 12XD..." class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-xs text-white" oninput="filtrarCatalogoCascata('pesquisa')" onkeydown="if(event.key==='Enter') aplicarPesquisaReferencia()">
          <button type="button" onclick="aplicarPesquisaReferencia()" class="bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 rounded-md text-xs font-semibold text-white shrink-0">Aplicar</button>
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
            <label class="text-[10px] font-semibold text-blue-300 uppercase">1. Grupo de Materiais (MMG)</label>
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

        <div class="grid grid-cols-3 gap-1.5">
          <div><label class="text-[10px] font-medium text-slate-300 block">1. Tipo Operação</label><select id="categoria" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-purple-300 font-semibold" onchange="onFiltroCatalogoChange('categoria')"><option value="">Todas</option></select></div>
          <div><label class="text-[10px] font-medium text-slate-300 block">2. Gama / Linha</label><select id="filtro-gama-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white" onchange="onFiltroCatalogoChange('gama')"><option value="">Todas</option></select></div>
          <div><label class="text-[10px] font-medium text-slate-300 block">3. Refrigeração</label><select id="filtro-refrig-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-sky-300 font-semibold" onchange="onFiltroCatalogoChange('refrig')"><option value="">Todas</option></select></div>
        </div>
        <div class="grid grid-cols-3 gap-1.5">
          <div><label class="text-[10px] font-medium text-slate-300 block">4. DIN 6535</label><select id="filtro-encabadouro-cat" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-amber-300 font-semibold" onchange="onFiltroCatalogoChange('encabadouro')"><option value="">Todos</option></select></div>
          <div><label class="text-[10px] font-medium text-slate-300 block">5. Diâmetro d1</label><input type="number" id="filtro-d1" list="lista-d1-sugestoes" step="0.01" min="0.1" max="100" placeholder="Ex: 10.00" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-white" oninput="onFiltroCatalogoChange('d1')" onchange="onFiltroCatalogoChange('d1')"><datalist id="lista-d1-sugestoes"></datalist></div>
          <div><label class="text-[10px] font-medium text-slate-300 block">6. Variante ×D</label><select id="filtro-xd" class="w-full bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-xs text-cyan-300 font-semibold" onchange="onFiltroCatalogoChange('xd')"><option value="">Todas</option></select></div>
        </div>
        <div class="space-y-0.5">
          <div class="flex justify-between"><label class="text-[10px] font-medium text-slate-300">7. Modelo de Ferramenta</label><span id="info-modelo-filtro" class="text-[9px] text-cyan-400 font-mono"></span></div>
          <select id="broca" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white" onchange="onMudarModeloFerramenta()"><option value="">— Vazio (sem modelo selecionado) —</option></select>
        </div>
        <div class="space-y-0.5">
          <label class="text-[10px] font-medium text-slate-300 block">8. Referência / Order no.</label>
          <select id="filtro-order-no" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white" onchange="onSelecionarOrderCatalogo()"><option value="">— Selecionar referência compatível —</option></select>
        </div>
      </div>

      <div class="bg-slate-900 p-2 rounded-md border border-slate-700/80 shrink-0">
        <label class="flex items-start gap-1.5 cursor-pointer text-[11px] text-slate-300">
          <input type="checkbox" id="liga-check" class="mt-0.5 rounded bg-slate-800 border-slate-600" onchange="atualizarCalculo()">
          <span><strong>Soma liga (Cr, Mo, Ni, V, W) &gt; 8%</strong><br><span class="text-[9px] text-amber-400">Regra MAPAL: avança para o grupo seguinte.</span></span>
        </label>
      </div>

      <div class="space-y-1 shrink-0">
        <label class="text-[11px] font-medium text-slate-300">3. MÉTODO DE REFRIGERAÇÃO A USAR</label>
        <div class="grid grid-cols-4 gap-1 bg-slate-900 p-1 rounded-md border border-slate-700 text-[11px] text-center font-medium">
          <button type="button" onclick="setRefrig('int')" id="ref-int" class="py-1.5 rounded bg-blue-600 text-white">Interna</button>
          <button type="button" onclick="setRefrig('ext')" id="ref-ext" class="py-1.5 rounded text-slate-400">Externa</button>
          <button type="button" onclick="setRefrig('mql')" id="ref-mql" class="py-1.5 rounded text-slate-400">MQL</button>
          <button type="button" onclick="setRefrig('ar')" id="ref-ar" class="py-1.5 rounded text-slate-400">Ar</button>
        </div>
        <p id="aviso-refrig" class="text-[9px] text-amber-400 hidden">Nota: Esta ferramenta não permite refrigeração interna.</p>
      </div>

      <div class="grid grid-cols-2 gap-2 shrink-0">
        <div id="bloco-diametro-manual" class="space-y-1">
          <label class="text-[11px] font-medium text-slate-300">4. DIÂMETRO (Ø)</label>
          <div class="flex items-center gap-1">
            <button onclick="ajustarDiametro(-0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">-</button>
            <input type="number" id="diametro" value="12.00" step="0.1" min="0.5" max="30" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white" oninput="onDiametroPrincipalChange()">
            <button onclick="ajustarDiametro(0.5)" class="bg-slate-700 hover:bg-slate-600 px-2 py-1.5 rounded-md text-white font-bold text-xs">+</button>
          </div>
        </div>
        <div id="bloco-diametro-catalogo" class="space-y-1 hidden">
          <label class="text-[11px] font-medium text-emerald-400">4. DIÂMETRO (Ø) — d1</label>
          <div class="bg-slate-900/90 border border-emerald-700/60 rounded-md p-1.5 flex items-center justify-between px-2">
            <div id="diametro-catalogo-valor" class="text-sm font-bold text-emerald-300">Ø 12.00 mm</div>
            <button type="button" onclick="limparDiametroD1()" class="text-[10px] text-slate-400 hover:text-white underline">Livre</button>
          </div>
        </div>
        <div class="space-y-1">
          <label class="text-[11px] font-medium text-slate-300">5. PROFUNDIDADE/FURO (L)</label>
          <div class="flex items-center gap-1">
            <input type="number" id="profundidade" value="31.0" step="1" min="0.1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-sm font-bold text-white" oninput="atualizarCalculo()">
            <span class="text-[10px] text-slate-400">mm</span>
          </div>
        </div>
      </div>

      <div id="alerta-profundidade" class="bg-slate-900 px-2.5 py-1.5 rounded-md border border-slate-700 text-[10px] text-slate-200 flex justify-between items-center gap-2 shrink-0">
        <span id="texto-limite-prof">Profundidade a validar com catálogo</span>
        <span id="badge-limite-prof" class="font-bold text-amber-400 shrink-0">VALIDAR</span>
      </div>

      <div class="pro-only hidden space-y-2.5 shrink-0">
        <div class="grid grid-cols-2 gap-2 pt-1">
          <div><label class="text-[11px] font-medium text-slate-300 block">6. QTD. FUROS (LOTE)</label><input type="number" id="qtd-furos" value="50" min="1" max="100000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white" oninput="atualizarCalculo()"></div>
          <div><label class="text-[11px] font-medium text-slate-300 block">7. DENSIDADE (g/cm³)</label><input type="number" id="densidade" value="7.85" step="0.01" min="0.5" max="25" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white" oninput="atualizarCalculo()"></div>
        </div>
        <div class="bg-slate-900 p-2.5 rounded-md border border-slate-700/80 space-y-2">
          <label class="flex items-center gap-2 cursor-pointer text-[11px] text-slate-300">
            <input type="checkbox" id="pecking-check" class="rounded bg-slate-800 border-slate-600" onchange="togglePeckingInputs()">
            <span><strong>Ciclo com Quebra de Cavaco (Pecking)</strong></span>
          </label>
          <div id="pecking-options" class="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800 hidden">
            <div class="space-y-1">
              <div class="flex justify-between"><label class="text-[10px] text-slate-400">PASSO (Q)</label><select id="pecking-unidade" class="bg-slate-800 border border-slate-700 rounded px-1 text-[9px] text-cyan-400" onchange="onChangePeckingUnidade()"><option value="xd" selected>×D</option><option value="mm">mm</option></select></div>
              <input type="number" id="pecking-passo" value="3.0" step="0.5" min="0.1" max="500" class="w-full bg-slate-800 border border-slate-700 rounded p-1 text-center text-xs font-bold text-white" oninput="atualizarCalculo()">
              <span id="pecking-equiv" class="text-[9px] text-cyan-400 block text-center">Equiv: 36.0 mm (4 passos)</span>
            </div>
            <div class="space-y-1">
              <label class="text-[10px] text-slate-400 block">AVANÇO RETRAÇÃO (mm/min)</label>
              <input type="number" id="pecking-retensao" value="5000" step="500" min="500" max="20000" class="w-full bg-slate-800 border border-slate-700 rounded p-1 text-center text-xs font-bold text-white" oninput="atualizarCalculo()">
              <span class="text-[9px] text-slate-500 block text-center">Retorno alívio</span>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2 pt-1">
          <div><label class="text-[11px] font-medium text-slate-300 block">8. VALOR SUCATA (€/kg)</label><input type="number" id="preco-sucata" value="0.35" step="0.05" min="0" max="50" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white" oninput="atualizarCalculo()"></div>
          <div><label class="text-[11px] font-medium text-slate-300 block">9. CUSTO HORA MÁQUINA (€/h)</label><input type="number" id="custo-hora" value="50.00" step="5" min="1" max="500" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white" oninput="atualizarCalculo()"></div>
        </div>
      </div>

      <div class="space-y-2 pt-2 border-t border-slate-700 shrink-0">
        <div class="flex justify-between"><label class="text-[11px] font-medium text-amber-400 uppercase">Capacidade do Spindle (Opcional)</label><span class="text-[9px] text-slate-400">Deixar vazio se n/a</span></div>
        <div class="grid grid-cols-2 gap-2">
          <div class="space-y-1">
            <div class="flex justify-between"><label class="text-[10px] text-slate-300">POTÊNCIA MÁX.</label><select id="unidade-potencia" class="bg-slate-900 border border-slate-700 rounded px-1 text-[9px] text-cyan-400" onchange="atualizarCalculo()"><option value="kw">kW</option><option value="cv">CV</option></select></div>
            <input type="number" id="spindle-potencia" placeholder="Ex: 11.0" step="0.5" min="0" max="200" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white" oninput="atualizarCalculo()">
          </div>
          <div class="space-y-1"><label class="text-[10px] text-slate-300 block">BINÁRIO MÁX. (N·m)</label><input type="number" id="spindle-binario" placeholder="Ex: 70" step="1" min="0" max="2000" class="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-center text-xs font-bold text-white" oninput="atualizarCalculo()"></div>
        </div>
      </div>

      <div class="space-y-2 pt-1 border-t border-slate-700 shrink-0">
        <label class="text-[11px] font-medium text-blue-400 uppercase">Ajustes Percentuais (%)</label>
        <div class="space-y-1">
          <div class="flex justify-between text-[11px] text-slate-300"><span>Ajuste Vc (%):</span><span id="vc-pct-val" class="font-bold text-cyan-400">0%</span></div>
          <div class="flex items-center gap-1.5">
            <button onclick="ajustarPct('vc',-1)" class="bg-slate-700 px-2 py-0.5 rounded text-white text-[10px] font-bold">-1%</button>
            <input type="range" id="vc-slider" min="-50" max="50" value="0" class="w-full accent-blue-500" oninput="onSliderVc()">
            <button onclick="ajustarPct('vc',1)" class="bg-slate-700 px-2 py-0.5 rounded text-white text-[10px] font-bold">+1%</button>
            <button onclick="resetPct('vc')" class="bg-slate-900 border border-slate-600 text-slate-400 px-1.5 py-0.5 rounded text-[10px]">Reset</button>
          </div>
        </div>
        <div class="space-y-1">
          <div class="flex justify-between text-[11px] text-slate-300"><span>Ajuste Avanço f (%):</span><span id="f-pct-val" class="font-bold text-cyan-400">0%</span></div>
          <div class="flex items-center gap-1.5">
            <button onclick="ajustarPct('f',-1)" class="bg-slate-700 px-2 py-0.5 rounded text-white text-[10px] font-bold">-1%</button>
            <input type="range" id="f-slider" min="-50" max="50" value="0" class="w-full accent-blue-500" oninput="onSliderF()">
            <button onclick="ajustarPct('f',1)" class="bg-slate-700 px-2 py-0.5 rounded text-white text-[10px] font-bold">+1%</button>
            <button onclick="resetPct('f')" class="bg-slate-900 border border-slate-600 text-slate-400 px-1.5 py-0.5 rounded text-[10px]">Reset</button>
          </div>
        </div>
      </div>
    </div>

    <div class="lg:col-span-8 flex flex-col gap-2.5 min-h-0 overflow-y-auto">
      <div class="bg-slate-800/95 p-2.5 rounded-lg border border-slate-700 shrink-0">
        <div class="flex flex-wrap justify-between items-center gap-1 mb-2">
          <span class="text-[11px] font-semibold text-cyan-300 uppercase">Cotas da Ferramenta Selecionada</span>
          <span id="meta-referencia-ativa" class="text-[10px] text-slate-400 font-mono">Order: — | Spec: — | DIN 6535: —</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-center">
          <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80"><div class="text-[10px] text-slate-400">d1 (Ø corte)</div><div id="cota-d1" class="text-sm font-bold text-white mt-0.5">—</div></div>
          <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80"><div class="text-[10px] text-slate-400">d2 (Ø encab.)</div><div id="cota-d2" class="text-sm font-bold text-white mt-0.5">—</div></div>
          <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80"><div class="text-[10px] text-slate-400">l1 (Comp. total)</div><div id="cota-l1" class="text-sm font-bold text-white mt-0.5">—</div></div>
          <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80"><div class="text-[10px] text-slate-400">l2 (Navalha)</div><div id="cota-l2" class="text-sm font-bold text-white mt-0.5">—</div></div>
          <div class="bg-slate-900/90 p-2 rounded border border-emerald-700/60"><div class="text-[10px] text-emerald-300 font-semibold">l3 (Útil corte)</div><div id="cota-l3" class="text-sm font-bold text-emerald-300 mt-0.5">—</div></div>
          <div class="bg-slate-900/90 p-2 rounded border border-slate-700/80"><div class="text-[10px] text-slate-400">l4 (Comp. encab.)</div><div id="cota-l4" class="text-sm font-bold text-white mt-0.5">—</div></div>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-5 gap-2.5 shrink-0">
        <div id="card-f" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700">
          <div class="flex justify-between"><span class="text-[11px] text-slate-400">Avanço (f)</span><button type="button" onclick="toggleLock('f')" id="btn-lock-f" class="text-xs px-1 py-0.5 rounded bg-slate-900/80 border border-slate-700">🔒</button></div>
          <input type="number" id="input-f" value="0.0000" step="0.005" min="0.001" readonly oninput="atualizarCalculo()" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
          <div class="flex justify-between mt-0.5"><span class="text-[9px] text-blue-400">mm/rot</span><span id="status-f" class="text-[9px] text-slate-500">Auto</span></div>
        </div>
        <div id="card-vc" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700">
          <div class="flex justify-between"><span class="text-[11px] text-slate-400">Vc</span><button type="button" onclick="toggleLock('vc')" id="btn-lock-vc" class="text-xs px-1 py-0.5 rounded bg-slate-900/80 border border-slate-700">🔒</button></div>
          <input type="number" id="input-vc" value="0" step="1" min="1" readonly oninput="atualizarCalculo()" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
          <div class="flex justify-between mt-0.5"><span class="text-[9px] text-slate-400">m/min</span><span id="status-vc" class="text-[9px] text-slate-500">Auto</span></div>
        </div>
        <div id="card-rpm-max" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700">
          <div class="flex justify-between"><span class="text-[11px] text-slate-400">RPM Máx. Máquina</span><button type="button" onclick="toggleLock('rpm-max')" id="btn-lock-rpm-max" class="text-xs px-1 py-0.5 rounded bg-slate-900/80 border border-slate-700">🔒</button></div>
          <input type="number" id="input-rpm-max" value="8000" step="100" min="100" max="60000" readonly oninput="atualizarCalculo()" class="w-full bg-transparent text-xl font-bold text-white mt-0.5 focus:outline-none rounded px-1 -ml-1">
          <div class="flex justify-between mt-0.5"><span class="text-[9px] text-slate-400">rpm</span><span id="status-rpm-max" class="text-[9px] text-slate-500">Inativo</span></div>
        </div>
        <div class="bg-slate-800 p-2.5 rounded-lg border border-slate-700"><span class="text-[11px] text-slate-400">Rotações (Spindle)</span><div class="text-xl font-bold text-white mt-0.5" id="res-n">0</div><span class="text-[9px] text-slate-400">rpm</span></div>
        <div class="bg-slate-800 p-2.5 rounded-lg border border-slate-700"><span class="text-[11px] text-slate-400">Avanço Trabalho</span><div class="text-xl font-bold text-white mt-0.5" id="res-vf">0</div><span class="text-[9px] text-slate-400">mm/min</span></div>
      </div>

      <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 shrink-0">
        <div class="flex justify-between items-center mb-1">
          <span class="text-[11px] font-semibold text-slate-300 uppercase">🎛️ Monitor Gráfico de Carga do Spindle</span>
          <span class="text-[10px] text-slate-400">Verde (&lt;70%) | Amarela (70-90%) | Vermelha (&gt;90% Stall)</span>
        </div>
        <div id="alerta-sobrecarga-spindle" class="hidden mb-2 bg-red-950/80 border border-red-500/80 text-red-200 px-3 py-2 rounded-md text-xs flex items-center justify-between gap-2">
          <div class="flex items-center gap-2"><span>⚠️</span><span id="texto-sobrecarga-spindle" class="font-semibold"></span></div>
          <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-red-600 text-white shrink-0">SOBRECARGA</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1" id="gauges-container"></div>
      </div>

      <div class="pro-only hidden grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
        <div class="bg-gradient-to-r from-blue-900/40 to-slate-800 p-2.5 rounded-lg border border-blue-700/50 flex justify-between items-center">
          <div><span class="text-[11px] text-blue-300 font-semibold uppercase">⏱️ Tempo de Ciclo (Lote / Unit.)</span><div class="text-lg font-extrabold text-white mt-0.5" id="res-tempo-total">0.0 min <span class="text-xs font-normal text-slate-300" id="res-tempo-unit">(0.0 seg/furo)</span></div></div>
          <div class="text-right"><span class="text-[10px] text-slate-400">Metragem Linear</span><div class="text-xs font-mono font-bold text-cyan-400" id="res-metragem">0.0 metros</div></div>
        </div>
        <div class="bg-gradient-to-r from-emerald-900/40 to-slate-800 p-2.5 rounded-lg border border-emerald-700/50 flex justify-between items-center">
          <div><span class="text-[11px] text-emerald-300 font-semibold uppercase">📦 Volume de Material (Lote)</span><div class="text-lg font-extrabold text-white mt-0.5" id="res-volume-total">0.0 cm³</div></div>
          <div class="text-right"><span class="text-[10px] text-slate-400">Taxa Remoção</span><div class="text-xs font-mono font-bold text-emerald-400" id="res-taxa">-- cm³/min</div></div>
        </div>
      </div>

      <div class="pro-only hidden grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
        <div class="bg-gradient-to-r from-cyan-900/40 to-slate-800 p-2.5 rounded-lg border border-cyan-700/50 flex justify-between items-center">
          <div><span class="text-[11px] text-cyan-300 font-semibold uppercase">⚖️ Peso Limalha (Lote)</span><div class="text-xl font-extrabold text-white mt-0.5" id="res-peso">0.000 kg</div></div>
          <div class="text-right"><span class="text-[10px] text-slate-400">Massa / Furo</span><div class="text-xs font-mono font-bold text-cyan-400" id="res-peso-g">0.00 g</div></div>
        </div>
        <div class="bg-gradient-to-r from-teal-900/40 to-slate-800 p-2.5 rounded-lg border border-teal-700/50 flex justify-between items-center">
          <div><span class="text-[11px] text-teal-300 font-semibold uppercase">💶 Valor Sucata (Lote)</span><div class="text-xl font-extrabold text-white mt-0.5" id="res-sucata-val">0.00 €</div></div>
          <div class="text-right"><span class="text-[10px] text-slate-400">Retorno / Furo</span><div class="text-xs font-mono font-bold text-teal-400" id="res-sucata-furo">0.00 € / furo</div></div>
        </div>
      </div>

      <div id="grid-esforcos-custos" class="grid grid-cols-1 md:grid-cols-2 gap-2.5 shrink-0">
        <div class="pro-only hidden bg-gradient-to-r from-indigo-900/40 to-slate-800 p-2.5 rounded-lg border border-indigo-700/50 flex justify-between items-center">
          <div><span class="text-[11px] text-indigo-300 font-semibold uppercase">💰 Custo Maquinação</span><div class="text-base font-extrabold text-white mt-0.5" id="res-custo-total">0.00 € <span class="text-[10px] font-normal text-slate-300" id="res-custo-furo">(0.00 €/furo)</span></div></div>
          <div class="text-right"><span class="text-[10px] text-slate-400">Custo Hora</span><div class="text-xs font-mono font-bold text-indigo-400" id="res-custo-hora-ref">50.00 €/h</div></div>
        </div>
        <div class="bg-gradient-to-r from-amber-900/40 to-slate-800 p-2.5 rounded-lg border border-amber-700/50 flex justify-between items-center">
          <div><span class="text-[11px] text-amber-300 font-semibold uppercase">⚡ Força Axial (Ff)</span><div class="text-xl font-extrabold text-white mt-0.5" id="res-forca">0 N</div></div>
          <div class="text-right"><span class="text-[10px] text-slate-400">Esforço em Z</span><div class="text-xs font-mono font-bold text-amber-400" id="res-forca-kgf">0 kgf</div></div>
        </div>
        <div class="bg-gradient-to-r from-purple-900/40 to-slate-800 p-2.5 rounded-lg border border-purple-700/50 flex justify-between items-center">
          <div><span class="text-[11px] text-purple-300 font-semibold uppercase">🔄 Binário de Corte (Mc)</span><div class="text-xl font-extrabold text-white mt-0.5" id="res-binario-card">0.0 N·m</div></div>
          <div class="text-right"><span class="text-[10px] text-slate-400">Torque Ferramenta</span><div class="text-xs font-mono font-bold text-purple-400">Estimado por kc</div></div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 flex-1 min-h-[200px]">
        <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 flex flex-col min-h-0">
          <div class="flex justify-between mb-1.5 shrink-0"><h3 class="text-[11px] font-semibold text-slate-400 uppercase">Tabela de Referência</h3><span class="text-[9px] font-bold text-emerald-400" id="val-estado">Dentro da gama</span></div>
          <div class="overflow-y-auto flex-1 min-h-0 max-h-[175px]">
            <table class="w-full text-left text-xs">
              <thead class="sticky top-0 bg-slate-800"><tr class="border-b border-slate-700 text-slate-400"><th class="pb-1">Ø (mm)</th><th class="pb-1">f Cat.</th><th class="pb-1">RPM (n)</th><th class="pb-1">Avanço (v_f)</th></tr></thead>
              <tbody id="tabela-ref" class="divide-y divide-slate-700/50"></tbody>
            </table>
          </div>
        </div>
        <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 flex flex-col justify-between min-h-0">
          <div class="flex justify-between shrink-0"><h3 class="text-[11px] font-semibold text-slate-400 uppercase">Avanço (f) vs. Ø</h3><span class="text-[9px] text-slate-400" id="badge-metodo">Interpolação Linear</span></div>
          <div class="w-full flex-1 bg-slate-900 rounded-md border border-slate-700 p-1 flex items-center justify-center my-1.5 min-h-[115px]"><svg id="svg-grafico" class="w-full h-full max-h-36" viewBox="0 0 400 180"></svg></div>
          <div class="flex justify-center gap-4 text-[9px] text-slate-400 shrink-0">
            <span><span class="w-2 h-2 rounded-full bg-blue-500 inline-block"></span> Catálogo</span>
            <span><span class="w-2 h-2 rounded-full bg-orange-500 inline-block"></span> Calculado</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modais -->
  <div id="modal-aviso-inicial" class="fixed inset-0 bg-black/85 flex items-center justify-center z-50 p-3">
    <div class="bg-slate-800 border border-amber-500/70 rounded-lg p-5 w-full max-w-md shadow-2xl space-y-4">
      <h3 class="text-sm font-bold text-amber-300 uppercase border-b border-slate-700 pb-2">⚠️ Aviso Técnico Importante</h3>
      <p class="text-xs text-slate-200 bg-slate-900 p-3 rounded border border-slate-700">Atenção: todos os parâmetros de corte são teóricos e poderão sofrer alterações no momento da usabilidade, consoante a máquina, aperto da peça, aperto da ferramenta e material a cortar.</p>
      <div class="flex justify-end"><button onclick="hide('modal-aviso-inicial')" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-md text-xs font-bold text-white">Compreendi, Continuar</button></div>
    </div>
  </div>

  <div id="modal-password-pro" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 hidden p-3">
    <div class="bg-slate-800 border border-purple-500/70 rounded-lg p-5 w-full max-w-sm shadow-2xl space-y-3.5">
      <div class="flex justify-between border-b border-slate-700 pb-2"><h3 class="text-sm font-bold text-white">🔓 Acesso ao Nível Pro</h3><button onclick="hide('modal-password-pro')" class="text-slate-400 hover:text-white text-sm">✕</button></div>
      <input type="password" id="input-pro-password" placeholder="Password Nível Pro" class="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-xs text-white" onkeydown="if(event.key==='Enter') validarPasswordPro()">
      <p id="erro-pro-password" class="text-[11px] text-rose-400 hidden"></p>
      <div class="flex justify-end gap-2"><button onclick="hide('modal-password-pro')" class="bg-slate-700 px-3 py-1.5 rounded-md text-xs text-white">Cancelar</button><button onclick="validarPasswordPro()" class="bg-purple-600 hover:bg-purple-500 px-3.5 py-1.5 rounded-md text-xs font-bold text-white">Desbloquear Pro</button></div>
    </div>
  </div>

  <div id="modal-pdf-parametros" class="fixed inset-0 bg-black/75 flex items-center justify-center z-50 hidden p-3">
    <div class="bg-slate-800 border border-cyan-600/70 rounded-lg p-5 w-full max-w-md shadow-2xl space-y-4">
      <div class="flex justify-between border-b border-slate-700 pb-2.5"><h3 class="text-sm font-bold text-white">📋 Gerar PDF com parâmetros de corte</h3><button onclick="hide('modal-pdf-parametros')" class="text-slate-400 hover:text-white text-sm">✕</button></div>
      <div class="space-y-2">
        <label class="flex items-start gap-2.5 bg-slate-900 p-3 rounded border border-slate-700 cursor-pointer"><input type="radio" name="escopo-pdf-parametros" value="selecionados" checked class="mt-0.5 accent-cyan-500"><div><strong class="text-xs text-white block">Só os parâmetros selecionados</strong><span class="text-[10px] text-slate-400">Material ativo, Ø, VC, F, RPM (n) e Avanço (vf).</span></div></label>
        <label class="flex items-start gap-2.5 bg-slate-900 p-3 rounded border border-slate-700 cursor-pointer"><input type="radio" name="escopo-pdf-parametros" value="todos" class="mt-0.5 accent-cyan-500"><div><strong class="text-xs text-white block">Todos os parâmetros suportados pela ferramenta</strong><span class="text-[10px] text-slate-400">Todos os grupos suportados para o Ø e refrigeração atuais.</span></div></label>
      </div>
      <p id="aviso-pdf-parametros" class="text-[11px] text-amber-300 hidden"></p>
      <div class="flex justify-end gap-2"><button onclick="hide('modal-pdf-parametros')" class="bg-slate-700 px-3 py-1.5 rounded-md text-xs text-white">Cancelar</button><button onclick="gerarPdfParametrosCorte()" class="bg-cyan-600 hover:bg-cyan-500 px-4 py-1.5 rounded-md text-xs font-bold text-white">📥 Gerar PDF</button></div>
    </div>
  </div>

  <div id="modal-export" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 hidden">
    <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 w-96 shadow-2xl space-y-4">
      <div class="flex justify-between"><h3 class="text-sm font-bold text-white">📄 Tipo de Relatório PDF</h3><button onclick="hide('modal-export')" class="text-slate-400 hover:text-white text-sm">✕</button></div>
      <div class="space-y-2">
        <label class="flex items-start gap-2 bg-slate-900 p-2.5 rounded border border-slate-700 cursor-pointer"><input type="radio" name="tipo-relatorio" id="radio-pdf-resumido" value="resumido" checked class="mt-0.5 accent-blue-500"><div><strong class="text-xs text-white block">Ficha Técnica (Básico)</strong><span class="text-[10px] text-slate-400">Ferramenta, material, Vc, RPM, f, vf e spindle.</span></div></label>
        <label class="pro-only hidden flex items-start gap-2 bg-slate-900 p-2.5 rounded border border-slate-700 cursor-pointer"><input type="radio" name="tipo-relatorio" id="radio-pdf-completo" value="completo" class="mt-0.5 accent-blue-500"><div><strong class="text-xs text-white block">Proposta Técnico-Comercial Completa (Pro)</strong><span class="text-[10px] text-slate-400">Lote, tempos, custos, limalha, sucata e comparativo.</span></div></label>
      </div>
      <div class="flex justify-end gap-2"><button onclick="hide('modal-export')" class="bg-slate-700 px-3 py-1.5 rounded-md text-xs text-white">Cancelar</button><button onclick="gerarPDF()" class="bg-blue-600 hover:bg-blue-500 px-3 py-1.5 rounded-md text-xs font-medium text-white">📥 Gerar PDF</button></div>
    </div>
  </div>

  <div id="modal-comparacao" class="fixed inset-0 bg-black/75 flex items-center justify-center z-50 hidden p-3">
    <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 w-full max-w-3xl shadow-2xl space-y-3.5 max-h-[92vh] overflow-y-auto">
      <div class="flex justify-between border-b border-slate-700 pb-2.5"><h3 class="text-sm font-bold text-white">⚖️ Comparação Técnico-Comercial</h3><button onclick="hide('modal-comparacao')" class="text-slate-400 hover:text-white text-sm">✕</button></div>
      <div class="grid grid-cols-1 md:grid-cols-12 gap-3 bg-slate-900/90 p-3 rounded-lg border border-slate-700 items-end">
        <div class="md:col-span-5 space-y-1"><label class="text-[10px] font-semibold text-emerald-400 uppercase block">Família / Cliente</label><select id="comp-ferramenta" class="w-full bg-slate-800 border border-slate-700 rounded-md p-1.5 text-xs text-white" onchange="onChangeFonteComparacao()"></select></div>
        <div id="comp-bloco-variante" class="md:col-span-2 space-y-1"><label class="text-[10px] font-semibold text-cyan-400 uppercase block">×D</label><select id="comp-variante" class="w-full bg-slate-800 border border-slate-700 rounded-md p-1.5 text-xs font-bold text-cyan-300" onchange="atualizarComparacao()"></select></div>
        <div class="md:col-span-5 space-y-1"><label class="text-[10px] font-semibold text-amber-300 uppercase block">Condição</label><button type="button" id="btn-corte-interrompido" onclick="toggleCorteInterrompido()" class="w-full py-1.5 px-3 rounded-md text-xs font-semibold border bg-slate-800 border-slate-600 text-slate-300"><span id="icone-corte-interrompido">○</span> Corte Interrompido (-30%)</button></div>
      </div>
      <div id="comp-bloco-cliente" class="bg-slate-900/90 p-3 rounded-lg border border-amber-700/50 grid grid-cols-1 sm:grid-cols-3 gap-3 hidden">
        <div><label class="text-[10px] text-amber-300 uppercase block">Designação</label><input type="text" id="comp-cliente-nome" value="Ferramenta do Cliente" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1.5 text-xs text-white" oninput="atualizarComparacao()"></div>
        <div><label class="text-[10px] text-amber-300 uppercase block">Vc Cliente (m/min)</label><input type="number" id="comp-cliente-vc" value="70" min="1" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1.5 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
        <div><label class="text-[10px] text-amber-300 uppercase block">f Cliente (mm/rot)</label><input type="number" id="comp-cliente-f" value="0.0200" step="0.005" min="0.001" class="w-full bg-slate-800 border border-slate-700 rounded-md px-2 py-1.5 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-700/80">
        <div class="space-y-2 md:border-r border-slate-800 md:pr-3">
          <span class="text-[10px] font-bold text-blue-400 uppercase block">MAPAL Atual</span>
          <div class="grid grid-cols-2 gap-2">
            <div><label class="text-[10px] text-slate-400 block">Preço (€)</label><input type="number" id="comp-preco-atual" value="680" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
            <div><div class="flex justify-between"><label class="text-[10px] text-slate-400">Vida</label><select id="comp-vida-unid-atual" class="bg-slate-800 text-[9px] text-cyan-400" onchange="atualizarComparacao()"><option value="furos">furos</option><option value="metros">metros</option></select></div><input type="number" id="comp-vida-atual" value="90" min="1" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
            <div><label class="text-[10px] text-slate-400 block">Reafiações</label><input type="number" id="comp-afi-qtd-atual" value="0" min="0" max="30" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-cyan-300 text-center" oninput="atualizarComparacao()"></div>
            <div><label class="text-[10px] text-slate-400 block">Custo / Afiação (€)</label><input type="number" id="comp-afi-custo-atual" value="25" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
          </div>
        </div>
        <div class="space-y-2">
          <span class="text-[10px] font-bold text-emerald-400 uppercase block">Comparada / Cliente</span>
          <div class="grid grid-cols-2 gap-2">
            <div><label class="text-[10px] text-slate-400 block">Preço (€)</label><input type="number" id="comp-preco-alvo" value="80" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
            <div><div class="flex justify-between"><label class="text-[10px] text-slate-400">Vida</label><select id="comp-vida-unid-alvo" class="bg-slate-800 text-[9px] text-cyan-400" onchange="atualizarComparacao()"><option value="furos">furos</option><option value="metros">metros</option></select></div><input type="number" id="comp-vida-alvo" value="250" min="1" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
            <div><label class="text-[10px] text-slate-400 block">Reafiações</label><input type="number" id="comp-afi-qtd-alvo" value="0" min="0" max="30" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-cyan-300 text-center" oninput="atualizarComparacao()"></div>
            <div><label class="text-[10px] text-slate-400 block">Custo / Afiação (€)</label><input type="number" id="comp-afi-custo-alvo" value="15" min="0" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs font-bold text-white text-center" oninput="atualizarComparacao()"></div>
          </div>
        </div>
      </div>
      <p id="comp-aviso-grupo" class="text-[11px] text-amber-300 bg-amber-950/40 border border-amber-700/50 rounded-md px-3 py-2 hidden"></p>
      <div class="flex flex-wrap justify-between items-center gap-2 pt-2 border-t border-slate-700">
        <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" id="comp-incluir-pdf" checked><span>Incluir no PDF</span></label>
        <div class="flex gap-2">
          <button onclick="hide('modal-comparacao')" class="bg-slate-700 px-3 py-2 rounded-md text-xs text-white">Fechar</button>
          <button id="btn-usar-comparada" onclick="aplicarFerramentaComparada()" class="bg-slate-600 hover:bg-slate-500 px-3 py-2 rounded-md text-xs font-semibold text-white">Usar Ferramenta</button>
          <button onclick="abrirResultadoComparacao()" class="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-md text-xs font-bold text-white">📊 Ver Resultado</button>
        </div>
      </div>
    </div>
  </div>

  <div id="modal-resultado-comparacao" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 hidden p-3">
    <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 w-full max-w-4xl shadow-2xl space-y-3.5 max-h-[92vh] overflow-y-auto">
      <div class="flex justify-between border-b border-slate-700 pb-2.5"><h3 class="text-sm font-bold text-white">📊 Resultado do Comparativo</h3><button onclick="hide('modal-resultado-comparacao')" class="text-slate-400 hover:text-white text-sm">✕</button></div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-900/90 p-3 rounded-lg border border-slate-700">
        <div><span class="text-[10px] font-semibold text-emerald-400 uppercase block">Capacidade &amp; Tempo</span><p id="comp-capacidade-texto" class="text-xs text-white mt-1"></p></div>
        <div><span class="text-[10px] font-semibold text-amber-300 uppercase block">Ponto de Equilíbrio</span><p id="comp-breakeven-texto" class="text-xs text-white mt-1"></p></div>
      </div>
      <div class="overflow-x-auto bg-slate-900 rounded-lg border border-slate-700">
        <table class="w-full text-left text-xs">
          <thead><tr class="border-b border-slate-700 text-slate-400"><th class="py-2 px-3">Indicador</th><th class="py-2 px-3 text-blue-400" id="comp-th-atual">Atual</th><th class="py-2 px-3 text-emerald-400" id="comp-th-alvo">Comparada</th><th class="py-2 px-3 text-amber-300">Diferença</th></tr></thead>
          <tbody id="comp-tabela-corpo" class="divide-y divide-slate-800"></tbody>
        </table>
      </div>
      <div class="flex justify-end"><button onclick="hide('modal-resultado-comparacao')" class="bg-slate-700 px-4 py-1.5 rounded-md text-xs text-white">Fechar</button></div>
    </div>
  </div>

  <footer class="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/80 flex flex-col sm:flex-row justify-between items-center gap-2 text-[11px] text-slate-400 shrink-0">
    <div>Created by <span class="text-white font-semibold">Bruno Pinto</span></div>
    <div class="flex items-center gap-4">
      <a href="mailto:bruno.pinto@alamo-ferramentas.com" class="hover:text-blue-400">✉️ bruno.pinto@alamo-ferramentas.com</a>
      <a href="tel:+351936959415" class="hover:text-blue-400">📱 +351 936 959 415</a>
    </div>
  </footer>
</div>

<script>
const PRO_PASSWORD = __PRO_PW__;
const FAMILIAS_JSON = __FAM__;
const REFERENCIAS_JSON = __REF__;
const PARAMETROS_JSON = __PAR__;
const GRUPOS_MMG_JSON = __MMG__;

const ISO_PALETTE = {
  P:{nome:'Aços (P)',cor:'#3b82f6',bg:'#2563eb',fg:'#fff'}, M:{nome:'Inox (M)',cor:'#facc15',bg:'#ca8a04',fg:'#0f172a'},
  K:{nome:'Fundições (K)',cor:'#ef4444',bg:'#dc2626',fg:'#fff'}, N:{nome:'Não Ferrosos (N)',cor:'#22c55e',bg:'#16a34a',fg:'#0f172a'},
  S:{nome:'Superligas (S)',cor:'#f97316',bg:'#ea580c',fg:'#fff'}, H:{nome:'Endurecidos (H)',cor:'#a855f7',bg:'#9333ea',fg:'#fff'},
  C:{nome:'Compósitos (C)',cor:'#06b6d4',bg:'#0891b2',fg:'#0f172a'}, X:{nome:'Misto (X*)',cor:'#ec4899',bg:'#db2777',fg:'#fff'},
  Y:{nome:'Sinterizados (Y*)',cor:'#94a3b8',bg:'#64748b',fg:'#0f172a'}
};
const PROP_GRUPO = {P:{kc:2200,d:7.85},M:{kc:2800,d:7.9},K:{kc:1800,d:7.2},N:{kc:800,d:2.7},S:{kc:3400,d:4.5},H:{kc:3200,d:7.85},C:{kc:1500,d:1.6},X:{kc:2000,d:5.5},Y:{kc:2400,d:7.5}};

let isProMode = false, referenciaAtivaObj = null, linhaAtivaInterna = '';
let refrigAtual = 'int', vcPct = 0, fPct = 0;
let locks = { f: false, vc: false, 'rpm-max': false };
let corteInterrompidoAtivo = false, mmgGrupoSel = null, mmgSubSel = null, mmgManual = false;

const dados = {}, mapaFam = {}, gruposMmgMap = {}, gruposMmgOrdem = [], mmgMeta = {}, mmgSubsIso = {};
const hide = id => document.getElementById(id)?.classList.add('hidden');
const show = id => document.getElementById(id)?.classList.remove('hidden');
const normMmg = c => String(c||'').trim().toUpperCase();
const chaveMmg = c => normMmg(c).replace(/^([A-Z]+\d+)[.-](\d+)$/,'$1.$2');
const numSafe = (v, fb=0) => { const n = parseFloat(String(v??'').replace(',','.').trim()); return isNaN(n)?fb:n; };
const normGama = g => { const s = String(g||'').toLowerCase(); return ['expert','performance','basic'].find(x=>s.includes(x)) || s.trim(); };
const fmtPt = (v, d=2) => (v===null||v===undefined||isNaN(+v)) ? '—' : (+v).toFixed(d).replace('.',',');

(function initGauges(){
  const arc = `<div class="bg-slate-900/90 p-2.5 rounded-md border border-slate-700/80 flex flex-col items-center">
    <span class="text-[10px] font-semibold text-slate-300 uppercase mb-1">__TITLE__</span>
    <div class="relative w-48 h-24 overflow-hidden flex justify-center items-end">
      <svg class="w-48 h-24 overflow-visible" viewBox="0 0 200 100">
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#334155" stroke-width="16" stroke-linecap="round"/>
        <path d="M 20 100 A 80 80 0 0 1 132.5 28.5" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round"/>
        <path d="M 132.5 28.5 A 80 80 0 0 1 165.4 53.2" fill="none" stroke="#f59e0b" stroke-width="16"/>
        <path d="M 165.4 53.2 A 80 80 0 0 1 180 100" fill="none" stroke="#ef4444" stroke-width="16" stroke-linecap="round"/>
        <g id="__NEEDLE__" class="gauge-needle"><line x1="100" y1="100" x2="100" y2="26" stroke="#fff" stroke-width="3" stroke-linecap="round"/><circle cx="100" cy="100" r="5" fill="#f8fafc"/></g>
      </svg>
    </div>
    <div class="flex justify-between w-full px-2 mt-1 items-center"><span class="text-xs font-bold text-white" id="__VAL__">0.0</span><span id="__BADGE__" class="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">Standby</span></div>
  </div>`;
  document.getElementById('gauges-container').innerHTML =
    arc.replace('__TITLE__','Potência de Corte Requerida').replace('__NEEDLE__','needle-potencia').replace('__VAL__','val-gauge-pot').replace('__BADGE__','badge-gauge-pot') +
    arc.replace('__TITLE__','Binário de Corte Requerido (Mc)').replace('__NEEDLE__','needle-binario').replace('__VAL__','val-gauge-bin').replace('__BADGE__','badge-gauge-bin');
})();

function resolverGrupo(tool, key) {
  if (!tool?.grupos || !key) return null;
  if (tool.grupos[normMmg(key)]) return tool.grupos[normMmg(key)];
  const tk = chaveMmg(key);
  for (const k of Object.keys(tool.grupos)) if (chaveMmg(k) === tk) return tool.grupos[k];
  return null;
}

function carregarDados() {
  (GRUPOS_MMG_JSON||[]).forEach(it => {
    const cod = normMmg(it?.codigo || it?.Grupo || it?.grupo);
    if (!cod) return;
    const iso = (it.iso||'').replace('*','').trim().toUpperCase() || cod[0];
    const sub = normMmg(it.subgrupo) || (cod.match(/^([A-Z]+\d+)/)?.[1] || '');
    gruposMmgMap[cod] = String(it.label || it.descricao || cod).trim();
    if (!gruposMmgOrdem.includes(cod)) gruposMmgOrdem.push(cod);
    mmgMeta[cod] = { codigo:cod, label:gruposMmgMap[cod], iso, subgrupo:sub, freq:String(it.materiais_frequentes||'').trim(), dureza:String(it.dureza||'').trim() };
    if (iso && sub) { mmgSubsIso[iso] = mmgSubsIso[iso] || []; if (!mmgSubsIso[iso].includes(sub)) mmgSubsIso[iso].push(sub); }
  });

  const ensureTool = (famRaw, meta={}) => {
    const k = famRaw.trim().toLowerCase();
    if (!dados[k]) {
      dados[k] = { familiaCode:famRaw.trim(), nomeProduto:meta.nomeProduto||'', linha:meta.gama||'expert', categoria:meta.categoria||'', temRefrigInt:true, variantes:{}, diametros:[], gruposList:[], gruposNames:{}, grupos:{}, _ref:new Set() };
    }
    const t = dados[k];
    if (meta.nomeProduto) t.nomeProduto = meta.nomeProduto;
    if (meta.gama) t.linha = meta.gama;
    if (meta.categoria) t.categoria = meta.categoria;
    t.nome = (t.familiaCode && t.nomeProduto) ? `${t.familiaCode} — ${t.nomeProduto}` : (t.familiaCode || t.nomeProduto);
    return t;
  };

  (FAMILIAS_JSON||[]).forEach(f => {
    const fam = String(f?.familia || f?.Familia || '').trim();
    if (!fam) return;
    const m = { nomeProduto:String(f.nome_produto||f['Nome do produto']||'').trim(), gama:normGama(f.gama||f.Gama), categoria:String(f.categoria||f.Categoria||'').trim() };
    mapaFam[fam.toLowerCase()] = m;
    ensureTool(fam, m);
  });

  (REFERENCIAS_JSON||[]).forEach(it => {
    const fam = String(it?.familia || it?.Familia || '').trim();
    if (!fam) return;
    const fm = mapaFam[fam.toLowerCase()] || {};
    const t = ensureTool(fam, { nomeProduto:String(it.nome_produto||fm.nomeProduto||'').trim(), gama:normGama(it.gama||it.linha||fm.gama), categoria:String(it.categoria||it.operacao||fm.categoria||'').trim() });
    const v = String(it.variante||'').trim();
    if (v && !t.variantes[v]) t.variantes[v] = { ratio: parseFloat(v.match(/(\d+(?:\.\d+)?)\s*x\s*d/i)?.[1] || 5) };
    const d1 = parseFloat(it.d1);
    if (!isNaN(d1) && d1 > 0 && !t.diametros.some(x => Math.abs(x - d1) < 1e-3)) { t.diametros.push(d1); t.diametros.sort((a,b)=>a-b); }
    const rc = normRefrig(it);
    if (rc) t._ref.add(rc);
  });

  (PARAMETROS_JSON||[]).forEach(r => {
    if (!r || r.suportado === false) return;
    const fam = String(r.familia || r.Familia || '').trim();
    const grp = normMmg(r.grupo || r.Grupo || r.mmg || r.MMG);
    if (!fam || !grp) return;
    const fm = mapaFam[fam.toLowerCase()] || {};
    const t = ensureTool(fam, { nomeProduto:String(r.nome_produto||fm.nomeProduto||'').trim(), gama:normGama(r.gama||r.linha||fm.gama), categoria:String(r.categoria||r.operacao||fm.categoria||'').trim() });
    if (!Object.keys(t.variantes).length) t.variantes = { '5xD': { ratio: 5 } };
    if (!t.diametros.length) t.diametros = [3,4.5,6.5,9.5,14,20];
    const vcS = (r.vc && typeof r.vc === 'object') ? r.vc : {};
    const vcObj = { int:numSafe(r.Vc_Int??r.vc_int??vcS.interna??vcS.int??r.vc,0), ext:numSafe(r.Vc_Ext??r.vc_ext??vcS.externa??vcS.ext??r.vc,0), mql:numSafe(r.Vc_MQL??r.vc_mql??vcS.mql??vcS.vc,0), ar:numSafe(r.Vc_Ar??r.vc_ar??vcS.ar,0) };
    const mapF = r.avancos_f || r.f_by_d;
    let fArr = Array.isArray(r.f) && r.f.length ? r.f.map(x=>numSafe(x,0.05)) : (mapF && typeof mapF==='object' ? t.diametros.map(d => { const mk = Object.keys(mapF).find(k=>Math.abs(parseFloat(k.replace(',','.'))-d)<0.02); return mk!==undefined ? numSafe(mapF[mk],0.05) : 0.05; }) : t.diametros.map(()=>numSafe(r.f,0.05)));
    t.grupos[grp] = { vc: vcObj, f: fArr };
    if (!t.gruposList.includes(grp)) t.gruposList.push(grp);
    t.gruposNames[grp] = gruposMmgMap[grp] || grp;
  });

  Object.values(dados).forEach(t => { if (t._ref.size && !t._ref.has('int')) t.temRefrigInt = false; });
  renderBotoesMmg([]);
}

const normRefrig = it => { const s = String(it?.refrigeracao||it?.refrig||'').toLowerCase(); return s.includes('int')||s==='ik'||s==='ic'?'int':s.includes('mql')||s.includes('mms')?'mql':s==='ar'||s.includes('air')?'ar':s.includes('ext')?'ext':s.trim(); };
const fmtRefrig = c => ({int:'Interna (INT)',ext:'Externa (EXT)',mql:'MQL',ar:'Ar'})[c] || c.toUpperCase();
const extrairDIN = it => {
  if (!it) return '';
  if (['HA','HB','HE'].includes(String(it.encabadouro||'').toUpperCase())) return String(it.encabadouro).toUpperCase();
  return [it.specification,it.designacao,it.nome,it.order_no].join(' ').toUpperCase().match(/(?:^|[^A-Z0-9])(HA|HB|HE)(?:[^A-Z0-9]|$|\d)/)?.[1] || '';
};
const getGamaIt = it => normGama(it?.gama||it?.linha) || mapaFam[String(it?.familia||'').toLowerCase()]?.gama || dados[String(it?.familia||'').toLowerCase()]?.linha || '';
const getCatIt = it => String(it?.categoria||it?.operacao||'').trim() || mapaFam[String(it?.familia||'').toLowerCase()]?.categoria || dados[String(it?.familia||'').toLowerCase()]?.categoria || '';
const fmtGama = g => ({expert:'Expert Line',performance:'Performance Line',basic:'Basic Line'})[g] || g || '—';

function renderBotoesMmg(dispList = []) {
  const contG = document.getElementById('mmg-botoes-grupo'), pSub = document.getElementById('mmg-painel-subgrupo'), cSub = document.getElementById('mmg-botoes-subgrupo');
  const pCod = document.getElementById('mmg-painel-codigo'), cCod = document.getElementById('mmg-botoes-codigo'), selG = document.getElementById('grupo');
  const dispNorm = dispList.map(normMmg).filter(Boolean);
  const mapDisp = {}; dispNorm.forEach(g => mapDisp[chaveMmg(g)] = g);
  const isosDisp = new Set(), subsDisp = new Set();
  dispNorm.forEach(g => { const iso=(mmgMeta[g]?.iso||g[0]).toUpperCase(), sub=normMmg(mmgMeta[g]?.subgrupo||g.match(/^([A-Z]+\d+)/)?.[1]||''); if(iso)isosDisp.add(iso); if(sub)subsDisp.add(sub); });
  const fil = dispNorm.length > 0 && isosDisp.size > 0;

  contG.innerHTML = '';
  ['P','M','K','N','S','H','C','X','Y'].forEach(iso => {
    const pal = ISO_PALETTE[iso], ativo = mmgGrupoSel === iso, btn = document.createElement('button');
    btn.type='button'; btn.className='iso-btn'; btn.disabled = fil && !isosDisp.has(iso); btn.title = pal.nome; btn.innerText = iso;
    btn.style.cssText = `color:${ativo?pal.fg:pal.cor};background:${ativo?pal.bg:'#0f172a'};border-color:${pal.cor};${ativo?`box-shadow:0 0 0 1.5px ${pal.cor}`:''}`;
    btn.onclick = () => { mmgGrupoSel = mmgGrupoSel===iso ? null : iso; mmgSubSel = null; mmgManual = Boolean(mmgGrupoSel); if(!mmgGrupoSel) selG.value=''; sincronizarMmg(); };
    contG.appendChild(btn);
  });

  if (!mmgGrupoSel) { pSub.classList.add('hidden'); pCod.classList.add('hidden'); return; }
  const pal = ISO_PALETTE[mmgGrupoSel];
  pSub.classList.remove('hidden');
  document.getElementById('mmg-label-subgrupo').innerText = `Subgrupo (${pal.nome})`;
  document.getElementById('mmg-label-subgrupo').style.color = pal.cor;
  cSub.innerHTML = '';

  const addSubBtn = (label, subVal, isAct) => {
    const b = document.createElement('button'); b.type='button'; b.className='sub-btn'; b.innerText=label;
    b.style.cssText = `color:${isAct?pal.fg:pal.cor};background:${isAct?pal.bg:'#0f172a'};border-color:${pal.cor}`;
    b.onclick = () => { mmgSubSel = subVal; mmgManual = Boolean(subVal); sincronizarMmg(); };
    cSub.appendChild(b);
  };
  addSubBtn(`${mmgGrupoSel} (Todos)`, null, !mmgSubSel);
  (mmgSubsIso[mmgGrupoSel]||[]).filter(s => !fil || subsDisp.has(normMmg(s))).forEach(s => addSubBtn(s, normMmg(s), mmgSubSel===normMmg(s)));

  pCod.classList.remove('hidden');
  document.getElementById('mmg-label-codigo').innerText = mmgSubSel ? `Grupo MAPAL (${mmgSubSel})` : `Grupo MAPAL (${pal.nome})`;
  document.getElementById('mmg-label-codigo').style.color = pal.cor;
  cCod.innerHTML = '';
  const codAtivo = normMmg(selG.value);
  [...new Set([...gruposMmgOrdem, ...dispNorm])].filter(c => {
    const iso=(mmgMeta[c]?.iso||c[0]).toUpperCase(), sub=normMmg(mmgMeta[c]?.subgrupo||c.match(/^([A-Z]+\d+)/)?.[1]||'');
    return iso===mmgGrupoSel && (!mmgSubSel || sub===mmgSubSel || c.startsWith(mmgSubSel));
  }).sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})).forEach(cod => {
    const kc = chaveMmg(cod), hab = !fil || Boolean(mapDisp[kc]), real = mapDisp[kc] || cod, act = chaveMmg(codAtivo)===kc && Boolean(codAtivo);
    const b = document.createElement('button'); b.type='button'; b.className='mmg-code-btn'; b.disabled=!hab; b.title=mmgMeta[cod]?.label||real; b.innerText=real;
    b.style.cssText = `color:${act?pal.fg:pal.cor};background:${act?pal.bg:'#0f172a'};border-color:${pal.cor};${act?`box-shadow:0 0 0 1px ${pal.cor}`:''}`;
    b.onclick = () => {
      if (![...selG.options].some(o=>normMmg(o.value)===normMmg(real))) { const op=document.createElement('option'); op.value=real; op.text=gruposMmgMap[real]||real; selG.appendChild(op); }
      selG.value = real; mmgManual = true; sincronizarMmg();
    };
    cCod.appendChild(b);
  });
  document.getElementById('mmg-detalhe-codigo').innerText = mmgMeta[codAtivo]?.dureza || mmgMeta[codAtivo]?.label || codAtivo || '';
}

function sincronizarMmg() {
  const g = normMmg(document.getElementById('grupo').value);
  if (g && PROP_GRUPO[g[0]]) document.getElementById('densidade').value = PROP_GRUPO[g[0]].d.toFixed(2);
  filtrarCatalogoCascata('mmg');
  atualizarFiltroBrocas(true);
  const bk = document.getElementById('broca').value;
  renderBotoesMmg(bk && dados[bk] ? dados[bk].gruposList : []);
  document.getElementById('mmg-selecao-detalhe').innerText = g ? (gruposMmgMap[g]||g) : (mmgSubSel || mmgGrupoSel || '—');
  atualizarCalculo();
}

function onSelectGrupoManual() {
  const v = normMmg(document.getElementById('grupo').value);
  mmgManual = Boolean(v);
  if (v) { mmgGrupoSel = (mmgMeta[v]?.iso||v[0]).toUpperCase(); mmgSubSel = normMmg(mmgMeta[v]?.subgrupo||v.match(/^([A-Z]+\d+)/)?.[1]||'') || null; }
  sincronizarMmg();
}

function getD1() { const n = parseFloat((document.getElementById('filtro-d1').value||'').replace(',','.')); return (!isNaN(n)&&n>0)?n:null; }
const matchD1 = (it, d1) => d1===null || (it.d1!==null && it.d1!==undefined && !isNaN(+it.d1) && Math.abs(+it.d1-d1)<=0.015);

function fillSel(el, opts, ph, fmt, cur) {
  el.innerHTML = `<option value="">${ph}</option>`;
  opts.forEach(v => { const op=document.createElement('option'); op.value=String(v); op.text=fmt?fmt(v):String(v); if(cur!==''&&String(v)===String(cur))op.selected=true; el.appendChild(op); });
}

function getBaseCatalogo() {
  const tok = (document.getElementById('ref-pesquisa').value||'').trim().toLowerCase().split(/\s+/).filter(Boolean);
  if (!Array.isArray(REFERENCIAS_JSON)) return [];
  if (!tok.length) return REFERENCIAS_JSON;
  return REFERENCIAS_JSON.filter(it => {
    const fk = String(it.familia||'').toLowerCase();
    const hay = [it.order_no,it.specification,it.designacao,it.nome,it.familia,it.nome_produto||mapaFam[fk]?.nomeProduto,it.variante,it.refrigeracao,normRefrig(it),extrairDIN(it),getGamaIt(it),getCatIt(it),it.d1!=null?Number(it.d1).toFixed(2):''].join(' ').toLowerCase();
    return tok.every(t => hay.includes(t));
  });
}

function filtrarCatalogoCascata(origem=null) {
  const sCat=document.getElementById('categoria'), sGama=document.getElementById('filtro-gama-cat'), sRef=document.getElementById('filtro-refrig-cat'), sEnc=document.getElementById('filtro-encabadouro-cat'), dlD1=document.getElementById('lista-d1-sugestoes'), sXd=document.getElementById('filtro-xd'), sOrd=document.getElementById('filtro-order-no'), sMod=document.getElementById('broca');
  const d1 = getD1(), gSel = normMmg(document.getElementById('grupo')?.value||'');
  const modFilt = (origem==='modelo' && sMod.value) ? sMod.value.toLowerCase() : '';
  const base = getBaseCatalogo().filter(c => {
    const t = dados[String(c.familia||'').toLowerCase()];
    if (!t?.grupos || (!mmgGrupoSel && !mmgSubSel && !gSel)) return true;
    const grps = t.gruposList.length ? t.gruposList : Object.keys(t.grupos);
    return grps.some(g => gSel ? chaveMmg(g)===chaveMmg(gSel) : mmgSubSel ? chaveMmg(mmgMeta[normMmg(g)]?.subgrupo||g).startsWith(chaveMmg(mmgSubSel)) : (mmgMeta[normMmg(g)]?.iso||g[0]).toUpperCase()===mmgGrupoSel);
  });

  const c1 = sCat.value, c2 = sGama.value, c3 = sRef.value, c4 = sEnc.value, c5 = sXd.value;
  const matchCond = (c, skip) =>
    (skip==='cat' || !c1 || getCatIt(c)===c1) &&
    (skip==='gama' || !c2 || getGamaIt(c)===c2) &&
    (skip==='ref' || !c3 || normRefrig(c)===c3) &&
    (skip==='enc' || !c4 || extrairDIN(c)===c4) &&
    (skip==='d1' || matchD1(c, d1)) &&
    (skip==='xd' || !c5 || String(c.variante||'').trim()===c5) &&
    (!modFilt || String(c.familia||'').toLowerCase()===modFilt);

  let cats = [...new Set(base.filter(c=>getCatIt(c)&&matchCond(c,'cat')).map(getCatIt))];
  if (!cats.length) cats = [...new Set([...(FAMILIAS_JSON||[]).map(f=>f?.categoria||f?.Categoria), ...(REFERENCIAS_JSON||[]).map(getCatIt), ...Object.values(dados).map(t=>t.categoria)].map(x=>String(x||'').trim()).filter(Boolean))];
  fillSel(sCat, cats, 'Todas', null, cats.includes(c1)?c1:'');

  const gamas = [...new Set(base.filter(c=>getGamaIt(c)&&matchCond(c,'gama')).map(getGamaIt))].sort((a,b)=>['expert','performance','basic'].indexOf(a)-['expert','performance','basic'].indexOf(b));
  fillSel(sGama, gamas, 'Todas', fmtGama, gamas.includes(c2)?c2:'');

  const refs = [...new Set(base.filter(c=>normRefrig(c)&&matchCond(c,'ref')).map(normRefrig))].sort((a,b)=>['int','ext','mql','ar'].indexOf(a)-['int','ext','mql','ar'].indexOf(b));
  fillSel(sRef, refs, 'Todas', fmtRefrig, refs.includes(c3)?c3:'');

  const encs = [...new Set(base.filter(c=>extrairDIN(c)&&matchCond(c,'enc')).map(extrairDIN))].sort((a,b)=>['HA','HB','HE'].indexOf(a)-['HA','HB','HE'].indexOf(b));
  fillSel(sEnc, encs, 'Todos', e=>`DIN ${e}`, encs.includes(c4)?c4:'');

  const d1s = [...new Set(base.filter(c=>c.d1!=null&&!isNaN(+c.d1)&&matchCond(c,'d1')).map(c=>Number(c.d1).toFixed(2)))].sort((a,b)=>+a-+b);
  dlD1.innerHTML = d1s.map(x=>`<option value="${x}">`).join('');

  const xds = [...new Set(base.filter(c=>c.variante&&matchCond(c,'xd')).map(c=>String(c.variante).trim()))].sort();
  fillSel(sXd, xds, 'Todas', null, xds.includes(c5)?c5:'');

  const finais = base.filter(c => matchCond(c, null));
  window._finaisCatalogo = finais;
  document.getElementById('contador-referencias').innerText = `${finais.length} ref.`;
  sOrd.innerHTML = `<option value="">${finais.length?`Escolher referência (${finais.length})...`:'Sem referências com estes filtros'}</option>` +
    finais.map((it,i)=>`<option value="${i}">${it.order_no} | ${it.familia||'—'} | Ø${it.d1!=null?Number(it.d1).toFixed(2):'—'} (${it.variante||'—'}) | l3:${it.l3!=null?Number(it.l3).toFixed(0)+'mm':'—'}</option>`).join('');

  if (d1 !== null) document.getElementById('diametro').value = d1.toFixed(2);
  if (origem==='refrig' && ['int','ext','mql','ar'].includes(sRef.value)) setRefrig(sRef.value);
  if (origem!=='order' && origem!=='modelo') { linhaAtivaInterna = sGama.value || ''; atualizarFiltroBrocas(true); }

  const hasFilt = Boolean(sCat.value||sGama.value||sRef.value||sEnc.value||d1!==null||sXd.value||(document.getElementById('ref-pesquisa').value||'').trim()||mmgGrupoSel||mmgSubSel||gSel);
  if (finais.length===1 && hasFilt && origem!=='order') { sOrd.value='0'; onSelecionarOrderCatalogo(); }
  else if (!hasFilt && origem!=='order') { referenciaAtivaObj=null; atualizarPainelCotas(); }
  else if (origem!=='order') { if (referenciaAtivaObj && !finais.includes(referenciaAtivaObj)) referenciaAtivaObj=null; atualizarPainelCotas(); atualizarCalculo(); }
}

const onFiltroCatalogoChange = c => filtrarCatalogoCascata(c);

function onSelecionarOrderCatalogo() {
  const it = (window._finaisCatalogo||[])[parseInt(document.getElementById('filtro-order-no').value,10)];
  if (!it) { referenciaAtivaObj=null; atualizarPainelCotas(); atualizarCalculo(); return; }
  referenciaAtivaObj = it;
  const fk = String(it.familia||'').toLowerCase();
  if (fk && dados[fk]) {
    const t = dados[fk];
    if (getGamaIt(it)) t.linha = getGamaIt(it);
    if (getCatIt(it)) t.categoria = getCatIt(it);
    linhaAtivaInterna = t.linha;
    if (t.categoria) document.getElementById('categoria').value = t.categoria;
    atualizarFiltroBrocas(true);
    document.getElementById('broca').value = fk;
    const mv = Object.keys(t.variantes||{}).find(k=>k.toLowerCase()===String(it.variante||'').trim().toLowerCase());
    const lockM = mmgManual; mudarBroca(mv||null); mmgManual = lockM;
  }
  const rc = normRefrig(it); if (['int','ext','mql','ar'].includes(rc)) setRefrig(rc);
  if (it.d1!=null && !isNaN(+it.d1)) document.getElementById('diametro').value = Number(it.d1).toFixed(2);
  atualizarPainelCotas(); atualizarCalculo();
}

function aplicarPesquisaReferencia() {
  const raw = document.getElementById('ref-pesquisa').value.trim();
  const fb = document.getElementById('ref-feedback');
  filtrarCatalogoCascata('pesquisa');
  const list = window._finaisCatalogo||[];
  if (!raw) { fb.innerText="Se souber a referência, pesquise acima; se não souber, filtre abaixo."; fb.className="text-[10px] text-slate-400 block"; return; }
  if (list.length) {
    document.getElementById('filtro-order-no').value='0'; onSelecionarOrderCatalogo();
    const din = extrairDIN(list[0]);
    fb.innerText = `Encontradas ${list.length} ref. para "${raw}". Selecionada: ${list[0].order_no}${din?` [DIN 6535-${din}]`:''}.`;
    fb.className = "text-[10px] text-emerald-400 block"; return;
  }
  const up = raw.toUpperCase(), fk = Object.keys(dados).find(k => `${k} ${dados[k].nomeProduto} ${dados[k].nome}`.toUpperCase().includes(up));
  if (!fk) { fb.innerText=`Nenhuma referência encontrada para "${raw}".`; fb.className="text-[10px] text-amber-400 block"; return; }
  const t = dados[fk]; linhaAtivaInterna = t.linha; if (t.categoria) document.getElementById('categoria').value = t.categoria;
  atualizarFiltroBrocas(true); document.getElementById('broca').value = fk;
  const xd = up.match(/(\d+)\s*X\s*D/)?.[1]; mudarBroca(xd && t.variantes[`${xd}xD`] ? `${xd}xD` : null);
  fb.innerText = `Selecionado: ${t.nome} (${getVarianteAtiva()})`; fb.className="text-[10px] text-emerald-400 block";
}

function limparFiltrosCatalogo() {
  ['ref-pesquisa','categoria','filtro-gama-cat','filtro-refrig-cat','filtro-encabadouro-cat','filtro-d1','filtro-xd','filtro-order-no','broca','grupo'].forEach(id=>{ const el=document.getElementById(id); if(el) el.value=''; });
  mmgGrupoSel=null; mmgSubSel=null; linhaAtivaInterna=''; referenciaAtivaObj=null;
  document.getElementById('ref-feedback').innerText="Se souber a referência, pesquise acima; se não souber, filtre abaixo.";
  filtrarCatalogoCascata('reset'); atualizarFiltroBrocas(false); renderBotoesMmg([]); atualizarPainelCotas(); atualizarCalculo();
}

function atualizarPainelCotas() {
  const r = referenciaAtivaObj, d = parseFloat(document.getElementById('diametro').value);
  const fmt = (v, dec=0) => (v===null||v===undefined||v===''||isNaN(+v)) ? '—' : `${Number(v).toFixed(dec)} mm`;
  document.getElementById('cota-d1').innerText = r ? fmt(r.d1,2) : fmt(d,2);
  document.getElementById('cota-d2').innerText = r ? fmt(r.d2,1) : '—';
  document.getElementById('cota-l1').innerText = r ? fmt(r.l1,0) : '—';
  document.getElementById('cota-l2').innerText = r ? fmt(r.l2,0) : '—';
  document.getElementById('cota-l3').innerText = r ? fmt(r.l3,0) : '—';
  document.getElementById('cota-l4').innerText = r ? fmt(r.l4,0) : '—';
  const bk = document.getElementById('broca').value;
  document.getElementById('meta-referencia-ativa').innerText = r
    ? `Order: ${r.order_no||'—'} | Spec: ${r.specification||'—'} | DIN 6535: ${extrairDIN(r)||'—'}${normRefrig(r)?` | Refrig: ${fmtRefrig(normRefrig(r))}`:''}`
    : `Família: ${bk&&dados[bk]?dados[bk].nome:'Sem modelo selecionado'}${bk?` (${getVarianteAtiva()})`:''} | DIN 6535: —`;

  const lockedD1 = getD1()!==null || (r && r.d1!=null && !isNaN(+r.d1));
  document.getElementById('bloco-diametro-manual').classList.toggle('hidden', lockedD1);
  document.getElementById('bloco-diametro-catalogo').classList.toggle('hidden', !lockedD1);
  if (lockedD1) document.getElementById('diametro-catalogo-valor').innerText = `Ø ${!isNaN(d)?d.toFixed(2):'—'} mm`;
}

function onDiametroPrincipalChange() {
  const d = parseFloat(document.getElementById('diametro').value);
  if (!isNaN(d) && d > 0) {
    const iD1 = document.getElementById('filtro-d1');
    if (iD1.value.trim()) iD1.value = d.toFixed(2);
    if (referenciaAtivaObj?.d1!=null && Math.abs(+referenciaAtivaObj.d1 - d) > 1e-3) referenciaAtivaObj = null;
  }
  atualizarCalculo();
}

function obterFamiliasCompativeis() {
  const c1=document.getElementById('categoria').value, c2=document.getElementById('filtro-gama-cat').value, c3=document.getElementById('filtro-refrig-cat').value, c4=document.getElementById('filtro-encabadouro-cat').value, d1=getD1(), c5=document.getElementById('filtro-xd').value, q=(document.getElementById('ref-pesquisa').value||'').trim(), gSel=normMmg(document.getElementById('grupo')?.value||'');
  if (!(c1||c2||c3||c4||d1!==null||c5||q||mmgGrupoSel||mmgSubSel||gSel)) return null;
  if (!(c1||c2||c3||c4||d1!==null||c5||q)) {
    return new Set(Object.entries(dados).filter(([,t]) => {
      const grps = t.gruposList.length?t.gruposList:Object.keys(t.grupos);
      return !grps.length || grps.some(g => gSel ? chaveMmg(g)===chaveMmg(gSel) : mmgSubSel ? chaveMmg(mmgMeta[normMmg(g)]?.subgrupo||g).startsWith(chaveMmg(mmgSubSel)) : (mmgMeta[normMmg(g)]?.iso||g[0]).toUpperCase()===mmgGrupoSel);
    }).map(([k])=>k.toLowerCase()));
  }
  const set = new Set();
  getBaseCatalogo().filter(c => (!c1||getCatIt(c)===c1)&&(!c2||getGamaIt(c)===c2)&&(!c3||normRefrig(c)===c3)&&(!c4||extrairDIN(c)===c4)&&matchD1(c,d1)&&(!c5||String(c.variante||'').trim()===c5)).forEach(c => { const fk=String(c.familia||'').toLowerCase(); if(fk&&dados[fk]) set.add(fk); });
  return set;
}

function atualizarFiltroBrocas(manter=false) {
  const sB = document.getElementById('broca'), cur = manter ? sB.value : '', compat = obterFamiliasCompativeis();
  const list = Object.keys(dados).filter(k => (!linhaAtivaInterna||dados[k].linha===linhaAtivaInterna) && (!document.getElementById('categoria').value||dados[k].categoria===document.getElementById('categoria').value) && (!compat||compat.has(k.toLowerCase())));
  sB.innerHTML = `<option value="">— Vazio (sem modelo selecionado) —</option>` + list.map(k=>`<option value="${k}">${dados[k].nome}</option>`).join('');
  document.getElementById('info-modelo-filtro').innerText = compat ? `${list.length} compatível(is)` : `${list.length} modelo(s)`;
  sB.value = (cur && list.includes(cur)) ? cur : '';
  mudarBroca();
}

function onMudarModeloFerramenta() {
  const bk = document.getElementById('broca').value;
  if (bk && dados[bk]) {
    linhaAtivaInterna = dados[bk].linha;
    if (dados[bk].categoria) document.getElementById('categoria').value = dados[bk].categoria;
    if (referenciaAtivaObj && String(referenciaAtivaObj.familia||'').toLowerCase()!==bk.toLowerCase()) referenciaAtivaObj = null;
  } else referenciaAtivaObj = null;
  mudarBroca(); filtrarCatalogoCascata('modelo');
}

function mudarBroca(varPref=null) {
  const bk = document.getElementById('broca').value, sG = document.getElementById('grupo'), btnInt = document.getElementById('ref-int');
  if (!bk || !dados[bk]) {
    btnInt.disabled=false; btnInt.classList.remove('opacity-40','cursor-not-allowed'); show('aviso-refrig'); hide('aviso-refrig');
    const all = gruposMmgOrdem.map(normMmg), cur = normMmg(sG.value);
    sG.innerHTML = `<option value="">— Todos os grupos MMG disponíveis —</option>` + all.map(g=>`<option value="${g}">${gruposMmgMap[g]||g}</option>`).join('');
    sG.value = all.includes(cur) ? cur : '';
    renderBotoesMmg([]); atualizarPainelCotas(); atualizarCalculo(); return;
  }
  const t = dados[bk];
  btnInt.disabled = t.temRefrigInt===false;
  btnInt.classList.toggle('opacity-40', t.temRefrigInt===false);
  btnInt.classList.toggle('cursor-not-allowed', t.temRefrigInt===false);
  document.getElementById('aviso-refrig').classList.toggle('hidden', t.temRefrigInt!==false);
  if (t.temRefrigInt===false && refrigAtual==='int') setRefrig('ext');

  const curG = normMmg(sG.value), grps = (t.gruposList.length?t.gruposList:Object.keys(t.grupos)).map(normMmg);
  sG.innerHTML = grps.length ? grps.map(g=>`<option value="${g}">${t.gruposNames[g]||gruposMmgMap[g]||g}</option>`).join('') : `<option value="">Sem parâmetros no JSON</option>`;
  sG.value = grps.includes(curG) ? curG : (grps[0]||'');
  if (varPref && t.variantes[varPref]) { const sXd=document.getElementById('filtro-xd'); if([...sXd.options].some(o=>o.value===varPref)) sXd.value=varPref; }
  renderBotoesMmg(grps);
  mudarGrupoMaterial();
}

function mudarGrupoMaterial() {
  const g = normMmg(document.getElementById('grupo').value);
  if (g && PROP_GRUPO[g[0]]) document.getElementById('densidade').value = PROP_GRUPO[g[0]].d.toFixed(2);
  document.getElementById('mmg-selecao-detalhe').innerText = g ? (gruposMmgMap[g]||g) : (mmgSubSel || mmgGrupoSel || '—');
  atualizarCalculo();
}

function setRefrig(tipo) {
  const bk = document.getElementById('broca').value;
  if (tipo==='int' && bk && dados[bk]?.temRefrigInt===false) return;
  refrigAtual = tipo;
  ['int','ext','mql','ar'].forEach(t => { document.getElementById(`ref-${t}`).className = t===tipo ? "py-1.5 rounded bg-blue-600 text-white" : "py-1.5 rounded text-slate-400"; });
  atualizarCalculo();
}

function ajustarDiametro(d) {
  const inp = document.getElementById('diametro');
  inp.value = Math.min(30, Math.max(0.5, (parseFloat(inp.value)||12) + d)).toFixed(2);
  onDiametroPrincipalChange();
}

function ajustarPct(tipo, d) {
  if (tipo==='vc') { vcPct = Math.min(50,Math.max(-50,vcPct+d)); document.getElementById('vc-slider').value=vcPct; }
  else { fPct = Math.min(50,Math.max(-50,fPct+d)); document.getElementById('f-slider').value=fPct; }
  atualizarCalculo();
}
const onSliderVc = () => { vcPct = +document.getElementById('vc-slider').value||0; atualizarCalculo(); };
const onSliderF = () => { fPct = +document.getElementById('f-slider').value||0; atualizarCalculo(); };
const resetPct = tipo => { if(tipo==='vc'){vcPct=0;document.getElementById('vc-slider').value=0;}else{fPct=0;document.getElementById('f-slider').value=0;} atualizarCalculo(); };

function toggleLock(campo) {
  locks[campo] = !locks[campo];
  const on = locks[campo], inp = document.getElementById(`input-${campo}`), btn = document.getElementById(`btn-lock-${campo}`), card = document.getElementById(`card-${campo}`), st = document.getElementById(`status-${campo}`);
  inp.readOnly = !on; btn.innerText = on ? '🔓' : '🔒';
  const col = campo==='rpm-max' ? 'border-cyan-500/80' : 'border-amber-500/80';
  const txtCol = campo==='rpm-max' ? 'text-cyan-300' : 'text-amber-300';
  card.classList.toggle(col, on); inp.classList.toggle(txtCol, on);
  st.innerText = campo==='rpm-max' ? (on?'Ativo':'Inativo') : (on?'Manual':'Auto');
  st.className = `text-[9px] ${on ? (campo==='rpm-max'?'text-cyan-400 font-semibold':'text-amber-400 font-semibold') : 'text-slate-500'}`;
  if (on) inp.focus();
  atualizarCalculo();
}

function getGrupoEfetivo() {
  const bk = document.getElementById('broca').value, gk = normMmg(document.getElementById('grupo').value);
  if (!bk || !dados[bk] || !gk || !document.getElementById('liga-check').checked) return gk;
  const lst = (dados[bk].gruposList||[]).map(normMmg), idx = lst.indexOf(gk);
  return (idx !== -1 && idx < lst.length - 1) ? lst[idx + 1] : gk;
}

const getVarianteAtiva = () => referenciaAtivaObj?.variante?.trim() || document.getElementById('filtro-xd').value || Object.keys(dados[document.getElementById('broca').value]?.variantes||{})[0] || '5xD';

function togglePeckingInputs() { document.getElementById('pecking-options').classList.toggle('hidden', !document.getElementById('pecking-check').checked); atualizarCalculo(); }
function onChangePeckingUnidade() {
  const u = document.getElementById('pecking-unidade').value, inp = document.getElementById('pecking-passo'), d = parseFloat(document.getElementById('diametro').value)||12, v = parseFloat(inp.value)||(u==='xd'?3:36);
  inp.step = u==='mm'?'1':'0.5'; inp.value = u==='mm' ? (v*d).toFixed(1) : (v/d).toFixed(2); atualizarCalculo();
}

function atualizarGauge(tipo, val, maxCap, unit) {
  const needle = document.getElementById(tipo==='pot'?'needle-potencia':'needle-binario'), vEl = document.getElementById(tipo==='pot'?'val-gauge-pot':'val-gauge-bin'), bEl = document.getElementById(tipo==='pot'?'badge-gauge-pot':'badge-gauge-bin');
  vEl.innerText = `${val.toFixed(tipo==='pot'?2:1)} ${unit}`;
  if (!maxCap || maxCap <= 0) { needle.style.transform='rotate(-90deg)'; bEl.innerText='Sem Limite Definido'; bEl.className='text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400'; return null; }
  const r = val / maxCap;
  needle.style.transform = `rotate(${(-90 + Math.min(1,Math.max(0,r))*180).toFixed(1)}deg)`;
  if (r < 0.7) { bEl.innerText=`Seguro (${(r*100).toFixed(0)}%)`; bEl.className='text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400'; return null; }
  if (r <= 0.9) { bEl.innerText=`Atenção (${(r*100).toFixed(0)}%)`; bEl.className='text-[9px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-400'; return null; }
  if (r <= 1.0) { bEl.innerText=`Crítico (${(r*100).toFixed(0)}%)`; bEl.className='text-[9px] font-bold px-2 py-0.5 rounded bg-red-950 text-red-400'; return null; }
  const ex = ((r-1)*100).toFixed(0);
  bEl.innerText=`STALL +${ex}%`; bEl.className='text-[9px] font-extrabold px-2 py-0.5 rounded bg-red-600 text-white';
  return `${tipo==='pot'?'Potência':'Binário'} excede capacidade em +${ex}%`;
}

function calcularPonto(toolData, grpObj, d, refCode, vPct, fPct, rpmMax) {
  const ds = toolData.diametros?.length ? toolData.diametros : [3,4.5,6.5,9.5,14,20];
  const fs = grpObj.f?.length ? grpObj.f : ds.map(()=>0.05);
  let idx = 0; for (let i=0;i<ds.length;i++) if (ds[i]<=d) idx=i; else break;
  let estado='Dentro da gama', cor='text-emerald-400', metodo='Interpolação Linear';
  if (ds.length > 1) {
    if (idx >= ds.length-1) { idx=ds.length-2; estado='Extrapolação Superior'; cor='text-amber-400'; metodo=cor=estado; }
    else if (d < ds[0]) { idx=0; estado='Extrapolação Inferior'; cor='text-amber-400'; metodo=estado; }
  }
  const x1=ds[idx], x2=ds[idx+1]??x1+1, y1=fs[idx]??0.05, y2=fs[idx+1]??y1;
  const fBase = Math.max(0.001, (y1 - ((x2-x1)?(y2-y1)/(x2-x1):0)*x1) + ((x2-x1)?(y2-y1)/(x2-x1):0)*d);
  let f = fBase * (1 + fPct/100);
  const vcRaw = grpObj.vc?.[refCode] > 0 ? grpObj.vc[refCode] : (grpObj.vc?.int > 0 ? grpObj.vc.int : (grpObj.vc?.ext || 0));
  let vc = vcRaw * (1 + vPct/100);
  let n = d > 0 ? Math.round((vc*1000)/(Math.PI*d)) : 0;
  if (rpmMax > 0 && n > rpmMax) { n = rpmMax; vc = (n*Math.PI*d)/1000; estado='Limitado por RPM Máx.'; cor='text-amber-400'; }
  return { f, vc, n, vf: Math.round(f*n), ds, fs, idx, estado, cor, metodo };
}

function atualizarCalculo() {
  const bk = document.getElementById('broca').value, gEf = getGrupoEfetivo();
  const d = Math.max(0.5, parseFloat(document.getElementById('diametro').value)||12);
  const prof = Math.max(0.1, parseFloat(document.getElementById('profundidade').value)||31);
  const qtd = Math.max(1, parseInt(document.getElementById('qtd-furos').value,10)||50);
  const dens = Math.max(0.5, parseFloat(document.getElementById('densidade').value)||7.85);
  const suc = Math.max(0, parseFloat(document.getElementById('preco-sucata').value)||0.35);
  const ch = Math.max(0, parseFloat(document.getElementById('custo-hora').value)||50);
  const rpmMaxVal = locks['rpm-max'] ? (parseFloat(document.getElementById('input-rpm-max').value)||8000) : 0;

  document.getElementById('vc-pct-val').innerText = `${vcPct>0?'+':''}${vcPct}%`;
  document.getElementById('f-pct-val').innerText = `${fPct>0?'+':''}${fPct}%`;

  const t = bk && dados[bk], gObj = t && gEf && resolverGrupo(t, gEf);
  atualizarPainelCotas();

  const l3 = (referenciaAtivaObj?.l3!=null && !isNaN(+referenciaAtivaObj.l3)) ? +referenciaAtivaObj.l3 : null;
  const nom = (t?.variantes?.[getVarianteAtiva()]?.ratio || 5) * d;
  const pBox = document.getElementById('alerta-profundidade'), pTxt = document.getElementById('texto-limite-prof'), pBdg = document.getElementById('badge-limite-prof');
  if (l3 !== null) {
    const ok = prof <= l3;
    pBox.className = `px-2.5 py-1.5 rounded-md border text-[10px] flex justify-between items-center gap-2 shrink-0 ${ok?'bg-emerald-950/40 border-emerald-700/60 text-emerald-200':'bg-red-950/70 border-red-500/80 text-red-200'}`;
    pTxt.innerText = ok ? `Dentro do limite real l3 (${l3.toFixed(0)} mm | margem ${(l3-prof).toFixed(1)} mm)` : `EXCEDE l3 (${l3.toFixed(0)} mm) em +${(prof-l3).toFixed(1)} mm!`;
    pBdg.innerText = ok ? 'OK (l3)' : 'EXCEDE l3'; pBdg.className = `font-bold shrink-0 ${ok?'text-emerald-300':'text-red-300'}`;
  } else {
    pTxt.innerText = t ? `Sem cota l3 na ref. ativa · Nominal ${getVarianteAtiva()} ≈ ${nom.toFixed(1)} mm` : 'Selecione um modelo ou referência';
    pBdg.innerText = t ? 'SEM l3' : 'AGUARDAR';
  }

  if (!gObj) { document.getElementById('tabela-ref').innerHTML=''; document.getElementById('svg-grafico').innerHTML=''; return; }

  const pto = calcularPonto(t, gObj, d, refrigAtual, vcPct, fPct, rpmMaxVal);
  let f = locks.f ? (parseFloat(document.getElementById('input-f').value)||pto.f) : pto.f;
  let vc = locks.vc ? (parseFloat(document.getElementById('input-vc').value)||pto.vc) : pto.vc;
  if (!locks.f) document.getElementById('input-f').value = f.toFixed(4);
  if (!locks.vc) document.getElementById('input-vc').value = Math.round(vc);

  let n = d > 0 ? Math.round((vc*1000)/(Math.PI*d)) : 0;
  let est = pto.estado, cor = pto.cor;
  if (rpmMaxVal > 0 && n > rpmMaxVal) { n = rpmMaxVal; vc = (n*Math.PI*d)/1000; if(!locks.vc) document.getElementById('input-vc').value=Math.round(vc); est='Limitado por RPM Máx.'; cor='text-amber-400'; }
  const vf = Math.round(f * n);

  const pOn = document.getElementById('pecking-check').checked, pUn = document.getElementById('pecking-unidade').value;
  const pInp = parseFloat(document.getElementById('pecking-passo').value)||(pUn==='xd'?3:36), pRet = parseFloat(document.getElementById('pecking-retensao').value)||5000;
  const passoMm = pUn==='xd' ? pInp*d : pInp, passos = Math.max(1, Math.ceil(prof/passoMm));
  document.getElementById('pecking-equiv').innerText = pUn==='xd' ? `Equiv: ${passoMm.toFixed(1)} mm (${passos} passo${passos>1?'s':''})` : `Equiv: ${(passoMm/d).toFixed(2)}×D (${passos} passo${passos>1?'s':''})`;

  let tFuro = vf > 0 ? ((prof + 0.3*d)/vf)*60 : 0;
  if (pOn) tFuro = (vf>0?(prof/vf)*60:0) + (passos*(prof/pRet))*60 + (vf>0?((0.3*d)/vf)*60:0);

  const kc = PROP_GRUPO[normMmg(gEf)[0]]?.kc || 2200;
  const ff = 0.5 * kc * d * Math.pow(f, 0.7);
  const mc = (kc * Math.pow(d, 2) * Math.pow(f, 0.8)) / 8000;
  const potKw = (mc * n) / (9550 * 0.85);
  const pMaxInp = parseFloat(document.getElementById('spindle-potencia').value);
  const pMaxKw = pMaxInp > 0 ? (document.getElementById('unidade-potencia').value==='cv' ? pMaxInp*0.735499 : pMaxInp) : null;
  const bMaxNm = parseFloat(document.getElementById('spindle-binario').value) > 0 ? parseFloat(document.getElementById('spindle-binario').value) : null;

  const errs = [atualizarGauge('pot', potKw, pMaxKw, 'kW'), atualizarGauge('bin', mc, bMaxNm, 'N·m')].filter(Boolean);
  document.getElementById('alerta-sobrecarga-spindle').classList.toggle('hidden', !errs.length);
  document.getElementById('texto-sobrecarga-spindle').innerText = errs.join(' | ');

  const area = Math.PI * Math.pow(d/2, 2), volFuro = (area*prof)/1000, volTot = volFuro*qtd, massFuro = volFuro*dens, pesoTot = (massFuro*qtd)/1000;
  document.getElementById('res-n').innerText = n;
  document.getElementById('res-vf').innerText = vf;
  document.getElementById('res-tempo-total').innerHTML = `${((tFuro*qtd)/60).toFixed(1)} min <span class="text-xs font-normal text-slate-300">(${tFuro.toFixed(1)} seg/furo)</span>`;
  document.getElementById('res-metragem').innerText = `${((prof*qtd)/1000).toFixed(2)} metros`;
  document.getElementById('res-volume-total').innerText = `${volTot.toFixed(1)} cm³`;
  document.getElementById('res-taxa').innerText = `${((area*vf)/1000).toFixed(1)} cm³/min`;
  document.getElementById('res-peso').innerText = `${pesoTot.toFixed(3)} kg`;
  document.getElementById('res-peso-g').innerText = `${massFuro.toFixed(2)} g / furo`;
  document.getElementById('res-sucata-val').innerText = `${(pesoTot*suc).toFixed(2)} €`;
  document.getElementById('res-sucata-furo').innerText = `${((massFuro/1000)*suc).toFixed(4)} € / furo`;
  document.getElementById('res-custo-total').innerHTML = `${(tFuro*(ch/3600)*qtd).toFixed(2)} € <span class="text-[10px] font-normal text-slate-300">(${(tFuro*(ch/3600)).toFixed(3)} €/furo)</span>`;
  document.getElementById('res-custo-hora-ref').innerText = `${ch.toFixed(2)} €/h`;
  document.getElementById('res-forca').innerText = `${Math.round(ff)} N`;
  document.getElementById('res-forca-kgf').innerText = `${(ff/9.80665).toFixed(1)} kgf`;
  document.getElementById('res-binario-card').innerText = `${mc.toFixed(1)} N·m`;
  document.getElementById('val-estado').innerText = est; document.getElementById('val-estado').className = `text-[9px] font-bold ${cor}`;
  document.getElementById('badge-metodo').innerText = pto.metodo;

  document.getElementById('tabela-ref').innerHTML = pto.ds.map((dc, i) => {
    const fc = pto.fs[i]??0.05;
    let nc = dc>0 ? Math.round((vc*1000)/(Math.PI*dc)) : 0;
    if (rpmMaxVal>0 && nc>rpmMaxVal) nc = rpmMaxVal;
    const hl = (i===pto.idx || i===pto.idx+1) ? 'bg-blue-900/20 font-medium text-blue-200' : '';
    return `<tr class="${hl}"><td class="py-1">${dc.toFixed(2)}</td><td class="py-1">${fc.toFixed(3)}</td><td class="py-1">${nc}</td><td class="py-1">${Math.round(fc*nc)}</td></tr>`;
  }).join('');

  renderGrafico(pto.ds, pto.fs, d, f, pto.idx);
  if (!document.getElementById('modal-comparacao').classList.contains('hidden')) atualizarComparacao();
}

function renderGrafico(ds, fs, dCalc, fCalc, idxInf) {
  const svg = document.getElementById('svg-grafico');
  const W=400, H=180, pL=40, pR=20, pT=18, pB=30, pW=W-pL-pR, pH=H-pT-pB;
  const xs=[...ds,dCalc], ys=[...fs,fCalc];
  let minX=Math.min(...xs), maxX=Math.max(...xs), minY=Math.min(...ys)*0.85, maxY=Math.max(...ys)*1.15;
  if(minX===maxX){minX-=1;maxX+=1;} if(minY===maxY){minY-=0.01;maxY+=0.01;}
  const sx = x => pL + ((x-minX)/(maxX-minX))*pW, sy = y => pT + pH - ((y-minY)/(maxY-minY))*pH;
  const ns = "http://www.w3.org/2000/svg";
  const el = (tag, attrs) => { const n=document.createElementNS(ns,tag); Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v)); return n; };

  svg.innerHTML = '';
  for (let i=0;i<=4;i++){ const yv=minY+(i/4)*(maxY-minY), yp=sy(yv); svg.appendChild(el('line',{x1:pL,y1:yp,x2:W-pR,y2:yp,stroke:'#334155','stroke-width':'0.5'})); const t=el('text',{x:pL-5,y:yp+3,fill:'#94a3b8','font-size':'8','text-anchor':'end'}); t.textContent=yv.toFixed(2); svg.appendChild(t); }
  ds.forEach(dv=>{ const t=el('text',{x:sx(dv),y:H-pB+12,fill:'#94a3b8','font-size':'8','text-anchor':'middle'}); t.textContent=dv.toFixed(1); svg.appendChild(t); });
  svg.appendChild(el('line',{x1:pL,y1:pT+pH,x2:W-pR,y2:pT+pH,stroke:'#64748b','stroke-width':'1'}));
  svg.appendChild(el('line',{x1:pL,y1:pT,x2:pL,y2:pT+pH,stroke:'#64748b','stroke-width':'1'}));
  if (ds.length>1) {
    svg.appendChild(el('polyline',{fill:'none',stroke:'#3b82f6','stroke-width':'2',points:ds.map((dv,i)=>`${sx(dv)},${sy(fs[i]??0.05)}`).join(' ')}));
    if (idxInf>=0 && idxInf<ds.length-1) svg.appendChild(el('line',{x1:sx(ds[idxInf]),y1:sy(fs[idxInf]),x2:sx(ds[idxInf+1]),y2:sy(fs[idxInf+1]),stroke:'#60a5fa','stroke-width':'3'}));
  }
  ds.forEach((dv,i)=>svg.appendChild(el('circle',{cx:sx(dv),cy:sy(fs[i]??0.05),r:'3.5',fill:'#3b82f6',stroke:'#0f172a','stroke-width':'1'})));
  const cx=sx(dCalc), cy=sy(fCalc);
  svg.appendChild(el('line',{x1:pL,y1:cy,x2:cx,y2:cy,stroke:'#f97316','stroke-width':'1','stroke-dasharray':'3,2'}));
  svg.appendChild(el('line',{x1:cx,y1:cy,x2:cx,y2:pT+pH,stroke:'#f97316','stroke-width':'1','stroke-dasharray':'3,2'}));
  svg.appendChild(el('circle',{cx,cy,r:'5',fill:'#f97316',stroke:'#fff','stroke-width':'1.5'}));
}

function aplicarModoUI() {
  document.querySelectorAll('.pro-only').forEach(e=>e.classList.toggle('hidden',!isProMode));
  const b = document.getElementById('badge-nivel-ativo'), p = document.getElementById('btn-modo-pro');
  b.innerText = isProMode ? 'Nível Pro' : 'Nível Básico';
  b.className = `text-[10px] font-bold uppercase px-2 py-0.5 rounded ${isProMode?'bg-purple-950 text-purple-300 border border-purple-500/70':'bg-slate-700 text-cyan-300 border border-slate-600'}`;
  p.innerText = isProMode ? '🔓 Sair do Pro' : '🔒 Aderir Nível Pro';
  document.getElementById('grid-esforcos-custos').className = `grid grid-cols-1 ${isProMode?'md:grid-cols-3':'md:grid-cols-2'} gap-2.5 shrink-0`;
  document.getElementById('lbl-btn-export').innerText = isProMode ? 'Exportar Proposta PDF' : 'Exportar PDF';
  if (!isProMode) { document.getElementById('radio-pdf-resumido').checked=true; hide('modal-comparacao'); hide('modal-resultado-comparacao'); }
}

function gerirModoPro() {
  if (isProMode) { isProMode=false; aplicarModoUI(); atualizarCalculo(); return; }
  hide('erro-pro-password'); document.getElementById('input-pro-password').value=''; show('modal-password-pro');
  setTimeout(()=>document.getElementById('input-pro-password').focus(),50);
}

function validarPasswordPro() {
  const v = document.getElementById('input-pro-password').value, err = document.getElementById('erro-pro-password');
  if (!PRO_PASSWORD) { err.innerText='Password Pro não configurada em st.secrets["PRO_PASSWORD"].'; show('erro-pro-password'); return; }
  if (v === PRO_PASSWORD) { isProMode=true; hide('modal-password-pro'); aplicarModoUI(); atualizarCalculo(); }
  else { err.innerText='Password incorreta.'; show('erro-pro-password'); }
}

function resetRapidoTudo() {
  ['f','vc','rpm-max'].forEach(k=>{if(locks[k])toggleLock(k);});
  document.getElementById('input-rpm-max').value=8000; vcPct=0; fPct=0;
  document.getElementById('vc-slider').value=0; document.getElementById('f-slider').value=0;
  document.getElementById('pecking-check').checked=false; hide('pecking-options');
  document.getElementById('pecking-unidade').value='xd'; document.getElementById('pecking-passo').value='3.0'; document.getElementById('pecking-retensao').value='5000';
  atualizarCalculo();
}

function toggleFullScreen() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(()=>{});
  else document.exitFullscreen?.();
}

function abrirModalComparacao() {
  if (!isProMode) return gerirModoPro();
  const sel = document.getElementById('comp-ferramenta'), prev = sel.value;
  sel.innerHTML = `<option value="__CLIENTE__">🛠️ Ferramenta do Cliente</option>` + Object.keys(dados).map(k=>`<option value="${k}">${dados[k].nome}</option>`).join('');
  sel.value = (prev && (prev==='__CLIENTE__'||dados[prev])) ? prev : '__CLIENTE__';
  onChangeFonteComparacao(); show('modal-comparacao');
}

function onChangeFonteComparacao() {
  const v = document.getElementById('comp-ferramenta').value, isCli = v==='__CLIENTE__';
  document.getElementById('comp-bloco-cliente').classList.toggle('hidden',!isCli);
  document.getElementById('comp-bloco-variante').classList.toggle('hidden',isCli);
  document.getElementById('btn-usar-comparada').classList.toggle('hidden',isCli);
  if (!isCli && dados[v]) {
    const sV = document.getElementById('comp-variante'), curV = getVarianteAtiva();
    sV.innerHTML = Object.keys(dados[v].variantes||{}).map(x=>`<option value="${x}" ${x===curV?'selected':''}>${x}</option>`).join('');
  }
  atualizarComparacao();
}

function toggleCorteInterrompido() {
  corteInterrompidoAtivo = !corteInterrompidoAtivo;
  document.getElementById('icone-corte-interrompido').innerText = corteInterrompidoAtivo ? '●' : '○';
  atualizarComparacao();
}

function calcCompSide(isCli, key, varKey, gEf, d, prof, qtd, ch, pOn, pUn, pInp, pRet, rpmMax) {
  const passoMm = pUn==='xd'?pInp*d:pInp, passos = Math.max(1,Math.ceil(prof/passoMm));
  const tFuro = vf => { let t = vf>0 ? ((prof+0.3*d)/vf)*60 : 0; if(pOn) t=(vf>0?(prof/vf)*60:0)+(passos*(prof/pRet))*60+(vf>0?((0.3*d)/vf)*60:0); return t; };
  if (isCli) {
    let vc = Math.max(1, parseFloat(document.getElementById('comp-cliente-vc').value)||70), f = Math.max(0.001, parseFloat(document.getElementById('comp-cliente-f').value)||0.02);
    let n = d>0 ? Math.round((vc*1000)/(Math.PI*d)) : 0;
    if (rpmMax>0 && n>rpmMax) { n=rpmMax; vc=(n*Math.PI*d)/1000; }
    const vf = Math.round(f*n), tf = tFuro(vf);
    return { nome: document.getElementById('comp-cliente-nome').value.trim()||'Ferramenta do Cliente', vc, f, n, vf, tf, tTot:(tf*qtd)/60, cMaq:tf*(ch/3600)*qtd, lim:Infinity };
  }
  const t = dados[key], gObj = t && resolverGrupo(t, gEf);
  if (!gObj) return null;
  const p = calcularPonto(t, gObj, d, refrigAtual, vcPct, fPct, rpmMax), tf = tFuro(p.vf);
  return { nome:`${t.nome} (${varKey})`, vc:p.vc, f:p.f, n:p.n, vf:p.vf, tf, tTot:(tf*qtd)/60, cMaq:tf*(ch/3600)*qtd, lim:(t.variantes?.[varKey]?.ratio||5)*d };
}

function custoVida(preco, vida, unid, afiQ, afiC, qtd, prof, fat) {
  const vEf = Math.max(1,vida)*fat, usos = 1+Math.max(0,afiQ);
  const vFuros = Math.max(1, unid==='metros' ? (vEf/Math.max(0.001,prof/1000))*usos : vEf*usos);
  const cFuro = ((preco||0)+Math.max(0,afiQ)*(afiC||0))/vFuros;
  return { vFuros, cFuro, cLote: cFuro*qtd };
}

function atualizarComparacao() {
  const bk=document.getElementById('broca').value, gEf=getGrupoEfetivo(), src=document.getElementById('comp-ferramenta').value, vk=document.getElementById('comp-variante').value;
  const d=parseFloat(document.getElementById('diametro').value)||12, prof=parseFloat(document.getElementById('profundidade').value)||31, qtd=parseInt(document.getElementById('qtd-furos').value,10)||50, ch=parseFloat(document.getElementById('custo-hora').value)||50;
  const rpmMax=locks['rpm-max']?(parseFloat(document.getElementById('input-rpm-max').value)||8000):0;
  const pOn=document.getElementById('pecking-check').checked, pUn=document.getElementById('pecking-unidade').value, pInp=parseFloat(document.getElementById('pecking-passo').value)||(pUn==='xd'?3:36), pRet=parseFloat(document.getElementById('pecking-retensao').value)||5000;

  const a = calcCompSide(false, bk, getVarianteAtiva(), gEf, d, prof, qtd, ch, pOn, pUn, pInp, pRet, rpmMax);
  const b = calcCompSide(src==='__CLIENTE__', src, vk, gEf, d, prof, qtd, ch, pOn, pUn, pInp, pRet, rpmMax);
  const av = document.getElementById('comp-aviso-grupo');
  if (!a || !b) { av.innerText='Selecione modelo e grupo válidos.'; show('comp-aviso-grupo'); return; }

  const fat = corteInterrompidoAtivo ? 0.7 : 1.0;
  const fa = custoVida(+document.getElementById('comp-preco-atual').value||0, +document.getElementById('comp-vida-atual').value||1, document.getElementById('comp-vida-unid-atual').value, +document.getElementById('comp-afi-qtd-atual').value||0, +document.getElementById('comp-afi-custo-atual').value||0, qtd, prof, fat);
  const fb = custoVida(+document.getElementById('comp-preco-alvo').value||0, +document.getElementById('comp-vida-alvo').value||1, document.getElementById('comp-vida-unid-alvo').value, +document.getElementById('comp-afi-qtd-alvo').value||0, +document.getElementById('comp-afi-custo-alvo').value||0, qtd, prof, fat);

  const totA = a.cMaq + fa.cLote, totB = b.cMaq + fb.cLote, dT = a.tTot - b.tTot, dC = totA - totB;
  document.getElementById('comp-th-atual').innerText = a.nome; document.getElementById('comp-th-alvo').innerText = b.nome;
  document.getElementById('comp-capacidade-texto').innerText = Math.abs(dT)<0.05 ? `Tempos equivalentes (${a.tTot.toFixed(1)} min).` : (dT>0 ? `MAPAL poupa ${dT.toFixed(1)} min no lote (${a.tTot.toFixed(1)} vs ${b.tTot.toFixed(1)} min).` : `Comparada é ${Math.abs(dT).toFixed(1)} min mais rápida no lote.`);

  const cFixA = a.cMaq/qtd + fa.cFuro, cFixB = b.cMaq/qtd + fb.cFuro, dFix = cFixB - cFixA, dInv = (+document.getElementById('comp-preco-atual').value||0) - (+document.getElementById('comp-preco-alvo').value||0);
  document.getElementById('comp-breakeven-texto').innerText = (dInv>0 && dFix>0) ? `MAPAL paga diferença aos ~${Math.ceil(dInv/dFix)} furos.` : (dC>0.01 ? `MAPAL mais económica no lote em ${dC.toFixed(2)} €.` : (dC<-0.01 ? `Comparada ${Math.abs(dC).toFixed(2)} € mais barata no lote.` : 'Custos empatados.'));

  const avisos = [];
  if (prof > a.lim) avisos.push(`Atual excede nominal (${a.lim.toFixed(1)} mm).`);
  if (src!=='__CLIENTE__' && prof > b.lim) avisos.push(`Comparada excede nominal (${b.lim.toFixed(1)} mm).`);
  if (corteInterrompidoAtivo) avisos.push('Corte interrompido: -30% vida.');
  av.innerText = avisos.join(' | '); av.classList.toggle('hidden', !avisos.length);

  window._ultimoComparativo = { nomeAtual:a.nome, nomeAlvo:b.nome, tempoTotalAtual:a.tTot, tempoTotalAlvo:b.tTot, custoTotalAtual:totA, custoTotalAlvo:totB, custoTotalFuroAtual:totA/qtd, custoTotalFuroAlvo:totB/qtd, diffTempoMin:dT, diffCustoTotal:dC };

  const df = (x,y,dec=1,u='') => `${(x-y)>0?'+':''}${(x-y).toFixed(dec)}${u}`;
  const rows = [
    ['Vc', `${a.vc.toFixed(0)} m/min`, `${b.vc.toFixed(0)} m/min`, df(a.vc,b.vc,0,' m/min')],
    ['Avanço f', a.f.toFixed(4), b.f.toFixed(4), df(a.f,b.f,4,'')],
    ['RPM (n)', `${a.n}`, `${b.n}`, df(a.n,b.n,0,' rpm')],
    ['Avanço vf', `${a.vf}`, `${b.vf}`, df(a.vf,b.vf,0,' mm/min')],
    ['Vida (c/ reaf.)', `${fa.vFuros.toFixed(0)} furos`, `${fb.vFuros.toFixed(0)} furos`, df(fa.vFuros,fb.vFuros,0,' furos')],
    ['Tempo / Furo', `${a.tf.toFixed(1)} s`, `${b.tf.toFixed(1)} s`, df(a.tf,b.tf,1,' s')],
    ['Tempo Total Lote', `${a.tTot.toFixed(1)} min`, `${b.tTot.toFixed(1)} min`, df(a.tTot,b.tTot,1,' min')],
    ['Custo Ferr. Lote', `${fa.cLote.toFixed(2)} €`, `${fb.cLote.toFixed(2)} €`, df(fa.cLote,fb.cLote,2,' €')],
    ['Custo Máq. Lote', `${a.cMaq.toFixed(2)} €`, `${b.cMaq.toFixed(2)} €`, df(a.cMaq,b.cMaq,2,' €')],
    ['Custo Total Lote', `<strong>${totA.toFixed(2)} €</strong>`, `<strong>${totB.toFixed(2)} €</strong>`, `<strong>${df(totA,totB,2,' €')}</strong>`]
  ];
  document.getElementById('comp-tabela-corpo').innerHTML = rows.map(r=>`<tr><td class="py-1.5 px-3 text-slate-300 font-medium">${r[0]}</td><td class="py-1.5 px-3 text-blue-300">${r[1]}</td><td class="py-1.5 px-3 text-emerald-300">${r[2]}</td><td class="py-1.5 px-3 text-amber-300">${r[3]}</td></tr>`).join('');
}

function abrirResultadoComparacao() { atualizarComparacao(); hide('modal-comparacao'); show('modal-resultado-comparacao'); }
function aplicarFerramentaComparada() {
  const k = document.getElementById('comp-ferramenta').value, v = document.getElementById('comp-variante').value;
  if (!k || k==='__CLIENTE__' || !dados[k]) return;
  linhaAtivaInterna = dados[k].linha; if (dados[k].categoria) document.getElementById('categoria').value = dados[k].categoria;
  atualizarFiltroBrocas(true); document.getElementById('broca').value = k; mudarBroca(v);
  hide('modal-resultado-comparacao'); hide('modal-comparacao');
}

function abrirModalPdfParametros() { hide('aviso-pdf-parametros'); show('modal-pdf-parametros'); }
function abrirModalExportacao() { show('modal-export'); }

function addFooterPages(doc, leftText) {
  const n = doc.internal.getNumberOfPages();
  for (let i=1; i<=n; i++) {
    doc.setPage(i); doc.setFont('helvetica','normal'); doc.setFontSize(8); doc.setTextColor(100,116,139);
    doc.text(leftText, 14, 290); doc.text(`Página ${i} de ${n}`, 196, 290, {align:'right'});
  }
}

function gerarPdfParametrosCorte() {
  if (!window.jspdf?.jsPDF) return alert('Biblioteca jsPDF não carregada.');
  const escopo = document.querySelector('input[name="escopo-pdf-parametros"]:checked')?.value || 'selecionados';
  const av = document.getElementById('aviso-pdf-parametros'), bk = document.getElementById('broca').value, gEf = getGrupoEfetivo();
  const d = parseFloat(document.getElementById('diametro').value)||12, rpmMax = parseFloat(document.getElementById('input-rpm-max').value)||8000;
  const t = bk && dados[bk], desig = referenciaAtivaObj?.specification || referenciaAtivaObj?.order_no || t?.nome || 'Ferramenta';
  const rows = [];

  if (t?.grupos) {
    const grps = escopo==='todos' ? (t.gruposList.length?t.gruposList:Object.keys(t.grupos)) : (gEf && resolverGrupo(t,gEf) ? [gEf] : []);
    if (!grps.length) { av.innerText='Selecione um grupo MMG ou escolha "Todos".'; return show('aviso-pdf-parametros'); }
    grps.forEach((gk, idx) => {
      const gObj = resolverGrupo(t, gk); if (!gObj) return;
      const p = calcularPonto(t, gObj, d, refrigAtual, vcPct, fPct, locks['rpm-max']?rpmMax:0);
      let f=p.f, vc=p.vc, n=p.n, vf=p.vf;
      if (escopo==='selecionados' && idx===0) {
        if (locks.f && +document.getElementById('input-f').value>0) f = +document.getElementById('input-f').value;
        if (locks.vc && +document.getElementById('input-vc').value>0) vc = +document.getElementById('input-vc').value;
        n = d>0 ? Math.round((vc*1000)/(Math.PI*d)) : 0;
        if (locks['rpm-max'] && rpmMax>0 && n>rpmMax) { n=rpmMax; vc=(n*Math.PI*d)/1000; }
        vf = Math.round(f*n);
      }
      rows.push([mmgMeta[gk]?.label ? `${gk} — ${mmgMeta[gk].label}` : (t.gruposNames[gk]||gk), fmtPt(d,2), String(Math.round(vc)), fmtPt(f,3), String(Math.round(n)), String(Math.round(vf))]);
    });
  } else {
    if (escopo==='todos') { av.innerText='Selecione um modelo de ferramenta.'; return show('aviso-pdf-parametros'); }
    rows.push([gEf?(gruposMmgMap[gEf]||gEf):'Material Selecionado', fmtPt(d,2), String(Math.round(+document.getElementById('input-vc').value||0)), fmtPt(+document.getElementById('input-f').value||0,3), document.getElementById('res-n').innerText, document.getElementById('res-vf').innerText]);
  }

  const doc = new window.jspdf.jsPDF({orientation:'portrait',unit:'mm',format:'a4'});
  doc.setFillColor(15,23,42); doc.rect(14,12,182,14,'F');
  doc.setTextColor(255,255,255); doc.setFont('helvetica','bold'); doc.setFontSize(13); doc.text('MAPAL',18,21);
  doc.setTextColor(15,23,42); doc.setFontSize(11); doc.text(`Parâmetros de corte ${desig}`,14,34);
  doc.setFontSize(9); doc.text(`Refrigeração: ${refrigAtual.toUpperCase()} | Ajuste VC: ${vcPct>=0?'+':''}${vcPct}% | Ajuste F: ${fPct>=0?'+':''}${fPct}%`,14,42);
  doc.autoTable({
    startY:47, head:[['Material','Ø','VC','F','RPM (n)','Avanço']], body:rows, theme:'grid',
    styles:{font:'helvetica',fontSize:8.5,cellPadding:2.2,textColor:[15,23,42]},
    headStyles:{fillColor:[30,41,59],textColor:[255,255,255]},
    columnStyles:{0:{cellWidth:82},1:{halign:'right',cellWidth:18},2:{halign:'right',cellWidth:16},3:{halign:'right',cellWidth:18},4:{halign:'right',cellWidth:22},5:{halign:'right',cellWidth:26}}
  });
  addFooterPages(doc, 'ÁLAMO — Bruno Pinto | Tlf.: 936959415');
  doc.save(`Parametros_Corte_${escopo==='todos'?'Todos':'Selecionados'}_${d.toFixed(1)}mm.pdf`);
  hide('modal-pdf-parametros');
}

function gerarPDF() {
  if (!window.jspdf?.jsPDF) return alert('Biblioteca jsPDF não carregada.');
  const tipo = isProMode ? (document.querySelector('input[name="tipo-relatorio"]:checked')?.value||'resumido') : 'resumido';
  const bk = document.getElementById('broca').value, gEf = getGrupoEfetivo();
  const d = parseFloat(document.getElementById('diametro').value)||12, prof = parseFloat(document.getElementById('profundidade').value)||31;
  const doc = new window.jspdf.jsPDF({orientation:'portrait',unit:'mm',format:'a4'});
  doc.setFillColor(15,23,42); doc.rect(0,0,210,30,'F');
  doc.setTextColor(255,255,255); doc.setFont('helvetica','bold'); doc.setFontSize(14); doc.text('PARÂMETROS DE CORTE MAPAL',14,14);
  doc.setFont('helvetica','normal'); doc.setFontSize(9); doc.setTextColor(148,163,184);
  doc.text(tipo==='completo'?'Proposta Técnico-Comercial Completa (Nível Pro)':'Ficha Técnica de Parâmetros de Corte (Nível Básico)',14,21);
  doc.text(`Data: ${new Date().toLocaleDateString('pt-PT')}`,196,14,{align:'right'});

  let y = 38; doc.setTextColor(15,23,42); doc.setFontSize(9.5);
  const lines = [
    `Modelo: ${bk&&dados[bk]?dados[bk].nome:'Sem modelo selecionado'} (${getVarianteAtiva()})`,
    `Grupo MMG: ${gEf?(gruposMmgMap[gEf]||gEf):'—'} | Refrigeração: ${fmtRefrig(refrigAtual)}`,
    `Ø: ${d.toFixed(2)} mm | Profundidade: ${prof.toFixed(1)} mm | Vc: ${document.getElementById('input-vc').value} m/min | f: ${Number(document.getElementById('input-f').value).toFixed(4)} mm/rot | RPM: ${document.getElementById('res-n').innerText} | vf: ${document.getElementById('res-vf').innerText} mm/min`,
    `Força Axial: ${document.getElementById('res-forca').innerText} (${document.getElementById('res-forca-kgf').innerText}) | Binário: ${document.getElementById('res-binario-card').innerText} | Potência: ${document.getElementById('val-gauge-pot').innerText}`
  ];
  if (tipo==='completo') lines.push(`Tempo Ciclo: ${document.getElementById('res-tempo-total').innerText} | Volume: ${document.getElementById('res-volume-total').innerText} | Limalha: ${document.getElementById('res-peso').innerText} | Sucata: ${document.getElementById('res-sucata-val').innerText} | Custo Maq.: ${document.getElementById('res-custo-total').innerText}`);
  if (isProMode && document.getElementById('comp-incluir-pdf').checked && window._ultimoComparativo) {
    const c = window._ultimoComparativo;
    lines.push(`Comparativo (${c.nomeAtual} vs ${c.nomeAlvo}): Tempo ${c.tempoTotalAtual.toFixed(1)} vs ${c.tempoTotalAlvo.toFixed(1)} min | Custo Lote ${c.custoTotalAtual.toFixed(2)} vs ${c.custoTotalAlvo.toFixed(2)} €`);
  }
  lines.forEach(l=>{ doc.text(l,14,y,{maxWidth:182}); y+=6; });

  const tRows = [...document.querySelectorAll('#tabela-ref tr')].map(tr=>[...tr.querySelectorAll('td')].map(td=>td.innerText)).filter(r=>r.length>=4);
  if (tRows.length && typeof doc.autoTable==='function') {
    doc.autoTable({ startY:y+4, head:[['Ø (mm)','f Cat.','RPM (n)','Avanço vf']], body:tRows, theme:'grid', styles:{fontSize:8.5}, headStyles:{fillColor:[30,41,59]} });
  }
  addFooterPages(doc, 'Created by Bruno Pinto | bruno.pinto@alamo-ferramentas.com | +351 936 959 415');
  doc.save(`MAPAL_${tipo==='completo'?'Proposta_Completa':'Ficha_Tecnica'}_${d.toFixed(1)}mm.pdf`);
  hide('modal-export');
}

carregarDados(); aplicarModoUI(); filtrarCatalogoCascata('init'); atualizarFiltroBrocas(false); atualizarPainelCotas(); atualizarCalculo();
</script>
</body>
</html>
"""

for k, v in payload.items():
    HTML = HTML.replace(k, v)

components.html(HTML, height=920, scrolling=False)