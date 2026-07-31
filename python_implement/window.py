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
        self.a_ver_tentativa = False #flag booleano confirma se tentativa foi ou não vista

        #carregar os elemntos do StopWatch:
        #Primeiro carrega-se os elementos de topo 
        self.zona_topo = tk.Frame(self.root, bg="purple")
        self.zona_topo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #Carregar o StopWatch
        self.meu_relogio = StopWatch(self.zona_topo)
        self.meu_relogio.pack()

        botao_iniciar = tk.Button(self.root, text="Comecar corrida", command=self.on_start)
        botao_iniciar.pack()

        botao_parar = tk.Button(self.root, text="Parar", command=self.on_stop)
        botao_parar.pack()

        botao_reset = tk.Button(self.root, text="Reset", command=self.meu_relogio.Reset)
        botao_reset.pack()

        #Criação do frame central 
        self.frame_central = tk.Frame(self.root, bg="green")
        self.frame_central.pack(side=tk.TOP, fill=tk.BOTH, expand=True) ##Criação do frame central 

        #criação do frame para o grafico
        self.frame_grafico = tk.Frame(self.frame_central, bg="#1e1e2e")
        self.frame_grafico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 

        # Criamos os elementos visuais
        self.fig = Figure(figsize=(6,4), dpi=100) #concertado o argumento figsize, e o dpi=100 para nao ficar pixalizado
        self.fig.patch.set_facecolor('#1e1e2e') #fundo fora do gráfico
           
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

        #Memória do gráfico
        self.y_data = []
        self.t_data = [] #lista do tempo
        self.v_data = []
        self.a_data = []

        #Listas paralelas para listar no ver_tentativa:
        self.y_data_completo = []
        self.t_data_completo = [] 
        self.v_data_completo = []
        self.a_data_completo = []

        #criar uma lista com um dicionário por eixo:
        #Explicar elementos do dict:    
            #ax - Isto é a moldura do gráfico, define limites, cor de fundo, labels, ticks. O mesmo é configurado uma vez: em _configurar_eixo e raramente muda depois
            #line - Isto é a linha 2D, os dados desenhados dentro do canvas, esta será sempre atualizada
            #bg - Existe para tirar um snapshot do background, assim não precisando de desenhar tudo sem ser o que precisa
                #o que precisa de ser atualizado, isto acontece antes e depois da janela ter feito um resize 
            #data - lista de dados tirados do sensor e matematicamente calculados 
        self.eixos = [
            {"ax": self.ax_dist, "line": self.line_dist, "bg": None, "data": self.y_data},
            {"ax": self.ax_vel, "line": self.line_vel, "bg": None, "data": self.v_data},
            {"ax": self.ax_acel, "line": self.line_acel, "bg": None, "data": self.a_data},
        ]
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        #Criação do frame para as tentativas
        self.frame_resultados = tk.Frame(self.frame_central, bg="red")
        self.frame_resultados.pack(side=tk.RIGHT, fill=tk.Y) 

        self.labels_tentativas = []
        self.botoes_graficos = []

        #Listar as tentativas
        for i in range(3): 
            label = tk.Label(self.frame_resultados, text=f"Tentativa {i+1}, ---")
            label.pack(pady=(8,0), padx=8, anchor="w")
            self.labels_tentativas.append(label)
        
        #Listar os botões das tentativas
        for i in range(3):
            btn = tk.Button(self.frame_resultados, text=f"Ver grafico {'{'}i+1{'}'}", 
                            command=lambda n=i: self.ver_grafico_tentativa(n), state=tk.NORMAL)
            btn.pack(pady=(2,0), padx=8, anchor="w")
            self.botoes_graficos.append(btn) #registar o que está no widget à classe?
        
        self.botao_guardar = tk.Button(self.frame_resultados, text="Guardar Tentativa", command=self.guardar_tentativa)
        self.botao_guardar.pack(pady=16, padx=8, fill=tk.X)

        self.voltar_live = tk.Button(self.frame_resultados, text="Voltar ao live", command=self.voltar_ao_live)
        self.voltar_live.pack(pady=16, padx=8, fill=tk.X)

        # Agendamos a primeira atualização
        self.update_gui()

        #Após a janela ser redimensionada, regenerar o background, senão fica desatualizado
        self.canvas.mpl_connect('resize_event', self._on_resize)
        self.root.after(100, self._init_blit)

    def update_gui(self):
        if self.a_ver_tentativa: #flag que previne o resto de correr se for verdadeiro 
            self.root.after(100, self.update_gui)
            print("ver tentativa deu verdadeiro")
            return
        # print("ver tentativa deu falso")

        #check, se o atributo bg não existir para prevenir a falha.
        #Agora não necessita verificar se atributo existe ou não, pois foi criado no __init__ pelo dict, mas apenas 
        if any(eixo["bg"] is None for eixo in self.eixos):
            self.root.after(50, self.update_gui)
            return

        #Nota o blit também vai ter de lidar com três <line> objects e capturar o <bg> de cada eixo separadamente!
        # 1. Vamos buscar o valor ao motor
        dist = self.sensor.get_distancia() #buscar do motor os dados da funcao get_distancia()
        agora = time.time()

        #2. Guardar o valor na nossa lista da distancia
        self._guardar_com_limite(self.y_data, dist)
        self._guardar_com_limite_completo(self.y_data_completo, dist)
        #guardar na lista do tempo
        self._guardar_com_limite(self.t_data, agora)
        self._guardar_com_limite_completo(self.t_data_completo, agora)

        N = 5
        if len(self.y_data) >= N: #Verificar se tem valores no tempo e terem passados mais de 5 passos, senão ignora
                #Calcular o delta_distancia e a velocidade:
                self.delta_dist = self.y_data[-1] - self.y_data[-N] #Aqui lê-se ao contrário da perpectiva da lista, -2 é o vi, o -1 o vf
                self.delta_t = self.t_data[-1] - self.t_data[-N]
                vel = self.delta_dist / self.delta_t 
                self._guardar_com_limite(self.v_data, vel)
                self._guardar_com_limite_completo(self.v_data_completo, vel)
        else:
                self.v_data.append(0) #caso especial: primeira leitura
                self.v_data_completo.append(0) #caso especial: primeira leitura

        if len(self.v_data) >= N:

                self.delta_t = self.t_data[-1] - self.t_data[-N]
                #calcular a variação da velocidade
                self.delta_v = self.v_data[-1] - self.v_data[-N]
                #Agora trabalhar na aceleração:
                acel = self.delta_v / self.delta_t
                self._guardar_com_limite(self.a_data, acel)
                self._guardar_com_limite_completo(self.a_data_completo, acel)
        else:
                self.a_data.append(0)
                self.a_data_completo.append(0)

        #IMPLEMENTAÇÃO SEM BOILER-PLATE:
        for eixo in self.eixos:
            eixo["line"].set_data(range(len(eixo["data"])),eixo["data"])
            self.canvas.restore_region(eixo["bg"])
            eixo["ax"].draw_artist(eixo["line"])
            self.canvas.blit(eixo["ax"].bbox)

        self.canvas.flush_events() #processar eventos pendentes

        self.root.after(100, self.update_gui)
    
    def _init_blit(self):
        for eixo in self.eixos:
            eixo["bg"] = self.canvas.copy_from_bbox(eixo["ax"].bbox) #criar snapshot do background (continuamente)

    def _on_resize(self, event):
        for eixo in self.eixos:
            eixo["bg"] = None #Limpar a informação do background
        self.root.after(100, self._reinit_blit)

    def _reinit_blit(self): #para o reinit_blit vou já me adiantar com o update:
        for eixo in self.eixos:
            eixo["line"].set_data([],[]) #Limpar a lista temporariamente
        self.canvas.draw()
        for eixo in self.eixos:
            eixo["bg"] = self.canvas.copy_from_bbox(eixo["ax"].bbox)
        for eixo in self.eixos:
            eixo["line"].set_data(range(len(eixo["data"])),eixo["data"])
        #Resultado final, fica sem linhas que se transponham, que era o problema inicial quando se fez o blit.
    def on_start(self):
        #limpar a lista logo depois de começar
        self.y_data_completo.clear()
        self.v_data_completo.clear()
        self.a_data_completo.clear()
        self.t_data_completo.clear()

        self.meu_relogio.Start() 

    def on_stop(self):
        self.meu_relogio.Stop()
        self.guardar_tentativa()

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

    def _guardar_com_limite_completo(self, lista, valor):
        lista.append(valor)

    def guardar_tentativa(self):
        if len(self.historico_tentativas) <= 3:
            nova_tentativa = {
                #"y": # ___ (copia self.y_data)
                "y": self.y_data_completo.copy(),
                "v": self.v_data_completo.copy(),
                "a": self.a_data_completo.copy(),
                "t": self.t_data_completo.copy(),
            }
            # ___ (adicionar nova_tentativa a self.historico_tentativas)
            self.historico_tentativas.append(nova_tentativa)
            self.numero_tentativa += 1

            #Fazer o clear depois do append ser feito
            self.y_data_completo.clear()
            self.v_data_completo.clear()
            self.a_data_completo.clear()
            self.t_data_completo.clear()

            print(f"Total de tentativas: {len(self.historico_tentativas)}")

            for idx, t in enumerate(self.historico_tentativas):
                print(f"Tentativa {idx+1}: y={len(t['y'])} pontos, v={len(t['v'])} pontos")

            print(self.historico_tentativas[0]["y"] is self.y_data) #Devolver falso, pois o que está no historico não faz parte da lista
        else:
            print("Passou do limite do numero de tentativas que atualmente pode guardar")
    
    def ver_grafico_tentativa(self, n):
        #1. Validar n; Se não for válido, avisa e sai já
        if(n > len(self.historico_tentativas)):
            print("n inválido, a retornar..")
            return
        #2. Ativar a flag que pausa o update_gui() ao vivo
        self.a_ver_tentativa = True

        #3. Buscar a "caixa" certa do historico
        tentativa = self.historico_tentativas[n]

        # Adicionar uma lista tempos que vai servir para ajustar os eixos para tempo em vez de pontos fixos
        tempos = [x - tentativa["t"][0] for x in tentativa["t"]]
        
        #4. Escrever os dados guardados nas line de cada eixo 
        self.line_dist.set_data(tempos, tentativa["y"])
        self.line_vel.set_data(tempos, tentativa["v"])
        self.line_acel.set_data(tempos, tentativa["a"])
        
        #5. Ajustar os limites do eixo x consoatne o tamanho real da tentativa
        self.ax_dist.set_xlim(0, tempos[-1])
        self.ax_vel.set_xlim(0, tempos[-1])
        self.ax_acel.set_xlim(0, tempos[-1])

        #6 Redenhar — decide se faz sentido aqui, dado que não é o loop de 100ms
        self.canvas.draw()

        #7. Atualizar o botão "Voltar ao live:"
        self.voltar_live.config(state=tk.NORMAL)
    
    def voltar_ao_live(self):
        #1. Desligar a flag
        self.a_ver_tentativa = False

        #2. Repor o xlim "de sempre" em cada eixo
        self.ax_dist.set_xlim(0, self.max_pontos)
        self.ax_vel.set_xlim(0, self.max_pontos)
        self.ax_acel.set_xlim(0, self.max_pontos)

        #3. Invalidar o bg antigo e pedir para ser reconstruído
        #   (pensa em qual função já faz isto — não precisas de reescrever a lógica)
        self.root.after(100, self._reinit_blit)

        #4. Atualizar o botão (inverso do que fizeste no passo 7 anterior)
        self.voltar_live.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    app = App(root)
    root.mainloop()