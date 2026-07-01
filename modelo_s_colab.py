"""
MODELO S — Google Colab
Cole cada bloco em uma célula separada e execute com Shift+Enter.
Autocontido: nenhuma instalação necessária (usa apenas stdlib Python).
"""

# ═══ CÉLULA 1 — Verificação do ambiente ═══
import sys, math, json, threading, urllib.request
from dataclasses import dataclass
from typing import NamedTuple, Optional, Dict, List, Tuple

print(f"Python {sys.version}")
assert sys.version_info >= (3, 8), "Precisa Python 3.8+"
print("✓ Ambiente OK")


# ═══ CÉLULA 2 — Coeficientes β do Modelo S ═══
BETA: Dict[str, float] = {
    "b0":  3.800,
    "M":   0.220,
    "lD":  0.150,
    "G":  -0.180,
    "TFR": 0.120,
    "E":   0.100,
    "C":   0.080,
    "I":   0.060,
    "P":   0.070,
    "S":   0.090,
    "lG":  0.080,
    "N":   0.050,
    "NL":  0.090,
    "EXM": 0.150,
    "EXS": 0.120,
    "TOT": 0.100,
    "GVC": 0.080,
    "EXC": 0.050,
    "CCO":-0.070,
    "IMD":-0.060,
}
print(f"✓ {len(BETA)} coeficientes  |  b0 = {BETA['b0']}")
print(f"  Soma |β| (sem b0) = {sum(abs(v) for k,v in BETA.items() if k!='b0'):.3f}")


# ═══ CÉLULA 3 — Estrutura PaisData ═══
@dataclass
class PaisData:
    """
    lD  = log10(densidade)  — pré-computado
    lG  = log10(commits)    — pré-computado
    TFR = filhos/mulher [1-4] — normalizado internamente
    E   = anos de escolaridade (ex: 7.8)
    """
    nome: str  = "País"
    ano:  int  = 2025
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

print("✓ PaisData definida")


# ═══ CÉLULA 4 — Funções do modelo ═══
def calcular_ss(d: PaisData, debug: bool = False) -> float:
    """Calcula SS ∈ [1.0, 6.0]."""
    tfr_contrib = 1.0 - (d.TFR - 1.0) / 3.0
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
        xvals = {
            "M": d.M, "lD": d.lD, "G": d.G, "TFR": tfr_contrib,
            "E": d.E, "C": d.C, "I": d.I, "P": d.P, "S": d.S,
            "lG": d.lG, "N": d.N, "NL": d.NL, "EXM": d.EXM,
            "EXS": d.EXS, "TOT": d.TOT, "GVC": d.GVC,
            "EXC": d.EXC, "CCO": d.CCO, "IMD": d.IMD,
        }
        acum = BETA["b0"]
        print(f"\n{'='*60}")
        print(f"  DEBUG SS — {d.nome} {d.ano}")
        print(f"{'='*60}")
        print(f"  {'var':<5} {'β':>7}  {'x':>8}  {'β×x':>8}  {'acum':>8}")
        print(f"  {'-'*54}")
        print(f"  {'b0':<5} {'':>7}  {'':>8}  {BETA['b0']:>+8.4f}  {acum:>8.4f}")
        for var, bx in termos.items():
            acum += bx
            print(f"  {var:<5} {BETA[var]:>+7.3f}  {xvals[var]:>8.4f}  {bx:>+8.4f}  {acum:>8.4f}")
        ss_bruto = BETA["b0"] + sum(termos.values())
        print(f"  {'-'*54}")
        print(f"  SS bruto = {ss_bruto:.4f}  →  clamp[1,6] = {round(max(1.0,min(6.0,ss_bruto)),4):.4f}")
    return round(max(1.0, min(6.0, BETA["b0"] + sum(termos.values()))), 4)


def classificar_ss(ss: float) -> Tuple[str, str]:
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


def projetar_pib(pib_t: float, ss_t: float, inflacao: float) -> float:
    return pib_t * (1 + 0.018 * ss_t) * (1 + inflacao)


