import time
import serial
from TF02_pro import MotorDados
from LidarSub import LidarSub

def main():
    #1: Criar o ZedSub (o construtor pode levantar ConnectionError: como tratas?)
    try:
        lidarSub = LidarSub()
    except serial.SerialException as e:
        print(f"Não foi possível inicializar: {e}")
        return

    try:
        time.sleep(1) #deixa estabilizar
        lidarSub.alternar_gravacao() # começar a gravar
        time.sleep(8) # mexe a mão à frente da câmera
        lidarSub.alternar_gravacao() #pára e guarda o tentativa_zed.csv

    finally:
        lidarSub.fechar()
if __name__=="__main__":
    main()
