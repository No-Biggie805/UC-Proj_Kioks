"""
Cliente de teste do servidor (sem a página base44).

1.º terminal:  uvicorn servidor:app --port 8000
2.º terminal:  python3 cliente_teste.py

Faz: liga -> espera 2 s -> distancia_alvo 5 m -> iniciar -> 5 s -> terminar -> guardar_resultado.
Imprime `estado` e `resultado_final` sempre; das restantes mensagens imprime 1 em cada 30.
"""
import asyncio
import contextlib
import json

import websockets

URL = "ws://localhost:8000/ws"


async def ouvir(ws):
    contagem = {}
    async for texto in ws:
        mensagem = json.loads(texto)
        tipo = mensagem["tipo"]
        if tipo in ("estado", "resultado_final"):
            print(mensagem)
            continue
        contagem[tipo] = contagem.get(tipo, 0) + 1
        if contagem[tipo] % 30 == 1:
            resumo = {k: (f"<{len(v)} chars>" if k == "imagem_base64" else v) for k, v in mensagem.items()}
            print(resumo)


async def enviar(ws, **mensagem):
    print(">>", mensagem)
    await ws.send(json.dumps(mensagem))


async def main():
    async with websockets.connect(URL) as ws:
        tarefa = asyncio.create_task(ouvir(ws))
        await asyncio.sleep(2)
        await enviar(ws, tipo="distancia_alvo", distancia_alvo_m=5.0)
        await enviar(ws, tipo="iniciar")
        await asyncio.sleep(5)
        await enviar(ws, tipo="terminar")
        await asyncio.sleep(1)
        await enviar(ws, tipo="guardar_resultado")
        await asyncio.sleep(1)
        tarefa.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await tarefa


if __name__ == "__main__":
    asyncio.run(main())
