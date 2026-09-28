# %% [markdown]
# ![Redis](https://redis.io/wp-content/uploads/2024/04/Logotype.svg?auto=webp&quality=85,75&width=120)
#
# # Atomic Locking for Agent Tools with Redis
#
# ## Introduction
#
# AI agents that call tools with real side effects need a genuine safety guarantee against duplicate or concurrent execution. A common first approach — checking a SQLite table with a SELECT before an INSERT — looks safe but isn't: two near-simultaneous calls can both pass the check before either finishes writing, a real race condition.
#
# ## What We'll Build
#
# A minimal, atomic lock using Redis's `SET NX EX`, and direct proof it correctly blocks a duplicate call while one is in progress.

# %%
%pip install redis

# %% [markdown]
# ## The lock
#
# `SET key value NX EX seconds` sets a key only if it does not already exist, as one indivisible operation — and automatically expires it after the given number of seconds, so a crashed process can't leave a permanently stuck lock.

# %%
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def acquire_lock(key, ttl=60):
    return r.set(key, "processing", nx=True, ex=ttl)

def release_lock(key):
    r.delete(key)

# %% [markdown]
# ## Proof: acquire, block, release, re-acquire

# %%
print("First attempt:", acquire_lock("demo_task"))
print("Second attempt while held:", acquire_lock("demo_task"))
release_lock("demo_task")
print("Third attempt after release:", acquire_lock("demo_task"))