from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os

TOKEN = "7977593128:AAHzwfhgfKxc-FOZv04zoMcmeBBNoJG-f7A"

app_bot = ApplicationBuilder().token(TOKEN).build()

estoque = ["4854643213331111|12|2028|123"]
usuarios = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    nome = user.first_name

    if user_id not in usuarios:
        usuarios[user_id] = {"saldo": 0, "pontos": 0}

    keyboard = [
        [InlineKeyboardButton("GGS 💳", callback_data="produtos")],
        [InlineKeyboardButton("Adicionar saldo", callback_data="saldo")],
        [InlineKeyboardButton("Resgatar Gift Code", callback_data="gift")],
        [InlineKeyboardButton("Suporte", url="https://t.me/Skarlet7771")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=open("IMG_6829.jpeg", "rb"),
        caption=f"Olá {nome}!

Seu ID: `{user_id}`
Saldo: R${usuarios[user_id]['saldo']}
Pontos: {usuarios[user_id]['pontos']}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "saldo":
        await query.edit_message_caption(
            caption="Pix Automático OFF. Adicione saldo via suporte @Skarlet7771",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]])
        )
    elif query.data == "produtos":
        if estoque:
            await query.edit_message_caption(
                caption=f"💳 {estoque[0]}

Clique em comprar para receber com dados completos.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Comprar por R$4", callback_data="comprar")],
                    [InlineKeyboardButton("Voltar", callback_data="voltar")]
                ])
            )
        else:
            await query.edit_message_caption("Sem estoque no momento.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]]))
    elif query.data == "comprar":
        if usuarios[user_id]["saldo"] >= 4:
            usuarios[user_id]["saldo"] -= 4
            usuarios[user_id]["pontos"] += 1
            card = estoque.pop(0)
            await query.edit_message_caption(
                caption=f"✅ Compra efetuada!

💳 {card}
Novo saldo: R${usuarios[user_id]['saldo']}
Pontos: {usuarios[user_id]['pontos']}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]])
            )
        else:
            await query.edit_message_caption("❌ Saldo insuficiente.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]]))
    elif query.data == "gift":
        await query.edit_message_caption("Envie seu gift code para resgatar:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="voltar")]]))
    elif query.data == "voltar":
        await start(update, context)

async def handle_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.text.startswith("GIFT-"):
        usuarios[user_id]["saldo"] += 4
        await update.message.reply_text("Gift code resgatado com sucesso! R$4 adicionados ao saldo.")

app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CallbackQueryHandler(button_handler))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gift))

import threading
def run_bot():
    app_bot.run_polling()
threading.Thread(target=run_bot).start()

app = Flask(__name__)
@app.route('/')
def index():
    return "Bot ativo!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
