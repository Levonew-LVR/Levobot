from pyrogram import Client, filters
from pyrogram.types import Message, Photo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from pyrogram.errors import PeerIdInvalid, UsernameInvalid, UsernameNotOccupied
import os
import asyncio
import logging
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

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


ADMINS = [7370035898,6438282268, 970720634, 5702506445, 5195985707, 7400531692, 6571365927]

# Manejador para el comando /start
@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user = message.from_user
    welcome_text = f"""
👋 Hola {user.first_name} {user.last_name}
🐰 Soy un simple conejito de prueba.

Usa /help para ver que puedo hacer.
    """
    await message.reply_text(welcome_text)
    
@app.on_message(filters.command("help"))
async def command_help(client, message: Message):
    help_text = """
😁 En esto momento mi dueño (🐰Levo) me está desarrollando.

**Commandos Disponible**
/start - Comenzar 
/del - Elimina un mensaje respondiendo un chat (admin)
/user - Ver información 
/report - para reportar un Error en espesifico(test)
    """
    await message.reply_text(help_text)
 
# handle_photo para recibir una foto   
@app.on_message(filters.photo)
async def handle_photo(client, message: Message):
    await message.reply_text("He recibido una foto")

# Comando para Eliminar un mensaje respondido en un chats .delete
@app.on_message(filters.command("del")  & filters.reply)
async def delete_message(client, message: Message):
    if message.from_user.id not in ADMINS:
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
async def command_info_user(client, message: Message):
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
📧 Usuario @{user.username}
👤 {user.first_name} {user.last_name}
🌐 Lang "{user.language_code or 'desconocido'}"
🤖 Bot "{'Si' if user.is_bot else 'No'}"
💎 Premium "{'Si' if user.is_premium else 'No'}"

**Como Utilizar**
/user  - Muestra tu información(sin argumentos)
/user @username - Muestra info de un usuario por su @
/user 12345678 - Muestra info de un usuario por ID
/user [Respondiendo un  mensaje de un user o bot en grupos o chat pv] - Muestra info del usuario respondido
    """
    await message.reply_text(user_info)

# Conectamos a la variable con int
ADMIN_CHAT = 7370035898,6438282268, 970720634, 5702506445, 5195985707, 7400531692, 6571365927

# Commando para reportar errores con message.forward()
@app.on_message(filters.command("report"))
async def comand_forward(client, message: Message):
   
    # Renvia el mensaje respondido
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "Sin motivo especificado"
    
    # Enviar reporte general (sin responder message)
    if not message.reply_to_message:
        await enviar_reporte_general(client, message, reason)
        return

    try:
        # Obtener motivo si se proporcionó
        mensaje_reportado = message.reply_to_message

        await mensaje_reportado.forward(admin_chat_id)

        # Información
        user = message.from_user
        user_repor = mensaje_reportado.from_user
        chat = message.chat

        # Para generar el Enlace en caso de ser supergruo o canal
        message_link = ""
        if chat.id < 0:  # Es un grupo/canal (ID negativo)
            chat_id_str = str(chat.id)[4:]  # Quitar el -100
            message_link = f"https://t.me/c/{chat_id_str}/{message.reply_to_message.id})"
            
        teclado = InlineKeyboardMarkup([
            [
            InlineKeyboardButton("Ver Mensaje", url=f"{message_link}")
            ]
        ])
        
        text_report = f"""
👤 **Reporte del Usarios**
Motivo: {reason}

**Info user**
Usario: {user.mention} ID {user.id}
Usarios Reportado: {user_repor.mention} ID {user_repor.id}
chat: {message.chat.title or 'Chat pv'} {chat.id}
fecha: {message.date.strftime('%d/%m/%Y %H:%M')}
        """
    
        await client.send_message(ADMIN_CHAT, text_report, reply_markup=teclado) # esta funcion es para compartir tanto la Información del mensaje y Usario.
        
        await message.reply(
            f"🙂 Tu reporte ha sido enviado a los admin (será atendido en el grupo de [soporte](https://t.me/grupcompresize))",
            parse_mode=ParseMode.MARKDOWN
        ) # esto va a salir tanto en chat pv y group
        
        logger.info(
            f"Reporte enviado por {user.id}"
        )
    except Exception as e:
        logger.error(f"Error /report: {e}")
        await message.reply(f"Error al enviar el Mensaje.\n\n Usa /report mensjae - para reportar \n\nmotivo:{str(e)[:100]}") # Esto es para Saber el error del mensaje

# Este es para recibir el motivo    
async def enviar_reporte_general(client, message, reason):
    """Enviar reporte general (sin mensaje específico)"""
    try:
        reporter = message.from_user
        chat = message.chat
        
        teclado = InlineKeyboardMarkup([
            [
            InlineKeyboardButton("Ver Mensaje", url=f"{message_link}")
            ]
        ])
        
        text_report = f"""
👤 **Reporte del Usuario**
Motivo: {reason}

**Info user**
Usuario: {reporter.mention if reporter.mention else reporter.first_name} ID {reporter.id}
Chat: {chat.title or 'Chat privado'} (ID: {chat.id})
Fecha: {message.date.strftime('%d/%m/%Y %H:%M')}
        """
        
        await client.send_message(admin_chat_id, text_report, reply_markup=teclado)
        
        # Confirmación
        await message.reply(
            f"🙂 Tu reporte general ha sido enviado a los admin (será atendido en el grupo de [soporte](https://t.me/grupcompresize))",
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Reporte general enviado por {reporter.id}")

    except Exception as e:
        logger.error(f"Error reporte general: {e}")
        await message.reply(f"Error al enviar el mensaje:\n\nUsa /report selecionando el mensjae y el Motivo\n\n motivo:{str(e)[:100]}")

# ===== iniciar el bot ===
if __name__ == "__main__":
    print("iniciando Bot...")
    app.run() # Corre el bot
    print("Bot Dectenido")