class PontoProjecao(NamedTuple):
    ano: int; ss: float; pib: float; classificacao: str; risco: str


def projetar_cenario(dados: PaisData, horizonte: int = 5,
                     delta_ss_anual: float = 0.0) -> List[PontoProjecao]:
    resultado = []
    ss, pib = calcular_ss(dados), dados.pib
    for i in range(horizonte + 1):
        cls, risco = classificar_ss(ss)
        resultado.append(PontoProjecao(dados.ano+i, round(ss,4), round(pib,4), cls, risco))
        pib = projetar_pib(pib, ss, dados.inflacao)
        ss  = max(1.0, min(6.0, ss + delta_ss_anual))
    return resultado


def relatorio(dados: PaisData, horizonte: int = 5) -> str:
    L = 64
    ss, (cls, risco) = calcular_ss(dados), classificar_ss(calcular_ss(dados))
    base = projetar_cenario(dados, horizonte, 0.0)
    otim = projetar_cenario(dados, horizonte, +0.05)
    pess = projetar_cenario(dados, horizonte, -0.05)
    linhas = [
        "="*L,
        f"  MODELO S — {dados.nome} ({dados.ano})".center(L),
        "="*L,
        f"  SS Base         : {ss:.4f}",
        f"  Classificação   : {cls}",
        f"  Risco de Colapso: {risco}",
        f"  PIB atual (T$)  : {dados.pib:.3f}",
        "",
        "-"*L,
        "  PROJEÇÃO DE CENÁRIOS (3 trajetórias)".center(L),
        "-"*L,
        f"  {'Ano':<6} {'Base':>8} {'Otimista':>10} {'Pessimista':>12}  Classe (base)",
        "-"*L,
    ]
    for b, o, p in zip(base, otim, pess):
        linhas.append(f"  {b.ano:<6} {b.ss:>8.4f} {o.ss:>10.4f} {p.ss:>12.4f}  {b.classificacao}")
    linhas.append("="*L)
    return "\n".join(linhas)

print("✓ Funções do modelo prontas")


# ═══ CÉLULA 5 — Presets ═══
BRASIL_2025 = PaisData(
    nome="Brasil", ano=2025,
    M=0.65, lD=1.40, G=0.52, TFR=1.75, E=7.8,
    C=0.68, I=0.52, P=0.45, S=0.22, lG=1.1,
    N=0.18, NL=0.75, EXC=0.12, TOT=1.05, CCO=0.55,
    EXM=0.05, EXS=0.42, GVC=0.52, IMD=0.18,
    pib=2.1, inflacao=0.045,
)
ALEMANHA_2025 = PaisData(
    nome="Alemanha", ano=2025,
    M=0.88, lD=2.38, G=0.31, TFR=1.46, E=9.0,
    C=0.65, I=0.75, P=0.90, S=0.75, lG=2.8,
    N=0.55, NL=0.95, EXC=0.04, TOT=1.02, CCO=0.12,
    EXM=0.40, EXS=0.85, GVC=0.88, IMD=0.22,
    pib=4.4, inflacao=0.022,
)
VENEZUELA_2025 = PaisData(
    nome="Venezuela", ano=2025,
    M=0.18, lD=1.54, G=0.52, TFR=2.40, E=5.5,
    C=0.30, I=0.05, P=0.01, S=0.00, lG=0.08,
    N=0.00, NL=0.18, EXC=0.88, TOT=0.62, CCO=0.95,
    EXM=0.01, EXS=0.08, GVC=0.10, IMD=0.78,
    pib=0.09, inflacao=0.80,
)
print("✓ Presets criados")


# ═══ CÉLULA 6 — Debug SS linha a linha ═══
ss_br = calcular_ss(BRASIL_2025,    debug=True)
ss_de = calcular_ss(ALEMANHA_2025,  debug=True)
ss_ve = calcular_ss(VENEZUELA_2025, debug=True)


