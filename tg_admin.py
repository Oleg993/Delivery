import sqlite3
import telebot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)
import DB_project as project
import os

bot = telebot.TeleBot('6386657547:AAGDz06oEBlutexV47VOPv_FfXen3Dv2Ja0')
# Список названий для кнопок СпуерАдмин
super_admin_btns = ['Добавить товар', 'Удалить товар', 'Товар на паузу', 'Редактировать товар',
                    'Добавить администратора', 'Удалить администратора', 'Изменить статус администратора',
                    'Редактировать комментарии', 'Добавить ключ доступа', 'Удалить ключ доступа',
                    'Блокировка пользователей']

# Список названий для кнопок обычный Админ
normal_admin_btns = ['Добавить товар', 'Удалить товар', 'Товар на паузу', 'Редактировать товар',
                     'Редактировать комментарии', 'Блокировка пользователей']


# Главное меню (Меню пользователя, Панель администратора)
def first_markup():
    """Кнопки: Меню пользователя, Панель администратора"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Меню пользователя'), KeyboardButton('Панель администратора'))
    return markup


# Кнопка Назад
def markup_back():
    """Возвращает в главное меню"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('В меню', callback_data='admin_menu'))
    return markup


# Меню категорий товаров
def categories_markup(category_name=None, start_ind=0):
    """:param category_name: название категории для удаления, редактирования и тд. добавляет приставку
    :param start_ind: Индекс начала отображения товаров
    :return: Возвращает меню категорий товаров с разными callback кнопками в зависимости от категории """
    categories = project.get_categories()
    finish_ind = start_ind + 5
    if finish_ind > len(categories):
        finish_ind = len(categories)
    if start_ind < 0:
        start_ind = 0
    if not categories:
        return 'Нет доступных категорий.'
    else:
        ctg_names = {'Удалить товар': 'delete_category', 'Товар на паузу': 'pause_category',
                     'Редактировать товар': 'edit_category', 'Редактировать комментарии': 'edit_comments'}
        markup = InlineKeyboardMarkup()
        if category_name is not None:
            for category in categories[start_ind:finish_ind]:
                markup.add(InlineKeyboardButton(category, callback_data=f"{ctg_names[category_name]} {category}"))
            if start_ind >= 5:
                markup.add(InlineKeyboardButton('Назад',
                                                callback_data=f"КтгНазад,{ctg_names[category_name]},{start_ind - 5}"))
            if finish_ind < len(categories):
                markup.add(InlineKeyboardButton('Вперед',
                                                callback_data=f"КтгВперед,{ctg_names[category_name]},{start_ind + 5}"))
        else:
            for category in categories[start_ind:finish_ind]:
                markup.add(InlineKeyboardButton(category, callback_data=f"ПростоКатегория,{category}"))
            if start_ind >= 5:
                markup.add(InlineKeyboardButton('Назад', callback_data=f"ПростоКатегория,{start_ind - 5}"))
            if finish_ind < len(categories):
                markup.add(InlineKeyboardButton('Вперед', callback_data=f"ПростоКатегория,{start_ind + 5}"))
        markup.add(InlineKeyboardButton('Назад', callback_data='admin_menu'))
    return markup


