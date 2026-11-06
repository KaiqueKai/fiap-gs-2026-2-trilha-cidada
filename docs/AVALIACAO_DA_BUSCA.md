# Avaliação reproduzível da busca — V4.2.0

## Objetivo

O benchmark compara a busca entre versões e ajuda a encontrar regressões. Cada pergunta dentro do escopo possui uma orientação esperada definida pela equipe. Perguntas fora do escopo verificam se o sistema se abstém em vez de inventar uma resposta.

## Como executar

```bash
python main.py --avaliar-busca
```

O comando lê `data/perguntas_avaliacao.csv` e salva o resultado detalhado em `reports/avaliacao_busca.json`.

## Composição atual

O arquivo contém **208 casos**:

- **175 perguntas dentro do escopo**, cobrindo paráfrases de 76 orientações cadastradas;
- **33 perguntas fora do escopo**, para testar a abstenção.

O conjunto inclui perguntas diretas e variações como “Como pedir demissão?”, “Se eu pedir as contas, o que recebo?”, “Sou mensalista e pedi demissão. Tenho que cumprir aviso?”, “A jornada de 44 horas vai mudar em dezembro de 2026?” e “Saí às 23h e querem que eu volte às 7h. Pode?”.

## Métricas

| Métrica | Significado |
|---|---|
| Acurácia top-1 | Percentual de perguntas do escopo em que a primeira orientação emitida é a esperada. |
| Acurácia top-3 | Percentual em que a orientação esperada aparece entre até três resultados. |
| Cobertura | Percentual das perguntas do escopo para as quais a busca emite orientação com pontuação mínima. |
| Respostas corretas entre as emitidas | Percentual das respostas emitidas que apontam para a orientação esperada. |
| Abstenções | Perguntas do escopo sem orientação suficiente. |
| Falsos positivos | Perguntas fora do escopo para as quais a busca emite orientação. |

Os limites de compatibilidade permanecem: 6 pontos ou mais = ALTA; 3 a 5 = MÉDIA; abaixo de 3 = INSUFICIENTE. Essa pontuação mede correspondência textual, não a certeza jurídica da orientação.

## Resultado da execução de referência

Em 06/11/2026, a execução local registrou:

| Indicador | Resultado |
|---|---:|
| Perguntas dentro do escopo corretas no top-1 | 175/175 (100%) |
| Perguntas dentro do escopo no top-3 | 175/175 (100%) |
| Cobertura dentro do escopo | 175/175 (100%) |
| Respostas emitidas incorretamente | 0 |
| Perguntas fora do escopo corretamente recusadas | 33/33 (100%) |
| Falsos positivos | 0 |

**Interpretação obrigatória:** os 100% descrevem somente as 208 perguntas escritas e controladas pela equipe. Não representam desempenho com todas as pessoas, todas as formulações possíveis ou todas as questões jurídicas. O benchmark mede a seleção da orientação cadastrada pela busca lexical. Ele não mede a expansão opcional por IA, não valida o conteúdo jurídico, não representa usuários reais e não substitui revisão humana ou teste de usabilidade.

## Caso que revelou a lacuna de demissão

A pergunta “Como pedir demissão?” não tinha orientação específica na versão anterior. A V4.2.0 adiciona orientações de pedido de demissão, verbas, aviso prévio, prazo da rescisão, modalidades de desligamento, rescisão indireta e acordo. A pergunta direta foi adicionada como caso Q192. A V4.2.0 adiciona Q198–Q204 para seguro-desemprego isolado e com erros de digitação e Q205–Q208 para erros em currículo, primeiro emprego e transporte. Foi corrigida a colisão de Q166: mencionar “seguro” após uma dispensa sem justa causa deve levar à orientação do benefício, e não à comparação entre modalidades de desligamento.


## Caso que revelou as falhas em seguro-desemprego e digitação

A consulta curta `seguro desemprego` recebia apenas pontos pelos termos do título, abaixo do limite de apresentação. A orientação ID 68 agora contém a expressão direta e outras formas frequentes de perguntar sobre solicitar ou receber o benefício. A resposta foi revisada com a FAQ oficial do MTE, que informa os requisitos de tempo de trabalho para a primeira, segunda e demais solicitações e o prazo geral de requerimento.

A busca também passou a corrigir, de forma conservadora, uma edição simples em palavras longas quando o vocabulário local contém uma única candidata. O relatório usa casos artificiais de regressão — `desempregp`, `desemprgo`, `desempregoo`, `desempregeo`, `curricuo`, `emprgo` e `tranpsorte` e `segur` — para verificar substituição, remoção, inserção e transposição. Isso não significa que todos os erros de escrita sejam corrigidos.

Fonte usada para atualizar a orientação: [Perguntas Frequentes — Seguro-Desemprego, MTE](https://www.gov.br/pt-br/temas/perguntas-frequentes-seguro-desemprego), consultada em 06/11/2026.

## Manutenção do benchmark

Quando uma pergunta real falhar:

1. retirar qualquer nome, CPF, telefone, e-mail ou outro dado pessoal;
2. verificar a resposta em fonte primária atual;
3. definir se a pergunta pertence ao escopo do produto;
4. atualizar a FAQ ou registrar uma abstenção correta;
5. adicionar a formulação anonimizada ao benchmark;
6. executar o benchmark e os testes automatizados novamente.

Não se deve adicionar uma palavra-chave apenas para forçar uma pergunta específica a passar. Ela precisa representar uma maneira legítima e reutilizável de perguntar sobre o mesmo assunto.

## Caso que revelou a lacuna de transporte

A consulta formada por uma única palavra — `transporte` — não atingia o mínimo de três pontos na versão anterior. A V4.2.0 inclui uma orientação geral sobre vale-transporte (ID 76), equivalências para `passagem` e `condução`, e uma regra contextual para não confundir o benefício de trabalhadores em geral com o registro específico do Jovem Aprendiz. Foram adicionadas regressões para `transporte`, `vale transporte` e `a empresa tem que pagar minha condução?`.

## Limitações e próximos testes

- As perguntas foram escritas pela equipe e podem não refletir a linguagem espontânea de todos os jovens.
- O benchmark não testa se a pessoa entendeu a explicação, encontrou a fonte ou tomou uma decisão segura.
- O conjunto fora do escopo é uma amostra e pode não cobrir todos os assuntos que geram confusão lexical.
- O projeto ainda precisa do teste real obrigatório com pelo menos três pessoas externas e dez atendimentos ou mais. Os resultados só devem ser documentados depois da execução; não preencher por estimativa.