# ═══ CÉLULA 7 — Ranking ═══
print("\n" + "="*60)
print(f"  {'PAÍS':<12} {'SS':>7}  {'CLASSIFICAÇÃO':<16}  RISCO")
print("="*60)
for p, ss in sorted(
    [(BRASIL_2025,ss_br),(ALEMANHA_2025,ss_de),(VENEZUELA_2025,ss_ve)],
    key=lambda t: t[1], reverse=True
):
    cls, risco = classificar_ss(ss)
    print(f"  {p.nome:<12} {ss:>7.4f}  {cls:<16}  {risco}")
print("="*60)


# ═══ CÉLULA 8 — Relatório 3 cenários ═══
for preset in [BRASIL_2025, ALEMANHA_2025, VENEZUELA_2025]:
    print("\n" + relatorio(preset, horizonte=5))


# ═══ CÉLULA 9 — País personalizado (edite os valores) ═══
MEU_PAIS = PaisData(
    nome="Meu País", ano=2025,
    M=0.50, lD=math.log10(50), G=0.40, TFR=2.0, E=8.0,
    C=0.60, I=0.30, P=0.10, S=0.05, lG=math.log10(100_000),
    N=0.02, NL=0.60, EXC=0.20, TOT=1.00, CCO=0.30,
    EXM=0.15, EXS=0.50, GVC=0.40, IMD=0.30,
    pib=0.5, inflacao=0.06,
)
print(relatorio(MEU_PAIS, horizonte=5))


# ═══ CÉLULA 10 — Funções Banco Mundial (requer internet) ═══
WB_BASE = "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}?format=json&mrv=3&per_page=3"
INDICADORES_WB = {
    "density":"EN.POP.DNST", "gini":"SI.POV.GINI",
    "fertility":"SP.DYN.TFRT.IN", "schooling":"SE.SCH.LIFE",
    "imports":"NE.IMP.GNFS.ZS", "exports":"NE.EXP.GNFS.ZS",
    "manuf_exp":"TX.VAL.MANF.ZS.UN", "hitech":"TX.VAL.MRCH.HI.ZS",
    "gdp":"NY.GDP.MKTP.CD", "inflation":"FP.CPI.TOTL.ZG",
    "patents":"IP.PAT.RESD", "population":"SP.POP.TOTL",
    "urban":"SP.URB.TOTL.IN.ZS", "gni_pc":"NY.GNP.PCAP.CD",
    "tot":"TT.PRI.MRCH.XD.WD",
}
PAIS_ISO = {"brasil":"BRA","brazil":"BRA","alemanha":"DEU","germany":"DEU","venezuela":"VEN"}

