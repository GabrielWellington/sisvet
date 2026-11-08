from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from cadastros.models import Animal, Tutor
from .models import Castracao


class CastracaoTests(TestCase):
    def setUp(self):
        self.tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.outro = Tutor.objects.create(nome='Bruno Dias', telefone='14999991111')
        self.animal = Animal.objects.create(tutor=self.tutor, nome='Bidu', especie='CAO', sexo='MACHO')

    def dados(self, **extra):
        base = dict(tutor=self.tutor, animal=self.animal, data_agendada=date(2026, 10, 5), periodo='MANHA')
        base.update(extra)
        return base

    def test_agendamento_valido_inicia_como_agendada(self):
        castracao = Castracao(**self.dados())
        castracao.full_clean()
        castracao.save()
        self.assertEqual(castracao.status, 'AGENDADA')

    def test_animal_de_outro_tutor_e_rejeitado(self):
        castracao = Castracao(**self.dados(tutor=self.outro))
        with self.assertRaises(ValidationError) as erro:
            castracao.full_clean()
        self.assertIn('animal', erro.exception.message_dict)

    def test_sem_animal_mostra_erro_de_campo_obrigatorio(self):
        dados = self.dados()
        dados.pop('animal')
        with self.assertRaises(ValidationError) as erro:
            Castracao(**dados).full_clean()
        self.assertIn('animal', erro.exception.message_dict)

    def test_sem_tutor_mostra_erro_de_campo_obrigatorio(self):
        dados = self.dados()
        dados.pop('tutor')
        with self.assertRaises(ValidationError) as erro:
            Castracao(**dados).full_clean()
        self.assertIn('tutor', erro.exception.message_dict)
