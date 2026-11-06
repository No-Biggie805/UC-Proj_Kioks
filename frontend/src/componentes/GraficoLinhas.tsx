import type { Amostra, CampoGrafico } from '../protocolo'

const LARGURA = 360
const ALTURA = 180
const MARGEM = { topo: 18, direita: 12, fundo: 30, esquerda: 46 }
const MAX_PONTOS_DESENHADOS = 400
// Marcadores visíveis por série: os dados chegam a ~30 amostras/s.
const MAX_MARCADORES = 24
const NUM_TICKS = 4

interface Props {
  lidar: Amostra[]
  // Sem série ZED o gráfico mostra só o LiDAR (nem linha nem legenda ZED).
  zed?: Amostra[]
  campo: CampoGrafico
  unidade: string
  // Rótulo do eixo Y; por omissão mostra a unidade.
  eixoY?: string
}

function formatarEixo(valor: number) {
  if (Math.abs(valor) >= 100) return valor.toFixed(0)
  return valor.toFixed(2)
}

function ticks(minimo: number, maximo: number) {
  const passo = (maximo - minimo) / (NUM_TICKS - 1)
  return Array.from({ length: NUM_TICKS }, (_, i) => minimo + i * passo)
}

export function GraficoLinhas({ lidar, zed, campo, unidade, eixoY }: Props) {
  const todas = zed ? [...lidar, ...zed] : lidar

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
  const baseY = ALTURA - MARGEM.fundo

  const x = (t: number) => MARGEM.esquerda + ((t - tMin) / intervaloX) * larguraUtil
  const y = (valor: number) => MARGEM.topo + (1 - (valor - yMin) / (yMax - yMin)) * alturaUtil

  const desenhadas = (lista: Amostra[]) => {
    if (lista.length === 0) return []
    const passo = Math.max(1, Math.ceil(lista.length / MAX_PONTOS_DESENHADOS))
    return lista.filter((_, i) => i % passo === 0 || i === lista.length - 1)
  }

  const caminho = (pontos: Amostra[]) =>
    pontos
      .map((a, i) => `${i === 0 ? 'M' : 'L'}${x(a.t_s).toFixed(1)},${y(a[campo]).toFixed(1)}`)
      .join(' ')

  const marcadores = (pontos: Amostra[], classe: string) => {
    const passo = Math.max(1, Math.ceil(pontos.length / MAX_MARCADORES))
    return pontos
      .filter((_, i) => i % passo === 0 || i === pontos.length - 1)
      .map((a, i) => (
        <circle key={`${classe}-${i}`} className={`ponto ponto--${classe}`} cx={x(a.t_s)} cy={y(a[campo])} r={2.6} />
      ))
  }

  const ticksY = ticks(yMin, yMax)
  const ticksX = ticks(tMin, tMax)
  const pontosLidar = desenhadas(lidar)
  const pontosZed = zed ? desenhadas(zed) : []

  return (
    <div className="grafico">
      <svg
        viewBox={`0 0 ${LARGURA} ${ALTURA}`}
        role="img"
        aria-label={`Gráfico de ${unidade} ao longo do tempo`}
      >
        {ticksX.map((valor, indice) => (
          <g key={`x-${indice}`}>
            <line
              className="grafico-grelha"
              x1={x(valor)}
              x2={x(valor)}
              y1={MARGEM.topo}
              y2={baseY}
            />
            <text className="grafico-rotulo" x={x(valor)} y={baseY + 14} textAnchor="middle">
              {valor.toFixed(1)}
            </text>
          </g>
        ))}

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

        <line className="grafico-eixo" x1={MARGEM.esquerda} x2={LARGURA - MARGEM.direita} y1={baseY} y2={baseY} />

        {zed ? (
          <>
            <path className="serie serie--zed" d={caminho(pontosZed)} />
            {marcadores(pontosZed, 'zed')}
          </>
        ) : null}
        <path className="serie serie--lidar" d={caminho(pontosLidar)} />
        {marcadores(pontosLidar, 'lidar')}

        <text className="grafico-titulo-eixo" x={LARGURA / 2} y={ALTURA - 4} textAnchor="middle">
          Tempo (s)
        </text>
        <text className="grafico-titulo-eixo" x={8} y={11} textAnchor="start">
          {eixoY ?? unidade}
        </text>
      </svg>

      <ul className="legenda">
        {zed ? (
          <li>
            <span className="legenda-cor legenda-cor--zed" aria-hidden="true" />
            ZED (posição 3D)
          </li>
        ) : null}
        <li>
          <span className="legenda-cor legenda-cor--lidar" aria-hidden="true" />
          {zed ? 'Sensor de distância' : 'LiDAR'}
        </li>
      </ul>
    </div>
  )
}
