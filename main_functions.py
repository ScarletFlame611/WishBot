from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler
from gia_functions import check_answer
from constants import MOD
import sqlite3


# начало работы с ботом
def start(update, context):
    # берём никнейм пользователя
    nickname = update.message.from_user.username
    user_id = update.message.from_user.id
    con = sqlite3.connect("wishdb.db")
    cur = con.cursor()
    # проверка, есть ли пользователь в базе данных
    is_here = cur.execute("""SELECT * FROM users
                WHERE user_id = ?""", (user_id,)).fetchall()
    # если нет - добавляем
    if not is_here:
        cur.execute("""INSERT INTO users(nickname,primogems,user_id) VALUES(?,?,?)""",
                    (nickname, 0, user_id))
        con.commit()
    reply_keyboard = [['/start', '/help', '/close'], ['/profile', '/wish', '/wish10'],
                      ['/inventory', '/daily', '/work']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        "Привет! Я бот-симулятор круток в геншине! Зарабатывать примогемы вы сможете,"
        " решая задания! Удачи!",
        reply_markup=markup)


# обработчик текстовых сообщений
def echo(update, context):
    chat_id = update.message.chat_id
    # если просто введено какое-то сообщение:
    if chat_id not in MOD:
        if "Маша не пишет" in update.message.text:
            update.message.reply_text("МАША, ПИШИ!!!")
            return
        update.message.reply_text(update.message.text)
    # если ожидается ответ от пользователя
    else:
        check_answer(update, context, MOD[chat_id])
        MOD.pop(chat_id)


# помощь по командам
def help(update, context):
    update.message.reply_text(
        "Основные команды бота:\n\n"
        "/profile - команда для просмотра профиля\n"
        "/inventory - команда для просмотра инвентаря\n"
        "/wish - команда для совершения одной молитвы\n"
        "/wish10 - команда для совершения 10 молитв сразу\n"
        "/daily - команда для получения ежедневной порции примогемов!\n"
        "/work - команда для заработка примогемов")


# убрать клавиатуру
def close_keyboard(update, context):
    update.message.reply_text("Ok", reply_markup=ReplyKeyboardRemove())
