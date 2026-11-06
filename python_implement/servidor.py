"""
Passo 7 — Backend FastAPI/WebSocket sobre o motor (LidarSub + ZedSub).

Correr a partir de python_implement/ (SEM --reload e com 1 só worker, porque
o processo abre a câmara e a porta série uma única vez):

1.  source .venv/bin/activate #python -c "import pyzed.sl, serial, fastapi, uvicorn; print('ok')", verifica as dependências
2.    QT_QPA_PLATFORM=xcb __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia \
        uvicorn servidor:app --port 8000
    Se o de cima falhar:  
        python -m uvicorn servidor:app --port 8000

A página liga-se a:  ws://localhost:8000/ws

Peças:
    - Orquestrador : máquina de estados (parado / a_gravar / terminado) e traduz
                     comandos da página em chamadas aos dois subs.
    - Ligacoes     : conjunto de páginas ligadas + difusão de mensagens.
    - emissor      : tarefa que envia camara/lidar/zed a CADENCIA_HZ.
    - ws_endpoint  : recebe comandos da página.
"""
import asyncio
import base64
import contextlib
import io
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from PIL import Image

from LidarSub import LidarSub
from ZedSub import ZedSub

# --------------------------------------------------------------------------
# Constantes do contrato
# --------------------------------------------------------------------------
CADENCIA_HZ = 30                  # camara, lidar e zed ao vivo (a rever depois de ver o resultado)
FORMATO_IMAGEM = "jpeg"           # "jpeg" ou "webp" -> vai no campo `format` da mensagem camara
QUALIDADE_IMAGEM = 70
TAMANHO_IMAGEM = (640, 360)
DISTANCIA_ALVO_PADRAO_M = 5.0

_FORMATOS_PIL = {"jpeg": "JPEG", "webp": "WEBP"}

# Comandos da página que o motor aceita mas ainda ignora (pausar não é prioridade).
COMANDOS_IGNORADOS = {"pausar", "retomar"}

# "Resultado final" (mockup, 9 campos). Todos entram sempre na mensagem.
#   CALCULADOS pelo motor hoje : tempo_total_s, velocidade_maxima
#   NULOS (por calcular)       : tempo_ida_s, tempo_volta_s, distancia_total_m,
#                                velocidade_media, turnaround_s, passos, execucao_valida
CAMPOS_RESULTADO_FINAL = (
    "tempo_total_s",
    "tempo_ida_s",
    "tempo_volta_s",
    "distancia_total_m",
    "velocidade_media",
    "velocidade_maxima",
    "turnaround_s",
    "passos",
    "execucao_valida",
)


def calcular_resultado_final(amostras_lidar):
    """amostras_lidar: lista de {"t","y","v","a"} (t absoluto em s; y em m; v em m/s)."""
    resultado = {campo: None for campo in CAMPOS_RESULTADO_FINAL}
    if len(amostras_lidar) >= 2:
        resultado["tempo_total_s"] = round(amostras_lidar[-1]["t"] - amostras_lidar[0]["t"], 3)
        resultado["velocidade_maxima"] = round(max(abs(a["v"]) for a in amostras_lidar), 3)
    return resultado


# --------------------------------------------------------------------------
# Orquestrador: estado + comandos
# --------------------------------------------------------------------------
class Orquestrador:
    def __init__(self, lidar, zed):
        self.lidar = lidar
        self.zed = zed
        self.estado = "parado"        # parado | a_gravar | terminado  (em_pausa fica por implementar)
        self.distancia_alvo_m = DISTANCIA_ALVO_PADRAO_M
        self.resultado_final = None   # dict preenchido em terminar(), apagado em guardar_resultado()

    def mensagem_estado(self):
        return {
            "tipo": "estado",
            "estado_tentativa": self.estado,
            "zed_ligada": True,       # sempre verdadeiros para já
            "sensor_ligado": True,
            "fase_atual": None,       # nulo até o motor detetar as fases do teste
        }

    # Cada comando devolve True se o estado mudou, False se foi rejeitado.

    def definir_distancia_alvo(self, valor_m):
        """Só antes de começar o teste. Não muda o estado."""
        if self.estado == "a_gravar":
            return False
        try:
            valor = float(valor_m)
        except (TypeError, ValueError):
            return False
        if valor <= 0:
            return False
        self.distancia_alvo_m = valor
        return True

    def iniciar(self):
        if self.estado == "a_gravar":
            return False
        # estado parado, ou terminado com tentativa por guardar -> é descartada
        # (os iniciar_gravacao() de cada sub fazem clear() da lista_temp).
        self.resultado_final = None
        self.lidar.iniciar_gravacao()
        self.zed.iniciar_gravacao()
        self.estado = "a_gravar"
        return True

    def terminar(self):
        if self.estado != "a_gravar":
            return False
        self.lidar.parar_gravacao()
        self.zed.parar_gravacao()
        # A tentativa fica em memória nos subs (lista_temp) até guardar_resultado.
        self.resultado_final = calcular_resultado_final(self.lidar.get_amostras())
        self.estado = "terminado"
        return True

    def guardar_resultado(self):
        if self.estado != "terminado":
            return False
        self.lidar.guardar_csv()
        self.zed.guardar_csv()
        self.resultado_final = None   # opção 1: volta a parado e apaga a tentativa da memória
        self.estado = "parado"
        return True


