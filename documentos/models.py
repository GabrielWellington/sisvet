from django.db import models
from cadastros.models import Tutor, Animal


class Documento(models.Model):
    TIPO_CHOICES = [
        ('EUTANASIA', 'Termo de eutanásia'),
        ('AUTORIZACAO_PROCEDIMENTO', 'Autorização de procedimento'),
        ('EXAME', 'Exame'),
        ('OUTRO', 'Outro'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='documentos', verbose_name='Tutor')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='documentos', verbose_name='Animal')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo')
    arquivo = models.FileField(upload_to='documentos/', verbose_name='Arquivo')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.animal.nome}'