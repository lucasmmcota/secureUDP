# -*- coding: iso-8859-1 -*-
__author__ = 'Lucas Monteiro'

import os, socket

HOST = 'localhost'  # Endereço IP
PORT = 2000         # Porta utilizada para receber conexões
BUFFER_SIZE = 1460  # Tamanho do buffer para recepção dos dados

CAMINHO_SERVIDOR = 'servidor/'
SENHA_CORRETA = '1234'

def enviar_pacotes(s, addr, caminho_arquivo):
    # Enviar tamanho do arquivo
    tamanho_arquivo = os.path.getsize(caminho_arquivo)
    s.sendto(str(tamanho_arquivo).encode(), addr)

    # Enviar arquivo
    with open(caminho_arquivo, "rb") as f:
        num_seq = 0
        while True:
            dados = f.read(BUFFER_SIZE)
            if not dados:
                break

            # Enviando pacote
            s.sendto(dados, addr)

            # Esperar confirmação - Tempo limite de 5 segundos
            ack = -1
            while num_seq != ack:
                s.settimeout(5)
                try:
                    ack, addr = s.recvfrom(BUFFER_SIZE)
                    if ack.decode() == str(num_seq):
                        break
                except socket.timeout:
                    s.sendto(dados, addr)

            # Atualizar o número de sequência
            num_seq += 1

def main():
    print("Servidor UDP iniciado...")

    while True:
        print("Aguardando conexões...")

        # Iniciar servidor
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((HOST, PORT))
        conexao = True

        print(f"Servidor de Arquivos conetado em {HOST}:{PORT}")

        while conexao:
            try:
                opcao, addr = s.recvfrom(BUFFER_SIZE)
                opcao = opcao.decode()

                # Verifica se o usuario digitou um numero
                if opcao.isdigit():
                    opcao = int(opcao)
                    if opcao == 0:
                        print('Encerrando socket do cliente {} !' . format(addr[0]))
                        s.close()
                        conexao = False
                    elif opcao == 1:
                        # Enviar lista de arquivos
                        arquivos = os.listdir(CAMINHO_SERVIDOR)
                        lista_arquivos = "\n".join(arquivos)
                        s.sendto(lista_arquivos.encode(), addr)

                        # Receber nome do arquivo
                        nome_arquivo, addr = s.recvfrom(BUFFER_SIZE)
                        nome_arquivo = nome_arquivo.decode()

                        # Verificar se arquivo existe
                        if nome_arquivo in arquivos:
                            s.sendto("Arquivo encontrado".encode(), addr)
                            enviar_pacotes(s, addr, CAMINHO_SERVIDOR + nome_arquivo)
                        else:
                            s.sendto("Arquivo não encontrado".encode(), addr)

                        s.close()
                        break
                    elif opcao == 2:
                        # Receber senha do cliente
                        senha, addr = s.recvfrom(BUFFER_SIZE)
                        senha = senha.decode()
                        if senha == SENHA_CORRETA:
                            s.sendto("Senha correta".encode(), addr)

                            # Receber caminho do arquivo
                            caminho_arquivo, addr = s.recvfrom(BUFFER_SIZE)
                            caminho_arquivo = caminho_arquivo.decode()

                            # Verificar se arquivo existe
                            if os.path.exists(caminho_arquivo):
                                s.sendto("Arquivo encontrado".encode(), addr)
                                enviar_pacotes(s, addr, caminho_arquivo)
                            else:
                                s.sendto("Arquivo não encontrado".encode(), addr)
                        else:
                            s.sendto("Senha incorreta".encode(), addr)
                            
                        s.close()
                        break
            except Exception as error:
                print('Erro na conexão com o cliente !')
                print(error)
                s.close()
                return

if __name__ == "__main__":
    main()
