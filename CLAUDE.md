# Projeto: UC-Proj_Kioks

Quiosque com sensor LiDAR TF02-Pro: lê distância por porta série, deteta
movimento/passagem, e mostra distância/velocidade/aceleração em tempo
real numa GUI Tkinter + matplotlib. Cronometra tentativas com um
stopwatch embutido na GUI.

Ignora sempre a pasta `C_implement/` — não faz parte deste trabalho.

## Comandos

- `pip install -r requirements.txt`: instalar dependências
- `python python_implement/window.py`: correr a aplicação (precisa do sensor ligado)
- `pytest`: correr testes (ver "Testes" abaixo)
- `ruff check python_implement`: lint

## Arquitetura

- `python_implement/window.py`: GUI principal (classe `App`). Junta o
  StopWatch e o MotorDados, desenha os 3 gráficos (distância, velocidade,
  aceleração) com blitting para performance.
- `python_implement/StopWatch.py`: classe `StopWatch(Frame)` — Start/Stop/Reset
  de um cronómetro Tkinter.
- `python_implement/TF02_pro.py`: classe `MotorDados` — lê o sensor por
  série numa thread de fundo, faz parsing do protocolo TF02-Pro (pacotes
  de 9 bytes, cabeçalho `\x59\x59`, checksum no último byte).
- `python_implement/TF02-pro-templates.py`: rascunho histórico com
  versões anteriores da leitura do sensor, tudo comentado. Não é código
  ativo — só para referência/histórico de tentativas.

## Estado atual / cuidados

- `window.py` já tem comentários deixados a meio de tarefas em curso
  (ex.: `_configurar_eixo`, blitting dos 3 eixos). Lê os comentários
  existentes antes de assumir que algo está por fazer — pode já estar
  decidido.
- `TF02_pro.py`: revê a indentação do `time.sleep(0.01)` no fim do
  `_read_loop` antes de mexer nessa função — confirma que está a fazer
  o que o comentário ao lado diz.
- `__pycache__/` não devia estar no repositório — já não vai ser gerado
  para o controlo de versões (ver `.gitignore`), mas convém removê-lo
  do histórico do git com `git rm -r --cached python_implement/__pycache__`.

## Como trabalhar comigo

- Estou a aprender ativamente — explica a abordagem antes de codificar.
- Não implementes lógica nova por completo a menos que eu peça
  explicitamente. Aponta o problema/objetivo, sugere a estrutura, e
  deixa-me escrever a função.
- Se encontrares um bug ou algo que pareça não intencional (como
  indentação suspeita), diz-me em vez de corrigir sem avisar.
- Não tenho hardware sempre disponível para testar — quando fizer
  sentido, sugere testes que não dependam do sensor físico (ex.: dar
  bytes falsos ao parser do `TF02_pro.py` em vez de precisar da porta
  série real).
