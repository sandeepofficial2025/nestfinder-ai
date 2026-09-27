import os
import time
import asyncio
from playwright.async_api import async_playwright

async def record_demo():
    os.makedirs("recordings", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir="recordings/",
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("Navigating to NestFinder AI frontend...")
        await page.goto("http://localhost:8080")
        await page.wait_for_timeout(2000)

        # 1. First prompt: Database Lookup / Search listings
        prompt1 = "Search 2BR apartment listings in SoHo under $4000"
        print(f"Typing prompt 1: {prompt1}")
        await page.type("#input", prompt1, delay=45)
        await page.wait_for_timeout(500)
        await page.click("#form button")

        # Wait for agent response
        print("Waiting for response 1...")
        await page.wait_for_selector(".msg.agent", timeout=15000)
        await page.wait_for_timeout(6000)

        # 2. Second, richer prompt: Image generation tool call & rendering
        prompt2 = "Generate a visual rendering of a modern sunlit living room in SoHo with exposed brick"
        print(f"Typing prompt 2: {prompt2}")
        await page.type("#input", prompt2, delay=45)
        await page.wait_for_timeout(500)
        await page.click("#form button")

        # Wait for image rendering response
        print("Waiting for response 2...")
        await page.wait_for_timeout(10000)
        await page.wait_for_timeout(4000)

        video_path = await page.video.path()
        print(f"Recorded video saved to: {video_path}")
        await context.close()
        await browser.close()
        return video_path

if __name__ == "__main__":
    asyncio.run(record_demo())
