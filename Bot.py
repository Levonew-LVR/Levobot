from pyrogram import Client, filters
from pyrogram.types import Message, Photo, Document 
import os
import asyncio
from pyrogram.errors import PeerIdInvalid, UsernameInvalid, UsernameNotOccupied
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
    user = message.from_user.
    welcome_text = f"""
👋 Hola {user.first_name and user.last_name}
🐰 Soy un simple conejito de prueba.

Usa /help para ver que puedo hacer.
    """
    await message.reply_text(welcome_text)
    
@app.on_message(filters.command("help"))
async def command_help(Client, message: Message):
    help_text = """
😁 En esto momento mi dueño (🐰Levo) me está desarrollando.

**Commandos Disponible**
/start - Comenzar 
/delete - Elimina un mensaje respondiendo un chat (admin)
/user - Ver información 
    """
    await message.reply_text(help_text)
 
# handle_photo para recibir una foto   
@app.on_message(filters.photo)
async def handle_photo(Client, message: Message):
    await message.reply_text("He recibido una foto")

# Comando para Eliminar un mensaje respondido en un chats
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
        await comfir.delete()
    except Exception as e:
        await message.reply(f"Error al eliminar: {e}")

# Command para ver la información del usuarios
@app.on_message(filters.command("user"))
async def command_info_user(Client, message: Message):
     # Comando con argumento (username o ID)
    if len(message.command) > 1:
        target = message.command[1]
        await get_user_by_argument(client, message, target)
    
    # Comando como respuesta a un mensaje
    elif message.reply_to_message:
        await get_replied_user_info(client, message)
    
    #  Comando sin argumentos (mostrar propia info)
    else:
        await get_self_user_info(client, message)

# def con la funcion de @user y id , del command
async def get_user_by_argument(client, message, target):
    try:
        # Intentar como ID numérico
        if target.isdigit() or (target.startswith('-') and target[1:].isdigit()):
            user_id = int(target)
            user = await client.get_users(user_id)
            await send_user_info(client, message, user, "por ID")
        
        # Intentar como username (con o sin @)
        elif target.startswith('@'):
            username = target[1:]  # Quitar el @
            user = await client.get_users(username)
            await send_user_info(client, message, user, "por username")
        
        else:
            # Intentar sin @
            user = await client.get_users(target)
            await send_user_info(client, message, user, "por username")
            
    except (PeerIdInvalid, UsernameInvalid, UsernameNotOccupied):
        await message.reply("No se encontró el usuario. Verifica el ID o username.")
    except Exception as e:
        await message.reply(f" Error: {e}")

# Def como respuesta al mensaje respondido del usario
async def get_replied_user_info(client, message):
    user = message.reply_to_message.from_user
    await send_user_info(client, message, user, "respondido")

# Envia la información del usario sin argumentos
async def get_self_user_info(client, message):
    user = message.from_user
    await send_user_info(client, message, user, "tú")

async def send_user_info(client, message, user, source=""):
    """Enviar información formateada del usuario"""
    # Determinar cómo se obtuvo el usuario
    source_text = f" (obtenido {source})" if source else ""

    user_info = f"""
**👤 Información del usuario**{source_text}

🆔 {user.id}
📧 Usuario @{user.username or 'no tiene'}
👤 Nombre y apellido {user.first_name and user.last_name or 'no tiene'}
🌐 Lang {user.language_code or 'desconocido'}
🤖 Bot {'Si' if user.is_bot else 'No'}
💎 Premium {'Si' if user.is_premium else 'No'}

**Como Utilizar**
/user  - Muestra tu información(sin argumentos)
/user @username - Muestra info de un usuario por su @
/user 12345678 - Muestra info de un usuario por ID
/user [Respondiendo un  mensaje de un user o bot en grupos o chat pv] - Muestra info del usuario respondido
    """
    await message.reply_text(user_info)
    
# ===== iniciar el bot ===
if __name__ == "__main__":
    print("iniciando Bot...")
    app.run() # Corre el bot
    print("Bot Dectenido")