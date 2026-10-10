import type { Message } from '@agentskit/core'
import { connectRedis } from './redis-adapter.js'
import { createSessionMemory } from './session-memory.js'

const redisUrl = process.env.REDIS_URL ?? 'redis://localhost:6379'
const { adapter, close } = await connectRedis(redisUrl)

const message = (id: string, content: string): Message => ({
  id,
  role: 'user',
  content,
  status: 'complete',
  createdAt: new Date(),
})

try {
  const customerA = createSessionMemory({
    client: adapter,
    sessionId: 'customer-a',
    ttlSeconds: 300,
  })
  const customerB = createSessionMemory({
    client: adapter,
    sessionId: 'customer-b',
    ttlSeconds: 300,
  })

  await customerA.save([message('a-1', 'Remember that I prefer TypeScript.')])
  await customerB.save([message('b-1', 'Remember that I prefer Python.')])

  console.log({
    customerA: (await customerA.load()).map(item => item.content),
    customerB: (await customerB.load()).map(item => item.content),
  })

  await customerA.clear?.()
  console.log({ customerAAfterClear: await customerA.load() })
} finally {
  await close()
}
