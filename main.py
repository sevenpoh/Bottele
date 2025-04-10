import os
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or "COLE_SEU_TOKEN_AQUI"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with open("start.jpg", "rb") as image_file:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(image_file),
            caption=f"Olá, {user.first_name}!\n\nBem-vindo ao GGS Bot.",
            reply_markup=ReplyKeyboardMarkup(
                [["GGS 💳", "Adicionar saldo"], ["Resgatar Gift Code", "Suporte"]],
                resize_keyboard=True
            )
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()