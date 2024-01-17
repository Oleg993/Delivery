import sqlite3
import datetime
import telebot

bot = telebot.TeleBot('6386657547:AAGDz06oEBlutexV47VOPv_FfXen3Dv2Ja0')


class UserInfo:
    """Содержит методы: is_in_black_list, is_new, is_admin, is_super_admin, get_user_data, show_users"""
    def __init__(self):
        self.db_file = 'Delivery.db'

    def is_in_black_list(self, user_id):
        """проверка пользователь в блэке или нет
        :param user_id: id пользователя
        :return: True - в блэке, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT block_status FROM Users WHERE id == ?", [user_id])
                result = cursor.fetchone()
                return result[0] == '1' if result is not None else False
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return False

    def is_new(self, user_id):
        """проверка новый пользователь или нет
        :param user_id: id пользователя
        :return: True - новый, False - есть в базе"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM Users WHERE id == ?", [user_id])
                result = cursor.fetchone()
                return True if result is None else False
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")

    def is_admin(self, user_id):
        """проверяем является ли админом
        :param user_id: id пользователя
        :return: True - admin, False - не админ"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT is_admin FROM Users WHERE Users.id == ?", [user_id])
                result = cursor.fetchone()
                return result[0] == '1'
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return False

    def is_super_admin(self, user_id):
        """проверяем с какими полномочиями
        :param user_id: id admin
        :return: True - super, False - обычный"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT is_super_admin FROM Admins WHERE Admins.user_id == ?", [user_id])
                result = cursor.fetchone()
                return result[0] == '1'
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return False

    def get_user_data(self, user_id):
        """ Получение данных пользователя
        :param user_id: id пользователя
        :return: Возвращает данные пользователя в виде кортежа"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Users where id = ?", [user_id])
                result = cursor.fetchone()
                return f"Пользователь с id: {user_id} не найден в БД" if result is None else result
        except sqlite3.Error as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            return False

    def show_users(self, user_id):
        """Отображение списка имеющихся пользователей
        :return: возвращаем список кортежей [(name, id, block_status)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT user_name, id, block_status FROM Users
                                  WHERE id != ?""", [user_id])
                data = cursor.fetchall()
                return data if len(data) != 0 else False
        except sqlite3.Error as e:
            print(f"Не удалось получить список администраторов: {e}")
            return False


class Registrator:
    """Содержит методы: registrator"""

    def __init__(self):
        self.db_file = 'Delivery.db'

    def registrator(self, user_data):
        """принимает список данных и добавляет пользователя в БД
        :param user_data: [id, user_name, phone_number, birthday (формат ввода '01.01.2023')]
        :return:True если регистрация прошла успешно"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO Users(id, user_name, phone_number, birthday) VALUES (?, ?, ?, ?)", user_data)
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении регистраиции: {e}")
            return False


class Categories:
    """Содержит методы: get_categories, get_from_category"""

    def __init__(self):
        self.db_file = 'Delivery.db'

    def get_categories(self):
        """возвращаем список названий категорий
        :return: Список категорий, False если таблица пустая """
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT category_name FROM Categories GROUP BY category_name")
                result = cursor.fetchall()
                return False if len(result) == 0 else [i[0] for i in result]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка при получении списка категорий: {e}")

    def get_from_category(self, category_name):
        """возвращает список всех названий товаров в категории и статус(На паузе или нет)
        :param category_name: название категории
        :return: список всех названий товаров в категории [(name, 0), (name, 1)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                query = ("""SELECT DISTINCT Goods.name, Goods.is_on_pause FROM Goods 
                           JOIN Categories ON Categories.category_name = Goods.category
                           WHERE Categories.category_name = ?""")
                cursor.execute(query, [category_name])
                result = cursor.fetchall()
                return False if len(result) == 0 else [i for i in result]
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список товаров категории: {e}")
            return False


class Good:
    """Содержит методы: show_product_card, get_total_price, get_good_ids, get_max_good_time"""
    def __init__(self):
        self.db_file = 'Delivery.db'

    def show_product_card(self, product_name):
        """Отображает данные для карточки товара
        :param product_name: название товара
        :return: возвращает картеж с данными для карточки товара ПРЕДпоследний элемент кортежа - ПУТЬ К КАРТИНКЕ,
        последний элемент - ID картинки из ТГ"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT id, category, name, good_description, 
                                        price, time_to_ready, ranking, weight, is_on_pause
                                        FROM Goods WHERE name = ?""", [product_name])
                result = cursor.fetchone()
                cursor.execute("""SELECT img_path, tg_id FROM Images WHERE good_name = ?""", [product_name])
                img_info = cursor.fetchone()
                result += img_info
                return result if result is not None else False
        except sqlite3.Error as e:
            print(f"Произошла ошибка при получении данных: {e}")
            return False

    def get_total_price(self, goods):
        """вывод общей стоимости товаров в заказе по имени товара
        :param goods: [[название товара, количество единиц]]
        :return: общая сумма заказа"""
        try:
            with sqlite3.connect(self.db_file) as db:
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

    def get_good_ids(self, names):
        """вывод списка id товаров по именам товаров
        :param names: СПИСОК [название товара, название товара]
        :return: список id товаров"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                goods_id = []
                for name in names:
                    cursor.execute("SELECT id FROM Goods WHERE name = ?", [name])
                    good_id = cursor.fetchone()
                    if good_id:
                        goods_id.append(good_id[0])
                return goods_id
        except sqlite3.Error as e:
            print(f"Ошибка при получении общей id товаров: {e}")
            return None

    def get_max_good_time(self, good_names):
        """вывод максимального времени приготовленя блюда + 30 МИНУТ
        :param good_names: список названий товаров
        :return: максимальное время приготовления товара в минутах + 30 минут """
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                max_time = []
                for name in good_names:
                    cursor.execute("SELECT time_to_ready FROM Goods WHERE name = ?", [name])
                    good_time = cursor.fetchone()
                    if good_time:
                        max_time.append(good_time[0])
                return max(max_time) + 30
        except sqlite3.Error as e:
            print(f"Ошибка при получении общей id товаров: {e}")
            return None


