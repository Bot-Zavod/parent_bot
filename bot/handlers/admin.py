from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext

from bot.data import text
from bot.database import db_interface
from bot.states import State
from bot.utils.log import log_message
from bot.utils.spreadsheet import GAMES_SHEET
from bot.utils.spreadsheet import update_games
from bot.utils.wraps import restrict_user


PUSH_TEXT = None  # for text that admin wants to send


@restrict_user
def admin_menu(update: Update, context: CallbackContext):
    """show up basic admin menu"""
    log_message(update)

    reply_keyboard = [
        [text["push"], text["users"]],
        [text["update_games"]],
        [text["back"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    update.message.reply_text(text=text["hi_boss"], reply_markup=markup)
    return State.ADMIN


@restrict_user
def update_games_tables(update: Update, context: CallbackContext):
    log_message(update)
    games_num = update_games()
    msg = (
        f"Games database was succesfully updated with {games_num} games"
        + f"\nfrom table:\nhttps://docs.google.com/spreadsheets/d/{GAMES_SHEET}/"
    )
    update.message.reply_text(text=msg)
    return State.ADMIN


@restrict_user
def list_users(update: Update, context: CallbackContext):
    log_message(update)
    users_count = db_interface.users_count()
    msg = f"Воспользовались: {users_count}"
    update.message.reply_text(text=msg)
    return State.ADMIN


@restrict_user
def ask_push_text(update: Update, context: CallbackContext):
    log_message(update)
    update.message.reply_text(
        text=text["ask_push_text"], reply_markup=ReplyKeyboardRemove()
    )
    return State.PUSH_WHAT


@restrict_user
def set_push_text(update: Update, context: CallbackContext):
    """catches admin massage"""
    log_message(update)

    global PUSH_TEXT
    answer = update.message.text
    PUSH_TEXT = answer

    reply_keyboard = [[text["send"], text["cancel"]]]
    markup = ReplyKeyboardMarkup(
        reply_keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    msg = text["push_submit"].format(answer=answer)
    update.message.reply_text(text=msg, reply_markup=markup)
    return State.PUSH_SUBMIT


@restrict_user
def push_handler(update: Update, context: CallbackContext):
    log_message(update)

    global PUSH_TEXT
    # sending the notification message
    users_ids = db_interface.get_users()
    for chat_id in users_ids:
        context.bot.send_message(chat_id=chat_id, text=PUSH_TEXT)
    user_number = len(users_ids)
    update.message.reply_text(text=text["push_success"].format(user_number=user_number))
    return admin_menu(update, context)
