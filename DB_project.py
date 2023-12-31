import sqlite3
import datetime
import telebot

bot = telebot.TeleBot('6386657547:AAGDz06oEBlutexV47VOPv_FfXen3Dv2Ja0')


# В БЛЭКЕ ИЛИ НЕТ ++
def is_in_black_list(user_id):
    """проверка пользователь в блэке или нет
    :param user_id: id пользователя
    :return: True - в блэке, False - нет"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT block_status FROM Users WHERE id == ?", [user_id])
            result = cursor.fetchone()
            return True if result[0] == 2 else False
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")
        return False


# НОВЫЙ ПОЛЬЗОВАТЕЛЬ ИЛИ НЕТ ++
def is_new(user_id):
    """проверка новый пользователь или нет
    :param user_id: id пользователя
    :return: True - новый, False - есть в базе"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT id FROM Users WHERE id == ?", [user_id])
            result = cursor.fetchone()
            return True if result is None else False
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")


# ЯВЛЯЕТСЯ ЛИ АДМИНОМ +
def is_admin(user_id):
    """проверяем является ли админом
    :param user_id: id пользователя
    :return: True - admin, False - не админ"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT is_admin FROM Users WHERE Users.id == ?", [user_id])
            result = cursor.fetchone()
            return result[0] == 1
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")
        return False


# ПРОВЕРЯЕТ ПОЛНОМОЧИЯ АДМИНА +
def is_super_admin(user_id):
    """проверяем с какими полномочиями
    :param user_id: id admin
    :return: True - super, False - обычный"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT is_super_admin FROM Admins WHERE Admins.user_id == ?", [user_id])
            result = cursor.fetchone()
            return result[0] == 1
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")
        return False


# РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ ++
def registrator(user_data):
    """принимает СПИСОК данных и добавляет пользователя в БД
    :param user_data: [id, user_name, phone_number, birthday (формат ввода '01.01.2023')]
    :return:True - регистрация прошла успешно иначе False"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Users(id, user_name, phone_number, birthday) VALUES (?, ?, ?, ?)",
                           user_data)
            return cursor.rowcount == 1
    except sqlite3.Error as e:
        print(f"Ошибка при выполнении регистраиции: {e}")
        return False


# СПИСОК КАТЕГОРИЙ ++
def get_categories():
    """возвращаем список названий категорий
    :return: Список категорий, False если таблица пустая """
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT name FROM Categories GROUP BY name")
            result = cursor.fetchall()
            return False if len(result) == 0 else [i[0] for i in result]
    except sqlite3.Error as e:
        raise Exception(f"Ошибка при получении списка категорий: {e}")


# СПИСОК ТОВАРОВ В ВЫБРАННОЙ КАТЕГОРИИ ++
def get_from_category(category_name):
    """ возвращает список всех названий товаров в категории
    :param category_name: название категории
    :return: список всех названий товаров в категории [(name), (name)]"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            query = ("""SELECT DISTINCT Goods.name FROM Goods 
                       JOIN Categories ON Categories.id = Goods.category
                       WHERE Categories.category_name = ?""")
            cursor.execute(query, [category_name])
            result = cursor.fetchall()
            return False if len(result) == 0 else [i[0] for i in result]
    except sqlite3.Error as e:
        print(f"Не удалось загрузить список товаров категории: {e}")
        return False


# КАРТОЧКА ВЫБРАННОГО ТОВАРА ++
def show_product_card(product_name):
    """Отображает данные для карточки товара
    :param product_name: название товара
    :return: возвращает картеж с данными для карточки товара
    последний элемент кортежа - ПУТЬ К КАРТИНКЕ"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT name, good_description, weight, price, ranking, image
                           FROM Goods WHERE name = ?""", [product_name])
            result = cursor.fetchone()
            return result if result is not None else False
    except sqlite3.Error as e:
        print(f"Произошла ошибка при получении данных: {e}")
        return False


# ДОБАВЛЕНИЕ АДРЕСА ДОСТАВКИ В ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
def add_delivery_address(delivery_address):
    """добавление адреса в БД
    :param delivery_address: адресс введенный пользователем в формате str
    :return: True если добавлен, False если ошибка"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Users (last_address) VALUES (?)", [delivery_address])
            return cursor.rowcount == 1
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении адреса: {e}")
        return False


