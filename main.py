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
_COD_PROGRAM      = "A19"  # program
_COD_DECLARATIONS = "A04"  # declarations
_COD_ENDDECL      = "A06"  # endDeclarations
_COD_FUNCTIONS    = "A13"  # functions
_COD_ENDFUNCTIONS = "A08"  # endFunctions
_COD_FUNCTYPE     = "A14"  # funcType
_COD_ENDFUNCTION  = "A07"  # endFunction
_COD_ENDPROGRAM   = "A10"  # endProgram
_COD_VARTYPE      = "A24"  # varType
_COD_LBRACKET     = "B08"  # [  — indica declaração de vetor

# Apenas identificadores vão para a tabela de símbolos
_CODIGOS_TABELA = {"C01", "C02", "C03"} 

# Mapeamento tipo da linguagem
_TIPO_SIMB = {
    "A20": "FP",  # real
    "A16": "IN",  # integer
    "A22": "ST",  # string
    "A01": "BL",  # boolean
    "A03": "CH",  # character
    "A25": "VD",  # void
}
_TIPO_SIMB_ARRAY = {
    "A20": "AF",  # array of real
    "A16": "AI",  # array of integer
    "A22": "AS",  # array of string
    "A01": "AB",  # array of boolean
    "A03": "AC",  # array of character
}


def main():
    # ----------------------------------------------------------
    # 1. Leitura do parâmetro de entrada
    # ----------------------------------------------------------
    if len(sys.argv) < 2:
        print("Para usar o checker: python main.py <nome_do_arquivo>")
        print("Exemplo: python main.py testes/MeuTeste")
        return

    entrada = sys.argv[1]

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
    # ----------------------------------------------------------
    tokens = []
    codigo_anterior: str | None = None

    # Estado para inferência de tipo durante declarações
    tipo_corrente: str | None = None   # ex: "IN", "FP", "ST"...
    eh_vetor: bool = False             # Atualizado se após vartype abriu um array
    indices_declarados: list[int] = [] # índices na tabela dos vars desta declaração

    while True:
        tok = lexico.obter_proximo_token()
        if tok is None:
            break  # EOF

        # --- Atualiza escopo ---
        if tok.codigo == _COD_PROGRAM:
            escopo.abrir(NivelEscopo.PROGRAMA)

        elif tok.codigo == _COD_DECLARATIONS:
            escopo.abrir(NivelEscopo.DECLARACOES)

        elif tok.codigo == _COD_ENDDECL:
            escopo.fechar()

        elif tok.codigo == _COD_FUNCTIONS:
            escopo.abrir(NivelEscopo.FUNCOES)

        elif tok.codigo == _COD_FUNCTYPE:
            escopo.abrir(NivelEscopo.CORPO_FUNCAO)
            escopo.sinalizar_functype()

        elif tok.codigo == _COD_ENDFUNCTION:
            escopo.fechar()

        elif tok.codigo == _COD_ENDFUNCTIONS:
            escopo.fechar()

        elif tok.codigo == _COD_ENDPROGRAM:
            escopo.fechar()

        #Detecta início de declaração de variável: varType <tipo>
        if tok.codigo == _COD_VARTYPE:
            tipo_corrente = None
            eh_vetor = False
            indices_declarados = []

        # guarda o código A se teve um vartype antes e se o token atual é um tipo válido    
        elif codigo_anterior in (_COD_VARTYPE, _COD_FUNCTYPE) and tok.codigo in _TIPO_SIMB:
            tipo_corrente = tok.codigo

        # Detecta se é vetor: varType <tipo> [] 
        elif tok.codigo == _COD_LBRACKET and escopo.esta_em(NivelEscopo.DECLARACOES):
            eh_vetor = True

        # Ao encontrar ";" encerra a declaração atual
        elif tok.codigo == "B01":  # semicolon
            # Aplica o tipo a todos os identificadores desta declaração
            if tipo_corrente and indices_declarados:
                mapa = _TIPO_SIMB_ARRAY if eh_vetor else _TIPO_SIMB
                sigla = mapa.get(tipo_corrente, "-")
                for idx in indices_declarados:
                    simb = tabela_simbolos.buscar_por_indice(idx)
                    if simb:
                        simb.set_tipo(sigla)
            tipo_corrente = None
            eh_vetor = False
            indices_declarados = []

        # Refinamento do código do identificador
        if tok.codigo == "C01":
            tok.codigo = escopo.codigo_para_identificador(codigo_anterior)

        # Insere identificadores na tabela de símbolos
        if tok.codigo in _CODIGOS_TABELA:
            idx = tabela_simbolos.inserir_ou_atualizar(
                lexeme           = tok.lexeme,
                codigo           = tok.codigo,
                qtd_antes_trunc  = tok.qtd_antes_trunc,
                qtd_depois_trunc = tok.qtd_depois_trunc,
                linha            = tok.linha,
            )
            tok.indice_tab = idx

            # Acumula os índices de variáveis da declaração corrente para
            # atribuir o tipo quando encontrar o ";"
            if tipo_corrente and tok.codigo == "C01":
                indices_declarados.append(idx)

        tokens.append(tok)
        codigo_anterior = tok.codigo

    # ----------------------------------------------------------
    # 5. Geração dos relatórios .LEX e .TAB
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


if __name__ == "__main__":
    main()
