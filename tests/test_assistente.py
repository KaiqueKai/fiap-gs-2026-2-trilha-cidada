"""Testes automatizados do núcleo do Trilha Cidadã."""

import tempfile
import unittest
from pathlib import Path

from assistente import Assistente, CAMPOS_HISTORICO
from base_conhecimento import BaseConhecimento, CABECALHO, normalizar
from orientacao import Orientacao


PASTA_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_BASE_REAL = PASTA_PROJETO / "data" / "base_conhecimento.csv"


class TesteBaseConhecimento(unittest.TestCase):
    def setUp(self):
        self.orientacao = Orientacao(
            "1",
            "Primeiros passos",
            "Carteira de Trabalho Digital",
            ["carteira de trabalho digital", "ctps", "carteira digital"],
            "Acesse o serviço oficial.",
            ["CPF"],
            "Portal gov.br",
            "https://www.gov.br",
            "2026-11-06",
        )
        self.base_real = BaseConhecimento(CAMINHO_BASE_REAL)
        self.assertTrue(self.base_real.carregar())

    @staticmethod
    def _criar_csv(pasta: str, linhas: list[str]) -> Path:
        caminho = Path(pasta) / "base.csv"
        conteudo = ";".join(CABECALHO) + "\n" + "\n".join(linhas) + "\n"
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    @staticmethod
    def _linha(
        identificador="1",
        categoria="Primeiros passos",
        titulo="Carteira Digital",
        chaves="carteira|ctps|digital",
        resposta="Acesse o serviço oficial.",
        documentos="CPF",
        onde="Portal gov.br",
        fonte="https://www.gov.br",
        data="2026-11-06",
    ):
        return ";".join(
            [identificador, categoria, titulo, chaves, resposta, documentos, onde, fonte, data]
        )

    def test_normalizacao_remove_acento_pontuacao_e_espacos(self):
        self.assertEqual(normalizar("  CARTÃO, do SUS!  "), "cartao do sus")

    def test_normalizacao_lida_com_valor_vazio(self):
        self.assertEqual(normalizar(None), "")

    def test_pontuacao_palavra_chave_e_titulo(self):
        pontos = self.base_real.pontuar(
            "Como acessar a carteira de trabalho digital?", self.orientacao
        )
        self.assertEqual(pontos, 6)

    def test_explicacao_da_pontuacao_soma_corretamente(self):
        detalhes = self.base_real.explicar_pontuacao(
            "Como acessar a carteira de trabalho digital?", self.orientacao
        )
        self.assertEqual(
            detalhes["total"], detalhes["pontos_chaves"] + detalhes["pontos_titulo"]
        )
        self.assertIn("carteira de trabalho digital", detalhes["palavras_chave"])
        self.assertIn("digital", detalhes["palavras_titulo"])
        self.assertEqual(detalhes["confianca"], "ALTA")

    def test_palavra_chave_exige_limite_de_palavra(self):
        self.assertEqual(self.base_real.pontuar("sctpsxyz", self.orientacao), 0)
        self.assertEqual(self.base_real.pontuar("minha ctps", self.orientacao), 3)

    def test_confianca_media_a_partir_de_tres_pontos(self):
        detalhes = self.base_real.explicar_pontuacao("minha ctps", self.orientacao)
        self.assertEqual(detalhes["total"], 3)
        self.assertEqual(detalhes["confianca"], "MÉDIA")

    def test_confianca_insuficiente_abaixo_de_tres_pontos(self):
        detalhes = self.base_real.explicar_pontuacao("quero uma orientação", self.orientacao)
        self.assertEqual(detalhes["confianca"], "INSUFICIENTE")

    def test_base_real_atende_requisitos_do_trabalho(self):
        self.assertGreaterEqual(len(self.base_real.orientacoes), 10)
        self.assertGreaterEqual(len(self.base_real.categorias()), 3)
        self.assertEqual(len({item.id for item in self.base_real.orientacoes}), len(self.base_real.orientacoes))
        for item in self.base_real.orientacoes:
            self.assertGreaterEqual(len(item.palavras_chave), 3)
            self.assertTrue(item.fonte.startswith("https://"))
            self.assertRegex(item.verificado_em, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.base_real.validar_requisitos(), [])

    def test_base_real_tem_76_orientacoes(self):
        self.assertEqual(len(self.base_real.orientacoes), 76)



    def test_termo_isolado_transporte_encontra_direito_geral(self):
        ranking = self.base_real.buscar("transporte")
        self.assertGreaterEqual(ranking[0][0], 3)
        self.assertEqual(ranking[0][1].id, "76")

    def test_variante_conducao_encontra_vale_transporte(self):
        ranking = self.base_real.buscar("a empresa tem que pagar minha condução?")
        self.assertGreaterEqual(ranking[0][0], 3)
        self.assertEqual(ranking[0][1].id, "76")

    def test_direitos_trabalhistas_basicos_tem_orientacao_especifica(self):
        perguntas = {
            "Como pedir demissão?": "46",
            "Se eu pedir as contas, quais valores recebo?": "47",
            "Sou mensalista e pedi demissão. Tenho que cumprir aviso?": "48",
            "Em quantos dias a empresa tem que pagar meu acerto?": "49",
            "Compare pedir demissão com ser dispensado sem justa causa: o que muda?": "50",
            "Meu patrão não paga e descumpre o contrato. Posso pedir rescisão indireta?": "51",
            "A empresa quer fazer acordo para me desligar. Como funciona?": "52",
            "Fui dispensado sem justa causa. O que tenho direito a receber?": "53",
            "Fui demitido por justa causa. O que ainda recebo?": "54",
            "Meu salário não caiu. Até que dia a empresa pode pagar?": "55",
            "A jornada de 44 horas vai mudar em dezembro de 2026?": "57",
            "Quanto a mais recebo por fazer hora extra?": "58",
            "Trabalho 8 horas por dia. Quanto tempo tenho para almoçar?": "59",
            "Saí às 23h e querem que eu volte às 7h. Pode?": "60",
            "Quantas folgas semanais são garantidas pela regra de 2026?": "61",
            "Meu chefe me humilha todos os dias. O que posso fazer?": "71",
            "A empresa pode me escalar todo domingo?": "72",
            "Tenho direitos mesmo trabalhando sem registro?": "74",
            "Quando a empresa deve pagar o décimo terceiro?": "75",
        }
        for pergunta, esperado in perguntas.items():
            with self.subTest(pergunta=pergunta):
                ranking = self.base_real.buscar(pergunta)
                self.assertGreaterEqual(ranking[0][0], 3)
                self.assertEqual(ranking[0][1].id, esperado)

    def test_faqs_adicionais_de_direitos_do_aprendiz(self):
        perguntas = {
            "Aprendiz maior de 18 anos tem direito a adicional noturno?": "41",
            "O aprendiz tem direito a intervalo para descanso?": "42",
            "A empresa precisa registrar o ponto nas aulas teóricas do aprendiz?": "43",
            "Jovem aprendiz recebe seguro-desemprego quando acaba o contrato?": "44",
            "Quais descontos podem aparecer no salário do aprendiz?": "45",
        }
        for pergunta, esperado in perguntas.items():
            with self.subTest(pergunta=pergunta):
                self.assertEqual(self.base_real.buscar(pergunta)[0][1].id, esperado)

    def test_perguntas_obvias_sao_direcionadas_a_orientacao_especifica(self):
        perguntas = {
            "Quero encontrar curso de aprendizagem reconhecido pelo SENAI.": "14",
            "Como criar meu currículo dentro do Progredir?": "28",
            "Onde fica a opção Meu Currículo no Progredir?": "28",
            "Como editar meu currículo no Progredir?": "29",
            "Como faço para enviar meu currículo à empresa?": "34",
            "O jovem aprendiz tem direito a tirar férias?": "36",
            "Depois de quanto tempo o aprendiz pode sair de férias?": "36",
            "O aprendiz recebe vale-transporte para ir ao curso?": "37",
            "A empresa precisa fornecer passagem para o jovem aprendiz?": "37",
            "Jovem aprendiz pode trabalhar em feriado?": "38",
            "Podem me escalar no feriado sendo aprendiz?": "38",
            "Tenho 17 anos e querem que eu trabalhe de madrugada. Pode?": "39",
            "As horas do curso de aprendiz contam como jornada?": "40",
        }
        for pergunta, esperado in perguntas.items():
            with self.subTest(pergunta=pergunta):
                ranking = self.base_real.buscar(pergunta)
                self.assertEqual(ranking[0][1].id, esperado)
                self.assertGreaterEqual(ranking[0][0], 3)

    def test_busca_retorna_maior_pontuacao_primeiro(self):
        resultados = self.base_real.buscar("Quero consultar meus contratos na carteira de trabalho")
        self.assertGreaterEqual(resultados[0][0], resultados[-1][0])
        self.assertEqual(resultados[0][1].id, "1")

    def test_categorias_sao_unicas_e_ordenadas(self):
        categorias = self.base_real.categorias()
        self.assertEqual(categorias, sorted(set(categorias), key=str.casefold))
        self.assertEqual(len(categorias), 7)

    def test_consulta_de_uma_palavra_transporte_encontra_orientacao_geral(self):
        ranking = self.base_real.buscar("transporte")
        self.assertEqual(ranking[0][1].id, "76")
        self.assertGreaterEqual(ranking[0][0], 3)

    def test_conducao_e_passagem_sao_equivalentes_a_transporte(self):
        for pergunta in ("condução", "passagem", "ônibus", "metrô"):
            with self.subTest(pergunta=pergunta):
                ranking = self.base_real.buscar(pergunta)
                self.assertEqual(ranking[0][1].id, "76")

    def test_transporte_de_aprendiz_prioriza_orientacao_especifica(self):
        perguntas = {
            "Jovem aprendiz tem direito a transporte?": "37",
            "Preciso de vale-transporte para ir ao curso de aprendizagem.": "37",
        }
        for pergunta, esperado in perguntas.items():
            with self.subTest(pergunta=pergunta):
                self.assertEqual(self.base_real.buscar(pergunta)[0][1].id, esperado)

    def test_busca_reconhece_como_criar_um_curriculo(self):
        assistente = Assistente("Teste", self.base_real, tempfile.mkdtemp())
        resultados, status = assistente.buscar_pergunta("Como criar um currículo?")
        self.assertEqual(status, "encontrado")
        self.assertEqual(resultados[0][1].id, "17")
        self.assertGreaterEqual(resultados[0][0], 3)

    def test_busca_reconhece_curriculo_sem_experiencia(self):
        assistente = Assistente("Teste", self.base_real, tempfile.mkdtemp())
        resultados, status = assistente.buscar_pergunta("Nunca trabalhei. O que coloco no currículo?")
        self.assertEqual(status, "encontrado")
        self.assertEqual(resultados[0][1].id, "18")

    def test_busca_reconhece_vagas_locais_de_itaqua(self):
        assistente = Assistente("Teste", self.base_real, tempfile.mkdtemp())
        resultados, status = assistente.buscar_pergunta("Onde encontro vagas em Itaquaquecetuba?")
        self.assertEqual(status, "encontrado")
        self.assertEqual(resultados[0][1].id, "23")

    def test_busca_entende_pergunta_natural_com_palavra_intermediaria(self):
        assistente = Assistente("Teste", self.base_real, tempfile.mkdtemp())
        resultados, status = assistente.buscar_pergunta("Quero denunciar uma empresa")
        self.assertEqual(status, "encontrado")
        self.assertEqual(resultados[0][1].id, "11")

    def test_arquivo_inexistente_retorna_falha_sem_excecao(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = BaseConhecimento(Path(pasta) / "inexistente.csv")
            self.assertFalse(base.carregar())
            self.assertTrue(any("não encontrado" in erro for erro in base.erros))

    def test_cabecalho_invalido_retorna_falha(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "base.csv"
            caminho.write_text("id;titulo\n1;Teste\n", encoding="utf-8")
            base = BaseConhecimento(caminho)
            self.assertFalse(base.carregar())
            self.assertIn("Cabeçalho inválido. Confira os nomes e a ordem das colunas.", base.erros)

    def test_linha_com_id_duplicado_e_ignorada(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self._criar_csv(
                pasta,
                [self._linha(), self._linha(titulo="Outro título")],
            )
            base = BaseConhecimento(caminho)
            self.assertTrue(base.carregar())
            self.assertEqual(len(base.orientacoes), 1)
            self.assertTrue(any("ID duplicado" in erro for erro in base.erros))

    def test_fonte_sem_https_e_ignorada(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self._criar_csv(
                pasta,
                [self._linha(fonte="http://exemplo.com")],
            )
            base = BaseConhecimento(caminho)
            self.assertFalse(base.carregar())
            self.assertTrue(any("HTTPS" in erro for erro in base.erros))

    def test_data_invalida_e_ignorada(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self._criar_csv(pasta, [self._linha(data="06/11/2026")])
            base = BaseConhecimento(caminho)
            self.assertFalse(base.carregar())
            self.assertTrue(any("data inválida" in erro for erro in base.erros))

    def test_linha_malformada_nao_impede_leitura_das_demais(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self._criar_csv(
                pasta,
                ["linha;com;poucos;campos", self._linha()],
            )
            base = BaseConhecimento(caminho)
            self.assertTrue(base.carregar())
            self.assertEqual(len(base.orientacoes), 1)
            self.assertTrue(any("quantidade de campos inválida" in erro for erro in base.erros))


class TesteAssistente(unittest.TestCase):
    def setUp(self):
        self.base = BaseConhecimento(CAMINHO_BASE_REAL)
        self.assertTrue(self.base.carregar())
        self.orientacao = self.base.orientacoes[0]
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta_temporaria.cleanup)
        self.assistente = Assistente("Teste", self.base, self.pasta_temporaria.name)

    def test_bloqueio_de_dados_pessoais(self):
        self.assertTrue(Assistente.contem_dados_pessoais("meu cpf 12345678900"))
        self.assertTrue(Assistente.contem_dados_pessoais("meu email teste@exemplo.com"))
        self.assertTrue(Assistente.contem_dados_pessoais("1234 5678"))
        self.assertFalse(Assistente.contem_dados_pessoais("1234567"))
        self.assertFalse(Assistente.contem_dados_pessoais("como funciona jovem aprendiz"))

    def test_busca_bloqueia_dados_pessoais(self):
        resultados, status = self.assistente.buscar_pergunta("meu CPF é 12345678900")
        self.assertIsNone(resultados)
        self.assertEqual(status, "dados_pessoais")

    def test_busca_rejeita_pergunta_vazia(self):
        resultados, status = self.assistente.buscar_pergunta("   ")
        self.assertEqual(resultados, [])
        self.assertEqual(status, "pergunta_vazia")

    def test_registro_e_exportacao(self):
        salvo = self.assistente.registrar(
            "pergunta", "como funciona a carteira digital", self.orientacao,
            True, True, 1, 2.4,
        )
        caminho = self.assistente.exportar_csv()
        self.assertTrue(salvo)
        self.assertTrue(caminho.exists())
        self.assertEqual(len(self.assistente.historico), 1)
        self.assertEqual(self.assistente.indicadores()["total"], 1)
        self.assertEqual(len(caminho.read_text(encoding="utf-8").splitlines()), 2)

    def test_pergunta_com_dado_pessoal_nunca_e_registrada(self):
        with self.assertRaises(ValueError):
            self.assistente.registrar(
                "pergunta", "cpf 12345678900", None, False, False, 1, 1
            )
        self.assertEqual(len(self.assistente.historico), 0)

    def test_campos_com_separador_e_quebra_de_linha_sao_limpos(self):
        self.assistente.registrar(
            "pergunta", "Como faço;\npara acessar a carteira?", None,
            False, False, 1, 1,
        )
        registro = self.assistente.historico[0]
        self.assertNotIn(";", registro["pergunta"])
        self.assertNotIn("\n", registro["pergunta"])
        linhas = self.assistente.caminho_historico.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(linhas[1].split(";")), len(CAMPOS_HISTORICO))

    def test_indicadores_calculam_encontradas_resolvidas_e_pendentes(self):
        self.assistente.registrar(
            "pergunta", "carteira digital", self.orientacao, True, True, 1, 2.0
        )
        self.assistente.registrar(
            "pergunta", "não achei como atualizar", None, False, False, 2, 4.0
        )
        dados = self.assistente.indicadores()
        self.assertEqual(dados["total"], 2)
        self.assertEqual(dados["taxa_encontrada"], 50.0)
        self.assertEqual(dados["taxa_resolucao"], 50.0)
        self.assertEqual(dados["taxa_nao_encontrada"], 50.0)
        self.assertEqual(dados["tempo_medio"], 3.0)
        self.assertEqual(dados["tentativas_medias"], 1.5)
        self.assertEqual(len(dados["duvidas_sem_solucao"]), 1)

    def test_indicadores_listam_orientacoes_mais_consultadas(self):
        outra = self.base.orientacoes[1]
        self.assistente.registrar("categoria", self.orientacao.titulo, self.orientacao, True, True, 1, 1)
        self.assistente.registrar("categoria", self.orientacao.titulo, self.orientacao, True, True, 1, 1)
        self.assistente.registrar("categoria", outra.titulo, outra, True, False, 1, 1)
        populares = self.assistente.indicadores()["orientacoes_mais_consultadas"]
        self.assertEqual(populares[0]["id"], self.orientacao.id)
        self.assertEqual(populares[0]["consultas"], 2)

    def test_facilidade_e_indicadores(self):
        self.assertTrue(self.assistente.registrar_facilidade(5))
        dados = self.assistente.indicadores()
        self.assertEqual(dados["facilidade_media"], 5.0)
        self.assertEqual(dados["total_avaliacoes"], 1)
        with self.assertRaises(ValueError):
            self.assistente.registrar_facilidade(6)
        with self.assertRaises(ValueError):
            self.assistente.registrar_facilidade("nota")

    def test_historico_existente_e_carregado(self):
        self.assistente.registrar(
            "pergunta", "carteira digital", self.orientacao, True, True, 1, 2.4
        )
        novo = Assistente("Teste", self.base, self.pasta_temporaria.name)
        self.assertEqual(len(novo.historico), 1)
        self.assertEqual(novo.historico[0]["pergunta"], "carteira digital")

    def test_cabecalho_danificado_nao_e_sobrescrito(self):
        caminho = Path(self.pasta_temporaria.name) / "historico.csv"
        caminho.write_text("colunas;diferentes\n", encoding="utf-8")
        novo = Assistente("Teste", self.base, self.pasta_temporaria.name)
        self.assertFalse(novo._persistencia_historico)
        self.assertTrue(any("cabeçalho" in aviso for aviso in novo.avisos_armazenamento))
        salvo = novo.registrar("pergunta", "pergunta de teste", None, False, False, 1, 1)
        self.assertFalse(salvo)
        self.assertEqual(len(novo.historico), 1)
        self.assertEqual(caminho.read_text(encoding="utf-8"), "colunas;diferentes\n")

    def test_linha_corrompida_e_ignorada_sem_interromper_o_programa(self):
        caminho = Path(self.pasta_temporaria.name) / "historico.csv"
        data = "2026-11-06T12:00:00-03:00"
        caminho.write_text(
            ";".join(CAMPOS_HISTORICO)
            + "\nlinha;corrompida\n"
            + f"{data};pergunta;duvida de teste;1;sim;sim;1;2.0\n",
            encoding="utf-8",
        )
        novo = Assistente("Teste", self.base, self.pasta_temporaria.name)
        self.assertEqual(len(novo.historico), 1)
        self.assertTrue(any("registro ignorado" in aviso for aviso in novo.avisos_armazenamento))

    def test_nota_invalida_no_arquivo_de_avaliacoes_e_ignorada(self):
        caminho = Path(self.pasta_temporaria.name) / "avaliacoes.csv"
        caminho.write_text(
            "data;facilidade\n2026-11-06T12:00:00-03:00;9\n",
            encoding="utf-8",
        )
        novo = Assistente("Teste", self.base, self.pasta_temporaria.name)
        self.assertEqual(novo.avaliacoes, [])
        self.assertTrue(any("registro ignorado" in aviso for aviso in novo.avisos_armazenamento))

    def test_pergunta_como_conseguir_primeiro_emprego_encontra_orientacao(self):
        resultados = self.base.buscar("Como conseguir o primeiro emprego?")
        self.assertEqual(resultados[0][1].id, "16")
        self.assertGreaterEqual(resultados[0][0], 3)
        self.assertEqual(self.base.explicar_pontuacao("Como conseguir o primeiro emprego?", resultados[0][1])["confianca"], "ALTA")

    def test_variacoes_naturais_sao_direcionadas_ao_assunto_correto(self):
        perguntas = {
            "Como arranjar meu primeiro emprego?": "16",
            "Não tenho experiência, onde procuro emprego?": "16",
            "Preciso encontrar uma oportunidade de trabalho.": "16",
            "Onde vejo vagas de emprego?": "25",
            "Como faço cadastro no SINE?": "25",
            "Como me cadastrar para buscar vagas?": "25",
            "Como entrar no mercado de trabalho?": "16",
            "Quero encontrar trabalho sem experiência.": "16",
            "Como me candidatar a uma vaga?": "34",
            "Tem vaga para quem nunca trabalhou?": "16",
            "Como conseguir emprego na minha cidade?": "25",
            "Quero procurar vagas de emprego.": "25",
        }
        for pergunta, esperado in perguntas.items():
            with self.subTest(pergunta=pergunta):
                resultados = self.base.buscar(pergunta)
                self.assertGreaterEqual(resultados[0][0], 3)
                self.assertEqual(resultados[0][1].id, esperado)

    def test_normalizacao_reconhece_sinonimos_e_variacoes_comuns(self):
        from base_conhecimento import normalizar
        self.assertEqual(normalizar("Meu Curriculum Vitae"), "meu curriculo")
        self.assertEqual(normalizar("CVs e currículos"), "curriculo e curriculo")
        self.assertEqual(normalizar("Vagas e entrevistas"), "vaga e entrevista")

    def test_curriculum_vitae_e_cv_encontram_orientacao_de_curriculo(self):
        for pergunta in ("Como criar meu curriculum vitae?", "Como montar meu CV?"):
            with self.subTest(pergunta=pergunta):
                resultados = self.base.buscar(pergunta)
                self.assertGreaterEqual(resultados[0][0], 3)
                self.assertEqual(resultados[0][1].id, "17")

    def test_orientacoes_especificas_de_direitos_do_aprendiz(self):
        perguntas = {
            "O aprendiz tem direito a tirar férias?": "36",
            "Aprendiz recebe vale-transporte para ir ao curso?": "37",
            "Jovem aprendiz pode trabalhar em feriado?": "38",
            "Menor aprendiz pode trabalhar depois das 22 horas?": "39",
            "A empresa pode descontar falta na aula teórica do aprendiz?": "40",
        }
        for pergunta, esperado in perguntas.items():
            with self.subTest(pergunta=pergunta):
                resultados = self.base.buscar(pergunta)
                self.assertGreaterEqual(resultados[0][0], 3)
                self.assertEqual(resultados[0][1].id, esperado)

    def test_seguro_desemprego_isolado_encontra_orientacao_correta(self):
        for pergunta in ("seguro desemprego", "seguro-desemprego", "benefício seguro desemprego"):
            with self.subTest(pergunta=pergunta):
                resultados = self.base.buscar(pergunta)
                self.assertGreaterEqual(resultados[0][0], 3)
                self.assertEqual(resultados[0][1].id, "68")

    def test_busca_corrige_um_caractere_errado_em_termo_conhecido(self):
        perguntas = (
            "seguro desempregp",   # substituição
            "seguro desemprgo",    # remoção
            "seguro desempregoo",  # inserção
            "seguro desempregeo",  # transposição
            "segur desemprego",     # letra faltante em palavra de cinco letras
        )
        for pergunta in perguntas:
            with self.subTest(pergunta=pergunta):
                resultados = self.base.buscar(pergunta)
                self.assertGreaterEqual(resultados[0][0], 3)
                self.assertEqual(resultados[0][1].id, "68")
                detalhes = self.base.explicar_pontuacao(pergunta, resultados[0][1])
                self.assertTrue(detalhes["termos_corrigidos"])

    def test_correcao_de_digitacao_funciona_em_assuntos_diferentes(self):
        perguntas = {
            "Como montar curricuo?": "17",
            "primeiro emprgo": "16",
            "tranpsorte": "76",
        }
        for pergunta, esperado in perguntas.items():
            with self.subTest(pergunta=pergunta):
                resultados = self.base.buscar(pergunta)
                self.assertGreaterEqual(resultados[0][0], 3)
                self.assertEqual(resultados[0][1].id, esperado)
                self.assertTrue(
                    self.base.explicar_pontuacao(pergunta, resultados[0][1])["termos_corrigidos"]
                )

    def test_curriculo_sem_experiencia_supera_orientacao_generica(self):
        resultados = self.base.buscar("Nunca trabalhei. O que coloco no currículo?")
        self.assertGreaterEqual(resultados[0][0], 3)
        self.assertEqual(resultados[0][1].id, "18")

    def test_privacidade_no_curriculo_tem_orientacao_especifica(self):
        resultados = self.base.buscar("Precisa colocar foto no currículo?")
        self.assertGreaterEqual(resultados[0][0], 3)
        self.assertEqual(resultados[0][1].id, "35")

    def test_candidatura_generica_nao_e_confundida_com_progredir(self):
        resultados = self.base.buscar("Como me candidatar a uma vaga?")
        self.assertGreaterEqual(resultados[0][0], 3)
        self.assertEqual(resultados[0][1].id, "34")


    def test_ia_interpreta_toda_pergunta_mesmo_com_busca_local_forte(self):
        assistente = Assistente("Teste", self.base, tempfile.mkdtemp())

        class IACompleta:
            def __init__(self):
                self.chamadas = 0
                self.ultimo_erro = ""
            def analisar(self, pergunta, orientacoes):
                self.chamadas += 1
                self.assert_catalogo = len(orientacoes)
                return {
                    "escopo": "dentro",
                    "titulo": "Como conseguir emprego",
                    "ids_relevantes": ["16"],
                    "ids_fontes": ["16"],
                    "resposta": "Comece procurando vagas de entrada e preparando seu currículo.",
                    "consultas": [],
                }

        ia = IACompleta()
        assistente.expansor_ia = ia
        resultados, status = assistente.buscar_pergunta("emprego")
        self.assertEqual(status, "encontrado")
        self.assertEqual(ia.chamadas, 1)
        self.assertEqual(resultados[0][1].id, "16")
        self.assertTrue(resultados[0][1].gerada_por_ia)
        self.assertEqual(resultados[0][1].resposta, "Comece procurando vagas de entrada e preparando seu currículo.")

    def test_ia_classifica_assunto_fora_do_escopo(self):
        assistente = Assistente("Teste", self.base, tempfile.mkdtemp())

        class IACompleta:
            ultimo_erro = ""
            def analisar(self, pergunta, orientacoes):
                return {"escopo": "fora", "ids_relevantes": [], "ids_fontes": [], "resposta": "", "consultas": []}

        assistente.expansor_ia = IACompleta()
        resultados, status = assistente.buscar_pergunta("como fazer um bolo de chocolate")
        self.assertEqual(status, "fora_escopo")
        self.assertEqual(resultados, [])

    def test_falso_negativo_de_escopo_da_ia_nao_bloqueia_correspondencia_local_forte(self):
        assistente = Assistente("Teste", self.base, tempfile.mkdtemp())

        class IACompleta:
            ultimo_erro = ""
            def analisar(self, pergunta, orientacoes):
                return {"escopo": "fora", "ids_relevantes": [], "ids_fontes": [], "resposta": "", "consultas": []}

        assistente.expansor_ia = IACompleta()
        resultados, status = assistente.buscar_pergunta("emprego")
        self.assertEqual(status, "encontrado")
        self.assertEqual(resultados[0][1].id, "16")

    def test_termos_isolados_emprego_e_seguro_encontram_assuntos(self):
        casos = {"emprego": "16", "seguro": "68", "transporte": "76"}
        for pergunta, esperado in casos.items():
            with self.subTest(pergunta=pergunta):
                ranking = self.base.buscar(pergunta)
                self.assertGreaterEqual(ranking[0][0], 3)
                self.assertEqual(ranking[0][1].id, esperado)



    def test_falha_de_ia_nao_esconde_diagnostico_e_mantem_fallback_local(self):
        assistente = Assistente("Teste", self.base, tempfile.mkdtemp())

        class IAIndisponivel:
            ultimo_erro = "Ollama HTTP 401: chave inválida"
            def analisar(self, pergunta, orientacoes):
                return None

        assistente.expansor_ia = IAIndisponivel()
        resultados, status = assistente.buscar_pergunta("emprego")
        self.assertEqual(status, "encontrado")
        self.assertEqual(resultados[0][1].id, "16")
        self.assertIn("401", assistente.ultimo_erro_ia)



if __name__ == "__main__":
    unittest.main(verbosity=2)