# ПОЛУЧАЕМ id и ОБЩУЮ СТОИМОСТЬ ЗАКАЗА
def get_total_price(goods):
    """вывод общей стоимости товаров в заказе по имени товара
    :param goods: [[название товара, количество единиц]]
    :return: общая сумма заказа"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            total_price = 0
            for good in goods:
                cursor.execute("SELECT price FROM Goods WHERE name = ?", [good[0]])
                good_price = cursor.fetchone()
                total_price += good_price[0] * good[1]
            return total_price
    except sqlite3.Error as e:
        print(f"Ошибка при получении общей стоимости товара: {e}")
        return None


# ПОЛУЧАЕМ ID ТОВАРОВ ПО НАЗВАНИЯМ
def get_good_ids(names):
    """вывод списка id товаров по именам товаров
    :param names: [название товара, название товара]
    :return: список id товаров"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            goods_id = []
            for name in names:
                cursor.execute("SELECT id FROM Goods WHERE name = ?", [names])
                good_id = cursor.fetchone()
                goods_id.append(good_id)
            return goods_id
    except sqlite3.Error as e:
        print(f"Ошибка при получении общей id товаров: {e}")
        return None


# ЗАГРУЗКА ДАННЫХ В БД ПОСЛЕ ПОДТВЕРЖДЕНИЯ ЗАКАЗА               !!!--- прорить после создания корзины ---!!!
def from_cart_into_db(user_data, price, cart, delivery_note):
    """помещаем заказ из корзины в БД
    :param user_data: данные пользователя [user_id, user_tel, address]
    :param price: общая цена товара из функции get_total_price
    :param cart: корзина [[название, количество], [название, количество]]
    :param delivery_note: комментарий пользователя к заказу
    :return: True если все загрузилось False если нет"""
    try:
        order_info = show_order_info(user_data[0])
        max_time = sorted(order_info, key=lambda x: x[2])[-1][2]
        current_day = datetime.datetime.now()
        result_time = current_day + datetime.timedelta(minutes=max_time)
        delivery_time = result_time.strftime("%d.%m.%Y %H:%M")
        current_date = current_day.strftime("%d.%m.%Y")

        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO Orders (user_id, user_tel, address, total_price, order_status, order_date, 
               delivery_time, user_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           [user_data[0], user_data[1], user_data[2], price, 'заказ принят', current_date, delivery_time,
                            delivery_note])
            order_id = cursor.lastrowid

            for good in cart:
                cursor.execute("SELECT id FROM Goods WHERE name = ?", [good[0]])
                good_id = cursor.fetchone()
                cursor.execute("INSERT INTO Goods_in_order (order_id, good_id, quantity) VALUES(?, ?, ?)",
                               [order_id, good_id[0], good[1]])

        return True
    except sqlite3.Error as e:
        print(f"Ошибка при загрузке заказа в БД: {e}")
        return False


# УДАЛЕНИЕ ТОВАРА ИЗ ТАБЛИЦЫ (ИСПОЛЬЗОВАТЬ КОГДА ТОВАР ДОСТАВЛЕН)
def del_from_orders(user_id):
    """удаляем заказ после доставления
    :param user_id: id пользователя чей заказ нужно удалить
    :return: True = удален, False = не удален"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Orders WHERE user_id = ?", [user_id])
            return cursor.rowcount == 0
    except sqlite3.Error as e:
        print(f"Ошибка при удалении заказа из БД: {e}")
        return False


# НОМЕР ЗАКАЗА И ВРЕМЯ ПРИГОТОВЛЕНИЯ + 30 МИН. +                !!!--- перепроверить после создания корзины ---!!!
def show_order_info(user_id):
    """Показывает информацию о заказах пользователя, кроме доставленных заказов.
    :param user_id: id пользователя
    :return: информация о заказах и время доставки в минутах"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("""
                    SELECT Orders.id, Orders.order_status, MAX(Goods.time_to_ready) + 30
                    FROM Orders
                    JOIN Goods_in_order ON Orders.id = Goods_in_order.order_id
                    JOIN Goods ON Goods_in_order.good_id = Goods.id
                    WHERE Orders.user_id = ? AND Orders.order_status != 'доставлен'
                    GROUP BY Orders.id 
                    ORDER BY Orders.id DESC
                """, [user_id])
            result = cursor.fetchall()
            return 'Заказы не найдены' if len(result) == 0 else result
    except sqlite3.Error as e:
        print(f"Ошибка при получении информации о заказах: {e}")
        return None


# КОРТЕЖ ДАННЫХ ПОЛЬЗОВАТЕЛЯ ++
def get_user_data(user_id):
    """ Получение данных пользователя
    :param user_id: id пользователя
    :return: Возвращает данные пользователя в виде кортежа"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users where id = ?", [user_id])
            result = cursor.fetchone()
            return f"Пользователь с id: {user_id} не найден в БД" if result is None else result
    except sqlite3.Error as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return False


# КОРТЕЖ ДАННЫХ АДМИНА ++
def get_admin_data(user_id):
    """ Получение данных администратора
        :param user_id: id пользователя
        :return: Возвращает данные администратора в виде кортежа (ID, name, полномочия(1-супер, 2- обычный)"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT Users.id, Users.user_name, Admins.is_super_admin 
                                    FROM Users
                                    JOIN Admins ON Users.id = Admins.user_id 
                                    WHERE Users.id = ?""", [user_id])
            result = cursor.fetchone()
            return f"Администратор с id: {user_id} не найден." if result is None else result
    except sqlite3.Error as e:
        print(f"Ошибка при получении информации об администраторе: {e}")
        return False


