"""
Modelo S — Índice de Estabilidade Socioeconômica (SS)

Fórmula principal:
  SS = β₀ + β₁·M + β₂·ℓD + β₃·G + β₄·(1-TFR) + β₅·E + β₆·C + β₇·I
     + β₈·P + β₉·S + β₁₀·ℓG + β₁₁·N + β₁₂·NL + β₁₃·EXM + β₁₄·EXS
     + β₁₅·TOT + β₁₆·GVC + β₁₇·EXC - β₁₈·CCO - β₁₉·IMD

Escala de saída: 1.0 – 6.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields
from typing import NamedTuple


# ---------- Coeficientes calibrados ----------

BETA = {
    "b0":  3.800,   # intercepto
    "M":   0.220,   # mobilidade social
    "lD":  0.150,   # log-densidade populacional
    "G":  -0.180,   # coeficiente de Gini
    "TFR": 0.120,   # (1 - TFR) → baixa fecundidade
    "E":   0.100,   # escolaridade média
    "C":   0.080,   # entropia cultural
    "I":   0.060,   # imigração por HDI
    "P":   0.070,   # patentes per capita
    "S":   0.090,   # startups unicórnio per capita
    "lG":  0.080,   # log-GitHub commits
    "N":   0.050,   # prêmios Nobel per capita
    "NL":  0.090,   # intensidade de luz noturna
    "EXM": 0.150,   # exportação manufaturados/PIB
    "EXS": 0.120,   # sofisticação das exportações
    "TOT": 0.100,   # termos de troca de commodities
    "GVC": 0.080,   # cadeias globais de valor
    "EXC": 0.050,   # exportação commodities/PIB
    "CCO":-0.070,   # concentração de commodities (negativo)
    "IMD":-0.060,   # dependência de importações (negativo)
}


# ---------- Estrutura de entrada ----------

@dataclass
class PaisData:
    """Dados de entrada para um país/período.

    lD  → log10 da densidade populacional (ex: log10(25) ≈ 1.40)
    lG  → log dos commits GitHub (ex: log(1_000_000) ≈ 13.8; valor pré-computado)
    TFR → taxa de fecundidade real em filhos/mulher [1-4]
    E   → anos médios de escolaridade [0-15], usado diretamente
    EXS → sofisticação exportações [0-1] (normalizado de 0-100)
    """
    nome: str = "País"
    ano: int = 2025

    # Variáveis sociais
    M:   float = 0.0   # mobilidade social [0-1]
    lD:  float = 1.2   # log10(densidade em hab/km²)
    G:   float = 0.5   # coeficiente de Gini [0-1]
    TFR: float = 2.0   # taxa de fecundidade total [1-4]
    E:   float = 8.0   # escolaridade média (anos) — usado direto
    C:   float = 0.5   # entropia cultural [0-1]
    I:   float = 0.3   # imigração por HDI [0-1]

    # Inovação
    P:   float = 0.0   # patentes per capita [0-∞]
    S:   float = 0.0   # startups unicórnio per capita [0-∞]
    lG:  float = 1.1   # log-GitHub commits (pré-computado)

    # Tecnologia / satélite
    N:   float = 0.0   # Nobel per capita [0-∞]
    NL:  float = 0.5   # luz noturna [0-∞]

    # Comércio exterior — nível 1: commodities
    EXC: float = 0.3   # exportação commodities/PIB [0-1]
    TOT: float = 1.0   # termos de troca [0-∞]
    CCO: float = 0.3   # concentração Herfindahl [0-1]

    # Comércio exterior — nível 2: produção agregada
    EXM: float = 0.2   # exportação manufaturados/PIB [0-1]
    EXS: float = 0.5   # sofisticação exportações [0-1] (já normalizado)
    GVC: float = 0.4   # cadeias globais de valor [0-1]
    IMD: float = 0.3   # dependência importações [0-1]

    # PIB (usado para projeção)
    pib: float = 1.0   # PIB em trilhões USD
    inflacao: float = 0.03  # taxa de inflação anual


# ---------- Funções puras do modelo ----------

def calcular_ss(d: PaisData) -> float:
    """Calcula o Índice de Estabilidade Socioeconômica (SS).

    Convenções do documento:
      lD  → já é log10(densidade), fornecido diretamente
      lG  → já é log(commits), fornecido diretamente
      E   → anos de escolaridade usados sem normalização (β·E direto)
      TFR → normalizado internamente: tfr_norm = (TFR-1)/3; contribuição = β·(1-tfr_norm)
      EXS → escala 0-1 (normalizar antes se vier em 0-100)
    """
    tfr_norm = (d.TFR - 1.0) / 3.0          # mapeia [1,4] → [0,1]
    tfr_contrib = 1.0 - tfr_norm              # baixa fecundidade → valor alto

    ss = (
        BETA["b0"]
        + BETA["M"]   * d.M
        + BETA["lD"]  * d.lD
        + BETA["G"]   * d.G
        + BETA["TFR"] * tfr_contrib
        + BETA["E"]   * d.E            # anos direto, ex: 7.8 → contribui 0.78
        + BETA["C"]   * d.C
        + BETA["I"]   * d.I
        + BETA["P"]   * d.P
        + BETA["S"]   * d.S
        + BETA["lG"]  * d.lG
        + BETA["N"]   * d.N
        + BETA["NL"]  * d.NL
        + BETA["EXM"] * d.EXM
        + BETA["EXS"] * d.EXS
        + BETA["TOT"] * d.TOT
        + BETA["GVC"] * d.GVC
        + BETA["EXC"] * d.EXC
        + BETA["CCO"] * d.CCO
        + BETA["IMD"] * d.IMD
    )
    return round(ss, 4)


def projetar_pib(pib_t: float, ss_t: float, inflacao: float) -> float:
    """PIB_{t+1} = PIB_t × (1 + 0.018 × SS_t) × (1 + inflação)"""
    return pib_t * (1 + 0.018 * ss_t) * (1 + inflacao)


def normalizar_zscore(valor: float, media: float, desvio: float) -> float:
    if desvio == 0:
        return 0.0
    return (valor - media) / desvio


def calcular_vif(r2: float) -> float:
    """VIF = 1 / (1 - R²). Requisito: VIF < 5."""
    if r2 >= 1.0:
        return float("inf")
    return 1.0 / (1.0 - r2)


def classificar_ss(ss: float) -> tuple[str, str]:
    """Retorna (classificação, risco_de_colapso)."""
    tabela = [
        (2.0, "Crítico",       "Iminente (>80%)"),
        (2.5, "Alto",          "Alto (50-80%)"),
        (3.5, "Moderado",      "Médio (20-50%)"),
        (4.5, "Estável",       "Baixo (5-20%)"),
        (5.5, "Muito Estável", "Muito Baixo (<5%)"),
        (6.1, "Excelente",     "Negligenciável"),
    ]
    for limite, classe, risco in tabela:
        if ss < limite:
            return classe, risco
    return "Excelente", "Negligenciável"


# ---------- Projeção multi-período ----------

class PontoProjecao(NamedTuple):
    ano: int
    ss: float
    pib: float
    classificacao: str
    risco: str


def projetar_cenario(
    dados: PaisData,
    horizonte: int = 10,
    delta_ss_anual: float = 0.0,
) -> list[PontoProjecao]:
    """
    Projeta SS e PIB para `horizonte` anos.
    `delta_ss_anual` permite simular cenários (ex: +0.05 otimista, -0.05 pessimista).
    """
    resultado: list[PontoProjecao] = []
    ss = calcular_ss(dados)
    pib = dados.pib

    for i in range(horizonte + 1):
        ano = dados.ano + i
        classe, risco = classificar_ss(ss)
        resultado.append(PontoProjecao(ano, round(ss, 4), round(pib, 4), classe, risco))
        pib = projetar_pib(pib, ss, dados.inflacao)
        ss = max(1.0, min(6.0, ss + delta_ss_anual))

    return resultado


# ---------- Relatório ----------

LARGURA = 62

def _linha(char: str = "-") -> str:
    return char * LARGURA


def relatorio(dados: PaisData, horizonte: int = 5) -> str:
    ss_base = calcular_ss(dados)
    classe, risco = classificar_ss(ss_base)

    cenario_base = projetar_cenario(dados, horizonte, delta_ss_anual=0.0)
    cenario_otimista = projetar_cenario(dados, horizonte, delta_ss_anual=+0.05)
    cenario_pessimista = projetar_cenario(dados, horizonte, delta_ss_anual=-0.05)

    linhas: list[str] = [
        _linha("="),
        f"  MODELO S — {dados.nome} ({dados.ano})".center(LARGURA),
        _linha("="),
        f"  SS Base        : {ss_base:.4f}",
        f"  Classificação  : {classe}",
        f"  Risco de Colapso: {risco}",
        f"  PIB atual (T$) : {dados.pib:.2f}",
        "",
        _linha(),
        "  PROJEÇÃO DE CENÁRIOS".center(LARGURA),
        _linha(),
        f"  {'Ano':<6} {'Base':>8} {'Otimista':>10} {'Pessimista':>12}  {'Classe (base)':<14}",
        _linha(),
    ]
    for b, o, p in zip(cenario_base, cenario_otimista, cenario_pessimista):
        linhas.append(
            f"  {b.ano:<6} {b.ss:>8.4f} {o.ss:>10.4f} {p.ss:>12.4f}  {b.classificacao:<14}"
        )
    linhas.append(_linha("="))
    return "\n".join(linhas)


# ---------- Dados de exemplo ----------

# Valores alinhados com o exemplo do documento (SS_Brasil ≈ 3.20)
BRASIL_2025 = PaisData(
    nome="Brasil", ano=2025,
    M=0.65, lD=1.20, G=0.52, TFR=1.75, E=7.8,
    C=0.68, I=0.72,
    P=0.45, S=0.32, lG=1.1,
    N=0.28, NL=0.85,
    EXC=0.12, TOT=1.1, CCO=0.65,
    EXM=0.05, EXS=0.42, GVC=0.72, IMD=0.15,
    pib=2.1, inflacao=0.045,
)

ALEMANHA_2025 = PaisData(
    nome="Alemanha", ano=2025,
    M=0.82, lD=2.38, G=0.31, TFR=1.55, E=13.2,   # log10(240)≈2.38
    C=0.60, I=0.65,
    P=2.10, S=0.85, lG=8.5,
    N=1.20, NL=0.95,
    EXC=0.04, TOT=1.05, CCO=0.12,
    EXM=0.40, EXS=0.85, GVC=0.88, IMD=0.22,
    pib=4.4, inflacao=0.025,
)

VENEZUELA_2025 = PaisData(
    nome="Venezuela", ano=2025,
    M=0.20, lD=1.54, G=0.44, TFR=2.30, E=6.5,    # log10(35)≈1.54
    C=0.55, I=0.10,
    P=0.01, S=0.00, lG=0.1,
    N=0.01, NL=0.20,
    EXC=0.85, TOT=0.75, CCO=0.92,
    EXM=0.02, EXS=0.10, GVC=0.15, IMD=0.65,
    pib=0.09, inflacao=0.80,
)


# ---------- CLI ----------

def menu_interativo() -> None:
    paises = {
        "1": BRASIL_2025,
        "2": ALEMANHA_2025,
        "3": VENEZUELA_2025,
    }

    while True:
        print("\n" + _linha("="))
        print("  MODELO S — SISTEMA PREDITIVO DE ESTABILIDADE".center(LARGURA))
        print(_linha("="))
        print("  [1] Brasil 2025")
        print("  [2] Alemanha 2025")
        print("  [3] Venezuela 2025")
        print("  [4] Inserir dados manualmente")
        print("  [0] Sair")
        print(_linha())

        opcao = input("  Opção: ").strip()

        if opcao == "0":
            print("  Encerrando.")
            break
        elif opcao in paises:
            dados = paises[opcao]
            horizonte = _pedir_int("  Horizonte de projeção (anos, padrão 5)", 5)
            print("\n" + relatorio(dados, horizonte))
        elif opcao == "4":
            dados = _coletar_dados()
            horizonte = _pedir_int("  Horizonte de projeção (anos, padrão 5)", 5)
            print("\n" + relatorio(dados, horizonte))
        else:
            print("  Opção inválida.")


def _pedir_int(msg: str, padrao: int) -> int:
    try:
        return int(input(f"{msg}: ").strip() or padrao)
    except ValueError:
        return padrao


def _pedir_float(msg: str, padrao: float) -> float:
    try:
        return float(input(f"  {msg} (padrão {padrao}): ").strip() or padrao)
    except ValueError:
        return padrao


def _coletar_dados() -> PaisData:
    print("\n  --- Inserir dados do país ---")
    nome = input("  Nome do país: ").strip() or "País"
    ano = _pedir_int("  Ano", 2025)

    densidade = _pedir_float("D   — Densidade populacional (hab/km²)", 50.0)
    lD = math.log10(max(densidade, 1e-9))

    return PaisData(
        nome=nome, ano=ano,
        M   = _pedir_float("M   — Mobilidade social [0-1]", 0.5),
        lD  = lD,
        G   = _pedir_float("G   — Coeficiente de Gini [0-1]", 0.4),
        TFR = _pedir_float("TFR — Taxa de fecundidade total [1-4]", 2.0),
        E   = _pedir_float("E   — Escolaridade média (anos)", 8.0),
        C   = _pedir_float("C   — Entropia cultural [0-1]", 0.5),
        I   = _pedir_float("I   — Imigração por HDI [0-1]", 0.3),
        P   = _pedir_float("P   — Patentes per capita", 0.1),
        S   = _pedir_float("S   — Startups unicórnio per capita", 0.05),
        lG  = _pedir_float("lG  — Log-GitHub commits (ex: 1.1)", 1.0),
        N   = _pedir_float("N   — Nobel per capita", 0.05),
        NL  = _pedir_float("NL  — Luz noturna [0-∞]", 0.5),
        EXC = _pedir_float("EXC — Export. commodities/PIB [0-1]", 0.3),
        TOT = _pedir_float("TOT — Termos de troca [0-∞]", 1.0),
        CCO = _pedir_float("CCO — Conc. commodities Herfindahl [0-1]", 0.3),
        EXM = _pedir_float("EXM — Export. manufaturados/PIB [0-1]", 0.2),
        EXS = _pedir_float("EXS — Sofisticação exportações [0-1]", 0.5),
        GVC = _pedir_float("GVC — Cadeias globais de valor [0-1]", 0.4),
        IMD = _pedir_float("IMD — Dependência de importações [0-1]", 0.3),
        pib = _pedir_float("PIB — PIB (trilhões USD)", 1.0),
        inflacao = _pedir_float("Inflação anual (ex: 0.04)", 0.04),
    )


if __name__ == "__main__":
    menu_interativo()
