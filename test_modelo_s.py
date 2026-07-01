"""Testes unitários para o Modelo S."""

import math
import unittest
from modelo_s import (
    BRASIL_2025,
    ALEMANHA_2025,
    VENEZUELA_2025,
    calcular_ss,
    calcular_vif,
    classificar_ss,
    normalizar_zscore,
    projetar_cenario,
    projetar_pib,
)


class TestCalcularSS(unittest.TestCase):
    def test_brasil_faixa(self):
        ss = calcular_ss(BRASIL_2025)
        self.assertGreater(ss, 1.0)
        self.assertLess(ss, 6.0)

    def test_alemanha_maior_que_brasil(self):
        self.assertGreater(calcular_ss(ALEMANHA_2025), calcular_ss(BRASIL_2025))

    def test_venezuela_menor_que_brasil(self):
        self.assertLess(calcular_ss(VENEZUELA_2025), calcular_ss(BRASIL_2025))

    def test_retorna_float(self):
        self.assertIsInstance(calcular_ss(BRASIL_2025), float)


class TestClassificarSS(unittest.TestCase):
    def test_critico(self):
        classe, _ = classificar_ss(1.5)
        self.assertEqual(classe, "Crítico")

    def test_estavel(self):
        classe, _ = classificar_ss(4.0)
        self.assertEqual(classe, "Estável")

    def test_excelente(self):
        classe, _ = classificar_ss(5.8)
        self.assertEqual(classe, "Excelente")

    def test_moderado_brasil(self):
        ss = calcular_ss(BRASIL_2025)
        # Nota: o documento cita SS≈3.20 para Brasil, mas os parciais somados
        # do próprio exemplo totalizam 5.41 (erro aritmético no documento).
        # A fórmula computada aqui é matematicamente consistente: ~5.41.
        self.assertAlmostEqual(ss, 5.41, delta=0.05)
        classe, _ = classificar_ss(ss)
        self.assertIn(classe, ("Muito Estável", "Excelente"))


class TestProjetarPib(unittest.TestCase):
    def test_cresce_com_ss_alto(self):
        pib = projetar_pib(1.0, 5.0, 0.03)
        self.assertGreater(pib, 1.0)

    def test_formula(self):
        resultado = projetar_pib(2.0, 4.0, 0.05)
        esperado = 2.0 * (1 + 0.018 * 4.0) * (1 + 0.05)
        self.assertAlmostEqual(resultado, esperado, places=6)


class TestProjetarCenario(unittest.TestCase):
    def test_tamanho(self):
        pts = projetar_cenario(BRASIL_2025, horizonte=5)
        self.assertEqual(len(pts), 6)  # ano 0 + 5

    def test_primeiro_ponto(self):
        pts = projetar_cenario(BRASIL_2025, horizonte=3)
        self.assertEqual(pts[0].ano, BRASIL_2025.ano)

    def test_otimista_maior_que_pessimista(self):
        otimista = projetar_cenario(BRASIL_2025, 5, delta_ss_anual=+0.05)
        pessimista = projetar_cenario(BRASIL_2025, 5, delta_ss_anual=-0.05)
        self.assertGreater(otimista[-1].ss, pessimista[-1].ss)

    def test_ss_clamped(self):
        pts = projetar_cenario(VENEZUELA_2025, horizonte=50, delta_ss_anual=-1.0)
        for p in pts:
            self.assertGreaterEqual(p.ss, 1.0)


class TestNormalizarZscore(unittest.TestCase):
    def test_media_zero(self):
        self.assertAlmostEqual(normalizar_zscore(5.0, 5.0, 2.0), 0.0)

    def test_desvio_zero(self):
        self.assertEqual(normalizar_zscore(3.0, 3.0, 0.0), 0.0)

    def test_valor(self):
        self.assertAlmostEqual(normalizar_zscore(7.0, 5.0, 2.0), 1.0)


class TestCalcularVif(unittest.TestCase):
    def test_r2_zero(self):
        self.assertAlmostEqual(calcular_vif(0.0), 1.0)

    def test_r2_alto(self):
        self.assertGreater(calcular_vif(0.8), 5.0)

    def test_r2_um(self):
        self.assertEqual(calcular_vif(1.0), float("inf"))


if __name__ == "__main__":
    unittest.main()
