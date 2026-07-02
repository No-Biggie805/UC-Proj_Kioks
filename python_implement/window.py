#1 - Mudar a gui para com que faca um plot
#Edição 1: Problemas conspiram ser o facto de dar erro na variável y que antes não existia (penso eu no código do motor), isto porque o gráfico de linha precisa de memória. Histórico de dados necessário.
#Outro problema no código feito da parte do matplotlib, foi uma virgula e o argumento do figsize(concertado)

#2 - Adicionar botões Start/Stop

import tkinter as tk
import time
from TF02_pro import MotorDados
from StopWatch import StopWatch


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor LiDAR TF02-Pro")

        # Iniciamos o motor
        self.sensor = MotorDados()
        
        #adicionar lista do historico e inicializar a variavel numero
        self.historico_tentativas = []
        self.numero_tentativa = 1

        #carregar os elemntos do StopWatch:
        #Primeiro carrega-se os elementos de topo 
        self.zona_topo = tk.Frame(self.root, bg="purple")
        self.zona_topo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #Carregar o StopWatch
        self.meu_relogio = StopWatch(self.zona_topo)
        self.meu_relogio.pack()

        botao_iniciar = tk.Button(self.root, text="Comecar corrida", command=self.meu_relogio.Start)
        botao_iniciar.pack()

        botao_parar = tk.Button(self.root, text="Parar", command=self.meu_relogio.Stop)
        botao_parar.pack()

        #Criação do frame central 
        self.frame_central = tk.Frame(self.root, bg="green")
        self.frame_central.pack(side=tk.TOP, fill=tk.BOTH, expand=True) ##Criação do frame central 

        #criação do frame para o grafico
        self.frame_grafico = tk.Frame(self.frame_central, bg="#1e1e2e")
        self.frame_grafico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 

        # Criamos os elementos visuais
        self.fig = Figure(figsize=(6,4), dpi=100) #concertado o argumento figsize, e o dpi=100 para nao ficar pixalizado
        self.fig.patch.set_facecolor('#1e1e2e') #fundo fora do gráfico
        # self.ax = self.fig.add_subplot(111)
        # self.line, = self.ax.plot([], [], 'r-', linewidth=2) #!!, ax.plot consegue desenhar varias linhas ao mesmo tempo, para isso por agora se poe uma virgula no depois da variavel, o que faz com a lista entregue diretamente à variável
        
        # DEPOIS (esqueleto):
        self.max_pontos = 50

        self.ax_dist = self.fig.add_subplot(311)   # ___ linha: cria a tua line de distância aqui
        self.line_dist, = self.ax_dist.plot([], [], 'r-', linewidth=2)
        self._configurar_eixo(self.ax_dist, "Distancia (cm)", (0, 500))
        self.ax_vel  = self.fig.add_subplot(312)   # ___ linha: cria a tua line de velocidade aqui
        self.line_vel, = self.ax_vel.plot([], [], 'g-', linewidth=2)
        self._configurar_eixo(self.ax_vel, "Velocidade (cm/s)", (-150, 150))
        self.ax_acel = self.fig.add_subplot(313)   # ___ linha: cria a tua line de aceleração aqui
        self.line_acel, = self.ax_acel.plot([], [], 'b-', linewidth=2)
        self._configurar_eixo(self.ax_acel, "Aceleração (cm/s²)", (-300, 300))

        # Pergunta para ti: cada self.ax_X precisa dos mesmos set_facecolor / set_ylim /
        # tick_params / set_ylabel que já tinhas no self.ax original?
        # Sugestão: experimenta criar uma função auxiliar tipo self._configurar_eixo(ax, ylabel, ylim)
        # para não repetires o mesmo bloco 3 vezes.
                
        #Memória do gráfico
        self.y_data = []
        self.t_data = [] #lista do tempo
        self.v_data = []
        self.a_data = []
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        #Criação do frame para as tentativas
        self.frame_resultados = tk.Frame(self.frame_central, bg="red")
        self.frame_resultados.pack(side=tk.RIGHT, fill=tk.Y) 

        self.labels_tentativas = []
        self.botoes_graficos = []
        for i in range(3): 
            label = tk.Label(self.frame_resultados, text=f"Tentativa {i+1}, ---")
            label.pack(pady=(8,0), padx=8, anchor="w")
            self.labels_tentativas.append(label)
        
        for i in range(3):
            btn = tk.Button(self.frame_resultados, text=f"Ver grafico {'{'}i+1{'}'}", 
                            command=lambda n=i: self.ver_grafico_tentativa(n), state=tk.DISABLED)
            btn.pack(pady=(2,0), padx=8, anchor="w")
            self.botoes_graficos.append(btn) #registar o que está no widget à classe?
        
        self.botao_guardar = tk.Button(self.frame_resultados, text="Guardar Tentativa", state=tk.DISABLED)
        self.botao_guardar.pack(pady=16, padx=8, fill=tk.X)
        #canvas.draw() removido pois o mesmo aparenta conseguir fazer um draw automático e tem tempo para fazer o blit sem problemas

        # Agendamos a primeira atualização
        self.update_gui()

        #Após a janela ser redimensionada, regenerar o background, senão fica desatualizado
        self.canvas.mpl_connect('resize_event', self._on_resize)
        self.root.after(100, self._init_blit)

    def update_gui(self):

        #check, se o atributo bg não existir para prevenir a falha.
        if not hasattr(self, 'bg_dist') or self.bg_dist is None or not hasattr(self, 'bg_vel') or self.bg_vel is None or not hasattr(self, 'bg_acel') or self.bg_acel is None:
            self.root.after(50, self.update_gui)
            return
        #Nota o blit também vai ter de lidar com três <line> objects e capturar o <bg> de cada eixo separadamente!
        # 1. Vamos buscar o valor ao motor
        dist = self.sensor.get_distancia() #buscar do motor os dados da funcao get_distancia()
        agora = time.time()

        #2. Guardar o valor na nossa lista da distancia
        self._guardar_com_limite(self.y_data, dist)
        #guardar na lista do tempo
        self._guardar_com_limite(self.t_data, agora)

        N = 5
        if len(self.y_data) >= N: #Verificar se tem valores no tempo e terem passados mais de 5 passos, senão ignora
                #Calcular o delta_distancia e a velocidade:
                self.delta_dist = self.y_data[-1] - self.y_data[-N] #Aqui lê-se ao contrário da perpectiva da lista, -2 é o vi, o -1 o vf
                self.delta_t = self.t_data[-1] - self.t_data[-N]
                vel = self.delta_dist / self.delta_t 
                self._guardar_com_limite(self.v_data, vel)
        else:
                self.v_data.append(0) #caso especial: primeira leitura

        if len(self.v_data) >= N:

                self.delta_t = self.t_data[-1] - self.t_data[-N]
                #calcular a variação da velocidade
                self.delta_v = self.v_data[-1] - self.v_data[-N]
                #Agora trabalhar na aceleração:
                acel = self.delta_v / self.delta_t
                self._guardar_com_limite(self.a_data, acel)
        else:
                self.a_data.append(0)

        # blit: lembra-te que agora tens 3 eixos. Vais precisar de restore_region
        # e draw_artist para CADA eixo, ou um bg que cubra a figura toda?
        # Isto é decisão tua — pensa no que já fizeste em _init_blit.
        self.line_dist.set_data(range(len(self.y_data)), self.y_data)
        self.line_vel.set_data(range(len(self.v_data)), self.v_data)
        self.line_acel.set_data(range(len(self.a_data)), self.a_data)

        #Em vez de canvas.draw, mesmo no __init__
        self.canvas.restore_region(self.bg_dist) #restaurar o fundo
        self.canvas.restore_region(self.bg_vel) #restaurar o fundo
        self.canvas.restore_region(self.bg_acel) #restaurar o fundo

        self.ax_dist.draw_artist(self.line_dist) #Desenhar só a linha
        self.ax_vel.draw_artist(self.line_vel) #Desenhar só a linha
        self.ax_acel.draw_artist(self.line_acel) #Desenhar só a linha

        self.canvas.blit(self.ax_dist.bbox) #enviar para o ecrã
        self.canvas.blit(self.ax_vel.bbox) #enviar para o ecrã
        self.canvas.blit(self.ax_acel.bbox) #enviar para o ecrã

        self.canvas.flush_events() #processar eventos pendentes

        self.root.after(100, self.update_gui)
    
    def _init_blit(self):
        self.bg_dist = self.canvas.copy_from_bbox(self.ax_dist.bbox)
        self.bg_vel = self.canvas.copy_from_bbox(self.ax_vel.bbox)
        self.bg_acel = self.canvas.copy_from_bbox(self.ax_acel.bbox) 

    def _on_resize(self, event):
        self.bg_dist = None 
        self.bg_vel = None 
        self.bg_acel = None 
        self.root.after(100, self._reinit_blit)

    def _reinit_blit(self): #para o reinit_blit vou já me adiantar com o update:
        self.line_dist.set_data([], []) #limpa a linha temporariamente
        self.line_vel.set_data([], []) 
        self.line_acel.set_data([], []) 

        self.canvas.draw()

        self.bg_dist = self.canvas.copy_from_bbox(self.ax_dist.bbox)
        self.bg_vel = self.canvas.copy_from_bbox(self.ax_vel.bbox)
        self.bg_acel = self.canvas.copy_from_bbox(self.ax_acel.bbox)

        #restaura os dados reais da linha (mesmo padrão que foi feito no update_gui)
        self.line_dist.set_data(range(len(self.y_data)), self.y_data) 
        self.line_vel.set_data(range(len(self.v_data)), self.v_data) 
        self.line_acel.set_data(range(len(self.a_data)), self.a_data) 
    # def on_stop(self):

    def _configurar_eixo(self, ax, ylabel, ylim):
        ax.set_facecolor('#2e2e3e') #fundo dentro dos eixos
        ax.set_ylim(*ylim)
        ax.set_xlim(0, self.max_pontos)
        ax.tick_params(colors='white') #cor dos números dos eixos
        ax.set_ylabel(ylabel)
        ax.yaxis.label.set_color('white') #cor do label no eixo dos y

    def _guardar_com_limite(self, lista, valor):
        lista.append(valor)
        if len(lista) > self.max_pontos:
            lista.pop(0)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    app = App(root)
    root.mainloop()