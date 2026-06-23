from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Atendimento, Doenca, FotoAtendimento
from django import forms


@admin.register(Doenca)
class DoencaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class AtendimentoAdminForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'doenca_confirmada' in self.fields:
            self.fields['doenca_confirmada'].queryset = Doenca.objects.all()


class FotoAtendimentoInline(admin.TabularInline):
    model = FotoAtendimento
    extra = 1
    readonly_fields = ('criado_em',)


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    form = AtendimentoAdminForm
    list_display = ('animal', 'veterinaria', 'data_atendimento', 'status')
    search_fields = ('animal__nome', 'animal__tutor__nome', 'veterinaria__username')
    list_filter = ('status', 'data_atendimento', 'veterinaria')
    readonly_fields = ('data_atendimento', 'veterinaria', 'link_ficha_animal')
    date_hierarchy = 'data_atendimento'
    inlines = [FotoAtendimentoInline]
    autocomplete_fields = ['animal']

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                ('Informações principais', {
                    'fields': ('animal', 'veterinaria', 'status')
                }),
                ('Triagem', {
                    'fields': (
                        'queixa_principal',
                        'historico_clinico',
                        'sintomas',
                        'peso_no_atendimento',
                        'temperatura',
                    )
                }),
                ('Conclusão clínica', {
                    'fields': (
                        'diagnostico',
                        'tratamento',
                        'observacoes',
                        'doenca_confirmada',
                    )
                }),
            )
        return (
            ('Informações principais', {
                'fields': ('animal', 'link_ficha_animal', 'veterinaria', 'status')
            }),
            ('Triagem', {
                'fields': (
                    'queixa_principal',
                    'historico_clinico',
                    'sintomas',
                    'peso_no_atendimento',
                    'temperatura',
                )
            }),
            ('Conclusão clínica', {
                'fields': (
                    'diagnostico',
                    'tratamento',
                    'observacoes',
                    'doenca_confirmada',
                )
            }),
        )

    def link_ficha_animal(self, obj):
        if obj and obj.animal_id:
            url = reverse('admin:cadastros_animal_change', args=[obj.animal_id])
            return format_html(
                '<a href="{}" target="_blank" style="background:#17a2b8;color:#fff;padding:6px 12px;border-radius:4px;text-decoration:none;font-weight:500;">'
                '🔍 Abrir ficha completa do animal (histórico, castrações, óbitos, documentos)'
                '</a>',
                url
            )
        return ''

    link_ficha_animal.short_description = 'Ficha do animal'

    def save_model(self, request, obj, form, change):
        if not obj.veterinaria_id:
            obj.veterinaria = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, 'perfil') and request.user.perfil.tipo == 'ADMIN':
            return qs

        return qs.filter(veterinaria=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "animal":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(status='ATIVO')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FotoAtendimento)
class FotoAtendimentoAdmin(admin.ModelAdmin):
    list_display = ('atendimento', 'descricao', 'criado_em')
    search_fields = ('atendimento__animal__nome', 'descricao')
    list_filter = ('criado_em',)