import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  Amostra,
  Comando,
  EstadoLigacao,
  MensagemEstado,
  MensagemResultadoFinal,
  MensagemServidor,
  Series,
} from './protocolo'
import { URL_SERVIDOR } from './protocolo'

// Reconexão: espera crescente, nunca mais do que 5 s entre tentativas.
const ESPERA_MAXIMA_MS = 5000
// Os gráficos só são redesenhados 10x por segundo, apesar de chegarem ~30 amostras/s.
const INTERVALO_DESENHO_MS = 100
const MAX_AMOSTRAS = 1800

export function useServidor(
  imagemRef: React.MutableRefObject<HTMLImageElement | null>,
  profundidadeRef: React.MutableRefObject<HTMLImageElement | null>,
) {
  const [ligacao, setLigacao] = useState<EstadoLigacao>('a_ligar')
  const [estado, setEstado] = useState<MensagemEstado | null>(null)
  const [resultado, setResultado] = useState<MensagemResultadoFinal | null>(null)
  const [series, setSeries] = useState<Series>({ lidar: [], zed: [] })
  const [temImagem, setTemImagem] = useState(false)
  const [temImagemProfundidade, setTemImagemProfundidade] = useState(false)

  const wsRef = useRef<WebSocket | null>(null)
  const seriesRef = useRef<Series>({ lidar: [], zed: [] })
  const desenhoAgendado = useRef<number | null>(null)

  const agendarDesenho = useCallback(() => {
    if (desenhoAgendado.current !== null) return
    desenhoAgendado.current = window.setTimeout(() => {
      desenhoAgendado.current = null
      setSeries({ lidar: seriesRef.current.lidar.slice(), zed: seriesRef.current.zed.slice() })
    }, INTERVALO_DESENHO_MS)
  }, [])

  const limparSeries = useCallback(() => {
    seriesRef.current = { lidar: [], zed: [] }
    setSeries({ lidar: [], zed: [] })
  }, [])

  useEffect(() => {
    let encerrado = false
    let tentativa = 0
    let temporizador: number | undefined

    const tratar = (mensagem: MensagemServidor) => {
      switch (mensagem.tipo) {
        case 'estado':
          // O estado nunca é assumido pela página: vem sempre do servidor.
          setEstado(mensagem)
          if (mensagem.estado_tentativa === 'a_gravar') {
            limparSeries()
            setResultado(null)
          }
          break

        case 'camara':
          if (imagemRef.current) {
            imagemRef.current.src = `data:image/${mensagem.format};base64,${mensagem.imagem_base64}`
          }
          setTemImagem(true)
          break

        case 'camara_profundidade':
          if (profundidadeRef.current) {
            profundidadeRef.current.src = `data:image/${mensagem.format};base64,${mensagem.imagem_base64}`
          }
          setTemImagemProfundidade(true)
          break

        case 'lidar':
        case 'zed': {
          const amostra: Amostra = {
            t_s: mensagem.t_s,
            distancia_m: mensagem.distancia_m,
            velocidade: mensagem.velocidade,
            aceleracao: mensagem.aceleracao,
          }
          const lista = seriesRef.current[mensagem.tipo]
          lista.push(amostra)
          if (lista.length > MAX_AMOSTRAS) lista.splice(0, lista.length - MAX_AMOSTRAS)
          agendarDesenho()
          break
        }

        case 'resultado_final':
          setResultado(mensagem)
          break
      }
    }

    const ligar = () => {
      setLigacao('a_ligar')
      const ws = new WebSocket(URL_SERVIDOR)
      wsRef.current = ws

      ws.onopen = () => {
        tentativa = 0
        setLigacao('ligada')
        // Os botões só voltam a ativar quando chegar a mensagem `estado`.
        setEstado(null)
        setTemImagem(false)
        setTemImagemProfundidade(false)
      }

      ws.onmessage = (evento) => {
        let mensagem: MensagemServidor
        try {
          mensagem = JSON.parse(evento.data as string) as MensagemServidor
        } catch {
          return
        }
        if (mensagem && typeof mensagem.tipo === 'string') tratar(mensagem)
      }

      ws.onerror = () => ws.close()

      ws.onclose = () => {
        wsRef.current = null
        if (encerrado) return
        setLigacao('desligada')
        setEstado(null)
        setTemImagem(false)
        setTemImagemProfundidade(false)
        tentativa += 1
        temporizador = window.setTimeout(ligar, Math.min(tentativa * 1000, ESPERA_MAXIMA_MS))
      }
    }

    ligar()

    return () => {
      encerrado = true
      window.clearTimeout(temporizador)
      if (desenhoAgendado.current !== null) {
        window.clearTimeout(desenhoAgendado.current)
        desenhoAgendado.current = null
      }
      wsRef.current?.close()
      wsRef.current = null
    }
  }, [agendarDesenho, limparSeries, imagemRef, profundidadeRef])

  const enviar = useCallback((comando: Comando) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) return
    ws.send(JSON.stringify(comando))
  }, [])

  return { ligacao, estado, resultado, series, temImagem, temImagemProfundidade, enviar }
}
