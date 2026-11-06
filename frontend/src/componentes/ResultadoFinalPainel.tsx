import type { MensagemResultadoFinal } from '../protocolo'
import { Painel } from './Painel'

type ChaveResultado = Exclude<keyof MensagemResultadoFinal, 'tipo'>

const CAMPOS: { chave: ChaveResultado; rotulo: string; unidade: string }[] = [
  { chave: 'tempo_total_s', rotulo: 'Tempo total', unidade: 's' },
  { chave: 'tempo_ida_s', rotulo: 'Tempo ida', unidade: 's' },
  { chave: 'tempo_volta_s', rotulo: 'Tempo volta', unidade: 's' },
  { chave: 'distancia_total_m', rotulo: 'Distância total', unidade: 'm' },
  { chave: 'velocidade_media', rotulo: 'Velocidade média', unidade: 'm/s' },
  { chave: 'velocidade_maxima', rotulo: 'Velocidade máxima', unidade: 'm/s' },
  { chave: 'turnaround_s', rotulo: 'Turnaround', unidade: 's' },
  { chave: 'passos', rotulo: 'Nº de passos', unidade: '' },
  { chave: 'execucao_valida', rotulo: 'Execução válida', unidade: '' },
]

function formatar(valor: MensagemResultadoFinal[ChaveResultado], unidade: string) {
  if (valor === null || valor === undefined) return '—'
  if (typeof valor === 'boolean') return valor ? 'Sim' : 'Não'
  return unidade ? `${valor} ${unidade}` : `${valor}`
}

export function ResultadoFinalPainel({ resultado }: { resultado: MensagemResultadoFinal | null }) {
  return (
    <Painel titulo="Resultado final">
      <dl className="resultado-grelha">
        {CAMPOS.map(({ chave, rotulo, unidade }) => (
          <div className="resultado-item" key={chave}>
            <dt>{rotulo}</dt>
            <dd>{formatar(resultado ? resultado[chave] : null, unidade)}</dd>
          </div>
        ))}
      </dl>
    </Painel>
  )
}