class Delivery:
    """Содержит методы: from_cart_into_db, correct_delivery_address, change_delivery_status"""
    def __init__(self):
        self.db_file = 'Delivery.db'

    def from_cart_into_db(self, user_data, price, cart, delivery_time, delivery_note):
        """помещаем заказ из корзины в БД
        :param user_data: данные пользователя [user_id, user_tel, address]
        :param price: общая цена товара из функции get_total_price
        :param cart: корзина СПИСОК С ВЛОЖЕННЫМ(И) СПИСКОМ(МИ) [[название, количество], [название, количество]]
        :param delivery_time: время доставки товара
        :param delivery_note: комментарий пользователя к заказу
        :return: True если все загрузилось False если нет"""
        try:
            current_day = datetime.datetime.now()
            current_date = current_day.strftime("%d.%m.%Y")

            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO Orders (user_id, user_tel, address, total_price, order_status, order_date, 
                   delivery_time, user_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                               [user_data[0], user_data[1], user_data[2], price, 'заказ принят', current_date,
                                delivery_time, delivery_note])
                order_id = cursor.lastrowid
                cursor.execute("UPDATE Users SET last_address= ? WHERE id = ?", [user_data[2], user_data[0]])
                for good in cart:
                    cursor.execute("SELECT id FROM Goods WHERE name = ?", [good[0]])
                    good_id = cursor.fetchone()
                    cursor.execute("INSERT INTO Goods_in_order (order_id, good_id, quantity) VALUES(?, ?, ?)",
                                   [order_id, good_id[0], good[1]])
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке заказа в БД: {e}")
            return False

    def correct_delivery_address(self, delivery_address, user_id):
        """Изменение адреса пользователя в БД
        :param delivery_address: новый адресс введенный пользователем в формате str
        :param user_id: id пользователя
        :return: True если добавлен, False если ошибка"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("UPDATE Users SET last_address=? WHERE id = ?", [delivery_address, user_id])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении адреса: {e}")
            return False

    def change_delivery_status(self, order_id):
        """изменяем статус заказа после доставления на "доставлено"
        :param order_id: id заказа в котором нужно изменить статус
        :return: True = изменен на "доставлено", False = не изменен"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("UPDATE Orders SET order_status = ? WHERE id = ?", ["доставлено", order_id])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при изменении статуса заказа: {e}")
            return False


class Order:
    """Содержит методы: show_order_info, delete_order"""
    def __init__(self):
        self.db_file = 'Delivery.db'

    def show_order_info(self, user_id):
        """Показывает информацию о заказах пользователя, кроме доставленных заказов.
        :param user_id: id пользователя
        :return: информация о заказах и время доставки в минутах"""
        try:
            with sqlite3.connect(self.db_file) as db:
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

    def delete_order(self, order_id):
        """удаляет заказ если пользователь решил отменить
        :param order_id: id заказа в который нужно удалить
        :return: True = удален, False = НЕ удален"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM Orders WHERE id = ?", [order_id])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении заказа: {e}")
            return False


class Comments:
    """Содержит методы: show_comments, add_comment, delete_comment"""
    def __init__(self):
        self.db_file = 'Delivery.db'

    def show_comments(self, good_name):
        """Выводит все комментарии в виде [(comment_id, коммент, пользователь)]
        :param good_name: название товара
        :return: список кортежей с данными"""
        try:
            with sqlite3.connect(self.db_file) as db:
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

    def add_comment(self, good_name, user_id, content):
        """добавление нового комментария
        :param good_name: имя товара
        :param user_id: id пользователя
        :param content: содержание комментария
        :return: True = комментарий добалвен, False = не добавлен"""
        try:
            with sqlite3.connect(self.db_file) as db:
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

    def delete_comment(self, com_id):
        """Удаление комментария по id, Админ вписывает id комментария
        :param com_id: id комментария
        :return: True = удален, False = не удален/ошибка"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM Comment WHERE id = ?", [com_id])
                if cursor.rowcount > 0:
                    cursor.execute("DELETE FROM Comments WHERE comment_id = ?", [com_id])
                    return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось удалить комментарий: {e}")
            return False


