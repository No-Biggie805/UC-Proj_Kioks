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
## versão bruta, para tirar dados do sensor.

import serial

porta = '/dev/ttyUSB0'
baud_rate = 115200

print(f"A abrir a porta {porta} em modo BRUTO...")

try:
    ser = serial.Serial(porta, baud_rate, timeout=1)
    print("Porta aberta! À escuta de rigorosamente qualquer coisa...")
    
    while True:
        # Se houver algum byte à espera na gaveta
        if ser.in_waiting > 0:
            # Lê tudo o que lá está
            dados_brutos = ser.read(ser.in_waiting)
            
            # Imprime no ecrã em formato Hexadecimal 
            hex_formatado = dados_brutos.hex(' ').upper()
            print(f"Recebido: [ {hex_formatado} ]")

except KeyboardInterrupt:
    print("\nFechado pelo utilizador.")
except Exception as e:
    print(f"Deu erro: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()



