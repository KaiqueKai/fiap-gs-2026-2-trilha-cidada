# Changelog

## 4.5.0 — Experiência desktop, histórico e feedback — 06/11/2026

- Interface redesenhada em tema escuro de baixo brilho, mantendo contraste confortável e reduzindo superfícies brancas.
- Navegação agrupada por Início, Atendimento, Qualidade e Informações.
- Painel inicial com visão de atendimentos, taxa de resolução, facilidade, tamanho da base, últimas perguntas e atalhos.
- Histórico de perguntas com busca por texto, filtros por situação, detalhes do atendimento e ação para repetir uma pergunta.
- Histórico de avaliações consolidando votos sobre respostas e notas de facilidade de uso, sem misturar os dois indicadores.
- Indicadores e fontes reorganizados com a mesma linguagem visual.
- Layout ajustado para janela padrão de 1280×820 e largura mínima de 1050×680.
- Documentadas referências de produto: Open WebUI (histórico), Chatwoot (indicadores/CSAT) e Langfuse (feedback e avaliação).
- Preservados os CSVs, a busca pontuada obrigatória da FIAP, a integração Ollama e as três classes centrais do trabalho.
- Testes automatizados e navegação de telas verificados localmente; conexão real Cloud depende da chave do usuário e deve ser validada na instalação.

## 4.4.0 — Interface renovada e atendimento no terminal — 06/11/2026

- Interface atualizada para tema claro com contraste aprimorado, cartões brancos, navegação lateral com estado ativo e barra superior de versão/configuração da IA.
- Fonte Segoe UI, campo de busca mais legível, exemplos clicáveis e atalhos de teclado (Ctrl+L para nova pergunta; Esc para limpar o campo).
- Após avaliar uma resposta, a interface retorna diretamente para uma nova pergunta.
- Modo de atendimento explícito `py -3 main.py --terminal`; saída informa quando a IA está analisando e diferencia resposta assistida de fallback local.
- Criado `docs/TESTE_MANUAL_TERMINAL.md` com roteiro de perguntas e demonstração.
- Criado `TESTAR_TUDO.bat` para executar validação, benchmark, `unittest`, compilação e teste real do provedor.
- README registra o teste parcial relatado pela equipe: 3 participantes e 9 atendimentos positivos; permanece pendente pelo menos 1 atendimento adicional.

## 4.3.0 — Núcleo conversacional por IA e RAG — 06/11/2026

- Mudança arquitetural: a IA agora interpreta toda pergunta quando Ollama está configurado, inclusive perguntas que já teriam pontuação alta na busca local.
- O modelo recebe o catálogo completo da base (76 orientações) e devolve classificação de escopo, IDs relevantes, IDs de fontes, consultas alternativas e uma resposta sintetizada.
- IDs sugeridos pela IA são validados contra o CSV; links e datas de verificação vêm dos registros locais, não de URLs inventadas pelo modelo.
- Para empregabilidade geral, o modelo pode oferecer orientação prática; para direitos, valores e prazos legais, deve usar registros verificados e explicitar limites quando faltarem fontes.
- Perguntas curtas como `emprego`, `seguro` e `transporte` têm fallback local reforçado.
- A interface agora executa consultas em thread para não congelar durante a chamada Cloud e mostra claramente quando a IA participou ou ficou indisponível.
- Criado `python main.py --testar-ia` para diagnóstico real do provedor sem revelar a chave.
- Tempo limite padrão aumentado para 45 segundos, configurável por `OLLAMA_TIMEOUT`.
- Suíte ampliada para 87 testes, incluindo roteamento IA, escopo, termos isolados, proteção contra falso negativo de escopo, IDs permitidos e proteção de dados.
- O benchmark local de 208 casos continua medindo a busca pontuada; não mede a qualidade da IA. A chamada real ao Ollama Cloud ainda precisa ser testada com a chave configurada pelo usuário.


## 4.2.0 — recuperação de termos curtos e erros de digitação — 06/11/2026

- Corrigida a recuperação de `seguro desemprego` como consulta isolada e adicionadas variações comuns de intenção (pedir, solicitar, receber e requisitos).
- Atualizada a orientação de seguro-desemprego (ID 68) com critérios de primeira, segunda e terceira solicitação ou posteriores, prazo geral de requerimento e canais oficiais, com fonte na FAQ do MTE conferida em 06/11/2026.
- Corrigida colisão em que a pergunta “Fui mandado embora sem justa causa. Posso pedir seguro?” podia ser classificada como comparação entre modalidades de desligamento.
- Adicionada correção conservadora de erro de um caractere: substituição, letra faltante, letra extra ou transposição adjacente, apenas quando há uma única palavra candidata no vocabulário da base.
- A interface informa quando uma palavra foi ajustada automaticamente.
- Benchmark ampliado para 208 casos: 175 perguntas dentro do escopo e 33 fora do escopo.
- Suíte automatizada ampliada, com regressões para perguntas isoladas e erros de digitação.