# --------------------------------------------------------------------------
# Ligações WebSocket
# --------------------------------------------------------------------------
class Ligacoes:
    def __init__(self):
        self.ativas = set()
        self._trinco = asyncio.Lock()   # emissor e comandos escrevem no mesmo socket

    async def difundir(self, mensagem):
        async with self._trinco:
            mortas = []
            for ws in list(self.ativas):
                try:
                    await ws.send_json(mensagem)
                except Exception:
                    mortas.append(ws)
            for ws in mortas:
                self.ativas.discard(ws)


# --------------------------------------------------------------------------
# Mensagens ao vivo
# --------------------------------------------------------------------------
def codificar_frame(frame):
    """frame BGRA (ZED) -> imagem 640x360 JPEG/WebP em base64 (str)."""
    rgb = frame[:, :, [2, 1, 0]]
    imagem = Image.fromarray(rgb).resize(TAMANHO_IMAGEM, resample=Image.Resampling.BOX)
    buffer = io.BytesIO()
    imagem.save(buffer, format=_FORMATOS_PIL[FORMATO_IMAGEM], quality=QUALIDADE_IMAGEM)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def mensagem_amostra(tipo, amostra):
    return {
        "tipo": tipo,                                    # "lidar" ou "zed"
        "t_s": round(amostra["t_s"], 3),
        "distancia_m": round(amostra["distancia_m"], 3),
        "velocidade": round(amostra["velocidade"], 3),
        "aceleracao": round(amostra["aceleracao"], 3),
    }


async def emissor(app):
    """Envia camara sempre; lidar e zed só em a_gravar. Tudo a CADENCIA_HZ."""
    periodo = 1 / CADENCIA_HZ
    proximo = time.monotonic()
    ultimo_t = {"lidar": None, "zed": None}   # evita reenviar a mesma amostra se o sensor parar

    while True:
        orq = app.state.orq
        ligacoes = app.state.ligacoes

        if ligacoes.ativas:                    # sem páginas ligadas não gasta CPU a codificar
            mensagens = []

            frame = orq.zed.get_ultimo_frame()
            if frame is not None:              # None até a câmara entregar o 1.º frame
                imagem = await asyncio.to_thread(codificar_frame, frame)
                mensagens.append({"tipo": "camara", "format": FORMATO_IMAGEM, "imagem_base64": imagem})

            if orq.estado == "a_gravar":
                for tipo, sub in (("lidar", orq.lidar), ("zed", orq.zed)):
                    amostra = sub.get_ultima_amostra()
                    if amostra is not None and amostra["t_s"] != ultimo_t[tipo]:
                        ultimo_t[tipo] = amostra["t_s"]
                        mensagens.append(mensagem_amostra(tipo, amostra))
            else:
                ultimo_t = {"lidar": None, "zed": None}

            for mensagem in mensagens:
                await ligacoes.difundir(mensagem)

        # max(): se um ciclo demorou demais, não faz rajadas para recuperar o atraso
        proximo = max(proximo + periodo, time.monotonic())
        await asyncio.sleep(max(0.0, proximo - time.monotonic()))


# --------------------------------------------------------------------------
# Comandos página -> motor
# --------------------------------------------------------------------------
async def tratar_comando(app, mensagem):
    orq = app.state.orq
    ligacoes = app.state.ligacoes
    tipo = mensagem.get("tipo")

    if tipo == "iniciar":
        mudou = orq.iniciar()
    elif tipo == "terminar":
        mudou = orq.terminar()
    elif tipo == "guardar_resultado":
        mudou = orq.guardar_resultado()
    elif tipo == "distancia_alvo":
        aceite = orq.definir_distancia_alvo(mensagem.get("distancia_alvo_m"))
        print(f"distancia_alvo -> {orq.distancia_alvo_m} m ({'aceite' if aceite else 'rejeitada'})")
        return
    elif tipo in COMANDOS_IGNORADOS:
        print(f"Comando '{tipo}' ignorado (não implementado)")
        return
    else:
        print(f"Comando desconhecido: {mensagem!r}")
        return

    if not mudou:
        print(f"Comando '{tipo}' rejeitado no estado '{orq.estado}'")
        return

    await ligacoes.difundir(orq.mensagem_estado())
    if tipo == "terminar":
        await ligacoes.difundir({"tipo": "resultado_final", **orq.resultado_final})


# --------------------------------------------------------------------------
# Aplicação
# --------------------------------------------------------------------------
@asynccontextmanager
async def ciclo_de_vida(app):
    zed = ZedSub()                 # pode levantar ConnectionError
    try:
        lidar = LidarSub()         # pode levantar serial.SerialException
    except Exception:
        zed.fechar()
        raise

    app.state.orq = Orquestrador(lidar, zed)
    app.state.ligacoes = Ligacoes()
    tarefa = asyncio.create_task(emissor(app))
    try:
        yield
    finally:
        tarefa.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await tarefa
        lidar.fechar()
        zed.fechar()


app = FastAPI(lifespan=ciclo_de_vida)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    ligacoes = websocket.app.state.ligacoes
    ligacoes.ativas.add(websocket)
    try:
        # contrato: `estado` é enviado sempre que uma página se liga
        await websocket.send_json(websocket.app.state.orq.mensagem_estado())
        # o ciclo mantém a função (e por isso a ligação) viva a ouvir comandos
        while True:
            try:
                mensagem = await websocket.receive_json()
            except ValueError:     # JSON inválido: ignora e continua
                continue
            if isinstance(mensagem, dict):
                await tratar_comando(websocket.app, mensagem)
    except WebSocketDisconnect:
        pass
    finally:
        ligacoes.ativas.discard(websocket)
