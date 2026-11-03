# Ambiente de desenvolvimento (Base44)

Notas de setup que não se leem nos manifestos. Complementam o `CLAUDE.md` — o
estilo de trabalho descrito lá mantém-se.

## Como correr

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

- Página em http://localhost:3000 (Vite em modo dev na porta 5173 dentro do
  contentor, código montado a partir do repositório).
- `npm ci` corre no arranque do serviço, a partir de `frontend/package-lock.json`;
  `node_modules` fica num volume próprio, fora do bind mount. Se o lockfile
  mudar, reiniciar o serviço.
- Só o `frontend/` corre aqui. `python_implement/servidor.py` precisa da câmara
  ZED e do sensor LiDAR, por isso é lançado na máquina do hardware.

Verificação:

```bash
docker compose -f docker-compose.base44.yml exec -T web npm run typecheck
docker compose -f docker-compose.base44.yml exec -T web npm run build
```

## Servidor WebSocket

- Contrato em `frontend/src/protocolo.ts`; a página liga-se a
  `ws://localhost:8000/ws` e nunca calcula valores — só desenha o que recebe.
- Sem o servidor a correr, a página mostra legitimamente `desligado` e tenta
  reconectar com espera crescente até 5 s. Os botões só ativam depois de chegar
  uma mensagem `estado`.
- `VITE_WS_URL` substitui o endereço do servidor. No sandbox usa-se
  `wss://3000-$BASE44_PUBLIC_HOST_SUFFIX/ws`: o proxy `/ws` do Vite (ver
  `frontend/vite.config.ts`) encaminha para `127.0.0.1:8000` na mesma origem.
- Painéis sem dados no protocolo (mapa de profundidade, pose 3D, vista lateral,
  trajetória, passos/cadência/qualidade) ficam visíveis com "por implementar".

## Overrides do sandbox

- `frontend/vite.config.ts` só acrescenta `server.allowedHosts` (domínio do
  sandbox e origem do preview) quando `BASE44_PREVIEW_MODE === '1'`; sem a flag
  fica `undefined` e o Vite usa o comportamento por omissão.
- `BASE44_PREVIEW_MODE`, `BASE44_PUBLIC_HOST_SUFFIX`, `BASE44_SANDBOX_HOST_DOMAIN`
  e `__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS` são passados ao serviço `web` sem
  valor fixo, a partir do ambiente.
