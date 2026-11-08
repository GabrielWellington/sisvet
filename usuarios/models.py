from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    TIPO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('VET', 'Veterinária'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    ativo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Perfil inativo impede o acesso: a autenticação do Django verifica User.is_active.
        if not self.ativo and self.usuario.is_active:
            self.usuario.is_active = False
            self.usuario.save(update_fields=['is_active'])

    def __str__(self):
        return f'{self.usuario.username} - {self.get_tipo_display()}'