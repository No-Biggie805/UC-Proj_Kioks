# UC-Proj_Kioks

Quiosque interativo com sensor LiDAR TF02-Pro. O sensor mede a
distância a que uma pessoa/objeto está, e a aplicação mostra em tempo
real a distância, velocidade e aceleração num gráfico, com um
cronómetro para medir tentativas.

Este repositório tem duas implementações:

- `python_implement/` — versão em Python (Tkinter + matplotlib) — **em uso**
- `C_implement/` — versão em C, fora do âmbito atual

## Setup

```bash
pip install -r requirements.txt
```

Confirma a porta série do sensor antes de correr (por omissão é
`/dev/ttyUSB0`, ver `TF02_pro.py`).

## Uso

```bash
python python_implement/window.py
```

## Estrutura

| Ficheiro | Responsabilidade |
|---|---|
| `window.py` | GUI principal, gráficos em tempo real |
| `StopWatch.py` | Cronómetro (classe `StopWatch`) |
| `TF02_pro.py` | Leitura e parsing do sensor LiDAR TF02-Pro |
| `TF02-pro-templates.py` | Rascunhos/histórico de tentativas anteriores (comentado) |

## Notas conhecidas

- Ver `CLAUDE.md` para o estado atual e pontos a rever antes de mexer no código.
