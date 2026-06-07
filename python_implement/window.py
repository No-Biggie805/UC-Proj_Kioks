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

        #Memória do gráfico
        self.y_data = []
        self.max_pontos = 50

        # Criamos os elementos visuais
        self.fig = Figure(figsize=(6,4), dpi=100) #concertado o argumento figsize, e o dpi=100 para nao ficar pixalizado
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [], 'r-', linewidth=2) #!!, ax.plot consegue desenhar varias linhas ao mesmo tempo, para isso por agora se poe uma virgula no depois da variavel, o que faz com a lista entregue diretamente à variável

        self.ax.set_ylim(0, 500)
        self.ax.set_xlim(0, self.max_pontos)
        self.ax.set_title("Estabilidade do sinal LiDAR", fontsize=14)
        self.ax.set_ylabel("Distancia (cm)")
        
        #carregar os elemntos do StopWatch:
        #Primeiro carrega-se os elementos de topo 
        self.zona_topo = tk.Frame(self.root)
        self.zona_topo.pack(side=tk.TOP)

        #Carregar o StopWatch
        self.meu_relogio = StopWatch(self.zona_topo)
        self.meu_relogio.pack()

        botao_iniciar = tk.Button(self.root, text="Comecar corrida", command=self.meu_relogio.Start)
        botao_iniciar.pack()

        botao_parar = tk.Button(self.root, text="Parar", command=self.meu_relogio.Stop)
        botao_parar.pack()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
       
        # Agendamos a primeira atualização
        self.update_gui()

    def update_gui(self):
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
        self.canvas.draw()
        
        #6. O segredo: Agendar a próxima atualização para daqui a 50ms
        self.root.after(50, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    app = App(root)
    root.mainloop()