"""
Modelo S — App Android
Interface Kivy para cálculo do Índice de Estabilidade Socioeconômica.
"""

import math

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle

from modelo_s import (
    ALEMANHA_2025,
    BRASIL_2025,
    VENEZUELA_2025,
    PaisData,
    calcular_ss,
    classificar_ss,
    projetar_cenario,
)

# ── Paleta ────────────────────────────────────────────────────────────
BG      = (0.05, 0.11, 0.17, 1)   # navy escuro
GREEN   = (0.18, 0.80, 0.44, 1)
BLUE    = (0.18, 0.53, 0.87, 1)
WHITE   = (0.93, 0.94, 0.96, 1)
GRAY    = (0.4,  0.4,  0.4,  1)
PANEL   = (0.09, 0.18, 0.28, 1)

Window.clearcolor = BG


# ── Helpers de cor hex ────────────────────────────────────────────────
def _hex(r, g, b, a=1):
    return [r, g, b, a]


# ── Widget base com fundo arredondado ─────────────────────────────────
class Card(BoxLayout):
    def __init__(self, bg=PANEL, radius=18, **kw):
        super().__init__(**kw)
        self._bg = bg
        self._radius = radius
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self._radius])


# ── Botão estilizado ──────────────────────────────────────────────────
class StyledButton(Button):
    def __init__(self, color=GREEN, **kw):
        super().__init__(**kw)
        self.background_color = (*color[:3], 0)
        self.color = WHITE
        self.bold = True
        self.font_size = dp(16)
        self._btn_color = color
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._btn_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


# ── Campo de entrada ──────────────────────────────────────────────────
def _input_row(label_text, default_text):
    row = BoxLayout(orientation="horizontal", size_hint_y=None,
                    height=dp(48), spacing=dp(8))
    row.add_widget(Label(text=label_text, color=WHITE, size_hint_x=0.55,
                         font_size=dp(13), halign="right",
                         text_size=(None, None)))
    ti = TextInput(text=str(default_text), multiline=False,
                   size_hint_x=0.45,
                   background_color=(0.12, 0.22, 0.34, 1),
                   foreground_color=WHITE,
                   cursor_color=GREEN,
                   font_size=dp(14))
    row.add_widget(ti)
    return row, ti


# ══════════════════════════════════════════════════════════════════════
#  TELA 1 — Logo / Splash
# ══════════════════════════════════════════════════════════════════════
KV_LOGO = """
<LogoScreen>:
    name: "logo"

    canvas.before:
        Color:
            rgba: 0.05, 0.11, 0.17, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(30)
        spacing: dp(0)

        Widget:
            size_hint_y: 0.12

        # ── Logo: dois S formando o 8 ──────────────────────────────
        RelativeLayout:
            size_hint_y: 0.42

            Label:
                text: "S"
                font_size: dp(160)
                bold: True
                color: 0.18, 0.80, 0.44, 1
                pos_hint: {"center_x": 0.5, "top": 1.02}

            Label:
                text: "S"
                font_size: dp(160)
                bold: True
                color: 0.18, 0.53, 0.87, 1
                pos_hint: {"center_x": 0.5, "y": -0.02}

        # ── Título ────────────────────────────────────────────────
        Label:
            text: "MODELO S"
            font_size: dp(28)
            bold: True
            color: 0.93, 0.94, 0.96, 1
            size_hint_y: 0.10

        Label:
            text: "Índice de Estabilidade\\nSocioeconômica"
            font_size: dp(14)
            color: 0.55, 0.65, 0.75, 1
            halign: "center"
            size_hint_y: 0.08

        Widget:
            size_hint_y: 0.06

        # ── Botão entrar ─────────────────────────────────────────
        Button:
            text: "COMEÇAR"
            font_size: dp(17)
            bold: True
            size_hint: 0.7, None
            height: dp(52)
            pos_hint: {"center_x": 0.5}
            background_color: 0.18, 0.80, 0.44, 0
            color: 0.93, 0.94, 0.96, 1
            on_release: app.go_menu()
            canvas.before:
                Color:
                    rgba: 0.18, 0.80, 0.44, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(14)]

        Widget:
            size_hint_y: 0.12
"""


class LogoScreen(Screen):
    pass


