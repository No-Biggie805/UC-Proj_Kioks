# import tkinker as tk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure

# class RealTimeApp:
#     def __init__(self, root, data_engine):
#         self.root = root
#         self.engine = data_engine
#         self.running = False
        
#         # Criação do gráfico (usamos self. para que o plot seja acessível)
#         self.fig = Figure(figsize=(6,4), dpi=100)
#         self.ax = self.fig.add_subplot(111)
#         self.line, = self.ax.plot([], [], 'r-')
#         self.ax.set_ylim(0, 100)
        
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
#         self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
#         # Botões
#         tk.Button(root, text="Start", command=self.start_plot).pack(side=tk.LEFT)
#         tk.Button(root, text="Stop", command=self.stop_plot).pack(side=tk.LEFT)

#     def start_plot(self):
#         self.running = True
#         self.update_plot()

#     def stop_plot(self):
#         self.running = False

#     def update_plot(self):
#         if self.running:
#             x, y = self.engine.fetch_new_data()
#             self.line.set_data(range(len(y)), y)
#             self.ax.set_xlim(0, len(y))
#             self.canvas.draw()
#             self.root.after(200, self.update_plot)

#1 - Mudar a gui para com que faca um plot

#Edição 1: Problemas conspiram ser o facto de dar erro na variável y que antes não existia (penso eu no código do motor), isto porque o gráfico de linha precisa de memória. Histórico de dados necessário.
#Outro problema no código feito da parte do matplotlib, foi uma virgula e o argumento do figsize(concertado)




import tkinter as tk
from TF02_pro import MotorDados
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
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # self.label_titulo = tk.Label(root, text="Distância Atual:", font=("Arial", 20))
        # self.label_titulo.pack(pady=10)

        # self.label_valor = tk.Label(root, text="--- cm", font=("Arial", 50, "bold"), fg="blue")
        # self.label_valor.pack(pady=20)

        # Agendamos a primeira atualização
        self.update_gui()

    def update_gui(self):
        # 1. Vamos buscar o valor ao motor
        dist = self.sensor.get_distancia()

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