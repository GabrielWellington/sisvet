from django.contrib import admin
from .models import Tutor, Animal, ObitoAnimal
from atendimentos.models import Atendimento
from castracoes.models import Castracao
from documentos.models import Documento
from visitas.models import Visita


class AnimalInline(admin.TabularInline):
    model = Animal
    extra = 1
    fields = ('nome', 'especie', 'sexo', 'raca', 'status')
    show_change_link = True


class AtendimentoInline(admin.TabularInline):
    model = Atendimento
    extra = 0
    fields = (
        'data_atendimento',
        'veterinaria',
        'queixa_principal',
        'diagnostico',
        'doenca_confirmada',
        'status',
    )
    readonly_fields = (
        'data_atendimento',
        'veterinaria',
        'queixa_principal',
        'diagnostico',
        'doenca_confirmada',
        'status',
    )
    can_delete = False
    show_change_link = True
    verbose_name = 'Atendimento anterior'
    verbose_name_plural = 'Histórico de atendimentos'

    def has_add_permission(self, request, obj=None):
        return False


class CastracaoInline(admin.TabularInline):
    model = Castracao
    extra = 0
    fields = ('data_agendada', 'periodo', 'status')
    readonly_fields = ('data_agendada', 'periodo', 'status')
    can_delete = False
    show_change_link = True
    verbose_name = 'Castração'
    verbose_name_plural = 'Histórico de castrações'

    def has_add_permission(self, request, obj=None):
        return False


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    fields = ('tipo', 'arquivo', 'criado_em')
    readonly_fields = ('tipo', 'arquivo', 'criado_em')
    can_delete = False
    show_change_link = True
    verbose_name = 'Documento'
    verbose_name_plural = 'Documentos do animal'

    def has_add_permission(self, request, obj=None):
        return False


class VisitaInline(admin.TabularInline):
    model = Visita
    extra = 0
    fields = ('data_visita', 'area', 'setor', 'quadra', 'situacao')
    readonly_fields = ('data_visita', 'area', 'setor', 'quadra', 'situacao')
    can_delete = False
    show_change_link = True
    verbose_name = 'Visita'
    verbose_name_plural = 'Histórico de visitas'

    def has_add_permission(self, request, obj=None):
        return False


class ObitoInline(admin.TabularInline):
    model = ObitoAnimal
    extra = 0
    fields = ('data_obito', 'tipo', 'origem', 'motivo')
    readonly_fields = ('data_obito', 'tipo', 'origem', 'motivo')
    can_delete = False
    show_change_link = True
    verbose_name = 'Óbito'
    verbose_name_plural = 'Óbito registrado'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'cpf')
    search_fields = ('nome', 'cpf', 'telefone')
    inlines = [AnimalInline]


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tutor', 'especie', 'sexo', 'raca', 'peso', 'status')
    search_fields = (
        'nome',
        'tutor__nome',
        'tutor__telefone',
        'tutor__cpf',
        'especie_outro',
    )
    list_filter = ('especie', 'sexo', 'status')
    autocomplete_fields = ['tutor']

    fieldsets = (
        ('Dados do animal', {
            'fields': ('tutor', 'nome', 'especie', 'especie_outro', 'sexo', 'raca', 'cor')
        }),
        ('Características físicas', {
            'fields': ('idade_aproximada', 'peso')
        }),
        ('Observações e status', {
            'fields': ('observacoes', 'status')
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        return [AtendimentoInline, CastracaoInline, DocumentoInline, VisitaInline, ObitoInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status='ATIVO')

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        tutor_id = request.GET.get('tutor_id')
        if tutor_id:
            queryset = queryset.filter(tutor_id=tutor_id)
        return queryset, may_have_duplicates

@admin.register(ObitoAnimal)
class ObitoAnimalAdmin(admin.ModelAdmin):
    list_display = ('animal', 'tutor', 'tipo', 'origem', 'data_obito')
    search_fields = ('animal__nome', 'tutor__nome', 'tutor__cpf', 'tutor__telefone')
    list_filter = ('tipo', 'origem', 'data_obito')
    autocomplete_fields = ['animal', 'tutor']
    date_hierarchy = 'data_obito'

    class Media:
        js = ('js/filtra_animais_por_tutor.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.animal and obj.animal.status != 'FALECIDO':
            obj.animal.status = 'FALECIDO'
            obj.animal.save()