## 4.1.0 — 06/11/2026

- Adicionada orientação geral de vale-transporte (ID 76), incluindo consultas curtas como `transporte`, `passagem` e `condução`.
- Desambiguação: consultas gerais sobre transporte não devem cair na FAQ exclusiva do Jovem Aprendiz; perguntas que mencionam aprendizagem continuam priorizando a orientação específica.
- Adicionada expansão opcional de consultas via Ollama (Cloud ou local). O modelo só sugere paráfrases; respostas e fontes continuam vindo do CSV revisado.
- IA desativada por padrão; Ollama Cloud sem chave permanece desativado e sem configuração a aplicação não faz chamadas externas.
- Criado `.env.example`; `.env` continua ignorado pelo Git.
- Benchmark atualizado para 197 perguntas (164 dentro do escopo e 33 fora dele).
- Adicionados testes de integração simulada da expansão IA, privacidade, falha de rede e consulta isolada `transporte`.
- Atualizada a documentação de arquitetura, auditoria de fontes e limites de atualização automática.

## 4.0.0 — Auditoria de conteúdo e ampliação trabalhista — 06/11/2026

- Base expandida de 45 para 75 orientações em sete categorias.
- Incluídas orientações sobre pedido de demissão, verbas rescisórias, aviso prévio, prazo de pagamento, justa causa, dispensa sem justa causa, rescisão indireta e acordo.
- Incluídas perguntas sobre salário, jornada, horas extras, intervalos, descanso, férias, faltas, registro, FGTS, seguro-desemprego, descontos, EPI, assédio, domingos e feriados, experiência, trabalho sem registro e 13º salário.
- Atualizados os links do Manual da Aprendizagem Profissional para o catálogo oficial vigente do MTE.
- Corrigida a regra de aviso prévio com base no art. 487 da CLT: 8 dias para pagamento semanal ou menor e 30 dias para pagamento quinzenal ou mensal.
- Atualizadas jornada e folgas conforme a Emenda Constitucional nº 141/2026: 42 horas semanais a partir de 16/12/2026, 40 horas a partir de 16/12/2027 e dois dias de repouso semanal a partir de 16/12/2026.
- Busca ampliada com equivalências linguísticas, correspondência independente da ordem das palavras e regras contextuais para diferenciar temas parecidos.
- Benchmark ampliado para 192 perguntas: 159 dentro do escopo e 33 fora. Referência local: 159/159 acertos top-1 e 33/33 abstenções corretas; resultado interno, não teste com usuários reais.
- Documentação de cobertura e revisão de fontes atualizada; teste externo obrigatório continua pendente.

## 3.3.0 — Busca por expressões, semântica controlada e regressão — 06/11/2026

- Busca agora reconhece expressões-chave mesmo com palavras intermediárias e ordem diferente, usando conjuntos de termos relevantes.
- Aliases redundantes deixam de inflar a pontuação: expressões menores contidas em expressões mais específicas não são somadas novamente.
- Mantida a regra didática de +3 por expressão-chave independente e +1 por termo relevante do título.
- Ampliadas expressões para SINE, SENAI, currículo, Progredir, candidatura e direitos do aprendiz.
- Adicionados testes para 13 perguntas naturais que antes eram respondidas incorretamente ou sem resposta.
- Corrigidos testes antigos que esperavam 35 orientações e 12 perguntas fora do escopo, apesar de a base e o benchmark já conterem 40 e 20.
- A avaliação não será declarada perfeita por antecipação: os resultados medidos serão publicados com os erros encontrados.

## 3.2.1 — FAQ oficial do aprendiz e correções de busca — 06/11/2026

- Corrigido conflito entre perguntas sobre ansiedade em entrevista e preparação genérica para entrevista.
- Corrigido caso de teste: pergunta sobre procurar emprego na própria cidade corresponde ao serviço geral do SINE/Emprega Brasil, não necessariamente à orientação específica de primeiro emprego.
- Adicionadas cinco orientações do Manual da Aprendizagem Profissional do MTE: férias, vale-transporte, feriados, trabalho noturno para menores de 18 anos e faltas na formação teórica.
- Detalhada a orientação sobre remuneração do aprendiz, incluindo as horas de formação teórica.
- Normalização ampliada com equivalências controladas para CV/curriculum vitae e plurais frequentes.
- Benchmark ampliado para 110 casos: 90 dentro do escopo e 20 fora do escopo.
- Incluídos testes de regressão para novas FAQs, variações de currículo e perguntas fora do escopo.
- Mantido o mecanismo de pontuação exigido no enunciado: palavras-chave +3 e palavras do título +1; compatibilidade de busca alta a partir de 6 e média a partir de 3; a pontuação não expressa certeza jurídica.

## 3.2.0 — Expansão da base de conhecimento e FAQ curada — 06/11/2026