# СПИСОК КОММЕНТАРИЕВ +
def show_comments(good_name):
    """Выводит все комментарии в виде [(comment_id, коммент, пользователь), (comment_id, коммент, пользователь)]
    :param good_name: название товара
    :return: список кортежей с данными"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT Comments.comment_id, Comment.content, Users.user_name
                                    FROM Comments
                                    JOIN Comment ON Comments.comment_id = Comment.id
                                    JOIN Goods ON Comments.good_id = Goods.id
                                    JOIN Users ON Comment.from_user = Users.id
                                    WHERE Goods.name = ?""", [good_name])
            result = cursor.fetchall()
            return 'Комментарии отсутствуют' if len(result) == 0 else result
    except sqlite3.Error as e:
        print(f"Ошибка при получении информации о комментариях: {e}")
        return False


# ИСПРАВИТЬ ДОБАВЛЕНИЕ КОММЕНТА НЕ ПО ИД А ПО НАЗВАНИЮ ТОВАРА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ДОБАВЛЕНИЕ КОММЕНТАРИЯ +
def add_comment(good_name, user_id, content):
    """добавление нового комментария
    :param good_name: имя товара
    :param user_id: id пользователя
    :param content: содержание комментария
    :return: True = комментарий добалвен, False = не добавлен"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Comment (content, from_user) VALUES (?, ?)", [content, user_id])
            comment_id = cursor.lastrowid

            cursor.execute("SELECT id FROM Goods WHERE name = ?", [good_name])
            good_id = cursor.fetchone()

            cursor.execute("INSERT INTO Comments (comment_id, good_id, user_id) VALUES (?, ?, ?)",
                           [comment_id, good_id[0], user_id])
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении комментария: {e}")
        return False


# ____________________ АДМИН ПАНЕЛЬ ____________________
# !!!!!!!!!!!!!!!! ИСПРАВИТЬ!!!!!!!!!!!!!!!!!!!!!
# ДОБАВЛЕНИЕ НОВОГО ТОВАРА +
def add_new_goods(params):
    """добавление нового товара
    :param params:[категория, название, описание, цена, время приготовления, вес, путь к изображению из imgs]
    :return: True = данные загружены False = не загружены/ошибка """
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO Goods(category, name, good_description, price, time_to_ready, weight, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", params)
            good_id = cursor.lastrowid
            if params[0] == 1:
                category_name = 'Блюда'
            if params[0] == 2:
                category_name = 'Напитки'
            cursor.execute("INSERT INTO Categories(id, category_name) VALUES(?, ?)", [params[0], category_name])
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")
        return False


# УДАЛЕНИЕ ТОВАРА +
def delete_goods(good_name):
    """удаляем товра из БД
    :param good_name: имя товара
    :return: True = удален, False =  не удален"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Goods WHERE name = ?", [good_name])
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Ошибка при удалении товара: {e}")
        return False


# ИСПРАВИТЬ ИСПРАВЛЕНИЕ ТОВАРА НЕ ПО ИД А ПО НАЗВАНИЮ ТОВАРА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
            return f"Карточка товара обновлена: \n {show_product_card(new_data[1])})"
        return "Не удалось внести изменения."


# ДОБАВЛЕНИЕ НОВОГО АДМИНА +
def add_new_admin(admin_id, name, is_super):
    """Добавояем нового администратора
    :param admin_id: id нового админа
    :param name: имя нового админа
    :param is_super: полномочия(1 = супер, 2 = обычный)
    :return: True = добавлен. False = не добавлен/ошибка"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Admins(user_id, is_super_admin) VALUES(?, ?)", [admin_id, is_super])
            if cursor.rowcount > 0:
                cursor.execute("INSERT INTO Users(id, user_name, is_admin, block_status) VALUES(?, ?, ?, ?)",
                               [admin_id, name, 1, 0])
                return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении администратора: {e}")
        return False


# ПОСМОТРЕТЬ КАК ПРОЩЕ КНОПКАМИ ВЫВОДИТЬ ИЛИ ТЕКСТОМ ДЛЯ ПОСЛЕДУЮЩЕГО УДАЛЕНИЯ
# ВЫВОДИМ СПИСОК АДМИНОВ +
def show_admins():
    """Отображаем список имеющихся администраторов
    :return: возвращаем список кортежей [(name, id, is_super(1-super, 2- нет)]"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT Users.user_name, Users.id, Admins.is_super_admin
                              FROM Users
                              JOIN Admins ON Users.id = Admins.user_id""")
            data = cursor.fetchall()
            return data if len(data) != 0 else False
    except sqlite3.Error as e:
        print(f"Не удалось получить список администраторов: {e}")
        return False


# УДАЛЯЕМ АДМИНА ++
def delete_admin(admin_id):
    """удаляет администратора по ID,
    :param admin_id: id администратора
    :return: True = удален, False = не удален"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Admins WHERE user_id =  ?", [admin_id])
            if cursor.rowcount > 0:
                cursor.execute("DELETE FROM Users WHERE id =  ?", [admin_id])
                return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Не удалось удалить администратора: {e}")
        return False


