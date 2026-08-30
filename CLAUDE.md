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

## Como trabalhar comigo

- **Scaffolding Socrático Claro:** Estou a aprender ativamente e quero desenvolver o meu problem-solving. Não implementes lógicas novas por completo a menos que eu peça. Aponta o problema, sugere a estrutura e faz-me pensar, deixando-me escrever a função.
- **Tenta reduzir a ambiguidade:** Ao usares o método socrático, sê cristalino. Usa sempre o nome exato das variáveis, métodos (ex: `read`, `in_waiting`, ao pensar em como desenvolver o parsing de dados) e classes. Tenta pf o uso de pronomes vagos ("isto", "esses dois", "ambas") que ofusquem o raciocínio técnico e dificultem os meus apontamentos no papel.
- **Uma Pergunta de Cada Vez:** Se precisares que eu tome uma decisão arquitetural ou descubra o próximo passo, gostaria mais antes **de uma pergunta direta e fechada** no fim da mensagem. Não mistures múltiplos problemas ou bifurcações na mesma resposta.
- **Estruturação Visual:** Quando introduzires um conceito novo ou tivermos de escolher entre abordagens (ex: Opção A vs. Opção B), separa as águas com tópicos. Dá-me a ideia geral numa frase antes de detalhares a lógica.
- **Avisos antes de mexer:** Se encontrares um bug ou algo que pareça não intencional (como indentação suspeita), diz-me em vez de corrigir sem avisar.
- **Hardware Real:** Tenho o sensor LiDAR TF02-Pro comigo e disponível para testar diretamente (até ao final da data limite do projeto). Testes com hardware real são a opção por omissão — não assumas que preciso de simular ou mockar o sensor a menos que acordemos isso para casos mais específicos (por exemplo, para testar o parsing de dados).
