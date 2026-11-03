import { useEffect, useRef, useState } from 'react'
import type { Comando, EstadoTentativa } from '../protocolo'

interface Props {
  controlosAtivos: boolean
  estadoTentativa: EstadoTentativa | null
  enviar: (comando: Comando) => void
}

const DISTANCIA_INICIAL = '5.0'
const ATRASO_ENVIO_MS = 400

export function BarraControlo({ controlosAtivos, estadoTentativa, enviar }: Props) {
  const [distancia, setDistancia] = useState(DISTANCIA_INICIAL)
  const temporizador = useRef<number | undefined>(undefined)

  useEffect(() => () => window.clearTimeout(temporizador.current), [])

  const podeEditar = controlosAtivos && estadoTentativa !== 'a_gravar'

  const enviarDistancia = (texto: string) => {
    const numero = Number(texto.replace(',', '.'))
    if (!Number.isFinite(numero) || numero <= 0) return
    enviar({ tipo: 'distancia_alvo', distancia_alvo_m: numero })
  }

  const alterarDistancia = (delta: number) => {
    const atual = Number(distancia.replace(',', '.')) || 0
    const novo = Math.round((atual + delta) * 10) / 10
    if (novo <= 0) return
    const texto = novo.toFixed(1)
    setDistancia(texto)
    window.clearTimeout(temporizador.current)
    enviarDistancia(texto)
  }

  const escreverDistancia = (texto: string) => {
    setDistancia(texto)
    window.clearTimeout(temporizador.current)
    temporizador.current = window.setTimeout(() => enviarDistancia(texto), ATRASO_ENVIO_MS)
  }

  return (
    <footer className="barra-controlo">
      <div className="barra-descricao">
        <strong>Controlo do teste</strong>
        <p>Configure a distância, inicie a aquisição e acompanhe o teste em tempo real.</p>
      </div>

      <div className="controlo-distancia">
        <span className="metrica-rotulo">Distância alvo (m)</span>
        <div className="passo">
          <button
            type="button"
            className="botao-passo"
            onClick={() => alterarDistancia(-0.5)}
            disabled={!podeEditar}
            aria-label="Diminuir distância alvo"
          >
            −
          </button>
          <input
            className="entrada-distancia"
            value={distancia}
            inputMode="decimal"
            onChange={(evento) => escreverDistancia(evento.target.value)}
            disabled={!podeEditar}
            aria-label="Distância alvo em metros"
          />
          <button
            type="button"
            className="botao-passo"
            onClick={() => alterarDistancia(0.5)}
            disabled={!podeEditar}
            aria-label="Aumentar distância alvo"
          >
            +
          </button>
        </div>
      </div>

      <div className="acoes">
        <button
          type="button"
          className="botao botao--iniciar"
          onClick={() => enviar({ tipo: 'iniciar' })}
          disabled={!controlosAtivos || estadoTentativa === 'a_gravar'}
        >
          <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
            <path d="M8 5.5v13l11-6.5z" fill="currentColor" />
          </svg>
          Iniciar Teste
        </button>

        <button type="button" className="botao botao--pausar" disabled title="Por implementar">
          <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
            <path d="M7.5 5h3.2v14H7.5zM13.3 5h3.2v14h-3.2z" fill="currentColor" />
          </svg>
          Pausar
        </button>

        <button
          type="button"
          className="botao botao--terminar"
          onClick={() => enviar({ tipo: 'terminar' })}
          disabled={!controlosAtivos || estadoTentativa !== 'a_gravar'}
        >
          <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
            <rect x="6.5" y="6.5" width="11" height="11" rx="1.6" fill="currentColor" />
          </svg>
          Terminar
        </button>

        <button
          type="button"
          className="botao botao--guardar"
          onClick={() => enviar({ tipo: 'guardar_resultado' })}
          disabled={!controlosAtivos || estadoTentativa !== 'terminado'}
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
            <path d="M5 4.5h10.5L19.5 8.5V19.5H5z" strokeLinejoin="round" />
            <path d="M8.5 4.5v5h6v-5M8.5 19.5v-5.5h7v5.5" strokeLinejoin="round" />
          </svg>
          Guardar Resultado
        </button>
      </div>
    </footer>
  )
}
