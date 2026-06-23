from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Animal


def tutor_do_animal(request):
    animal_id = request.GET.get('animal_id')
    if not animal_id:
        return JsonResponse({'tutor_id': None})

    try:
        animal = Animal.objects.select_related('tutor').get(pk=animal_id)
        return JsonResponse({
            'tutor_id': animal.tutor.id,
            'tutor_nome': animal.tutor.nome,
        })
    except Animal.DoesNotExist:
        return JsonResponse({'tutor_id': None})