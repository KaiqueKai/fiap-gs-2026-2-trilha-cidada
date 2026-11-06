# Núcleo conversacional por IA + RAG local — V4.3.0

## O problema corrigido

Nas versões anteriores, a IA só era chamada quando a busca por palavras-chave não encontrava pontuação suficiente. Portanto, perguntas curtas ou escritas de forma diferente dependiam quase inteiramente do CSV. Em alguns casos, a busca ainda podia escolher uma orientação errada e impedir a expansão por IA.

Na V4.3.0, a IA participa de **toda pergunta**, quando Ollama está configurado. Ela recebe o catálogo completo das orientações, interpreta a intenção, escolhe os registros relevantes e organiza uma resposta em português simples. A busca local por pontuação continua sendo executada e é usada como fallback e evidência técnica da atividade.

## Fluxo de atendimento

1. **Proteção:** perguntas vazias ou com oito ou mais dígitos ou `@` são bloqueadas antes de qualquer chamada externa.
2. **Busca obrigatória por pontuação:** o método local compara pergunta, título e palavras-chave com a regra explicável (+3 por expressão-chave e +1 por termo do título). Termos isolados de conteúdo, como `emprego`, `seguro` e `transporte`, também podem localizar o assunto correspondente.
3. **Interpretação por IA:** a aplicação envia a pergunta e o catálogo completo da base (título, categoria, palavras-chave, resposta, documentos, local, fonte e data). A IA roda mesmo quando a busca local já encontrou uma correspondência.
4. **Recuperação semântica:** o modelo devolve somente IDs existentes e consultas alternativas. Os IDs são validados contra os registros reais do CSV.
5. **Resposta com RAG:** a resposta exibida é sintetizada a partir dos registros selecionados. A aplicação mantém os links e as datas das fontes desses registros.
6. **Escopo:** a IA classifica a pergunta como dentro, fora ou ambígua. Pergunta curta não é considerada fora do escopo só por ser curta. Assunto alheio ao trabalho e à empregabilidade é recusado.
7. **Fallback:** se a API falhar, a busca local continua funcionando. A interface informa explicitamente que a IA não respondeu; não finge que a camada de IA foi usada.

## O que a IA pode e não pode responder

O escopo inclui primeiro emprego, procura de vagas, currículo, entrevistas, aprendizagem profissional, qualificação, CTPS, contratos, salário, benefícios, jornada, segurança, desligamento, FGTS, seguro-desemprego e serviços públicos relacionados ao trabalho.

Quando houver registros pertinentes, a IA pode combinar até quatro orientações da base e explicar o conteúdo com outras palavras. Quando o tema for de empregabilidade geral, pode acrescentar recomendações gerais e práticas, sem apresentá-las como obrigação legal.

Quando uma dúvida exigir um direito, prazo, valor ou regra jurídica que não esteja sustentado pelos registros entregues ao modelo, ele deve explicitar a limitação e apontar um canal oficial. Não deve inventar artigo de lei, percentual, prazo ou benefício. A IA não substitui advogado, sindicato, MTE ou órgão público.

Uma base local de 76 orientações não contém toda a legislação nem todos os casos individuais. A arquitetura amplia a compreensão e a combinação das informações existentes; não promete que qualquer situação complexa terá resposta jurídica conclusiva.

## Configuração do Ollama

Copie `.env.example` para `.env` e configure:

```env
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=gemma4:31b
OLLAMA_API_KEY=sua_chave_ollama
OLLAMA_TIMEOUT=45
```

Para servidor local, use `OLLAMA_BASE_URL=http://localhost:11434`, um modelo instalado e chave vazia. O projeto usa a API de chat `POST /api/chat` e o cabeçalho `Authorization: Bearer ...` quando há chave.

Teste a conexão real com:

```powershell
py -3 main.py --testar-ia
```

A saída mostra host, modelo e status, mas nunca imprime a chave. O teste faz uma chamada real ao provedor e pode consumir tokens.

## Dados enviados ao provedor

No modo Cloud, a pergunta e o catálogo completo da base local são enviados ao Ollama para interpretação. A aplicação bloqueia automaticamente perguntas com oito ou mais dígitos ou com `@`, mas essa proteção não identifica todos os dados pessoais (por exemplo, nomes e endereços). Não digite nomes, CPF, telefone, e-mail, endereço, senha, dados de saúde ou detalhes que identifiquem alguém.

A chave fica no `.env`, excluído pelo `.gitignore`. Nunca faça commit desse arquivo nem cole a chave em mensagens.

## Limitações e atualização de conteúdo

O modelo não atualiza a lei sozinho e a IA não é um navegador oficial em tempo real. As orientações continuam sendo mantidas no CSV, com fonte e data de verificação. Uma atualização confiável exige buscar fontes governamentais, comparar a redação, atualizar a orientação e executar novamente os testes.

Próxima evolução recomendada: criar um atualizador de fontes oficiais que baixe páginas selecionadas, detecte mudanças e gere uma proposta de alteração para revisão humana. Só depois da conferência a alteração deve entrar no CSV. Não permitir que um modelo modifique diretamente regras trabalhistas na base de produção.

## Relação com os requisitos FIAP

A busca pontuada, normalização, tuplas e comparação das orientações permanecem implementadas e demonstráveis. O benchmark `--avaliar-busca` mede exclusivamente o mecanismo local determinístico; ele não mede a qualidade da IA Cloud. Os testes automatizados simulam respostas do provedor para validar o código, mas não substituem `--testar-ia` com chave real nem testes com usuários externos.

## Referências técnicas

- [Ollama Cloud — API Key e chamada de chat](https://github.com/ollama/ollama/blob/main/docs/cloud.mdx)
- [Ollama API — autenticação](https://github.com/ollama/ollama/blob/main/docs/api/authentication.mdx)
- [Ollama API — URLs Cloud e local](https://github.com/ollama/ollama/blob/main/docs/api/introduction.mdx)
