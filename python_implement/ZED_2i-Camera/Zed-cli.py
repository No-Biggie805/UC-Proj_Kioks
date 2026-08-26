"""
Bloco A — Teste de abertura da câmara ZED 2i

Objetivo único deste script: confirmar que conseguimos abrir a câmara
com os parâmetros escolhidos, e fechar de forma limpa. Não faz grab(),
não lê profundidade ainda — isso é o Bloco B.

Corre isto DENTRO do Distrobox Ubuntu 26.04 (onde confirmaste o
`import pyzed.sl` com sucesso, SDK 5.4.1), com as mesmas variáveis de
ambiente que usaste para o ZED_Explorer, caso o SDK precise de abrir
qualquer contexto gráfico internamente:

    QT_QPA_PLATFORM=xcb __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia python3 Zed-cli.py
"""
import threading
import time
import math
import csv
import pyzed.sl as sl

"""
ALTERAÇÕES DO BLOCO C -- A partir do bloco C o código irá tomar um rumo diferente. Aqui irá ser aplicado o uso de
classes que torna o nosso cli OOP. 
Para tal temos isto então estruturado da seguinte forma: 
    -__init__: isto será onde tudo se inicializa.
    -_read_loop: aqui será configurado o loop do grab, também onde grava os dados
    -_guardar_csv_tentativa: guardar as tentativas no ficheiro CSV
    -alternar_gravacao: toggle ON-OFF do programa a partir do ENTER
    -fechar: função para exit do programa
"""
class GravadorZed:

    def __init__(self, camera_resolution=sl.RESOLUTION.HD720, fps=60):
        self.zed = sl.Camera() 
        self.lock = threading.Lock()

        # 2. Configurar parâmetros de abertura
        self.init_params = sl.InitParameters()
        self.init_params.camera_resolution = sl.RESOLUTION.HD720   # confirmaste 720@60fps no ZED_Explorer
        self.init_params.camera_fps = 60
        self.init_params.coordinate_units = sl.UNIT.CENTIMETER      # para bater certo com o TF02_pro.py (guarda em cm)
        self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL_LIGHT     # modo mais leve/rápido; NEURAL fica como opção futura se precisares de mais precisão

        # 3. Abrir a câmara e validar
        # Nota: a comparação correta é ">" e não "!=" — no enum ERROR_CODE,
        # valores abaixo de SUCCESS são warnings toleráveis, não falhas.
        # É o padrão usado nos exemplos oficiais da Stereolabs.
        self.status = self.zed.open(self.init_params)
        if self.status > sl.ERROR_CODE.SUCCESS:
            print(f"Erro ao abrir a câmara: {repr(self.status)}")
            self.zed.close()
            return
        
        print("Câmara ZED aberta com sucesso!")
        print(f"Versão do SDK: {self.zed.get_sdk_version()}")

        info = self.zed.get_camera_information()
        print(f"Resolução configurada: {info.camera_configuration.resolution.width}x{info.camera_configuration.resolution.height}")
        print(f"FPS configurado: {info.camera_configuration.fps}")

        self.running = True
        self.a_gravar = False
        self.lista_temp = []

        self.numero_tentativa = 1

        # Tarefa de fundo para não bloquear o input() da thread principal
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
    
    def _read_loop(self):
        #Definir os paremetros que vao ler a profundidade
        depth = sl.Mat()
        runtime_parameters = sl.RuntimeParameters()

        while self.running:
            if self.a_gravar: #Se for verdadeiro
                #1 -> grab() -> se sucesso
                # 2 - grab, busca valores para guardar no mapa e assim..
                grab_status = self.zed.grab(runtime_parameters)
                if (grab_status == sl.ERROR_CODE.SUCCESS):
                    # 2.1 - buscar medida de profundidade
                    timestamp = time.time() #Ordem de inicializacao assim que estiver a recolher a profundidade
                    self.zed.retrieve_measure(depth, sl.MEASURE.DEPTH) # Retrieve depth Mat. Depth is aligned on the left image
                    # 2.2 - calcular x e y da profundidade
                    x = round(depth.get_width()/2)
                    y = round(depth.get_height()/2)
                    # 3 - print a "cru" dos valores
                    # print(depth.get_value(x,y)) #Devolve o (status (eg:SUCCESS), valor da profundidade aka:distancia)
                    #TOMAR NOTA QUE O VALOR PODE DEVOLVER <nan> ou <inf> dependendo da superficie em que a camera esteje a apontar..
                    get_status, valor = depth.get_value(x,y) #valores descompactados

                    #Se get_status não suceder
                    # print(repr(get_status), end='\r')
                    if get_status > sl.ERROR_CODE.SUCCESS:
                        print(f"Leitura inválida no pixel central: {repr(get_status)}")
                    #Se valor for nan ou inf
                    elif math.isnan(valor) or math.isinf(valor):
                        print(f"Valor é infinito ou nulo")
                    #Se valor for um numero normal, mas irrelevante para T-Test [PROFUNDIDADE_MIN, PROFUNDIDADE_MAX]
                    elif valor < 0 or valor > 1000: #valores brutos expressos em cm 
                        print(f"válido tecnicamente, mas fora do que interessa ao T-Test")
                    #Se valor for válido e normal..
                    else: 
                        with self.lock: #Travar o processo do append durante um bocado
                            # 3 - print a "cru" dos valores se for um caso normal
                            self.lista_temp.append({"t":timestamp, "y":valor})
                        print(repr(get_status), valor, end='\r')#Devolve o (status e valor da distancia em cru)
                        #Esta impressão acontece de forma a que o valor torne-se fixo no terminal 
                        pass
                else:
                    print(f"Erro no grab(): {repr(grab_status)}")
            else:
                time.sleep(0.01)

    def _guardar_csv_tentativa(self):
        # tentativa = self.lista_temp
        with self.lock:
            #Abrir o ficheiro ainda fora do loop, duhh
            tempos = [i["t"] - self.lista_temp[0]["t"] for i in self.lista_temp] #para copiar todos os valores da lista
            #Resolver typeError e segfault, e porquê?
            # i["t"]: Por ser uma lista de dicionario, não um dicionário de **listas**
            # in self.lista_tempos sem ["t"], porque itera o i no dicionario
            # self.lista_temp[0]["t"], porque a lista não tem chaves e tava a aceder numa chave

            with open("tentativa.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "distancia"]) 
                for i, leitura in enumerate(self.lista_temp):
                    # tempos = [tempos[i] - self.lista_temp[0]["t"]]
                    writer.writerow([f"{tempos[i]:.2f}", f"{leitura["y"]:.2f}"])
            #Limpar a lista
            self.lista_temp.clear()
            # self.numero_tentativa += 1
        pass

    def alternar_gravacao(self):
        """Chamado pela thread principal a cada Enter. Faz o toggle."""
        if not self.a_gravar:
            self.a_gravar = True
            print("A gravar... primir Enter para parar.")
        else:
            self.a_gravar = False
            print("Thread de gravação Parado, a iniciar gravação para ficheiro")
            #chamar o _guardar_csv_tentativa? eu acho que sim pois gravação para e passa a escrita
            self._guardar_csv_tentativa()
    
    def fechar(self):
        self.running = False
        #ainda falta ajustar o guardar para quando sai do programa
        self.zed.close()
        # 4. Fechar de forma limpa
        print("Câmara fechada com segurança.")
        pass

def main():
    
    gravador = GravadorZed()

    try:
        while True:
            print("Premir enter para Começar/Parar") 
            input()
            gravador.alternar_gravacao()
    except KeyboardInterrupt:
        print("\nInterrompido pelo utilizador.")
    finally:
        gravador.fechar()


if __name__ == "__main__":
    main()
