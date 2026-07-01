"""
Busca dados em tempo real via World Bank API.
Funciona em Colab e no app Android (urllib puro, sem dependências extras).
"""

import json
import math
import threading
import urllib.request
import urllib.error
from typing import Optional, Callable, Dict

from modelo_s import PaisData

# ── Configuração ──────────────────────────────────────────────────────
WB_BASE = (
    "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}"
    "?format=json&mrv=3&per_page=3"
)

PAIS_ISO = {
    "brasil":    "BRA",
    "brazil":    "BRA",
    "alemanha":  "DEU",
    "germany":   "DEU",
    "venezuela": "VEN",
}

# Indicadores do Banco Mundial usados no modelo
INDICADORES = {
    "density":    "EN.POP.DNST",      # densidade hab/km²
    "gini":       "SI.POV.GINI",      # Gini 0-100
    "fertility":  "SP.DYN.TFRT.IN",   # filhos/mulher
    "schooling":  "SE.SCH.LIFE",      # anos escolaridade
    "imports":    "NE.IMP.GNFS.ZS",   # importações % PIB
    "exports":    "NE.EXP.GNFS.ZS",   # exportações % PIB
    "manuf_exp":  "TX.VAL.MANF.ZS.UN",# manufat. % merch exports
    "hitech":     "TX.VAL.MRCH.HI.ZS",# hi-tech % merch exports
    "gdp":        "NY.GDP.MKTP.CD",   # PIB USD corrente
    "inflation":  "FP.CPI.TOTL.ZG",   # inflação CPI %
    "patents":    "IP.PAT.RESD",      # patentes residentes
    "population": "SP.POP.TOTL",      # população total
    "urban":      "SP.URB.TOTL.IN.ZS",# % população urbana
    "savings":    "NY.GNS.ICTR.ZS",   # poupança bruta % PIB
    "invest":     "NE.GDI.TOTL.ZS",   # formação bruta capital % PIB
    "gni_pc":     "NY.GNP.PCAP.CD",   # RNB per capita USD
    "tot":        "TT.PRI.MRCH.XD.WD",# termos de troca (índice)
}


# ── Funções de busca ──────────────────────────────────────────────────

def _wb_get(iso: str, indicator: str, timeout: int = 10) -> Optional[float]:
    """Retorna o valor mais recente não-nulo de um indicador WB."""
    url = WB_BASE.format(iso=iso.upper(), ind=indicator)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ModeloS/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            if len(payload) < 2 or not payload[1]:
                return None
            for rec in payload[1]:
                if rec.get("value") is not None:
                    return float(rec["value"])
    except Exception:
        pass
    return None


