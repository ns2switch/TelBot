#!/usr/bin/env python
# pylint: disable=C0116
import datetime
import logging
import os
from datetime import date
from random import randrange
from uuid import uuid4
from dotenv import load_dotenv
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from telegram.utils.helpers import escape_markdown

load_dotenv ()
# variables
TOKEN = os.getenv ('TOKEN')
# Logging
logging.basicConfig (
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger (__name__)


# handler

def start(update: Update, _: CallbackContext) -> None :
	update.message.reply_text ('Hi!')


def help_command(update: Update, _: CallbackContext) -> None :
	update.message.reply_text ('Help!')


def reserva_command(update: Update, _: CallbackContext) -> None :
	user = update.message.from_user
	message = update.message.text.split (" ")[1]
	update.message.reply_text ("se ha pedido " + message)


def libros_command(update: Update, _: CallbackContext) -> None :
	tdate = date.today ()
	rdays = randrange (365)
	entrega = tdate + datetime.timedelta (days=rdays)
	date_entrega = entrega.ctime ()
	update.message.reply_text ("recibiras los libros del master: " + str (entrega))


def gracias_command(update: Update, _: CallbackContext) -> None :
	update.message.reply_text ('GraciasManel')


def inlinequery(update: Update, _: CallbackContext) -> None :
	query = update.inline_query.query

	if query == "" :
		return

	results = [
		InlineQueryResultArticle (
			id=str (uuid4 ()),
			title="Caps",
			input_message_content=InputTextMessageContent (query.upper ()),
		),
		InlineQueryResultArticle (
			id=str (uuid4 ()),
			title="Bold",
			input_message_content=InputTextMessageContent (
				f"*{escape_markdown (query)}*", parse_mode=ParseMode.MARKDOWN
			),
		),
		InlineQueryResultArticle (
			id=str (uuid4 ()),
			title="Italic",
			input_message_content=InputTextMessageContent (
				f"_{escape_markdown (query)}_", parse_mode=ParseMode.MARKDOWN
			),
		),
	]

	update.inline_query.answer (results)


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
	dispatcher.add_handler (CommandHandler ("libros", libros_command))

	# on non command i.e message - echo the message on Telegram
	dispatcher.add_handler (InlineQueryHandler (inlinequery))

	# Start the Bot
	updater.start_polling ()

	# Block until the user presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle ()


if __name__ == '__main__' :
	main ()
