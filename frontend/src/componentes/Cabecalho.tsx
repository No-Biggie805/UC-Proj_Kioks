import type { EstadoLigacao, MensagemEstado } from '../protocolo'
import { URL_SERVIDOR } from '../protocolo'

const TEXTO_LIGACAO: Record<EstadoLigacao, string> = {
  a_ligar: 'a ligar…',
  ligada: 'ligado',
  desligada: 'desligado',
}

interface Props {
  ligacao: EstadoLigacao
  estado: MensagemEstado | null
}

export function Cabecalho({ ligacao, estado }: Props) {
  return (
    <header className="cabecalho">
      <div className="cabecalho-titulo">
        <span className="etiqueta">Avaliação funcional</span>
        <h1>Teste Linear de Ida e Volta</h1>
        <p>Avaliação da mobilidade e capacidade funcional</p>
      </div>

      <div className="cabecalho-cartoes">
        <div className="cartao-info">
          <div className="utilizador">
            <span className="utilizador-icone" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8">
                <circle cx="12" cy="8" r="3.4" />
                <path d="M4.5 20c0-3.6 3.4-6 7.5-6s7.5 2.4 7.5 6" strokeLinecap="round" />
              </svg>
            </span>
            <div className="utilizador-texto">
              <strong>Utilizador</strong>
              <span>ID: U001</span>
            </div>
          </div>
          <button type="button" className="botao-contorno">
            Novo Utilizador
          </button>
        </div>

        <div className="cartao-info">
          <div className="cartao-info-topo">
            <strong>Estado do Sistema</strong>
            <span className={`pilula pilula--${ligacao}`}>{TEXTO_LIGACAO[ligacao]}</span>
          </div>
          <ul className="estado-sistema">
            <li className={estado?.zed_ligada ? 'estado-ok' : 'estado-neutro'}>
              <span className="estado-ponto" aria-hidden="true" />
              ZED ligada
            </li>
            <li className={estado?.sensor_ligado ? 'estado-ok' : 'estado-neutro'}>
              <span className="estado-ponto" aria-hidden="true" />
              Sensor ligado
            </li>
          </ul>
          <code className="url-servidor">{URL_SERVIDOR}</code>
        </div>
      </div>
    </header>
  )
}
