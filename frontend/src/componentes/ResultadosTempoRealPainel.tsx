import type { Amostra } from '../protocolo'
import { Painel } from './Painel'

interface Props {
  amostra: Amostra | undefined
}

export function ResultadosTempoRealPainel({ amostra }: Props) {
  const itens: { rotulo: string; valor: string; porImplementar?: boolean }[] = [
    { rotulo: 'Distância percorrida', valor: 'por implementar', porImplementar: true },
    {
      rotulo: 'Velocidade atual',
      valor: amostra ? `${amostra.velocidade.toFixed(2)} m/s` : '—',
    },
    {
      rotulo: 'Aceleração atual',
      valor: amostra ? `${amostra.aceleracao.toFixed(2)} m/s²` : '—',
    },
    { rotulo: 'Nº de passos (estimado)', valor: 'por implementar', porImplementar: true },
    { rotulo: 'Cadência', valor: 'por implementar', porImplementar: true },
    { rotulo: 'Qualidade tracking', valor: 'por implementar', porImplementar: true },
  ]

  return (
    <Painel titulo="Resultados em tempo real">
      <div className="metricas metricas--grelha">
        {itens.map((item) => (
          <div className="metrica" key={item.rotulo}>
            <span className="metrica-rotulo">{item.rotulo}</span>
            <strong className={`metrica-valor ${item.porImplementar ? 'metrica-valor--pi' : ''}`}>
              {item.valor}
            </strong>
          </div>
        ))}
      </div>
    </Painel>
  )
}
