import sqlite3
from datetime import datetime

import telebot
import imghdr

bot = telebot.TeleBot('6386657547:AAGDz06oEBlutexV47VOPv_FfXen3Dv2Ja0')


# В БЛЭКЕ ИЛИ НЕТ +
def is_in_black_list(user_id):
    """проверка в блэке или нет
    True - в блэке, False - нет"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT block_status FROM Users WHERE id == ?", [user_id])
        result = cursor.fetchone()
        if len(result) == 0:
            return False
        return True


# НОВЫЙ ПОЛЬЗОВАТЕЛЬ ИЛИ НЕТ +
def is_new(user_id):
    """проверка новый пользователь или нет
     True - новый, False - есть в базе"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM Users WHERE id == ?", [user_id])
        result = cursor.fetchone()
        if len(result) == 0:
            return True
        return False


# ЯВЛЯЕТСЯ ЛИ АДМИНОМ +
def is_admin(user_id):
    """проверяем является ли админом, если да, то с какими полномочиями
       False если не админ"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT is_admin, is_super_admin 
                                FROM Users
                                JOIN Admins ON Users.id = Admins.user_id 
                                WHERE Users.id == ?""", [user_id])
        result = cursor.fetchone()
        if len(result) == 0:
            return False
        return 'Суперадмин' if result[1] == 1 else 'Обычный'


# РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ +
def registrator(user_data):
    """принимает список данных [id, user_name, phone_number, birthday (формат ввода '01.01.2023')] и записываем в БД"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Users(id, user_name, phone_number, birthday) VALUES (?, ?, ?, ?)",
                       user_data)
        cursor.execute("SELECT user_name FROM Users WHERE id = ?", [user_data[0]])
        data = cursor.fetchone()
        if len(data) == 0:
            return f'Не удалось добавить пользователя {user_data[1]} в БД.'
        return f'Пользователь {user_data[1]} добавлен в базу данных.'


# СПИСОК КАТЕГОРИЙ +
def get_categories():
    """возвращаем списка названий категорий"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Categories GROUP BY name")
        result = cursor.fetchall()
        if len(result) == 0:
            return "Не удалось загрузить список категорий."
        return [i[0] for i in result]


# СПИСОК ТОВАРОВ В ВЫБРАННОЙ КАТЕГОРИИ +
def get_from_category(category_name, is_on_pause=None):
    """возвращаем список всех названий товаров в категории и их id например [(name), (name)]
    для возврата товаров которые на паузе вызываем функцию с is_on_pause = 1, не на паузе is_on_pause = 2"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        query = ("""SELECT DISTINCT Goods.name FROM Goods 
                   JOIN Categories ON Categories.description = Goods.category
                   WHERE Categories.category_name = ?""")
        if is_on_pause is not None:
            query += " AND is_on_pause = ?"
            cursor.execute(query, [category_name, is_on_pause])
        else:
            cursor.execute(query, [category_name])
        result = cursor.fetchall()
        if len(result) == 0:
            return f"Не удалось загрузить список товаров категории: '{category_name}'"
        return [i[0] for i in result]


# КАРТОЧКА ВЫБРАННОГО ТОВАРА +
def get_product_card(product_name):
    """возвращает картеж с данными для карточки товара"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT name, image, good_description, weight, price, ranking
                       FROM Goods WHERE name = ?""", [product_name])
        result = cursor.fetchone()
        if len(result) == 0:
            return f"Не удалось загрузить карточку товара: '{product_name}'"
        return result


# ЗАГРУЗКА ДАННЫХ В БД ПОСЛЕ ПОДТВЕРЖДЕНИЯ ЗАКАЗА               !!!--- прорить после создания корзины ---!!!
def from_cart_into_db(cart, goods_info):
    """помещаем заказ из корзины в БД
    создать списки в которых будут храниться товары из карзины, данные по товару
    а при подтверждении заказа забираем товары из словаря и вносим в базу
    cart = [user_id, user_tel, address, total_price, order_status, order_date, delivery_time, user_note]
    goods_info = [{'good_id':111, 'quantity':1}, {'good_id':222, 'quantity':2}]
    находим order_id = cursor.lastrowid чтобы корректно поместить данные в таблицу"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO Order (user_id, user_tel, address, total_price, order_status, order_date, 
        delivery_time, user_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", cart)
        db.commit()
    order_id = cursor.lastrowid
    for good in goods_info:
        cursor.execute("""INSERT INTO Goods_in_order (order_id, good_id, quantity) VALUES(?, ?, ?)""",
                       [order_id, good['good_id'], good['quantity']])
        db.commit()
    # если нужно посмотреть, прошла ли загрузка
    cursor.execute("""SELECT * FROM Order
                            JOIN Goods_in_order ON Goods_in_order.order_id = Order.id
                            where Order.id = ?""", [order_id])
    data = cursor.fetchall()
    if len(data) == 0:
        return 'Не удалось добавить товар в таблицу Order'
    return order_id


