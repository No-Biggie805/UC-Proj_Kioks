import type { ReactNode } from 'react'

interface Props {
  titulo: string
  acao?: ReactNode
  children: ReactNode
  className?: string
  semEspaco?: boolean
}

export function Painel({ titulo, acao, children, className, semEspaco }: Props) {
  return (
    <section className={`painel ${className ?? ''}`}>
      <header className="painel-topo">
        <h2>{titulo}</h2>
        {acao}
      </header>
      <div className={`painel-corpo ${semEspaco ? 'painel-corpo--sem-espaco' : ''}`}>{children}</div>
    </section>
  )
}

export function PorImplementar({ nota }: { nota?: string }) {
  return (
    <div className="por-implementar">
      <span>por implementar</span>
      {nota ? <small>{nota}</small> : null}
    </div>
  )
}
