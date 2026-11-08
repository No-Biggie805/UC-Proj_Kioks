import type { Amostra, CampoGrafico } from '../protocolo'

const LARGURA = 360
const ALTURA = 180
const MARGEM = { topo: 18, direita: 12, fundo: 30, esquerda: 46 }
const MAX_PONTOS_DESENHADOS = 400
// Marcadores visíveis por série: os dados chegam a ~30 amostras/s.
const MAX_MARCADORES = 24
const NUM_TICKS = 4

// Escala e janela do painel «Sensor de distância linear».
export const Y_MIN_M = 0
export const Y_MAX_M = 10
export const PASSO_Y_M = 2
export const JANELA_S = 10

interface Props {
  lidar: Amostra[]
  // Sem série ZED o gráfico mostra só o LiDAR (nem linha nem legenda ZED).
  zed?: Amostra[]
  campo: CampoGrafico
  unidade: string
  // Rótulo do eixo Y; por omissão mostra a unidade.
  eixoY?: string
  // Eixo Y fixo (sem folga nem limites tirados dos dados) e respectivo passo entre ticks.
  yMin?: number
  yMax?: number
  passoY?: number
  // Janela temporal deslizante, em segundos, a partir da última amostra LiDAR.
  janelaS?: number
}

function formatarEixo(valor: number) {
  if (Math.abs(valor) >= 100) return valor.toFixed(0)
  return valor.toFixed(2)
}

function ticks(minimo: number, maximo: number) {
  const passo = (maximo - minimo) / (NUM_TICKS - 1)
  return Array.from({ length: NUM_TICKS }, (_, i) => minimo + i * passo)
}

function ticksPorPasso(minimo: number, maximo: number, passo: number) {
  const quantidade = Math.round((maximo - minimo) / passo)
  return Array.from({ length: quantidade + 1 }, (_, i) => minimo + i * passo)
}

// Cada segundo inteiro dentro da janela.
function segundosInteiros(minimo: number, maximo: number) {
  const primeiro = Math.ceil(minimo)
  const ultimo = Math.floor(maximo)
  return Array.from({ length: Math.max(0, ultimo - primeiro + 1) }, (_, i) => primeiro + i)
}

export function GraficoLinhas({ lidar, zed, campo, unidade, eixoY, yMin, yMax, passoY, janelaS }: Props) {
  const todas = zed ? [...lidar, ...zed] : lidar

  if (todas.length === 0) {
    return <div className="grafico-vazio">Sem dados</div>
  }

  // Eixo X: com janela, o eixo segue a última amostra LiDAR e só desliza depois de a preencher.
  let tMin: number
  let tMax: number

  if (janelaS !== undefined) {
    const tAtual = Math.max(...lidar.map((a) => a.t_s))
    tMax = Math.max(tAtual, janelaS)
    tMin = tMax - janelaS
  } else {
    const tMinDados = Math.min(...todas.map((a) => a.t_s))
    const tMaxDados = Math.max(...todas.map((a) => a.t_s))
    // Com uma só amostra não há intervalo: abre-se o eixo para o ponto ficar visível.
    const semIntervalo = tMaxDados - tMinDados < 1e-9
    tMin = semIntervalo ? tMinDados - 0.5 : tMinDados
    tMax = semIntervalo ? tMaxDados + 0.5 : tMaxDados
  }

  // Eixo Y: com limites explícitos não se olha para os dados.
  const escalaFixa = yMin !== undefined && yMax !== undefined
  let eixoYMin: number
  let eixoYMax: number

  if (escalaFixa) {
    eixoYMin = yMin
    eixoYMax = yMax
  } else {
    // Com janela, a escala automática olha só para as amostras visíveis.
    const visiveisFiltradas = janelaS !== undefined ? todas.filter((a) => a.t_s >= tMin) : todas
    const visiveis = visiveisFiltradas.length > 0 ? visiveisFiltradas : todas
    const valores = visiveis.map((a) => a[campo])
    let minimo = Math.min(...valores)
    let maximo = Math.max(...valores)

    if (maximo - minimo < 1e-9) {
      const folga = Math.abs(maximo) || 1
      minimo -= folga / 2
      maximo += folga / 2
    } else {
      const folga = (maximo - minimo) * 0.1
      minimo -= folga
      maximo += folga
    }

    eixoYMin = minimo
    eixoYMax = maximo
  }

  const intervaloX = tMax - tMin || 1
  const larguraUtil = LARGURA - MARGEM.esquerda - MARGEM.direita
  const alturaUtil = ALTURA - MARGEM.topo - MARGEM.fundo
  const baseY = ALTURA - MARGEM.fundo

  const x = (t: number) => MARGEM.esquerda + ((t - tMin) / intervaloX) * larguraUtil
  // O valor é limitado ao eixo para o traço nunca sair da área do gráfico.
  const y = (valor: number) => {
    const limitado = Math.min(Math.max(valor, eixoYMin), eixoYMax)
    return MARGEM.topo + (1 - (limitado - eixoYMin) / (eixoYMax - eixoYMin)) * alturaUtil
  }

  const desenhadas = (lista: Amostra[]) => {
    if (lista.length === 0) return []
    // Dentro da janela desenha-se tudo: 10 s a ~30 amostras/s cabem no limite.
    if (janelaS !== undefined) return lista.filter((a) => a.t_s >= tMin)
    const passo = Math.max(1, Math.ceil(lista.length / MAX_PONTOS_DESENHADOS))
    return lista.filter((_, i) => i % passo === 0 || i === lista.length - 1)
  }

  const caminho = (pontos: Amostra[]) =>
    pontos
      .map((a, i) => `${i === 0 ? 'M' : 'L'}${x(a.t_s).toFixed(1)},${y(a[campo]).toFixed(1)}`)
      .join(' ')

  const marcadores = (pontos: Amostra[], classe: string) => {
    if (janelaS !== undefined) {
      if (pontos.length === 0) return []
      // Um marcador por segundo inteiro, na amostra temporalmente mais próxima desse segundo.
      return segundosInteiros(tMin, tMax).map((segundo) => {
        const maisProxima = pontos.reduce((melhor, a) =>
          Math.abs(a.t_s - segundo) < Math.abs(melhor.t_s - segundo) ? a : melhor,
        )
        return (
          <circle
            key={`${classe}-t${segundo}`}
            className={`ponto ponto--${classe}`}
            cx={x(maisProxima.t_s)}
            cy={y(maisProxima[campo])}
            r={2.6}
          />
        )
      })
    }

    const passo = Math.max(1, Math.ceil(pontos.length / MAX_MARCADORES))
    return pontos
      .filter((_, i) => i % passo === 0 || i === pontos.length - 1)
      .map((a, i) => (
        <circle key={`${classe}-${i}`} className={`ponto ponto--${classe}`} cx={x(a.t_s)} cy={y(a[campo])} r={2.6} />
      ))
  }

  const ticksY =
    escalaFixa && passoY !== undefined ? ticksPorPasso(eixoYMin, eixoYMax, passoY) : ticks(eixoYMin, eixoYMax)
  const ticksX = janelaS !== undefined ? segundosInteiros(tMin, tMax) : ticks(tMin, tMax)
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
              {janelaS !== undefined ? valor.toFixed(0) : valor.toFixed(1)}
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
              {escalaFixa ? valor.toFixed(0) : formatarEixo(valor)}
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
