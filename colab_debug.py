"""
MODELO S — Debug para Google Colab
Cole cada célula separadamente (Shift+Enter) para executar passo a passo.
Todos os valores e fórmulas espelham modelo_s.py do app Android.
"""

# =============================================================================
# CÉLULA 1 — Imports e versão Python
# =============================================================================
import sys, math
from dataclasses import dataclass
from typing import Dict, List, Tuple, NamedTuple

print(f"Python {sys.version}")
assert sys.version_info >= (3, 8), "Precisa Python 3.8+"
print("OK")


# =============================================================================
# CÉLULA 2 — Coeficientes β (idênticos ao modelo_s.py)
# =============================================================================
BETA: Dict[str, float] = {
    "b0":   3.800,
    "M":    0.220,   # mobilidade social [0-1]
    "lD":   0.150,   # log10(densidade hab/km²)
    "G":   -0.180,   # Gini [0-1]
    "TFR":  0.120,   # (1 - TFR_norm), onde TFR_norm = (TFR-1)/3
    "E":    0.100,   # escolaridade média em anos
    "C":    0.080,   # entropia cultural [0-1]
    "I":    0.060,   # imigração por HDI [0-1]
    "P":    0.070,   # patentes per capita
    "S":    0.090,   # startups unicórnio per capita
    "lG":   0.080,   # log10(commits GitHub)
    "N":    0.050,   # Nobel per capita
    "NL":   0.090,   # luz noturna [0-1]
    "EXM":  0.150,   # export manufaturados/PIB
    "EXS":  0.120,   # sofisticação exportações [0-1]
    "TOT":  0.100,   # termos de troca
    "GVC":  0.080,   # cadeias globais [0-1]
    "EXC":  0.050,   # export commodities/PIB
    "CCO": -0.070,   # concentração commodities (negativo)
    "IMD": -0.060,   # dependência importações (negativo)
}

print(f"OK — {len(BETA)} coeficientes  |  b0={BETA['b0']}")
print(f"     soma |β| (excl. b0) = {sum(abs(v) for k,v in BETA.items() if k!='b0'):.3f}")


# =============================================================================
# CÉLULA 3 — Estrutura de dados PaisData
# =============================================================================
@dataclass
class PaisData:
    """
    Variáveis de entrada para um país.

    Notas de escala:
      lD  — log10(densidade), pré-computado (ex: log10(25)≈1.40)
      lG  — log10(commits GitHub), pré-computado (ex: log10(100)≈2.0)
      E   — anos médios de escolaridade (ex: 7.8)
      TFR — taxa de fecundidade bruta [1-4]; normalizada internamente
      P, S, N — podem ser > 1 (per-capita com escala própria)
      TOT — termos de troca em torno de 1.0
    """
    nome: str = "País"
    ano:  int = 2025
    M:    float = 0.5
    lD:   float = 1.4
    G:    float = 0.4
    TFR:  float = 2.0
    E:    float = 8.0
    C:    float = 0.5
    I:    float = 0.3
    P:    float = 0.1
    S:    float = 0.05
    lG:   float = 1.0
    N:    float = 0.05
    NL:   float = 0.5
    EXC:  float = 0.3
    TOT:  float = 1.0
    CCO:  float = 0.3
    EXM:  float = 0.2
    EXS:  float = 0.5
    GVC:  float = 0.4
    IMD:  float = 0.3
    pib:      float = 1.0
    inflacao: float = 0.03

print("OK — PaisData definida")


