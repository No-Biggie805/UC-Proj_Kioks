import tkinter as tk
import time
import csv
import threading
from TF02_pro import MotorDados
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class LidarSub:
    def __init__(self, root, frame_pai):
        self.root = root
        self.lock = threading.Lock()
        self.running = True

        # sensor
        self.sensor = MotorDados()
        
        self.max_pontos = 500

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.fig.patch.set_facecolor('#1e1e2e')

        self.ax_dist = self.fig.add_subplot(311)
        self.line_dist, = self.ax_dist.plot([], [], '-r', linewidth=2)
        self._configurar_eixo(self.ax_dist, "Distancia (cm)", (0, 500))
        self.ax_vel = self.fig.add_subplot(312)
        self.line_vel, = self.ax_vel.plot([], [], '-g', linewidth=2)
        self._configurar_eixo(self.ax_vel, "Velocidade (cm/s)", (-150, 150))
        self.ax_acel = self.fig.add_subplot(313)
        self.line_acel, = self.ax_acel.plot([], [], '-b', linewidth=2)
        self._configurar_eixo(self.ax_acel, "Aceleração (cm/s²)", (-300, 300))

        # Memória do gráfico
        self.y_data = []
        self.t_data = []
        self.v_data = []
        self.a_data = []

        self.t0 = None
        self.lista_temp = [] #Lista de dicionários, aqui onde começa o refactor
        self.a_gravar = False #flag que vai determinar o estado de gravação, para memória

        self.eixos = [
            {"ax": self.ax_dist, "line": self.line_dist, "bg":None, "data": self.y_data},
            {"ax": self.ax_vel, "line": self.line_vel, "bg":None, "data": self.v_data},
            {"ax": self.ax_acel, "line": self.line_acel, "bg":None, "data": self.a_data},
        ]

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_pai)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect('resize_event', self._on_resize)
        self.root.after(100, self._init_blit)
        
        # **Tarefa de fundo** para não bloquear o input() da thread principal
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        
        self.update_gui()
        
    def update_gui(self):
        #Thread principal: Este será a que desenha
        # Isto prob. será obseleto, para um formato mais similar ao GravadorZed

        if any(eixo["bg"] is None for eixo in self.eixos):
            self.update_timer_ID = self.root.after(50, self.update_gui)
            return
        """
        Notas
        1. self.running no update_gui, não será necessário porque o update_gui não é um ciclo, mas sim uma callback que se reagenda.
        O Mecanismo de parágem está no <after_cancel(self.update_timer_ID)> do fechar()
        2.
        """
        # with self.lock: #Segurar o lock enquanto o update_gui desenha, pois agora objetos serão partilhados entre threads.
        #     # IMPLEMENTAÇÃO SEM BOILER-PLATE:
        #     # redenhar a linha, isto acontece a cada 100ms
        #     for eixo in self.eixos:
        #         eixo["line"].set_data(range(len(eixo["data"])),eixo["data"])
        #         self.canvas.restore_region(eixo["bg"])
        #         eixo["ax"].draw_artist(eixo["line"])
        #         self.canvas.blit(eixo["ax"].bbox)
        #     self.canvas.flush_events()
        # self.update_timer_ID = self.root.after(100, self.update_gui) #identificador fica de fora, thread de fundo não o lê logo não necessita a proteção

        with self.lock:
            copias = [] #uma por eixo, pela ordem de self.eixos
            self._copia_buffers(copias)
            # for eixo in self.eixos:
            #     copias.append(list(eixo["data"]))

        for eixo, copia in zip(self.eixos, copias):
            eixo["line"].set_data(range(len(copia)),copia)
            self.canvas.restore_region(eixo["bg"])
            eixo["ax"].draw_artist(eixo["line"])
            self.canvas.blit(eixo["ax"].bbox)

        self.canvas.flush_events()
        self.update_timer_ID = self.root.after(100, self.update_gui) #identificador fica de fora, thread de fundo não o lê logo não necessita a proteção

    def _copia_buffers(self, copias):
        # copias = [] #uma por eixo, pela ordem de self.eixos
        for eixo in self.eixos:
            copias.append(list(eixo["data"]))

    def _read_loop(self):
        #Thread de fundo: Esta será a que recolhe e calcula os valores
        while self.running:
            if self.a_gravar:

                dist = self.sensor.get_distancia()
                agora = time.time()

                with self.lock:
                    # guardar valor da distancia na lista
                    self._guardar_com_limite(self.y_data, dist)
                    # guardar valor do tempo na lista
                    self._guardar_com_limite(self.t_data, agora)

                    #Calcular a velocidade pela função, depois guardar na lista
                    vel = self._calcular_vel(agora, dist)
                    self._guardar_com_limite(self.v_data, vel)

                    #Calcular a aceleração pela função, depois guardar na lista
                    acel = self._calcular_acel(agora, vel)
                    self._guardar_com_limite(self.a_data, acel)

                    if self.a_gravar: #semelhante ao zedSub, força o programa a gravar exclusivamente quando a flag for verdadeiro
                        self.lista_temp.append({"y":dist, "t":agora, "v":vel, "a":acel}) #Lista de dicionarios, cada chave y,t,v,a irá guardar um valor respectivo ao que foi calculado no ciclo atual
                        print("Valores LiDAR:"f"{dist:.2f} {vel:.2f} {acel:.2f}")#Devolve o (status e valor da distancia em cru)
                # print("agora anterior=", agora_anterior)
                # agora_anterior = agora
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

    def _init_blit(self):
        for eixo in self.eixos:
            eixo["bg"] = self.canvas.copy_from_bbox(eixo["ax"].bbox) #criar snapshot do background (continuamente)

    def _on_resize(self, event):
        for eixo in self.eixos: 
            eixo["bg"] = None #Limpar a informação do background
        self.root.after(100, self._reinit_blit)

    def _reinit_blit(self):
        for eixo in self.eixos:
            eixo["line"].set_data([],[]) #, copias
        self.canvas.draw()
        for eixo in self.eixos:
            eixo["bg"] = self.canvas.copy_from_bbox(eixo["ax"].bbox)

        with self.lock:
            copias = [] #uma por eixo, pela ordem de self.eixos
            # for eixo in self.eixos:
            #     copias.append(list(eixo["data"]))
            self._copia_buffers(copias)
        for eixo, copia in zip(self.eixos, copias):
            eixo["line"].set_data(range(len(copia)),copia)

    def _configurar_eixo(self, ax, ylabel, ylim):
        ax.set_facecolor('#2e2e3e')
        ax.set_ylim(*ylim)
        ax.set_xlim(0, self.max_pontos)
        ax.tick_params(colors='white')
        ax.set_ylabel(ylabel)
        ax.yaxis.label.set_color('white')

    def _guardar_com_limite(self, lista, valor):
        lista.append(valor)
        if len(lista) > self.max_pontos:
            lista.pop(0)

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
            self.y_data.clear()
            self.t_data.clear()
            self.v_data.clear()
            self.a_data.clear()

            #O lista_temp será também esvaziado, este clear vai proteger o programa quando o for loop do _guardar_csv atinjir exceções
            with self.lock:
                self.lista_temp.clear() 
                self.t0 = time.time() 
            self.a_gravar = True #flag ativa, começou a gravar (isto vai influenciar quando começar a ter o sistema do input() e _read_loop)
        else: 
            #Ramo de parar de gravar
            self.a_gravar = False 
            #Futuramente ver aqui do guardar CSV semelhante ao do GravadorZed
            self._guardar_csv_tentativa()
    
    def fechar(self):
        #Fechar o identificador
        self.root.after_cancel(self.update_timer_ID)
        #fechar o motor de dados
        self.running = False
        self.thread.join(timeout=1)
        self.sensor.fechar()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    frame_teste = tk.Frame(root)
    frame_teste.pack(fill=tk.BOTH, expand=True)
    app = LidarSub(root, frame_teste)

    root.after(2000, app.alternar_gravacao)  # começar a gravar aos 2s
    root.after(12000, app.alternar_gravacao)  # parar de gravar aos 6s

    root.mainloop()