# ____________________ АДМИН ПАНЕЛЬ ____________________

class AdminManager:
    """Содержит методы: get_admin_data, add_new_admin, show_admins, delete_admin,
    change_admin_status, change_user_to_admin, block_unblock_user"""
    def __init__(self):
        self.db_file = 'Delivery.db'

    def get_admin_data(self, user_id):
        """Получение данных администратора
        :param user_id: id пользователя
        :return: Возвращает данные администратора в виде кортежа (ID, name, полномочия(1-супер, 2- обычный)"""
        try:
            with sqlite3.connect(self.db_file) as db:
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

    def add_new_admin(self, admin_id, name, is_super):
        """Добавление нового администратора
        :param admin_id: id нового админа
        :param name: имя нового админа
        :param is_super: полномочия(1 = супер, 0 = обычный)
        :return: True = добавлен. False = не добавлен/ошибка"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO Admins(user_id, is_super_admin) VALUES(?, ?)", [admin_id, is_super])
                if cursor.rowcount > 0:
                    cursor.execute("INSERT INTO Users(id, user_name, is_admin, block_status) VALUES(?, ?, ?, ?)",
                                   [admin_id, name, 1, 0])
                    return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении администратора: {e}")
            return False

    def show_admins(self, user_id):
        """Отображаем список имеющихся администраторов, кроме того который запрашивает
        :return: возвращаем список кортежей [(name, id, is_super(1-super, 0- нет)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT Users.user_name, Users.id, Admins.is_super_admin
                                  FROM Users
                                  JOIN Admins ON Users.id = Admins.user_id
                                  WHERE Users.id != ?""", [user_id])
                data = cursor.fetchall()
                return data if len(data) != 0 else False
        except sqlite3.Error as e:
            print(f"Не удалось получить список администраторов: {e}")
            return False

    def delete_admin(self, admin_id):
        """Удаление администратора по ID,
        :param admin_id: id администратора
        :return: True = удален, False = не удален"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM Admins WHERE user_id =  ?", [admin_id])
                if cursor.rowcount > 0:
                    cursor.execute("DELETE FROM Users WHERE id =  ?", [admin_id])
                    return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось удалить администратора: {e}")
            return False

    def change_admin_status(self, admin_id):
        """Изменение статуса администратора с простого на Супер и наоборот
        :param admin_id: id админа
        :return: True = статус изменен, False = не изменен/ошибка """
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT is_super_admin FROM Admins WHERE user_id = ?", [admin_id])
                result = cursor.fetchone()
                if result is not None:
                    current_status = result[0]
                    new_status = '1' if current_status == '0' else '0'
                    cursor.execute("UPDATE Admins SET is_super_admin = ? WHERE user_id = ?", [new_status, admin_id])
                    return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось изменить статус: {e}")
            return False

    def change_user_to_admin(self, user_id, key):
        """Изменение статуса пользователя с ключом доступа
        :param user_id: id пользователя
        :param key: ключ введенный пользователем
        :return: True = стал админом False = не удалось сделать админом/ошибка"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT is_for_super FROM Keys_for_admin_panel WHERE key = ?", [key])
                if cursor.rowcount > 1:
                    is_super = cursor.fetchone()
                    cursor.execute("UPDATE Users SET is_admin = ? WHERE id = ?", [1, user_id])
                    if cursor.rowcount > 1:
                        cursor.execute("INSERT INTO Admins (user_id, is_super_admin) VALUES(?, ?)",
                                       [user_id, is_super[0]])
                        return cursor.rowcount > 1
        except sqlite3.Error as e:
            print(f"Не удалось добавить права админстратора пользователю: {e}")
            return False

    def block_unblock_user(self, user_id):
        """Внесение пользователя в черный список,
        :param user_id: id пользователя
        :return: True = добавлен в ЧС, False = НЕ добавлен"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT block_status FROM Users WHERE id = ?", [user_id])
                result = cursor.fetchone()
                if result is not None:
                    current_status = result[0]
                    new_status = 1 if current_status == 0 else 0
                    cursor.execute("UPDATE Users SET block_status = ? WHERE id = ?", [new_status, user_id])
                    return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось изменить статус пользователя: {e}")
            return False