# =============================================================================
# CÉLULA 4 — Fórmula principal com debug linha a linha
# =============================================================================
def calcular_ss(d: PaisData, debug: bool = False) -> float:
    """SS ∈ [1.0, 6.0]"""
    tfr_norm    = (d.TFR - 1.0) / 3.0
    tfr_contrib = 1.0 - tfr_norm

    termos = {
        "M":   BETA["M"]   * d.M,
        "lD":  BETA["lD"]  * d.lD,
        "G":   BETA["G"]   * d.G,
        "TFR": BETA["TFR"] * tfr_contrib,
        "E":   BETA["E"]   * d.E,
        "C":   BETA["C"]   * d.C,
        "I":   BETA["I"]   * d.I,
        "P":   BETA["P"]   * d.P,
        "S":   BETA["S"]   * d.S,
        "lG":  BETA["lG"]  * d.lG,
        "N":   BETA["N"]   * d.N,
        "NL":  BETA["NL"]  * d.NL,
        "EXM": BETA["EXM"] * d.EXM,
        "EXS": BETA["EXS"] * d.EXS,
        "TOT": BETA["TOT"] * d.TOT,
        "GVC": BETA["GVC"] * d.GVC,
        "EXC": BETA["EXC"] * d.EXC,
        "CCO": BETA["CCO"] * d.CCO,
        "IMD": BETA["IMD"] * d.IMD,
    }

    if debug:
        acum = BETA["b0"]
        print(f"\n{'='*58}")
        print(f"  DEBUG SS — {d.nome} {d.ano}")
        print(f"{'='*58}")
        print(f"  {'var':<5} {'β':>7}  {'x':>8}  {'β×x':>8}  {'acum':>8}")
        print(f"  {'-'*52}")
        print(f"  {'b0':<5} {'':>7}  {'':>8}  {BETA['b0']:>+8.4f}  {acum:>8.4f}")

        xvals = {
            "M": d.M, "lD": d.lD, "G": d.G, "TFR": tfr_contrib,
            "E": d.E, "C": d.C, "I": d.I, "P": d.P, "S": d.S,
            "lG": d.lG, "N": d.N, "NL": d.NL, "EXM": d.EXM,
            "EXS": d.EXS, "TOT": d.TOT, "GVC": d.GVC,
            "EXC": d.EXC, "CCO": d.CCO, "IMD": d.IMD,
        }
        for var, bx in termos.items():
            acum += bx
            print(f"  {var:<5} {BETA[var]:>+7.3f}  {xvals[var]:>8.4f}  {bx:>+8.4f}  {acum:>8.4f}")

        ss_bruto = BETA["b0"] + sum(termos.values())
        ss_final = round(max(1.0, min(6.0, ss_bruto)), 4)
        print(f"  {'-'*52}")
        print(f"  SS bruto = {ss_bruto:.4f}  →  clamp[1,6] = {ss_final:.4f}")

    return round(max(1.0, min(6.0, BETA["b0"] + sum(termos.values()))), 4)


def classificar_ss(ss: float) -> Tuple[str, str]:
    """(classificação, risco_de_colapso)"""
    for limite, cls, risco in [
        (2.0, "Crítico",       "Iminente (>80%)"),
        (2.5, "Alto",          "Alto (50-80%)"),
        (3.5, "Moderado",      "Médio (20-50%)"),
        (4.5, "Estável",       "Baixo (5-20%)"),
        (5.5, "Muito Estável", "Muito Baixo (<5%)"),
        (6.1, "Excelente",     "Negligenciável"),
    ]:
        if ss < limite:
            return cls, risco
    return "Excelente", "Negligenciável"

print("OK — calcular_ss e classificar_ss prontas")


# =============================================================================
# CÉLULA 5 — Presets (idênticos ao modelo_s.py do app)
# =============================================================================
BRASIL_2025 = PaisData(
    nome="Brasil", ano=2025,
    M=0.65, lD=1.40, G=0.52, TFR=1.75, E=7.8,
    C=0.68, I=0.52,
    P=0.45, S=0.22, lG=1.1,
    N=0.18, NL=0.75,
    EXC=0.12, TOT=1.05, CCO=0.55,
    EXM=0.05, EXS=0.42, GVC=0.52, IMD=0.18,
    pib=2.1, inflacao=0.045,
)

ALEMANHA_2025 = PaisData(
    nome="Alemanha", ano=2025,
    M=0.88, lD=2.38, G=0.31, TFR=1.46, E=9.0,
    C=0.65, I=0.75,
    P=0.90, S=0.75, lG=2.8,
    N=0.55, NL=0.95,
    EXC=0.04, TOT=1.02, CCO=0.12,
    EXM=0.40, EXS=0.85, GVC=0.88, IMD=0.22,
    pib=4.4, inflacao=0.022,
)