def products_markup(category, ctg_action, start_ind=0):
    """:param category: Название категории как в таблице
    :param ctg_action: Приставка перед названием категории для передачи в callback
    :param start_ind: Индекс начала отображения товаров
    :return: Кнопки с разным callback в зависимости от выбранного действия"""
    goods = project.get_from_category(category)
    finish_ind = start_ind + 5
    if finish_ind > len(goods):
        finish_ind = len(goods)
    if start_ind < 0:
        start_ind = 0
    markup = InlineKeyboardMarkup()
    actions = {'delete_category': 'del', 'pause_category': 'pause', 'edit_category': 'edit', 'edit_comments': 'd_com'}
    if ctg_action == 'pause_category':
        for good in goods[start_ind:finish_ind]:
            markup.add(InlineKeyboardButton(f"{good[0]} - {good[1]}", callback_data=f"{actions[ctg_action]} {good}"))
        if start_ind >= 5:
            markup.add(InlineKeyboardButton('Назад', callback_data=f"Назад,{category},{ctg_action},{start_ind-5}"))
        if finish_ind < len(goods):
            markup.add(InlineKeyboardButton('Вперед', callback_data=f"Вперед,{category},{ctg_action},{start_ind+5}"))
    else:
        for good in goods[start_ind:finish_ind]:
            markup.add(InlineKeyboardButton(good[0], callback_data=f"{actions[ctg_action]} {good[0]}"))
        if start_ind >= 5:
            markup.add(InlineKeyboardButton('Назад', callback_data=f"Назад,{category},{ctg_action},{start_ind-5}"))
        if finish_ind < len(goods):
            markup.add(InlineKeyboardButton('Вперед', callback_data=f"Вперед,{category},{ctg_action},{start_ind+5}"))
    markup.add(InlineKeyboardButton('В меню', callback_data=f"prod_m {category} {ctg_action}"))
    return markup


def admin_menu(status=None):
    """:param status: Если запускать с super то вернет СуперАдмин кнопки, если без super то для обыяного
    :return: Возвращает кнопки для админ панели"""
    markup = InlineKeyboardMarkup()
    if status == 'super':
        for btn in super_admin_btns:
            markup.add(InlineKeyboardButton(btn, callback_data=btn))
    else:
        for btn in normal_admin_btns:
            markup.add(InlineKeyboardButton(btn, callback_data=btn))
    return markup


# Меню список админов
def show_admins(delete_or_change, user_id, start_ind=0):
    """:param delete_or_change: 'delete' - для удаления, 'change' - изменение статуса админа
    :param user_id: id админа
    :param start_ind: id индекс с которого отображаются ключи
    :return: Кнопки с именами админов кроме того админиа который вызывает(чтобы сам себя не удалил)"""
    admins = project.show_admins(user_id)
    finish_ind = start_ind + 5
    if finish_ind > len(admins):
        finish_ind = len(admins)
    if start_ind < 0:
        start_ind = 0
    if not admins:
        return 'Вы являетесь единственным администратором.'
    else:
        markup = InlineKeyboardMarkup()
        for admin in admins[start_ind:finish_ind]:
            markup.add(InlineKeyboardButton(f"{admin[0]} c правами {admin[-1]} категории",
                                            callback_data=f"{delete_or_change} {admin[1]}"))
        if start_ind >= 5:
            markup.add(InlineKeyboardButton('Назад',
                                            callback_data=f"НазадАдмин,{delete_or_change},{user_id},{start_ind - 5}"))
        if finish_ind < len(admins):
            markup.add(InlineKeyboardButton('Вперед',
                                            callback_data=f"ВпередАдмин,{delete_or_change},{user_id},{start_ind + 5}"))
        markup.add(InlineKeyboardButton('В меню', callback_data='admin_menu'))
        return markup


# Список комментариев
def show_comments(good_name):
    """:param good_name: Название товара
    :return: Список комментариев"""
    comments = project.show_comments(good_name)
    if comments == 'Комментарии отсутствуют':
        return 'Комментарии отсутствуют'
    else:
        count = 1
        result = ''
        for comment in comments:
            result += f"{count}) id:{comment[0]}, content:{comment[1]}\n"
            count += 1
        return result


# Список ключей доступа
def show_keys(start_ind=0):
    """:param start_ind: индекс с которого отображаются ключи
    :return:Возвращает список доступных ключей доступа."""
    keys = project.show_keys()
    finish_ind = start_ind + 5
    if finish_ind > len(keys):
        finish_ind = len(keys)
    if start_ind < 0:
        start_ind = 0
    if keys:
        markup = InlineKeyboardMarkup()
        for key in keys[start_ind:finish_ind]:
            markup.add(InlineKeyboardButton(f"{key[0]}, key: {key[1]}, status {key[-1]}\n",
                                            callback_data=f"del_key {key[0]}"))
        if start_ind >= 5:
            markup.add(InlineKeyboardButton('Назад', callback_data=f"НазадКлючи,{start_ind-5}"))
        if finish_ind < len(keys):
            markup.add(InlineKeyboardButton('Вперед', callback_data=f"ВпередКлючи,{start_ind+5}"))
        markup.add(InlineKeyboardButton('В меню', callback_data='admin_menu'))
        return markup
    else:
        return 'Ключи отсутствуют'