class AdminGoods:
    """Содержит методы: add_new_goods, delete_goods, correct_goods, set_on_pause"""
    def __init__(self):
        self.db_file = 'Delivery.db'

    def add_new_goods(self, params):
        """Добавление нового товара
        :param params:[категория, название, описание, цена, время приготовления, вес, id картинки из ТГ]
        :return: True = данные загружены False = не загружены/ошибка """
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO Goods(category, name, good_description, price, time_to_ready, weight)
                VALUES (?, ?, ?, ?, ?, ?)""", params[:-2])
                if cursor.rowcount > 0:
                    cursor.execute("INSERT INTO Categories(good_name, category_name) VALUES(?, ?)",
                                   [params[1], params[0]])
                    if cursor.rowcount > 0:
                        cursor.execute("INSERT INTO Images(good_name, img_path, tg_id) VALUES(?, ?, ?)",
                                       [params[1], params[-2], params[-1]])
                        return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return False

    def delete_goods(self, good_name):
        """Удаление товра из БД
        :param good_name: имя товара
        :return: True = удален, False =  не удален"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM Goods WHERE name = ?", [good_name])
                good_id = cursor.fetchone()
                if good_id:
                    cursor.execute("DELETE FROM Goods WHERE name = ?", [good_name])
                    if cursor.rowcount > 0:
                        cursor.execute("DELETE FROM Categories WHERE good_name = ?", [good_name])
                        return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении товара: {e}")
            return False

    def correct_goods(self, good_name, new_data):
        """Изменение карточки товара
        :param good_name: название товара
        :param new_data: [категория, название, описание, цена, время приготовления, вес, TG id полученного фото]
        :return: True - изменен, False - не изменен """
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Goods SET category = ?, name = ?, good_description = ?, 
                price = ?, time_to_ready = ?, weight = ? WHERE name = ?""", [*new_data[:-2], good_name])
                if cursor.rowcount > 0:
                    cursor.execute("""UPDATE Categories SET good_name = ?, category_name = ? WHERE good_name = ?""",
                                   [new_data[1], new_data[0], good_name])
                    if cursor.rowcount > 0:
                        cursor.execute(
                            """UPDATE Images SET good_name = ?, img_path = ?, tg_id = ? WHERE good_name = ?""",
                            [new_data[1], new_data[-2], new_data[-1], good_name])
                        return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при внесении изменений в карточку товара: {e}")
            return False

    def set_on_pause(self, good_name):
        """Изменяет статус товара на противоположный
        :param good_name: название товара
        :return: True -изменен статус, False- не изменен/ошибка"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT is_on_pause FROM Goods WHERE name = ?", [good_name])
                result = cursor.fetchone()
                if result is not None:
                    current_status = result[0]
                    new_status = 1 if current_status == 0 else 0
                    cursor.execute("UPDATE Goods SET is_on_pause = ? WHERE name = ?", [new_status, good_name])
                    return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось изменить статус товара: {e}")
            return False


class AdminKeys:
    """Содержит методы: add_new_key, show_keys, delete_key, is_valid_key"""

    def __init__(self):
        self.db_file = 'Delivery.db'

    def add_new_key(self, new_key, is_for_super):
        """Добавление ключа доступа в таблицу
        :param new_key: в формате int либо str.strpi()
        :param is_for_super: в формате int (1= супер админ, 0 = обычный)
        :return: True = добавлен, False = не добавлен/ошибка"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO Keys_for_admin_panel(key, is_for_super) VALUES(?, ?)",
                               [new_key, is_for_super])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось добавить новый ключ: {e}")
            return False

    def show_keys(self):
        """Вывод имеющихся ключей и их статуса
        :return: [(id, ключ, статус)] статус 1- супер админ, 0 - обычный"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id, key, is_for_super FROM Keys_for_admin_panel")
                data = cursor.fetchall()
                return data if len(data) != 0 else False
        except sqlite3.Error as e:
            print(f"Не удалось загрузить данные: {e}")
            return False

    def delete_key(self, key_id):
        """Удаление ключа доступа из БД
        :param key_id: id ключа
        :return: True = ключ удален, False не удален/ошибка"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM Keys_for_admin_panel WHERE id = ?", [key_id])
                return cursor.rowcount > 1
        except sqlite3.Error as e:
            print(f"Не удалось удалить ключ id: {e}")
            return False

    def is_valid_key(self, key):
        """Проверка есть ли ключ
        :param key: ключ введенный пользователем int либо str.strip()
        :return: True = есть ключ, False = нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT key, is_for_super FROM Keys_for_admin_panel WHERE key = ?", [key])
                data = cursor.fetchone()
                return True if data is not None else False
        except sqlite3.Error as e:
            print(f"Не удалось удалить ключ id: {e}")
            return False
