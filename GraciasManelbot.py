#!/usr/bin/env python
# pylint: disable=C0116
import json
import random
import string
import datetime
import logging
import time
import re
from random import randrange
from uuid import uuid4
from datetime import date , datetime , timedelta
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
from youtubesearchpython import VideosSearch
from pymongo import MongoClient, TEXT, DESCENDING

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

SHORT_TIME_FORMAT = '%Y.%m.%d %H:%M'
DAY_NAMES = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


#handler
def get_text_repr(doc):
    time = doc['time']
    day_shortname = get_day_shortname(time)
    time_str = '%s (%s)' % (time.strftime(SHORT_TIME_FORMAT), day_shortname)
    text = '•' + ' %s\n%s' % (time_str, doc['post'])
    return text


def get_day_shortname(time):
    today = datetime.utcnow().date()
    if time.date() == today:
        return 't'

    yesterday = today - timedelta(days=1)
    if time.date() == yesterday:
        return 'y'

    weekday = DAY_NAMES[time.weekday()]
    return weekday


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi!')

def get_user_collection(user):
    client = MongoClient('mongodb://mongodb:27017/')
    database = client['telbot']

    collection_name = str(user.id)
    user_collection = database[collection_name]
    return user_collection

def history_cursor_to_str(cur):
    reprs = [get_text_repr(d) for d in cur]
    return '\n\n'.join(reprs[::-1])

def get_document_from_message(msg):
    DATETIME_SET_RE = r'#t (\d{4}.\d{2}.\d{2} \d{1,2}:\d{1,2})'
    timestamp = re.search(DATETIME_SET_RE, msg)
    if timestamp:
        explicit_time = datetime.strptime(timestamp.group(1), SHORT_TIME_FORMAT)
        msg = re.sub(DATETIME_SET_RE, '', msg)
    else:
        explicit_time = None

    post = msg

    doc = {
	'time': explicit_time or datetime.utcnow(),
        'post': post,
    }
    return doc

def search(update: Update, _: CallbackContext ) -> None:
    user = update.message.from_user
    user_collection = get_user_collection(user)

    # make sure user collection has a text index
    user_collection.create_index([('post', TEXT)], default_language='spanish')

    msg = update.message.text.replace('/busca', '')

    res_cur = user_collection.find({'$text': {'$search': msg }}) \
                             .sort('time', -1) \
                             .limit(10)
    res_str = history_cursor_to_str(res_cur)
    if not res_str.strip():
        res_str = 'No se que me dices'
    update.message.reply_text(res_str, disable_web_page_preview=True)

def save(update: Update, _: CallbackContext ) -> None:
    msg = update.message.text
    user = update.message.from_user
    msg = update.message.text.replace('/recuerda', '')
    user_collection = get_user_collection(user)
    doc = get_document_from_message(msg)
    doc_id = user_collection.insert_one(doc)
    if doc_id:
        update.message.reply_text('Apuntado')

def stats(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    user_coll = get_user_collection(user)
    response = 'Hay logeados {} mensajes\n'.format(user_coll.count())

    client = MongoClient('mongodb://mongodb:27017/')
    db = client['telbot']
    coll_counts = [db[coll].count() for coll in db.collection_names()]
    response += '\nTelBot has `{}` users\n'.format(len(coll_counts))
    response += 'Conversacion mas larga: `{}`\n'.format(sorted(coll_counts)[-3:])
    month_ago = datetime.utcnow() - timedelta(days=30)
    recent_counts = [db[coll].find({'time': {'$gt': month_ago}}).count() for coll in db.collection_names()]
    response += 'Mensajes en el ultimo mess:  `{}`\n'.format(sum(recent_counts))
    active_colls = sum([c > 0 for c in recent_counts])
    response += 'Usuarios activos en el ultimo mess: `{}`\n'.format(active_colls)

    update.message.reply_text(response, parse_mode='Markdown')


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help!')

def reserva_command(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    message = update.message.text.split(" ")[1]
    update.message.reply_text("se ha pedido " + message)

def modulo_command(update: Update, _: CallbackContext) -> None:
    tdate = date.today()
    rdays = randrange(365)
    entrega = tdate + datetime.timedelta (days=rdays)
    date_entrega = entrega.ctime()
    update.message.reply_text("Julio te corregira el modulo 2 el dia: " + str(entrega))

def gracias_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('GraciasManel')

def libros_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Pa esta semana los tienes xdxd')

def pass_command(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    length = update.message.text.split(" ")[1]
    if not length:
        length = 1
    length = int(length)
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    all = lower + upper + num + symbols
    temp = random.sample(all,length)
    passw = "".join(temp)
    update.message.reply_text(passw)

def video_command(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    text =  update.message.text.replace('/video', '')
    videosSearch = VideosSearch(text, limit = 1)
    res = videosSearch.result()
    for item in res:
        data = res[item][0]['link']
    update.message.reply_text(data)

def inlinequery(update: Update, _: CallbackContext) -> None:
    query = update.inline_query.query

    if query == "":
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]

    update.inline_query.answer(results)


def main() -> None :
    # Create the Updater and pass it your bot's token.
    updater = Updater (TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler (CommandHandler ("start", start))
    dispatcher.add_handler (CommandHandler ("help", help_command))
    dispatcher.add_handler (CommandHandler ("gracias", gracias_command))
    dispatcher.add_handler (CommandHandler ("reserva", reserva_command))
    dispatcher.add_handler (CommandHandler ("modulo2", modulo_command))
    dispatcher.add_handler (CommandHandler ("libros", libros_command))
    dispatcher.add_handler (CommandHandler ("video", video_command))
    dispatcher.add_handler (CommandHandler ("pass", pass_command))
    dispatcher.add_handler (CommandHandler ("stats", stats))
    dispatcher.add_handler (CommandHandler ("recuerda", save))
    dispatcher.add_handler (CommandHandler ("busca", search))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler (InlineQueryHandler (inlinequery))

    # Start the Bot
    updater.start_polling ()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle ()

if __name__ == '__main__':
    main()

