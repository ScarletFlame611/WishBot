import sqlite3
import random

import requests
from sdamgia import SdamGIA
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from constants import MOD

sdamgia = SdamGIA()
answer = ""


# выбор предмета
def subjects(update, context):
    subjects = ["Математика", "Русский язык"]
    # создаём клавиатуру из инлайн-кнопок с названиями предметов
    keybord_cols = 3 if len(subjects) >= 3 else len(subjects)
    choose_subject_buttons = []
    rows = len(subjects) // keybord_cols if len(subjects) >= 3 else 1
    for i in range(rows):
        row = []
        for j in range(keybord_cols):
            if (i * keybord_cols) + j >= len(subjects):
                break
            row.append(InlineKeyboardButton(subjects[(i * keybord_cols) + j],
                                            callback_data=subjects[(
                                                                           i * keybord_cols) + j] + "||" + "sbcb"))
        choose_subject_buttons.append(row)
    keyboard = InlineKeyboardMarkup(choose_subject_buttons, one_time_keyboard=False)
    update.message.reply_text("Выберите предмет:", reply_markup=keyboard)


# выбор номера задания
def choose_catalog(update, context):
    tasks_amounts = {"math": 11, "rus": 26}  # кол-во заданий тестовой части
    subject = choose_subject(
        update.callback_query.data.split("||")[0])  # краткое название выбранного предмета
    # создаём клавиатуру из инлайн-кнопок с номерами заданий
    choose_catalog_buttons = []
    keybord_cols = 5 if tasks_amounts[subject] >= 5 else tasks_amounts[subject]
    rows = (tasks_amounts[subject] + keybord_cols - 1) // keybord_cols if tasks_amounts[
                                                                              subject] >= 5 else 1
    for i in range(rows):
        row = []
        for j in range(keybord_cols):
            if (i * keybord_cols) + j + 1 > tasks_amounts[subject]:
                break
            row.append(InlineKeyboardButton(str((i * keybord_cols) + j + 1),
                                            callback_data=subject + "_" + str(
                                                (i * keybord_cols) + j + 1) + "||" + "cccb"))
        choose_catalog_buttons.append(row)
    keyboard = InlineKeyboardMarkup(choose_catalog_buttons, one_time_keyboard=False)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Выберите номер задания", reply_markup=keyboard)


# переименовываем полное название предмета в краткое
def choose_subject(subject):
    subjects_codes = {"Математика": "math", "Русский язык": "rus"}
    return subjects_codes[subject]


# отсылаем сообщение для возможности получить задание
def get_task(update, context):
    tasks_amounts = {"math": 11, "rus": 26}
    data = update.callback_query.data.split("||")[0]  # краткое название предмета + номер задания
    print(data)
    subject = data.split("_")[0]
    id = int(data.split("_")[1])
    catalog = sdamgia.get_catalog(subject)[:tasks_amounts[subject]]
    task = catalog[id - 1]  # информация о конкретном каталоге
    '''
    {'topic_id': '1', 'topic_name': 'Простейшие уравнения', 'categories': [
        {'category_id': '14', 'category_name': 'Линейные, квадратные, кубические уравнения'},
        {'category_id': '9', 'category_name': 'Рациональные уравнения'},
        {'category_id': '10', 'category_name': 'Иррациональные уравнения'},
        {'category_id': '11', 'category_name': 'Показательные уравнения'},
        {'category_id': '12', 'category_name': 'Логарифмические уравнения'},
        {'category_id': '13', 'category_name': 'Тригонометрические уравнения'}]}
    '''
    # кнопка для отправления задания
    get_task_button = [
        [InlineKeyboardButton("Получить задание", callback_data=f"{subject}_{id}||gtcb")]]
    keyboard = InlineKeyboardMarkup(get_task_button, one_time_keyboard=False)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Выбрано задание номер {task['topic_id']}: {task['topic_name']}"
                             , reply_markup=keyboard)


# получение задания
def task(update, context):
    tasks_amounts = {"math": 11, "rus": 26}
    data = update.callback_query.data.split("||")[0]  # краткое название предмета + номер задания
    subject = data.split("_")[0]
    id = int(data.split("_")[1])
    catalogs = sdamgia.get_catalog(subject)[:tasks_amounts[subject]]
    catalog = catalogs[id - 1]  # информация о конкретном каталоге
    category = random.choice(
        [i['category_id'] for i in catalog["categories"]])  # получаем рандомную категорию задания
    task = random.choice(sdamgia.get_category_by_id(subject, category))  # получаем номер задания
    task_data = sdamgia.get_problem_by_id(subject, task)  # получаем информацию о конкретном задании
    # отправляем текст задания
    update.callback_query.message.reply_text(task_data['condition']['text'])
    # отправляем картинки к заданию при наличии
    if task_data['condition']['images']:
        for i in task_data['condition']['images']:
            response = requests.get(i)
            with open('img/problem.svg', 'wb') as input_file:
                input_file.write(response.content)
            # преобразовываем svg в png
            drawing = svg2rlg('img/problem.svg')
            renderPM.drawToFile(drawing, 'img/problem.png', fmt='PNG')
            update.callback_query.message.reply_photo(photo=open('img/problem.png', 'rb'))
    answer = task_data['answer']  # ответ на задание
    chat_id = update.callback_query.message.chat_id
    MOD[chat_id] = answer  # меняем состояние чата на ожидание ответа


# проверка ответа
def check_answer(update, context, correct_answer):
    # если правильно прибавляем 10 примогемов
    if update.message.text == correct_answer:
        update.message.reply_text('Красава!')
        nickname = update.message.from_user.username
        user_id = update.message.from_user.id
        con = sqlite3.connect("wishdb.db")
        cur = con.cursor()
        primogems = int(cur.execute("""SELECT primogems FROM users
            WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
        primogems += 40
        cur.execute("""UPDATE users
        SET primogems = ?
        WHERE user_id = ?""",
                    (primogems, user_id))
        con.commit()
    else:
        update.message.reply_text('Неа')
