from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import PerfilUsuario


class PerfilUsuarioTests(TestCase):
    def test_perfil_inativo_bloqueia_o_login(self):
        usuario = User.objects.create_user('vet', password='senha-forte-123', is_staff=True)
        PerfilUsuario.objects.create(usuario=usuario, tipo='VET', ativo=False)
        usuario.refresh_from_db()
        self.assertFalse(usuario.is_active)
        self.assertFalse(self.client.login(username='vet', password='senha-forte-123'))

    def test_login_com_credenciais_validas_e_invalidas(self):
        User.objects.create_user('vet', password='senha-forte-123', is_staff=True)
        url = reverse('admin:login')
        ok = self.client.post(url, {'username': 'vet', 'password': 'senha-forte-123', 'next': '/admin/'})
        self.assertEqual(ok.status_code, 302)
        self.client.logout()
        erro = self.client.post(url, {'username': 'vet', 'password': 'errada', 'next': '/admin/'})
        self.assertEqual(erro.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
