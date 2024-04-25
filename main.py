import logging
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import Message_texts as mes_txt
import books
import config
import votings

TG_BOT_TOKEN = '6349888088:AAH6iwE-hnAg6Lbpm5aXPbLzFEtvUkGsm5c'
ADMIN = 1027691775

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /start')
        return
    await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.GREETINGS)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /help')
        return
    await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.HELP)


async def already(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /already')
        return
    already_read_books = await books.get_already_read_books()
    response = 'Прочитанные книги: \n\n'
    for index, book in enumerate(already_read_books, 1):
        response += f'{index}. {book.name} (читали с {book.read_start} по {book.read_finish})\n'

    await context.bot.send_message(chat_id=effective_chat.id, text=response)


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /now')
        return
    now_reading = await books.get_now_reading_books()
    if now_reading:
        responce = 'Сейчас мы читаем:\n\n'
        just_one_book = len(now_reading) == 1
        for index, book in enumerate(now_reading, 1):
            responce += f'{str(index) + ". " if not just_one_book else ""}{book.name} (читаем c {book.read_start} по {book.read_finish})'
    else:
        responce = 'Сейчас мы не читаем книгу'

    await context.bot.send_message(chat_id=effective_chat.id, text=responce)


async def all_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /allbooks')
        return
    categories_with_books = await books.get_all_books()
    for category in categories_with_books:
        response = '**' + category.name + '**\n\n'
        for index, book in enumerate(category.books, 1):
            response += f'{index}. {book.name}\n'
        await context.bot.send_message(chat_id=effective_chat.id, text=response)


async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /allbooks')
        return
    if await votings.get_actual_voting() is None:
        await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.NO_ACTUAL_VOTING)
        return
    categories_with_books = await books.get_not_started_books()
    index = 1
    for category in categories_with_books:
        response = '**' + category.name + '**\n\n'
        for book in category.books:
            response += f'{index}. {book.name}\n'
            index += 1
        await context.bot.send_message(chat_id=effective_chat.id, text=response)
    await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.VOTE)


async def vote_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /allbooks')
        return
    if await votings.get_actual_voting() is None:
        await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.NO_ACTUAL_VOTING)
        return

    user_message = update.message.text
    numbers = re.findall(r'\d+', user_message)
    numbers = tuple(map(int, numbers))
    if len(set(numbers)) != config.VOTE_ELEMENTS_COUNT:
        await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.VOTE_PROCESS_INCORRECT_INPUT)
        return

    book = await books.get_books_by_numbers(numbers)
    if len(book) != config.VOTE_ELEMENTS_COUNT:
        await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.VOTE_PROCESS_INCORRECT_BOOKS)
        return

    await votings.save_vote(update.effective_user.id, book)

    response = "Вы выбрали три книги: \n\n"
    for index, book_name in enumerate(book, 1):
        response += f'{index}. {book_name.name}\n'
    await context.bot.send_message(chat_id=effective_chat.id, text=response)


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat in /vote_results')
        return
    leaders = await votings.get_leaders()
    if leaders is None:
        await context.bot.send_message(chat_id=effective_chat.id, text=mes_txt.NO_VOTE_RESULTS)
        return
    response = "Топ 10 книг голосования: \n\n"
    for index, book in enumerate(leaders.leaders, 1):
        response += f'{index}. "{book.book_name}" с рейтингом: {book.score}\n'
    response += f'\n Даты голосования: с {leaders.vote_start} по {leaders.vote_finish}'
    await context.bot.send_message(chat_id=effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    allbooks_handler = CommandHandler('allbooks', all_books)
    application.add_handler(allbooks_handler)

    already_handler = CommandHandler('already', already)
    application.add_handler(already_handler)

    now_handler = CommandHandler('now', now)
    application.add_handler(now_handler)

    vote_handler = CommandHandler('vote', vote)
    application.add_handler(vote_handler)

    vote_results_handler = CommandHandler('vote_results', vote_results)
    application.add_handler(vote_results_handler)

    vote_process_handler = MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=vote_process)
    application.add_handler(vote_process_handler)

    application.run_polling()
