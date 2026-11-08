from datetime import date
import io

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from docx import Document

from atendimentos.models import Atendimento
from cadastros.models import Animal, Tutor
from castracoes.models import Castracao
from vacinacoes.models import BoletimVacinacaoRaiva
from .views import _coleta_dados_castracoes, _coleta_dados_mes


class BaseRelatorio(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('vet', password='senha-forte-123', is_staff=True)
        self.tutor = Tutor.objects.create(nome='Ana Reis', telefone='14999990000')
        self.cao = Animal.objects.create(tutor=self.tutor, nome='Bidu', especie='CAO', sexo='MACHO')
        self.gata = Animal.objects.create(tutor=self.tutor, nome='Mimi', especie='GATO', sexo='FEMEA')


class AcessoTests(BaseRelatorio):
    def test_relatorios_exigem_login(self):
        for nome in ('detalhes_castracoes', 'exportar_castracoes_docx', 'relatorio_anual'):
            resposta = self.client.get(reverse(nome))
            self.assertEqual(resposta.status_code, 302, nome)
            self.assertTrue(resposta['Location'].startswith('/admin/login/'), nome)

    def test_ano_ou_mes_invalidos_nao_provocam_erro(self):
        self.client.force_login(self.usuario)
        for consulta in ('?mes=13&ano=2026', '?mes=5&ano=0', '?mes=5&ano=abc', '?mes=x&ano=2026'):
            self.assertEqual(self.client.get(reverse('detalhes_castracoes') + consulta).status_code, 200, consulta)
            self.assertEqual(self.client.get(reverse('exportar_castracoes_docx') + consulta).status_code, 200, consulta)
        for consulta in ('?ano=abc', '?ano=0', '?ano=99999'):
            self.assertEqual(self.client.get(reverse('relatorio_anual') + consulta).status_code, 200, consulta)


class CastracoesMensalTests(BaseRelatorio):
    def setUp(self):
        super().setUp()
        dia = date(2026, 9, 10)
        Castracao.objects.create(tutor=self.tutor, animal=self.cao, data_agendada=dia, periodo='MANHA', status='REALIZADA')
        Castracao.objects.create(tutor=self.tutor, animal=self.gata, data_agendada=dia, periodo='TARDE', status='COMPARECEU')
        Castracao.objects.create(tutor=self.tutor, animal=self.cao, data_agendada=dia, periodo='MANHA', status='FALTOU')

    def test_contadores_e_criterio_de_castracao_efetivada(self):
        d = _coleta_dados_castracoes(9, 2026)
        self.assertEqual(d['total_mes'], 3)
        self.assertEqual(d['realizadas_mes'], 1)
        self.assertEqual(d['compareceram_mes'], 1)
        self.assertEqual(d['faltaram_mes'], 1)
        self.assertEqual(d['cao_macho'] + d['gato_femea'], 2)
        self.assertEqual(d['taxa_comparecimento'], 66.7)

    def test_resumo_anual_usa_o_mesmo_criterio(self):
        mes = _coleta_dados_mes(2026, 9)
        self.assertEqual(mes['cao_macho'], 1)
        self.assertEqual(mes['gato_femea'], 1)

    def test_tela_e_exportacao_mostram_os_mesmos_numeros(self):
        self.client.force_login(self.usuario)
        tela = self.client.get(reverse('detalhes_castracoes') + '?mes=9&ano=2026')
        self.assertEqual(tela.context['faltaram_mes'], 1)
        arquivo = self.client.get(reverse('exportar_castracoes_docx') + '?mes=9&ano=2026')
        doc = Document(io.BytesIO(arquivo.content))
        valores = [c.text for c in doc.tables[0].rows[1].cells]
        self.assertEqual(valores, ['3', '0', '1', '1', '1', '0'])


class ResumoAnualTests(BaseRelatorio):
    def test_total_anual_igual_a_soma_dos_meses(self):
        BoletimVacinacaoRaiva.objects.create(tipo_posto='FIXO', tipo_vacinacao='ROTINA',
                                             data=date(2026, 3, 2), caes=10)
        Atendimento.objects.create(animal=self.cao, veterinaria=self.usuario, queixa_principal='Tosse')
        Castracao.objects.create(tutor=self.tutor, animal=self.cao, data_agendada=date(2026, 7, 1),
                                 periodo='MANHA', status='REALIZADA')
        meses = [_coleta_dados_mes(2026, m)['total_animais'] for m in range(1, 13)]

        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse('relatorio_anual') + '?ano=2026')
        self.assertEqual(resposta.status_code, 200)
        doc = Document(io.BytesIO(resposta.content))
        ultima_linha = doc.tables[0].rows[-1]
        self.assertIn(f'TOTAL DE ANIMAIS: {sum(meses):02d}', ultima_linha.cells[3].text)
