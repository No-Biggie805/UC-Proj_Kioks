import type { EstadoTentativa, MensagemEstado } from '../protocolo'
import { Painel } from './Painel'

const ROTULO_ESTADO: Record<EstadoTentativa, string> = {
  parado: 'Parado',
  a_gravar: 'Em execução',
  terminado: 'Terminado',
}

const FASES = ['Início', 'Ida', 'Mudança de direção', 'Volta', 'Fim']

interface Props {
  estado: MensagemEstado | null
  tempoDecorrido?: number
}

export function EstadoTestePainel({ estado, tempoDecorrido }: Props) {
  const tentativa = estado?.estado_tentativa ?? null
  const faseAtual = estado?.fase_atual ?? null

  return (
    <Painel
      titulo="Estado do teste"
      acao={
        <span className={`pilula ${tentativa ? `pilula--${tentativa}` : 'pilula--neutra'}`}>
          {tentativa ? ROTULO_ESTADO[tentativa] : '—'}
        </span>
      }
    >
      <div className="estado-teste">
        <div className="estado-teste-linha">
          <span className="metrica-rotulo">Fase atual</span>
          <strong className="estado-teste-valor">{faseAtual ?? '—'}</strong>
        </div>
        <div className="estado-teste-linha">
          <span className="metrica-rotulo">Tempo decorrido</span>
          <strong className="estado-teste-valor">
            {tempoDecorrido === undefined ? '—' : `${tempoDecorrido.toFixed(2)} s`}
          </strong>
        </div>
      </div>

      <ol className="fases">
        {FASES.map((fase) => {
          const ativa = faseAtual !== null && faseAtual.trim().toLowerCase() === fase.toLowerCase()
          return (
            <li key={fase} className={`fase ${ativa ? 'fase--ativa' : ''}`}>
              <span className="fase-no" aria-hidden="true" />
              <span className="fase-rotulo">{fase}</span>
            </li>
          )
        })}
      </ol>
    </Painel>
  )
}
