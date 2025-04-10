
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

usuarios = {}
preco = 4

def carregar_estoque():
    with open("estoque.txt", "r") as f:
        return [linha.strip() for linha in f if linha.strip()]

def salvar_estoque(linhas):
    with open("estoque.txt", "w") as f:
        f.write("\n".join(linhas))

def formatar_cartao(cartao):
    numero, mes, ano, cvv = cartao.split("|")
    return f"💳 {numero}\n|{mes}|{ano}|{cvv}|VISA|NUBANK\nNome: João da Silva\nCPF: 123.456.789-00\nPaís: BRASIL"

def get_keyboard(menu="principal"):
    if menu == "principal":
        return [[InlineKeyboardButton("GGS 💳", callback_data="produtos")],
                [InlineKeyboardButton("Adicionar saldo", callback_data="saldo")],
                [InlineKeyboardButton("Resgatar Gift Code", callback_data="resgatar")],
                [InlineKeyboardButton("Suporte", url="https://t.me/Skarlet7771")]]
    if menu == "voltar":
        return [[InlineKeyboardButton("Voltar", callback_data="voltar")]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios.setdefault(user_id, {"saldo": 10, "pontos": 0})  # saldo inicial de teste
    with open("image.jpg", "rb") as img:
        await update.message.reply_photo(
            photo=InputFile(img),
            caption=f"Bem-vindo {update.effective_user.first_name}!\nSaldo: R${usuarios[user_id]['saldo']}\nPontos: {usuarios[user_id]['pontos']}\nID: {user_id}",
            reply_markup=InlineKeyboardMarkup(get_keyboard())
        )

async def botao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "produtos":
        estoque = carregar_estoque()
        if estoque:
            await query.edit_message_caption(
                caption=f"💳 {estoque[0][:12]}...
Preço: R${preco}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Comprar", callback_data="comprar")], *get_keyboard("voltar")])
            )
        else:
            await query.edit_message_caption(caption="Sem estoque.", reply_markup=InlineKeyboardMarkup(get_keyboard("voltar")))

    elif query.data == "saldo":
        await query.edit_message_caption(caption="Pix Automático OFF. Adicione saldo via suporte @Skarlet7771", reply_markup=InlineKeyboardMarkup(get_keyboard("voltar")))

    elif query.data == "resgatar":
        await query.edit_message_caption(caption="Envie o código do gift usando /resgatar código", reply_markup=InlineKeyboardMarkup(get_keyboard("voltar")))

    elif query.data == "voltar":
        with open("image.jpg", "rb") as img:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=user_id,
                photo=InputFile(img),
                caption=f"Bem-vindo {query.from_user.first_name}!\nSaldo: R${usuarios[user_id]['saldo']}\nPontos: {usuarios[user_id]['pontos']}\nID: {user_id}",
                reply_markup=InlineKeyboardMarkup(get_keyboard())
            )

    elif query.data == "comprar":
        if usuarios[user_id]["saldo"] >= preco:
            estoque = carregar_estoque()
            if estoque:
                cartao = estoque.pop(0)
                salvar_estoque(estoque)
                usuarios[user_id]["saldo"] -= preco
                usuarios[user_id]["pontos"] += 1
                with open("image.jpg", "rb") as img:
                    await query.message.delete()
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=InputFile(img),
                        caption=f"✅ Compra efetuada!
Novo saldo: R${usuarios[user_id]['saldo']}
Pontos: {usuarios[user_id]['pontos']}
{formatar_cartao(cartao)}",
                        reply_markup=InlineKeyboardMarkup(get_keyboard("voltar"))
                    )
            else:
                await query.edit_message_caption(caption="Sem estoque disponível.", reply_markup=InlineKeyboardMarkup(get_keyboard("voltar")))
        else:
            await query.edit_message_caption(caption="Saldo insuficiente.", reply_markup=InlineKeyboardMarkup(get_keyboard("voltar")))

async def resgatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) == 1 and context.args[0] == "GIFT123":
        usuarios[user_id]["saldo"] += 10
        await update.message.reply_text(f"Gift code resgatado! Novo saldo: R${usuarios[user_id]['saldo']}")
    else:
        await update.message.reply_text("Gift code inválido.")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resgatar", resgatar))
    app.add_handler(CallbackQueryHandler(botao))
    app.run_polling()
