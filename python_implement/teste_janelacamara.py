import tkinter as tk
from ZedSub import ZedSub
from JanelaCamera import JanelaCamera

def main():
    try:
        zed = ZedSub()
    except ConnectionError as e:
        print(f"Não foi possível inicializar: {e}")
        return
    
    root = tk.Tk()
    janela = JanelaCamera(root, zed)
    #1: Pôr o ZedSub a preencher o ultimo_frame
    # zed.get_ultimo_frame() #Retirado pois não vai fazer nada aqui.
    # zed.alternar_gravacao()
    #2: ao clicar no X da janela, chamar zed.fechar() e root.destroy()
    #   (o App.py já faz isto no _fechar)
    def ao_fechar():
        zed.fechar()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", ao_fechar)
    root.mainloop()

if __name__ == "__main__":
    main()