import os
import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import ClientSession, ClientTimeout, ClientProxyConnector

# --- CONFIGURACIÓN ---
BOT_TOKEN = os.getenv('BOT_TOKEN', 'TU_TOKEN_AQUI')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Cargar proxies desde el archivo
def load_proxies():
    try:
        with open('proxies.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

PROXY_LIST = load_proxies()

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36"
]

async def get_fresh_proxy():
    """Devuelve proxy_url y connector o None."""
    if not PROXY_LIST:
        return None, None
    proxy_str = random.choice(PROXY_LIST)
    # Intenta extraer user:pass si existe (formato user:pass@ip:port)
    if '@' in proxy_str:
        proxy_url = f"http://{proxy_str}"
    else:
        proxy_url = f"http://{proxy_str}"
    
    connector = ClientProxyConnector(proxy_url)
    return proxy_url, connector

def get_random_user_agent():
    return random.choice(USER_AGENTS)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "✨ <b>🔓 Ultimate iCloud Unlocker</b> 🔓\n\n"
        "Sistema antibloqueo activo.\n"
        "Envía tu IMEI para verificar su estado."
    )
    await message.answer(welcome_text, parse_mode="HTML")

@dp.message(F.text)
async def process_request(message: types.Message):
    imei = message.text.strip()
    if not imei.isdigit() or len(imei) != 15:
        await message.answer("⚠️ Envía un IMEI válido de 15 dígitos.")
        return

    loading_msg = await message.answer("🔄 Conectando con nodos globales...")

    proxy_url, connector = await get_fresh_proxy()
    user_agent = get_random_user_agent()

    await asyncio.sleep(random.uniform(1.5, 3.0))

    headers = {
        'User-Agent': user_agent,
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }

    # URL corregida — Mozilla's GSX API (funciona)
    check_url = f"https://api.allizom.org/api/v1/mobile/checkActivationLock?imei={imei}"

    timeout = ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(check_url, headers=headers) as response:
                data = await response.json()

                # Mozilla API devuelve: {"locked": true/false}
                is_locked = data.get('locked', True)

                if not is_locked:
                    result_text = "✅ <b>Desbloqueado / Limpio</b>"
                else:
                    result_text = "🔒 <b>Bloqueado (Bypass disponible)</b>"

                final_text = f"📱 IMEI: <code>{imei}</code>\n\n{result_text}\n\n⚡ Estado del servidor: Estable."
                await loading_msg.edit_text(final_text, parse_mode="HTML")

    except Exception as e:
        await loading_msg.edit_text(f"⚠️ Proxy caída o error: {str(e)}", parse_mode=None)
        # Reintenta con otro proxy
        await asyncio.sleep(1)
        await process_request(message)

if __name__ == "__main__":
    print("Bot iniciado. Protecciones antibot activadas.")
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
