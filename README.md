# Trilha Cidadã — Citizen Assist AI

**Informação que transforma oportunidades em caminhos.**  
**Versão:** 4.5.0  
**Status:** desenvolvimento funcional concluído — pronto para demonstração e validação com usuários.  
**Documentação revisada em:** 06/11/2026

O **Trilha Cidadã** é um assistente digital de orientação sobre trabalho, oportunidades e direitos. Ele ajuda o cidadão a encontrar informações sobre primeiro emprego, currículo, entrevistas, aprendizagem profissional, direitos trabalhistas básicos e canais oficiais de emprego e qualificação. A base reúne referências federais e orientações municipais de Itaquaquecetuba (SP).

> **Projeto educacional:** o Trilha Cidadã não representa um órgão público, não presta consultoria jurídica e não substitui os canais oficiais. As orientações são gerais, possuem fontes indicadas e devem ser confirmadas nos canais oficiais quando envolverem uma situação individual.

---

## Equipe do projeto

A equipe responsável pelo desenvolvimento é formada por:

| **INTEGRANTE** | **RM FIAP** |
|:---|:---:|
| **KAIQUE DA SILVA ASSIS** | **572718** |
| **ANDRÉ DEBIAZZI BALDI NEGRINI** | **569062** |
| **VINICIUS CRISTAL DE OLIVEIRA** | **572049** |

## Links de entrega

| Entrega | Link |
|:---|:---|
| **Repositório público no GitHub** | **`INSERIR_LINK_DO_REPOSITORIO`** |
| **Vídeo técnico no YouTube (não listado)** | **`INSERIR_LINK_DO_VIDEO`** |

> Antes da entrega, substitua os dois campos pelos links definitivos. O vídeo técnico deve ter entre 5 e 8 minutos, conforme o enunciado da FIAP.

## Objetivo, público e impacto

**Público atendido:** jovens em busca do primeiro emprego, pessoas interessadas em oportunidades de Jovem Aprendiz e trabalhadores que precisam localizar orientações básicas sobre seus direitos.

**Problema abordado:** informações sobre trabalho e serviços públicos estão distribuídas em diferentes portais e frequentemente usam linguagem técnica. O Trilha Cidadã reúne orientações verificadas em uma experiência de consulta mais simples, apresentando a origem da informação e a data de conferência.

**ODS relacionados:**

- **ODS 4 — Educação de Qualidade:** facilitar o acesso a informações sobre formação e qualificação profissional.
- **ODS 8 — Trabalho Decente e Crescimento Econômico:** aproximar o público de oportunidades de trabalho e informações sobre direitos.
- **ODS 10 — Redução das Desigualdades:** reduzir barreiras de acesso à informação pública.

---

# 1. Execução pelo terminal — modo principal

O **terminal é o modo principal de execução e demonstração** do projeto. Ele apresenta o fluxo de atendimento em texto, permite conversar com a IA, navegar pelas categorias, registrar avaliações, consultar indicadores e exportar os atendimentos. Esse modo atende diretamente à proposta do enunciado da FIAP.

## 1.1. Requisitos

- Python 3.10 ou superior.
- Windows com o Python Launcher (`py`) ou Python disponível no `PATH`.
- Conexão com a internet e chave do Ollama Cloud para utilizar a interpretação por IA em nuvem.
- Não é necessário instalar bibliotecas Python externas. A interface gráfica utiliza Tkinter.

Abra o PowerShell na pasta do projeto.

## 1.2. Configurar o Ollama Cloud

O projeto continua oferecendo busca local quando a IA não está configurada. Para ativar a interpretação por IA, crie o arquivo `.env` a partir do modelo:

```powershell
Copy-Item .env.example .env
notepad .env
```

Preencha as configurações:

```env
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=gemma4:31b
OLLAMA_API_KEY=SUA_CHAVE_OLLAMA
OLLAMA_TIMEOUT=45
```

