import tkinter as tk
import time
import csv
import threading
from TF02_pro import MotorDados

class LidarSub:
    # def __init__(self, root, frame_pai):
    def __init__(self):
        # self.root = root
        self.lock = threading.Lock()
        self.running = True

        # sensor
        self.sensor = MotorDados()
        
        self.t0 = None
        self.lista_temp = [] #Lista de dicionários, aqui onde começa o refactor
        self.a_gravar = False #flag que vai determinar o estado de gravação, para memória

        # **Tarefa de fundo** para não bloquear o input() da thread principal
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        
    def _read_loop(self):
        #Thread de fundo: Esta será a que recolhe e calcula os valores
        while self.running:
            if self.a_gravar:

                dist = self.sensor.get_distancia()
                agora = time.time()

                with self.lock:

                    #Calcular a velocidade pela função, depois guardar na lista
                    vel = self._calcular_vel(agora, dist)

                    #Calcular a aceleração pela função, depois guardar na lista
                    acel = self._calcular_acel(agora, vel)

                    if self.a_gravar: #semelhante ao zedSub, força o programa a gravar exclusivamente quando a flag for verdadeiro
                        self.lista_temp.append({"y":dist, "t":agora, "v":vel, "a":acel}) #Lista de dicionarios, cada chave y,t,v,a irá guardar um valor respectivo ao que foi calculado no ciclo atual
                        print("Valores LiDAR:"f"{dist:.2f} {vel:.2f} {acel:.2f}")#Devolve o (status e valor da distancia em cru)
            time.sleep(0.01)

    def _calcular_vel(self, timestamp, valor): #Os Objetos tempo e dist, passam a locais?
        janela = 0.5
        for i in range(len(self.lista_temp) - 1, -1, -1):
            idade = timestamp - self.lista_temp[i]["t"]
            if idade > janela:
                break
        else:
            return 0
        
        ref_index= i + 1
        if ref_index >= len(self.lista_temp):
            return 0

        # guadar o ponto referência, antes de indice ser "velho"
        # ponto_referencia = i + 1 # ERRADO: É o índice do dicionário não a posição em si, para depois calcular os dados.
        ponto_referencia = self.lista_temp[ref_index] #+1 Para somar à posição no momento em que o índice pára

        # calcular o delta_valor (distancia) e o delta_t entre o *agora* e *ponto_referencia*, e devolver delta_valor/delta_t
        delta_valor = valor - ponto_referencia["y"]
        delta_tempo = timestamp - ponto_referencia["t"]

        if delta_tempo <= 0:
            return 0

        return delta_valor/delta_tempo

    # -------x---------        
    def _calcular_acel(self, timestamp, velocidade):
        # criar outra vez um espaço na janela
        janela = 0.5
        for i in range(len(self.lista_temp) -1, -1, -1):
            idade = timestamp - self.lista_temp[i]["t"]
            if idade > janela:
                break
        else:
            return 0

        ref_index= i + 1
        if ref_index >= len(self.lista_temp):
            return 0

        # guadar o ponto referência, antes de indice ser "velho"
        # ponto_referencia = i + 1 # ERRADO: É o índice do dicionário não a posição em si, para depois calcular os dados.
        ponto_referencia = self.lista_temp[ref_index] #+1 Para somar à posição no momento em que o índice pára

        # calcular o delta_valor (distancia) e o delta_t entre o *agora* e *ponto_referencia*, e devolver delta_valor/delta_t
        delta_velocidade = velocidade - ponto_referencia["v"]
        delta_tempo = timestamp - ponto_referencia["t"]
        if delta_tempo <= 0:
            return 0

        return delta_velocidade/delta_tempo

    def _guardar_csv_tentativa(self):
        with self.lock:
            # tempos = [i["t"] - self.lista_temp[0]["t"] for i in self.lista_temp]
            tempos = [i["t"] - self.t0 for i in self.lista_temp]

            with open("tentativa.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "distancia", "velocidade", "aceleracao"])
                for i, leitura in enumerate(self.lista_temp):
                    writer.writerow([f"{tempos[i]:.2f}", f"{leitura["y"]:.2f}",f"{leitura["v"]:.2f}",f"{leitura["a"]:.2f}"])
            #Limpar a lista
            self.lista_temp.clear()

    def alternar_gravacao(self):
        if not self.a_gravar:
            #Ramo de começar a gravar!!
            #O código limpa as listas assim que começar a correr, de seguida passa o correr para recolha de dados a True
            #O lista_temp será também esvaziado, este clear vai proteger o programa quando o for loop do _guardar_csv atinjir exceções
            with self.lock:
                self.lista_temp.clear() 
                self.t0 = time.time() 
            self.a_gravar = True #flag ativa, começou a gravar (isto vai influenciar quando começar a ter o sistema do input() e _read_loop)
        else: 
            #Ramo de parar de gravar
            self.a_gravar = False 
            print("Thread de gravação Parado, a iniciar gravação para ficheiro")
            #Futuramente ver aqui do guardar CSV semelhante ao do GravadorZed
            self._guardar_csv_tentativa()
    
    def fechar(self):
        #fechar o motor de dados
        self.running = False
        self.thread.join(timeout=1)
        self.sensor.fechar()


# if __name__ == "__main__":
#     root = tk.Tk()
#     root.geometry("400x300")
#     frame_teste = tk.Frame(root)
#     frame_teste.pack(fill=tk.BOTH, expand=True)
#     app = LidarSub(root, frame_teste)

#     root.after(2000, app.alternar_gravacao)  # começar a gravar aos 2s
#     root.after(12000, app.alternar_gravacao)  # parar de gravar aos 6s

#     root.mainloop()