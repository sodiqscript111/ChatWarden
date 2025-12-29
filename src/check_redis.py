import asyncio
import redis.asyncio as r

async def main():
    try:
        url = 'redis://127.0.0.1:6379/0'
        print(f"Connecting to {url}...")
        client = r.from_url(url, encoding="utf-8", decode_responses=True, socket_connect_timeout=2)
        await client.ping()
        print("REDIS_SUCCESS")
    except Exception as e:
        print(f"REDIS_FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(main())
