#1 - Mudar a gui para com que faca um plot
#Edição 1: Problemas conspiram ser o facto de dar erro na variável y que antes não existia (penso eu no código do motor), isto porque o gráfico de linha precisa de memória. Histórico de dados necessário.
#Outro problema no código feito da parte do matplotlib, foi uma virgula e o argumento do figsize(concertado)

#2 - Adicionar botões Start/Stop

import tkinter as tk
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
       
        #Memória do gráfico
        self.y_data = []
        self.max_pontos = 50

        # Criamos os elementos visuais
        self.fig = Figure(figsize=(6,4), dpi=100) #concertado o argumento figsize, e o dpi=100 para nao ficar pixalizado
        self.fig.patch.set_facecolor('#1e1e2e') #fundo fora do gráfico
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [], 'r-', linewidth=2) #!!, ax.plot consegue desenhar varias linhas ao mesmo tempo, para isso por agora se poe uma virgula no depois da variavel, o que faz com a lista entregue diretamente à variável

        self.ax.set_facecolor('#2e2e3e') #fundo dentro dos eixos
        self.ax.set_ylim(0, 500)
        self.ax.set_xlim(0, self.max_pontos)
        self.ax.tick_params(colors='white') #cor dos números dos eixos
        self.ax.set_title("Estabilidade do sinal LiDAR", fontsize=14)
        self.ax.title.set_color('white')
        self.ax.set_ylabel("Distancia (cm)")
        self.ax.yaxis.label.set_color('white') #cor do label no eixo dos y

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        #Criação do frame para as tentativas
        self.frame_resultados = tk.Frame(self.root, bg="red")
        self.frame_resultados.pack(side=tk.LEFT, fill=tk.Y) 
        
        #Devido ao bbox precisar de ser chamado após um draw completo e síncrono, 
        #o draw como era assíncrono foi juntamente passado para o loop tornando-se síncrono o que previne de resultar num background vazio ou incompleto.
        self.canvas.draw_idle()

        # Agendamos a primeira atualização
        self.update_gui()

        #Após a janela ser redimensionada, regenerar o background, senão fica desatualizado
        self.canvas.mpl_connect('resize_event', self._on_resize)
        self.root.after(100, self._init_blit)

    def update_gui(self):

        #check, se o atributo bg não existir para prevenir a falha.
        if not hasattr(self, 'bg') or self.bg is None:
            self.root.after(50, self.update_gui)
            return

        # 1. Vamos buscar o valor ao motor
        dist = self.sensor.get_distancia() #buscar do motor os dados da funcao get_distancia()

        #2. Guardar o valor na nossa lista "memoria"
        self.y_data.append(dist)

        #3. Se a lista ficar maior que 50, apagar o mais antigo. Isto cria um efeito de "scroll" (a linha anda para a esquerda)
        if len(self.y_data) > self.max_pontos:
            self.y_data.pop(0)
        
        #4: injetar os novos dados na linha do grafico. Eixo X = range (0, 1, 2, 3...), Eixo Y = lista de distancias
        self.line.set_data(range(len(self.y_data)), self.y_data)
        
        #5: Resenhamos o ecrã
        # self.canvas.draw_idle()

        #Em vez de canvas.draw
        self.canvas.restore_region(self.bg) #restaurar o fundo
        self.ax.draw_artist(self.line) #Desenhar só a linha
        self.canvas.blit(self.ax.bbox) #enviar para o ecrã
        self.canvas.flush_events() #processar eventos pendentes
       
        #6. O segredo: Agendar a próxima atualização para daqui a 50ms
        self.root.after(100, self.update_gui)
    
    def _init_blit(self):
        self.bg = self.canvas.copy_from_bbox(self.ax.bbox)

    def _on_resize(self, event):
        self.bg = None 
        self.root.after(100, self._reinit_blit)
      
    def _reinit_blit(self):
        self.line.set_data([], []) #limpa a linha temporariamente
        self.canvas.draw_idle()
        self.bg = self.canvas.copy_from_bbox(self.ax.bbox)
        #restaura os dados reais da linha (mesmo padrão que foi feito no update_gui)
        self.line.set_data(range(len(self.y_data)), self.y_data)
    
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    app = App(root)
    root.mainloop()