import { useRef } from 'react'
import { useServidor } from './useServidor'
import { BarraControlo } from './componentes/BarraControlo'
import { Cabecalho } from './componentes/Cabecalho'
import { CamaraPainel } from './componentes/CamaraPainel'
import { EstadoTestePainel } from './componentes/EstadoTestePainel'
import { Painel, PorImplementar } from './componentes/Painel'
import {
  AceleracaoPainel,
  ComparacaoPainel,
  SensorPainel,
  VelocidadePainel,
} from './componentes/PaineisGraficos'
import { ResultadoFinalPainel } from './componentes/ResultadoFinalPainel'
import { ResultadosTempoRealPainel } from './componentes/ResultadosTempoRealPainel'

export default function App() {
  const imagemRef = useRef<HTMLImageElement | null>(null)
  const { ligacao, estado, resultado, series, temImagem, enviar } = useServidor(imagemRef)

  const ultimaLidar = series.lidar[series.lidar.length - 1]
  // Os botões só ativam com ligação aberta E com um `estado` recebido do servidor.
  const controlosAtivos = ligacao === 'ligada' && estado !== null

  return (
    <div className="pagina">
      <div className="conteudo">
        <Cabecalho ligacao={ligacao} estado={estado} />

        <main className="grelha">
          <div className="span-5">
            <CamaraPainel imagemRef={imagemRef} temImagem={temImagem} ligado={ligacao === 'ligada'} />
          </div>

          <div className="span-3">
            <Painel titulo="Câmara ZED — Mapa de profundidade">
              <PorImplementar nota="Chega da ZED" />
            </Painel>
          </div>

          <div className="span-4">
            <Painel titulo="Pose 3D (ZED)">
              <PorImplementar nota="Chega da ZED" />
            </Painel>
          </div>

          <div className="span-3">
            <Painel titulo="Vista lateral (perfil)">
              <PorImplementar nota="Chega da ZED" />
            </Painel>
          </div>

          <div className="span-5">
            <SensorPainel series={series} estado={estado} />
          </div>

          <div className="span-4">
            <EstadoTestePainel estado={estado} tempoDecorrido={ultimaLidar?.t_s} />
          </div>

          <div className="span-4">
            <ComparacaoPainel series={series} />
          </div>

          <div className="span-4">
            <VelocidadePainel series={series} />
          </div>

          <div className="span-4">
            <AceleracaoPainel series={series} />
          </div>

          <div className="span-5">
            <ResultadosTempoRealPainel amostra={ultimaLidar} />
          </div>

          <div className="span-3">
            <Painel titulo="Trajetória do utilizador (vista superior)">
              <PorImplementar nota="Depende das fases do teste" />
            </Painel>
          </div>

          <div className="span-4">
            <ResultadoFinalPainel resultado={resultado} />
          </div>
        </main>
      </div>

      <BarraControlo
        controlosAtivos={controlosAtivos}
        estadoTentativa={estado?.estado_tentativa ?? null}
        enviar={enviar}
      />
    </div>
  )
}
