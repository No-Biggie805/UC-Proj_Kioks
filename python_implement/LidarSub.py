import tkinter as tk
import time
import csv
from TF02_pro import MotorDados
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class LidarSub:
    def __init__(self, root, frame_pai):
        self.root = root

        # sensor
        self.sensor = MotorDados()
        
        self.max_pontos = 50

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

        self.update_gui()
        
    def update_gui(self):
        # Isto prob. será obseleto, para um formato mais similar ao GravadorZed

        if any(eixo["bg"] is None for eixo in self.eixos):
            self.root.after(50, self.update_gui)
            return

        dist = self.sensor.get_distancia()
        agora = time.time()

        # guardar valor da distancia na lista
        self._guardar_com_limite(self.y_data, dist)
        # guardar valor do tempo na lista
        self._guardar_com_limite(self.t_data, agora)

        N = 5
        if len(self.y_data) >= N:
            self.delta_dist = self.y_data[-1] - self.y_data[-N]
            self.delta_t = self.t_data[-1] - self.t_data[-N]
            vel = self.delta_dist / self.delta_t
            self._guardar_com_limite(self.v_data, vel)
        else: 
            self.v_data.append(0)
            vel = 0

        if len(self.v_data) >= N:
            self.delta_t = self.t_data[-1] - self.t_data[-N]
            self.delta_v = self.v_data[-1] - self.v_data[-N]

            acel = self.delta_v/self.delta_t
            self._guardar_com_limite(self.a_data, acel)
        else:
            self.a_data.append(0)
            acel = 0
        
        # if self.a_gravar:
        self.lista_temp.append({"y":dist, "t":agora, "v":vel, "a":acel}) #Lista de dicionarios, cada chave y,t,v,a irá guardar um valor respectivo ao que foi calculado no ciclo atual
        print(f"{dist:.2f} {vel:.2f} {acel:.2f}")#Devolve o (status e valor da distancia em cru)

        # IMPLEMENTAÇÃO SEM BOILER-PLATE:
        # redenhar a linha, isto acontece a cada 100ms
        for eixo in self.eixos:
            eixo["line"].set_data(range(len(eixo["data"])),eixo["data"])
            self.canvas.restore_region(eixo["bg"])
            eixo["ax"].draw_artist(eixo["line"])
            self.canvas.blit(eixo["ax"].bbox)

        self.canvas.flush_events()
        self.root.after(100, self.update_gui)

    def _init_blit(self):
        for eixo in self.eixos:
            eixo["bg"] = self.canvas.copy_from_bbox(eixo["ax"].bbox) #criar snapshot do background (continuamente)

    def _on_resize(self, event):
        for eixo in self.eixos: 
            eixo["bg"] = None #Limpar a informação do background
        self.root.after(100, self._reinit_blit)

    def _reinit_blit(self):
        for eixo in self.eixos:
            eixo["line"].set_data([],[]) #Limpar a lista temporariamente
        self.canvas.draw()
        for eixo in self.eixos:
            eixo["bg"] = self.canvas.copy_from_bbox(eixo["ax"].bbox)
        for eixo in self.eixos:
            eixo["line"].set_data(range(len(eixo["data"])),eixo["data"])
        #Resultado final, fica sem linhas que se transponham, que era o problema inicial quando se fez o blit.

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
        tempos = [i["t"] - self.lista_temp[0]["t"] for i in self.lista_temp]

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
            #O código vai por agora vai a limpeza na memória assim que premir Enter, portanto antes de começar a gravar novamente, esvazia as listas
            self.y_data.clear()
            self.t_data.clear()
            self.v_data.clear()
            self.a_data.clear()

            #O lista_temp será também esvaziado, mas quando mudar para como está o GravadorZed será adotado talvez para _guardar_csv_tentativa
            self.lista_temp.clear() 
            self.a_gravar = True #flag ativa, começou a gravar (isto vai influenciar quando começar a ter o sistema do input() e _read_loop)
        else: 
            #Ramo de parar de gravar
            self.a_gravar = False 
            #Futuramente ver aqui do guardar CSV semelhante ao do GravadorZed
            self._guardar_csv_tentativa()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    frame_teste = tk.Frame(root)
    frame_teste.pack(fill=tk.BOTH, expand=True)
    app = LidarSub(root, frame_teste)

    root.after(2000, app.alternar_gravacao)  # começar a gravar aos 2s
    root.after(6000, app.alternar_gravacao)  # parar de gravar aos 6s

    root.mainloop()