from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Variables globales para los botones

def menu_principal():
    boton1 = InlineKeyboardButton("Help", callback_data="help")
    boton2 = InlineKeyboardButton("Channel", url="https://t.me/homelevo")
    boton3 = InlineKeyboardButton("Support", url="https://t.me/+1wspSzFEfdFkYjJh")
    
    teclado = InlineKeyboardMarkup([[boton2, boton3, boton1]])
    return teclado

def ayuda_menu():
    teclado2 = InlineKeyboardMarkup([
        [InlineKeyboardButton("Version", callback_data="Ver")],
        [InlineKeyboardButton("Inicio", callback_data="Principal")]
    ])
    return teclado2


app = Client('bot', API_ID, API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    teclado = menu_principal()
    await message.reply(
        "Bienvedido al bot de Compresion", reply_markup=teclado
    )

@app.on_callback_query()
async def Manejo_boton(client, callback_query):
    data = callback_query.data
    # Craamos el help, y conectado a la Variables ayuda menu
    if data == "help":
        teclado2 = ayuda_menu()
        await callback_query.edit_message_text(
            "Aquí puede obtener Ayuda de cómo utilizar el bot",
            reply_markup=teclado2
        )
    # Le ponemo elif para tener regreso a if 
    elif data == "Ver":
        menu = InlineKeyboardMarkup([
            [InlineKeyboardButton("Volver", callback_data="help")]
        ])
        await callback_query.edit_message_text(
            "Aquí puede ver la versión del Bot\n\n**Versión 1.0**", 
            reply_markup=menu
        )
    # Igual mente 
    elif data == "Principal":
        teclado = menu_principal()
        await callback_query.edit_message_text(
            "Bienvenido al bot de Compresión",
            reply_markup=teclado
        )

    
    # esto es para que Funcione
    await callback_query.answer()