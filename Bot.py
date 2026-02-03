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

# Variable global

Admin = [7370035898]

# Manejador para el comando /start
@app.on_message(filters.command("start"))
async def start_command(Client, message: Message):
    welcome_text = f"""
👋 Hola soy un bot de ejemplo de Levo.
🙂Usa /help para ver que puedo hacer en esto momentos de desarrollo.
    """
    await message.reply_text(welcome_text)
    
@app.on_message(filters.command("help"))
async def command_help(Client, message: Message):
    help_text = """
😁 En esto momentos estoy en desarrollo, solamente puedes usar

**Commandos**
/start - Comenzar 
/delete - elimmina el mensaje
/user - ver el id tuyo (en desarrollo)
    """
    await message.reply_text(help_text)
    
@app.on_message(filters.photo)
async def handle_photo(Client, message: Message):
    await message.reply_text("He recibido una foto")

@app.on_message(filters.command("delete")  & filters.reply)
async def delete_message(Client, message: Message):
    if message.from_user.id not in Admin:
        await message.reply("😕 No eres admin para usar el command")
        return
    try:
        await message.reply_to_message.delete() # Borra el mensaje que respondio 
        await message.delete() # Borra el commando 
        comfir = await message.reply_text("Mensaje eliminado...") # Confirma el mensje
        await asyncio.sleep(2) # espera 2 segundos para eliminar un message
        await comfir = message.delete()
    except Exception as e:
        await message.reply(f"Error al eliminar: {e}")

        
@app.on_message(filters.command("user"))
async def command_info_user(Client, message: Message):
    user = message.reply_to_message.from_user
    Message_info = (
f"Detalles del usario {user.mention}\n\n"
f"Tu id es {user.id}\n"
f"Tu Nombre de usario es @{user.username}\n"
f"Nombre y appellido {user.first_name} {user.last_name}\n"
f"lang (Lenguaje) {user.language_code}"
    )
    await message.reply_text(Message_info)
    
# ===== iniciar el bot ===
if __name__ == "__main__":
    print("iniciando Bot...")
    app.run() # Corre el bot
    print("Bot Dectenido")