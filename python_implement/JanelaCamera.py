import tkinter as tk
from PIL import Image, ImageTk

class JanelaCamera:
    def __init__(self, root, zed_sub):
        self.root = root
        self.zed_sub = zed_sub

        self.label_imagem = tk.Label(self.root)
        self.label_imagem.pack()

        self._atualizar()
    
    def _atualizar(self):
        frame = self.zed_sub.get_ultimo_frame()
        if frame is not None:
            # ___ 1: de BGRA (4 canais) para RGB (3 canais, ordem R, G, B)
            frame_rgb = frame[:,:,[2,1,0]] #Passar de 4 canais para 3 canais; posição 2-> 255(o R), posição 1-> 0(o G), posição 0->0(o B)
            # ___ 2: array numpy -> Image.fromarray(...) -> ImageTk.PhotoImage(...)
            #2.1: numpy -> PIL
            Pil_obj = Image.fromarray(frame_rgb)
            #2.1.1: Redimensionamento do PIL
            Pil_rez = Pil_obj.resize(size=(640,360), resample=Image.Resampling.BOX)
            #2.2: PIL -> Tk
            Tk_obj = ImageTk.PhotoImage(Pil_rez)
            # ___ 3: self.label_imagem.configure(image=...)
            self.label_imagem.configure(image=Tk_obj)
            #        Pergunta-te: a PhotoImage pode existir só como variável local?
            # guardar o objeto tk numa referência para reter a imagem?
            self.tk_ref = Tk_obj
            #Testagem na fase 1b.3, porque precisa de um Tk com mainloop e do ZedSub real.

        self.root.after(33, self._atualizar)