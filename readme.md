# Analisador Léxico da linguagem Bobenzo

Este projeto implementa um compilador (fase de análise léxica e gestão de tabelas de símbolos) para a linguagem com extensão `.261`. O programa não realiza a análise sintática completa, contendo apenas uma parte inicial de gerenciamento de escopo.

## Como Executar

O analisador pode ser executado de duas formas: utilizando o código-fonte em Python ou diretamente pelo executável binário (`main.exe`) gerado pelo PyInstaller (localizado na pasta `dist`).

### Opção 1: Pelo Executável (`main.exe`)

O executável está localizado dentro da pasta `dist/`. (Caso mova o executável para outro local, basta ajustar o caminho correspondente.)

1. Abra o terminal na pasta raiz do projeto (Prompt de Comando ou PowerShell no Windows).
2. Execute o binário apontando para qualquer arquivo de teste, conforme o exemplo:

```bash
./dist/main.exe .\testes\T01_basico.261
```

### Opção 2: Pelo Código-Fonte (`main.py`)

Requer o **Python 3.10+** instalado no sistema.

1. Abra o terminal na pasta raiz do projeto.
2. Execute o arquivo `main.py` passando o caminho do arquivo de teste como argumento (não é necessário informar a extensão `.261` do arquivo):

```bash
python main.py testes/MeuTeste
```