# ══════════════════════════════════════════════════════════════════════
#  TELA 2 — Menu principal
# ══════════════════════════════════════════════════════════════════════
KV_MENU = """
<MenuScreen>:
    name: "menu"

    canvas.before:
        Color:
            rgba: 0.05, 0.11, 0.17, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(14)

        Label:
            text: "Selecione um país"
            font_size: dp(20)
            bold: True
            color: 0.93, 0.94, 0.96, 1
            size_hint_y: None
            height: dp(56)

        # Países pré-definidos
        Button:
            text: "🇧🇷  Brasil 2025"
            font_size: dp(16)
            bold: True
            background_color: 0, 0, 0, 0
            color: 0.93, 0.94, 0.96, 1
            on_release: app.show_country("brasil")
            canvas.before:
                Color:
                    rgba: 0.09, 0.30, 0.16, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12)]

        Button:
            text: "🇩🇪  Alemanha 2025"
            font_size: dp(16)
            bold: True
            background_color: 0, 0, 0, 0
            color: 0.93, 0.94, 0.96, 1
            on_release: app.show_country("alemanha")
            canvas.before:
                Color:
                    rgba: 0.09, 0.18, 0.38, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12)]

        Button:
            text: "🇻🇪  Venezuela 2025"
            font_size: dp(16)
            bold: True
            background_color: 0, 0, 0, 0
            color: 0.93, 0.94, 0.96, 1
            on_release: app.show_country("venezuela")
            canvas.before:
                Color:
                    rgba: 0.28, 0.16, 0.06, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12)]

        Widget:
            size_hint_y: None
            height: dp(8)

        # Entrada manual
        Button:
            text: "✏️  Inserir dados manualmente"
            font_size: dp(15)
            bold: True
            background_color: 0, 0, 0, 0
            color: 0.93, 0.94, 0.96, 1
            on_release: app.go_form()
            canvas.before:
                Color:
                    rgba: 0.18, 0.18, 0.28, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12)]

        Widget:
            size_hint_y: 1

        Button:
            text: "← Voltar"
            font_size: dp(13)
            color: 0.55, 0.65, 0.75, 1
            background_color: 0, 0, 0, 0
            size_hint_y: None
            height: dp(40)
            on_release: app.go_logo()
"""


class MenuScreen(Screen):
    pass


# ══════════════════════════════════════════════════════════════════════
#  TELA 3 — Formulário de entrada
# ══════════════════════════════════════════════════════════════════════
class FormScreen(Screen):
    def __init__(self, **kw):
        super().__init__(name="form", **kw)
        self._fields: dict[str, TextInput] = {}
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))

        # Cabeçalho
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_back = Button(text="←", size_hint_x=0.15, background_color=(0, 0, 0, 0),
                          color=WHITE, font_size=dp(22))
        btn_back.bind(on_release=lambda *_: App.get_running_app().go_menu())
        header.add_widget(btn_back)
        header.add_widget(Label(text="Dados do País", color=WHITE,
                                font_size=dp(18), bold=True))
        root.add_widget(header)

        # Scroll com campos
        scroll = ScrollView(size_hint_y=1)
        grid = GridLayout(cols=1, spacing=dp(4), size_hint_y=None,
                          padding=[0, 0, 0, dp(16)])
        grid.bind(minimum_height=grid.setter("height"))

        FIELDS = [
            ("Nome do país",                     "nome",     "País",  False),
            ("M  — Mobilidade social [0-1]",     "M",        "0.5",   False),
            ("lD — Log10(densidade hab/km²)",     "lD",       "1.4",   False),
            ("G  — Gini [0-1]",                  "G",        "0.4",   False),
            ("TFR — Fecundidade [1-4]",           "TFR",      "2.0",   False),
            ("E  — Escolaridade (anos)",          "E",        "8.0",   False),
            ("C  — Entropia cultural [0-1]",      "C",        "0.5",   False),
            ("I  — Imigração por HDI [0-1]",      "I",        "0.3",   False),
            ("P  — Patentes per capita",          "P",        "0.1",   False),
            ("S  — Startups unicórnio p.c.",      "S",        "0.05",  False),
            ("lG — Log-GitHub commits",           "lG",       "1.0",   False),
            ("N  — Nobel per capita",             "N",        "0.05",  False),
            ("NL — Luz noturna [0-∞]",            "NL",       "0.5",   False),
            ("EXC — Exp. commodities/PIB [0-1]",  "EXC",      "0.3",   False),
            ("TOT — Termos de troca [0-∞]",       "TOT",      "1.0",   False),
            ("CCO — Conc. commodities [0-1]",     "CCO",      "0.3",   False),
            ("EXM — Exp. manufat./PIB [0-1]",     "EXM",      "0.2",   False),
            ("EXS — Sofistic. exportações [0-1]", "EXS",      "0.5",   False),
            ("GVC — Cadeias globais [0-1]",       "GVC",      "0.4",   False),
            ("IMD — Dep. importações [0-1]",      "IMD",      "0.3",   False),
            ("PIB (trilhões USD)",                "pib",      "1.0",   False),
            ("Inflação anual (ex: 0.04)",         "inflacao", "0.04",  False),
        ]

        for label_txt, key, default, _ in FIELDS:
            row, ti = _input_row(label_txt, default)
            self._fields[key] = ti
            grid.add_widget(row)

        scroll.add_widget(grid)
        root.add_widget(scroll)

        # Botão calcular
        btn = StyledButton(text="CALCULAR SS", color=GREEN,
                           size_hint_y=None, height=dp(52))
        btn.bind(on_release=self._calcular)
        root.add_widget(btn)

        self.add_widget(root)

    def populate(self, dados: PaisData):
        for key, ti in self._fields.items():
            val = getattr(dados, key, "")
            ti.text = str(val)

    def _calcular(self, *_):
        try:
            nome = self._fields["nome"].text or "País"
            d = PaisData(
                nome=nome,
                M=float(self._fields["M"].text),
                lD=float(self._fields["lD"].text),
                G=float(self._fields["G"].text),
                TFR=float(self._fields["TFR"].text),
                E=float(self._fields["E"].text),
                C=float(self._fields["C"].text),
                I=float(self._fields["I"].text),
                P=float(self._fields["P"].text),
                S=float(self._fields["S"].text),
                lG=float(self._fields["lG"].text),
                N=float(self._fields["N"].text),
                NL=float(self._fields["NL"].text),
                EXC=float(self._fields["EXC"].text),
                TOT=float(self._fields["TOT"].text),
                CCO=float(self._fields["CCO"].text),
                EXM=float(self._fields["EXM"].text),
                EXS=float(self._fields["EXS"].text),
                GVC=float(self._fields["GVC"].text),
                IMD=float(self._fields["IMD"].text),
                pib=float(self._fields["pib"].text),
                inflacao=float(self._fields["inflacao"].text),
            )
            App.get_running_app().show_results(d)
        except ValueError as e:
            popup = Popup(title="Erro de entrada",
                          content=Label(text=f"Valor inválido:\n{e}",
                                        color=WHITE),
                          size_hint=(0.8, 0.4))
            popup.open()


