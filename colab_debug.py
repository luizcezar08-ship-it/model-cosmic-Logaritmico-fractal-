"""
MODELO S — Debug Completo para Google Colab
Cole cada bloco em uma célula separada e execute em ordem (Shift+Enter).
"""

# =============================================================================
# CÉLULA 1 — Python OK
# =============================================================================
import sys, math
from dataclasses import dataclass
from typing import Dict, List, Tuple

print(f"Python {sys.version}")
assert sys.version_info >= (3, 8)
print("OK")


# =============================================================================
# CÉLULA 2 — Coeficientes β
# =============================================================================
BETA: Dict[str, float] = {
    "b0":   3.800,   # intercepto
    "M":    0.220,   # PIB per capita (normalizado)
    "lD":   0.150,   # densidade populacional (normalizado)
    "G":   -0.180,   # Gini 0-1
    "TFR":  0.120,   # fertilidade normalizada  (TFR-1)/3
    "E":    0.100,   # expectativa de vida (normalizada)
    "C":    0.080,   # consumo / PIB
    "I":    0.060,   # investimento / PIB
    "P":    0.070,   # produtividade 0-1
    "S":    0.090,   # poupança / PIB
    "lG":   0.080,   # inovação tecnológica (normalizado)
    "N":    0.050,   # capital natural / PIB
    "NL":   0.090,   # infra urbana 0-1
    "EXM":  0.150,   # export manufaturados / PIB
    "EXS":  0.120,   # sofisticação export 0-1
    "TOT":  0.100,   # termos de troca 0-1
    "GVC":  0.080,   # cadeias globais 0-1
    "EXC":  0.050,   # export commodities / PIB
    "CCO": -0.070,   # concentração commodities (negativo)
    "IMD": -0.060,   # dependência importações (negativo)
}
print(f"OK — {len(BETA)} coeficientes  |  b0={BETA['b0']}")
print(f"     soma |β| (excl. b0) = {sum(abs(v) for k,v in BETA.items() if k!='b0'):.3f}")


# =============================================================================
# CÉLULA 3 — Estrutura de dados (valores RAW — normalizações ficam no cálculo)
# =============================================================================
@dataclass
class PaisData:
    """
    Valores de entrada para um país.

    Variáveis em escala natural (serão normalizadas dentro de calcular_ss):
        M   — PIB per capita PPC em USD  (ex: 16500)
        lD  — Densidade em hab/km²       (ex: 25.4)
        E   — Expectativa de vida em anos (ex: 75.5)
        lG  — Commits GitHub (proxy inovação, ex: 2_800_000)

    Variáveis já em [0, 1]:
        G, TFR, C, I, P, S, N, NL, EXM, EXS, TOT, GVC, EXC, CCO, IMD
        TFR deve ser passado já normalizado: (taxa_fertilidade - 1) / 3
    """
    nome: str
    ano:  int
    # escala natural → normalizadas internamente
    M:    float = 0.0
    lD:   float = 0.0
    E:    float = 0.0
    lG:   float = 0.0
    # [0, 1]
    G:    float = 0.0
    TFR:  float = 0.0
    C:    float = 0.0
    I:    float = 0.0
    P:    float = 0.0
    S:    float = 0.0
    N:    float = 0.0
    NL:   float = 0.0
    EXM:  float = 0.0
    EXS:  float = 0.0
    TOT:  float = 0.0
    GVC:  float = 0.0
    EXC:  float = 0.0
    CCO:  float = 0.0
    IMD:  float = 0.0

print("OK — PaisData definida")


# =============================================================================
# CÉLULA 4 — Normalizações internas (aqui está o BUG corrigido)
# =============================================================================
# BUG ORIGINAL: E, M e lG eram usados diretamente sem normalizar.
#   E = 75.5 anos  →  β_E × E = 0.100 × 75.5 = +7.55  (dominava toda a fórmula!)
#   M = log10(16500) = 4.22  →  β_M × M = 0.220 × 4.22 = +0.93  (aceitável)
#   lG = log10(2.8M) = 6.45  →  β_lG × lG = 0.080 × 6.45 = +0.52  (grande demais)
#
# FIX: normalizar tudo para escala comparável antes de aplicar β.

def _norm_M(pib_pc_usd: float) -> float:
    """PIB per capita → [0,1]  (escala log, referência 100–1.000.000 USD)"""
    return (math.log10(max(pib_pc_usd, 1)) - 2) / 4      # log [2,6] → [0,1]

