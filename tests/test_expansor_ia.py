"""Testes da integração opcional com modelo de linguagem."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from expansor_ia import ExpansorConsultaIA
from assistente import Assistente
from base_conhecimento import BaseConhecimento


class RespostaFake:
    def __init__(self, dados):
        self.dados = dados

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.dados).encode("utf-8")


class TesteExpansorConsultaIA(unittest.TestCase):
    def test_ia_permanece_desativada_sem_configuracao(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(ExpansorConsultaIA.do_projeto(Path(tempfile.mkdtemp())))

    def test_ollama_cloud_sem_chave_permanece_desativado(self):
        with patch.dict("os.environ", {}, clear=True):
            with tempfile.TemporaryDirectory() as pasta:
                Path(pasta, ".env").write_text(
                    "OLLAMA_BASE_URL=https://ollama.com\nOLLAMA_MODEL=gemma4:31b\n",
                    encoding="utf-8",
                )
                self.assertIsNone(ExpansorConsultaIA.do_projeto(pasta))

    def test_consulta_com_dados_pessoais_nao_e_enviada(self):
        modelo = ExpansorConsultaIA("http://localhost:11434", "modelo-teste")
        with patch("expansor_ia.urllib.request.urlopen") as chamada:
            self.assertEqual(modelo.expandir("meu telefone 11987654321"), [])
        chamada.assert_not_called()

    def test_modelo_retorna_parafrase_sem_gerar_resposta(self):
        modelo = ExpansorConsultaIA("http://localhost:11434", "modelo-teste")
        payload = {
            "message": {
                "content": json.dumps({"consultas": ["vale transporte", "passagem para trabalhar"]})
            }
        }
        with patch("expansor_ia.urllib.request.urlopen", return_value=RespostaFake(payload)) as chamada:
            consultas = modelo.expandir("ajuda com deslocamento laboral", ["Vale-transporte"])
        self.assertEqual(consultas, ["vale transporte", "passagem para trabalhar"])
        self.assertEqual(chamada.call_count, 1)

    def test_resposta_da_ia_e_limitada_e_filtrada(self):
        modelo = ExpansorConsultaIA("http://localhost:11434", "modelo-teste")
        payload = {
            "message": {
                "content": json.dumps({
                    "consultas": [
                        "vale transporte", "vale transporte", "", "12345678 dado pessoal",
                        "passagem", "deslocamento", "ônibus", "quinta opção"
                    ]
                })
            }
        }
        with patch("expansor_ia.urllib.request.urlopen", return_value=RespostaFake(payload)):
            consultas = modelo.expandir("transporte")
        self.assertEqual(consultas, ["vale transporte", "passagem", "deslocamento", "ônibus"])

    def test_falha_de_rede_nao_interrompe_atendimento(self):
        modelo = ExpansorConsultaIA("http://localhost:11434", "modelo-teste")
        with patch("expansor_ia.urllib.request.urlopen", side_effect=TimeoutError):
            self.assertEqual(modelo.expandir("pergunta pouco clara"), [])

    def test_expansao_ia_recupera_orientacao_mas_nao_cria_resposta(self):
        raiz = Path(__file__).resolve().parents[1]
        base = BaseConhecimento(raiz / "data" / "base_conhecimento.csv")
        self.assertTrue(base.carregar())
        assistente = Assistente("Teste", base, tempfile.mkdtemp())

        class ExpansorFake:
            def expandir(self, _pergunta, _titulos):
                return ["benefício de transporte para trabalhadores"]

        assistente.expansor_ia = ExpansorFake()
        resultados, status = assistente.buscar_pergunta("ajuda com deslocamento laboral")
        self.assertEqual(status, "encontrado")
        self.assertEqual(resultados[0][1].id, "76")
        explicacao = assistente.explicar_busca("ajuda com deslocamento laboral", resultados[0][1])
        self.assertTrue(explicacao["busca_ampliada_ia"])
        self.assertEqual(explicacao["consulta_utilizada"], "benefício de transporte para trabalhadores")
        self.assertTrue(resultados[0][1].fonte.startswith("https://"))


    def test_analisar_considera_catalogo_completo_e_retorna_ids_validos(self):
        modelo = ExpansorConsultaIA("http://localhost:11434", "modelo-teste")
        raiz = Path(__file__).resolve().parents[1]
        base = BaseConhecimento(raiz / "data" / "base_conhecimento.csv")
        self.assertTrue(base.carregar())
        resposta = {
            "escopo": "dentro",
            "titulo": "Orientação sobre seguro-desemprego",
            "ids_relevantes": ["68", "9999"],
            "ids_fontes": ["68"],
            "resposta": "O seguro-desemprego é um benefício para quem atende aos requisitos legais.",
            "consultas": ["benefício para trabalhador dispensado"],
        }
        with patch.object(modelo, "_chat_json", return_value=resposta) as chamada:
            analise = modelo.analisar("seguro", base.orientacoes)
        self.assertEqual(analise["escopo"], "dentro")
        self.assertEqual(analise["ids_relevantes"], ["68"])
        self.assertEqual(analise["ids_fontes"], ["68"])
        self.assertEqual(analise["consultas"], ["benefício para trabalhador dispensado"])
        chamada.assert_called_once()
        self.assertIn("Quem pode receber seguro-desemprego", str(chamada.call_args))

    def test_analisar_bloqueia_dados_pessoais_antes_da_chamada(self):
        modelo = ExpansorConsultaIA("http://localhost:11434", "modelo-teste")
        with patch.object(modelo, "_chat_json") as chamada:
            self.assertIsNone(modelo.analisar("meu CPF 12345678900", []))
        chamada.assert_not_called()

    def test_teste_de_conexao_confirma_resposta_real(self):
        modelo = ExpansorConsultaIA("https://ollama.com", "gemma4:31b", "chave-teste")
        with patch.object(modelo, "_chat_json", return_value={"ok": True}):
            sucesso, mensagem = modelo.testar_conexao()
        self.assertTrue(sucesso)
        self.assertIn("gemma4:31b", mensagem)



if __name__ == "__main__":
    unittest.main()