@bot.message_handler(commands=['start'])
def start(message):
    """Проверяет находился ли в БлэкЛисте, является ли новым пользователем, является ли админом
    :param message: команда /start
    :return: Возвращает клавиатуру если Админ, предлагает регистрацию если новый, шлет подальше если в блэке """
    if message.text == '/start':
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        if not project.is_in_black_list(user_id):
            if not project.is_new(user_id):
                if not project.is_admin(user_id):
                    bot.send_message(message.chat.id, f"Привет {user_name} выбирай.", reply_markup=categories_markup())
                else:
                    bot.send_message(message.chat.id, f"Привет {user_name} выбирай.", reply_markup=first_markup())
            else:
                bot.send_message(message.chat.id, f"Привет {user_name} ты у нас новенький, давай зарегистрируемся!?")
                # project.registrator()
        else:
            bot.send_message(message.chat.id, f"Привет {user_name} ты у нас в черном списке, давай до свидания.")


@bot.message_handler(content_types=['text'])
def show_main_panel(message):
    """Проверяет какими полномочиями наделен Админ для отображения меню
    :return: отображает админ панель в зависимости от полномочий админа"""
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if project.is_admin(user_id):
        if message.text == 'Панель администратора':
            if project.is_super_admin(message.from_user.id):
                bot.send_message(message.chat.id, f"Привет {user_name}, ты наделен правами Супер Администратора.",
                                 reply_markup=admin_menu('super'))
            else:
                bot.send_message(message.chat.id, f"Привет {user_name}, ты наделен правами Администратора.",
                                 reply_markup=admin_menu())
        elif message.text == 'Меню пользователя':
            bot.send_message(message.chat.id, f"Привет {user_name}, выбирай:", reply_markup=categories_markup())
    else:
        bot.send_message(message.chat.id, f"Привет {user_name}, ты не наделен правами Администратора.",
                         reply_markup=first_markup())


