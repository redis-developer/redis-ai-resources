# Redis-backed agent memory with AgentsKit

This TypeScript recipe uses [`@agentskit/memory`](https://www.npmjs.com/package/@agentskit/memory)
to persist complete agent conversation snapshots in Redis.

It demonstrates:

- isolated memory per conversation;
- message and date serialization through the AgentsKit `ChatMemory` contract;
- replacement of a complete conversation snapshot;
- native Redis expiration refreshed on every save;
- explicit conversation deletion.

The memory contract is independent of the model or agent runtime, so the same Redis
backend can be used with any provider.

## Run

Start Redis:

```bash
docker run --rm -p 6379:6379 redis:8-alpine
```

Then run the recipe:

```bash
npm install
npm run demo
```

Set `REDIS_URL` to use Redis Cloud or another Redis deployment.

## Validate

```bash
npm test
npm run check
```

The unit tests are credential-free. They verify session isolation, replacement,
expiration, and deletion. The demo exercises the same behavior against a live Redis
server.
