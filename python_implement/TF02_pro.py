import threading
import time
import serial 

# porta = '/dev/ttyUSB0'
# baud_rate = 115200

# print(f"A ligar ao sensor na porta {porta} a {baud_rate} bps..")

class MotorDados:
    def __init__(self, porta = '/dev/ttyUSB0', baud_rate = 115200):
        print(f"A ligar ao sensor na porta {porta} a {baud_rate} bps..")
    # try: 
        self.ser = serial.Serial(porta,baud_rate,timeout=0.1)
        self.distancia = 0
        # self.forca = 0
        # self.temperatura = 0
        self.running = True

        #Tarefa de fundo para nao travar a GUI
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

        # #o sensor fazer o reset como era antes o arduino mal o python abrir a porta ?
        # #Esperar 2s para ele acordar e depois aceitar
        # #fora o "lixo" que ele enviou a meio do processo.
        # time.sleep(1)
        # ser.reset_input_buffer()

    def _read_loop(self):
        print("ligação estabelecida! À procura do movimento...")

        buffer_dados = b''

        while self.running:
            if self.ser.in_waiting > 0:
                buffer_dados += self.ser.read(self.ser.in_waiting)
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
                    self.distancia = pacote[2] + (256 * pacote[3])
                    # forca = pacote[4] + (256 * pacote[5])
                    # temperatura = (pacote[6] + (256 * pacote[7]))/8 - 256 #Temp = temp/8 - 256; onde temp é composto do que está dentro do valor total da palavra de 16bits 

        time.sleep(0.01) #Pequena pausa para não fritar a CPU

                    # #A logica do quiosque
                    # if distancia < 150:
                    #     alerta = "⚠️ ALGUÉM PERTO! (Ligar Ecrã)"
                    # else:
                    #     alerta = "✅ Limpo."
    def get_distancia(self):
        return self.distancia

    #                 print(f"Distancia da pessoa: {distancia:4}cm | forca do sinal: {forca:5} | temperatura do sensor: {temperatura} | {alerta}")
    # except KeyboardInterrupt:
    #     print("\nScript terminado por end-user")
    # except Exception as e:
    #     print(f"Erro fatal: {e}")
    # finally:
    #     if "ser" in locals() and ser.is_open:
    #         ser.close()
    #         print("Porta fechada com segurança")
    

                    