@bot.callback_query_handler(func=lambda call: True)
def show_admin_panel(call):
    print(call.data)
    user_id = call.from_user.id
    if call.data == 'Добавить товар':
        bot.send_message(call.message.chat.id, """Введите данные в формате:\n\nКатегория(Блюда, Напитки и т.д.)/
Уникальное название(до 35 символов)/\nОписание товара(до 500 символов)/\nЦена(формат 1.99)/
Время приготовления(30- если 30 минут)/\nВес товара(в граммах)\n\nВвод данных через слэш '/'.""",
                         reply_markup=markup_back())
        bot.register_next_step_handler(call.message, add_photo)

    elif call.data in ['Удалить товар', 'Товар на паузу', 'Редактировать товар', 'Редактировать комментарии']:
        categories = categories_markup(call.data)
        if isinstance(categories, str):
            bot.send_message(call.message.chat.id, categories, reply_markup=markup_back())
        else:
            bot.send_message(call.message.chat.id, f"Выберите категорию товара:", reply_markup=categories)

    elif call.data == 'Добавить администратора':
        bot.send_message(call.message.chat.id, """Введите данные нового администратора в формате:
id/ имя/ статус цифрой(1 - суперАдмин, 0 - обычный)""", reply_markup=markup_back())
        bot.register_next_step_handler(call.message, add_new_admin)

    elif call.data == 'Удалить администратора':
        admins_markup = show_admins('delete', user_id)
        if isinstance(admins_markup, str):
            bot.send_message(call.message.chat.id, admins_markup, reply_markup=markup_back())
        else:
            bot.send_message(call.message.chat.id, "Список администраторов:\n(нажмите на кнопку для удаления)",
                             reply_markup=admins_markup)

    elif call.data.split()[0] == 'delete':
        if project.delete_admin(call.data[6:].strip()):
            admins_markup = show_admins('delete', user_id)
            if isinstance(admins_markup, str):
                bot.send_message(call.message.chat.id, admins_markup, reply_markup=markup_back())
            else:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=show_admins('delete', user_id))
                bot.send_message(call.message.chat.id, f"Администратор id: {call.data[6:].strip()} удален.")

    elif call.data == 'Изменить статус администратора':
        admins_markup = show_admins('change', user_id)
        if isinstance(admins_markup, str):
            bot.send_message(call.message.chat.id, admins_markup, reply_markup=markup_back())
        else:
            bot.send_message(call.message.chat.id, "Список администраторов:\n(нажмите на кнопку для изменения статуса)",
                             reply_markup=show_admins('change', user_id))

    elif call.data.split()[0] == 'change':
        if project.change_admin_status(call.data[6:].strip()):
            admins_markup = show_admins('change', user_id)
            if isinstance(admins_markup, str):
                bot.send_message(call.message.chat.id, admins_markup, reply_markup=markup_back())
            else:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=show_admins('change', user_id))
                bot.send_message(call.message.chat.id, f"Статус администратора id: {call.data[6:].strip()} изменен.")

    elif call.data.split()[0] in ['delete_category', 'pause_category', 'edit_category', 'edit_comments']:
        categories = {'delete_category': 'удаления',
                      'pause_category': 'установки/снятия паузы\n0- не на паузе, 1- на паузе',
                      'edit_category': 'редактирования', 'edit_comments': 'редактирования'}
        bot.send_message(call.message.chat.id, f"Выберите товар для {categories[call.data.split()[0]]}:",
                         reply_markup=products_markup(call.data.split()[-1], call.data.split()[0]))

    elif call.data.split()[0] == 'del':
        if project.delete_goods(call.data[4:]):
            bot.send_message(call.message.chat.id, f"Товар: {call.data[4:]} удален.",
                             reply_markup=categories_markup('Удалить товар'))

    elif call.data.split()[0] == 'pause':
        if project.set_on_pause(call.data[8:-5]):
            bot.send_message(call.message.chat.id, f"Установена/снята пауза для товара: {call.data[8:-5].strip()}.",
                             reply_markup=categories_markup('Товар на паузу'))

    elif call.data.split()[0] == 'edit':
        product = call.data[5:]
        old_product = project.show_product_card(product)
        good_name = old_product[2]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Назад', callback_data='admin_menu'))
        bot.send_photo(call.message.chat.id, old_product[-1], caption=f"Категория: {old_product[1]}\nНазвание: {old_product[2]}\nОписание: {old_product[3]}\nЦена: {old_product[4]}\nВремя приготовления: {old_product[5]}\nВес: {old_product[7]}")
        bot.send_message(call.message.chat.id, """Введите новые данные о товаре:\n
Категория (Блюда, Напитки и т.д.)\nНазвание (до 35 символов)\nОписание товара до 500 символов)\nЦена (формат 1.99)
Время приготовления (30- если 30 минут)\nВес (в граммах)\n\nФото загружается после притнятия всех текстовых данны.
\nВвод данных через слэш "/".""", reply_markup=markup)
        bot.register_next_step_handler(call.message, correct_goods, good_name)

    elif call.data.split()[0] == 'd_com':
        product = call.data[6:]
        comments = show_comments(product)
        if comments == 'Комментарии отсутствуют':
            bot.send_message(call.message.chat.id, comments, reply_markup=markup_back())
        else:
            bot.send_message(call.message.chat.id, f"Список доступных комментариев:\nВведите id комментария, который необходимо удалить:\n\n{comments}", reply_markup=markup_back())
        bot.register_next_step_handler(call.message, delete_comment, product)

    elif call.data == 'Добавить ключ доступа':
        bot.send_message(call.message.chat.id, """Введите новый ключ доступа в формате:
ключ доступа, статус цифрой(1 - суперАдмин, 0 - обычный)""", reply_markup=markup_back())
        bot.register_next_step_handler(call.message, add_new_key)

    elif call.data == 'Удалить ключ доступа':
        keys_markup = show_keys()
        if isinstance(keys_markup, str):
            bot.send_message(call.message.chat.id, keys_markup, reply_markup=markup_back())
        else:
            bot.send_message(call.message.chat.id, "Список доступных ключей:\n(нажмите на кнопку для удаления)",
                             reply_markup=keys_markup)

    elif call.data == 'Блокировка пользователей':
        users = project.show_users(user_id)
        res = ''
        for i in users:
            res += f"Имя: {i[0]}, id:{i[1]}, статус: {i[2]}\n"
        if len(users) == 0:
            bot.send_message(call.message.chat.id, 'Нет других пользователей', reply_markup=markup_back())
        else:
            bot.send_message(call.message.chat.id,
                             f"Список пользователей:\n(введите ID пользователя для блокировки/разблокироваки"
                             f"\n(Статус: 1-заблокирован, 0 -не заблокирован))\n\n{res}",
                             reply_markup=markup_back())
            bot.register_next_step_handler(call.message, block_unblock_user)

    elif call.data.split()[0] == 'del_key':
        key_id = call.data[8:].strip()
        project.delete_key(key_id)
        if isinstance(show_keys(), str):
            bot.send_message(call.message.chat.id, f"Ключ доступа id: {key_id} удален.\n\n{show_keys()}",
                             reply_markup=markup_back())
        else:
            bot.send_message(call.message.chat.id, f"Ключ доступа id: {key_id} удален.", reply_markup=show_keys())

    elif call.data == 'admin_menu':
        if project.is_super_admin(call.from_user.id):
            bot.send_message(call.message.chat.id, f"Панель администратора:", reply_markup=admin_menu('super'))
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, f"Панель администратора:", reply_markup=admin_menu())
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.send_message(call.message.chat.id, f"Для выхода в главное меню: --> /start")

    elif call.data.split()[0] == 'prod_m':
        category = call.data.split()[-1]
        categories = {'delete_category': 'Удалить товар', 'pause_category': 'Товар на паузу',
                      'edit_category': 'Редактировать товар', 'edit_comments': 'Редактировать комментарии'}
        if project.is_super_admin(call.from_user.id):
            bot.send_message(call.message.chat.id, f"Выбирай:", reply_markup=categories_markup(categories[category]))
            bot.send_message(call.message.chat.id, f"Для выхода в главное меню: --> '/start'")

    elif call.data.split(',')[0] in ['Вперед', 'Назад']:
        category = call.data.split(',')[1].strip()
        action = call.data.split(',')[2].strip()
        start_ind = int(call.data.split(',')[-1])
        if project.is_super_admin(call.from_user.id):
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=products_markup(category, action, start_ind))

    elif call.data.split(',')[0] in ['КтгНазад', 'КтгВперед']:
        ctg_name = call.data.split(',')[2].strip()
        start_ind = int(call.data.split()[-1])
        if project.is_super_admin(call.from_user.id):
            bot.send_message(call.message.chat.id, "Выбирай:", reply_markup=categories_markup(ctg_name, start_ind))
            bot.send_message(call.message.chat.id, f"Для выхода в главное меню? --> '/start'")

    elif call.data.split(',')[0] == 'ПростоКатегория':
        ctg_name = call.data.split(',')[1].strip()
        start_ind = int(call.data.split()[-1])
        if project.is_super_admin(call.from_user.id):
            bot.send_message(call.message.chat.id, "Выбирай:", reply_markup=categories_markup(start_ind))
            bot.send_message(call.message.chat.id, f"Для выхода в главное меню? --> '/start'")

    elif call.data.split(',')[0] in ['ВпередКлючи', 'НазадКлючи']:
        start_ind = int(call.data.split(',')[-1])
        if project.is_super_admin(call.from_user.id):
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=show_keys(start_ind))

    elif call.data.split(',')[0] in ['ВпередАдмин', 'НазадАдмин']:
        start_ind = int(call.data.split(',')[-1])
        delete_or_change = call.data.split(',')[1]
        user_id = call.data.split(',')[2]
        if project.is_super_admin(call.from_user.id):
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=show_admins(delete_or_change, user_id, start_ind))