def _norm_lD(densidade: float) -> float:
    """Densidade hab/km² → [0,1]  (log, ref 1–10.000)"""
    return math.log10(max(densidade, 0.1)) / 4             # log [0,4] → [0,1]

def _norm_E(anos: float) -> float:
    """Expectativa de vida em anos → [0,1]  (ref 40–90 anos)"""
    return (anos - 40) / 50                                # 40→0, 90→1

def _norm_lG(commits: float) -> float:
    """Commits GitHub → [0,1]  (log, ref 1.000–1.000.000.000)"""
    return (math.log10(max(commits, 1)) - 3) / 6          # log [3,9] → [0,1]

# Teste das normalizações
print("Normalização — Brasil como exemplo:")
print(f"  M   PIB=16500 → {_norm_M(16500):.4f}   (esperado ~0.55)")
print(f"  lD  dens=25.4 → {_norm_lD(25.4):.4f}   (esperado ~0.35)")
print(f"  E   anos=75.5 → {_norm_E(75.5):.4f}   (esperado ~0.71)")
print(f"  lG  com=2.8M  → {_norm_lG(2_800_000):.4f}   (esperado ~0.57)")
print()
print("BUG ANTIGO — E sem normalizar:")
print(f"  β_E × 75.5 = {0.100 * 75.5:.3f}  ← causava SS = 13+ (clampado em 6)")
print(f"  β_E × {_norm_E(75.5):.3f} = {0.100 * _norm_E(75.5):.3f}  ← valor correto")


# =============================================================================
# CÉLULA 5 — Função de cálculo (com debug opcional)
# =============================================================================
def calcular_ss(p: PaisData, debug: bool = False) -> float:
    """
    SS = b0 + Σ βᵢ·xᵢ  clampado em [1, 6].
    Variáveis em escala natural (M, lD, E, lG) são normalizadas aqui.
    """
    x = {
        "M":   _norm_M(p.M),
        "lD":  _norm_lD(p.lD),
        "G":   p.G,
        "TFR": p.TFR,
        "E":   _norm_E(p.E),
        "C":   p.C,
        "I":   p.I,
        "P":   p.P,
        "S":   p.S,
        "lG":  _norm_lG(p.lG),
        "N":   p.N,
        "NL":  p.NL,
        "EXM": p.EXM,
        "EXS": p.EXS,
        "TOT": p.TOT,
        "GVC": p.GVC,
        "EXC": p.EXC,
        "CCO": p.CCO,
        "IMD": p.IMD,
    }

    total = BETA["b0"]
    if debug:
        print(f"\n{'='*56}")
        print(f"  SS DEBUG — {p.nome} {p.ano}")
        print(f"{'='*56}")
        print(f"  {'var':<5} {'β':>7}  {'x_norm':>8}  {'βx':>8}  {'acum':>8}")
        print(f"  {'-'*50}")
        print(f"  {'b0':<5} {'':>7}  {'':>8}  {BETA['b0']:>8.4f}  {total:>8.4f}")

    for var, val in x.items():
        parcela = BETA[var] * val
        total  += parcela
        if debug:
            print(f"  {var:<5} {BETA[var]:>+7.3f}  {val:>8.4f}  {parcela:>+8.4f}  {total:>8.4f}")

    ss = max(1.0, min(6.0, total))
    if debug:
        print(f"  {'-'*50}")
        print(f"  SS bruto={total:.4f}  →  clamp[1,6]={ss:.4f}")
    return ss


def classificar_ss(ss: float) -> Tuple[str, str]:
    """(classificação, cor_hex)"""
    if ss < 2.0:  return "Crítico",       "#E74C3C"
    if ss < 3.0:  return "Alto Risco",    "#E67E22"
    if ss < 4.0:  return "Moderado",      "#F1C40F"
    if ss < 5.0:  return "Estável",       "#2ECC71"
    if ss < 5.5:  return "Muito Estável", "#27AE60"
    return              "Excelente",      "#1ABC9C"

print("OK — calcular_ss e classificar_ss prontas")