# НОМЕР ЗАКАЗА И ВРЕМЯ ПРИГОТОВЛЕНИЯ + 30 МИН. +                !!!--- перепроверить после создания корзины ---!!!
def show_order_info(order_id):
    """показываем id добавленного товара и время приготовления времязатратного блюда + 30 мин.
    забираем результат возвращенный функцией from_cart_into_db т.к. он возвращает order_id
    например order_id = from_cart_into_db(cart, goods_info)"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("""
                    SELECT Orders.id, MAX(Goods.time_to_ready) + 30
                    FROM Orders
                    JOIN Goods_in_order ON Orders.id = Goods_in_order.order_id
                    JOIN Goods ON Goods_in_order.good_id = Goods.id
                    WHERE Orders.id = ?
                    GROUP BY Orders.id
                """, [order_id])
        result = cursor.fetchone()
        if len(result) == 0:
            return 'Заказ не найден'
        return result


    # КОРТЕЖ ДАННЫХ ПОЛЬЗОВАТЕЛЯ +
def get_user_data(user_id):
    """Возвращаем из БДданные пользователя  в виде кортежа с данными ()
       Параметр вводить ввиде строки"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users where id = ?", [user_id])
        result = cursor.fetchone()
        if len(result) == 0:
            return f"Пользователь с id: {user_id} не найден в БД"
        return result


# КОРТЕЖ ДАННЫХ АДМИНА +
def get_admin_data(user_id):
    """возвращаем кортеж с данными об админе (ID, name, полномочия(1-супер, 2- обычный))"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT Users.id, Users.user_name, Admins.is_super_admin 
                                FROM Users
                                JOIN Admins ON Users.id = Admins.user_id 
                                WHERE Users.id = ?""", [user_id])
        result = cursor.fetchone()
        if len(result) == 0:
            return f"Пользователь с id: {user_id} не обладает правами администратора"
        return result


# СПИСОК КОММЕНТАРИЕВ +
def get_comments(good_id):
    """достаем все комментарии в виде [(comment_id, коммент, пользователь), (comment_id, коммент, пользователь)]
    good_id забираем из функции get_from_category"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT Comment.id, Comment.content, Users.user_name
                                FROM Comments
                                JOIN Comment ON Comments.comment_id = Comment.id
                                JOIN Users ON Comment.from_user = Users.id
                                WHERE Comments.good_id = ?""", [good_id])
        result = cursor.fetchall()
        if len(result) == 0:
            return 'Комментарии отсутствуют'
        return result


