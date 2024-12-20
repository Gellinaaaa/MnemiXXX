from telebot import TeleBot
from telebot import types
import json
import os
import random
import time
from datetime import datetime, timedelta
import threading

user_data = {}

def get_user_data(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {"blocks": {}}
        print(f"Создан новый профиль для пользователя {chat_id}.")  # Отладочное сообщение
    return user_data[chat_id]

FILE_PATH = "blocks.json"

def load_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

blocks = load_data()

def save_data():
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=4)

token = "7902434008:AAF69cCpY0_k7OHNSKKYFe3k7t9EdExe9go"
bot = TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить новый блок")
    btn2 = types.KeyboardButton("Посмотреть все блоки")
    btn3 = types.KeyboardButton("Добавить новую связку")
    btn4 = types.KeyboardButton("Тренировка памяти")
    btn5 = types.KeyboardButton("Что происходит?")
    btn6 = types.KeyboardButton("Напоминалки")
    btn7 = types.KeyboardButton("Удалить блок")
    btn8 = types.KeyboardButton("Удалить связку")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    bot.send_message(message.chat.id, text= "Вы в главном меню.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "Что происходит?"):
        bot.send_message(message.chat.id, text="Этот телеграмм-бот заточен под помощь с выучиванием некоторых связок. Например, страны и их столицы, слово и его перевод,"
                                               "событие и дата этого события. Для удобства, разделяйте связки на блоки, например, в блоке <перевод> пусть обитают "
                                               "пары слово-перевод. Если есть сложности с заучиванием, добавьте себе вместе со связкой подсказку. Вы сами выбираете, "
                                               "какой блок тренировать."
                                               "Также в меню есть кнопка <Напоминалки>. Там Вы можете настроить периодичность сообщений с частями Ваших связок."
                                               "Так, в течение дня, бот будет присылать Вам напоминания.")
    elif (message.text == "Посмотреть все блоки"):
        view_blocks(message)

    elif (message.text == "Добавить новую связку"):
        add_pair_block_selection(message)

    elif (message.text == "Тренировка памяти"):
        memory_training(message)

    elif (message.text == "Напоминалки"):
        reminders(message)

    elif(message.text == "Добавить новый блок"):
        msg = bot.send_message(message.chat.id, "Введите название нового блока:")
        bot.register_next_step_handler(msg, add_block)

    elif(message.text == "Удалить блок"):
        delete_block(message)

    elif(message.text == "Удалить связку"):
        delete_pair(message)


def add_pair_block_selection(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    if not user_info["blocks"]:
        bot.send_message(chat_id, "Сначала добавьте хотя бы один блок.")
        start_message(message)
        return

    # Генерация кнопок для выбора блока
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for block_name in user_info["blocks"]:
        markup.add(types.KeyboardButton(block_name))

    msg = bot.send_message(chat_id, "Выберите блок, в который хотите добавить связку:", reply_markup=markup)
    bot.register_next_step_handler(msg, add_pair_first)


def add_pair_first(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    # Проверка, существует ли выбранный блок
    block_name = message.text
    if block_name not in user_info["blocks"]:
        bot.send_message(chat_id, "Такого блока не существует. Попробуйте снова.")
        start_message(message)
        return

    user_info["current_block"] = block_name
    msg = bot.send_message(chat_id, "Введите первую часть связки:")
    bot.register_next_step_handler(msg, add_pair_second)


def add_pair_second(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    if "current_block" not in user_info:
        bot.send_message(chat_id, "Ошибка: блок не выбран.")
        start_message(message)
        return

    user_info["current_pair"] = {"first": message.text}
    msg = bot.send_message(chat_id, "Введите вторую часть связки:")
    bot.register_next_step_handler(msg, add_pair_hint)


def add_pair_hint(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    if "current_pair" not in user_info:
        bot.send_message(chat_id, "Ошибка: первая часть связки не найдена.")
        start_message(message)
        return

    user_info["current_pair"]["second"] = message.text
    msg = bot.send_message(chat_id, "Введите подсказку или напишите 'нет':")
    bot.register_next_step_handler(msg, save_pair)


def save_pair(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    hint = message.text if message.text.lower() != "нет" else None
    pair = user_info.pop("current_pair", None)

    if not pair:
        bot.send_message(chat_id, "Ошибка: связка не найдена.")
        start_message(message)
        return

    block_name = user_info["current_block"]
    user_info["blocks"][block_name]["pairs"].append({
        "first": pair["first"],
        "second": pair["second"],
        "hint": hint
    })
    bot.send_message(chat_id, f"Связка добавлена в блок '{block_name}'!")
    start_message(message)  # Возвращаемся в главное меню


def add_block(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)  # Получаем данные пользователя
    block_name = message.text
    if block_name in user_info["blocks"]:
        bot.send_message(chat_id, "Блок с таким названием уже существует.")
    else:
        user_info["blocks"][block_name] = {"pairs": []}
        bot.send_message(chat_id, f"Блок '{block_name}' добавлен!")
    start_message(message)  # Возвращаемся в главное меню


def memory_training(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    if not user_info["blocks"]:
        bot.send_message(chat_id, "Нет доступных блоков для тренировки.")
        return

    # Проверка, есть ли в блоках хотя бы одна связка
    available_blocks = {name: data for name, data in user_info["blocks"].items() if data["pairs"]}
    if not available_blocks:
        bot.send_message(chat_id, "Нет доступных блоков для тренировки.")
        return

    # Генерация кнопок для выбора блока
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for block_name in available_blocks:
        markup.add(types.KeyboardButton(block_name))

    msg = bot.send_message(chat_id, "Выберите блок для тренировки:", reply_markup=markup)
    bot.register_next_step_handler(msg, start_training, available_blocks)


def start_training(message, available_blocks):
    chat_id = message.chat.id
    block_name = message.text

    if block_name not in available_blocks:
        bot.send_message(chat_id, "Ошибка: выбранный блок недоступен для тренировки.")
        return

    # Получение связок из выбранного блока
    pairs = available_blocks[block_name]["pairs"]
    if not pairs:
        bot.send_message(chat_id, "В этом блоке нет связок для тренировки.")
        return

    # Начало тренировки
    user_data[chat_id]["current_training"] = {
        "block_name": block_name,
        "pairs": pairs,
        "index": 0
    }
    send_training_question(chat_id)


def send_training_question(chat_id):
    training = user_data[chat_id]["current_training"]
    pairs = training["pairs"]
    index = training["index"]

    if index >= len(pairs):
        bot.send_message(chat_id, "Тренировка завершена!")
        del user_data[chat_id]["current_training"]
        return

    pair = pairs[index]
    question = pair["first"]
    hint = pair["hint"]

    msg_text = f"Что соответствует: {question}?"
    if hint:
        msg_text += f" (Подсказка: {hint})"

    bot.send_message(chat_id, msg_text)
    bot.register_next_step_handler_by_chat_id(chat_id, check_training_answer)


def check_training_answer(message):
    chat_id = message.chat.id
    training = user_data[chat_id]["current_training"]
    pairs = training["pairs"]
    index = training["index"]

    pair = pairs[index]
    correct_answer = pair["second"]

    if message.text.strip().lower() == correct_answer.lower():
        bot.send_message(chat_id, "Верно!")
    else:
        bot.send_message(chat_id, f"Неверно. Правильный ответ: {correct_answer}")

    # Переход к следующему вопросу
    user_data[chat_id]["current_training"]["index"] += 1
    send_training_question(chat_id)
    start_message(message)  # Возвращаемся в главное меню

def view_blocks(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)
    blocks = user_info["blocks"]

    if not blocks:
        bot.send_message(chat_id, "У вас еще нет созданных блоков.")
        return

    response = "Ваши блоки и их содержимое:\n"
    for block_name, block_data in blocks.items():
        response += f"\n📦 Блок: *{block_name}*\n"
        if not block_data["pairs"]:
            response += "  Пусто\n"
        else:
            for i, pair in enumerate(block_data["pairs"], start=1):
                first = pair["first"]
                second = pair["second"]
                hint = pair.get("hint", "без подсказки")
                response += f"  {i}. {first} - {second} (подсказка: {hint})\n"

    bot.send_message(chat_id, response, parse_mode="Markdown")

def delete_pair(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    if not user_info["blocks"]:
        bot.send_message(chat_id, "У вас нет созданных блоков с связками для удаления.")
        return

    # Генерация кнопок для выбора блока
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for block_name in user_info["blocks"]:
        markup.add(types.KeyboardButton(block_name))

    msg = bot.send_message(chat_id, "Выберите блок, в котором хотите удалить связку:", reply_markup=markup)
    bot.register_next_step_handler(msg, select_pair_for_deletion)

def select_pair_for_deletion(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    block_name = message.text
    if block_name not in user_info["blocks"]:
        bot.send_message(chat_id, "Такого блока не существует. Попробуйте снова.")
        start_message(message)
        return

    # Если в блоке нет связок
    if not user_info["blocks"][block_name]["pairs"]:
        bot.send_message(chat_id, f"В блоке '{block_name}' нет связок для удаления.")
        start_message(message)
        return

    # Генерация списка связок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i, pair in enumerate(user_info["blocks"][block_name]["pairs"], 1):
        markup.add(types.KeyboardButton(f"{i}. {pair['first']} - {pair['second']}"))

    msg = bot.send_message(chat_id, "Выберите связку для удаления:", reply_markup=markup)
    bot.register_next_step_handler(msg, confirm_delete_pair, block_name)

def confirm_delete_pair(message, block_name):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    try:
        # Извлекаем индекс выбранной связки
        pair_index = int(message.text.split('.')[0]) - 1
    except ValueError:
        bot.send_message(chat_id, "Ошибка: выберите правильный вариант.")
        start_message(message)
        return

    if pair_index < 0 or pair_index >= len(user_info["blocks"][block_name]["pairs"]):
        bot.send_message(chat_id, "Ошибка: выбранная связка не существует.")
        start_message(message)
        return

    # Удаление связки
    del user_info["blocks"][block_name]["pairs"][pair_index]
    bot.send_message(chat_id, f"Связка из блока '{block_name}' успешно удалена.")
    start_message(message)  # Возвращаемся в главное меню

def delete_block(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    if not user_info["blocks"]:
        bot.send_message(chat_id, "У вас нет созданных блоков для удаления.")
        return

    # Генерация кнопок для выбора блока
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for block_name in user_info["blocks"]:
        markup.add(types.KeyboardButton(block_name))

    msg = bot.send_message(chat_id, "Выберите блок, который хотите удалить:", reply_markup=markup)
    bot.register_next_step_handler(msg, confirm_delete_block)

def confirm_delete_block(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    block_name = message.text
    if block_name not in user_info["blocks"]:
        bot.send_message(chat_id, "Такого блока не существует. Попробуйте снова.")
        start_message(message)
        return

    # Удаление блока
    del user_info["blocks"][block_name]
    bot.send_message(chat_id, f"Блок '{block_name}' успешно удалён.")
    start_message(message)  # Возвращаемся в главное меню


def reminders(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Раз в 3 часа", "Раз в 6 часов", "Раз в день", "Не отправлять")

    msg = bot.send_message(chat_id, "Как часто вам отправлять напоминания?", reply_markup=markup)
    bot.register_next_step_handler(msg, set_reminder_frequency)

def set_reminder_frequency(message):
    chat_id = message.chat.id
    user_info = get_user_data(chat_id)

    frequency = message.text

    if frequency == "Раз в 3 часа":
        user_info["reminder_frequency"] = 3
    elif frequency == "Раз в 6 часов":
        user_info["reminder_frequency"] = 6
    elif frequency == "Раз в день":
        user_info["reminder_frequency"] = 24
    elif frequency == "Не отправлять":
        user_info["reminder_frequency"] = 0
    else:
        bot.send_message(chat_id, "Неизвестный выбор. Пожалуйста, выберите из предложенных вариантов.")
        reminders(message)
        return

    bot.send_message(chat_id, f"Вы выбрали: {frequency}. Напоминания будут настроены.")
    start_message(message)  # Возвращаемся в главное меню

def send_random_pair(chat_id):
    user_info = get_user_data(chat_id)

    if not user_info["blocks"]:
        bot.send_message(chat_id, "У вас нет доступных блоков для напоминаний.")
        return

    # Выбираем случайный блок
    block_name = random.choice(list(user_info["blocks"].keys()))
    block = user_info["blocks"][block_name]

    if not block["pairs"]:
        bot.send_message(chat_id, f"В блоке '{block_name}' нет связок для напоминания.")
        return

    # Выбираем случайную связку из блока
    pair = random.choice(block["pairs"])
    first_part = pair["first"]

    # Отправляем первую часть связки
    msg = bot.send_message(chat_id, f"Напоминание: {first_part}")

    # Регистрируем следующий шаг для ввода второй части
    bot.register_next_step_handler(msg, check_second_part, pair, chat_id)

# Функция для проверки введенной пользователем второй части
def check_second_part(message, pair, chat_id):
    user_answer = message.text.strip()
    correct_answer = pair["second"].strip()

    # Проверяем правильность ответа
    if user_answer.lower() == correct_answer.lower():
        bot.send_message(chat_id, "Правильно! Молодец!")
    else:
        bot.send_message(chat_id, f"Не совсем. Правильный ответ: {correct_answer}")

    # После ответа возвращаемся к основному меню
    start_message(message)

# Функция для запуска напоминаний по расписанию
def schedule_reminders():
    while True:
        current_time = datetime.now()
        for chat_id, user_info in user_data.items():
            if user_info["reminder_frequency"] > 0:
                # Проверяем время последнего напоминания
                last_reminder_time = user_info.get("last_reminder_time", current_time - timedelta(days=1))
                time_diff = current_time - last_reminder_time

                # Если прошло нужное количество часов
                if time_diff >= timedelta(hours=user_info["reminder_frequency"]):
                    send_random_pair(chat_id)
                    user_info["last_reminder_time"] = current_time

        time.sleep(60 * 60)  # Проверяем каждый час

# Запуск потока для напоминаний
reminder_thread = threading.Thread(target=schedule_reminders)
reminder_thread.daemon = True  # Поток завершится при завершении программы
reminder_thread.start()



bot.polling(none_stop=True)