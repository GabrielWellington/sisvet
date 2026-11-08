from django.contrib import admin
from .models import Castracao


@admin.register(Castracao)
class CastracaoAdmin(admin.ModelAdmin):
    list_display = (
        'animal',
        'tutor',
        'data_agendada',
        'periodo',
        'status',
    )
    search_fields = ('animal__nome', 'tutor__nome', 'tutor__cpf', 'tutor__telefone')
    list_filter = ('status', 'periodo', 'data_agendada')
    date_hierarchy = 'data_agendada'
    list_editable = ('status',)
    autocomplete_fields = ['tutor', 'animal']

    class Media:
        js = ('js/filtra_animais_por_tutor.js',)


    # A seleção de animais pelo campo de busca (autocomplete) já lista apenas
    # animais ativos (ver AnimalAdmin.get_queryset). O formulário aceita o animal
    # já gravado, permitindo editar registros antigos de animais que faleceram.