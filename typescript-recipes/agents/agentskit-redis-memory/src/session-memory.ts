import type { ChatMemory } from '@agentskit/core'
import { redisChatMemory } from '@agentskit/memory'
import type { RedisClientAdapter } from '@agentskit/memory'

export interface SessionMemoryOptions {
  client: RedisClientAdapter
  sessionId: string
  ttlSeconds: number
  keyPrefix?: string
}

export function createSessionMemory(options: SessionMemoryOptions): ChatMemory {
  const keyPrefix = options.keyPrefix ?? 'agentskit:chat'
  const key = `${keyPrefix}:${options.sessionId}`
  const memory = redisChatMemory({
    url: '',
    client: options.client,
    conversationId: options.sessionId,
    keyPrefix,
  })

  return {
    load: memory.load,
    clear: memory.clear,
    async save(messages, operationOptions) {
      await memory.save(messages, operationOptions)
      operationOptions?.signal?.throwIfAborted()
      await options.client.call('EXPIRE', key, options.ttlSeconds)
    },
  }
}
