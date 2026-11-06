$ErrorActionPreference = "Continue"
Set-Location -LiteralPath $PSScriptRoot

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: o Python Launcher (py) nao foi encontrado." -ForegroundColor Red
    Write-Host "Instale o Python 3 e marque a opcao Python Launcher."
    exit 9009
}

$checks = @(
    @{ Nome = "Validacao da base"; Args = @("-3", "main.py", "--validar-base") },
    @{ Nome = "Benchmark de busca"; Args = @("-3", "main.py", "--avaliar-busca") },
    @{ Nome = "Testes automatizados"; Args = @("-3", "-m", "unittest", "discover", "-s", "tests", "-v") },
    @{ Nome = "Compilacao Python"; Args = @("-3", "-m", "compileall", "-q", ".") },
    @{ Nome = "Conexao real com Ollama"; Args = @("-3", "main.py", "--testar-ia") }
)

$resultados = @()
foreach ($check in $checks) {
    Write-Host "`n========== $($check.Nome) ==========" -ForegroundColor Cyan
    $argumentos = $check.Args
    & py @argumentos
    $codigo = $LASTEXITCODE
    if ($null -eq $codigo) { $codigo = 0 }
    $estado = if ($codigo -eq 0) { "APROVADO" } else { "FALHOU ($codigo)" }
    $resultados += [PSCustomObject]@{ Teste = $check.Nome; Resultado = $estado }
}

Write-Host "`n========== RELATORIO FINAL ==========" -ForegroundColor Cyan
$resultados | Format-Table -AutoSize

$falhas = @($resultados | Where-Object { $_.Resultado -ne "APROVADO" })
if ($falhas.Count -eq 0) {
    Write-Host "TODOS OS TESTES PASSARAM." -ForegroundColor Green
    Write-Host "Para testar conversas no terminal: py -3 main.py --terminal" -ForegroundColor Green
    Write-Host "Para abrir a interface grafica: py -3 main.py --gui" -ForegroundColor Green
    exit 0
}

Write-Host "HA TESTES COM FALHA. Leia o diagnostico acima." -ForegroundColor Red
exit 1
