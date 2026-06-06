import os
import sys

def main():
    # 1. Verifica se o parâmetro foi passado
    if len(sys.argv) < 2:
        print("Para usar o checker digite no terminal: python main.py <nome_do_arquivo>")
        return
    
    entrada_usuario = sys.argv[1]
    
    nome_arquivo_com_extensao = f"{entrada_usuario}.261"

    if not os.path.isfile(nome_arquivo_com_extensao):
        print(f"Erro: O arquivo '{nome_arquivo_com_extensao}' não foi encontrado.")
        return

   
    print(f"Sucesso: Abrindo e analisando '{nome_arquivo_com_extensao}'...")
    
 
    try:
        with open(nome_arquivo_com_extensao, 'r', encoding='ascii') as arquivo:
            conteudo = arquivo.read()
            
            # TODO: Lógica pra chamar o analisador léxico e sintático talvez aqui
            
    except UnicodeDecodeError:
        print(f"Erro: O arquivo '{nome_arquivo_com_extensao}' contém caracteres não-ASCII.")

if __name__ == "__main__":
    main()