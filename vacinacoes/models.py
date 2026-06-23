from django.db import models


class BoletimVacinacaoRaiva(models.Model):
    TIPO_POSTO_CHOICES = [
        ('FIXO', 'Fixo'),
        ('VOLANTE', 'Volante'),
    ]

    TIPO_VACINACAO_CHOICES = [
        ('ROTINA', 'Rotina'),
        ('CAMPANHA', 'Campanha'),
        ('COBERTURA_FOCO', 'Cobertura de foco'),
    ]

    gve = models.CharField(max_length=100, blank=True, null=True, verbose_name='GVE')
    municipio = models.CharField(max_length=100, default='Promissão', verbose_name='Município')
    posto = models.CharField(max_length=100, blank=True, null=True, verbose_name='Posto')

    tipo_posto = models.CharField(max_length=20, choices=TIPO_POSTO_CHOICES, verbose_name='Tipo de posto')
    tipo_vacinacao = models.CharField(max_length=30, choices=TIPO_VACINACAO_CHOICES, verbose_name='Tipo de vacinação')

    data = models.DateField(verbose_name='Data')

    caes = models.PositiveIntegerField(default=0, verbose_name='Cães')
    gatos = models.PositiveIntegerField(default=0, verbose_name='Gatos')
    outros = models.PositiveIntegerField(default=0, verbose_name='Outros')

    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    responsavel_preenchimento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Responsável pelo preenchimento')

    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    @property
    def total(self):
        return self.caes + self.gatos + self.outros

    class Meta:
        verbose_name = 'Boletim de vacinação antirrábica'
        verbose_name_plural = 'Boletins de vacinação antirrábica'

    def __str__(self):
        return f'Vacinação Raiva - {self.data.strftime("%d/%m/%Y")} - Total: {self.total}'