# Добавление фото к полученным данным по новому товару. Запуск функции с загрузкой данных в БД
def add_photo(data):
    """Добавление фото к полученным данным, запуск функции с загрузкой в БД
    :param data: данные товара введенные пользователем
    :return: Запуск функции с загрузкой данных в БД, Перезапуск запроса на добавление фото если ошибка"""
    product_data = [i.strip() for i in data.text.split('/')]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Отмена', callback_data='admin_menu'))
    # считаем правильное ли количество данных введено
    if len(product_data) == 6:
        bot.send_message(data.chat.id, f"Добавьте фотографию для товара.", reply_markup=markup)
        return bot.register_next_step_handler(data, add_to_db, product_data)
    else:
        bot.send_message(data.chat.id, """Что-то пошло не так.\n\nВведите данные в формате:\n
Категория(Блюда, Напитки и т.д.)/\nУникальное название(до 35 символов)/\nОписание товара(до 500 символов)/
Цена(формат 1.99)/\nВремя приготовления(30- если 30 минут)/\nВес товара(в граммах)/
\nВвод данных через слэш '/'.""", reply_markup=markup)
        return bot.register_next_step_handler(data, add_photo)


# Изменение карточки товара
def correct_goods(message, good_name):
    """:param message: Данные полученные от пользователя
    :param good_name: Название продукта
    :return: Запуск функции загрузки в БД или перезапуск данной функции в случае не верно введенных данных"""
    new_data = [i.strip() for i in message.text.split('/')]
    if len(new_data) == 6:
        bot.send_message(message.chat.id, f"Добавьте фотографию для товара:", reply_markup=markup_back())
        return bot.register_next_step_handler(message, add_correct_data_to_db, new_data, good_name)
    else:
        bot.send_message(message.chat.id, f"""Не верный ввод данных.\nВведите новые данные о товаре:\n
Категория(Блюда, Напитки и т.д.)/\nУникальное название(до 35 символов)/\nОписание товара(до 500 символов)/
Цена(формат 1.99)/\nВремя приготовления(30- если 30 минут)/\nВес товара(в граммах)/
\nВвод данных через слэш '/'.""", reply_markup=markup_back())
        return bot.register_next_step_handler(message, correct_goods, good_name)


