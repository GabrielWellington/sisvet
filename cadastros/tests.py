from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Animal, ObitoAnimal, Tutor


class TutorTests(TestCase):
    def test_bloqueia_tutor_com_mesmo_nome_ignorando_maiusculas(self):
        Tutor.objects.create(nome='Maria Souza', telefone='14999990000')
        repetido = Tutor(nome='  maria souza ', telefone='14988880000')
        with self.assertRaises(ValidationError):
            repetido.full_clean()

    def test_permite_editar_o_proprio_tutor(self):
        tutor = Tutor.objects.create(nome='Maria Souza', telefone='14999990000')
        tutor.telefone = '14977770000'
        tutor.full_clean()


class AnimalTests(TestCase):
    def setUp(self):
        self.tutor = Tutor.objects.create(nome='João Lima', telefone='14999990000')

    def test_cadastro_valido_sem_nome(self):
        animal = Animal(tutor=self.tutor, especie='CAO', sexo='MACHO')
        animal.full_clean()
        animal.save()
        self.assertIn('Sem nome', str(animal))

    def test_especie_outro_exige_descricao(self):
        animal = Animal(tutor=self.tutor, especie='OUTRO', sexo='FEMEA')
        with self.assertRaises(ValidationError):
            animal.full_clean()

    def test_descricao_de_outra_especie_e_limpa_quando_nao_aplicavel(self):
        animal = Animal(tutor=self.tutor, especie='GATO', sexo='FEMEA', especie_outro='Coelho')
        animal.full_clean()
        self.assertIsNone(animal.especie_outro)


class ObitoTests(TestCase):
    def setUp(self):
        self.tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.outro_tutor = Tutor.objects.create(nome='Carlos Reis', telefone='14999991111')
        self.animal = Animal.objects.create(tutor=self.tutor, nome='Rex', especie='CAO', sexo='MACHO')

    def test_data_do_obito_e_informada_pelo_usuario(self):
        ontem = timezone.localdate() - timedelta(days=1)
        obito = ObitoAnimal(animal=self.animal, origem='OUTRO', tipo='OBITO', data_obito=ontem)
        obito.full_clean()
        obito.save()
        self.assertEqual(ObitoAnimal.objects.get().data_obito, ontem)

    def test_data_futura_e_rejeitada(self):
        amanha = timezone.localdate() + timedelta(days=1)
        obito = ObitoAnimal(animal=self.animal, origem='OUTRO', tipo='OBITO', data_obito=amanha)
        with self.assertRaises(ValidationError):
            obito.full_clean()

    def test_nao_permite_dois_obitos_para_o_mesmo_animal(self):
        ObitoAnimal.objects.create(animal=self.animal, origem='OUTRO', tipo='OBITO')
        segundo = ObitoAnimal(animal=self.animal, origem='VISITA', tipo='EUTANASIA')
        with self.assertRaises(ValidationError):
            segundo.full_clean()

    def test_tutor_do_obito_deve_ser_o_tutor_do_animal(self):
        obito = ObitoAnimal(animal=self.animal, tutor=self.outro_tutor, origem='OUTRO', tipo='OBITO')
        with self.assertRaises(ValidationError):
            obito.full_clean()

    def test_marcar_como_falecido_mantem_um_unico_registro(self):
        self.animal.marcar_como_falecido(origem='ATENDIMENTO', tipo='OBITO')
        self.animal.marcar_como_falecido(origem='VISITA', tipo='EUTANASIA')
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.status, 'FALECIDO')
        self.assertEqual(ObitoAnimal.objects.filter(animal=self.animal).count(), 1)


class PainelAnimaisTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@exemplo.com', 'senha-forte-123')
        self.client.force_login(self.admin)
        tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.vivo = Animal.objects.create(tutor=tutor, nome='Bidu', especie='CAO', sexo='MACHO')
        self.falecido = Animal.objects.create(
            tutor=tutor, nome='Mimi', especie='GATO', sexo='FEMEA', status='FALECIDO'
        )

    def test_listagem_padrao_mostra_apenas_ativos(self):
        resposta = self.client.get(reverse('admin:cadastros_animal_changelist'))
        self.assertContains(resposta, 'Bidu')
        self.assertNotContains(resposta, 'Mimi')

    def test_filtro_de_falecidos_lista_os_falecidos(self):
        resposta = self.client.get(reverse('admin:cadastros_animal_changelist') + '?status__exact=FALECIDO')
        self.assertContains(resposta, 'Mimi')

    def test_ficha_do_animal_falecido_continua_acessivel(self):
        resposta = self.client.get(reverse('admin:cadastros_animal_change', args=[self.falecido.pk]))
        self.assertEqual(resposta.status_code, 200)

    def test_registro_de_obito_pelo_painel_atualiza_status(self):
        url = reverse('admin:cadastros_obitoanimal_add')
        resposta = self.client.post(url, {
            'animal': self.vivo.pk,
            'tutor': '',
            'data_obito': timezone.localdate().strftime('%d/%m/%Y'),
            'origem': 'OUTRO',
            'tipo': 'OBITO',
            'motivo': '',
            'observacoes': '',
        })
        self.assertEqual(resposta.status_code, 302, getattr(resposta, 'context', None) and resposta.context['adminform'].form.errors)
        self.vivo.refresh_from_db()
        self.assertEqual(self.vivo.status, 'FALECIDO')
        self.assertEqual(ObitoAnimal.objects.get(animal=self.vivo).tutor_id, self.vivo.tutor_id)


class TutorDoAnimalEndpointTests(TestCase):
    def setUp(self):
        tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.animal = Animal.objects.create(tutor=tutor, nome='Bidu', especie='CAO', sexo='MACHO')
        self.url = reverse('tutor_do_animal')

    def test_sem_sessao_nao_expoe_dados(self):
        resposta = self.client.get(self.url, {'animal_id': self.animal.pk})
        self.assertEqual(resposta.status_code, 403)
        self.assertNotIn('Ana Reis', resposta.content.decode())

    def test_usuario_do_painel_recebe_o_tutor(self):
        usuario = User.objects.create_user('vet', password='senha-forte-123', is_staff=True)
        self.client.force_login(usuario)
        resposta = self.client.get(self.url, {'animal_id': self.animal.pk})
        self.assertEqual(resposta.json()['tutor_nome'], 'Ana Reis')

    def test_identificador_invalido(self):
        usuario = User.objects.create_user('vet', password='senha-forte-123', is_staff=True)
        self.client.force_login(usuario)
        self.assertIsNone(self.client.get(self.url, {'animal_id': 'abc'}).json()['tutor_id'])
