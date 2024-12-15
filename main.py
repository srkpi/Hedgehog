import re
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.error import BadRequest, NetworkError
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
import swagger_DB_ui as SWG
import mongo_DB_ui as MNG
import join_conversation
import event_conversation

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


if os.path.isfile('.env'):
    load_dotenv(dotenv_path='.env') # зчитування з файлу .env
dev_chat_id = str(os.getenv("DEV_CHAT"))
admin_id = str(os.getenv("ADMIN_ID"))
telegram_token = str(os.getenv("BOT_TOKEN"))
swagger_url = str(os.getenv("SWAGGER_URL"))
swagger_key = str(os.getenv("SWAGGER_KEY"))
mongo_url = str(os.getenv("MONGO_KEY"))


ordinary_commands=[("start", "Запускає бота"),("help", "Коротка довідка"),("chatid", "Показує ID цього чату"),("join", "Заповнення форми для приєднання"),("addevent", "Додавання нової події")]
form_commands=[("cancel","Скасувати заповнення форми"),("start", "Запускає бота"),("help", "Коротка довідка"),("chatid", "Показує ID цього чату"),("join", "Заповнення форми для приєднання"),("addevent", "Додавання нової події")]

forms={}
event_users=[]
username_pattern=r"^@[A-Za-z0-9_]{5,32}$"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != dev_chat_id:
        await update.message.reply_text("Привіт. Я їжак:)")
    else:
        await context.bot.send_message(chat_id=dev_chat_id, text="У службовому чаті ця команда нічого не робить.")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) == dev_chat_id:
        await update.message.reply_text("Не допомагаю поки.")
    elif str(update.message.chat_id) == admin_id:
        await update.message.reply_text("Команди для адміна:\n"
                                        " /adduser @username - надання прав додавання подій;\n"
                                        " /removeuser @username - скасування прав додавання подій;\n"
                                        " /listusers - список користувачів із правами додавання подій.")
    else:
        await update.message.reply_text(text="Списку команд ще немає.")


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"ID цього чату: {update.message.chat_id}")


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # обробник кнопок під повідомленнями
    query = update.callback_query  # отримання черги повідомлень із кнопками
    await query.answer()
    if (query.message.message_id in forms.keys()):
        data = forms.get(int(query.message.message_id), ['None', 'None', 'None'])
        chat_id = int(data[0])
        reply_message_id = int(data[1])
        forms.pop(int(query.message.message_id))
        MNG.delete_one_dictionary_item(int(query.message.message_id), "Join_forms")
        if query.data == 'good':
            keyboard = [
                [InlineKeyboardButton("🔘 Прийнято ✅ 🔘", callback_data="none")]]
            text = "Заповнену тобою форму прийнято! ☑️"
            forms[int(query.message.message_id)] = (chat_id, reply_message_id, 1)
        elif query.data == 'bad':
            keyboard = [
                [InlineKeyboardButton("🔘 Відхилено ❌ 🔘", callback_data="none")]]
            text = "Заповнену тобою форму відхилено! 🚫"
            forms[int(query.message.message_id)] = (chat_id, reply_message_id, 2)
        else:
            return
        values = forms.get(int(query.message.message_id))
        MNG.insert_one_dictionary_item(int(query.message.message_id), values, "Join_forms")
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)  # модифікація повідомлення з формою
        await context.bot.send_message(text=text, chat_id=chat_id, reply_to_message_id=reply_message_id)


async def add_event_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != admin_id:
        await unknown_command(update, context)
    else:
        input = update.message.text.replace("/adduser","").strip()
        if input=="":
            await update.message.reply_text(text="Не введено @username для додавання до списку❗️\n"
                                                 "Введіть вручну ще раз, будь-ласка.")
        else:
            if re.match(username_pattern,input):
                if input not in event_users:
                    event_users.append(input)
                    MNG.insert_one_array_item(input,"Event_users")
                    await update.message.reply_text(text=f"Користувачеві {input} успішно надано дозвіл на створення подій.")
                else:
                    await update.message.reply_text(text=f"Користувач {input} вже є у списку❗️")
            else:
                await update.message.reply_text(text="@username введено некоректно❗️\n"
                                                     "Введіть вручну ще раз, будь-ласка.")


async def remove_event_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != admin_id:
        await unknown_command(update, context)
    else:
        input = update.message.text.replace("/removeuser","").strip()
        if input=="":
            await update.message.reply_text(text="Не введено @username для вилучення із списку❗️\n"
                                                 "Введіть вручну ще раз, будь-ласка.")
        else:
            if re.match(username_pattern,input):
                if input in event_users:
                    event_users.remove(input)
                    MNG.delete_one_array_item(input,"Event_users")
                    await update.message.reply_text(text=f"Користувачеві {input} успішно скасовано права на створення подій.")
                else:
                    await update.message.reply_text(text=f"Користувача {input} немає у списку❗️")
            else:
                await update.message.reply_text(text="@username введено некоректно❗️\n"
                                                     "Введіть вручну ще раз, будь-ласка.")


async def view_event_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != admin_id:
        await unknown_command(update, context)
    else:
        if len(event_users)>0:
            message_text="Користувачі із правом додавання подій:\n"
            i=1
            for event_user in event_users:
                message_text+=f" {i}) {event_user}\n"
                i += 1
            await update.message.reply_text(text=message_text)
        else:
            await update.message.reply_text(text="Список користувачів із правом додавання подій порожній❗️")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != dev_chat_id:
        await update.message.reply_text("Невідома команда.")


async def post_init(context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Started")
    await context.bot.set_my_commands(ordinary_commands)
    await context.bot.set_my_commands(
        [("start", "Запускає бота"), ("help", "Коротка довідка"), ("chatid", "Показує ID цього чату")],
        scope=telegram.BotCommandScopeChat(dev_chat_id))


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(str(context.error))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a+") as file:
        file.write(f"{str(context.error)}\n{current_time}\n")


def main():
    print("Launched.")
    reboot = True
    SWG.initialize(swagger_url,swagger_key)
    MNG.initialize(mongo_url,"HedgeHog_bot_DB")
    MNG.load_all_to_array(event_users,"Event_users")
    app = ApplicationBuilder().token(telegram_token).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("chatid", chat_id))
    app.add_handler(CommandHandler("adduser", add_event_user))
    app.add_handler(CommandHandler("removeuser", remove_event_user))
    app.add_handler(CommandHandler("listusers", view_event_users))
    app.add_handler(join_conversation.init(dev_chat_id, forms, ordinary_commands, form_commands))
    app.add_handler(event_conversation.init(dev_chat_id, event_users, ordinary_commands, form_commands))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(CallbackQueryHandler(buttons))  # додавання обробника кнопок
    app.add_error_handler(error_handler)
    while reboot:
        try:
            print("Starting app...")
            app.run_polling(allowed_updates=Update.ALL_TYPES, timeout=50, close_loop=True, poll_interval=0.5)
        except NetworkError as e:
            print(str(e))
            with open("log.txt", "a+") as file:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"{str(e)}\n{current_time}\n")
            time.sleep(10)


if __name__ == "__main__":
    main()
