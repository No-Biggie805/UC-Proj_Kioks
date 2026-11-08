/**
 * Contrato com o servidor local (python_implement/servidor.py).
 * A página só desenha o que chega aqui — não calcula nenhuma grandeza.
 */

// Endereço do servidor, tal como no contrato. Só muda quando VITE_WS_URL é
// definido no ambiente (usado para servir a página no sandbox).
export const URL_SERVIDOR = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export type EstadoTentativa = 'parado' | 'a_gravar' | 'terminado'

export type EstadoLigacao = 'a_ligar' | 'ligada' | 'desligada'

export interface MensagemEstado {
  tipo: 'estado'
  estado_tentativa: EstadoTentativa
  zed_ligada: boolean
  sensor_ligado: boolean
  fase_atual: string | null
}

export interface MensagemCamara {
  tipo: 'camara'
  format: 'jpeg' | 'webp'
  imagem_base64: string
}

// Mesmo formato da câmara, mas com o mapa de profundidade já desenhado pelo
// servidor (~30 Hz). A página não calcula nada.
export interface MensagemCamaraProfundidade {
  tipo: 'camara_profundidade'
  format: 'jpeg' | 'webp'
  imagem_base64: string
}

export interface Amostra {
  t_s: number
  distancia_m: number
  velocidade: number
  aceleracao: number
}

export interface MensagemAmostra extends Amostra {
  tipo: 'lidar' | 'zed'
}

export interface MensagemResultadoFinal {
  tipo: 'resultado_final'
  tempo_total_s: number | null
  tempo_ida_s: number | null
  tempo_volta_s: number | null
  distancia_total_m: number | null
  velocidade_media: number | null
  velocidade_maxima: number | null
  turnaround_s: number | null
  passos: number | null
  execucao_valida: boolean | null
}

export type MensagemServidor =
  | MensagemEstado
  | MensagemCamara
  | MensagemCamaraProfundidade
  | MensagemAmostra
  | MensagemResultadoFinal

export type Comando =
  | { tipo: 'distancia_alvo'; distancia_alvo_m: number }
  | { tipo: 'iniciar' }
  | { tipo: 'terminar' }
  | { tipo: 'guardar_resultado' }

export interface Series {
  lidar: Amostra[]
  zed: Amostra[]
}

export type CampoGrafico = 'distancia_m' | 'velocidade' | 'aceleracao'
