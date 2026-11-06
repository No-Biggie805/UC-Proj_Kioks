import type { Amostra, MensagemEstado, Series } from '../protocolo'
import { GraficoLinhas } from './GraficoLinhas'
import { Painel } from './Painel'

interface Props {
  series: Series
  estado: MensagemEstado | null
}

function valor(valorRecebido: number | undefined, casas: number, unidade: string) {
  if (valorRecebido === undefined) return '—'
  return `${valorRecebido.toFixed(casas)} ${unidade}`
}

function Metricas({ amostra }: { amostra: Amostra | undefined }) {
  return (
    <div className="metricas">
      <div className="metrica">
        <span className="metrica-rotulo">Distância atual</span>
        <strong className="metrica-valor">{valor(amostra?.distancia_m, 2, 'm')}</strong>
      </div>
      <div className="metrica">
        <span className="metrica-rotulo">Velocidade atual</span>
        <strong className="metrica-valor">{valor(amostra?.velocidade, 2, 'm/s')}</strong>
      </div>
      <div className="metrica">
        <span className="metrica-rotulo">Taxa de aquisição</span>
        <strong className="metrica-valor metrica-valor--pi">—</strong>
        <small className="metrica-nota">por implementar</small>
      </div>
    </div>
  )
}

export function SensorPainel({ series, estado }: Props) {
  const ultimaLidar = series.lidar[series.lidar.length - 1]

  return (
    <Painel
      titulo="Sensor de distância linear"
      acao={
        <span className={`pilula ${estado?.sensor_ligado ? 'pilula--ligada' : 'pilula--desligada'}`}>
          {estado ? (estado.sensor_ligado ? 'Ativo' : 'Inativo') : '—'}
        </span>
      }
    >
      <Metricas amostra={ultimaLidar} />
      <div className="grafico-mini">
        {/* Este painel é só do sensor LiDAR; a série ZED é usada nos painéis de comparação. */}
        <GraficoLinhas lidar={series.lidar} campo="distancia_m" unidade="m" />
      </div>
    </Painel>
  )
}

export function ComparacaoPainel({ series }: { series: Series }) {
  const ultimaLidar = series.lidar[series.lidar.length - 1]
  const ultimaZed = series.zed[series.zed.length - 1]
  // Único valor derivado da página: subtração das duas últimas amostras recebidas.
  const diferenca =
    ultimaLidar !== undefined && ultimaZed !== undefined
      ? ultimaZed.distancia_m - ultimaLidar.distancia_m
      : undefined

  return (
    <Painel titulo="Comparação de distância (ZED vs Sensor)">
      <GraficoLinhas lidar={series.lidar} zed={series.zed} campo="distancia_m" unidade="m" />
      <div className="metricas metricas--coluna">
        <div className="metrica">
          <span className="metrica-rotulo">Distância atual</span>
          <strong className="metrica-valor">{valor(ultimaLidar?.distancia_m, 2, 'm')}</strong>
        </div>
        <div className="metrica">
          <span className="metrica-rotulo">Diferença (ZED − Sensor)</span>
          <strong className="metrica-valor">{valor(diferenca, 2, 'm')}</strong>
        </div>
      </div>
    </Painel>
  )
}

export function VelocidadePainel({ series }: { series: Series }) {
  return (
    <Painel titulo="Velocidade (LiDAR vs ZED)">
      <GraficoLinhas lidar={series.lidar} zed={series.zed} campo="velocidade" unidade="m/s" />
    </Painel>
  )
}

export function AceleracaoPainel({ series }: { series: Series }) {
  return (
    <Painel titulo="Aceleração (LiDAR vs ZED)">
      <GraficoLinhas lidar={series.lidar} zed={series.zed} campo="aceleracao" unidade="m/s²" />
    </Painel>
  )
}