# Получение фото и добавление данных в БД
def add_to_db(message, product_data):
    file_id = message.photo[-1].file_id # ID картинки
    file_path = bot.get_file(file_id).file_path # путь для скачивания картинки из ТГ
    file_extension = os.path.splitext(file_path)[1] # забираем формат картинки
    img_path = f'imgs/{file_id}{file_extension}' # путь к картинке в папке
    downloaded_file = bot.download_file(file_path) # скачиваем картинку из ТГ

    # сохраняем картинку в папку
    with open(img_path, 'wb') as new_img:
        new_img.write(downloaded_file)

    product_data.extend([img_path, file_id])
    if project.add_new_goods(product_data):
        bot.send_message(message.chat.id, f"Продукт: '{product_data[1]}' успешно добавлен.", reply_markup=markup_back())
    else:
        bot.send_message(message.chat.id, f"Что-то пошло не так!!!", reply_markup=markup_back())


# Внесение изменений в карточку товара
def add_correct_data_to_db(message, new_data, good_name):
    print("запуск")
    file_id = message.photo[-1].file_id  # ID картинки
    file_path = bot.get_file(file_id).file_path  # путь для скачивания картинки из ТГ
    file_extension = os.path.splitext(file_path)[1]  # забираем формат картинки
    img_path = f'imgs/{file_id}{file_extension}'  # путь к картинке в папке
    downloaded_file = bot.download_file(file_path)  # скачиваем картинку из ТГ

    with open(img_path, 'wb') as new_img:
        new_img.write(downloaded_file)

    new_data.extend([img_path, file_id])
    try:
        if project.correct_goods(good_name, new_data):
            bot.send_message(message.chat.id, f"Продукт: '{new_data[1]}' успешно изменен.")
            bot.send_photo(message.chat.id, file_id,
                           caption=f"Категория: {new_data[0]}\nНазвание: {new_data[1]}\nОписание: {new_data[2]}\nЦена: {new_data[3]}\nВремя приготоваления: {new_data[4]}\nВес: {new_data[5]}",
                           reply_markup=markup_back())
    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Что-то пошло не так: {e}", reply_markup=markup_back())


