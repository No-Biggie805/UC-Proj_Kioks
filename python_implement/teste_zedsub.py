import time
from ZedSub import ZedSub

def main():
    #1: Criar o ZedSub (o construtor pode levantar ConnectionError: como tratas?)
    try:
        zed = ZedSub()
    except ConnectionError as e:
        print(f"Não foi possível inicializar: {e}")
        return

    try:
        time.sleep(1) #deixa estabilizar
        zed.alternar_gravacao() # começar a gravar
        time.sleep(5) # mexe a mão à frente da câmera
        zed.alternar_gravacao() #pára e guarda o tentativa_zed.csv

    finally:
        zed.fechar()
if __name__=="__main__":
    main()
