"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from relatorios.views import dashboard, relatorio_geral, gerar_resumo_anual, detalhes_castracoes, exportar_castracoes_docx


def home(request):
    return redirect('/admin/')

urlpatterns = [
    path('', home),

    path('relatorio-geral/', relatorio_geral, name='relatorio_geral'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('cadastros/', include('cadastros.urls')),
    
    path('relatorio-anual/', gerar_resumo_anual, name='relatorio_anual'),
    path('detalhes-castracoes/', detalhes_castracoes, name='detalhes_castracoes'),
    path('detalhes-castracoes/exportar/', exportar_castracoes_docx, name='exportar_castracoes_docx'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = 'SisVet Promissão'
admin.site.site_title = 'SisVet Promissão'
admin.site.index_title = 'Painel Administrativo'