# ДОБАВЛЕНИЕ КОММЕНТАРИЯ +
def add_comment(good_id, user_id, content):
    """добавляем новый комментарий
    возвращаем f"Комментарий {comment_id} от пользователя {user_id} добавлен.
    передавать все значения в виде строк"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Comment (content, from_user) VALUES (?, ?)", [content, user_id])
        comment_id = cursor.lastrowid

        cursor.execute("INSERT INTO Comments (comment_id, good_id, user_id) VALUES (?, ?, ?)",
                       [comment_id, good_id, user_id])
        cursor.execute("""SELECT Comments.id, Comment.from_user FROM Comment
                                    JOIN Comments ON Comment.id = Comments.comment_id
                                    WHERE Comment.id = ?""", [comment_id])
        data = cursor.fetchall()
        if len(data) == 0:
            return 'Не удалось добавить комментарий в БД.'
        return f"Комментарий {comment_id} от пользователя {user_id} добавлен."



# __________Админ панель__________

# ДОБАВЛЕНИЕ НОВОГО ТОВАРА +
def add_new_goods(params):
    """добавление нового товара создать список товаров в виде следующего списка
    [категория, название, описание, цена, время приготовления, вес, изображение в формате BLOB(в бинарном виде)]"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        query = """INSERT INTO Goods(category, name, good_description, price, time_to_ready, weight, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
        valid_formats = ['jpeg', 'png', 'gif']
        img_format = imghdr.what(params[-1])
        if img_format.lower() in valid_formats:
            cursor.execute(query, params)
            good_id = cursor.lastrowid
            category = params[0]
            if params[0] == 1:
                category_name = 'Блюда'
            if params[0] == 2:
                category_name = 'Напитки'
            cursor.execute("INSERT INTO Categories(description, category_name) VALUES(?, ?)", [category, category_name])
            cursor.execute("SELECT * FROM Goods WHERE id = ?", [good_id])
            data = cursor.fetchall()
            if len(data) == 0:
                return "Не удалось добавить товар в базу данных."
            return f"Добавлен новый товар: {params[1]}"
        else:
            return 'Неверный формат изображения. Допустимые форматы: jpeg, png, gif.'


# УДАЛЕНИЕ ТОВАРА +
def delete_goods(good_id):
    """удаляем товра из БД
    берем id товара из функции get_from_category
    запускаем get_from_category для админа без параметр is_on_pause
    чтобы отобразить полностью все товары"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM Goods WHERE id = ?", [good_id])

        cursor.execute("SELECT id FROM Goods WHERE id = ?", [good_id])
        data = cursor.fetchone()
        return f"Товар id: {good_id} удален, либо отсутствует в БД." if data is None else f"Не удалось удалить товар id:{good_id}"


# ИЗМЕНЕНИЕ КАРТОЧКИ ТОВАРА                 ------ Исправить чтобы загружало фото-----
# МОЖНО СДЕЛАТЬ ФУНКЦИЮ КОТОРАЯ ПРИНИМАЕТ НОВЫЕ ДАННЫЕ,
# А ЕСЛИ ПОЛЬЗОВАТЕЛЬ ХОЧЕТ ЧТОБЫ ДАННЫЕ ОСТАЛИСЬ БЕЗ ИЗМЕНЕНИЯ, ПРОСТО НАЖИМАЕТ ВВОД
def correct_goods(good_id, new_data):
    """изменяем карточку товара
    берем id товара из функции get_from_category
    new_data == [категория, название, описание, цена, время приготовления, вес,
    изображение в формате BLOB(в бинарном виде)]"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        query = """UPDATE Goods SET category = ?, name = ?, good_description = ?, price = ?, time_to_ready = ?, 
                                    weight = ?, image = ? WHERE id = ?"""
        cursor.execute(query, [*new_data, good_id])
        cursor.execute("SELECT * FROM Goods WHERE id = ?", [good_id])
        updated_data = cursor.fetchone()
        if updated_data:
            return f"Карточка товара обновлена: \n {get_product_card(new_data[1])})"
        return "Не удалось внести изменения."


# ДОБАВЛЕНИЕ НОВОГО АДМИНА +
def add_new_admin(admin_id, name, is_super):
    """"Добавояем нового администратора
        параметры admin_id, name, is_super
        1 - супер админ
        2- оыбчный"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Admins(user_id, is_super_admin) VALUES(?, ?)",  [admin_id, is_super])

        cursor.execute("""INSERT INTO Users(id, user_name, is_admin, block_status) VALUES(?, ?, ?, ?)""",
                       [admin_id, name, 1, 1])

        cursor.execute("""SELECT Users.user_name, Users.is_admin, Admins.is_super_admin
                                FROM Users
                                JOIN Admins ON Users.id = Admins.user_id
                                WHERE Users.id = ?""", [admin_id])
        data = cursor.fetchone()
        if data is not None:
            return f"Администратор {name}, id: {admin_id} с правами {is_super} категории, добавлен"
        return "Не удалось добавить нового администратора"


# ВЫВОДИМ СПИСОК АДМИНОВ +
def show_admins():
    """Отображаем список имеющихся администраторов
       возвращаем список кортежей где [(name, id, is_super(1-super, 2- нет), (name, id, is_super)]"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT Users.user_name, Users.id, Admins.is_super_admin
                          FROM Users
                          JOIN Admins ON Users.id = Admins.user_id""")
        data = cursor.fetchall()
        return data if len(data) != 0 else "Не удалось получить список администраторов"


