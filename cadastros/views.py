from django.http import JsonResponse
from .models import Animal


def tutor_do_animal(request):
    """Retorna o tutor de um animal para o preenchimento automático dos formulários.

    Exige usuário autenticado com acesso ao painel; sem isso responde 403,
    sem expor dados de tutores.
    """
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'erro': 'Acesso não autorizado.'}, status=403)

    animal_id = request.GET.get('animal_id')
    if not animal_id or not str(animal_id).isdigit():
        return JsonResponse({'tutor_id': None})

    animal = Animal.objects.select_related('tutor').filter(pk=animal_id).first()
    if animal is None:
        return JsonResponse({'tutor_id': None})
    return JsonResponse({
        'tutor_id': animal.tutor.id,
        'tutor_nome': animal.tutor.nome,
    })
