import sqlite3
import random
from datetime import datetime as dt, timezone


# функция для показа профиля пользователя
def profile(update, context):
    nickname = update.message.from_user.username
    user_id = update.message.from_user.id
    con = sqlite3.connect("wishdb.db")
    cur = con.cursor()
    until4 = int(cur.execute("""SELECT until4 FROM users
            WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    until5 = int(cur.execute("""SELECT until5 FROM users
            WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    primogems = int(cur.execute("""SELECT primogems FROM users
                WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    text = f"Профиль {nickname}:\n\n" \
           f"Примогемы: {primogems}\n" \
           f"Откручено до 4*: {until4}\n" \
           f"Откручено до 5*: {until5}\n"
    update.message.reply_text(text)


# алгоритм совершения крутки
def do_wish(user_id):
    # вероятность выпадения на крутках
    five_chance = {1: 0.600, 2: 0.596, 3: 0.592, 4: 0.591, 5: 0.586, 6: 0.582, 7: 0.579, 8: 0.575,
                   9: 0.571, 10: 0.568, 11: 0.565, 12: 0.561, 13: 0.558, 14: 0.554, 15: 0.552,
                   16: 0.549, 17: 0.545, 18: 0.541, 19: 0.539, 20: 0.536, 21: 0.531, 22: 0.528,
                   23: 0.525, 24: 0.523, 25: 0.519, 26: 0.517, 27: 0.513, 28: 0.511, 29: 0.507,
                   30: 0.503, 31: 0.501, 32: 0.498, 33: 0.495, 34: 0.491, 35: 0.489, 36: 0.486,
                   37: 0.483, 38: 0.480, 39: 0.477, 40: 0.475, 41: 0.471, 42: 0.469, 43: 0.467,
                   44: 0.464, 45: 0.461, 46: 0.457, 47: 0.456, 48: 0.453, 49: 0.448, 50: 0.447,
                   51: 0.445, 52: 0.442, 53: 0.439, 54: 0.437, 55: 0.434, 56: 0.430, 57: 0.428,
                   58: 0.426, 59: 0.423, 60: 0.420, 61: 0.418, 62: 0.416, 63: 0.413, 64: 0.410,
                   65: 0.408, 66: 0.406, 67: 0.404, 68: 0.401, 69: 0.399, 70: 0.396, 71: 0.393,
                   72: 0.392, 73: 0.388, 74: 6, 75: 12, 76: 18, 77: 24, 78: 30,
                   79: 36, 80: 42, 81: 48, 82: 54, 83: 60, 84: 66, 85: 72,
                   86: 78, 87: 84, 88: 90, 89: 96, 90: 100}
    four_chance = {1: 13, 2: 13, 3: 13, 4: 13, 5: 13, 6: 13, 7: 13, 8: 13,
                   9: 13, 10: 100}
    con = sqlite3.connect("wishdb.db")
    cur = con.cursor()
    # берём из базы данных кол-во открученных до гарантов
    until5 = int(cur.execute("""SELECT until5 FROM users
                        WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    until4 = int(cur.execute("""SELECT until4 FROM users
                            WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    # прибавляем текущую молитву
    until5 += 1
    until4 += 1
    # суммарные шансы выпадения 4* или 5* на текущей крутке
    probability5 = five_chance[until5]
    probability4 = four_chance[until4]
    print(probability5)
    # с учётом вероятности выбираем, выпадет ли 4* или 5*
    is_5 = random.choices([True, False], weights=[probability5, 100 - probability5])[0]
    is_4 = random.choices([True, False], weights=[probability4, 100 - probability4])[0]
    # задаём редкость дропа по полученным данным
    # (5* в приоритете над 4*, т.к. за 10 круток выпадает 4* ИЛИ ВЫШЕ)
    if is_5:
        rare = 5
        until5 = 0
        until4 = 0
    elif is_4:
        rare = 4
        until4 = 0
    else:
        rare = 3
    # береём всех данной редкости
    all = cur.execute("""SELECT * FROM drops
                        WHERE rare = ?""", (rare,)).fetchall()
    # рандомно выбираем что-то из данной редкости
    drop_id = random.randint(0, len(all) - 1)
    drop = all[drop_id]  # вся информация о выпаденном предмете, функция её возвращает
    # обнуляем гарант после пиковой крутки для гаранта
    if until5 == 90:
        until5 = 0
    if until4 == 10:
        until4 = 0
    # обновляем информацию в бд
    cur.execute("""UPDATE users
                        SET until5 = ?
                        WHERE user_id = ?""",
                (until5, user_id))
    cur.execute("""UPDATE users
                            SET until4 = ?
                            WHERE user_id = ?""",
                (until4, user_id))
    con.commit()
    return drop


# одна крутка
def wish(update, context):
    nickname = update.message.from_user.username
    user_id = update.message.from_user.id
    con = sqlite3.connect("wishdb.db")
    cur = con.cursor()
    primogems = int(cur.execute("""SELECT primogems FROM users
                    WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    # если больше 160 примогемов, осуществляем крутку:
    if primogems >= 160:
        primogems -= 160
        drop = do_wish(user_id)
        text = f"{nickname}, вы получили: \n" \
               f"{drop[1]}, {drop[2]}*"
        update.message.reply_photo(photo=open(f'data/{drop[4]}', 'rb'))
        update.message.reply_text(text)
        cur.execute("""UPDATE users
                        SET primogems = ?
                        WHERE user_id = ?""",
                    (primogems, user_id))
        # добавляем выпавшее в инвентарь
        inventory = str(cur.execute("""SELECT inventory FROM users
                    WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
        if inventory:
            inventory = inventory.split()
            inventory.append(str(drop[0]))
            inventory = " ".join(inventory)
        else:
            inventory = []
            inventory.append(str(drop[0]))
            inventory = " ".join(inventory)
        cur.execute("""UPDATE users
                                SET inventory = ?
                                WHERE user_id = ?""",
                    (inventory, user_id))
        con.commit()
    else:
        update.message.reply_text("У вас недостаточно примогемов")


# 10 круток сразу
def wish10(update, context):
    nickname = update.message.from_user.username
    user_id = update.message.from_user.id
    con = sqlite3.connect("wishdb.db")
    cur = con.cursor()
    primogems = int(cur.execute("""SELECT primogems FROM users
                    WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    # если больше 1600 примогемов, осуществляем крутки:
    if primogems >= 1600:
        primogems -= 1600
        drops = sorted([do_wish(user_id) for i in range(10)], key=lambda x: x[2],
                       reverse=True)  # все выпавшее, отсортированное по редкости
        text = f"{nickname}, вы получили: \n"
        for i in drops:
            text += f"{i[1]}, {i[2]}*\n"  # прибавляем к тексту каждый дроп
        update.message.reply_photo(
            photo=open(f'data/{drops[0][4]}', 'rb'))  # отсылаем фото самого редкого
        update.message.reply_text(text)
        # добавляем выпавшее в инвентарь
        inventory = str(cur.execute("""SELECT inventory FROM users
                            WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
        if inventory:
            inventory = inventory.split()
            for i in drops:
                inventory.append(str(i[0]))
            inventory = " ".join(inventory)
        else:
            inventory = []
            for i in drops:
                inventory.append(str(i[0]))
            inventory = " ".join(inventory)
        cur.execute("""UPDATE users
                        SET primogems = ?
                        WHERE user_id = ?""",
                    (primogems, user_id))
        cur.execute("""UPDATE users
                                        SET inventory = ?
                                        WHERE user_id = ?""",
                    (inventory, user_id))
        con.commit()
    else:
        update.message.reply_text("У вас недостаточно примогемов")


# показать инвентарь пользователя
def show_inventory(update, context):
    nickname = update.message.from_user.username
    user_id = update.message.from_user.id
    con = sqlite3.connect("wishdb.db")
    cur = con.cursor()
    inventory = str(cur.execute("""SELECT inventory FROM users
                                WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
    if not inventory:
        update.message.reply_text(f"{nickname}, Ваш инвентарь пуст :(")
        return
    inventory = inventory.split()
    # создаём словарь id предмета : информация о нём
    all_you_have = {}
    for i in inventory:
        if i not in all_you_have:
            rare = cur.execute("""SELECT rare FROM drops
                                            WHERE id = ?""", (int(i),)).fetchall()[0][0]
            type = cur.execute("""SELECT type FROM drops
                                            WHERE id = ?""", (int(i),)).fetchall()[0][0]
            name = cur.execute("""SELECT name FROM drops
                                                        WHERE id = ?""", (int(i),)).fetchall()[0][0]
            amount = inventory.count(i)
            all_you_have[i] = [rare, type, name, amount]
    # сортируем словарь по редкости и типу
    sorted_tuple = sorted(all_you_have.items(), key=lambda x: (-x[1][0], x[1][1]))
    all_you_have = dict(sorted_tuple)
    text = f"{nickname}, Ваш инвентарь:\n\n"
    # добавляем к тексту содержимое инвенторя пользователя
    for i in all_you_have:
        # если персонаж - с6, если оружие - r5 и т.д.
        if all_you_have[i][1] == "character":
            c6 = all_you_have[i][3] // 7  # количество c6
            rest = all_you_have[i][3] % 7  # количество конст, не дошедшее до c6
            # пишем количество c6 + сколько конст помимо этого
            if c6:
                text += f"{all_you_have[i][0]}*: {all_you_have[i][2]} С6 x{c6}\n"
            if rest:
                text += f"{all_you_have[i][0]}*: {all_you_have[i][2]} С{rest - 1}\n"
        else:
            r5 = all_you_have[i][3] // 5  # количество r5
            rest = all_you_have[i][3] % 5  # количество конст, не дошедшее до r5
            # пишем количество r5 + сколько конст помимо этого
            if r5:
                text += f"{all_you_have[i][0]}*: {all_you_have[i][2]} r5 x{r5}\n"
            if rest:
                text += f"{all_you_have[i][0]}*: {all_you_have[i][2]} r{rest}\n"
    update.message.reply_text(text)


# ежедневная порция примогемов :)
def daily(update, context):
    nickname = update.message.from_user.username
    user_id = update.message.from_user.id
    con = sqlite3.connect("wishdb.db")
    cur = con.cursor()
    # берём из бд дату последнего получения ежедневного бонуса
    last_date = cur.execute("""SELECT daily FROM users
                                    WHERE user_id = ?""", (user_id,)).fetchall()[0][0]
    # если таковой не было, добавляем примогемы и текущую дату в бд
    if not last_date:
        primogems = int(cur.execute("""SELECT primogems FROM users
                            WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
        primogems += 640
        update.message.reply_text("Вы получили 640 примогемов!")
        cur.execute("""UPDATE users
                                SET primogems = ?
                                WHERE user_id = ?""",
                    (primogems, user_id))
        # записываем в бд текущую дату по гринвичу
        now_utc = dt.now(timezone.utc)
        cur.execute("""UPDATE users
                                        SET daily = ?
                                        WHERE user_id = ?""",
                    (now_utc, user_id))
        con.commit()
    # если уже когда-то получали бонус - проверяем, прошло ли 24 часа
    else:
        print(last_date)
        # конвертируем строку в дату
        f = '%Y-%m-%d %H:%M:%S'
        last_date = dt.strptime(last_date.split(".")[0], f)
        difference = dt.utcnow() - last_date
        # если не прошло 24 часа - пишем, что нельзя
        if difference.days == 0:
            update.message.reply_text("С момента прошлого получения не прошло 24 часа!")
        # иначе добавляем примогемы и обновляем дату получения
        else:
            primogems = int(cur.execute("""SELECT primogems FROM users
                                        WHERE user_id = ?""", (user_id,)).fetchall()[0][0])
            primogems += 640
            update.message.reply_text("Вы получили 640 примогемов!")
            cur.execute("""UPDATE users
                                            SET primogems = ?
                                            WHERE user_id = ?""",
                        (primogems, user_id))
            now_utc = dt.now(timezone.utc)
            cur.execute("""UPDATE users
                                                    SET daily = ?
                                                    WHERE user_id = ?""",
                        (now_utc, user_id))
            con.commit()
