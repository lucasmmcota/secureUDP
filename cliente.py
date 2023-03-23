# -*- coding: iso-8859-1 -*-
__author__ = 'Lucas Monteiro'

import os, socket

HOST = 'localhost'  # Endereço IP
PORT = 2000         # Porta utilizada para conexão
BUFFER_SIZE = 1460  # Tamanho do buffer para recepção dos dados

def menu_principal():
    print('\n--------------- SERVIDOR DE ARQUIVOS ---------------\n')
    print('Realize o seu download ou faça um upload caso possua uma senha.')
    print('0- Sair')
    print('1- Realizar Download')
    print('2- Realizar Upload')

def receber_pacotes(s, caminho_arquivo):
    # Receber tamanho do arquivo
    tamanho_arquivo, addr = s.recvfrom(BUFFER_SIZE)
    tamanho_arquivo = int(tamanho_arquivo.decode())
    print("\nTamanho do arquivo:", tamanho_arquivo, "bytes")

    # Receber arquivo
    with open(caminho_arquivo, "wb") as f:
        num_seq = 0
        recebidos = 0
        while recebidos < tamanho_arquivo:
            dados, addr = s.recvfrom(BUFFER_SIZE)
            f.write(dados)
            recebidos += len(dados)

            # Enviar confirmação
            s.sendto(str(num_seq).encode(), addr)
            num_seq += 1
        print('\nBytes recebidos:', recebidos)

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        while True:
            menu_principal()
            opcao = input('Digite a sua opção: ')
            s.sendto(opcao.encode(), (HOST, PORT))
            if opcao.isdigit():
                opcao = int(opcao)
                if opcao == 0:
                    break
                elif opcao == 1:
                    # Receber lista de arquivos
                    lista_arquivos, addr = s.recvfrom(BUFFER_SIZE)
                    lista_arquivos = lista_arquivos.decode()
                    print("\nLista de arquivos:")
                    print(lista_arquivos)

                    # Solicitar nome do arquivo
                    nome_arquivo = input("\nDigite o nome do arquivo que você deseja fazer o download: ")
                    
                    # Enviar nome do arquivo
                    s.sendto(nome_arquivo.encode(), (HOST, PORT))
                    resposta, addr = s.recvfrom(BUFFER_SIZE)
                    resposta = resposta.decode()

                    if resposta == "Arquivo encontrado":
                        receber_pacotes(s, "downloads/" + nome_arquivo)
                    else:
                        print(resposta)

                elif opcao == 2:
                    # Enviar senha
                    senha = input("\nDigite a sua senha: ")
                    s.sendto(senha.encode(), (HOST, PORT))
                    resposta, addr = s.recvfrom(BUFFER_SIZE)
                    resposta = resposta.decode()

                    if resposta == "Senha correta":
                        # Solicitar nome do arquivo
                        nome_arquivo = input("\nDigite o nome do arquivo que você deseja fazer o upload: ")
                        
                        # Enviar nome do arquivo
                        s.sendto(nome_arquivo.encode(), (HOST, PORT))
                        resposta, addr = s.recvfrom(BUFFER_SIZE)
                        resposta = resposta.decode()

                        if resposta == "Arquivo encontrado":
                            receber_pacotes(s, "servidor/" + os.path.basename(nome_arquivo))
                        else:
                            print(resposta)
                    else:
                        print(resposta)
                else:
                    print('Opção inválida! Digite o número da opção que você deseja.')
            else:
                print('Opção inválida! Digite o número da opção que você deseja.')
        # Fechar socket
        print('\nEncerrando...')
        s.close()
    except Exception as error:
        print('Erro na conexão com o servidor!')
        print(error)
        s.close()
        return

if __name__ == "__main__":
    main()
