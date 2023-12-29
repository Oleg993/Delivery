import sqlite3
from datetime import datetime
from PIL import Image
import io

from DB_project import is_valid_key


print(is_valid_key(331))


    # (2, 'Fix Dark', 'Fix Dark - это таинственное темное пиво, которое пленит своей глубиной и насыщенным вкусом. Его аромат обволакивает нежными нотами шоколада и кофе, а густая пена создает иллюзию ночного неба. Откройте для себя магию темных оттенков в каждом глотке Fix Dark.', 4.99, 3, 4, 500, 2, open('imgs/beer.jpeg', 'rb').read()),
    # (2, 'Beer OuroPretana', 'Beer OuroPretana - это темное пиво с глубокими оттенками и богатым вкусом. Его аромат раскрывается нотками шоколада, кофе и карамели, создавая приятное слияние сладости и горечи. Пиво обладает плотной текстурой и умеренной газировкой, что придает ему особую гармонию. Beer OuroPretana - это идеальный выбор для ценителей темных сортов пива, желающих насладиться насыщенным и утонченным вкусом.', 5.35, 3, 4, 500, 2, open('imgs/beer2.jpeg', 'rb').read()),
    # (1, 'Вкуснейший стейк', 'Вкуснейший стейк, приготовленный по традиционному рецепту, сопровождается хрустящими картофельными фри. Нежное мясо и хрустящая корочка картошки создают идеальное сочетание текстур и ароматов. Приготовьтесь к настоящему кулинарному наслаждению!', 25.90, 25, 4, 455, 2, open('imgs/black steak.jpeg', 'rb').read()),
    # (1, 'Вкусная жареная курица', 'Вкусная жареная курица с сочными кусочками манго и свежей зеленью - это настоящий взрыв вкусов! Нежное мясо курицы сочетается с сладостью манго и ароматом свежей зелени, создавая идеальное блюдо для наслаждения. Попробуйте эту уникальную комбинацию и погрузитесь в мир гастрономического наслаждения!', 17.20, 20, 4, 530, 2, open('imgs/Chicken.jpeg', 'rb').read()),
    # (1, 'Черный шоколадный торт', 'Ароматный кофе, приготовленный с любовью и мастерством. Идеальное сочетание вкуса, аромата и тела, чтобы пробудить в Вас энергию и вдохновение.', 12.0, 20, 4, 350, 2, open('imgs/chocolate cake.jpeg', 'rb').read()),
    # (2, 'Освежающая безалкогольная Кока-Кола Лайт', 'Освежающая безалкогольная Кока-Кола Лайт - идеальный выбор для тех, кто ценит непревзойденный вкус без лишних калорий.', 3.99, 3, 4, 500, 2, open('imgs/coca-cola.jpeg', 'rb').read()),
    # (2, 'Ароматный кофе', 'Ароматный кофе, приготовленный с любовью и мастерством. Идеальное сочетание вкуса, аромата и тела, чтобы пробудить в Вас энергию и вдохновение.', 7.20, 5, 4, 400, 2, open('imgs/coffee.jpeg', 'rb').read()),
    # (1, 'Черная паста с креветками', 'Черная паста с королевскими креветками - это изысканное блюдо, которое поразит Вас своим вкусом и элегантностью. Ароматная паста, окрашенная натуральным чернилами каракатицы, и сочные креветки создают идеальное сочетание, которое покорит ваш вкусовой рецептор.', 19.0, 25, 4, 430, 2, open('imgs/pasta.jpeg', 'rb').read()),
    # (1, 'Соблазнительная пицца на черном тесте', 'Соблазнительная пицца на черном тесте - это искусство вкуса и эстетики. Сочные томаты, ароматные специи и аппетитные топпинги создают идеальное сочетание на каждом кусочке. Отведайте этот мрачно-прекрасный кулинарный шедевр!', 16.50, 15, 4, 510, 2, open('imgs/pizza.jpeg', 'rb').read()),
    # (1, 'Суши', 'Суши – искусство вкуса и эстетики. Сочетание свежих ингредиентов, нежного риса и изысканных соусов создает неповторимый вкусовой опыт. Погрузитесь в мир японской кулинарии с каждым кусочком. Отведайте суши и ощутите гармонию вкусов и текстур.', 19.90, 20, 4, 620, 2, open('imgs/Sushi.jpeg', 'rb').read()),
    # (2, 'Зимний чай с корицей', 'В глубокой зимней ночи, когда мороз за окном сверкает, замечательный зимний чай с нотками корицы становится настоящим утешением. Его аромат и тепло согревают душу, а палочка корицы добавляет неповторимую нотку праздника. Каждый глоток этого чая – это волшебное путешествие в мир уюта и комфорта.', 4.50, 5, 4, 400, 2, open('imgs/tea.jpeg', 'rb').read())

# cursor.executemany(insert_query, data)
# cursor.execute('DELETE FROM Categories')

