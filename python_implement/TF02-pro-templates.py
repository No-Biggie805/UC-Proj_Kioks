#versao ler byte codes byte por byte, (+) verbose, suscetivel a interrupções na ordem!!

# import serial
# import time

# #IMPORTANTE: confirmar a porta! poder ser /dev/ttyACM0 (cabo direto Arduino)
# #ou /dev/ttyusb0 (se por exemplo for o adaptador D-SUN)
# # porta = '/dev/ttyACM0'
# porta = '/dev/ttyUSB0'
# baud_rate = 115200

# print(f"A ligar ao sensor na porta {porta} a {baud_rate} bps...")

# try:
#     ser = serial.Serial(porta, baud_rate, timeout=1)
#     #o arduino faz reset mal o python abra a porta.
#     #Esperar 2s para ele acordar e depois aceitar
#     #fora o "lixo" que ele enviou a meio do processo.
#     time.sleep(2)
#     ser.reset_input_buffer()

#     print("ligação estabelecida! À procura do movimento...")
#     while True:
#         #Procurar primeiro o 0x59
#         if ser.read(1) == b'\x59':
#             #2. confirmar com o segundo
#             if ser.read(1) == b'\x59':
#                 #encontramos o inicio! Lemos o restantes 7 bytes
#                 dados = ser.read(7)
                
#                 if len(dados) == 7:
#                     #colocamos o cabeçalho com os dados para ter os 9 bytes
#                     pacote_completo = b'\x59\x59' + dados

#                     #colocamos o cabeçalho do nosso lado para ver se não haverá ruído
#                     checksum_calculado = sum(pacote_completo[0:8]) & 0xFF
#                     checksum_recebido = pacote_completo[8]

#                     if checksum_calculado == checksum_recebido:
#                         #3.Extração dos dados
#                         distancia = pacote_completo[2] + (pacote_completo[3] * 256)
#                         forca = pacote_completo[4] + (pacote_completo[5] * 256)

#                         #4. A logica do quiosque
#                         if distancia < 150:
#                             alerta = "ALGUEM PERTO! (Ligar ecran)"
#                         else:
#                             alerta = "Limpo!"

#                         print(f"Distancia: {distancia:4} cm | Força: {forca:4} | {alerta}")
#                     else:
#                         print("Aviso: Pacote corrompido, a ignorar...")
# except Exception as e:
#     print(f"Erro faltar: {e}")
# finally:
#     if 'ser' in locals() and ser.is_open:
#         ser.close()
#         print("Porta fechada com segurança.")

#-------------x------------------x--------------------
# versão bruta, para tirar dados do sensor.

# import serial

# porta = '/dev/ttyUSB0'
# baud_rate = 115200

# print(f"A abrir a porta {porta} em modo BRUTO...")

# try:
#     ser = serial.Serial(porta, baud_rate, timeout=1)
#     print("Porta aberta! À escuta de rigorosamente qualquer coisa...")
    
#     while True:
#         # Se houver algum byte à espera na gaveta
#         if ser.in_waiting > 0:
#             # Lê tudo o que lá está
#             dados_brutos = ser.read(ser.in_waiting)
            
#             # Imprime no ecrã em formato Hexadecimal 
#             hex_formatado = dados_brutos.hex(' ').upper()
#             print(f"Recebido: [ {hex_formatado} ]")

# except KeyboardInterrupt:
#     print("\nFechado pelo utilizador.")
# except Exception as e:
#     print(f"Deu erro: {e}")
# finally:
#     if 'ser' in locals() and ser.is_open:
#         ser.close()

#-----------------x------------------------------------
# import serial 
# import time

# porta = '/dev/ttyUSB0'
# baud_rate = 115200

# print(f"A ligar ao sensor na porta {porta} a {baud_rate} bps..")

# try: 
#     ser = serial.Serial(porta,baud_rate,timeout=0.1)
#     #o sensor fazer o reset como era antes o arduino mal o python abrir a porta ?
#     #Esperar 2s para ele acordar e depois aceitar
#     #fora o "lixo" que ele enviou a meio do processo.
#     time.sleep(1)
#     ser.reset_input_buffer()

#     print("ligação estabelecida! À procura do movimento...")

#     buffer_dados = b''

#     while True:
#         if ser.in_waiting > 0:
#             buffer_dados += ser.read(ser.in_waiting)

#         #só tentamos agora se tivermos apenas 9 bytes
#         # Imprime no ecrã em formato Hexadecimal 
#         # hex_formatado = buffer_dados.hex(' ').upper()
#         # print(f"Recebido: [ {hex_formatado} ]")

#         while len(buffer_dados) >= 9:
#             #procurar onde está o cabeçalho
#             inicio = buffer_dados.find(b'\x59\x59')

#             #se nao encontrarmos, ou se o pacote estiver cortado no fim, esperar por mais dados
#             if inicio == -1 or len(buffer_dados) < inicio + 9:
#                 break
#             #Recortamos o pacote perfeito de 9 bytes
#             pacote = buffer_dados[inicio:inicio+9]

#             #Limpar o buffer (limpar o anterior para recolher novo)
#             buffer_dados = buffer_dados[inicio+9:]

#             #validar o checksum
#             soma = sum(pacote[0:8]) & 0xFF

#             if soma == pacote[8]:
#                 #-------------------------------
#                 # A Logica da extracao 
#                 #-------------------------------
#                 distancia = pacote[2] + (256 * pacote[3])
#                 forca = pacote[4] + (256 * pacote[5])
#                 temperatura = (pacote[6] + (256 * pacote[7]))/8 - 256 #Temp = temp/8 - 256; onde temp é composto do que está dentro do valor total da palavra de 16bits 

#                 #A logica do quiosque
#                 if distancia < 150:
#                     alerta = "⚠️ ALGUÉM PERTO! (Ligar Ecrã)"
#                 else:
#                     alerta = "✅ Limpo."
                    
#                 print(f"Distancia da pessoa: {distancia:4}cm | forca do sinal: {forca:5} | temperatura do sensor: {temperatura} | {alerta}")
# except KeyboardInterrupt:
#     print("\nScript terminado por end-user")
# except Exception as e:
#     print(f"Erro fatal: {e}")
# finally:
#     if "ser" in locals() and ser.is_open:
#         ser.close()
#         print("Porta fechada com segurança")
