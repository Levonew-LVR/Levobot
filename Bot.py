from pyrogram import Client, filters
from pyrogram.types import Message
import os 
from dotenv import load_dotenv

# = CONFIGURACION DEL BOT =
load_dotenv() # archivo .env

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "Levobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Manejador para el comando /start
@app.on_message(filters.command("start"))
async def start_command(Client, message: Message):
    welcome_text = f"""
Hola soy un bot de ejemplo de Levo.
    """
    await message.reply_text(welcome_text)
    
# ===== iniciar el bot ===
if __name__ == "__main___":
    print("iniciando Bot...")
    app.run() # Corre el bot
    print("Bot Dectenido")