# ══════════════════════════════════════════════════════════════════════
#  TELA 4 — Resultados
# ══════════════════════════════════════════════════════════════════════
CLASS_COLOR = {
    "Crítico":       (0.80, 0.15, 0.15, 1),
    "Alto":          (0.85, 0.38, 0.10, 1),
    "Moderado":      (0.85, 0.65, 0.10, 1),
    "Estável":       (0.20, 0.70, 0.35, 1),
    "Muito Estável": (0.15, 0.60, 0.85, 1),
    "Excelente":     (0.50, 0.15, 0.85, 1),
}


class ResultsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(name="results", **kw)
        self._root = BoxLayout(orientation="vertical",
                               padding=dp(16), spacing=dp(10))
        self.add_widget(self._root)

    def show(self, dados: PaisData):
        self._root.clear_widgets()
        ss = calcular_ss(dados)
        classe, risco = classificar_ss(ss)
        projecoes = projetar_cenario(dados, horizonte=5)
        cor = CLASS_COLOR.get(classe, GREEN)

        # ── Cabeçalho ──────────────────────────────────────────────
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_back = Button(text="←", size_hint_x=0.15,
                          background_color=(0, 0, 0, 0),
                          color=WHITE, font_size=dp(22))
        btn_back.bind(on_release=lambda *_: App.get_running_app().go_menu())
        header.add_widget(btn_back)
        header.add_widget(Label(text=f"{dados.nome} {dados.ano}",
                                color=WHITE, font_size=dp(18), bold=True))
        self._root.add_widget(header)

        # ── Card SS ────────────────────────────────────────────────
        card_ss = Card(orientation="vertical", size_hint_y=None,
                       height=dp(130), padding=dp(16))
        card_ss.add_widget(Label(
            text=f"Índice SS: [b][color={_rgba_hex(cor)}]{ss:.4f}[/color][/b]",
            markup=True, font_size=dp(26), color=WHITE, size_hint_y=0.5))
        card_ss.add_widget(Label(
            text=f"[b]{classe}[/b]",
            markup=True, font_size=dp(18),
            color=cor, size_hint_y=0.3))
        card_ss.add_widget(Label(
            text=f"Risco: {risco}",
            font_size=dp(13), color=(*GRAY[:3], 1), size_hint_y=0.2))
        self._root.add_widget(card_ss)

        # ── Barra de progresso ────────────────────────────────────
        self._root.add_widget(
            _progress_bar(ss, min_val=1.0, max_val=6.0, color=cor))

        # ── Card PIB ──────────────────────────────────────────────
        card_pib = Card(orientation="vertical", size_hint_y=None,
                        height=dp(64), padding=dp(12))
        card_pib.add_widget(Label(
            text=f"PIB atual: US$ {dados.pib:.2f} tri  |  Inflação: {dados.inflacao*100:.1f}%",
            font_size=dp(13), color=WHITE))
        self._root.add_widget(card_pib)

        # ── Tabela de projeção ────────────────────────────────────
        self._root.add_widget(Label(
            text="Projeção 5 anos", color=WHITE, font_size=dp(15),
            bold=True, size_hint_y=None, height=dp(30)))

        scroll = ScrollView(size_hint_y=1)
        grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None,
                          padding=[0, 0, 0, dp(8)])
        grid.bind(minimum_height=grid.setter("height"))

        for header_txt in ("Ano", "SS", "PIB T$", "Status"):
            grid.add_widget(Label(text=header_txt, color=(*GRAY[:3], 1),
                                  font_size=dp(12), bold=True,
                                  size_hint_y=None, height=dp(28)))

        for p in projecoes:
            c_row = CLASS_COLOR.get(p.classificacao, GREEN)
            for val in (str(p.ano), f"{p.ss:.2f}",
                        f"{p.pib:.2f}", p.classificacao[:8]):
                grid.add_widget(Label(
                    text=val, color=c_row if val == p.classificacao[:8] else WHITE,
                    font_size=dp(12), size_hint_y=None, height=dp(28)))

        scroll.add_widget(grid)
        self._root.add_widget(scroll)

        # ── Botão refazer ─────────────────────────────────────────
        btn = StyledButton(text="← NOVO CÁLCULO", color=BLUE,
                           size_hint_y=None, height=dp(46))
        btn.bind(on_release=lambda *_: App.get_running_app().go_menu())
        self._root.add_widget(btn)


