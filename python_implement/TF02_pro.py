import threading
import time
import serial 

# porta = '/dev/ttyUSB0'
# baud_rate = 115200

# print(f"A ligar ao sensor na porta {porta} a {baud_rate} bps..")

class MotorDados:
    def __init__(self, porta = '/dev/ttyUSB0', baud_rate = 115200):
        print(f"A ligar ao sensor na porta {porta} a {baud_rate} bps..")
        self.ser = serial.Serial(porta,baud_rate,timeout=0.1)
        self.distancia = 0
        self.forca = 0
        self.temperatura = 0
        self.running = True

        #Tarefa de fundo para nao travar a GUI
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def _read_loop(self):
        print("ligação estabelecida! À procura do movimento...")

        buffer_dados = b'' #b'' para guardar bytes puros (HEX)

        while self.running:
            if self.ser.in_waiting > 0:
                buffer_dados += self.ser.read(self.ser.in_waiting) #preencher o buffer no canal do serial
            #só tentamos agora se tivermos apenas 9 bytes
            #caso não tiver os 9 bytes passa ao seguinte ignorando qualquer buffer que tenha menos 
            while len(buffer_dados) >= 9:
                #começou agora a processar os dados no raspberry pi

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
                    self.forca = pacote[4] + (256 * pacote[5])
                    self.temperatura = (pacote[6] + (256 * pacote[7]))/8 - 256 #Temp = temp/8 - 256; onde temp é composto do que está dentro do valor total da palavra de 16bits 
        time.sleep(0.01) #Pequena pausa antes de voltar ao serial, isto evita maior uso da CPU em ciclos vazios

    def get_distancia(self):
        return self.distancia
    def get_forca(self):
        return self.forca
    def get_temperatura(self):
        return self.temperatura