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
    user = message.from_user
    welcome_text = f"""
👋 Hola {user.mention} soy un bot de ejemplo de Levo.
🙂Usa /help para ver que puedo hacer en esto momentos de desarrollo.
    """
    await message.reply_text(welcome_text)
    
@app.on_message(filters.command("help"))
async def command_help(Client, message: Message):
    help_text = """
😁 En esto momentos estoy en desarrollo, solamente puedes usar

**Commandos**
/start - Comenzar 
/info - ver el id tuyo (en desarrollo)
    """
    await message.reply_text(help_text)
    
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