- Base ampliada de 16 para 35 orientações verificadas e organizadas em seis categorias.
- Novas orientações sobre currículo, currículo sem experiência, objetivo profissional, entrevista, nervosismo, vestimenta, candidatura a vagas e privacidade das informações curriculares.
- Incluídas informações municipais de Itaquaquecetuba: Itaquá Mais Emprego e Qualifica Itaquá, com links e contatos oficiais.
- Incluídas orientações do SINE e Portal Emprega Brasil para buscar vagas e atualizar o perfil.
- Incluídas perguntas frequentes do Programa Progredir, com aviso explícito de que o cadastro exige inscrição no CadÚnico.
- Palavras-chave ampliadas com variações de linguagem natural, sem reduzir os limites de confiança.
- Benchmark ampliado de 46 para 92 perguntas: 80 dentro do escopo e 12 fora dele.
- Adicionados testes de regressão para currículo, ausência de experiência, candidatura, privacidade no currículo, busca de vagas e serviços locais.
- Suíte automatizada atualizada para 51 testes aprovados na validação desta versão.
- Conteúdo verificado em fontes oficiais em 06/11/2026.
- Limitação mantida: base offline e curada manualmente; não consulta vagas em tempo real nem substitui atendimento oficial.

# Histórico de versões

## 3.1.0 — Cobertura de primeiro emprego (revisada)

- Adicionada orientação oficial sobre como procurar o primeiro emprego por meio do SINE, Portal Emprega Brasil e Carteira de Trabalho Digital.
- Incluídas quatro formulações naturais sobre primeiro emprego no benchmark de regressão.
- Acrescentados testes para garantir que a pergunta que revelou a lacuna e outras paráfrases naturais sejam reconhecidas.
- Corrigido o registro CSV: removidos separadores `;` indevidos do texto da orientação, que impediam sua leitura pelo parser simples exigido no trabalho.
- Mantida a resposta ligada ao serviço oficial do SINE e incluídas orientações para quem ainda não possui experiência, sem afirmar que o cadastro garante contratação.
- Mantido o limite mínimo de confiança e a lógica de abstenção; a correção ocorreu na base de conhecimento, não no relaxamento da busca.


## V3 — Avaliação reproduzível da busca — 06/11/2026

- Novo módulo `avaliador_busca.py` para executar um benchmark determinístico de perguntas.
- Novo comando `python main.py --avaliar-busca`.
- Conjunto original de 42 perguntas de referência: 30 dentro do escopo e 12 fora do escopo.
- Métricas top-1, top-3, cobertura, respostas corretas entre as emitidas, abstenções e falsos positivos.
- Relatório JSON exportado para `reports/avaliacao_busca.json`.
- Ajustes pontuais de palavras-chave após análise de perguntas ambíguas e de frequência escolar.
- Remoção de palavra-chave genérica que gerava risco de falso positivo em dúvidas não trabalhistas.
- 39 testes automatizados com `unittest` (31 anteriores + 8 novos).
- Resultado atual do benchmark interno: 30/30 acertos top-1 no escopo e 12/12 abstenções fora do escopo. Esse resultado não substitui testes com usuários reais.

## V2 técnica — 06/11/2026

- Validação ampliada da base CSV: campos obrigatórios, IDs únicos, palavras-chave diferentes, HTTPS e datas ISO.
- Novo diagnóstico da base com `python main.py --validar-base`.
- Busca com explicação do nível de confiança e ordenação determinística em empates.
- Leitura do histórico mais tolerante a linhas inválidas e cabeçalhos inesperados.
- Avisos quando um atendimento é contado na sessão, mas a gravação em disco não pode ser confirmada.
- Indicadores adicionais: percentual de buscas sem orientação suficiente e orientações mais consultadas.
- Base expandida de 12 para 15 orientações.
- Documentação de arquitetura, decisões e plano de validação.
- Suíte automatizada ampliada para 31 testes.


## V4.4.0 — Experiência de uso e testes no terminal

- Interface atualizada para tema claro com contraste aprimorado, cartões brancos, navegação lateral com estado ativo e barra superior de versão/configuração da IA.
- Fonte Segoe UI, campos de busca mais legíveis, exemplos clicáveis de perguntas e atalhos de teclado (Ctrl+L para nova pergunta; Esc para limpar o campo).
- Após avaliar uma resposta, a interface retorna diretamente para uma nova pergunta, sem exigir voltar à tela inicial.
- Modo de atendimento explícito `py -3 main.py --terminal`; saída informa quando a IA está analisando e diferencia resposta assistida de fallback local.
- Novo guia `docs/TESTE_MANUAL_TERMINAL.md`.
- Novo `TESTAR_TUDO.bat` para executar em sequência validação, benchmark, `unittest`, compilação e teste real do provedor.
- README registra o resultado parcial relatado: 3 participantes e 9 atendimentos positivos; permanece pendente pelo menos 1 atendimento adicional e os registros de avaliação não informados.