# =============================================================================
# CÉLULA 6 — BRASIL 2025
# =============================================================================
BRASIL_2025 = PaisData(
    nome="Brasil", ano=2025,
    M   = 16_500,       # PIB pc PPC USD
    lD  = 25.4,         # hab/km²
    E   = 75.5,         # anos
    lG  = 2_800_000,    # commits GitHub
    G   = 0.530,
    TFR = (1.65 - 1) / 3,
    C   = 0.650,
    I   = 0.175,
    P   = 0.420,
    S   = 0.175,
    N   = 0.080,
    NL  = 0.620,
    EXM = 0.105,
    EXS = 0.420,
    TOT = 0.550,
    GVC = 0.350,
    EXC = 0.085,
    CCO = 0.520,
    IMD = 0.280,
)

ss_br = calcular_ss(BRASIL_2025, debug=True)
cls_br, cor_br = classificar_ss(ss_br)
print(f"\n  ► BRASIL: SS = {ss_br:.3f}  →  {cls_br}")


# =============================================================================
# CÉLULA 7 — ALEMANHA 2025
# =============================================================================
ALEMANHA_2025 = PaisData(
    nome="Alemanha", ano=2025,
    M   = 63_000,
    lD  = 234.0,
    E   = 81.2,
    lG  = 8_500_000,
    G   = 0.310,
    TFR = (1.46 - 1) / 3,
    C   = 0.530,
    I   = 0.220,
    P   = 0.720,
    S   = 0.290,
    N   = 0.040,
    NL  = 0.910,
    EXM = 0.280,
    EXS = 0.820,
    TOT = 0.580,
    GVC = 0.780,
    EXC = 0.020,
    CCO = 0.120,
    IMD = 0.320,
)

ss_de = calcular_ss(ALEMANHA_2025, debug=True)
cls_de, cor_de = classificar_ss(ss_de)
print(f"\n  ► ALEMANHA: SS = {ss_de:.3f}  →  {cls_de}")


# =============================================================================
# CÉLULA 8 — VENEZUELA 2025
# =============================================================================
VENEZUELA_2025 = PaisData(
    nome="Venezuela", ano=2025,
    M   = 4_200,
    lD  = 35.2,
    E   = 71.5,
    lG  = 180_000,
    G   = 0.440,
    TFR = (2.20 - 1) / 3,
    C   = 0.580,
    I   = 0.090,
    P   = 0.210,
    S   = 0.090,
    N   = 0.120,
    NL  = 0.510,
    EXM = 0.028,
    EXS = 0.150,
    TOT = 0.380,
    GVC = 0.100,
    EXC = 0.210,
    CCO = 0.880,
    IMD = 0.550,
)

ss_ve = calcular_ss(VENEZUELA_2025, debug=True)
cls_ve, cor_ve = classificar_ss(ss_ve)
print(f"\n  ► VENEZUELA: SS = {ss_ve:.3f}  →  {cls_ve}")


# =============================================================================
# CÉLULA 9 — Ranking comparativo
# =============================================================================
print("\n" + "="*58)
print(f"  {'PAÍS':<12} {'SS':>6}  {'CLASSIFICAÇÃO':<16}  {'COR'}")
print("="*58)
paises = [
    (ALEMANHA_2025, ss_de, cls_de, cor_de),
    (BRASIL_2025,   ss_br, cls_br, cor_br),
    (VENEZUELA_2025,ss_ve, cls_ve, cor_ve),
]
for p, ss, cls, cor in sorted(paises, key=lambda t: t[1], reverse=True):
    print(f"  {p.nome:<12} {ss:>6.3f}  {cls:<16}  {cor}")


# =============================================================================
# CÉLULA 10 — Projeção 5 anos
# =============================================================================
def projetar_cenario(pais: PaisData, anos: int = 5,
                     delta_ot=0.05, delta_base=0.02, delta_pe=-0.03) -> List[Dict]:
    ss0 = calcular_ss(pais)
    return [
        {"ano": pais.ano + t,
         "otimista":   round(min(6.0, ss0 + delta_ot   * t), 3),
         "base":       round(min(6.0, ss0 + delta_base  * t), 3),
         "pessimista": round(max(1.0, ss0 + delta_pe    * t), 3)}
        for t in range(1, anos + 1)
    ]

def projetar_pib(pib_usd: float, ss: float, inflacao=0.04, anos=5) -> List[float]:
    pibs = [pib_usd]
    for _ in range(anos):
        pibs.append(round(pibs[-1] * (1 + 0.018 * ss) * (1 + inflacao), 0))
    return pibs

