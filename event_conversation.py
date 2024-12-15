import copy
import re
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
import time
from datetime import datetime, timedelta
import swagger_DB_ui as SWG

dev_chat_id = 0
form_commands = []
ordinary_commands = []
event_users = []
conversation_handler = None

NAME, DESCRIPTION, LOCATION, TAG, START_DATE, END_DATE, CONFIRM = range(7)

def init(DEV_CHAT, EVENT_USERS, ORDINARY_COMMANDS, FORM_COMMANDS):
    global dev_chat_id, forms, form_commands, ordinary_commands, event_users
    dev_chat_id=DEV_CHAT
    ordinary_commands=ORDINARY_COMMANDS
    form_commands=FORM_COMMANDS
    event_users=EVENT_USERS
    conv_handler = ConversationHandler(
        entry_points=[(CommandHandler("addevent", new_event))],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
            TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, tag)],
            START_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_date)],
            END_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, end_date)],
            CONFIRM: [CallbackQueryHandler(confirm)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    return conv_handler


def is_valid_date(date_string: str) -> bool:
    try:
        date = datetime.strptime(date_string, "%H:%M %d.%m.%Y")
        if date >= datetime.now():
            return True
        else:
            return False
    except ValueError:
        return False


def is_past_date(first_date: str, second_date: str) -> bool:
    try:
        date1 = datetime.strptime(first_date, "%H:%M %d.%m.%Y")
        date2 = datetime.strptime(second_date, "%H:%M %d.%m.%Y")
        if date2 > date1:
            return True
        else:
            return False
    except ValueError:
        return False


async def new_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if ("@"+update.message.from_user.username) in event_users:
        await context.bot.set_my_commands(form_commands,scope=telegram.BotCommandScopeChat(update.message.chat_id))
        context.user_data['index']=1
        await update.message.reply_text("Для заповнення форми дай відповіді на запитання нижче(для скасування заповнення форми введи /cancel).")
        await update.message.reply_text(f"{context.user_data.get('index')}. Назва події, яку ти хочеш додати.")
        return NAME
    else:
        await update.message.reply_text(text="Немає прав для додавання подій!")
        return ConversationHandler.END


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    index = context.user_data.get('index')
    context.user_data['index'] = index+1
    await update.message.reply_text(f"{context.user_data.get('index')}. Надайте короткий опис події(кілька речень).")
    return DESCRIPTION


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await update.message.reply_text(f"{context.user_data.get('index')}. Назва локації, в якій відбуватиметься подія.")
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['location'] = update.message.text
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await update.message.reply_text(f"{context.user_data.get('index')}. Надай тег для події у форматі #тег.")
    return TAG


async def tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if re.match(r"^#\w+$", update.message.text):
        context.user_data['tag'] = update.message.text
    else:
        await update.message.reply_text(
            "Неправильний формат введення даних. Введи ще раз, будь ласка.")
        return TAG
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await update.message.reply_text(f"{context.user_data.get('index')}. Дата та час початку події у форматі  гг:хх дд.мм.рррр.")
    return START_DATE


async def start_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if (is_valid_date(update.message.text)):
        context.user_data['start_date_buffer'] = update.message.text
        index = context.user_data.get('index')
        context.user_data['index'] = index + 1
        await update.message.reply_text(f"{context.user_data.get('index')}. Дата та час кінця події у форматі  гг:хх дд.мм.рррр.")
        return END_DATE
    else:
        await update.message.reply_text(
            "Неправильний формат введення даних або введено дату та час, які вже минули/не є можливими. Введи ще раз, будь ласка.")
        return START_DATE


async def end_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if (is_valid_date(update.message.text) and is_past_date(context.user_data.get('start_date_buffer'),update.message.text)):
        context.user_data['end_date'] = update.message.text.replace(" "," - ")
        context.user_data['start_date'] =  context.user_data.get('start_date_buffer').replace(" "," - ")
        index = context.user_data.get('index')
        context.user_data['index'] = index + 1
        keyboard = [
            [InlineKeyboardButton("Все вірно, додати подію", callback_data="Yes")],
            [InlineKeyboardButton("Ні, повторити заповнення форми", callback_data="No")],
        ]

        report_message = (
            f"*Назва події:* {context.user_data.get('name')}\n"
            f"*Опис:* {context.user_data.get('description')}\n"
            f"*Локація:* {context.user_data.get('location')}\n"
            f"*Тег:* {context.user_data.get('tag')}\n"
            f"*Дата початку:* {context.user_data.get('start_date')}\n"
            f"*Дата кінця:* {context.user_data.get('end_date')}\n"
        )
        context.user_data['username'] = str("@"+update.message.from_user.username if update.message.from_user.username else (update.message.from_user.first_name + " " + update.message.from_user.last_name)).replace("_","\_")
        context.user_data['report'] = report_message
        await update.message.reply_text(
            f"Дякую! Введені тобою дані:\n{report_message}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard))
        return CONFIRM
    else:
        await update.message.reply_text(
            "Неправильний формат введення даних або введено дату та час, які вже минули/раніші за дату та час початку або не є можливими. Введи ще раз, будь ласка.")
        return END_DATE


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    none_keyboard=""
    if(query.data=="Yes"):
        none_keyboard = [
            [InlineKeyboardButton("🔘 Все вірно, додати подію 🔘 ", callback_data="none")],
        ]
    elif(query.data=="No"):
        none_keyboard = [
            [InlineKeyboardButton("🔘 Ні, повторити заповнення форми 🔘 ", callback_data="none")],
        ]
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(none_keyboard))
    while (query.data == "none"):
        query = update.callback_query
        await query.answer()
    if (query.data == "Yes"):
        form = await context.bot.send_message(chat_id=dev_chat_id,text=f"Нова заповнена форма!!!")
        await context.bot.edit_message_text(chat_id=dev_chat_id,message_id=form.message_id,text=f"📅 Нова додана подія від {context.user_data.get('username')}:\n*ID форми*: #T{query.message.chat.id}{((form.message_id) + 1)}\n{context.user_data.get('report')}",parse_mode="Markdown")
        new_event = {
            "title": context.user_data.get('name'),
            "shortDescription": context.user_data.get('description'),
            "location": context.user_data.get('location'),
            "tag": context.user_data.get('tag'),
            "startDate": datetime.strptime(context.user_data.get('start_date'), "%H:%M - %d.%m.%Y").isoformat()+"Z",
            "endDate": datetime.strptime(context.user_data.get('end_date'), "%H:%M - %d.%m.%Y").isoformat()+"Z"
        }
        SWG.create_event(new_event)
        context.user_data.clear()
        await context.bot.set_my_commands(ordinary_commands, scope=telegram.BotCommandScopeChat(query.message.chat.id))
        return ConversationHandler.END
    elif (query.data == "No"):
        context.user_data.clear()
        context.user_data['index'] = 1
        await query.message.reply_text(f"{context.user_data.get('index')}. Назва події, яку ти хочеш додати.")
        return NAME


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введення форми скасовано!")
    await context.bot.set_my_commands(ordinary_commands,scope=telegram.BotCommandScopeChat(update.message.chat_id))
    return ConversationHandler.END