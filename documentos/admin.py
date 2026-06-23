from django.contrib import admin
from .models import Documento


class DocumentoBaseAdmin(admin.ModelAdmin):
    list_display = ('animal', 'tutor', 'criado_em')
    search_fields = ('animal__nome', 'tutor__nome', 'tutor__cpf', 'tutor__telefone')
    list_filter = ('criado_em',)
    readonly_fields = ('criado_em',)
    autocomplete_fields = ['tutor', 'animal']

    class Media:
        js = ('js/filtra_animais_por_tutor.js',)


# Termos de Eutanásia
class TermoEutanasia(Documento):
    class Meta:
        proxy = True
        verbose_name = 'Termo de eutanásia'
        verbose_name_plural = 'Termos de eutanásia'


@admin.register(TermoEutanasia)
class TermoEutanasiaAdmin(DocumentoBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo='EUTANASIA')

    def save_model(self, request, obj, form, change):
        obj.tipo = 'EUTANASIA'
        super().save_model(request, obj, form, change)

    fields = ('tutor', 'animal', 'arquivo', 'observacoes', 'criado_em')


# Autorizações de Procedimento
class AutorizacaoProcedimento(Documento):
    class Meta:
        proxy = True
        verbose_name = 'Autorização de procedimento'
        verbose_name_plural = 'Autorizações de procedimento'


@admin.register(AutorizacaoProcedimento)
class AutorizacaoProcedimentoAdmin(DocumentoBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo='AUTORIZACAO_PROCEDIMENTO')

    def save_model(self, request, obj, form, change):
        obj.tipo = 'AUTORIZACAO_PROCEDIMENTO'
        super().save_model(request, obj, form, change)

    fields = ('tutor', 'animal', 'arquivo', 'observacoes', 'criado_em')


# Exames
class Exame(Documento):
    class Meta:
        proxy = True
        verbose_name = 'Exame'
        verbose_name_plural = 'Exames'


@admin.register(Exame)
class ExameAdmin(DocumentoBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo='EXAME')

    def save_model(self, request, obj, form, change):
        obj.tipo = 'EXAME'
        super().save_model(request, obj, form, change)

    fields = ('tutor', 'animal', 'arquivo', 'observacoes', 'criado_em')


# Outros Documentos
class OutroDocumento(Documento):
    class Meta:
        proxy = True
        verbose_name = 'Outro documento'
        verbose_name_plural = 'Outros documentos'


@admin.register(OutroDocumento)
class OutroDocumentoAdmin(DocumentoBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo='OUTRO')

    def save_model(self, request, obj, form, change):
        obj.tipo = 'OUTRO'
        super().save_model(request, obj, form, change)

    fields = ('tutor', 'animal', 'arquivo', 'observacoes', 'criado_em')