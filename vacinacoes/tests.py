from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import BoletimVacinacaoRaiva


class BoletimTests(TestCase):
    def boletim(self, **extra):
        base = dict(tipo_posto='FIXO', tipo_vacinacao='ROTINA', data=date(2026, 10, 5))
        base.update(extra)
        return BoletimVacinacaoRaiva(**base)

    def test_total_e_a_soma_das_especies(self):
        boletim = self.boletim(caes=10, gatos=5, outros=2)
        boletim.full_clean()
        self.assertEqual(boletim.total, 17)

    def test_quantidade_negativa_e_rejeitada(self):
        with self.assertRaises(ValidationError):
            self.boletim(caes=-1).full_clean()

    def test_quantidade_decimal_e_rejeitada(self):
        with self.assertRaises(ValidationError):
            self.boletim(gatos='2.5').full_clean()
