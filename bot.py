from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import random
import string
import logging
import os
import asyncio
import time
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv

# Carga las VARIABLES .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS").split(",")] # en el caso de una lista 
MONGO_URI = os.getenv("MONGO_URI")


#Id from channel
CANAL_PRIVADO_ID = -1002506012356 # mi canal

app = Client(
    "Moviestar",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Base de mongo
mongo = MongoClient(MONGO_URI)
db = mongo["moviestar"]

usuarios = db.usuarios
contenidos = db.contenidos
archivos_db = db.archivos

usuarios.create_index("user_id", unique=True)
contenidos.create_index("random_id", unique=True)
archivos_db.create_index("contenido_id")



# ====  VARIABLES GLOBALES =====
temp_data = {}



# HELPERS

# Def para dectetar admin
def es_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
    
# generar_id del link
def generar_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
# Funcion Para generar un enlace
def generar_link(random_id):
    return f"https://t.me/{app.me.username}?start=new_{random_id}"

# Funcion para linpiar , los procesos vacios
def limpiar_sesiones_viejas():
    current_time = time.time()
    to_delete = []
    for user_id, data in temp_data.items():
        if current_time - data.get("timestamp", 0) > 3600:  # 1 hora
            to_delete.append(user_id)
    for user_id in to_delete:
        del temp_data[user_id]
        

# Commando para Comezar
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user = message.from_user
    args = message.text.split()
    
    # Registrar usuario
    if not usuarios.find_one({"user_id": str(user.id)}):
        usuarios.insert_one({
            "user_id": str(user.id),
            "nombre": user.first_name,
            "fecha_registro": datetime.utcnow()
        })
    
    # Link
    if len(args) > 1 and args[1].startswith("new_"):
        random_id = args[1].replace("new_", "")
        contenido = contenidos.find_one({"random_id": random_id})

        if not contenido:
            return await message.reply("❌ Enlace no válido")

        archivos = list(
            archivos_db.find({"contenido_id": contenido["_id"]}).sort("orden", 1)
        )

        await message.reply(f"🎬 **{contenido['titulo']}**\nEnviando contenido...")

        for archivo in archivos:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=CANAL_PRIVADO_ID,
                    message_id=archivo["mensaje_id"]
                )
                await asyncio.sleep(1)
            except Exception as e:
                await message.reply(f"Error: {e}")
        return
    
    # Mensaje de Bienvenida a los admin.
    if message.from_user.id in ADMIN_IDS:
        user = message.from_user
        await message.reply(f"Bienvenido {user.first_name}\n\n😊, ¿Qué vamos a publicar hoy? 😉")
        return
    # Mensaje normal de inicio
    teclado_welcom = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Moviestar ⭐", url="https://t.me/MOVISTARTTV")]
        ])
    await message.reply(
        f"🎬 **Bienvenido {user.mention } a Moviestar** ⭐\n\n"
        f"Pusla /help para ver que puedo hacer😊\n"
        f"Unete al canal para ver tus pelicula y series favoritas🤩👇", reply_markup=teclado_welcom
    )

# ==== Comando de ayuda ====
@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    help_menu = """
**Commandos del bot**
    
Para usuarios
/start - Comenzar
/help - obtener ayuda
    
Para admin
/add - para agregar nuevo contenido
/end - para terminar
/cancel - para cancelar el procecso

    """
    await message.reply(help_menu)
    
# Comando para agragar un nuevo contendio
@app.on_message(filters.command("add") & filters.private)
async def add_content(client, message):
    if not es_admin(message.from_user.id):
        return await message.reply("😕No eres admin para utilizar este comnand")
        
    user_id = str(message.from_user.id)
     
    # Inicializar datos temporales
    temp_data[user_id] = {
        "estado": "esperando_titulo",
        "timestamp": time.time(),
        "tipo": None,
        "titulo": None,
        "archivos": [],
        "mensajes_temp": []
    }
    
    # Preguntar por el tipo
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Película", callback_data="tipo_pelicula")],
        [InlineKeyboardButton("Serie", callback_data="tipo_serie")]
    ])
    
    await message.reply(
        "**🎥 Agregar un nuevo Contenido**\n\n"
        "Por favor selecciona una opción 😊",
        reply_markup=keyboard
    )

# Callback para tipo de contenido
@app.on_callback_query(filters.regex("^tipo_"))
async def seleccionar_tipo(client, callback):
    user_id = str(callback.from_user.id)
    
    if user_id not in temp_data:
        await callback.answer("Sesión expirada. Usa /add nuevamente")
        return
    
    tipo = callback.data.replace("tipo_", "")
    temp_data[user_id]["tipo"] = tipo
    temp_data[user_id]["estado"] = "esperando_titulo"
    
    tipo_texto = "película" if tipo == "pelicula" else "serie"
    
    await callback.message.edit(
        f"Tipo seleccionado: **{tipo_texto.upper()}**\n\n"
        f"Ahora envía el título de la {tipo_texto}:\n"
        f"Ejemplo: 'Avengers Endgame' o 'Stranger Things Temporada 1'"
    )
    await callback.answer()

