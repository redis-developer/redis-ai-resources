import type { Message } from '@agentskit/core'
import type { RedisClientAdapter } from '@agentskit/memory'
import { describe, expect, it } from 'vitest'
import { createSessionMemory } from '../src/session-memory.js'

function createFakeRedis(): {
  client: RedisClientAdapter
  values: Map<string, string>
  expirations: Map<string, number>
} {
  const values = new Map<string, string>()
  const expirations = new Map<string, number>()
  const client: RedisClientAdapter = {
    async get(key) {
      return values.get(key) ?? null
    },
    async set(key, value) {
      values.set(key, value)
    },
    async del(key) {
      for (const item of Array.isArray(key) ? key : [key]) values.delete(item)
    },
    async keys(pattern) {
      const prefix = pattern.replace('*', '')
      return [...values.keys()].filter(key => key.startsWith(prefix))
    },
    async disconnect() {},
    async call(command, ...args) {
      if (command === 'EXPIRE') expirations.set(String(args[0]), Number(args[1]))
      return 1
    },
  }
  return { client, values, expirations }
}

const message = (id: string, content: string): Message => ({
  id,
  role: 'user',
  content,
  status: 'complete',
  createdAt: new Date('2026-01-01T00:00:00Z'),
})

describe('AgentsKit Redis session memory', () => {
  it('isolates conversations and applies TTL on every save', async () => {
    const redis = createFakeRedis()
    const first = createSessionMemory({
      client: redis.client,
      sessionId: 'first',
      ttlSeconds: 60,
    })
    const second = createSessionMemory({
      client: redis.client,
      sessionId: 'second',
      ttlSeconds: 120,
    })

    await first.save([message('1', 'first session')])
    await second.save([message('2', 'second session')])

    expect((await first.load())[0]?.content).toBe('first session')
    expect((await second.load())[0]?.content).toBe('second session')
    expect(redis.expirations.get('agentskit:chat:first')).toBe(60)
    expect(redis.expirations.get('agentskit:chat:second')).toBe(120)
  })

  it('replaces the snapshot and clears it', async () => {
    const redis = createFakeRedis()
    const memory = createSessionMemory({
      client: redis.client,
      sessionId: 'replace',
      ttlSeconds: 60,
    })

    await memory.save([message('1', 'old')])
    await memory.save([message('2', 'new')])
    expect((await memory.load()).map(item => item.content)).toEqual(['new'])

    await memory.clear?.()
    expect(await memory.load()).toEqual([])
  })
})
