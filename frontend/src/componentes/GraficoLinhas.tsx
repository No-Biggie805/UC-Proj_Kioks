import type { Amostra, CampoGrafico } from '../protocolo'

const LARGURA = 360
const ALTURA = 180
const MARGEM = { topo: 12, direita: 12, fundo: 26, esquerda: 44 }
const MAX_PONTOS_DESENHADOS = 400
const NUM_TICKS = 4

interface Props {
  lidar: Amostra[]
  zed: Amostra[]
  campo: CampoGrafico
  unidade: string
}

function formatarEixo(valor: number) {
  if (Math.abs(valor) >= 100) return valor.toFixed(0)
  return valor.toFixed(2)
}

function ticks(minimo: number, maximo: number) {
  const passo = (maximo - minimo) / (NUM_TICKS - 1)
  return Array.from({ length: NUM_TICKS }, (_, i) => minimo + i * passo)
}

export function GraficoLinhas({ lidar, zed, campo, unidade }: Props) {
  const todas = [...lidar, ...zed]

  if (todas.length === 0) {
    return <div className="grafico-vazio">Sem dados</div>
  }

  const tMinDados = Math.min(...todas.map((a) => a.t_s))
  const tMaxDados = Math.max(...todas.map((a) => a.t_s))
  // Com uma só amostra não há intervalo: abre-se o eixo para o ponto ficar visível.
  const semIntervalo = tMaxDados - tMinDados < 1e-9
  const tMin = semIntervalo ? tMinDados - 0.5 : tMinDados
  const tMax = semIntervalo ? tMaxDados + 0.5 : tMaxDados
  const valores = todas.map((a) => a[campo])
  let yMin = Math.min(...valores)
  let yMax = Math.max(...valores)

  if (yMax - yMin < 1e-9) {
    const folga = Math.abs(yMax) || 1
    yMin -= folga / 2
    yMax += folga / 2
  } else {
    const folga = (yMax - yMin) * 0.1
    yMin -= folga
    yMax += folga
  }

  const intervaloX = tMax - tMin || 1
  const larguraUtil = LARGURA - MARGEM.esquerda - MARGEM.direita
  const alturaUtil = ALTURA - MARGEM.topo - MARGEM.fundo

  const x = (t: number) => MARGEM.esquerda + ((t - tMin) / intervaloX) * larguraUtil
  const y = (valor: number) => MARGEM.topo + (1 - (valor - yMin) / (yMax - yMin)) * alturaUtil

  const caminho = (lista: Amostra[]) => {
    if (lista.length === 0) return ''
    const passo = Math.max(1, Math.ceil(lista.length / MAX_PONTOS_DESENHADOS))
    const pontos = lista.filter((_, i) => i % passo === 0 || i === lista.length - 1)
    return pontos
      .map((a, i) => `${i === 0 ? 'M' : 'L'}${x(a.t_s).toFixed(1)},${y(a[campo]).toFixed(1)}`)
      .join(' ')
  }

  const ticksY = ticks(yMin, yMax)
  const ticksX = ticks(tMin, tMax)

  return (
    <div className="grafico">
      <svg viewBox={`0 0 ${LARGURA} ${ALTURA}`} role="img" aria-label={`Gráfico de ${unidade} ao longo do tempo`}>
        {ticksY.map((valor, indice) => (
          <g key={`y-${indice}`}>
            <line
              className="grafico-grelha"
              x1={MARGEM.esquerda}
              x2={LARGURA - MARGEM.direita}
              y1={y(valor)}
              y2={y(valor)}
            />
            <text className="grafico-rotulo" x={MARGEM.esquerda - 6} y={y(valor) + 3} textAnchor="end">
              {formatarEixo(valor)}
            </text>
          </g>
        ))}

        {ticksX.map((valor, indice) => (
          <text
            key={`x-${indice}`}
            className="grafico-rotulo"
            x={x(valor)}
            y={ALTURA - MARGEM.fundo + 14}
            textAnchor="middle"
          >
            {valor.toFixed(1)}
          </text>
        ))}

        <line
          className="grafico-eixo"
          x1={MARGEM.esquerda}
          x2={LARGURA - MARGEM.direita}
          y1={ALTURA - MARGEM.fundo}
          y2={ALTURA - MARGEM.fundo}
        />

        <path className="serie serie--zed" d={caminho(zed)} />
        <path className="serie serie--lidar" d={caminho(lidar)} />

        {zed.length === 1 ? (
          <circle className="ponto ponto--zed" cx={x(zed[0].t_s)} cy={y(zed[0][campo])} r={2.5} />
        ) : null}
        {lidar.length === 1 ? (
          <circle className="ponto ponto--lidar" cx={x(lidar[0].t_s)} cy={y(lidar[0][campo])} r={2.5} />
        ) : null}

        <text className="grafico-titulo-eixo" x={LARGURA / 2} y={ALTURA - 3} textAnchor="middle">
          t (s)
        </text>
        <text className="grafico-titulo-eixo" x={10} y={MARGEM.topo + 2} textAnchor="start">
          {unidade}
        </text>
      </svg>

      <ul className="legenda">
        <li>
          <span className="legenda-cor legenda-cor--lidar" aria-hidden="true" />
          LiDAR
        </li>
        <li>
          <span className="legenda-cor legenda-cor--zed" aria-hidden="true" />
          ZED
        </li>
      </ul>
    </div>
  )
}