# ИЗМЕНЕНИЕ СТАТУСА АДМИНИСТРАТОРА +
def change_admin_status(admin_id, new_status):
    """Изменяет статус администратора
    :param admin_id: id админа
    :param new_status: новый статус (1- супер админ, 2- обычный админ)
    :return: True = статус изменен, False = не изменен/ошибка """
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("UPDATE Admins SET is_super_admin = ? WHERE user_id = ?", [new_status, admin_id])
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Не удалось изменить статус: {e}")
        return False


# УДАЛЕНИЕ КОММЕНТАРИЯ +
def delete_comment(com_id):
    """удаляет комментарий по id
    админ руками вписывает id комментария
    :param com_id: id комментария
    :return: True = удален, False = не удален/ошибка"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Comment WHERE id = ?", [com_id])
            if cursor.rowcount > 0:
                cursor.execute("DELETE FROM Comments WHERE comment_id = ?", [com_id])
                return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Не удалось удалить комментарий: {e}")
        return False


# ДОБАВЛЕНИЕ НОВОГО КЛЮЧА +
def add_new_key(new_key, is_for_super):
    """добавляем ключ доступа в таблицу
    :param new_key: в формате int либо str.strpi()
    :param is_for_super: в формате int (1=супер админ, 2 = обычный)
    :return: True = добавлен, False = не добавлен/ошибка"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Keys_for_admin_panel(key, is_for_super) VALUES(?, ?)", [new_key, is_for_super])
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Не удалось добавить новый ключ: {e}")
        return False


# ОТОБРАЖАЕМ ИМЕЮЩИЕСЯ КЛЮЧИ ДОСТУПА +
def show_keys():
    """выводит все имебщиеся ключи и их статус
    :return: [(id, ключ, статус)] статус 1- супер админ, 2 - обычный"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT id, key, is_for_super FROM Keys_for_admin_panel")
            data = cursor.fetchall()
            return data if len(data) != 0 else False
    except sqlite3.Error as e:
        print(f"Не удалось загрузить данные: {e}")
        return False


# УДАЛЕНИЕ КЛЮЧА ИЗ ТАБЛИЦЫ +
def delete_key(key_id):
    """удаляем ключ доступа из БД
    :param key_id: id ключа
    :return: True = ключ удален, False не удален/ошибка"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Keys_for_admin_panel WHERE id = ?", [key_id])
            return cursor.rowcount > 1
    except sqlite3.Error as e:
        print(f"Не удалось удалить ключ id: {e}")
        return False


# ПРОВЕРКА ВАЛИДНОСТИ КЛЮЧА ДОСТУПА +
def is_valid_key(key):
    """Проверяем есть ли ключ
    :param key: ключ введенный пользователем int либо str.strip()
    :return: True = есть ключ, False = нет"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT key, is_for_super FROM Keys_for_admin_panel WHERE key = ?", [key])
            data = cursor.fetchone()
            return True if data is not None else False
    except sqlite3.Error as e:
        print(f"Не удалось удалить ключ id: {e}")
        return False


# ИЗМЕНЕНИЕ СТАТУСА ПОЛЬЗОВАТЕЛЯ НА АДМИНА В СЛУЧАЕ ВВЕДЕНИЯ КЛЮЧА ДОСТУПА
def change_user_to_admin(user_id, key):
    """Изменям статус пользователя с ключом доступа
    :param user_id: id пользователя
    :param key: ключ введенный пользователем
    :return: True = стал админом False = не удалось сделать админом/ошибка"""
    try:
        with sqlite3.connect('Delivery.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT is_for_super FROM Keys_for_admin_panel WHERE key = ?", [key])
            if cursor.rowcount > 1:
                is_super = cursor.fetchone()
                cursor.execute("UPDATE Users SET is_admin = ? WHERE id = ?",  [1, user_id])
                if cursor.rowcount > 1:
                    cursor.execute("INSERT INTO Admins (user_id, is_super_admin) VALUES(?, ?)", [user_id, is_super[0]])
                    return cursor.rowcount > 1
    except sqlite3.Error as e:
        print(f"Не удалось добавить права админстратора пользователю: {e}")