def add_new_admin(message):
    """:param message: id, имя и статус нового админа
    :return: добавляет в базу или перезапускается в случае ошибки"""
    data = [i.strip() for i in message.text.split('/')]
    if data[0].isdigit and data[-1] in ['0', '1']:
        project.add_new_admin(int(data[0]), data[1], data[2])
        return bot.send_message(message.chat.id, f"Администратор: {data[1]} c правами {data[-1]} категории, добавлен.",
                                reply_markup=markup_back())
    else:
        bot.send_message(message.chat.id, """Неверный формат данных
Введите данные нового администратора в формате: 
id/ имя/ статус цифрой(1 - суперАдмин, 0 - обычный)""")
        return bot.register_next_step_handler(message, add_new_admin)


# Удаление коментариев
def delete_comment(message, product):
    """:param message: id коммента
    :param product: название продукта
    :return: удаялет комментарий или перезаупускает функцию в случае ошибки"""
    if project.delete_comment(message.text):
        comments = show_comments(product)
        if comments != 'Комментарии отсутствуют':
            bot.send_message(message.chat.id, f"Комментарий id: {message.text}, удален.\n"
                                              f"Выберите новый комментарий для удаления:\n\n{comments}",
                             reply_markup=markup_back())
            bot.register_next_step_handler(message, delete_comment, product)
    else:
        bot.send_message(message.chat.id, """Неверный формат данных.
Введите id комментария, который необходимо удалить.""", reply_markup=markup_back())
        return bot.register_next_step_handler(message, delete_comment, product)


# Добавление нового ключа
def add_new_key(message):
    """:param message: текст с данными ключа и статусом(1-супер, 0 - обычный)
    :return: Добавляет ключ или перезапускается в слувае ошибки"""
    data = [i.strip() for i in message.text.split('/')]
    if data[0] and data[-1] in ['1', '0']:
        project.add_new_key(data[0], data[1])
        return bot.send_message(message.chat.id, f"""Ключ доступа: {data[0]} c правами {data[-1]} категории, добавлен.\n
Введите новый ключ доступа в формате: ключ доступа, статус цифрой(1 - суперАдмин, 0 - обычный)""",
                                reply_markup=markup_back())
    else:
        bot.send_message(message.chat.id, """Неверный формат данных.
Введите новый ключ доступа в формате:
ключ доступа, статус цифрой(1 - суперАдмин, 0 - обычный)""", reply_markup=markup_back())
        return bot.register_next_step_handler(message, add_new_key)


def block_unblock_user(message):
    main_user = message.from_user.id
    try:
        if message.text.isdigit():
            user_to_change = int(message.text)
            if project.block_unblock_user(user_to_change):
                users = project.show_users(main_user)
                res = ''
                for i in users:
                    res += f"Имя: {i[0]}, id:{i[1]}, статус: {i[2]}\n"
                bot.send_message(message.chat.id, f"Пользователь с ID:{user_to_change} заблокирован/разблокирован.\n\n"
                                 f"Список пользователей:\n(введите ID пользователя для блокировки/разблокироваки\n"
                                 f"(Статус: 1-заблокирован, 0 -не заблокирован))\n\n{res}", reply_markup=markup_back())
                bot.register_next_step_handler(message, block_unblock_user)
        else:
            bot.send_message(message.chat.id, f"Введен некорректный ID пользователя!\n"
                                              f"Введите ID пользователя для блокировки/разблокироваки"
                                              f"\n(Статус: 1-заблокирован, 0 -не заблокирован))\n\n"
                             , reply_markup=markup_back())
            bot.register_next_step_handler(message, block_unblock_user)
    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Что-то пошло не так: {e}", reply_markup=markup_back())


print('ready')
bot.polling(none_stop=True)
