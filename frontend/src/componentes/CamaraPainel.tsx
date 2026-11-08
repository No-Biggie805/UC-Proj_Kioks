import type { MutableRefObject } from 'react'
import { Painel } from './Painel'

interface Props {
  imagemRef: MutableRefObject<HTMLImageElement | null>
  temImagem: boolean
  ligado: boolean
  titulo?: string
  alt?: string
  textoVazio?: string
  etiqueta?: string | null
}

// Painel de imagem ao vivo, partilhado pela vista RGB e pelo mapa de
// profundidade. Os frames são escritos diretamente no <img> pelo hook, por
// isso o ref é obrigatório e o estado React só guarda "tem imagem".
export function CamaraPainel({
  imagemRef,
  temImagem,
  ligado,
  titulo = 'Câmara ZED — Vista RGB',
  alt = 'Vista RGB da câmara ZED',
  textoVazio = 'Sem imagem da câmara',
  etiqueta = '30 FPS',
}: Props) {
  return (
    <Painel
      titulo={titulo}
      semEspaco
      acao={etiqueta ? <span className="etiqueta-tecnica">{etiqueta}</span> : undefined}
    >
      <div className="camara">
        <img ref={imagemRef} alt={alt} className="camara-imagem" />
        <span className={`selo-live ${ligado ? '' : 'selo-live--off'}`}>
          <span className="selo-ponto" aria-hidden="true" />
          {ligado ? 'Live' : 'desligado'}
        </span>
        {temImagem ? null : <div className="camara-vazio">{textoVazio}</div>}
      </div>
    </Painel>
  )
}
