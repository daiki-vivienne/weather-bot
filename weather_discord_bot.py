import discord
from discord.ext import commands
import asyncio
from playwright.async_api import async_playwright
from city_urls import CITY_URLS

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1378337014646308964  # 送信先チャンネルID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'ログイン成功: {bot.user}')

@bot.command(name="天気")
async def weather(ctx, *, city: str):
    # スペースと「県」「市」などを取り除く
    city = city.strip().replace("　", "").replace("県", "").replace("市", "")

    if city in CITY_URLS:
        await ctx.send(f"🔍 {city}の天気を取得中だよ...ちょっと待ってね！☁️")
        await send_weather_screenshot(ctx, CITY_URLS[city], city)
    else:
        await ctx.send("ごめん、その地域はまだ対応してないよ！🗾💦")
from discord.ext.commands import MissingRequiredArgument

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        if error.param.name == 'city':
            await ctx.send("ごめん、地域名を教えてね！例: `!天気 東京`")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("ごめん、そのコマンドはわからないよ！")
    else:
        raise error
    
async def send_weather_screenshot(ctx, url, city):
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("チャンネルが見つかりませんでした")
        await ctx.send("エラー: チャンネルが見つかりませんでした")
        return

    screenshot_path = f"{city}_weather.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state('load')
        await asyncio.sleep(2)

        try:
            await page.wait_for_selector("section.section-wrap", timeout=10000)
            weather_element = await page.query_selector("section.section-wrap")
            await weather_element.screenshot(path=screenshot_path)
        except Exception as e:
            print(f"天気の要素が見つかりませんでした: {e}")
            await page.screenshot(path=screenshot_path, full_page=True)

        await browser.close()

    # ② 天気画像と一緒にコメントを送信
    await channel.send(content=f"📍 {city}の天気だよ！", file=discord.File(screenshot_path))

bot.run(TOKEN)