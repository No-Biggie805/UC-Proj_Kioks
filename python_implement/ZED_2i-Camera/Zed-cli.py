"""
Bloco A — Teste de abertura da câmara ZED 2i

Objetivo único deste script: confirmar que conseguimos abrir a câmara
com os parâmetros escolhidos, e fechar de forma limpa. Não faz grab(),
não lê profundidade ainda — isso é o Bloco B.

Corre isto DENTRO do Distrobox Ubuntu 26.04 (onde confirmaste o
`import pyzed.sl` com sucesso, SDK 5.4.1), com as mesmas variáveis de
ambiente que usaste para o ZED_Explorer, caso o SDK precise de abrir
qualquer contexto gráfico internamente:

    QT_QPA_PLATFORM=xcb __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia python3 zed_bloco_a_teste_abertura.py
"""

import pyzed.sl as sl


def main():
    # 1. Criar o objeto câmara (handle, ainda não ligado a nada)
    zed = sl.Camera()

    # 2. Configurar parâmetros de abertura
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720   # confirmaste 720@60fps no ZED_Explorer
    init_params.camera_fps = 60
    init_params.coordinate_units = sl.UNIT.CENTIMETER      # para bater certo com o TF02_pro.py (guarda em cm)
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL_LIGHT     # modo mais leve/rápido; NEURAL fica como opção futura se precisares de mais precisão

    # 3. Abrir a câmara e validar
    # Nota: a comparação correta é ">" e não "!=" — no enum ERROR_CODE,
    # valores abaixo de SUCCESS são warnings toleráveis, não falhas.
    # É o padrão usado nos exemplos oficiais da Stereolabs.
    status = zed.open(init_params)
    if status > sl.ERROR_CODE.SUCCESS:
        print(f"Erro ao abrir a câmara: {repr(status)}")
        zed.close()
        return

    print("Câmara ZED aberta com sucesso!")
    print(f"Versão do SDK: {zed.get_sdk_version()}")

    info = zed.get_camera_information()
    print(f"Resolução configurada: {info.camera_configuration.resolution.width}x{info.camera_configuration.resolution.height}")
    print(f"FPS configurado: {info.camera_configuration.fps}")

    # 4. Fechar de forma limpa
    zed.close()
    print("Câmara fechada com segurança.")


if __name__ == "__main__":
    main()
