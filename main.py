"""Ponto de entrada do Trilha Cidadã."""

import argparse
from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento
from avaliador_busca import AvaliadorBusca
from expansor_ia import ExpansorConsultaIA


PASTA_PROJETO = Path(__file__).resolve().parent


def iniciar_interface(assistente: Assistente) -> None:
    """Inicia a interface gráfica sem impedir o uso do terminal em caso de falha."""
    try:
        from interface import TrilhaCidadaApp

        TrilhaCidadaApp(assistente).executar()
    except ImportError as erro:
        print("Não foi possível carregar a interface gráfica.")
        print(f"Detalhe: {erro}")
        print("Execute sem --gui para utilizar o modo terminal.")
    except Exception as erro:
        print("A interface gráfica não pôde ser iniciada.")
        print(f"Detalhe: {erro}")
        print("Os arquivos e o modo terminal continuam disponíveis.")


def exibir_diagnostico(base: BaseConhecimento, carregou: bool) -> int:
    """Mostra uma checagem rápida da base e retorna código de sucesso ou falha."""
    print("\nTRILHA CIDADÃ — DIAGNÓSTICO DA BASE")
    print(f"Arquivo: {base.caminho}")
    print(f"Leitura: {'OK' if carregou else 'FALHOU'}")
    print(f"Orientações válidas: {len(base.orientacoes)}")
    print(f"Categorias: {len(base.categorias())}")

    if base.erros:
        print("\nProblemas encontrados:")
        for erro in base.erros:
            print(f"- {erro}")
    if base.avisos:
        print("\nRequisitos que precisam de atenção:")
        for aviso in base.avisos:
            print(f"- {aviso}")

    if carregou and not base.erros and not base.avisos:
        print("\nResultado: base aprovada na validação estrutural.")
        return 0

    print("\nResultado: revise os problemas acima antes da entrega.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trilha Cidadã — IA para primeiro emprego, empregabilidade e direitos do trabalhador"
    )
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--gui", action="store_true", help="Abre a interface gráfica")
    modos.add_argument("--terminal", action="store_true", help="Abre o atendimento interativo no terminal")
    modos.add_argument(
        "--validar-base",
        action="store_true",
        help="Confere estrutura, fontes, datas e requisitos mínimos do CSV",
    )
    modos.add_argument(
        "--avaliar-busca",
        action="store_true",
        help="Executa o benchmark de perguntas para medir a qualidade da busca local",
    )
    modos.add_argument(
        "--testar-ia",
        action="store_true",
        help="Faz uma chamada real ao provedor configurado no .env",
    )
    args = parser.parse_args()

    caminho_csv = PASTA_PROJETO / "data" / "base_conhecimento.csv"
    base = BaseConhecimento(caminho_csv)
    carregou = base.carregar()

    if args.validar_base:
        return exibir_diagnostico(base, carregou)

    if args.testar_ia:
        print("\nTRILHA CIDADÃ — TESTE REAL DE CONEXÃO COM IA")
        modelo_ia = ExpansorConsultaIA.do_projeto(PASTA_PROJETO)
        if modelo_ia is None:
            print("IA não configurada. Confira OLLAMA_BASE_URL, OLLAMA_MODEL e OLLAMA_API_KEY no .env.")
            return 1
        print(f"Provedor: {modelo_ia.base_url}")
        print(f"Modelo: {modelo_ia.modelo}")
        print("Chave: configurada (valor oculto)")
        sucesso, mensagem = modelo_ia.testar_conexao()
        print(("\nAPROVADO: " if sucesso else "\nFALHOU: ") + mensagem)
        return 0 if sucesso else 1

    if args.avaliar_busca:
        if not carregou:
            print("A avaliação não pode continuar porque a base não foi carregada.")
            return 1
        avaliador = AvaliadorBusca(
            base, PASTA_PROJETO / "data" / "perguntas_avaliacao.csv"
        )
        if not avaliador.carregar_perguntas():
            print("Não foi possível carregar o conjunto de avaliação:")
            for erro in avaliador.erros:
                print(f"- {erro}")
            return 1
        relatorio = avaliador.executar()
        AvaliadorBusca.exibir_resumo(relatorio)
        caminho_relatorio = PASTA_PROJETO / "reports" / "avaliacao_busca.json"
        AvaliadorBusca.salvar_relatorio(relatorio, caminho_relatorio)
        print(f"\nRelatório completo salvo em: {caminho_relatorio}")
        return 0

    for erro in base.erros:
        print(f"Aviso na base: {erro}")
    for aviso in base.avisos:
        print(f"Atenção: {aviso}")

    if not carregou:
        print("A base de conhecimento não pôde ser carregada.")
        print("O programa continuará aberto, mas a busca não terá orientações disponíveis.")

    assistente = Assistente("Trilha Cidadã", base, PASTA_PROJETO / "data")

    if args.gui:
        iniciar_interface(assistente)
    else:
        assistente.executar_terminal()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
