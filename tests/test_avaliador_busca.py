"""Testes do benchmark de qualidade da busca."""

import json
from pathlib import Path
import tempfile
import unittest

from avaliador_busca import AvaliadorBusca
from base_conhecimento import BaseConhecimento


PASTA_PROJETO = Path(__file__).resolve().parents[1]


class TesteAvaliadorBusca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = BaseConhecimento(PASTA_PROJETO / "data" / "base_conhecimento.csv")
        if not cls.base.carregar():
            raise AssertionError(cls.base.erros)
        cls.avaliador = AvaliadorBusca(
            cls.base, PASTA_PROJETO / "data" / "perguntas_avaliacao.csv"
        )
        if not cls.avaliador.carregar_perguntas():
            raise AssertionError(cls.avaliador.erros)
        cls.relatorio = cls.avaliador.executar()

    def test_conjunto_tem_175_perguntas_do_escopo_e_33_fora(self):
        self.assertEqual(self.relatorio["dentro_escopo"]["total"], 175)
        self.assertEqual(self.relatorio["fora_escopo"]["total"], 33)

    def test_todas_as_perguntas_do_escopo_sao_reconhecidas_no_top1(self):
        dados = self.relatorio["dentro_escopo"]
        self.assertEqual(dados["acertos_top1"], 175)
        self.assertEqual(dados["acuracia_top1_percentual"], 100.0)

    def test_perguntas_fora_do_escopo_sao_rejeitadas(self):
        dados = self.relatorio["fora_escopo"]
        self.assertEqual(dados["abstencoes_corretas"], 33)
        self.assertEqual(dados["falsos_positivos"], 0)

    def test_metricas_top3_e_cobertura(self):
        dados = self.relatorio["dentro_escopo"]
        self.assertEqual(dados["acuracia_top3_percentual"], 100.0)
        self.assertEqual(dados["cobertura_percentual"], 100.0)

    def test_resultado_da_pergunta_de_frequencia_escolar(self):
        caso = next(
            item for item in self.relatorio["casos"] if item["id"] == "Q030"
        )
        self.assertEqual(caso["orientacao_prevista"], "15")
        self.assertTrue(caso["acerto_top1"])


    def test_primeiro_emprego_e_canais_de_vagas_sao_separados(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q043", "Q044"):
            with self.subTest(caso=identificador):
                self.assertEqual(casos[identificador]["orientacao_prevista"], "16")
                self.assertTrue(casos[identificador]["acerto_top1"])
        for identificador in ("Q045", "Q046"):
            with self.subTest(caso=identificador):
                self.assertEqual(casos[identificador]["orientacao_prevista"], "25")
                self.assertTrue(casos[identificador]["acerto_top1"])

    def test_perguntas_de_curriculo_sao_reconhecidas(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q047", "Q048", "Q049", "Q050"):
            with self.subTest(caso=identificador):
                self.assertTrue(casos[identificador]["acerto_top1"])

    def test_perguntas_de_servicos_locais_e_progredir_sao_reconhecidas(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q059", "Q060", "Q061", "Q062", "Q063", "Q064", "Q065", "Q066", "Q067", "Q068", "Q069", "Q070", "Q071", "Q072", "Q073", "Q074", "Q075", "Q076", "Q077", "Q078", "Q079", "Q080"):
            with self.subTest(caso=identificador):
                self.assertTrue(casos[identificador]["acerto_top1"])

    def test_novas_perguntas_de_candidatura_e_privacidade_do_curriculo(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q081", "Q082", "Q083", "Q084", "Q085", "Q086", "Q087", "Q088", "Q089", "Q090", "Q091", "Q092"):
            with self.subTest(caso=identificador):
                self.assertTrue(casos[identificador]["acerto_top1"])

    def test_novas_perguntas_sobre_direitos_do_aprendiz(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q093", "Q094", "Q095", "Q096", "Q097", "Q098", "Q099", "Q100", "Q101", "Q102"):
            with self.subTest(caso=identificador):
                self.assertTrue(casos[identificador]["acerto_top1"])


    def test_faqs_adicionais_do_manual_mte(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q111", "Q112", "Q113", "Q114", "Q115", "Q116", "Q117", "Q118"):
            with self.subTest(caso=identificador):
                self.assertTrue(casos[identificador]["acerto_top1"])

    def test_novas_perguntas_fora_do_escopo_sao_recusadas(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q103", "Q104", "Q105", "Q106", "Q107", "Q108", "Q109", "Q110", "Q119", "Q120"):
            with self.subTest(caso=identificador):
                self.assertEqual(casos[identificador]["status"], "abstencao_correta")

    def test_pergunta_como_pedir_demissao_e_reconhecida(self):
        caso = next(item for item in self.relatorio["casos"] if item["id"] == "Q192")
        self.assertEqual(caso["orientacao_prevista"], "46")
        self.assertTrue(caso["acerto_top1"])

    def test_transicao_constitucional_de_jornada_esta_no_benchmark(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        self.assertEqual(casos["Q144"]["orientacao_prevista"], "57")
        self.assertTrue(casos["Q144"]["acerto_top1"])
        self.assertEqual(casos["Q152"]["orientacao_prevista"], "61")
        self.assertTrue(casos["Q152"]["acerto_top1"])

    def test_seguro_desemprego_isolado_e_com_erros_de_digitacao(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        for identificador in ("Q198", "Q199", "Q200", "Q201", "Q202", "Q203", "Q204", "Q208"):
            with self.subTest(caso=identificador):
                self.assertEqual(casos[identificador]["orientacao_prevista"], "68")
                self.assertTrue(casos[identificador]["acerto_top1"])

    def test_erros_de_digitacao_sao_reconhecidos_em_temas_diferentes(self):
        casos = {item["id"]: item for item in self.relatorio["casos"]}
        esperados = {"Q205": "17", "Q206": "16", "Q207": "76"}
        for identificador, orientacao in esperados.items():
            with self.subTest(caso=identificador):
                self.assertEqual(casos[identificador]["orientacao_esperada"], orientacao)
                self.assertTrue(casos[identificador]["acerto_top1"])

    def test_relatorio_json_pode_ser_salvo(self):
        with tempfile.TemporaryDirectory() as temporario:
            destino = Path(temporario) / "relatorio.json"
            AvaliadorBusca.salvar_relatorio(self.relatorio, destino)
            conteudo = json.loads(destino.read_text(encoding="utf-8"))
        self.assertEqual(conteudo["total_casos"], 208)
        self.assertEqual(conteudo["acuracia_geral_percentual"], 100.0)

    def test_cabecalho_invalido_e_rejeitado(self):
        with tempfile.TemporaryDirectory() as temporario:
            arquivo = Path(temporario) / "perguntas.csv"
            arquivo.write_text("id;texto\n1;pergunta\n", encoding="utf-8")
            avaliador = AvaliadorBusca(self.base, arquivo)
            self.assertFalse(avaliador.carregar_perguntas())
            self.assertTrue(any("Cabeçalho inválido" in erro for erro in avaliador.erros))

    def test_id_de_orientacao_inexistente_e_rejeitado(self):
        with tempfile.TemporaryDirectory() as temporario:
            arquivo = Path(temporario) / "perguntas.csv"
            arquivo.write_text(
                "id;tipo;pergunta;orientacao_esperada\n"
                "A1;dentro_escopo;Pergunta de teste;999\n"
                "A2;fora_escopo;Pergunta fora do tema;\n",
                encoding="utf-8",
            )
            avaliador = AvaliadorBusca(self.base, arquivo)
            self.assertFalse(avaliador.carregar_perguntas())
            self.assertTrue(any("orientação esperada inexistente" in erro for erro in avaliador.erros))


if __name__ == "__main__":
    unittest.main(verbosity=2)