print("PROJEÇÃO 5 ANOS — BRASIL")
proj = projetar_cenario(BRASIL_2025)
print(f"  {'ANO':<6} {'OTIMISTA':>10} {'BASE':>10} {'PESSIMISTA':>12}")
for row in proj:
    print(f"  {row['ano']:<6} {row['otimista']:>10.3f} {row['base']:>10.3f} {row['pessimista']:>12.3f}")

print()
pib_br = 2_100_000_000_000
pibs   = projetar_pib(pib_br, ss_br)
print("PROJEÇÃO PIB — BRASIL (USD trilhões)")
for i, pib in enumerate(pibs):
    print(f"  {2025+i}: {pib/1e12:.2f} T")


# =============================================================================
# CÉLULA 11 — Teste com país personalizado
# =============================================================================
MEU_PAIS = PaisData(
    nome="Meu País", ano=2025,
    # Edite os valores abaixo conforme o país que quiser analisar:
    M   = 10_000,    # PIB per capita PPC em USD
    lD  = 50.0,      # densidade hab/km²
    E   = 72.0,      # expectativa de vida (anos)
    lG  = 500_000,   # commits GitHub (proxy inovação tecnológica)
    G   = 0.40,      # índice de Gini
    TFR = (2.0-1)/3, # taxa de fertilidade (TFR-1)/3
    C   = 0.60,      # consumo / PIB
    I   = 0.20,      # investimento / PIB
    P   = 0.50,      # produtividade relativa [0-1]
    S   = 0.20,      # poupança / PIB
    N   = 0.10,      # capital natural / PIB
    NL  = 0.70,      # infraestrutura urbana [0-1]
    EXM = 0.15,      # export manufaturados / PIB
    EXS = 0.50,      # sofisticação das exportações [0-1]
    TOT = 0.50,      # termos de troca [0-1]
    GVC = 0.40,      # cadeias globais [0-1]
    EXC = 0.10,      # export commodities / PIB
    CCO = 0.30,      # concentração commodities [0-1]
    IMD = 0.30,      # dependência importações [0-1]
)

ss_meu = calcular_ss(MEU_PAIS, debug=True)
cls_meu, _ = classificar_ss(ss_meu)
print(f"\n  ► MEU PAÍS: SS = {ss_meu:.3f}  →  {cls_meu}")


# =============================================================================
# CÉLULA 12 — Verificação de integridade e testes automáticos
# =============================================================================
print("VERIFICAÇÃO DE INTEGRIDADE")
print("-"*40)

# 1. Todos os países dentro do intervalo
for nome, ss in [("Brasil", ss_br), ("Alemanha", ss_de), ("Venezuela", ss_ve)]:
    assert 1.0 <= ss <= 6.0, f"SS fora de [1,6]: {nome}={ss}"
    print(f"  OK  {nome}: SS={ss:.3f} ∈ [1, 6]")

# 2. Ordenação esperada: Alemanha > Brasil > Venezuela
assert ss_de > ss_br > ss_ve, \
    f"Ordem errada: DE={ss_de:.3f} BR={ss_br:.3f} VE={ss_ve:.3f}"
print(f"  OK  Ordenação correta: Alemanha > Brasil > Venezuela")

# 3. Normalizações ficam em [0, 1]
for func, val, nome in [
    (_norm_M,  16_500,     "M (Brasil)"),
    (_norm_lD, 25.4,       "lD (Brasil)"),
    (_norm_E,  75.5,       "E (Brasil)"),
    (_norm_lG, 2_800_000,  "lG (Brasil)"),
]:
    n = func(val)
    assert 0 <= n <= 1, f"Normalização fora de [0,1]: {nome}={n}"
    print(f"  OK  norm({nome}) = {n:.4f} ∈ [0, 1]")

# 4. Classificações corretas
for ss, esperado in [(1.5,"Crítico"), (2.5,"Alto Risco"), (3.5,"Moderado"),
                     (4.5,"Estável"), (5.2,"Muito Estável"), (5.8,"Excelente")]:
    cls, _ = classificar_ss(ss)
    assert cls == esperado, f"Classificação errada: SS={ss} → '{cls}' != '{esperado}'"
    print(f"  OK  SS={ss} → {cls}")

print()
print("✓ Todos os testes passaram")
print(f"  Brasil    SS={ss_br:.3f}")
print(f"  Alemanha  SS={ss_de:.3f}")
print(f"  Venezuela SS={ss_ve:.3f}")
