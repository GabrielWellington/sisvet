from django.contrib import admin
from django import forms
from .models import Visita


class VisitaAdminForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = '__all__'
        widgets = {
            'doencas_positivas': forms.CheckboxSelectMultiple,
        }


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    form = VisitaAdminForm

    list_display = (
        'data_visita',
        'nome_responsavel',
        'area',
        'setor',
        'quadra',
        'situacao',
    )

    search_fields = (
        'nome_responsavel',
        'endereco',
        'telefone',
        'animal__nome',
        'tutor__nome',
        'nome_animal_nao_cadastrado',
    )

    list_filter = (
        'area',
        'setor',
        'situacao',
        'data_visita',
    )

    autocomplete_fields = ['animal', 'tutor']
    date_hierarchy = 'data_visita'
    
    class Media:
        js = ('js/filtra_animais_por_tutor.js',)


    fieldsets = (
        ('Localização da visita', {
            'fields': ('area', 'setor', 'quadra', 'data_visita')
        }),
        ('Responsável / endereço', {
            'fields': ('nome_responsavel', 'endereco', 'telefone')
        }),
        ('Animal', {
            'fields': ('tutor', 'animal', 'nome_animal_nao_cadastrado')
        }),
        ('Resultado da visita', {
            'fields': (
                'situacao',
                'doencas_positivas',
                'observacoes',
            )
        }),
    )