from pyrogram import Client, filters
from pyrogram.types import Message, Photo, Document 
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
    
@app.on_message(filters.photo)
async def handle_photo(Client, message: Message):
    await message.reply_text("He recibido una foto")
    
@app.on_message(filters.command("info"))
async def command_info_user(Client, message: Message):
    Message_info = f"""
Tu Id es {message.from_user.id}
    
    """
    await message.reply_text(Message_info)
    
# ===== iniciar el bot ===
if __name__ == "__main__":
    print("iniciando Bot...")
    app.run() # Corre el bot
    print("Bot Dectenido")