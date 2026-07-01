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
