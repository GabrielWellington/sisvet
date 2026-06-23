from django.db import models
from django.core.exceptions import ValidationError
from cadastros.models import Tutor, Animal
from atendimentos.models import Doenca


class Visita(models.Model):
    AREA_CHOICES = [
        ('RURAL', 'Zona rural'),
        ('URBANA', 'Zona urbana'),
    ]

    SITUACAO_CHOICES = [
        ('NORMAL', 'Visita normal'),
        ('CASA_FECHADA', 'Casa fechada'),
        ('RECUSA', 'Recusa'),
        ('OUTRO', 'Outro'),
    ]

    area = models.CharField(max_length=20, choices=AREA_CHOICES, verbose_name='Área')
    setor = models.CharField(max_length=20, verbose_name='Setor')
    quadra = models.CharField(max_length=20, blank=True, null=True, verbose_name='Quadra')

    nome_responsavel = models.CharField(max_length=100, verbose_name='Nome do responsável')
    endereco = models.TextField(verbose_name='Endereço')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')

    tutor = models.ForeignKey(Tutor, on_delete=models.SET_NULL, blank=True, null=True, related_name='visitas', verbose_name='Tutor')
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, blank=True, null=True, related_name='visitas', verbose_name='Animal')
    nome_animal_nao_cadastrado = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nome do animal (não cadastrado)')

    data_visita = models.DateField(verbose_name='Data da visita')
    situacao = models.CharField(max_length=30, choices=SITUACAO_CHOICES, default='NORMAL', verbose_name='Situação')

    doencas_positivas = models.ManyToManyField(Doenca, blank=True, verbose_name='Doenças positivas')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    def clean(self):
        if not self.animal and not self.nome_animal_nao_cadastrado:
            raise ValidationError('Informe um animal cadastrado ou escreva o nome do animal não cadastrado.')

        if self.animal and self.tutor and self.animal.tutor != self.tutor:
            raise ValidationError('O animal selecionado não pertence ao tutor informado.')

    class Meta:
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'

    def __str__(self):
        return f'{self.nome_responsavel} - {self.data_visita.strftime("%d/%m/%Y")}'