# УДАЛЯЕМ АДМИНА +
def delete_admin(admin_id):
    """удаляет администратора по ID,
       затем проверяет успешно ли прошло удаление и возвращает результат.
       admin_id можно взять из функции show_admins"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM Admins WHERE user_id =  ?", [admin_id])
        cursor.execute("DELETE FROM Users WHERE id =  ?", [admin_id])
        cursor.execute("""SELECT Users.id, Admins.user_id
                                 FROM Users
                                 JOIN Admins ON Users.id = Admins.user_id""")
        data = cursor.fetchone()
        return f"Admin id:{admin_id} успешно удален" if data is not None else f"Не удалось удалить админа id:{admin_id}"


# ИЗМЕНЕНИЕ СТАТУСА АДМИНИСТРАТОРА +
def change_admin_status(admin_id, new_status):
    """Изменяет статус администратора но новый
       admin_id можно взять из функции show_admins
       new_status 1- супер админ, 2- обычный админ"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("UPDATE Admins SET is_super_admin = ? WHERE user_id = ?", [new_status, admin_id])

        cursor.execute("SELECT is_super_admin FROM Admins WHERE user_id = ?", [admin_id])
        data = cursor.fetchone()
        return f"Статус успешно изменен" if data[0] == new_status else f"Не удалось изменить статус"


# УДАЛЕНИЕ КОММЕНТАРИЯ +
def delete_comment(com_id):
    """удаляет комментарий по его id"""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM Comment WHERE id = ?", [com_id])
        cursor.execute("DELETE FROM Comments WHERE comment_id = ?", [com_id])
        # Проверяем, был ли комментарий удален
        cursor.execute("""SELECT Comments.comment_id, Comment.id FROM Comments 
                          JOIN Comment ON Comments.comment_id = Comment.id
                          WHERE Comments.comment_id = ?""", [com_id])
        data = cursor.fetchone()
        return f"Комментарий id: {com_id} удален" if data is None else f"Не удалось удалить комментарий id:{com_id}"


# ДОБАВЛЕНИЕ НОВОГО КЛЮЧА +
def add_new_key(new_key, is_for_super):
    """
    добавляем ключ доступа в таблицу
    :param new_key: в формате int либо str.strpi()
    :param is_for_super: в формате int (1=супер админ, 2 = обычный)
    :return: Ключ: id добавлен или нет
    """
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Keys_for_admin_panel(key, is_for_super) VALUES(?, ?)", [new_key, is_for_super])

        cursor.execute("SELECT key FROM Keys_for_admin_panel WHERE key = ?", [new_key])
        data = cursor.fetchone()
        return f"Ключ: {new_key} добавлен" if data is not None else f"Не удалось добавить ключ {new_key}"


# ОТОБРАЖАЕМ ИМЕЮЩИЕСЯ КЛЮЧИ ДОСТУПА +
def show_keys():
    """
    :return: Выводит все имебщиеся ключи и их статус из таблицы Keys_for_admin_panel
             вывод в виде списка кортежей [(id, ключ, статус), (id, ключ, статус)]
             статус 1- супер админ, 2 - обычный админ
    """
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, key, is_for_super FROM Keys_for_admin_panel")
        data = cursor.fetchall()
        return data if data is not None else "Не удалось загрузить данные."


# УДАЛЕНИЕ КЛЮЧА ИЗ ТАБЛИЦЫ +
def delete_key(key_id):
    """
    удаляем ключ доступа из таблицы БД
    :param key_id: id ключа
    :return: ключ удален, если кдалили или нет ключа
    """
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM Keys_for_admin_panel WHERE id = ?", [key_id])
        # чтобы посмотреть удалился или нет
        cursor.execute("SELECT key FROM Keys_for_admin_panel WHERE id = ?", [key_id])
        data = cursor.fetchone()
        return f"Ключ id: {key_id} удален" if data is None else f"Не удалось удалить ключ id: {key_id}"


# ПРОВЕРКА ВАЛИДНОСТИ КЛЮЧА ДОСТУПА
def is_valid_key(key):
    """
    Проверяем валидность ключа,
    то есть имеется ли ключ в базе и какие полномочия предоставляет
    :param key: ключ введенный пользователем int либо str.strpi()
    :return: кортеж(ключ, 1- супер админ 2- обычный)
    """
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT key, is_for_super FROM Keys_for_admin_panel WHERE key = ?", [key])
        data = cursor.fetchone()
        return f"{data} if data is not None else f"Ключ {key} не найден в БД."


