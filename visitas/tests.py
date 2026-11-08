from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from cadastros.models import Animal, Tutor
from .models import Visita


class VisitaTests(TestCase):
    def setUp(self):
        self.tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.outro = Tutor.objects.create(nome='Bruno Dias', telefone='14999991111')
        self.animal = Animal.objects.create(tutor=self.tutor, nome='Bidu', especie='CAO', sexo='MACHO')

    def visita(self, **extra):
        base = dict(area='URBANA', setor='3', nome_responsavel='Morador', endereco='Rua A, 10',
                    data_visita=date(2026, 10, 5))
        base.update(extra)
        return Visita(**base)

    def test_aceita_animal_nao_cadastrado_pelo_nome(self):
        self.visita(nome_animal_nao_cadastrado='Pretinha').full_clean()

    def test_exige_alguma_identificacao_do_animal(self):
        with self.assertRaises(ValidationError):
            self.visita().full_clean()

    def test_rejeita_animal_de_outro_tutor(self):
        with self.assertRaises(ValidationError):
            self.visita(tutor=self.outro, animal=self.animal).full_clean()

    def test_aceita_animal_cadastrado_do_proprio_tutor(self):
        self.visita(tutor=self.tutor, animal=self.animal).full_clean()