VENEZUELA_2025 = PaisData(
    nome="Venezuela", ano=2025,
    M=0.18, lD=1.54, G=0.52, TFR=2.40, E=5.5,
    C=0.30, I=0.05,
    P=0.01, S=0.00, lG=0.08,
    N=0.00, NL=0.18,
    EXC=0.88, TOT=0.62, CCO=0.95,
    EXM=0.01, EXS=0.08, GVC=0.10, IMD=0.78,
    pib=0.09, inflacao=0.80,
)

print("OK — presets Brasil, Alemanha, Venezuela criados")


# =============================================================================
# CÉLULA 6 — Calcular SS com debug linha a linha
# =============================================================================
ss_br = calcular_ss(BRASIL_2025,    debug=True)
ss_de = calcular_ss(ALEMANHA_2025,  debug=True)
ss_ve = calcular_ss(VENEZUELA_2025, debug=True)


# =============================================================================
# CÉLULA 7 — Ranking comparativo
# =============================================================================
print("\n" + "="*60)
print(f"  {'PAÍS':<12} {'SS':>6}  {'CLASSIFICAÇÃO':<14}  RISCO")
print("="*60)
for p, ss in sorted([
    (BRASIL_2025,    ss_br),
    (ALEMANHA_2025,  ss_de),
    (VENEZUELA_2025, ss_ve),
], key=lambda t: t[1], reverse=True):
    cls, risco = classificar_ss(ss)
    print(f"  {p.nome:<12} {ss:>6.4f}  {cls:<14}  {risco}")


# =============================================================================
# CÉLULA 8 — Projeção de cenários
# =============================================================================
class PontoProjecao(NamedTuple):
    ano: int
    ss: float
    pib: float
    classificacao: str
    risco: str


def projetar_pib(pib_t: float, ss_t: float, inflacao: float) -> float:
    return pib_t * (1 + 0.018 * ss_t) * (1 + inflacao)


def projetar_cenario(dados: PaisData, horizonte: int = 5,
                     delta_ss: float = 0.0) -> List[PontoProjecao]:
    ss  = calcular_ss(dados)
    pib = dados.pib
    resultado = []
    for i in range(horizonte + 1):
        cls, risco = classificar_ss(ss)
        resultado.append(PontoProjecao(dados.ano + i, round(ss, 4),
                                       round(pib, 4), cls, risco))
        pib = projetar_pib(pib, ss, dados.inflacao)
        ss  = max(1.0, min(6.0, ss + delta_ss))
    return resultado


print("PROJEÇÃO 5 ANOS — BRASIL")
print(f"  {'Ano':<6} {'SS':>7} {'PIB T$':>8} {'Classe'}")
for pt in projetar_cenario(BRASIL_2025, horizonte=5):
    print(f"  {pt.ano:<6} {pt.ss:>7.4f} {pt.pib:>8.3f}  {pt.classificacao}")


# =============================================================================
# CÉLULA 9 — País personalizado (edite os valores abaixo)
# =============================================================================
MEU_PAIS = PaisData(
    nome="Meu País", ano=2025,
    M=0.50,   # mobilidade social [0-1]
    lD=math.log10(50),    # log10(50 hab/km²) ≈ 1.70
    G=0.40,   # Gini
    TFR=2.0,  # taxa de fecundidade [1-4]
    E=8.0,    # anos de escolaridade
    C=0.60,   # entropia cultural
    I=0.30,   # imigração por HDI
    P=0.10,   # patentes per capita
    S=0.05,   # startups unicórnio p.c.
    lG=math.log10(100_000),  # log10(100 mil commits) ≈ 5.0
    N=0.02,   # Nobel per capita
    NL=0.60,  # luz noturna
    EXC=0.20, # export commodities/PIB
    TOT=1.00, # termos de troca
    CCO=0.30, # concentração commodities
    EXM=0.15, # export manufaturados/PIB
    EXS=0.50, # sofisticação exportações
    GVC=0.40, # cadeias globais
    IMD=0.30, # dependência importações
    pib=0.5,  # PIB em trilhões USD
    inflacao=0.06,
)

