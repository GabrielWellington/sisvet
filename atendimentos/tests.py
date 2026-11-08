import io
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from cadastros.models import Animal, Tutor
from usuarios.models import PerfilUsuario
from .models import Atendimento, FotoAtendimento


def imagem_png():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), 'white').save(buffer, 'PNG')
    return SimpleUploadedFile('foto.png', buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class AtendimentoPainelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@exemplo.com', 'senha-forte-123')
        tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.animal = Animal.objects.create(tutor=tutor, nome='Bidu', especie='CAO', sexo='MACHO')
        self.url_add = reverse('admin:atendimentos_atendimento_add')

    def dados(self, **extra):
        base = {
            'animal': self.animal.pk, 'status': 'ABERTO', 'queixa_principal': 'Vômito',
            'historico_clinico': '', 'sintomas': '', 'peso_no_atendimento': '', 'temperatura': '',
            'diagnostico': '', 'tratamento': '', 'observacoes': '', 'doenca_confirmada': '',
            'fotos-TOTAL_FORMS': '1', 'fotos-INITIAL_FORMS': '0',
            'fotos-MIN_NUM_FORMS': '0', 'fotos-MAX_NUM_FORMS': '1000',
            'fotos-0-descricao': '',
        }
        base.update(extra)
        return base

    def test_registra_atendimento_com_foto_e_responsavel(self):
        self.client.force_login(self.admin)
        resposta = self.client.post(self.url_add, self.dados(**{'fotos-0-imagem': imagem_png()}))
        self.assertEqual(resposta.status_code, 302)
        atendimento = Atendimento.objects.get()
        self.assertEqual(atendimento.veterinaria, self.admin)
        self.assertEqual(FotoAtendimento.objects.filter(atendimento=atendimento).count(), 1)

    def test_queixa_principal_e_obrigatoria(self):
        self.client.force_login(self.admin)
        resposta = self.client.post(self.url_add, self.dados(queixa_principal=''))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Atendimento.objects.count(), 0)

    def test_arquivo_que_nao_e_imagem_e_rejeitado(self):
        self.client.force_login(self.admin)
        falso = SimpleUploadedFile('foto.png', b'nao e imagem', content_type='image/png')
        resposta = self.client.post(self.url_add, self.dados(**{'fotos-0-imagem': falso}))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Atendimento.objects.count(), 0)

    def test_edicao_de_atendimento_de_animal_que_faleceu(self):
        atendimento = Atendimento.objects.create(animal=self.animal, veterinaria=self.admin, queixa_principal='Tosse')
        self.animal.status = 'FALECIDO'
        self.animal.save()
        self.client.force_login(self.admin)
        url = reverse('admin:atendimentos_atendimento_change', args=[atendimento.pk])
        dados = self.dados(status='FINALIZADO', queixa_principal='Tosse')
        dados['fotos-TOTAL_FORMS'] = '0'
        resposta = self.client.post(url, dados)
        self.assertEqual(resposta.status_code, 302)
        atendimento.refresh_from_db()
        self.assertEqual(atendimento.status, 'FINALIZADO')


class ListagemPorResponsavelTests(TestCase):
    def setUp(self):
        tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        animal = Animal.objects.create(tutor=tutor, nome='Bidu', especie='CAO', sexo='MACHO')
        self.vet1 = User.objects.create_user('vet1', password='x', is_staff=True)
        self.vet2 = User.objects.create_user('vet2', password='x', is_staff=True)
        self.gestor = User.objects.create_user('gestor', password='x', is_staff=True)
        PerfilUsuario.objects.create(usuario=self.gestor, tipo='ADMIN')
        for usuario in (self.vet1, self.vet2, self.gestor):
            usuario.user_permissions.add(*__import__('django.contrib.auth.models', fromlist=['Permission'])
                                         .Permission.objects.filter(codename='view_atendimento'))
        Atendimento.objects.create(animal=animal, veterinaria=self.vet1, queixa_principal='Queixa da vet1')
        Atendimento.objects.create(animal=animal, veterinaria=self.vet2, queixa_principal='Queixa da vet2')
        self.url = reverse('admin:atendimentos_atendimento_changelist')

    def total_listado(self, usuario):
        self.client.force_login(usuario)
        return self.client.get(self.url).context['cl'].result_count

    def test_veterinaria_ve_somente_os_proprios_atendimentos(self):
        self.assertEqual(self.total_listado(self.vet1), 1)

    def test_perfil_administrador_ve_todos(self):
        self.assertEqual(self.total_listado(self.gestor), 2)
