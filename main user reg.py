from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
from DB_project import *

GROUP_ID = '223946162'
GROUP_TOKEN = 'vk1.a.zhRXKGyzrpgcWWQ5aSSFSdckc_EuQLXdT2PLoiX_5ZvTVu1HYMdcaezUMqjQVNKMQmffElYVvu39gBLIFVWYabtm3lQP_Fv8HO5yELeBKK09PXuldnTY2SzcM3dFGtBlpiJijl_xfT-gc8Y7lk1QXHIGDJv2fde9vGqN3x6-9S_plpAa9NWfKaXJKk5mJq4MOwRA_SQSPUQBCzit13VRlg'
API_VERSION = '5.120'

# Запуск бота
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

settings_keyboard_not_inline = dict(one_time=False, inline=False)
settings_keyboard_inline = dict(one_time=False, inline=True)

'''0- шаг регистрации, 1- id пользователя, 2- имя, 3- номер телефона, 4- дата рождения,
   5- старт клавиатуры, 6- конец клавиатуры, 7- шаг по клавиатуре между стартом и концом,
   8- список категорий/товаров, 9- "category" или "goods" для проверки, 10- клавиатура.
'''
users_id_info = [0, "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

start_bot_msg = ("start", "старт", "начать", "начало", "бот", "меню категорий")
CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app", "text")


text_instruction = """
1. Для начала работы нажмите : "запустить бота"
2. Выберите нужную Вам  категорию, если не нашли на первой странице, нажмите : "далее"
Затем введите номер нужной услуги и отправьте сообщением боту. 
3. Также вы всегда можете найти актуальный перечень всех акций и предложений нажав кнопку : "таблица со всеми промокодами"
4. Чтобы всегда оставаться на связи, подпишитесь на нас в телеграмм канале, нажав кнопку : "Мы в Телеграме"
"""

print("Ready")

category_goods = dict()
# products_info = dict()
categories = get_categories()
goods = []
basket = dict()


for categ in categories:
    goods_sql = get_from_category(categ)
    category_goods[categ] = goods_sql
    for pr in goods_sql:
        goods.append(pr)

print(categories)
print(category_goods)
print(goods)

# for info in list_of_lists[1:]:
#     if info[8] not in category_products:
#         category_products[info[8]] = []
#         # список уникальных категорий
#         categories.append(info[8])
#     if info[0] not in category_products[info[8]]:
#         category_products[info[8]].append(info[0])
#     if info[0] not in products_info:
#         products_info[info[0]] = []
#         # список уникальных компаний
#         products.append(info[0])
#     products_info[info[0]].append(info[:9])

'''Категории'''
def create_keyboard(begin, finish, index, name, text_for_buttons):
    keyboard = VkKeyboard(**settings_keyboard_inline)

    for num in range(begin[index], finish[index]):
        keyboard.add_button(label=f"{name[num]}", color=VkKeyboardColor.SECONDARY,
                            payload={"type": f"{text_for_buttons}"})
        keyboard.add_line()

    if len(begin) > 1:
        if begin[index] == 0:
            keyboard.add_callback_button(label='Далее', color=VkKeyboardColor.PRIMARY, payload={"type": "next"})
        elif begin[index] + 4 < len(name):
            keyboard.add_callback_button(label='Назад', color=VkKeyboardColor.PRIMARY, payload={"type": "previous"})
            keyboard.add_callback_button(label='Далее', color=VkKeyboardColor.PRIMARY, payload={"type": "next"})
        else:
            keyboard.add_callback_button(label='Назад', color=VkKeyboardColor.PRIMARY, payload={"type": "previous"})
        keyboard.add_line()

    if text_for_buttons == "category":
        keyboard.add_callback_button(label='Заказы', color=VkKeyboardColor.POSITIVE, payload={"type": "orders"})
    elif text_for_buttons == "goods":
        keyboard.add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE)
    keyboard.add_callback_button(label='Корзина', color=VkKeyboardColor.NEGATIVE, payload={"type": "basket"})

    return keyboard