def _fetch_todos(iso: str) -> Dict[str, Optional[float]]:
    """Busca todos os indicadores em threads paralelas."""
    resultados: Dict[str, Optional[float]] = {}
    lock = threading.Lock()

    def _worker(nome: str, ind: str):
        val = _wb_get(iso, ind)
        with lock:
            resultados[nome] = val

    threads = [
        threading.Thread(target=_worker, args=(nome, ind), daemon=True)
        for nome, ind in INDICADORES.items()
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    return resultados


def _mapear(iso: str, nome_pais: str, d: Dict[str, Optional[float]]) -> PaisData:
    """Converte dicionário de indicadores brutos em PaisData."""

    def v(key, fallback=None):
        val = d.get(key)
        return val if val is not None else fallback

    # M — mobilidade social: aproximado por RNB per capita / 80.000
    gni_pc  = v("gni_pc", 10_000)
    M_val   = min(1.0, max(0.0, gni_pc / 80_000))

    # lD — log10(densidade)
    density = v("density", 50.0)
    lD_val  = math.log10(max(density, 0.1))

    # G — Gini 0-1
    gini   = v("gini", 40.0)
    G_val  = gini / 100.0

    # TFR
    TFR_val = v("fertility", 2.0)

    # E — anos de escolaridade
    E_val = v("schooling", 8.0)

    # C — entropia cultural: % urbana como proxy
    urban  = v("urban", 60.0)
    C_val  = min(1.0, urban / 100.0)

    # I — imigração: padrão (sem indicador WB direto)
    I_val = 0.30

    # P — patentes per million
    patents = v("patents", 0.0)
    pop     = v("population", 1e7)
    P_val   = min(5.0, (patents / max(pop, 1)) * 1e6)

    # S — startups unicórnio: padrão
    S_val = 0.05

    # lG — GitHub commits (log10): padrão; sem API pública fácil
    lG_val = 1.0

    # N — Nobel per capita: padrão
    N_val = 0.02

    # NL — luz noturna: % urbana como proxy
    NL_val = min(1.0, urban / 100.0)

    # EXM — manufaturados/PIB  =  (manuf% de merch) × (exp% PIB) / 10000
    manuf  = v("manuf_exp", 30.0)
    exp_pct = v("exports", 20.0)
    EXM_val = min(1.0, (manuf / 100.0) * (exp_pct / 100.0))

    # EXS — sofisticação: hi-tech exports %
    hitech  = v("hitech", 10.0)
    EXS_val = min(1.0, hitech / 100.0)

    # TOT — termos de troca (índice WB; normalizado em torno de 1.0)
    tot_idx = v("tot", 100.0)
    TOT_val = tot_idx / 100.0

    # GVC — cadeias globais: (exp + imp) / 200 como proxy de abertura
    imp_pct = v("imports", 20.0)
    GVC_val = min(1.0, (exp_pct + imp_pct) / 200.0)

    # EXC — commodities: padrão
    EXC_val = 0.25

    # CCO — concentração: padrão
    CCO_val = 0.30

    # IMD — dependência importações
    IMD_val = min(1.0, imp_pct / 100.0)

    # PIB em trilhões USD
    gdp     = v("gdp", 1e12)
    pib_val = gdp / 1e12

    # Inflação
    inf_pct  = v("inflation", 3.0)
    inf_val  = max(0.0, inf_pct / 100.0)

    return PaisData(
        nome=nome_pais, ano=2024,
        M=round(M_val,  4), lD=round(lD_val,  4), G=round(G_val,   4),
        TFR=round(TFR_val, 3), E=round(E_val,  2),
        C=round(C_val,  3), I=round(I_val,  3),
        P=round(P_val,  4), S=round(S_val,  4), lG=round(lG_val, 4),
        N=round(N_val,  4), NL=round(NL_val, 3),
        EXM=round(EXM_val, 4), EXS=round(EXS_val, 4),
        TOT=round(TOT_val, 3), GVC=round(GVC_val,  4),
        EXC=round(EXC_val, 3), CCO=round(CCO_val,  3),
        IMD=round(IMD_val, 4),
        pib=round(pib_val, 3), inflacao=round(inf_val, 4),
    )


# ── API pública síncrona (Colab) ──────────────────────────────────────

def buscar_pais(nome: str) -> PaisData:
    """
    Busca dados em tempo real para o país e retorna um PaisData.
    Uso no Colab:
        dados = buscar_pais("brasil")
    """
    iso  = PAIS_ISO.get(nome.lower(), nome.upper()[:3])
    nome_titulo = nome.title()
    print(f"[fetch] Buscando {nome_titulo} (ISO={iso}) no Banco Mundial...")
    raw  = _fetch_todos(iso)
    dados = _mapear(iso, nome_titulo, raw)
    encontrados = sum(1 for v in raw.values() if v is not None)
    print(f"[fetch] {encontrados}/{len(INDICADORES)} indicadores obtidos.")
    return dados


# ── API assíncrona (Android/Kivy) ────────────────────────────────────

def buscar_pais_async(
    nome: str,
    on_success: Callable[[PaisData], None],
    on_error:   Callable[[str], None],
) -> None:
    """
    Busca em thread separada e chama callback na conclusão.
    Use on_success / on_error com Clock.schedule_once no Kivy.

    Exemplo:
        def _ok(dados):
            Clock.schedule_once(lambda dt: app.show_results(dados))
        def _err(msg):
            Clock.schedule_once(lambda dt: app.show_error(msg))
        buscar_pais_async("brasil", _ok, _err)
    """
    def _run():
        try:
            dados = buscar_pais(nome)
            on_success(dados)
        except Exception as exc:
            on_error(str(exc))

    threading.Thread(target=_run, daemon=True).start()
