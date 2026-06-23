from django.db import models
from django.core.exceptions import ValidationError


class Tutor(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF')
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    endereco = models.TextField(blank=True, null=True, verbose_name='Endereço')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Animal(models.Model):
    ESPECIE_CHOICES = [
        ('CAO', 'Cão'),
        ('GATO', 'Gato'),
        ('OUTRO', 'Outro'),
    ]

    SEXO_CHOICES = [
        ('MACHO', 'Macho'),
        ('FEMEA', 'Fêmea'),
    ]

    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('FALECIDO', 'Falecido'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='animais', verbose_name='Tutor')
    nome = models.CharField(max_length=100, verbose_name='Nome')
    especie = models.CharField(max_length=10, choices=ESPECIE_CHOICES, verbose_name='Espécie')
    especie_outro = models.CharField(max_length=50, blank=True, null=True, verbose_name='Outra espécie')
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, verbose_name='Sexo')
    raca = models.CharField(max_length=50, blank=True, null=True, verbose_name='Raça')
    idade_aproximada = models.CharField(max_length=50, blank=True, null=True, verbose_name='Idade aproximada')
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Peso (kg)')
    cor = models.CharField(max_length=50, blank=True, null=True, verbose_name='Cor')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO', verbose_name='Status')

    def clean(self):
        if self.especie == 'OUTRO' and not self.especie_outro:
            raise ValidationError('Informe qual é a espécie quando selecionar "Outro".')

        if self.especie != 'OUTRO':
            self.especie_outro = None

    def marcar_como_falecido(self, origem, tipo, motivo=None, observacoes=None):
        self.status = 'FALECIDO'
        self.save()

        ObitoAnimal.objects.update_or_create(
            animal=self,
            origem=origem,
            defaults={
                'tutor': self.tutor,
                'tipo': tipo,
                'motivo': motivo,
                'observacoes': observacoes,
            }
        )

    def esta_ativo(self):
        return self.status == 'ATIVO'

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'
        ordering = ['nome']

    def __str__(self):
        especie_display = self.get_especie_display() if self.especie != 'OUTRO' else self.especie_outro or 'Outro'
        return f'{self.nome} ({especie_display})'


class ObitoAnimal(models.Model):
    ORIGEM_CHOICES = [
        ('ATENDIMENTO', 'Atendimento'),
        ('CASTRACAO', 'Castração'),
        ('VISITA', 'Visita'),
        ('OUTRO', 'Outro'),
    ]

    TIPO_CHOICES = [
        ('OBITO', 'Óbito natural'),
        ('EUTANASIA', 'Eutanásia'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='obitos',
        verbose_name='Animal'
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tutor'
    )

    data_obito = models.DateField(auto_now_add=True, verbose_name='Data do óbito')

    origem = models.CharField(
        max_length=20,
        choices=ORIGEM_CHOICES,
        verbose_name='Origem'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo'
    )

    motivo = models.TextField(blank=True, null=True, verbose_name='Motivo')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Óbito de animal'
        verbose_name_plural = 'Óbitos de animais'
        ordering = ['-data_obito']

    def __str__(self):
        return f'{self.animal.nome} - {self.get_tipo_display()}'