from django.contrib import admin
from .models import BoletimVacinacaoRaiva


@admin.register(BoletimVacinacaoRaiva)
class BoletimVacinacaoRaivaAdmin(admin.ModelAdmin):
    list_display = ('data', 'municipio', 'posto', 'tipo_posto', 'tipo_vacinacao', 'caes', 'gatos', 'outros', 'total')
    search_fields = ('municipio', 'posto', 'responsavel_preenchimento')
    list_filter = ('tipo_posto', 'tipo_vacinacao', 'data')
    date_hierarchy = 'data'

    def total(self, obj):
        return obj.total