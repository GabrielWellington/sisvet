"""Configuração usada apenas para executar os testes automatizados.

Herda as configurações do projeto e troca o banco por SQLite em memória,
para que os testes possam ser executados sem acesso ao PostgreSQL.
Uso: python manage.py test --settings=config.settings_test
Para testar no próprio PostgreSQL, use apenas: python manage.py test
"""
import os

os.environ.setdefault('SECRET_KEY', 'chave-somente-para-testes')
for _var in ('DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'):
    os.environ.setdefault(_var, '')

from .settings import *  # noqa: E402,F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
