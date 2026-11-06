# Teste manual pelo terminal — Trilha Cidadã V4.5.0

Este teste demonstra o atendimento em texto, sem abrir a interface gráfica. Ele usa o mesmo `Assistente`, a mesma base CSV e o mesmo Ollama Cloud configurado no `.env`.

## Como iniciar

Abra o PowerShell dentro da pasta do projeto e execute:

```powershell
py -3 main.py --terminal
```

Também é possível abrir `ABRIR_TERMINAL.bat` com duplo clique.

## Como conversar com o assistente

1. No menu, digite `1` para fazer uma pergunta.
2. Escreva a dúvida com suas próprias palavras. Não informe CPF, telefone, e-mail, endereço completo ou senhas.
3. Aguarde a mensagem `IA Cloud analisando sua pergunta...`.
4. Leia a orientação, a origem da resposta e os links oficiais exibidos.
5. Digite `s` se a resposta ajudou ou `n` se não resolveu a dúvida.
6. Volte ao menu e repita com outra pergunta.
7. Digite `3` para conferir os indicadores e `0` para encerrar. Ao sair, informe uma nota de facilidade de 1 a 5.

## Perguntas recomendadas para a demonstração

- `Quero conseguir meu primeiro emprego. Por onde começo?`
- `Fui demitido sem justa causa. Como vejo se tenho direito ao seguro-desemprego?`
- `Como funciona o vale-transporte?`
- `Meu chefe não paga minhas horas extras. O que posso fazer?`
- `Como pedir demissão e o que recebo?`
- `Quero melhorar meu currículo, mas nunca trabalhei.`
- `Como posso me preparar para uma entrevista?`
- `Como encontrar vagas pelo SINE?`
- `O que é contrato de Jovem Aprendiz?`
- `Como fazer um bolo de chocolate?` (deve ser recusada por estar fora do escopo).

## Diferença entre testes automatizados e atendimento no terminal

- `py -3 -m unittest discover -s tests -v`: testa funções e regras do código, sem simular a experiência completa do cidadão.
- `py -3 main.py --avaliar-busca`: executa as perguntas fixas do benchmark interno.
- `py -3 main.py --testar-ia`: confirma que o provedor responde a uma chamada real, mas não mede a qualidade de todas as respostas.
- `py -3 main.py --terminal`: permite que uma pessoa faça perguntas novas, leia respostas e avalie se a orientação ajudou. Este é o teste manual de experiência.

Os atendimentos ficam em `data/historico.csv` e as avaliações de facilidade em `data/avaliacoes.csv`. O arquivo `data/atendimentos.csv` é atualizado pela opção de exportação. Não publique arquivos de histórico com informações de uso sem revisar os dados.
