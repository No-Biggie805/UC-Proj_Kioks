"""
Bloco A — Teste de abertura da câmara ZED 2i

Objetivo único deste script: confirmar que conseguimos abrir a câmara
com os parâmetros escolhidos, e fechar de forma limpa. Não faz grab(),
não lê profundidade ainda — isso é o Bloco B.

Corre isto DENTRO do Distrobox Ubuntu 26.04 (onde confirmaste o
`import pyzed.sl` com sucesso, SDK 5.4.1), com as mesmas variáveis de
ambiente que usaste para o ZED_Explorer, caso o SDK precise de abrir
qualquer contexto gráfico internamente:

    QT_QPA_PLATFORM=xcb __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia python3 Zed-cli_body-tracking.py
"""
import threading
import time
import math
import csv
import pyzed.sl as sl
import numpy as np

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
            # print(f"Erro ao abrir a câmara: {repr(self.status)}")
            self.zed.close()
            raise ConnectionError(f"Erro ao abrir a câmara: {repr(self.status)}") # Este erro vai parecer um erro de prompt, mas é mesmo de conecção
            # return
        
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
        runtime_parameters = sl.RuntimeParameters()

        #1º: positional tracking
        tracking_parameters = sl.PositionalTrackingParameters()
        positional_status = self.zed.enable_positional_tracking(tracking_parameters)
        if positional_status > sl.ERROR_CODE.SUCCESS:
            print("Erro ao abrir parâmetros da posição")
            return

        #2º: Body tracking
        body_params = sl.BodyTrackingParameters()
        #exemplo ->body params: tem a classe BODY_TRACKING_MODEL e membro HUMAN_BODY_FAST
        body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
        body_params.body_format = sl.BODY_FORMAT.BODY_18
        #Atribuir estado apesar de já ser atribuida, para ficar igual aos outros.
        body_params.enable_tracking = True
        body_enable_status = self.zed.enable_body_tracking(body_params)
        if body_enable_status > sl.ERROR_CODE.SUCCESS:
            print("Erro ao abrir body params")
            return

        #Ativar body tracking
        bodies = sl.Bodies()
        body_runtime_parameters = sl.BodyTrackingRuntimeParameters()
        instante_anterior=None #Para FPS

        while self.running:
            if self.a_gravar: #Se for verdadeiro
                #1 -> grab() -> se sucesso
                # 2 - grab, busca valores para guardar no mapa e assim..
                grab_status = self.zed.grab(runtime_parameters)
                if (grab_status == sl.ERROR_CODE.SUCCESS):
                    grab_body_status = self.zed.retrieve_bodies(bodies, body_runtime_parameters)
                    
                    #5) FPS
                    instante_atual = time.perf_counter()
                    fps = None
                    if instante_anterior is not None:
                        fps = 1/(instante_atual - instante_anterior)
                    instante_anterior = instante_atual
                    
                    if grab_body_status == sl.ERROR_CODE.SUCCESS:
                        n_corpos = len(bodies.body_list)
                        if n_corpos > 0:
                            primeiro_corpo = bodies.body_list[0]
                            kp = primeiro_corpo.keypoint
                            # n_keypoints = len(kp)
                            # finitos = np.isfinite(kp)
                            # linha_valida = finitos.all(axis=1)
                            n_validos = np.isfinite(kp).all(axis=1).sum()
                            print("num_corpos:", n_corpos, "id:", primeiro_corpo.id, "keypoints válidos:", n_validos, "FPS:", fps)
                    else:
                        print("Erro em retrieve bodies")                            
                else:
                    print(f"Erro no grab(): {repr(grab_status)}")
            else:
                instante_anterior = None
                time.sleep(0.01)

    def alternar_gravacao(self):
        """Chamado pela thread principal a cada Enter. Faz o toggle."""
        if not self.a_gravar:
            #Aqui o modo de execução da coleção de dados do sensor é acionada
            #Se quisesse limpar as listas da memória seria aqui, o mesmo ao menos acontece no _guardar_csv_tentativa
            self.a_gravar = True
            print("A gravar... primir Enter para parar.")
        else:
            self.a_gravar = False
            print("Thread de gravação à memória parado, a iniciar gravação para ficheiro")
    
    def fechar(self):
        self.running = False
        self.thread.join(timeout=1) #Espera 1s pela thread
        self.zed.disable_positional_tracking()
        self.zed.disable_body_tracking()
        #ainda falta ajustar o guardar para quando sai do programa
        self.zed.close()
        # 4. Fechar de forma limpa
        print("Câmara fechada com segurança.")
        pass

    def _calcular_vel(self, timestamp, valor):
        janela = 0.5

        for i in range(len(self.lista_temp) -1, -1, -1):
            idade = timestamp - self.lista_temp[i]["t"]
            if idade > janela:
                break
        else:
            return 0

        ref_index= i + 1
        if ref_index >= len(self.lista_temp):
            return 0

        #guadar o ponto referência, antes de indice ser "velho"
        # ponto_referencia = i + 1 # ERRADO: É o índice do dicionário não a posição em si, para depois calcular os dados.
        ponto_referencia = self.lista_temp[ref_index] #+1 Para somar à posição no momento em que o índice pára

        #calcular o delta_valor (distancia) e o delta_t entre o *agora* e *ponto_referencia*, e devolver delta_valor/delta_t
        delta_valor = valor - ponto_referencia["y"]
        delta_tempo = timestamp - ponto_referencia["t"]

        if delta_tempo <= 0:
            return 0
        
        return delta_valor/delta_tempo
    
    def _calcular_acel(self, timestamp, velocidade):
        #criar outra vez um espaço na janela
        janela = 0.5
        for i in range(len(self.lista_temp) - 1, -1, -1):
            idade = timestamp - self.lista_temp[i]["t"]
            if idade > janela:
                break
        else:
            return 0

        ref_index= i + 1
        if ref_index >= len(self.lista_temp):
            return 0

        #guadar o ponto referência, antes de indice ser "velho"
        # ponto_referencia = i + 1 # ERRADO: É o índice do dicionário não a posição em si, para depois calcular os dados.
        ponto_referencia = self.lista_temp[ref_index] #+1 Para somar à posição no momento em que o índice pára

        #calcular o delta_valor (distancia) e o delta_t entre o *agora* e *ponto_referencia*, e devolver delta_valor/delta_t
        delta_velocidade = velocidade - ponto_referencia["v"]
        delta_tempo = timestamp - ponto_referencia["t"]
        if delta_tempo <= 0:
            return 0
        
        return delta_velocidade/delta_tempo

def main():
    try:    
        gravador = GravadorZed()
    except ConnectionError as e:
        print(f"Não foi possivel inicializar: {e}")
        return
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
