#!/usr/bin/env python3
"""
Gera o logo do Modelo S: um 8 formado por dois S sobrepostos.
  - S verde  → metade superior do 8
  - S azul   → metade inferior, espelhado horizontalmente

Saída: logo.svg  (abra no browser para visualizar)
"""

W, H = 320, 460       # largura × altura do canvas
CX   = W // 2         # centro horizontal

FS       = 310        # font-size em px
GREEN    = "#2ECC71"  # verde vibrante
BLUE     = "#2E86DE"  # azul vibrante
BG       = "#0D1B2A"  # fundo escuro navy
GLOW_G   = "#27AE60"  # cor do brilho verde
GLOW_B   = "#1565C0"  # cor do brilho azul

# Cap-height típico para fontes bold (~72 % do font-size)
CAP = round(0.72 * FS)  # ≈ 223 px

# ── Posicionamento ──────────────────────────────────────────────
# S verde: topo visual a ~20 px da borda superior
#   baseline = 20 + CAP
Y_GREEN = 20 + CAP          # ≈ 243

# S azul (espelhado em X): base visual a ~20 px da borda inferior
#   Para texto espelhado a baseline segue a mesma lógica
Y_BLUE  = H - 20            # ≈ 440

# Os dois S se encontram ao redor de Y_GREEN / Y_BLUE - CAP,
# criando a "cruzeta" do 8 com ~(Y_GREEN - (Y_BLUE - CAP)) px de sobreposição.
# Sobreposição ≈ Y_GREEN - (H - 20 - CAP) = Y_GREEN - H + 20 + CAP
# Para H=460: 243 - 460 + 20 + 223 = 26 px → cruzamento visível


def build_svg() -> str:
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}">

  <defs>
    <!-- Brilho verde -->
    <filter id="glow-green" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feFlood flood-color="{GLOW_G}" flood-opacity="0.55" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <!-- Brilho azul -->
    <filter id="glow-blue" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feFlood flood-color="{GLOW_B}" flood-opacity="0.55" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Fundo -->
  <rect width="{W}" height="{H}" fill="{BG}" rx="28"/>

  <!-- ══ S VERDE — metade superior do 8 ══
       Posicionado normalmente, ocupa o topo do canvas. -->
  <text
    x="{CX}" y="{Y_GREEN}"
    text-anchor="middle"
    font-family="'Arial Black','Impact','Helvetica Neue',Arial,sans-serif"
    font-size="{FS}"
    font-weight="900"
    fill="{GREEN}"
    filter="url(#glow-green)">S</text>

  <!-- ══ S AZUL — metade inferior do 8, espelhado horizontalmente ══
       transform="matrix(-1,0,0,1,{W},0)" reflete em torno de x={CX}:
         x_novo = -x + {W}  →  o centro {CX} fica em {CX}  ✓
         y_novo = y          →  posição vertical inalterada  ✓
       O glifo aparece como "S invertido lateralmente" (∫-like),
       completando a forma do 8 com o S verde acima. -->
  <text
    x="{CX}" y="{Y_BLUE}"
    text-anchor="middle"
    font-family="'Arial Black','Impact','Helvetica Neue',Arial,sans-serif"
    font-size="{FS}"
    font-weight="900"
    fill="{BLUE}"
    transform="matrix(-1,0,0,1,{W},0)"
    filter="url(#glow-blue)">S</text>

</svg>"""


def main() -> None:
    content = build_svg()
    out = "logo.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Logo salvo: {out}")
    print("Abra no browser (Chrome/Firefox) para visualizar.")


if __name__ == "__main__":
    main()