def _rgba_hex(rgba) -> str:
    r, g, b, _ = rgba
    return "{:02x}{:02x}{:02x}".format(
        int(r * 255), int(g * 255), int(b * 255))


def _progress_bar(value, min_val, max_val, color, height=dp(18)):
    frac = (value - min_val) / (max_val - min_val)
    frac = max(0.0, min(1.0, frac))
    outer = BoxLayout(size_hint_y=None, height=height,
                      padding=[0, dp(2)])
    with outer.canvas.before:
        Color(0.15, 0.2, 0.3, 1)
        RoundedRectangle(pos=outer.pos, size=outer.size, radius=[dp(6)])
    fill = BoxLayout(size_hint_x=frac)
    with fill.canvas.before:
        Color(*color)
        RoundedRectangle(pos=fill.pos, size=fill.size, radius=[dp(6)])
    outer.bind(pos=lambda *_: _redraw_bar(outer, fill, frac, color),
               size=lambda *_: _redraw_bar(outer, fill, frac, color))
    outer.add_widget(fill)
    outer.add_widget(BoxLayout(size_hint_x=1 - frac))
    return outer


def _redraw_bar(outer, fill, frac, color):
    outer.canvas.before.clear()
    with outer.canvas.before:
        Color(0.15, 0.2, 0.3, 1)
        RoundedRectangle(pos=outer.pos, size=outer.size, radius=[dp(6)])
    fill.canvas.before.clear()
    with fill.canvas.before:
        Color(*color)
        RoundedRectangle(pos=fill.pos, size=fill.size, radius=[dp(6)])


# ══════════════════════════════════════════════════════════════════════
#  App principal
# ══════════════════════════════════════════════════════════════════════
Builder.load_string(KV_LOGO + KV_MENU)

PAISES = {
    "brasil":    BRASIL_2025,
    "alemanha":  ALEMANHA_2025,
    "venezuela": VENEZUELA_2025,
}


class ModeloSApp(App):
    def build(self):
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(LogoScreen())
        self.sm.add_widget(MenuScreen())

        self.form_screen = FormScreen()
        self.sm.add_widget(self.form_screen)

        self.results_screen = ResultsScreen()
        self.sm.add_widget(self.results_screen)

        return self.sm

    # ── Navegação ─────────────────────────────────────────────────
    def go_logo(self):
        self.sm.current = "logo"

    def go_menu(self):
        self.sm.current = "menu"

    def go_form(self):
        self.sm.current = "form"

    def show_country(self, key: str):
        dados = PAISES[key]
        self.show_results(dados)

    def show_results(self, dados: PaisData):
        self.results_screen.show(dados)
        self.sm.current = "results"


if __name__ == "__main__":
    ModeloSApp().run()