# ИЗМЕНЕНИЕ СТАТУСА ПОЛЬЗОВАТЕЛЯ НА АДМИНА В СЛУЧАЕ ВВЕДЕНИЯ КЛЮЧА ДОСТУПА
def change_user_to_admin(user_id, key):
    """Изменям статус пользователя ввевшего ключ доступа
       Предварительно необходимо проверить находится ли введенный ключ доступа в БД.
       user_id - id пользователя, key - введенный пользователем ключ."""
    with sqlite3.connect('Delivery.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT is_for_super FROM Keys_for_admin_panel WHERE key = ?", [key])
        is_super = cursor.fetchone()
        cursor.execute("UPDATE Users SET is_admin = ? WHERE id = ?",  [1, user_id])
        cursor.execute("UPDATE Admins SET is_super_admin = ? WHERE id = ?", [is_super[0], user_id])
        cursor.execute("""SELECT Users.is_admin, Admins.is_super_admin
                                FROM Users
                                JOIN Admins ON Users.id = Admins.user_id
                                WHERE Users.id = ?""", [user_id])
        updated_data = cursor.fetchone()
        if updated_data[1] != is_super[0]:
            return f"Не удалось добавить права админстратора пользователю {user_id}."
        return f"Пользователю {user_id} добавлены права администртора {is_super} категории."


a = 123123123

"""
Fix Dark - это таинственное темное пиво, которое пленит своей глубиной и насыщенным вкусом. Его аромат обволакивает нежными нотами шоколада и кофе, а густая пена создает иллюзию ночного неба. Откройте для себя магию темных оттенков в каждом глотке Fix Dark.

Beer OuroPretana - это темное пиво с глубокими оттенками и богатым вкусом. Его аромат раскрывается нотками шоколада, кофе и карамели, создавая приятное слияние сладости и горечи. Пиво обладает плотной текстурой и умеренной газировкой, что придает ему особую гармонию. Beer OuroPretana - это идеальный выбор для ценителей темных сортов пива, желающих насладиться насыщенным и утонченным вкусом.

Вкуснейший стейк, приготовленный по традиционному рецепту, сопровождается хрустящими картофельными фри. Нежное мясо и хрустящая корочка картошки создают идеальное сочетание текстур и ароматов. Приготовьтесь к настоящему кулинарному наслаждению!

Вкусная жареная курица с сочными кусочками манго и свежей зеленью - это настоящий взрыв вкусов! Нежное мясо курицы сочетается с сладостью манго и ароматом свежей зелени, создавая идеальное блюдо для наслаждения. Попробуйте эту уникальную комбинацию и погрузитесь в мир гастрономического наслаждения!

Освежающая безалкогольная Кока-Кола Лайт - идеальный выбор для тех, кто ценит непревзойденный вкус без лишних калорий.

Ароматный кофе, приготовленный с любовью и мастерством. Идеальное сочетание вкуса, аромата и тела, чтобы пробудить в Вас энергию и вдохновение.

Черная паста с королевскими креветками - это изысканноелюдо, которое поразит Вас своим вкусом и элегантностью. Ароматная паста, окрашенная натуральным чернилами каракатицы, и сочные креветки создают идеальное сочетание, которое покорит ваш вкусовой рецептор.

Соблазнительная пицца на черном тесте - это искусство вкуса и эстетики. Сочные томаты, ароматные специи и аппетитные топпинги создают идеальное сочетание на каждом кусочке. Отведайте этот мрачно-прекрасный кулинарный шедевр!

Суши – искусство вкуса и эстетики. Сочетание свежих ингредиентов, нежного риса и изысканных соусов создает неповторимый вкусовой опыт. Погрузитесь в мир японской кулинарии с каждым кусочком. Отведайте суши и ощутите гармонию вкусов и текстур.

В глубокой зимней ночи, когда мороз за окном сверкает, замечательный зимний чай с нотками корицы становится настоящим утешением. Его аромат и тепло согревают душу, а палочка корицы добавляет неповторимую нотку праздника. Каждый глоток этого чая – это волшебное путешествие в мир уюта и комфорта.
"""
