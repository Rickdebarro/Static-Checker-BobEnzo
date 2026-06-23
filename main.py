import os
import sys

# Garante que Src/ está no path para os imports funcionarem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Src"))

from lexico.tabela_reservados import TabelaPalavrasReservadas
from lexico.Alexico import Alexico
from tabela.tabela_simbolos import TabelaSimbolos
from relatorios.gerador_lex import GeradorRelatorioLEX
from relatorios.gerador_tab import GeradorRelatorioTAB
from sintatico.escopo import ControladorEscopo, NivelEscopo

# =============================================================
# DADOS DA EQUIPE
# =============================================================
CODIGO_EQUIPE = "EQ03"
COMPONENTES = [
    {"nome": "André Delarovera Rezende",   "email": "andre.rezende@aln.senaicimatec.edu.br",   "telefone": "(71) 9606-5925"},
    {"nome": "Gustavo Arleo Martins", "email": "gustavo.martins@aln.senaicimatec.edu.br", "telefone": "(71) 9127-0958"},
    {"nome": "Henrique Barros Araújo Correia", "email": "henrique.correia@aln.senaicimatec.edu.br", "telefone": "(75) 98883-7459"},
    {"nome": "João Paulo Caldas",  "email": "joao.lucas@aln.senaicimatec.edu.b",  "telefone": "(71) 9737-3872"},
]

# =============================================================
# Códigos de átomos que disparam mudança de escopo
# =============================================================
_COD_PROGRAM        = "A19"  # program
_COD_DECLARATIONS   = "A04"  # declarations
_COD_ENDDECL        = "A06"  # endDeclarations
_COD_FUNCTIONS      = "A13"  # functions
_COD_ENDFUNCTIONS   = "A08"  # endFunctions
_COD_FUNCTYPE       = "A14"  # funcType  → abre escopo de corpo de função
_COD_ENDFUNCTION    = "A07"  # endFunction
_COD_ENDPROGRAM     = "A10"  # endProgram

# Códigos C que devem ir para a tabela de símbolos
_CODIGOS_TABELA = {"C01", "C02", "C03", "C04", "C05", "C06", "C07"}


def main():
    # ----------------------------------------------------------
    # 1. Leitura do parâmetro de entrada
    # ----------------------------------------------------------
    if len(sys.argv) < 2:
        print("Para usar o checker: python main.py <nome_do_arquivo>")
        print("Exemplo: python main.py testes/MeuTeste")
        return

    entrada = sys.argv[1]

    # Suporte a caminho absoluto ou relativo
    if os.path.isabs(entrada):
        caminho_261 = entrada + ".261"
    else:
        caminho_261 = os.path.join(os.getcwd(), entrada + ".261")

    if not os.path.isfile(caminho_261):
        print(f"Erro: arquivo '{caminho_261}' não encontrado.")
        return

    # ----------------------------------------------------------
    # 2. Abertura do arquivo fonte
    # ----------------------------------------------------------
    try:
        with open(caminho_261, "r", encoding="ascii", errors="ignore") as f:
            conteudo = f.read()
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
        return

    nome_base   = os.path.splitext(os.path.basename(caminho_261))[0]
    pasta_saida = os.path.dirname(caminho_261)
    nome_fonte  = os.path.basename(caminho_261)

    print(f"Analisando: {caminho_261}")

    # ----------------------------------------------------------
    # 3. Inicialização das estruturas de dados
    # ----------------------------------------------------------
    tabela_reservada = TabelaPalavrasReservadas()
    tabela_simbolos  = TabelaSimbolos()
    escopo           = ControladorEscopo()
    lexico           = Alexico(conteudo, tabela_reservada)

    # ----------------------------------------------------------
    # 4. Loop sintax-driven — UMA chamada ao léxico por token
    #    O sintático controla o escopo e decide o código C correto
    # ----------------------------------------------------------
    tokens = []
    codigo_anterior: str | None = None

    while True:
        tok = lexico.obter_proximo_token()
        if tok is None:
            break  # EOF

        # --- Atualiza o escopo ANTES de processar o identificador ---
        # (assim quando o identificador chegar o escopo já está correto)
        if tok.codigo == _COD_PROGRAM:
            escopo.abrir(NivelEscopo.PROGRAMA)

        elif tok.codigo == _COD_DECLARATIONS:
            escopo.abrir(NivelEscopo.DECLARACOES)

        elif tok.codigo == _COD_ENDDECL:
            escopo.fechar()  # fecha DECLARACOES

        elif tok.codigo == _COD_FUNCTIONS:
            escopo.abrir(NivelEscopo.FUNCOES)

        elif tok.codigo == _COD_FUNCTYPE:
            escopo.abrir(NivelEscopo.CORPO_FUNCAO)
            escopo.sinalizar_functype()  # próximo identificador = functionName

        elif tok.codigo == _COD_ENDFUNCTION:
            escopo.fechar()  # fecha CORPO_FUNCAO

        elif tok.codigo == _COD_ENDFUNCTIONS:
            escopo.fechar()  # fecha FUNCOES

        elif tok.codigo == _COD_ENDPROGRAM:
            escopo.fechar()  # fecha PROGRAMA

        # --- Identificadores: refinamento de código e tabela de símbolos ---
        if tok.codigo == "C01":
            tok.codigo = escopo.codigo_para_identificador(codigo_anterior)

        # Todos os códigos C vão para a tabela de símbolos
        if tok.codigo in _CODIGOS_TABELA:
            idx = tabela_simbolos.inserir_ou_atualizar(
                lexeme           = tok.lexeme,
                codigo           = tok.codigo,
                qtd_antes_trunc  = tok.qtd_antes_trunc,
                qtd_depois_trunc = tok.qtd_depois_trunc,
                linha            = tok.linha,
            )
            tok.indice_tab = idx

        tokens.append(tok)
        codigo_anterior = tok.codigo

    # ----------------------------------------------------------
    # 5. Geração dos relatórios .LEX e .TAB
    #    Os arquivos são gerados na mesma pasta do .261
    # ----------------------------------------------------------
    caminho_lex = os.path.join(pasta_saida, nome_base + ".LEX")
    caminho_tab = os.path.join(pasta_saida, nome_base + ".TAB")

    GeradorRelatorioLEX(CODIGO_EQUIPE, COMPONENTES).gerar(
        caminho_lex, nome_fonte, tokens
    )
    GeradorRelatorioTAB(CODIGO_EQUIPE, COMPONENTES).gerar(
        caminho_tab, nome_fonte, tabela_simbolos
    )

    print(f"\nResumo:")
    print(f"  Tokens reconhecidos : {len(tokens)}")
    print(f"  Símbolos na tabela  : {len(tabela_simbolos)}")
    print(f"  Escopo final        : {escopo}")

    return 0;

if __name__ == "__main__":
    main()
