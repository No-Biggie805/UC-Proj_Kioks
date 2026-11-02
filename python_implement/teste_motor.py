from LidarSub import LidarSub
from ZedSub import ZedSub
import time
import serial

"""
Para correr o programa: 
    QT_QPA_PLATFORM=xcb __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia python3 teste_motor.py
"""

def main():
    #Declarar os objetos fora de try, se 
    zed = None
    lidarSub = None

    try:
        zed = ZedSub()
        lidarSub = LidarSub()
        time.sleep(2) #deixa estabilizar
        lidarSub.alternar_gravacao() # começar a gravar
        zed.alternar_gravacao()
        time.sleep(4) # mexe a mão à frente da câmera
        #Correr coisas..
        ultimo_frame = zed.get_ultimo_frame() #recolher o ultimo frame do zedsub
        print(ultimo_frame.shape, ultimo_frame.dtype)
        
        lidarSub.alternar_gravacao() #pára e guarda o tentativa_zed.csv
        zed.alternar_gravacao()

    except (ConnectionError, serial.SerialException) as e:
        print(f"Não foi possível inicializar: {e}")
        return

    finally:
        if lidarSub is not None:
            try:
                lidarSub.fechar()
            except Exception as e:
                print(f"Erro ao fechar o LiDAR: {e}")
        if zed is not None:
            try:
                zed.fechar()
            except Exception as e:
                print(f"Erro ao fechar Zed: {e}")
if __name__=="__main__":
    main()