# add_new_goods([2, 'Fix Dark', 'Fix Dark - это таинственное темное пиво, которое пленит своей глубиной и насыщенным вкусом. Его аромат обволакивает нежными нотами шоколада и кофе, а густая пена создает иллюзию ночного неба. Откройте для себя магию темных оттенков в каждом глотке Fix Dark.', 4.99, 3, 500, open('imgs/beer.jpeg', 'rb').read()])
#
# add_new_goods([2, 'Beer OuroPretana', 'Beer OuroPretana - это темное пиво с глубокими оттенками и богатым вкусом. Его аромат раскрывается нотками шоколада, кофе и карамели, создавая приятное слияние сладости и горечи. Пиво обладает плотной текстурой и умеренной газировкой, что придает ему особую гармонию. Beer OuroPretana - это идеальный выбор для ценителей темных сортов пива, желающих насладиться насыщенным и утонченным вкусом.', 5.35, 3, 500, open('imgs/beer2.jpeg', 'rb').read()])
#
# add_new_goods([1, 'Соблазнительная пицца на черном тесте', 'Соблазнительная пицца на черном тесте - это искусство вкуса и эстетики. Сочные томаты, ароматные специи и аппетитные топпинги создают идеальное сочетание на каждом кусочке. Отведайте этот мрачно-прекрасный кулинарный шедевр!', 16.50, 15, 510, open('imgs/pizza.jpeg', 'rb').read()])
#
# add_new_goods([1, 'Черная паста с креветками', 'Черная паста с королевскими креветками - это изысканное блюдо, которое поразит Вас своим вкусом и элегантностью. Ароматная паста, окрашенная натуральным чернилами каракатицы, и сочные креветки создают идеальное сочетание, которое покорит ваш вкусовой рецептор.', 19.0, 25, 430, open('imgs/pasta.jpeg', 'rb').read()])




# with sqlite3.connect('Delivery.db') as db:
#     cursor = db.cursor()
#
#     query = """
#     CREATE TABLE IF NOT EXISTS Categories(
#         id INTEGER PRIMARY KEY,
#         description INTEGER,
#         category_name TEXT(100)
#     );
#
#     CREATE TABLE IF NOT EXISTS Goods(
#         Id INTEGER PRIMARY KEY ,
#         category INTEGER,
#         name TEXT(100),
#         good_description TEXT(500),
#         price REAL DEFAULT 0.0,
#         time_to_ready INTEGER,
#         ranking INTEGER DEFAULT 4,
#         weight INTEGER,
#         is_on_pause INTEGER DEFAULT 2,
#         image BLOB,
#         FOREIGN KEY (category) REFERENCES Categories(description)
#     );
#         CREATE TABLE IF NOT EXISTS Recipe(
#         Id INTEGER PRIMARY KEY ,
#         good_id INTEGER,
#         composition TEXT(100),
#         description TEXT(500),
#         FOREIGN KEY (good_id) REFERENCES Goods(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Products(
#         id INTEGER PRIMARY KEY ,
#         name TEXT(50),
#         validity_days INTEGER,
#         grams_or_kg REAL,
#         temperature REAL,
#         product_type TEXT
#     );
#
#     CREATE TABLE IF NOT EXISTS Products_availability(
#         product_id INTEGER PRIMARY KEY,
#         quantity INTEGER,
#         valid_until DATETIME,
#         delivery_date DATETIME,
#         FOREIGN KEY (product_id) REFERENCES Products(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Orders(
#         Id INTEGER PRIMARY KEY ,
#         user_id INTEGER,
#         user_tel TEXT(30),
#         address TEXT(300),
#         total_price REAL,
#         order_status TEXT(30),
#         order_date DATATIME,
#         delivery_time INTEGER,
#         user_note TEXT(300),
#         FOREIGN KEY (user_id) REFERENCES Users(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Goods_in_order(
#         order_id INTEGER,
#         good_id INTEGER,
#         quantity INTEGER,
#         FOREIGN KEY (order_id) REFERENCES Orders(id),
#         FOREIGN KEY (good_id) REFERENCES Goods(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Users(
#         id INTEGER PRIMARY KEY,
#         user_name TEXT(100),
#         phone_number TEXT(30),
#         birthday DATETIME,
#         is_admin INTEGER DEFAULT 2,
#         block_status  INTEGER DEFAULT 1,
#         last_address TEXT(300) DEFAULT NONE
#     );
#
#     CREATE TABLE IF NOT EXISTS Admins(
#         id INTEGER PRIMARY KEY,
#         user_id INTEGER,
#         is_super_admin INTEGER,
#         FOREIGN KEY (user_id) REFERENCES Users(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Comments(
#         id INTEGER PRIMARY KEY,
#         comment_id INTEGER,
#         good_id INTEGER,
#         user_id INTEGER,
#         status INTEGER DEFAULT NONE,
#         FOREIGN KEY (good_id) REFERENCES Goods(id),
#         FOREIGN KEY (user_id) REFERENCES Users(id),
#         FOREIGN KEY (comment_id) REFERENCES Comment(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Comment(
#         id INTEGER PRIMARY KEY,
#         content TEXT(300),
#         from_user INTEGER,
#         FOREIGN KEY (from_user) REFERENCES Users(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Keys_for_admin_panel(
#         id INTEGER PRIMARY KEY,
#         key TEXT(20),
#         is_for_super INTEGER
#     );
#     """
#
#     cursor.executescript(query)
