from tkinter import *
from tkinter import ttk
import time

#Define the StopWatch class: Exender a class Frame, será usado para criar as funcionalidades do stopwatch
class StopWatch(Frame):
    #Criar os componentes da GUI
    def __init__(self, parent=None, **kw):
        Frame.__init__(self, parent, kw)
        self._start = 0.0
        self._elapsedtime = 0.0
        self._running = 0
        self.timestr = StringVar()

        self.makeWidgets()

    def makeWidgets(self):
        l = ttk.Label(self, textvariable=self.timestr)
        self._setTime(self._elapsedtime)
        l.pack(fill=X, expand=NO, pady=2, padx=2)

    #Fazer o update do tempo que passou 
    def _update(self):
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime)
        self._timer = self.after(50, self._update)
    
    def _setTime(self, elap):
        minutes = int(elap/60)
        hours = int(minutes/60)
        seconds = int(elap - minutes * 60.0)
        hseconds = int((elap - minutes * 60.0 - seconds) * 100)
        self.timestr.set('%02d:%02d:%02d:%02d' % (hours, minutes, seconds, hseconds)) 
    
    #implementar um start 
    def Start(self):
        if not self._running:
            self._start = time.time() - self._elapsedtime
            self._update()
            self._running = 1
    
    #implementar o stop
    def Stop(self):
        if self._running:
            self.after_cancel(self._timer)
            self._elapsedtime = time.time() - self._start
            self._setTime(self._elapsedtime)
            self._running = 0
    
    #criar um reset
    def Reset(self):
        self._start = time.time()
        self._elapsedtime = 0.0
        self._setTime(self._elapsedtime)

    #crear a função, aqui chamamos todas as funções e tem o paper de criar, manter a janela aberta
# def main():
#     root = Tk()
#     sw = StopWatch(root)
#     sw.pack(side=TOP)

#     # Button(root, text='Start', command=sw.Start).pack(side=LEFT)
#     # Button(root, text='Stop', command=sw.Stop).pack(side=LEFT)
#     # Button(root, text='Reset', command=sw.Reset).pack(side=LEFT)
#     # Button(root, text='Quit', command=sw.quit).pack(side=LEFT)

#     root.mainloop()
# if __name__ == "__main__":
#     main()
