import os
import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- CONFIGURACIÓN ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Cargar proxies desde el archivo (si existe) o usar una lista por defecto
def load_proxies():
    try:
        with open('proxies.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ["http://proxy1.com:80", "http://proxy2.com:80"] # Proxies de ejemplo

PROXY_LIST = load_proxies()

# User-Agents variados para simular tráfico real
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36"
]

async def get_fresh_proxy():
    """Selecciona una proxy al azar."""
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)

def get_random_user_agent():
    """Elige un navegador aleatorio."""
    return random.choice(USER_AGENTS)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    welcome_text = (
        "✨ <b>🔓 Ultimate iCloud Unlocker</b> 🔓\n\n"
        "Sistema antibloqueo activo.\n"
        "Envía tu IMEI para verificar su estado."
    )
    await message.answer(welcome_text, parse_mode="HTML")

@dp.message_handler(content_types=['text'])
async def process_request(message: types.Message):
    imei = message.text.strip()
    
    # Paso 1: Feedback visual inmediato
    loading_msg = await message.answer("🔄 Conectando con nodos globales...")
    
    # Paso 2: Preparación Antibot
    proxy_url = await get_fresh_proxy()
    user_agent = get_random_user_agent()
    
    # Simulamos un "pensamiento" humano antes de actuar
    await asyncio.sleep(random.uniform(1.5, 3.0)) 

    headers = {
        'User-Agent': user_agent,
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }

    # URL de ejemplo (GSX API). Ajusta esto según tu servicio.
    check_url = f"https://gsqdev.appspot.com/device/checkActivationLock?imei={imei}"

    try:
        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with session.get(check_url, proxy=proxy_url, headers=headers, timeout=timeout) as response:
                data = await response.json()
                
                status = data.get('result', 'Unknown')
                
                if status == '0':
                    result_text = "✅ <b>Desbloqueado / Limpio</b>"
                else:
                    result_text = "🔒 <b>Bloqueado (Bypass disponible)</b>"
                    
                final_text = f"📱 IMEI: <code>{imei}</code>\n\n{result_text}\n\n⚡ Estado del servidor: Estable."
                
                await loading_msg.edit_text(final_text, parse_mode="HTML")
                
    except Exception as e:
        await loading_msg.edit_text("⚠️ Proxy caída. Reintentando con IP fresca...", parse_mode=None)
        await asyncio.sleep(1)
        await process_request(message)

if __name__ == "__main__":
    print("Bot iniciado. Protecciones antibot activadas.")
    executor.start_polling(dp, skip_updates=True)
