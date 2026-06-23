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


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "animal":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(status='ATIVO')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)