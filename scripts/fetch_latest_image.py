import asyncio
import sys
import argparse
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def run(url):
    async with async_playwright() as p:
        user_data_dir = Path.home() / ".gemini_automation_profile"
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        downloads_path = Path.home() / "Downloads"
        
        # 定义任务完成事件
        task_completed = asyncio.Event()
        downloaded_file_path = None

        # 捕获下载文件
        async def handle_download(download):
            nonlocal downloaded_file_path
            save_path = downloads_path / download.suggested_filename
            await download.save_as(save_path)
            downloaded_file_path = str(save_path)
            print(f"✅ 【下载成功】已捕获并保存至: {save_path}")
            task_completed.set()

        page.on("download", handle_download)

        print(f"🚀 正在打开 URL: {url}")
        await page.goto(url, wait_until="domcontentloaded")

        # 寻找下载按钮
        print("⌛ 正在寻找页面上的最新图片下载按钮...")
        
        try:
            # 等待图片加载出来
            # 通常图片在 <img> 标签中，下载按钮是一个 aria-label 包含 "Download" 或 "下载" 的 button
            # 或者是 svg path 包含特定样式的按钮
            
            # 策略：寻找所有的下载按钮，取最后一个
            # 下载按钮的 aria-label 通常是 "Download image" 或 "下载图片"
            download_btns_selector = "button[aria-label*='Download'], button[aria-label*='下载']"
            
            # 等待至少一个下载按钮出现，超时 10 秒
            try:
                await page.wait_for_selector(download_btns_selector, timeout=10000)
            except:
                print("❌ 未能在页面上找到任何下载按钮，请确认图片是否已生成。")
                await browser.close()
                return None

            download_btns = await page.query_selector_all(download_btns_selector)
            if not download_btns:
                print("❌ 未找到下载按钮。")
                await browser.close()
                return None
            
            # 点击最后一个下载按钮（最新的图片）
            last_btn = download_btns[-1]
            print(f"✨ 找到 {len(download_btns)} 个下载按钮，点击最后一个...")
            await last_btn.click()

            # 等待下载完成
            await asyncio.wait_for(task_completed.wait(), timeout=30)
            
            await asyncio.sleep(2) # 留出一点点同步时间
            return downloaded_file_path

        except Exception as e:
            print(f"❌ 运行出错: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    try:
        result = asyncio.run(run(args.url))
        if result:
            print(f"RESULT_FILE_PATH:{result}")
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
