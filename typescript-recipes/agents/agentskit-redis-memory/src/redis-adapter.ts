import type { RedisClientAdapter } from '@agentskit/memory'
import { createClient } from 'redis'

export interface ConnectedRedis {
  adapter: RedisClientAdapter
  close: () => Promise<void>
}

export async function connectRedis(url: string): Promise<ConnectedRedis> {
  const client = createClient({ url })
  await client.connect()

  return {
    adapter: {
      get: key => client.get(key),
      async set(key, value) {
        await client.set(key, value)
      },
      async del(key) {
        const keys = Array.isArray(key) ? key : [key]
        if (keys.length > 0) await client.del(keys)
      },
      keys: pattern => client.keys(pattern),
      async disconnect() {
        await client.close()
      },
      call: (command, ...args) => client.sendCommand([command, ...args.map(String)]),
    },
    close: async () => {
      await client.close()
    },
  }
}
