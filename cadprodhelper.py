import json
import os

if os.name == 'nt': # Windows
    directory = os.getenv('LOCALAPPDATA') + "/ZMasterPrint/data"

else: # Linux and MacOS
    directory = os.path.expanduser("~") + "/.local/share/ZMasterPrint"

arquivo_json = directory + '/dados_produtos.json'

def write_data(dados_produtos):
    global directory
    global arquivo_json
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(arquivo_json, 'w+') as arquivo:
        json.dump(dados_produtos, arquivo, indent=4)
        arquivo.flush()
        arquivo.close()

# def read_data():
#     try:
#         with open(arquivo_json, 'r') as arquivo:
#             dados_produtos = json.load(arquivo)
#     except FileNotFoundError:
#         # Se o arquivo não existir, crie uma estrutura vazia
#         dados_produtos = {"produtos": []}
#         return dados_produtos
def read_data():
    global directory
    global arquivo_json
    if not os.path.exists(arquivo_json):
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Se o arquivo não existir, estrutura inicial
        estrutura_inicial = {
            "produtos": []
        }
        # Crie o arquivo e escreva a estrutura inicial nele
        with open(arquivo_json, 'w+') as arquivo:
            json.dump(estrutura_inicial, arquivo)
            arquivo.flush()
            arquivo.close()

    with open(arquivo_json, 'r') as arquivo:
        dados_produtos = json.load(arquivo)
    return dados_produtos
