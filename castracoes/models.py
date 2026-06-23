from django.db import models
from cadastros.models import Animal, Tutor
from django.core.exceptions import ValidationError


class Castracao(models.Model):
    PERIODO_CHOICES = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
    ]

    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('COMPARECEU', 'Compareceu'),
        ('FALTOU', 'Faltou'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.PROTECT, related_name='castracoes', verbose_name='Tutor')
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name='castracoes', verbose_name='Animal')

    data_agendada = models.DateField(verbose_name='Data agendada')
    periodo = models.CharField(max_length=10, choices=PERIODO_CHOICES, verbose_name='Período')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADA', verbose_name='Status')

    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    def clean(self):
        if self.animal and self.tutor and self.animal.tutor != self.tutor:
            raise ValidationError('O animal selecionado não pertence ao tutor informado.')

    class Meta:
        verbose_name = 'Castração'
        verbose_name_plural = 'Castrações'

    def __str__(self):
        return f'{self.animal.nome} - {self.data_agendada.strftime("%d/%m/%Y")} - {self.get_periodo_display()}'