Crie ou consulte sua chave em [Ollama API Keys](https://ollama.com/settings/keys). Mantenha o `.env` privado: ele está listado no `.gitignore` e **não deve ser enviado ao GitHub**. Nunca coloque a chave no README, em capturas de tela ou no vídeo.

## 1.3. Iniciar o atendimento pelo terminal

```powershell
py -3 main.py --terminal
```

Também é possível executar `py -3 main.py`; sem selecionar a interface gráfica, o programa inicia o terminal. No Windows, o arquivo `ABRIR_TERMINAL.bat` inicia o mesmo modo com duplo clique.

### Menu do terminal

| Opção | Ação |
|:---:|:---|
| **1** | Fazer uma pergunta e conversar com a IA. |
| **2** | Explorar as orientações organizadas por categoria. |
| **3** | Consultar os indicadores dos atendimentos. |
| **4** | Exportar os atendimentos para CSV. |
| **0** | Encerrar, registrar a nota de facilidade de uso (1 a 5) e sair. |

### Como realizar um atendimento

1. Digite `1` no menu.
2. Escreva sua dúvida com suas próprias palavras.
3. Aguarde a IA analisar a pergunta e consultar as orientações cadastradas. Se a IA estiver indisponível, o sistema informa que utilizará a busca local.
4. Leia a orientação, a origem da resposta e as fontes apresentadas.
5. Responda `s` ou `n` para informar se a orientação resolveu sua dúvida.
6. Faça novas perguntas ou utilize as outras opções do menu.
7. Ao encerrar com `0`, informe uma nota de facilidade de uso entre 1 e 5.

### Perguntas para demonstrar o atendimento

- `Quero conseguir meu primeiro emprego. Por onde começo?`
- `Como montar um currículo se nunca trabalhei?`
- `Fui demitido sem justa causa. Posso receber seguro-desemprego?`
- `Como pedir demissão e o que recebo?`
- `A empresa precisa pagar minha passagem?`
- `Meu chefe não paga minhas horas extras. O que posso fazer?`
- `Como funciona o contrato de Jovem Aprendiz?`
- `Como encontrar vagas pelo SINE?`
- `Como fazer um bolo de chocolate?` — deve ser identificada como pergunta fora do escopo.

Não informe CPF, telefone, e-mail, endereço completo, senha ou outros dados que identifiquem você ou outra pessoa. Ao usar o Ollama Cloud, o texto da pergunta e o catálogo de orientações são enviados ao provedor para processamento.

---

# 2. Execução pela interface gráfica

A interface desktop é uma **forma complementar de utilizar e demonstrar** o mesmo assistente. Ela foi criada para facilitar a navegação, consultar perguntas anteriores e acompanhar avaliações e indicadores. Utiliza a mesma base CSV, a mesma lógica de atendimento e a mesma configuração do Ollama Cloud.

Para abrir:

```powershell
py -3 main.py --gui
```

No Windows, também é possível abrir `ABRIR_INTERFACE.bat` com duplo clique.

### Funcionalidades da interface

- **Visão geral:** resumo de atendimentos, avaliações e atalhos.
- **Perguntas:** campo de consulta e apresentação das orientações recuperadas.
- **Categorias:** navegação pela base de conhecimento.
- **Histórico de perguntas:** pesquisa, filtros, detalhes e repetição de consultas anteriores.
- **Avaliações:** histórico do retorno sobre as respostas e das notas de facilidade de uso.
- **Indicadores:** volume, resolução, tempo médio e orientações mais consultadas.
- **Fontes e transparência:** acesso à procedência das informações e aos limites do assistente.

Os registros ficam salvos localmente nos arquivos CSV dentro de `data/`. A interface apresenta os registros da instalação em que o programa está sendo executado.

---

# 3. Testes e validação técnica

## 3.1. Bateria completa no Windows

Para executar a validação estrutural da base, o benchmark, os testes automatizados, a compilação e uma chamada real de conexão com o Ollama Cloud, execute:

```powershell
.\TESTAR_TUDO.bat
```

A chamada de conexão utiliza o provedor, o modelo e a chave configurados no `.env`; ela depende de internet e pode consumir tokens. Essa bateria não substitui a conversa manual pelo terminal nem a validação de experiência com usuários.

## 3.2. Comandos individuais

**Validar a base de conhecimento:**

```powershell
py -3 main.py --validar-base
```

**Executar o benchmark da busca local:**

```powershell
py -3 main.py --avaliar-busca
```

**Executar os testes automatizados:**

```powershell
py -3 -m unittest discover -s tests -v
```

**Verificar a sintaxe dos arquivos Python:**

```powershell
py -3 -m compileall -q .
```

**Testar a conexão real com o Ollama Cloud:**

```powershell
py -3 main.py --testar-ia
```

**Conversar com o assistente no terminal:**

```powershell
py -3 main.py --terminal
```

## 3.3. Resultados de referência da versão 4.5.0

Na validação técnica desta versão, foram obtidos os seguintes resultados:

| Verificação | Resultado de referência |
|:---|---:|
| Orientações válidas | **76** |
| Categorias | **7** |
| Perguntas dentro do escopo no benchmark | **175/175** reconhecidas no top-1 |
| Perguntas fora do escopo no benchmark | **33/33** recusadas corretamente |
| Testes automatizados | **87 aprovados** |
| Compilação dos arquivos Python | **Aprovada** |

Os percentuais do benchmark valem **somente para o conjunto interno de 208 perguntas preparado pela equipe**. Não representam uma taxa estatística de acerto para todas as perguntas reais nem garantem precisão jurídica. Os testes automatizados da integração com IA utilizam respostas simuladas; a conexão Cloud deve ser verificada separadamente com `--testar-ia`.

Para avaliar a experiência em texto, faça perguntas novas com `py -3 main.py --terminal`. Consulte também o [guia de teste manual pelo terminal](docs/TESTE_MANUAL_TERMINAL.md).

---

# 4. Como o assistente funciona

O Trilha Cidadã combina três componentes:

1. **Base de conhecimento local:** um CSV reúne orientações revisadas, categorias, palavras-chave, respostas, documentos, local de atendimento, fonte e data de verificação.
2. **Busca pontuada:** a pergunta é normalizada e comparada com títulos e expressões-chave. A busca retorna tuplas `(pontos, orientacao)`, ordenadas por relevância. Essa etapa preserva o requisito de busca com pontuação da FIAP.
3. **IA com recuperação de informações (RAG):** quando configurado, o Ollama interpreta toda pergunta, inclusive quando a busca local encontra correspondências. O modelo seleciona IDs existentes na base e organiza uma resposta em linguagem natural com apoio nos registros selecionados. As fontes e datas acompanham a orientação.

A IA pode combinar até quatro orientações cadastradas. O modelo não deve criar direitos, prazos ou valores jurídicos sem apoio nos registros. Quando a base não sustenta uma conclusão, o assistente deve reconhecer a limitação e encaminhar a pessoa para uma fonte ou canal oficial.

Se o Ollama estiver indisponível, a busca local continua funcionando. Nesse caso, a interpretação é menos flexível e o sistema deve indicar que a IA não participou daquela resposta.

## Regra didática de pontuação

| Regra | Pontuação |
|:---|---:|
| Expressão-chave independente reconhecida | +3 |
| Palavra da pergunta (com pelo menos quatro letras) encontrada no título | +1 |
| 6 pontos ou mais | Compatibilidade ALTA |
| 3 a 5 pontos | Compatibilidade MÉDIA |
| Menos de 3 pontos | Correspondência insuficiente para responder pela busca local |

A compatibilidade mede correspondência textual, não certeza jurídica. A busca também normaliza acentos e pontuação, aplica regras contextuais e corrige conservadoramente alguns erros simples de digitação quando encontra uma única palavra candidata.

---

# 5. Base de conhecimento e fontes oficiais

A versão 4.5.0 contém **76 orientações distribuídas em 7 categorias**. Os temas incluem primeiro emprego, currículo, entrevista, aprendizagem profissional, direitos trabalhistas, benefícios, proteção do trabalhador, vagas e qualificação.

A curadoria da base foi conferida em **06/11/2026**. Entre as fontes prioritárias estão:

- [Perguntas Frequentes do Ministério do Trabalho e Emprego — MTE](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/proteja/duvidas-frequentes/duvidas-frequentes) — orientações gerais, incluindo vale-transporte e direitos trabalhistas.
- [Perguntas Frequentes — Seguro-Desemprego, MTE](https://www.gov.br/pt-br/temas/perguntas-frequentes-seguro-desemprego) — requisitos, solicitação e revisão do benefício.
- [Solicitar Seguro-Desemprego — gov.br](https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego) — serviço oficial para solicitação do benefício; página consultada em 06/11/2026.
- [CLT — Planalto](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm) — legislação trabalhista de referência.
- [Manual de Aprendizagem Profissional — MTE](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/escola/e-biblioteca/manual-de-aprendizagem-profissional.pdf/view) — edição de 2025, com 145 perguntas e respostas; página atualizada em 19/02/2025.
- [Aprendizagem Profissional — MTE](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/aprendizagem-profissional) — página atualizada em 06/07/2026, com regras e entidades formadoras.
- [Contrato de aprendizagem: regras e direitos — MTE](https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/julho/aprendizagem-profissional-regras-direitos-e-funcionamento-do-contrato-de-aprendizagem) — publicação de 23/07/2026.
- [Emenda Constitucional nº 141/2026 — texto oficial na Câmara dos Deputados](https://www2.camara.leg.br/legin/fed/emecon/2026/emendaconstitucional-141-16-outubro-2026-800062-publicacaooriginal-181622-pl.html) — alteração da jornada semanal e do repouso remunerado.
- [Carteira de Trabalho Digital — MTE](https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/perguntas-frequentes-carteira-de-trabalho-digital).
- [SINE — serviço gov.br](https://www.gov.br/pt-br/servicos/buscar-emprego-no-sistema-nacional-de-emprego-sine) e [Portal Emprega Brasil — MTE](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/sistema-nacional-de-emprego-sine/portal-emprega-brasil).
- [Programa Progredir — MDS](https://www.gov.br/mds/pt-br/acoes-e-programas/outros/progredir/perguntas-frequentes).
- [Itaquá Mais Emprego — Prefeitura de Itaquaquecetuba](https://itaqua.sp.gov.br/seate/vagas.php) — vagas e informações municipais, sujeitas a atualização pelo município.
- [Guia de prevenção ao assédio moral e sexual — MTE](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/guia-de-prevencao-ao-assedio-moral-e-sexual) e [Denúncia da Inspeção do Trabalho](https://denuncia.sit.trabalho.gov.br/home).
- [Canais de atendimento do MTE — publicação de 06/07/2026](https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/julho/saiba-como-acessar-os-canais-de-atendimento-do-ministerio-do-trabalho-e-emprego/) — inclui a Central Alô Trabalho, telefone 158.

## Atualização e limites das fontes

A base é local e **não sincroniza automaticamente** com páginas do governo. A equipe revisa manualmente os registros e deve reabrir as fontes antes da entrega e sempre que houver notícia de alteração legal. Vagas, cursos, calendários municipais, salário mínimo e critérios de benefícios podem mudar. O comando `--validar-base` verifica a estrutura e o formato dos links, mas não confirma que o conteúdo de cada página continua igual nem substitui uma revisão humana.

A Emenda Constitucional nº 141/2026 prevê a transição da jornada máxima semanal para 42 horas a partir de **16/12/2026** e 40 horas a partir de **16/12/2027**. A mudança para dois dias de repouso semanal remunerado também produz efeitos a partir de **16/12/2026**, conforme as regras e exceções previstas no texto constitucional. As orientações correspondentes devem ser reavaliadas nas datas de transição e diante de regulamentação ou decisões posteriores.

---

# 6. Privacidade, segurança e limitações

- O programa não solicita nome, CPF, telefone ou e-mail.
- Como proteção preventiva exigida no enunciado, perguntas com oito ou mais dígitos ou com `@` são bloqueadas antes do registro e do envio à IA. Essa regra não é um detector completo de dados pessoais.
- Ao usar o Ollama Cloud, o texto da pergunta e o catálogo de orientações são enviados ao provedor para processamento. Não digite dados pessoais, documentos, senhas ou detalhes identificáveis.
- O histórico fica no computador em arquivos CSV. Antes de compartilhar o projeto, confira se os arquivos gerados não contêm informações pessoais. O `.gitignore` exclui os históricos e o `.env` do controle de versão.
- O sistema não registra denúncias, solicita benefícios nem executa serviços em nome do cidadão.
- Sem conexão com o provedor, a IA não consegue interpretar a pergunta; permanece disponível apenas a busca local.
- As respostas são orientações gerais e não substituem atendimento individual, sindicato, advogado, Ministério do Trabalho ou Justiça do Trabalho.

---

# 7. Status do projeto e validação com usuários

> **PROJETO FUNCIONALMENTE CONCLUÍDO — VERSÃO 4.5.0**

O desenvolvimento da solução, a integração com o Ollama Cloud, a base de conhecimento, a busca pontuada, o modo terminal, a interface gráfica, o histórico, as avaliações, os indicadores e a documentação estão implementados. O projeto está pronto para demonstração.

**Próxima etapa da equipe: validação final com usuários reais.** Essa etapa será realizada após a conclusão do desenvolvimento e seus resultados serão acrescentados a este README antes da entrega final. Portanto, os resultados de usuários não são apresentados como concluídos nem são simulados.

O enunciado da FIAP solicita:

- Pelo menos **3 pessoas de fora da equipe**.
- Pelo menos **10 atendimentos no total**.
- Registro dos indicadores reais, das dúvidas que ficaram sem solução e de pelo menos uma melhoria realizada a partir dos retornos.
- Não registrar nomes nem dados pessoais dos participantes.

### Registro da validação — preencher após os testes

| Indicador | Resultado real |
|:---|:---|
| Participantes externos | A preencher |
| Atendimentos realizados | A preencher (mínimo: 10) |
| Respostas que ajudaram | A preencher |
| Nota média de facilidade (1 a 5) | A preencher |
| Dúvidas sem solução | A preencher |
| Melhoria implementada a partir do teste | A preencher |

---

# 8. Estrutura do projeto

```text
trilha-cidada/
├── main.py
├── orientacao.py
├── base_conhecimento.py
├── assistente.py
├── avaliador_busca.py
├── expansor_ia.py
├── interface.py
├── .env.example
├── ABRIR_TERMINAL.bat
├── ABRIR_INTERFACE.bat
├── TESTAR_TUDO.bat
├── TESTAR_TUDO.ps1
├── data/
│   ├── base_conhecimento.csv
│   └── perguntas_avaliacao.csv
├── reports/
│   └── avaliacao_busca.json
├── docs/
└── tests/
```

Durante a execução, também são criados `data/historico.csv`, `data/avaliacoes.csv` e `data/atendimentos.csv`. Esses arquivos contêm dados de uso local e não devem ser publicados sem revisão.

# 9. Documentação complementar

- [Decisões técnicas e arquitetura](docs/DECISOES_TECNICAS.md)
- [Plano de validação e testes](docs/VALIDACAO_E_TESTES.md)
- [Metodologia do benchmark da busca](docs/AVALIACAO_DA_BUSCA.md)
- [Catálogo de fontes e cobertura](docs/CATALOGO_DE_FONTES_E_COBERTURA.md)
- [Revisão de fontes e atualizações](docs/REVISAO_DE_FONTES.md)
- [Arquitetura de IA e estratégia de atualização](docs/ARQUITETURA_IA_E_ATUALIZACAO.md)
- [Teste manual pelo terminal](docs/TESTE_MANUAL_TERMINAL.md)
- [Referências de produto e UX](docs/REFERENCIAS_DE_PRODUTO_E_UX.md)

---

**Disciplina:** Global Solution 2026.2 — Pensamento Computacional e Automação com Python (FIAP).