def _wb_get(iso, indicator, timeout=10):
    try:
        req = urllib.request.Request(
            WB_BASE.format(iso=iso.upper(), ind=indicator),
            headers={"User-Agent":"ModeloS/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            p = json.loads(r.read().decode())
            if len(p)<2 or not p[1]: return None
            for rec in p[1]:
                if rec.get("value") is not None: return float(rec["value"])
    except Exception: pass
    return None

def _fetch_paralelo(iso):
    res={}; lock=threading.Lock()
    def _w(k,v):
        val=_wb_get(iso,v)
        with lock: res[k]=val
    ts=[threading.Thread(target=_w,args=(k,v),daemon=True) for k,v in INDICADORES_WB.items()]
    for t in ts: t.start()
    for t in ts: t.join(timeout=15)
    return res

def _mapear_wb(iso, nome_pais, d):
    def v(k,fb): return d[k] if d.get(k) is not None else fb
    gni=v("gni_pc",10000); den=v("density",50); gini=v("gini",40)
    urb=v("urban",60); pat=v("patents",0); pop=v("population",1e7)
    mf=v("manuf_exp",30); ex=v("exports",20); im=v("imports",20)
    hi=v("hitech",10); tot=v("tot",100); gdp=v("gdp",1e12); inf=v("inflation",3)
    return PaisData(
        nome=nome_pais, ano=2024,
        M=round(min(1,max(0,gni/80000)),4),
        lD=round(math.log10(max(den,0.1)),4),
        G=round(gini/100,4), TFR=round(v("fertility",2.),3),
        E=round(v("schooling",8.),2), C=round(min(1,urb/100),3),
        I=0.30, P=round(min(5,(pat/max(pop,1))*1e6),4),
        S=0.05, lG=1.0, N=0.02, NL=round(min(1,urb/100),3),
        EXM=round(min(1,(mf/100)*(ex/100)),4),
        EXS=round(min(1,hi/100),4), TOT=round(tot/100,3),
        GVC=round(min(1,(ex+im)/200),4), EXC=0.25, CCO=0.30,
        IMD=round(min(1,im/100),4),
        pib=round(gdp/1e12,3), inflacao=round(max(0,inf/100),4),
    )

def buscar_pais_wb(nome):
    iso=PAIS_ISO.get(nome.lower(),nome.upper()[:3])
    print(f"\n[WB] Buscando {nome.title()} (ISO={iso})...")
    raw=_fetch_paralelo(iso); dados=_mapear_wb(iso,nome.title(),raw)
    print(f"[WB] {sum(1 for v in raw.values() if v is not None)}/{len(INDICADORES_WB)} indicadores obtidos")
    return dados

print("✓ Funções Banco Mundial carregadas")


# ═══ CÉLULA 11 — SS em tempo real ═══
print("\n"+"="*64)
print("  SS EM TEMPO REAL — DADOS BANCO MUNDIAL".center(64))
print("="*64)
resultados_live=[]
for np in ["brasil","alemanha","venezuela"]:
    try:
        d=buscar_pais_wb(np); ss=calcular_ss(d); cls,risco=classificar_ss(ss)
        resultados_live.append((d,ss,cls,risco))
        print(f"\n  {d.nome} ({d.ano})")
        print(f"    PIB:       ${d.pib:.3f} T")
        print(f"    Inflação:   {d.inflacao*100:.1f}%")
        print(f"    Gini:       {d.G:.3f}")
        print(f"    TFR:        {d.TFR:.2f} filhos/mulher")
        print(f"    Escolar.:   {d.E:.1f} anos")
        print(f"    ► SS={ss:.4f}  {cls}  |  {risco}")
    except Exception as e:
        print(f"  ERRO {np}: {e}")
print("\n"+"="*64)
print(f"  {'PAÍS':<12} {'SS live':>8}  CLASSIFICAÇÃO")
print("="*64)
for d,ss,cls,_ in sorted(resultados_live,key=lambda t:t[1],reverse=True):
    print(f"  {d.nome:<12} {ss:>8.4f}  {cls}")
print("="*64)


# ═══ CÉLULA 12 — Testes de integridade ═══
print("\nTESTES DE INTEGRIDADE")
print("-"*44)
for nome,ss in [("Brasil",ss_br),("Alemanha",ss_de),("Venezuela",ss_ve)]:
    assert 1.0<=ss<=6.0, f"SS fora de [1,6]: {nome}={ss}"
    print(f"  ✓  {nome}: SS={ss:.4f} ∈ [1.0, 6.0]")
assert ss_de>=ss_br>=ss_ve
print(f"  ✓  Ordem: Alemanha ≥ Brasil ≥ Venezuela")
for ss_val,esp in [(1.5,"Crítico"),(2.2,"Alto"),(3.0,"Moderado"),
                   (4.0,"Estável"),(5.0,"Muito Estável"),(5.8,"Excelente")]:
    cls,_=classificar_ss(ss_val)
    assert cls==esp, f"SS={ss_val} → '{cls}' != '{esp}'"
    print(f"  ✓  SS={ss_val} → {cls}")
proj=projetar_cenario(BRASIL_2025,horizonte=5)
assert proj[-1].pib>proj[0].pib
print(f"  ✓  PIB Brasil 2025→2030: {proj[0].pib:.3f}T → {proj[-1].pib:.3f}T")
print("\n✓ Todos os testes passaram")