# Manejar mensajes para que Funcioe
@app.on_message(
    filters.private
    & filters.user(ADMIN_IDS)
    & ~filters.command(["end", "cancel", "add", "help", "start"])
    & ~filters.document   
)
async def procesar_contenido(client, message):
    user_id = str(message.from_user.id)
    
    if user_id not in temp_data:
        return
    
    estado = temp_data[user_id]["estado"]
    
    # Si estamos esperando el título
    if estado == "esperando_titulo" and not message.command:
        titulo = message.text.strip()
        temp_data[user_id]["titulo"] = titulo
        temp_data[user_id]["estado"] = "subiendo_archivos"
        
        tipo = temp_data[user_id]["tipo"]
        tipo_texto = "película" if tipo == "pelicula" else "serie"
        
        await message.reply(
            f"Título guardado: **{titulo}**\n\n"
            f"Ahora envía los videos o documentos {tipo_texto}:\n"
            f"Puedes ser varias si es una saga de películas o serie.\n"
            "Cuando termines de enviar los archivos, envía el command /end para terminar y subirlo al canal pv, o /cancel para cancelar."
        )
    
    # Si estamos en modo subida de archivos
    elif estado == "subiendo_archivos":
        # Verificar si es un archivo válido
        if (message.video or message.document or message.audio or 
            message.photo or message.animation):
            
            # Guardar el mensaje original
            temp_data[user_id]["mensajes_temp"].append(message.id)
            
            # Determinar tipo de archivo
            file_type = "video"
            if message.document:
                file_type = "document"
            elif message.audio:
                file_type = "audio"
            elif message.photo:
                file_type = "photo"
            elif message.animation:
                file_type = "animation"
            
            temp_data[user_id]["archivos"].append({
                "message_id": message.id,
                "file_type": file_type,
                "orden": len(temp_data[user_id]["archivos"]) + 1
            })
            
            total = len(temp_data[user_id]["archivos"])
        elif not message.command:
            await asyncio.sleep(1)
            await message.reply("Por favor envía solo archivos multimedia (videos, fotos, etc.)")



# Comando /end para terminar
@app.on_message(filters.command("end") & filters.private)
async def end_content(client, message):
    if not es_admin(message.from_user.id):
        return await message.reply("😕No eres admin para utilizar este comnand")
    
    user_id = str(message.from_user.id)
        
    if user_id not in temp_data:
        return await message.reply("No hay proceso activo. Usa /add primero")
    
    if temp_data[user_id]["estado"] != "subiendo_archivos":
        return await message.reply("No estás en modo de subida de archivos")
    
    archivos = temp_data[user_id]["archivos"]
    if len(archivos) == 0:
        return await message.reply("No has enviado ningún archivo. Usa /cancel")
    
    # Crear random_id único
    random_id = generar_id()
    titulo = temp_data[user_id]["titulo"]
    tipo = temp_data[user_id]["tipo"]
    
    proceso_m = await message.reply("🔄 **Procesando contenido...**\n\nSubiendo al canal y generando enlace...")
    await asyncio.sleep(2)
    await proceso_m.delete()
    
    contenido = {
        "random_id": random_id,
        "titulo": titulo,
        "tipo": tipo,
        "fecha_creacion": datetime.utcnow()
    }

    contenido_id = contenidos.insert_one(contenido).inserted_id
    
    # Subir archivos al canal y guardar en BD
    mensajes_ids_canal = []
    
    for i, archivo in enumerate(archivos, 1):
        while True:
            try:
                msg = await client.copy_message(
                    chat_id=CANAL_PRIVADO_ID,
                    from_chat_id=message.chat.id,
                    message_id=archivo["message_id"],
                    caption=f"{titulo} - Parte {i}" if len(archivos) > 1 else f" {titulo}"
                )
                archivos_db.insert_one({
                    "contenido_id": contenido_id,
                    "mensaje_id": msg.id,
                    "file_type": archivo["file_type"],
                    "orden": i
                })
                await asyncio.sleep(2)  # delay seguro
                break

            except FloodWait as e:
                await asyncio.sleep(e.value + 1)  

            except Exception as e:
                await message.reply(f"❌ Error al subir archivo {i}: {e}")
                break 
        
    
    
    # Generar enlace
    enlace = generar_link(random_id)
    
    # Limpiar datos temporales
    del temp_data[user_id]
    
    # Enviar resumen
    tipo_texto = "película" if tipo == "pelicula" else "serie"
    
    await message.reply(
        f"**Contenido Agregado Exitosamente!**\n\n"
        f"🎥 **Título:** {titulo}\n"
        f"🎬 **Tipo:** {tipo_texto.upper()}\n"
        f"📂 **Archivos:** {len(archivos)}\n"
        f"🆔 **ID:** `{random_id}`\n\n"
        f"🔗 **Enlace Directo:**\n`{enlace}`"
    )

# Comando /cancel para cancelar
@app.on_message(filters.command("cancel") & filters.private)
async def cancel(client, message):
    if not es_admin(message.from_user.id):
        return await message.reply("😕No eres admin para utilizar este comnand")
    
    user_id = str(message.from_user.id)
    
    if user_id in temp_data:
        del temp_data[user_id]
        await message.reply("❌ Proceso cancelado. Los archivos temporales han sido eliminados.")
    else:
        await message.reply("❌ No hay proceso activo para cancelar.")


# INICIAR BOT
if __name__ == "__main__":
    print("Bot iniciado...")
    app.run()