import type { Amostra, MensagemEstado, Series } from '../protocolo'
import { GraficoLinhas, JANELA_S, PASSO_Y_M, Y_MAX_M, Y_MIN_M } from './GraficoLinhas'
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
        {/* Este painel é só do sensor LiDAR; a série ZED é usada no painel de comparação. */}
        <GraficoLinhas
          lidar={series.lidar}
          campo="distancia_m"
          unidade="m"
          eixoY="Distância (m)"
          yMin={Y_MIN_M}
          yMax={Y_MAX_M}
          passoY={PASSO_Y_M}
          janelaS={JANELA_S}
        />
      </div>
    </Painel>
  )
}

export function ComparacaoPainel({ series }: { series: Series }) {
  const ultimaLidar = series.lidar[series.lidar.length - 1]
  const ultimaZed = series.zed[series.zed.length - 1]
  // Único valor derivado da página: distância entre as duas últimas amostras recebidas.
  const diferenca =
    ultimaLidar !== undefined && ultimaZed !== undefined
      ? Math.abs(ultimaZed.distancia_m - ultimaLidar.distancia_m)
      : undefined

  return (
    <Painel titulo="Comparação de distância (ZED vs Sensor)">
      <div className="comparacao">
        <div className="comparacao-grafico">
          <GraficoLinhas
            lidar={series.lidar}
            zed={series.zed}
            campo="distancia_m"
            unidade="m"
            eixoY="Distância (m)"
            janelaS={JANELA_S}
          />
        </div>

        <aside className="comparacao-resumo">
          <h3>Distância atual</h3>
          <dl className="comparacao-linhas">
            <div className="comparacao-linha">
              <dt>ZED</dt>
              <dd>{valor(ultimaZed?.distancia_m, 2, 'm')}</dd>
            </div>
            <div className="comparacao-linha">
              <dt>Sensor</dt>
              <dd>{valor(ultimaLidar?.distancia_m, 2, 'm')}</dd>
            </div>
            <div className="comparacao-linha comparacao-linha--separada">
              <dt>Diferença</dt>
              <dd>{valor(diferenca, 2, 'm')}</dd>
            </div>
          </dl>
        </aside>
      </div>
    </Painel>
  )
}
