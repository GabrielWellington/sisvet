from django.urls import path
from . import views

urlpatterns = [
    path('tutor-do-animal/', views.tutor_do_animal, name='tutor_do_animal'),
]