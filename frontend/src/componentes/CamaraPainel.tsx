import type { MutableRefObject } from 'react'
import { Painel } from './Painel'

interface Props {
  imagemRef: MutableRefObject<HTMLImageElement | null>
  temImagem: boolean
  ligado: boolean
}

export function CamaraPainel({ imagemRef, temImagem, ligado }: Props) {
  return (
    <Painel
      titulo="Câmara ZED — Vista RGB"
      semEspaco
      acao={<span className="etiqueta-tecnica">30 FPS</span>}
    >
      <div className="camara">
        <img ref={imagemRef} alt="Vista RGB da câmara ZED" className="camara-imagem" />
        <span className={`selo-live ${ligado ? '' : 'selo-live--off'}`}>
          <span className="selo-ponto" aria-hidden="true" />
          {ligado ? 'Live' : 'desligado'}
        </span>
        {temImagem ? null : <div className="camara-vazio">Sem imagem da câmara</div>}
      </div>
    </Painel>
  )
}