ss_meu = calcular_ss(MEU_PAIS, debug=True)
cls_meu, risco_meu = classificar_ss(ss_meu)
print(f"\n  ► {MEU_PAIS.nome}: SS={ss_meu:.4f}  {cls_meu}  |  {risco_meu}")


# =============================================================================
# CÉLULA 10 — Testes automáticos de integridade
# =============================================================================
print("\nTESTES DE INTEGRIDADE")
print("-"*40)

# 1. Clamp respeitado
for nome, ss in [("Brasil", ss_br), ("Alemanha", ss_de), ("Venezuela", ss_ve)]:
    assert 1.0 <= ss <= 6.0, f"SS fora de [1,6]: {nome}={ss}"
    print(f"  OK  {nome}: SS={ss:.4f} ∈ [1.0, 6.0]")

# 2. Ranking correto
assert ss_de >= ss_br >= ss_ve, \
    f"Ordem errada: DE={ss_de} BR={ss_br} VE={ss_ve}"
print(f"  OK  Ordenação: Alemanha ({ss_de}) ≥ Brasil ({ss_br}) ≥ Venezuela ({ss_ve})")

# 3. Classificações
for ss_val, esperado in [
    (1.5, "Crítico"), (2.2, "Alto"), (3.0, "Moderado"),
    (4.0, "Estável"), (5.0, "Muito Estável"), (5.8, "Excelente"),
]:
    cls, _ = classificar_ss(ss_val)
    assert cls == esperado, f"Classificação errada: SS={ss_val} → '{cls}' != '{esperado}'"
    print(f"  OK  SS={ss_val} → {cls}")

# 4. Projeção PIB cresce com SS positivo
proj_br = projetar_cenario(BRASIL_2025, horizonte=5)
assert proj_br[-1].pib > proj_br[0].pib, "PIB deveria crescer"
print(f"  OK  PIB Brasil 2025→2030: {proj_br[0].pib:.3f}T → {proj_br[-1].pib:.3f}T")

print()
print("✓ Todos os testes passaram")


# =============================================================================
# CÉLULA 11 — Busca em tempo real via Banco Mundial (requer internet no Colab)
# =============================================================================
# Instale apenas se ainda não tiver (urllib já vem no Python stdlib):
#   !pip install -q requests   ← NÃO necessário; usamos urllib puro

import json, math, threading, urllib.request
from typing import Optional, Dict

WB_BASE = (
    "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}"
    "?format=json&mrv=3&per_page=3"
)

INDICADORES_COLAB = {
    "density":    "EN.POP.DNST",
    "gini":       "SI.POV.GINI",
    "fertility":  "SP.DYN.TFRT.IN",
    "schooling":  "SE.SCH.LIFE",
    "imports":    "NE.IMP.GNFS.ZS",
    "exports":    "NE.EXP.GNFS.ZS",
    "manuf_exp":  "TX.VAL.MANF.ZS.UN",
    "hitech":     "TX.VAL.MRCH.HI.ZS",
    "gdp":        "NY.GDP.MKTP.CD",
    "inflation":  "FP.CPI.TOTL.ZG",
    "patents":    "IP.PAT.RESD",
    "population": "SP.POP.TOTL",
    "urban":      "SP.URB.TOTL.IN.ZS",
    "gni_pc":     "NY.GNP.PCAP.CD",
    "tot":        "TT.PRI.MRCH.XD.WD",
}

PAIS_ISO_COLAB = {
    "brasil": "BRA", "brazil": "BRA",
    "alemanha": "DEU", "germany": "DEU",
    "venezuela": "VEN",
}


def _wb_get_colab(iso: str, indicator: str, timeout: int = 10) -> Optional[float]:
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


def _fetch_todos_colab(iso: str) -> Dict[str, Optional[float]]:
    resultados: Dict[str, Optional[float]] = {}
    lock = threading.Lock()

    def _worker(nome, ind):
        val = _wb_get_colab(iso, ind)
        with lock:
            resultados[nome] = val

    threads = [threading.Thread(target=_worker, args=(k, v), daemon=True)
               for k, v in INDICADORES_COLAB.items()]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)
    return resultados


