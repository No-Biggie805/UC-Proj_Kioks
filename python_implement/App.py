import tkinter as tk
from LidarSub import LidarSub
from ZedSub import ZedSub

"""
Para correr o programa: 
    QT_QPA_PLATFORM=xcb __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia python3 App.py
"""
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor LiDAR + ZED")
        self.a_gravar = False

        #1. Para o ZedSub o try:
        try:
            self.zed = ZedSub()
        except ConnectionError as e:
            print(f"Não foi possível inicializar: {e}")
            return
        
        #2. Frame que o LidarSub recebe como frame_pai
        self.frame_pai = tk.Frame(self.root, bg="green")
        self.frame_pai.pack(side=tk.TOP, fill=tk.BOTH, expand=True) ##Criação do frame central 

        #3. LidarSub
        self.lidar = LidarSub(root, frame_teste)
        
        #4. Botão único, (guardar em self.botao para poder mudar o texto depois?)
        self.botao = tk.Button(self.root, text="Começar", command=self._alternar)
        self.botao.pack()

        #5. Fecho da janela
        self.root.protocol("WM_DELETE_WINDOW", self._fechar)

    def _alternar(self):
        # ___ (chama alternar_gravacao() nas duas subs, uma a seguir à outra)
        # ___ (troca o texto do botão)
        self.zed.alternar_gravacao()
        self.lidar.alternar_gravacao()

        if (self.a_gravar is not True): 
            #Estado de condição em que o programa corre
            self.a_gravar = True
            self.botao.config(text="Parar")
        else:
            #Estado de condição que o programa para
            self.a_gravar = False
            self.botao.config(text="Começar")

    def _fechar(self):
        # ___
        #o .fechar do ZedSub vai já fechar as threads do zed e os recursos (zed.close), da camera
        self.zed.fechar()
        #Ver agora para o lidar, threads e recursos
        self.lidar.sensor.fechar()
        #Destruir a janela
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    frame_teste = tk.Frame(root)
    frame_teste.pack(fill=tk.BOTH, expand=True)
    app = App(root)

    # root.after(2000, app.alternar_gravacao)  # começar a gravar aos 2s
    # root.after(6000, app.alternar_gravacao)  # parar de gravar aos 6s

    root.mainloop()