count = 1
for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:

        if event.obj.message["text"] != '':
            if event.from_user:
                # print(event.obj)
                # print(event.obj.message["from_id"])

                '''Проверка на первый вход в бота с регистрацией'''
                if is_new(event.obj.message["from_id"]):
                    if event.obj.message["text"].lower() in start_bot_msg:
                        users_id_info[0] = 1
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            # keyboard=keyboard_main_menu.get_keyboard(),
                            message="Привет, ты у нас впервые, давай пройдем регистрацию\nВведите ваше ФИО:")
                    elif users_id_info[0] == 1:
                        users_id_info[0] = 2
                        users_id_info[1] = event.obj.message["from_id"]
                        users_id_info[2] = event.obj.message["text"]
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            message="Введите номер телефона (с кодом +375 или 80):")
                    elif users_id_info[0] == 2:
                        tel = event.obj.message["text"].strip()
                        scheme = "('{0}'[:4] == '+375' and '{0}'[1:].isdigit() and len('{0}') == 13) or" \
                                 "('{0}'[:2] == '80' and '{0}'[1:].isdigit() and len('{0}') == 11)"

                        if eval(scheme.format(tel)):
                            users_id_info[0] = 3
                            users_id_info[3] = event.obj.message["text"]

                            vk.messages.send(
                                user_id=event.obj.message['from_id'],
                                random_id=get_random_id(),
                                peer_id=event.obj.message['from_id'],
                                message="Введите дату рождения:")
                        else:
                            vk.messages.send(
                                user_id=event.obj.message['from_id'],
                                random_id=get_random_id(),
                                peer_id=event.obj.message['from_id'],
                                message="Неверный формат ввода номера телефона, повторите попытку:")

                    #'''Отправка сообщения с подтверждением или перезаписью введенных данных'''
                    elif users_id_info[0] == 3:
                        users_id_info[4] = event.obj.message["text"]

                        keyboard_accept_decline = VkKeyboard(**settings_keyboard_inline)
                        keyboard_accept_decline.add_callback_button(label='Подтвердить', color=VkKeyboardColor.POSITIVE,
                                                                    payload={"reg_user": "yes"})
                        keyboard_accept_decline.add_callback_button(label='Заполнить заново',
                                                                    color=VkKeyboardColor.NEGATIVE,
                                                                    payload={"reg_user": "no"})

                        user_info = f"Подтвердите введенные вами данные:\nИмя: {users_id_info[2]}\nТелефон: " \
                                    f"{users_id_info[3]}\nДата рождения: {users_id_info[4]}"
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=keyboard_accept_decline.get_keyboard(),
                            message=f"{user_info}")

                elif not is_new(event.obj.message["from_id"]):
                    if event.obj.message["text"].lower() in start_bot_msg:
                        len_category = len(categories)
                        users_id_info[5] = [i for i in range(0, len_category, 4)]
                        users_id_info[6] = [i for i in range(4, len_category, 4)] + [len_category]
                        users_id_info[7] = 0
                        users_id_info[8] = categories
                        users_id_info[9] = "category"
                        users_id_info[10] = create_keyboard(users_id_info[5], users_id_info[6], users_id_info[7],
                                                            users_id_info[8], users_id_info[9])
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=users_id_info[10].get_keyboard(),
                            message="Выберите доступную категорию товаров:")


                if event.obj.message["text"] in categories:
                    len_goods = len(category_goods[event.obj.message["text"]])
                    users_id_info[5] = [i for i in range(0, len_goods, 4)]
                    users_id_info[6] = [i for i in range(4, len_goods, 4)] + [len_goods]
                    users_id_info[7] = 0
                    users_id_info[8] = category_goods[event.obj.message["text"]]
                    users_id_info[9] = "goods"
                    users_id_info[10] = create_keyboard(users_id_info[5], users_id_info[6], users_id_info[7],
                                                        users_id_info[8], users_id_info[9])
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=users_id_info[10].get_keyboard(),
                        message="Выберите доступную товары:")

                elif event.obj.message["text"] in goods:
                    print(314242)
                    users_id_info[10] = VkKeyboard(**settings_keyboard_inline)
                    users_id_info[10].add_callback_button(label='-1', color=VkKeyboardColor.NEGATIVE,
                                                 payload={"count": "-1"})
                    users_id_info[10].add_callback_button(label=f"Количество - {count}", color=VkKeyboardColor.POSITIVE,
                                                 payload={"count": " "})
                    users_id_info[10].add_callback_button(label='+1', color=VkKeyboardColor.POSITIVE,
                                                 payload={"count": "+1"})
                    users_id_info[10].add_line()

                    users_id_info[10].add_callback_button(label='Добавить', color=VkKeyboardColor.POSITIVE,
                                                 payload={"type": "add"})
                    users_id_info[10].add_callback_button(label='Корзина', color=VkKeyboardColor.NEGATIVE,
                                                 payload={"type": "basket"})
                    users_id_info[10].add_line()

                    users_id_info[10].add_callback_button(label='< Блюда', color=VkKeyboardColor.POSITIVE,
                                                 payload={"type": "dishes left"})
                    users_id_info[10].add_callback_button(label='Блюда >', color=VkKeyboardColor.POSITIVE,
                                                 payload={"type": "dishes right"})
                    users_id_info[10].add_line()

                    users_id_info[10].add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE)
                    users_id_info[10].add_callback_button(label='Комментарии', color=VkKeyboardColor.POSITIVE,
                                                 payload={"type": "commentary"})
                    '''имя 1  описание 2  грамовка 3  цена 4  рейтинг 5  картинка 6
                    ('имя', 'описание', 1000, 12.0, 4, None)'''
                    text = ""
                    info = show_product_card(event.obj.message["text"])
                    for i in info[:-1]:
                        text += str(i) + "\n"

                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=users_id_info[10].get_keyboard(),
                        message=text)

    elif event.type == VkBotEventType.MESSAGE_EVENT:
        # print(event.object)
        if event.object.payload.get('type') in CALLBACK_TYPES:
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
        else:

            '''Подтверждение или перезапись введенных пользователем данных'''
            if event.object.payload.get("reg_user") == "yes":
                registrator(users_id_info[1:])
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message="Регистрация прошла успешно.",
                    conversation_message_id=event.obj.conversation_message_id)

                '''Вывод сообщения с категориями доступных товаров'''
                len_category = len(categories)
                users_id_info[5] = [i for i in range(0, len_category, 4)]
                users_id_info[6] = [i for i in range(4, len_category, 4)] + [len_category]
                users_id_info[7] = 0
                users_id_info[8] = categories
                users_id_info[9] = "category"
                users_id_info[10] = create_keyboard(users_id_info[5], users_id_info[6], users_id_info[7],
                                                    users_id_info[8], users_id_info[9])
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=users_id_info[10].get_keyboard(),
                    message="Выберите доступную категорию товаров:")
            elif event.object.payload.get("reg_user") == "no":
                users_id_info[0] = 1
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Введите ваше ФИО:',
                    conversation_message_id=event.obj.conversation_message_id)

            '''Переход в корзину'''
            if event.object.payload.get("type") == "basket":
                if not basket:
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Ваша корзина пустая, выберите что нибудь.',
                        conversation_message_id=event.obj.conversation_message_id)
                    vk.messages.send(
                        user_id=event.object.user_id,
                        random_id=get_random_id(),
                        peer_id=event.object.peer_id,
                        # keyboard=keyboard_categories.get_keyboard(),
                        message="Выберите доступную категорию товаров:")
                else:
                    pass


            if event.object.payload.get('type') == "next":
                if users_id_info[9] == "category":
                    users_id_info[7] += 1
                    users_id_info[10] = create_keyboard(users_id_info[5], users_id_info[6], users_id_info[7],
                                                        users_id_info[8], users_id_info[9])
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную категорию товаров:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[10].get_keyboard())
                elif users_id_info[9] == "goods":
                    users_id_info[7] += 1
                    users_id_info[10] = create_keyboard(users_id_info[5], users_id_info[6], users_id_info[7],
                                                        users_id_info[8], users_id_info[9])
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную товары:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[10].get_keyboard())

            elif event.object.payload.get('type') == "previous":
                if users_id_info[9] == "category":
                    users_id_info[7] -= 1
                    users_id_info[10] = create_keyboard(users_id_info[5], users_id_info[6], users_id_info[7],
                                                        users_id_info[8], users_id_info[9])
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную категорию товаров:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[10].get_keyboard())
                elif users_id_info[9] == "goods":
                    users_id_info[7] -= 1
                    users_id_info[10] = create_keyboard(users_id_info[5], users_id_info[6], users_id_info[7],
                                                        users_id_info[8], users_id_info[9])
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную товары:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[10].get_keyboard())
