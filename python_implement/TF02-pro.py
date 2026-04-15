import serial 
import time

porta = '/dev/ttyUSB0'
baud_rate = 115200

print(f"A ligar ao sensor na porta {porta} a {baud_rate} bps..")

try: 
    ser = serial.Serial(porta,baud_rate,timeout=0.1)
    #o sensor fazer o reset como era antes o arduino mal o python abrir a porta ?
    #Esperar 2s para ele acordar e depois aceitar
    #fora o "lixo" que ele enviou a meio do processo.
    time.sleep(1)
    ser.reset_input_buffer()

    print("ligação estabelecida! À procura do movimento...")

    buffer_dados = b''

    while True:
        if ser.in_waiting > 0:
            buffer_dados += ser.read(ser.in_waiting)
        #só tentamos agora se tivermos apenas 9 bytes
        while len(buffer_dados) >= 9:
            #procurar onde está o cabeçalho
            inicio = buffer_dados.find(b'\x59\x59')

            #se nao encontrarmos, ou se o pacote estiver cortado no fim, esperar por mais dados
            if inicio == -1 or len(buffer_dados) < inicio + 9:
                break
            #Recortamos o pacote perfeito de 9 bytes
            pacote = buffer_dados[inicio:inicio+9]

            #Limpar o buffer (limpar o anterior para recolher novo)
            buffer_dados = buffer_dados[inicio+9:]

            #validar o checksum
            soma = sum(pacote[0:8]) & 0xFF

            if soma == pacote[8]:
                #-------------------------------
                # A Logica da extracao 
                #-------------------------------
                distancia = pacote[2] + (256 * pacote[3])
                forca = pacote[4] + (256 * pacote[5])
                temperatura = (pacote[6] + (256 * pacote[7]))/8 - 256 #Temp = temp/8 - 256; onde temp é composto do que está dentro do valor total da palavra de 16bits 

                #A logica do quiosque
                if distancia < 150:
                    alerta = "⚠️ ALGUÉM PERTO! (Ligar Ecrã)"
                else:
                    alerta = "✅ Limpo."
                    
                print(f"Distancia da pessoa: {distancia:4}cm | forca do sinal: {forca:5} | temperatura do sensor: {temperatura} | {alerta}")
except KeyboardInterrupt:
    print("\nScript terminado por end-user")
except Exception as e:
    print(f"Erro fatal: {e}")
finally:
    if "ser" in locals() and ser.is_open:
        ser.close()
        print("Porta fechada com segurança")

                    










