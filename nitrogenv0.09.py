import random
import string
import asyncio
import aiohttp
import time

# Set the event loop policy for Windows
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def generate_code(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def construct_gift_url(code):
    return f"https://discord.gift/{code}"

async def verify_link(session, url):
    try:
        async with session.head(url, timeout=1) as response:
            return url if response.status == 200 else None
    except Exception:
        return None

async def send_code_to_discord(session, url):
    webhook_url = "https://discord.com/api/webhooks/1282114090424340510/KpIIQPnttws77JYyjlHu86S2x2bAWlbfSEGqgUhtPUa7EY6CKXFg9_bya0vbSwfVQMiz"
    data = {
        "content": f"Generated Nitro code: {url}"
    }
    async with session.post(webhook_url, json=data) as response:
        return response.status == 204

async def write_to_file(file, code):
    file.write(code + "\n")

async def worker(session, file):
    while True:  # Run indefinitely
        code = generate_code(16)
        url = construct_gift_url(code)
        valid_url = await verify_link(session, url)
        if valid_url:
            print(f"Generated valid code URL: {valid_url}")
            await write_to_file(file, valid_url)  # Write directly to the open file
            if await send_code_to_discord(session, valid_url):
                print(f"Successfully sent code: {valid_url}")
        # Log only a sample of invalid URLs to reduce logging overhead
        elif random.random() < 0.01:  # Log 1% of invalid URLs
            print(f"Invalid URL: {url}")

async def main():
    # Create or open the validcodes.txt file at the start
    with open("validcodes.txt", "a") as file:
        start_time = time.time()
        max_workers = 200  # Increased number of workers for more concurrency

        async with aiohttp.ClientSession() as session:
            tasks = [worker(session, file) for _ in range(max_workers)]
            await asyncio.gather(*tasks)

    print("Completed all tasks.")
    print(f"Time taken: {time.time() - start_time} seconds")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
