from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
import tempfile

from cadastros.models import Animal, Tutor
from .models import Documento


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DocumentoTests(TestCase):
    def setUp(self):
        self.tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.outro = Tutor.objects.create(nome='Bruno Dias', telefone='14999991111')
        self.animal = Animal.objects.create(tutor=self.tutor, nome='Bidu', especie='CAO', sexo='MACHO')

    def arquivo(self):
        return SimpleUploadedFile('termo.pdf', b'%PDF-1.4 teste', content_type='application/pdf')

    def test_documento_valido_e_armazenado(self):
        documento = Documento(tutor=self.tutor, animal=self.animal, tipo='EXAME', arquivo=self.arquivo())
        documento.full_clean()
        documento.save()
        self.assertTrue(documento.arquivo.name.startswith('documentos/'))

    def test_animal_de_outro_tutor_e_rejeitado(self):
        documento = Documento(tutor=self.outro, animal=self.animal, tipo='EXAME', arquivo=self.arquivo())
        with self.assertRaises(ValidationError):
            documento.full_clean()
