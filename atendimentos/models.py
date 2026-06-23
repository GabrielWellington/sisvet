from django.db import models
from django.contrib.auth.models import User
from cadastros.models import Animal


class Doenca(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')

    class Meta:
        verbose_name = 'Doença'
        verbose_name_plural = 'Doenças'

    def __str__(self):
        return self.nome


class Atendimento(models.Model):
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('EM_ATENDIMENTO', 'Em atendimento'),
        ('FINALIZADO', 'Finalizado'),
    ]

    doencas = models.ManyToManyField(Doenca, blank=True, verbose_name='Doenças')

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='atendimentos', verbose_name='Animal')
    veterinaria = models.ForeignKey(User, on_delete=models.PROTECT, related_name='atendimentos', verbose_name='Veterinária')

    data_atendimento = models.DateTimeField(auto_now_add=True, verbose_name='Data do atendimento')
    queixa_principal = models.TextField(verbose_name='Queixa principal')
    historico_clinico = models.TextField(blank=True, null=True, verbose_name='Histórico clínico')
    sintomas = models.TextField(blank=True, null=True, verbose_name='Sintomas')
    diagnostico = models.TextField(blank=True, null=True, verbose_name='Diagnóstico')
    doenca_confirmada = models.ForeignKey(
        Doenca,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='casos_confirmados',
        verbose_name='Doença confirmada'
    )
    tratamento = models.TextField(blank=True, null=True, verbose_name='Tratamento')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    peso_no_atendimento = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Peso no atendimento (kg)')
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, verbose_name='Temperatura (°C)')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO', verbose_name='Status')

    class Meta:
        verbose_name = 'Atendimento'
        verbose_name_plural = 'Atendimentos'

    def __str__(self):
        return f'{self.animal.nome} - {self.data_atendimento.strftime("%d/%m/%Y")}'


class FotoAtendimento(models.Model):
    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.CASCADE,
        related_name='fotos',
        verbose_name='Atendimento'
    )
    imagem = models.ImageField(upload_to='atendimentos/fotos/', verbose_name='Imagem')
    descricao = models.CharField(max_length=150, blank=True, null=True, verbose_name='Descrição')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Foto do atendimento'
        verbose_name_plural = 'Fotos dos atendimentos'

    def __str__(self):
        return f'Foto - {self.atendimento.animal.nome}'