def _mapear_colab(iso: str, nome_pais: str, d: Dict[str, Optional[float]]) -> PaisData:
    def v(key, fallback=None):
        val = d.get(key)
        return val if val is not None else fallback

    gni_pc   = v("gni_pc",   10_000)
    density  = v("density",  50.0)
    gini     = v("gini",     40.0)
    urban    = v("urban",    60.0)
    patents  = v("patents",  0.0)
    pop      = v("population", 1e7)
    manuf    = v("manuf_exp", 30.0)
    exp_pct  = v("exports",  20.0)
    imp_pct  = v("imports",  20.0)
    hitech   = v("hitech",   10.0)
    tot_idx  = v("tot",      100.0)
    gdp      = v("gdp",      1e12)
    inf_pct  = v("inflation", 3.0)

    return PaisData(
        nome=nome_pais, ano=2024,
        M=round(min(1.0, max(0.0, gni_pc / 80_000)), 4),
        lD=round(math.log10(max(density, 0.1)), 4),
        G=round(gini / 100.0, 4),
        TFR=round(v("fertility", 2.0), 3),
        E=round(v("schooling", 8.0), 2),
        C=round(min(1.0, urban / 100.0), 3),
        I=0.30,
        P=round(min(5.0, (patents / max(pop, 1)) * 1e6), 4),
        S=0.05, lG=1.0, N=0.02,
        NL=round(min(1.0, urban / 100.0), 3),
        EXM=round(min(1.0, (manuf / 100.0) * (exp_pct / 100.0)), 4),
        EXS=round(min(1.0, hitech / 100.0), 4),
        TOT=round(tot_idx / 100.0, 3),
        GVC=round(min(1.0, (exp_pct + imp_pct) / 200.0), 4),
        EXC=0.25, CCO=0.30,
        IMD=round(min(1.0, imp_pct / 100.0), 4),
        pib=round(gdp / 1e12, 3),
        inflacao=round(max(0.0, inf_pct / 100.0), 4),
    )


def buscar_pais_colab(nome: str) -> PaisData:
    iso = PAIS_ISO_COLAB.get(nome.lower(), nome.upper()[:3])
    print(f"\n[WB] Buscando {nome.title()} (ISO={iso})...")
    raw = _fetch_todos_colab(iso)
    dados = _mapear_colab(iso, nome.title(), raw)
    ok = sum(1 for val in raw.values() if val is not None)
    print(f"[WB] {ok}/{len(INDICADORES_COLAB)} indicadores obtidos")
    return dados


print("OK — funções de busca em tempo real carregadas")
print("     Rode a CÉLULA 12 para buscar e calcular o SS ao vivo.")


# =============================================================================
# CÉLULA 12 — Calcular SS com dados ao vivo do Banco Mundial
# =============================================================================
print("\n" + "="*60)
print("  SS EM TEMPO REAL — BANCO MUNDIAL")
print("="*60)

paises_live = ["brasil", "alemanha", "venezuela"]
resultados_live = []

for nome in paises_live:
    try:
        dados_live = buscar_pais_colab(nome)
        ss_live    = calcular_ss(dados_live)
        cls_live, risco_live = classificar_ss(ss_live)
        resultados_live.append((dados_live, ss_live, cls_live, risco_live))
        print(f"\n  {dados_live.nome} ({dados_live.ano})")
        print(f"    PIB:      ${dados_live.pib:.2f} T")
        print(f"    Inflação: {dados_live.inflacao*100:.1f}%")
        print(f"    Gini:     {dados_live.G:.3f}")
        print(f"    TFR:      {dados_live.TFR:.2f}")
        print(f"    Escola:   {dados_live.E:.1f} anos")
        print(f"    ► SS = {ss_live:.4f}  |  {cls_live}  |  {risco_live}")
    except Exception as exc:
        print(f"  ERRO ao buscar {nome}: {exc}")

print("\n" + "="*60)
print(f"  {'PAÍS':<12} {'SS (live)':>10}  {'CLASSE'}")
print("="*60)
for dados_live, ss_live, cls_live, _ in sorted(resultados_live,
                                                key=lambda t: t[1], reverse=True):
    print(f"  {dados_live.nome:<12} {ss_live:>10.4f}  {cls_live}")
print("="*60)
