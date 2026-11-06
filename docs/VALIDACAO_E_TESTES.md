# Plano de validação e testes — V4.5.0

## Diagnóstico estrutural da base

```bash
python main.py --validar-base
```

Resultado esperado: leitura concluída, **76 orientações**, **7 categorias** e nenhum erro estrutural.

## Benchmark de busca

```bash
python main.py --avaliar-busca
```

Conjunto esperado: **208 perguntas**, sendo 175 dentro do escopo e 33 fora do escopo. O resultado de referência da V4.5.0 foi 175/175 acertos top-1 e 33/33 abstenções corretas. Consulte [AVALIACAO_DA_BUSCA.md](AVALIACAO_DA_BUSCA.md) para entender as limitações dessas métricas internas.

## Testes automatizados

Na versão V4.5.0, a suíte contém **87 testes**, todos aprovados na última execução local do pacote. Os testes da camada de IA usam respostas simuladas para validar parsing, seleção de IDs, classificação de escopo e proteção de dados; não comprovam uma chamada Cloud com a chave do usuário.


```bash
python -m unittest discover -s tests -v
```

A suíte cobre normalização, pontuação, termos isolados, erros de digitação, seleção semântica simulada, síntese com registros selecionados, classificação de escopo, integridade da base, fontes HTTPS, datas, histórico, exportação, avaliações, privacidade e falhas de rede. Para validar a conexão real configurada no `.env`, execute `py -3 main.py --testar-ia`.

## Teste real do provedor

```powershell
py -3 main.py --testar-ia
```

O resultado deve mostrar `APROVADO` e o modelo configurado. Se falhar, use o texto de diagnóstico (sem compartilhar a chave) para corrigir o `.env`, a permissão ou a conexão.

## Testes manuais recomendados

1. `emprego` — a busca local deve localizar primeiro emprego e a IA deve interpretar o pedido amplo.
2. `seguro` — deve assumir seguro-desemprego no contexto de trabalho e informar a interpretação.
3. `transporte` — orientação geral de vale-transporte.
4. `seguro desemprego` — orientação 68.
5. `seguro desempregp` — corrigir a digitação e encontrar a orientação 68.
6. `Como montar curricuo?` — corrigir a palavra e encontrar a orientação 17.
7. `primeiro emprgo` — corrigir a palavra e encontrar a orientação 16.
8. `tranpsorte` — corrigir a transposição e encontrar a orientação 76.
9. `Como faço para começar no mercado de trabalho?` — IA deve combinar orientação de primeiro emprego e canais de vagas.
10. `Como pedir demissão?` — orientação 46.
11. `Se eu pedir as contas, quais valores recebo?` — orientação 47.
12. `Sou mensalista e pedi demissão. Tenho que cumprir aviso?` — orientação 48.
13. `Em quantos dias a empresa tem que pagar meu acerto?` — orientação 49.
14. `Fui demitido por justa causa. O que ainda recebo?` — orientação 54.
15. `A jornada de 44 horas vai mudar em dezembro de 2026?` — orientação 57.
16. `Trabalho 8 horas por dia. Quanto tempo tenho para almoçar?` — orientação 59.
17. `Meu chefe me humilha todos os dias. O que posso fazer?` — orientação 71.
18. `Como consertar a tela do celular?` — deve ser recusada por estar fora do escopo.
19. Digitar uma sequência de oito ou mais dígitos — deve ser bloqueada e não registrada nem enviada ao provedor.
20. `Como fazer bolo de chocolate?` — IA deve classificar como fora do escopo.

Em consultas respondidas pela IA, confirmar que a tela identifica a participação do modelo, exibe os links e as datas dos registros utilizados e não apresenta regras legais sem sustentação nos registros. Em caso de falha do provedor, confirmar que a interface informa o problema sem fingir que a IA respondeu.

## Teste obrigatório com pessoas reais — parcial

Conforme relato da equipe em 06/11/2026, três pessoas participaram e formularam três perguntas cada, totalizando nove atendimentos manuais. A equipe informou que todos os nove testes tiveram resultado positivo. Os enunciados e as notas individuais não foram fornecidos, portanto não são calculadas taxas detalhadas nem uma média de facilidade.

| Indicador | Resultado informado |
|---|---|
| Participantes | 3 pessoas (confirmar que não fazem parte da equipe) |
| Atendimentos realizados | 9 |
| Resultado qualitativo | 9 resultados positivos, conforme relato da equipe |
| Facilidade média | Não informada |
| Dúvidas sem solução | Não relatadas |
| Pendência | Realizar pelo menos mais 1 atendimento e registrar as avaliações disponíveis |

O requisito só estará integralmente cumprido após pelo menos dez atendimentos reais com no mínimo três pessoas de fora da equipe. Não inventar respostas, notas ou comentários ausentes.


## Atendimento manual pelo terminal

O programa pode ser testado como um chatbot de texto, utilizando a mesma IA configurada no `.env`:

```powershell
py -3 main.py --terminal
```

No menu, selecione `1. Fazer uma pergunta`, escreva uma pergunta livre, aguarde a análise da IA e responda `s` ou `n` para registrar se a orientação ajudou. Repita com perguntas diferentes. Use `3` para consultar os indicadores e `0` para encerrar. A janela `ABRIR_TERMINAL.bat` mantém o resultado visível após a saída.

Para executar a bateria automatizada e a verificação real de conexão Cloud no Windows, abra `TESTAR_TUDO.bat`.


## Verificação da interface desktop — V4.5.0

A navegação gráfica foi aberta em ambiente Tkinter e percorrida pelas telas de visão geral, busca, categorias, histórico de perguntas, avaliações, indicadores e fontes. Esse smoke test verifica montagem e navegação das telas, mas não substitui o teste visual no Windows do usuário nem uma chamada real ao Ollama Cloud.

- Tema escuro de baixo brilho e contraste consistente.
- Histórico de perguntas: pesquisa, filtros, detalhes e repetir consulta.
- Avaliações: histórico dos votos sobre respostas e notas de facilidade de uso.
- Painel inicial: métricas e registros recentes derivados dos CSVs locais.

Roteiro manual no Windows: abrir `py -3 main.py --gui`, fazer uma pergunta, registrar se ajudou, navegar ao Histórico de perguntas e Avaliações, localizar o registro e reabrir a pergunta.
