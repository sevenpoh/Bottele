import logging
import asyncio
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = '7977593128:AAHzwfhgfKxc-FOZv04zoMcmeBBNoJG-f7A'

nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

usuarios = {}
estoque = [
    "4854647167980934|07|2027|789",
    "4854647167982534|07|2027|789",
    "4854647167981783|07|2027|789",
    "4854647167987863|07|2027|789",
    "4854645152572310|07|2027|789",
    "4854645152580354|06|2027|789"
]

def menu_principal(user_id):
    nome = usuarios[user_id]["nome"]
    saldo = usuarios[user_id]["saldo"]
    texto = (
        f"Olá {nome}, Bem-vindo(a)!

"
        "Para comprar, selecione uma opção abaixo.
"
        "Em caso de dúvidas, fale com o suporte.

"
        f"ID: {user_id}
Saldo: R${saldo},00
Pontos: 0"
    )
    teclado = [
        [InlineKeyboardButton("Adicionar saldo", callback_data='saldo')],
        [InlineKeyboardButton("GGS 💳", callback_data='produtos')],
        [InlineKeyboardButton("Resgatar Gift Code", callback_data='resgatar')],
        [InlineKeyboardButton("Suporte", url='https://t.me/Skarlet7771')],
    ]
    return texto, InlineKeyboardMarkup(teclado)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in usuarios:
        usuarios[user.id] = {
            "nome": user.first_name,
            "saldo": 0,
            "pago": False,
            "gift_resgatado": False
        }
    with open("IMG_6829.jpeg", "rb") as imagem:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(imagem))
    texto, teclado = menu_principal(user.id)
    await update.message.reply_text(texto, reply_markup=teclado)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "saldo":
        await query.edit_message_text(
            "Pix Automático OFF. Adicione saldo via suporte @Skarlet7771",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]])
        )

    elif query.data == "produtos":
        if not estoque:
            await query.edit_message_text("Sem estoque no momento.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]]))
        else:
            await query.edit_message_text(
                "Clique abaixo para comprar:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 485464", callback_data='comprar_485464')],
                    [InlineKeyboardButton("Voltar", callback_data='voltar')]
                ])
            )

    elif query.data == "resgatar":
        usuarios[user_id]["gift_resgatado"] = True
        await query.edit_message_text(
            "Insira seu gift code: (ainda em desenvolvimento)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]])
        )

    elif query.data == "comprar_485464":
        user = usuarios[user_id]
        if user["saldo"] < 4:
            await query.edit_message_text("Saldo insuficiente.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]]))
        elif not user["gift_resgatado"]:
            await query.edit_message_text("Você precisa resgatar um gift antes.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]]))
        else:
            produto = estoque.pop(0)
            user["saldo"] -= 4
            msg = (
                "Compra efetuada!
"
                "- Preço: R$ 4
"
                f"- Novo Saldo: R$ {user['saldo']}
"
                "- Pontos recebidos: 0.32

"
                "💳 Produto:
"
                "País: 🇧🇷Brasil
"
                f"Cartão: {produto}
"
                "Bandeira: VISA
Banco: BANCO DO BRASIL

"
                f"✅ aqui o produto |{produto.split('|')[1]}|{produto.split('|')[2]}|{produto.split('|')[3]}|VISA|BANCO DO BRASIL|

"
                "🆘 Dados auxiliares:
"
                "Nome: Raimunda Barboza Duarte
CPF: 000.106.673-00"
            )
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]]))

    elif query.data == "voltar":
        texto, teclado = menu_principal(user_id)
        await query.edit_message_text(texto, reply_markup=teclado)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    print("Bot rodando...")
    await app.run_polling()

if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(main())