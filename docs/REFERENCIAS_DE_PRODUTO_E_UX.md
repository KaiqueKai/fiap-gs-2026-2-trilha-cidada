# Referências de produto e UX — Trilha Cidadã V4.5.0

Esta revisão não usa outro projeto como base de código. Foram estudados produtos open source e suas documentações para identificar padrões de navegação, histórico, métricas e feedback que fazem sentido em um assistente de orientação ao cidadão.

## 1. Open WebUI — conversas e histórico

**Referência:** [History & Search](https://docs.openwebui.com/features/chat-conversations/chat-features/history-search/) e [repositório](https://github.com/open-webui/open-webui).

Padrões observados: conversas persistentes, organização temporal, pesquisa do histórico, prévia de conteúdo e retomada de uma conversa.

**Aplicação no Trilha Cidadã:** tela de histórico com busca textual, filtros por situação, data, título da orientação, detalhes do atendimento e ação para refazer a pergunta. O CSV existente permanece como persistência simples exigida pela FIAP.

## 2. Chatwoot — operação de atendimento e satisfação

**Referência:** [Reports and Metrics](https://chatwoot.help/hc/user-guide/articles/1777328138-lesson-6-reports-and-metrics) e [repositório](https://github.com/chatwoot/chatwoot).

Padrões observados: indicadores que respondem perguntas operacionais, leitura de volume e resolução, satisfação e relatórios exportáveis. A documentação enfatiza que os dados de relatórios devem ser interpretados no contexto do volume e período observados.

**Aplicação no Trilha Cidadã:** cartões de métricas no painel inicial, página de indicadores e separação entre respostas que ajudaram e respostas que não ajudaram. As métricas são calculadas dos registros locais, sem dados demonstrativos na aplicação.

## 3. Langfuse — feedback e avaliação de IA

**Referência:** [User Feedback](https://langfuse.com/docs/observability/features/user-feedback), [Scores](https://langfuse.com/docs/evaluation/scores/overview) e [repositório](https://github.com/langfuse/langfuse).

Padrões observados: feedback explícito (positivo/negativo, estrelas, comentários) separado de avaliações técnicas; registros de avaliação ligados à interação; uso de feedback para encontrar problemas e montar conjuntos de avaliação.

**Aplicação no Trilha Cidadã:** histórico separado para feedback sobre a resposta (ajudou/não ajudou) e facilidade de uso (nota de 1 a 5). Uma evolução futura recomendada é permitir que o usuário explique por que uma resposta não ajudou, com opção de comentário curto e sem dados pessoais.

## 4. Decisões de design

- **Tema:** escuro, superfícies azul-marinho/grafite, texto claro e acento turquesa. O objetivo é reduzir grandes áreas brancas, sem reduzir o contraste necessário à leitura.
- **Hierarquia:** navegação lateral agrupada por tarefa; barra superior com estado do provedor; título, descrição curta e conteúdo principal por tela.
- **Página inicial:** visão resumida do uso real, atalhos e perguntas recentes; evita ser apenas uma tela decorativa.
- **Histórico:** busca e filtros para localizar perguntas antigas, consultar o resultado e repetir a consulta.
- **Avaliações:** separa a utilidade da resposta da facilidade de uso. Não trata uma métrica como se fosse a outra.
- **Transparência:** a fonte oficial, data de verificação e limites continuam visíveis nas respostas.
- **Compatibilidade acadêmica:** Python/Tkinter, CSV, classes e busca pontuada continuam preservados; a IA não substitui os requisitos obrigatórios do enunciado.

## 5. Próximas melhorias sugeridas (não incluídas nesta versão)

1. Motivo opcional para avaliações negativas (por exemplo: não respondeu, informação incompleta, fonte difícil de acessar).
2. Exportação independente do histórico e das avaliações, além do CSV atual de atendimentos.
3. Pesquisa por período e categoria no histórico.
4. Ação de apagar/anonimizar o histórico local, com confirmação explícita.
5. Testes de usabilidade observados com participantes externos e registro de dificuldades reais.

Nenhuma dessas melhorias deve apagar nem sobrescrever os arquivos CSV existentes sem confirmação.
