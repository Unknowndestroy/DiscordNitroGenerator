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
    webhook_url = "WEBHOOKHERE"
    data = {
        "content": f"Generated Nitro code: {url}"
    }
    async with session.post(webhook_url, json=data) as response:
        return response.status == 204

async def write_to_file(code):
    with open("validcodes.txt", "a") as file:
        file.write(code + "\n")

async def worker(session):
    while True:  # Run indefinitely
        code = generate_code(16)
        url = construct_gift_url(code)
        valid_url = await verify_link(session, url)
        if valid_url:
            print(f"Generated valid code URL: {valid_url}")
            await write_to_file(valid_url)
            if await send_code_to_discord(session, valid_url):
                print(f"Successfully sent code: {valid_url}")
        else:
            print(f"Invalid URL: {url}")  # Log invalid URLs
        # Removed delay to allow continuous processing

async def main():
    # Create or open the validcodes.txt file at the start
    open("validcodes.txt", "a").close()  # This creates the file if it doesn't exist

    start_time = time.time()
    max_workers = 100  # Number of workers

    async with aiohttp.ClientSession() as session:
        tasks = [worker(session) for _ in range(max_workers)]
        await asyncio.gather(*tasks)

    print("Completed all tasks.")
    print(f"Time taken: {time.time() - start_time} seconds")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
