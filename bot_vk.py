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

users_id_info = {}

start_bot_msg = ("start", "старт", "начать", "начало", "бот", "меню категорий", "н")
CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app", "text")

print("Ready")

category_goods = dict()
categories = get_categories()
goods = []
basket = dict()

for categ in categories:
    goods_sql = get_from_category(categ)
    category_goods[categ] = goods_sql
    for pr in goods_sql:
        goods.append(pr[0])


'''Категории'''
def create_new_keyboard(begin, finish, index, name, text_for_buttons):
    # begin, finish, index, name, text_for_buttons = info_for_keyboard
    keyboard = VkKeyboard(**settings_keyboard_inline)

    if text_for_buttons != "cart":
        for num in range(begin[index], finish[index]):
            keyboard.add_button(label=f"{name[num]}", color=VkKeyboardColor.SECONDARY,
                                payload={"type": f"{text_for_buttons}"})
            keyboard.add_line()
    else:
        for num in range(begin[index], finish[index]):
            keyboard.add_callback_button(label=f"{name[num][0]} - {name[num][1]}", color=VkKeyboardColor.SECONDARY,
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
        keyboard.add_callback_button(label='Корзина', color=VkKeyboardColor.NEGATIVE, payload={"type": "basket"})
    elif text_for_buttons == "goods":
        keyboard.add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE)
        keyboard.add_callback_button(label='Корзина', color=VkKeyboardColor.NEGATIVE, payload={"type": "basket"})
    elif text_for_buttons == "cart":
        keyboard.add_callback_button(label='Подтвердить заказ', color=VkKeyboardColor.POSITIVE, payload={"order": "accept"})
        keyboard.add_line()
        keyboard.add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE, payload={"type": "basket"})
        keyboard.add_callback_button(label='Отменить', color=VkKeyboardColor.NEGATIVE, payload={"order": "cancel"})

    return keyboard

def keyboard_spawn(id):
    return create_new_keyboard(users_id_info[id][5], users_id_info[id][6], users_id_info[id][7],
                               users_id_info[id][8], users_id_info[id][9])

for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:

        if event.obj.message["text"] != '':
            if event.from_user:
                if event.obj.message['from_id'] not in users_id_info:
                    '''0/ информация о товаре(карточка), 1- id пользователя/ общая информация 
                       для вывода, 2- имя, 3- номер телефона, 4- дата рождения, 5- старт клавиатуры, 
                       6- конец клавиатуры, 7- шаг по клавиатуре между стартом и концом, 8- список категорий/товаров, 
                       9- "category" или "goods" для проверки, 10- клавиатура, 11- корзина, 
                       12- количество товара в корзину, 13 - длина корзины, 14- информация о сформированных заказах,
                       15- сгрупированная инфомация заказов пользователя,
                       20- адрес доставки пользователя, 21- индикатор добавления адреса пользователем,
                       22 - комментарий пользователя, 23- индикатор добавления комментария,
                       24- вся информация о пользователе,
                       
                       0 - шаг регистрации + информация для регистрации, 2- клавиатура
                    '''
                    users_id_info[event.obj.message['from_id']] = [[0, event.obj.message['from_id']], [], "3", "4",
                                                                   [], "6", "7", "8", "9", "10",
                                                                   [], 1, "13", "14", "", "", "", "", "",
                                                                   "20", "21", "22", "23", "24", ""]

                '''Проверка на первый вход в бота с регистрацией'''
                if is_new(event.obj.message["from_id"]):
                    if event.obj.message["text"].lower() in start_bot_msg:
                        users_id_info[event.obj.message['from_id']][0][0] = 1
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            message="Привет, ты у нас впервые, давай пройдем регистрацию\nВведите ваше ФИО:")
                    elif users_id_info[event.obj.message['from_id']][0][0] == 1:
                        users_id_info[event.obj.message['from_id']][0][0] = 2
                        users_id_info[event.obj.message['from_id']][0].append(event.obj.message["text"])
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            message="Введите номер телефона (с кодом +375 или 80):")
                    elif users_id_info[event.obj.message['from_id']][0][0] == 2:
                        tel = event.obj.message["text"].strip()
                        scheme = "('{0}'[:4] == '+375' and '{0}'[1:].isdigit() and len('{0}') == 13) or" \
                                 "('{0}'[:2] == '80' and '{0}'[1:].isdigit() and len('{0}') == 11)"

                        if eval(scheme.format(tel)):
                            users_id_info[event.obj.message['from_id']][0][0] = 3
                            users_id_info[event.obj.message['from_id']][0].append(event.obj.message["text"])
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
                    elif users_id_info[event.obj.message['from_id']][0][0] == 3:
                        users_id_info[event.obj.message['from_id']][0].append(event.obj.message["text"])
                        keyboard_accept_decline = VkKeyboard(**settings_keyboard_inline)
                        keyboard_accept_decline.add_callback_button(label='Подтвердить', color=VkKeyboardColor.POSITIVE,
                                                                    payload={"reg_user": "yes"})
                        keyboard_accept_decline.add_callback_button(label='Заполнить заново',
                                                                    color=VkKeyboardColor.NEGATIVE,
                                                                    payload={"reg_user": "no"})
                        user_info = f"Подтвердите введенные вами данные:\n" \
                                    f"Имя: {users_id_info[event.obj.message['from_id']][0][2]}\n" \
                                    f"Телефон: {users_id_info[event.obj.message['from_id']][0][3]}\n" \
                                    f"Дата рождения: {users_id_info[event.obj.message['from_id']][0][4]}"
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=keyboard_accept_decline.get_keyboard(),
                            message=f"{user_info}")

                # '''Вывод первичного меню категорий товаров'''
                elif not is_new(event.obj.message["from_id"]):
                    if event.obj.message["text"].lower() in start_bot_msg:
                        users_id_info[event.obj.message['from_id']][11] = []  # создание пустой корзины
                        len_category = len(categories)
                        users_id_info[event.obj.message['from_id']][5] = [i for i in range(0, len_category, 4)]
                        users_id_info[event.obj.message['from_id']][6] = [i for i in range(4, len_category, 4)] + \
                                                                         [len_category]
                        users_id_info[event.obj.message['from_id']][7] = 0
                        users_id_info[event.obj.message['from_id']][8] = categories
                        users_id_info[event.obj.message['from_id']][9] = "category"
                        users_id_info[event.obj.message['from_id']][10] = keyboard_spawn(event.obj.message['from_id'])
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=users_id_info[event.obj.message['from_id']][10].get_keyboard(),
                            message="Выберите доступную категорию товаров:")

                if event.obj.message["text"] in categories:
                    len_goods = len(category_goods[event.obj.message["text"]])
                    users_id_info[event.obj.message['from_id']][5] = [i for i in range(0, len_goods, 4)]
                    users_id_info[event.obj.message['from_id']][6] = [i for i in range(4, len_goods, 4)] + [len_goods]
                    users_id_info[event.obj.message['from_id']][7] = 0
                    users_id_info[event.obj.message['from_id']][8] = [name[0] for name in category_goods[event.obj.message["text"]]]
                    users_id_info[event.obj.message['from_id']][9] = "goods"
                    users_id_info[event.obj.message['from_id']][10] = keyboard_spawn(event.obj.message['from_id'])
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=users_id_info[event.obj.message['from_id']][10].get_keyboard(),
                        message="Выберите доступную товары:")

                elif event.obj.message["text"] in goods:
                    users_id_info[event.obj.message['from_id']][10] = VkKeyboard(**settings_keyboard_inline)

                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label=f"Количество - {users_id_info[event.obj.message['from_id']][12]}",
                                                                                        color=VkKeyboardColor.PRIMARY,
                                                                                        payload={"count": " "})
                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='+1',
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"count": "+1", "count_good": "change"})
                    users_id_info[event.obj.message['from_id']][10].add_line()

                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='Добавить',
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"type": "add"})
                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='Корзина',
                                                                                        color=VkKeyboardColor.NEGATIVE,
                                                                                        payload={"type": "basket"})
                    users_id_info[event.obj.message['from_id']][10].add_line()

                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='< Блюда',
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"type": "dishes left"})
                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='Блюда >',
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"type": "dishes right"})
                    users_id_info[event.obj.message['from_id']][10].add_line()

                    users_id_info[event.obj.message['from_id']][10].add_button(label='Меню категорий',
                                                                               color=VkKeyboardColor.POSITIVE)
                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='Комментарии',
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"type": "commentary"})

                    names = ["Название: ", "Описание: ", "Граммовка: ", "Цена: ", "Рейтинг: "]
                    '''id, category, name, good_description, price, time_to_ready, ranking, weight, is_on_pause'''
                    '''(10, 'Блюда', 'Суши', 'Суши – искусство вкуса и эстетики. Сочетание свежих ингредиентов, нежного 
                    риса и изысканных соусов создает неповторимый вкусовой опыт. Погрузитесь в мир японской кулинарии с 
                    каждым кусочком. Отведайте суши и ощутите гармонию вкусов и текстур.', 19.9, 20, 4, 620, 0'''
                    print(show_product_card(event.obj.message["text"]))
                    users_id_info[event.obj.message['from_id']][0] = show_product_card(event.obj.message["text"])
                    users_id_info[event.obj.message['from_id']][1] = [names[0] + users_id_info[event.obj.message['from_id']][0][2] + "\n",
                                                                      names[1] + users_id_info[event.obj.message['from_id']][0][3] + "\n",
                                                                      names[2] + str(users_id_info[event.obj.message['from_id']][0][7]) + "\n",
                                                                      names[3] + str(users_id_info[event.obj.message['from_id']][0][4]) + "\n",
                                                                      names[4] + str(users_id_info[event.obj.message['from_id']][0][6])]
                    users_id_info[event.obj.message['from_id']][1] = "".join(users_id_info[event.obj.message['from_id']][1])
                    # print(users_id_info[event.obj.message['from_id']][0])
                    # print(users_id_info[event.obj.message['from_id']][1])
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=users_id_info[event.obj.message['from_id']][10].get_keyboard(),
                        message=users_id_info[event.obj.message['from_id']][1])

                '''Добавление нового адреса пользователя'''
                if users_id_info[event.obj.message['from_id']][21] == "add address":
                    users_id_info[event.obj.message['from_id']][21] = "21"
                    users_id_info[event.obj.message['from_id']][20] = event.obj.message["text"]
                    correct_delivery_address(users_id_info[event.obj.message['from_id']][20], event.obj.message['from_id'])

                    users_id_info[event.obj.message['from_id']][10] = VkKeyboard(**settings_keyboard_inline)
                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label="Добавить",
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"commentary": "add"})
                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='Продолжить без комментария',
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"commentary": "skip"})
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=users_id_info[event.obj.message['from_id']][10].get_keyboard(),
                        message="Хотите оставить комментарий ?")

                '''Добавление комментария к заказу'''
                if users_id_info[event.obj.message['from_id']][23] == "add":
                    users_id_info[event.obj.message['from_id']][23] = "23"
                    users_id_info[event.obj.message['from_id']][22] = event.obj.message["text"]

                    users_id_info[event.obj.message['from_id']][10] = VkKeyboard(**settings_keyboard_inline)
                    users_id_info[event.obj.message['from_id']][10].add_button(label='Меню категорий',
                                                                               color=VkKeyboardColor.POSITIVE)
                    users_id_info[event.obj.message['from_id']][10].add_callback_button(label='Заказы',
                                                                                        color=VkKeyboardColor.POSITIVE,
                                                                                        payload={"type": "orders"})
                    users_id_info[event.obj.message['from_id']][24] = get_user_data(event.obj.message['from_id'])
                    from_cart_into_db([users_id_info[event.obj.message['from_id']][24][i] for i in [0, 2, 6]],
                                      get_total_price(users_id_info[event.obj.message['from_id']][11]),
                                      users_id_info[event.obj.message['from_id']][11],
                                      30,
                                      users_id_info[event.obj.message['from_id']][22])

                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=users_id_info[event.obj.message['from_id']][10].get_keyboard(),
                        message="Заказ успешно сформирован.")

    elif event.type == VkBotEventType.MESSAGE_EVENT:
        # print(event.object)
        if event.object.payload.get('type') in CALLBACK_TYPES:
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
        else:

            '''Подтверждение или перезапись введенных пользователем данных регистрации'''
            if event.object.payload.get("reg_user") == "yes":
                registrator(users_id_info[event.object.user_id][0][1:])
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message="Регистрация прошла успешно.",
                    conversation_message_id=event.obj.conversation_message_id)

                '''Вывод сообщения с категориями доступных товаров'''
                len_category = len(categories)
                users_id_info[event.object.user_id][5] = [i for i in range(0, len_category, 4)]
                users_id_info[event.object.user_id][6] = [i for i in range(4, len_category, 4)] + [len_category]
                users_id_info[event.object.user_id][7] = 0
                users_id_info[event.object.user_id][8] = categories
                users_id_info[event.object.user_id][9] = "category"
                users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                    message="Выберите доступную категорию товаров:")
            elif event.object.payload.get("reg_user") == "no":
                print(users_id_info[event.object.user_id][0])
                users_id_info[event.object.user_id][0] = [1, event.object.user_id]
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Введите ваше ФИО:',
                    conversation_message_id=event.obj.conversation_message_id)

            '''Изменение количества выбранного товара для добавления в корзину'''
            if event.object.payload.get('count_good') == "change":
                users_id_info[event.object.user_id][12] += int(event.object.payload.get('count'))

                users_id_info[event.object.user_id][10] = VkKeyboard(**settings_keyboard_inline)
                if users_id_info[event.object.user_id][12] > 1:
                    users_id_info[event.object.user_id][10].add_callback_button(label='-1',
                                                                                color=VkKeyboardColor.NEGATIVE,
                                                                                payload={"count": "-1",
                                                                                         "count_good": "change"})

                users_id_info[event.object.user_id][10].add_callback_button(label=f"Количество - {users_id_info[event.object.user_id][12]}",
                                                                            color=VkKeyboardColor.PRIMARY,
                                                                            payload={"count": " "})
                users_id_info[event.object.user_id][10].add_callback_button(label='+1',
                                                                            color=VkKeyboardColor.POSITIVE,
                                                                            payload={"count": "+1",
                                                                                     "count_good": "change"})
                users_id_info[event.object.user_id][10].add_line()

                users_id_info[event.object.user_id][10].add_callback_button(label='Добавить',
                                                                            color=VkKeyboardColor.POSITIVE,
                                                                            payload={"type": "add"})
                users_id_info[event.object.user_id][10].add_callback_button(label='Корзина',
                                                                            color=VkKeyboardColor.NEGATIVE,
                                                                            payload={"type": "basket"})
                users_id_info[event.object.user_id][10].add_line()

                users_id_info[event.object.user_id][10].add_callback_button(label='< Блюда',
                                                                            color=VkKeyboardColor.POSITIVE,
                                                                            payload={"type": "dishes left"})
                users_id_info[event.object.user_id][10].add_callback_button(label='Блюда >',
                                                                            color=VkKeyboardColor.POSITIVE,
                                                                            payload={"type": "dishes right"})
                users_id_info[event.object.user_id][10].add_line()

                users_id_info[event.object.user_id][10].add_button(label='Меню категорий',
                                                                   color=VkKeyboardColor.POSITIVE)
                users_id_info[event.object.user_id][10].add_callback_button(label='Комментарии',
                                                                            color=VkKeyboardColor.POSITIVE,
                                                                            payload={"type": "commentary"})

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message=users_id_info[event.object.user_id][1],
                    keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                    conversation_message_id=event.obj.conversation_message_id)

            '''Добавление товара во временную корзину'''
            if event.object.payload.get('type') == "add":
                users_id_info[event.object.user_id][11].append([[users_id_info[event.object.user_id]][0][0][2],
                                                                users_id_info[event.object.user_id][12]])
                print([users_id_info[event.object.user_id]][0][0][2])
                users_id_info[event.object.user_id][12] = 1
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Товар успешно добавлен.',
                    conversation_message_id=event.obj.conversation_message_id)
                # print(users_id_info[event.object.user_id][11])

                len_category = len(categories)
                users_id_info[event.object.user_id][5] = [i for i in range(0, len_category, 4)]
                users_id_info[event.object.user_id][6] = [i for i in range(4, len_category, 4)] + [len_category]
                users_id_info[event.object.user_id][7] = 0
                users_id_info[event.object.user_id][8] = categories
                users_id_info[event.object.user_id][9] = "category"
                users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                    message="Выберите доступную категорию товаров:")

            '''Отмена текущего заказа / подтверждение'''
            if event.object.payload.get("order") == "cancel":
                users_id_info[event.object.user_id][11] = []
                len_category = len(categories)
                users_id_info[event.object.user_id][5] = [i for i in range(0, len_category, 4)]
                users_id_info[event.object.user_id][6] = [i for i in range(4, len_category, 4)] + [len_category]
                users_id_info[event.object.user_id][7] = 0
                users_id_info[event.object.user_id][8] = categories
                users_id_info[event.object.user_id][9] = "category"
                users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Заказ успешно отменен',
                    conversation_message_id=event.obj.conversation_message_id)
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                    message="Выберите доступную категорию товаров:")

            elif event.object.payload.get("order") == "accept":
                users_id_info[event.object.user_id][20] = get_user_data(event.object.user_id)[-1]

                if users_id_info[event.object.user_id][20] == "NONE" or event.object.payload.get("address") == "new":
                    users_id_info[event.object.user_id][21] = "add address"
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Введите адрес доставки:',
                        conversation_message_id=event.obj.conversation_message_id)
                elif event.object.payload.get("address") == "old":
                    users_id_info[event.object.user_id][10] = VkKeyboard(**settings_keyboard_inline)
                    users_id_info[event.object.user_id][10].add_callback_button(label="Добавить",
                                                                                color=VkKeyboardColor.POSITIVE,
                                                                                payload={"commentary": "add"})
                    users_id_info[event.object.user_id][10].add_callback_button(label='Продолжить без комментария',
                                                                                color=VkKeyboardColor.POSITIVE,
                                                                                payload={"commentary": "skip"})
                    vk.messages.send(
                        user_id=event.object.user_id,
                        random_id=get_random_id(),
                        peer_id=event.object.peer_id,
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                        message="Хотите оставить комментарий ?")

                elif users_id_info[event.object.user_id][20] != "NONE":
                    users_id_info[event.object.user_id][10] = VkKeyboard(**settings_keyboard_inline)
                    users_id_info[event.object.user_id][10].add_callback_button(label="Добавить новый",
                                                                                color=VkKeyboardColor.POSITIVE,
                                                                                payload={"order": "accept",
                                                                                         "address": "new"})
                    users_id_info[event.object.user_id][10].add_callback_button(label="Оставить прежний",
                                                                                color=VkKeyboardColor.POSITIVE,
                                                                                payload={"order": "accept",
                                                                                         "address": "old"})
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Доставить на последний добавленный адрес ?',
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id)

            '''Изменение количества товара'''
            if event.object.payload.get("type") == "cart":
                pass



            '''Добавление комментария к заказу'''
            if event.object.payload.get("commentary") == "add":
                users_id_info[event.object.user_id][23] = "add"

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Введите комментарий к заказу:',
                    conversation_message_id=event.obj.conversation_message_id)
            elif event.object.payload.get("commentary") == "skip":
                users_id_info[event.object.user_id][10] = VkKeyboard(**settings_keyboard_inline)
                users_id_info[event.object.user_id][10].add_button(label='Меню категорий',
                                                                           color=VkKeyboardColor.POSITIVE)
                users_id_info[event.object.user_id][10].add_callback_button(label='Заказы',
                                                                            color=VkKeyboardColor.POSITIVE,
                                                                            payload={"type": "orders"})
                users_id_info[event.object.user_id][24] = get_user_data(event.object.user_id)
                from_cart_into_db([users_id_info[event.object.user_id][24][i] for i in [0, 2, 6]],
                                  get_total_price([event.object.user_id][11]),
                                  users_id_info[event.object.user_id][11],
                                  30,
                                  users_id_info[event.object.user_id][22])

                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                    message="Заказ успешно сформирован.")

            '''Переход в корзину'''
            if event.object.payload.get("type") == "basket":

                if not users_id_info[event.object.user_id][11]:
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Ваша корзина пустая, выберите что нибудь.',
                        conversation_message_id=event.obj.conversation_message_id)
                    len_category = len(categories)
                    users_id_info[event.object.user_id][5] = [i for i in range(0, len_category, 4)]
                    users_id_info[event.object.user_id][6] = [i for i in range(4, len_category, 4)] + [len_category]
                    users_id_info[event.object.user_id][7] = 0
                    users_id_info[event.object.user_id][8] = categories
                    users_id_info[event.object.user_id][9] = "category"
                    users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)
                    vk.messages.send(
                        user_id=event.object.user_id,
                        random_id=get_random_id(),
                        peer_id=event.object.peer_id,
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                        message="Выберите доступную категорию товаров:")
                else:
                    users_id_info[event.object.user_id][13] = len(users_id_info[event.object.user_id][11])
                    users_id_info[event.object.user_id][5] = [i for i in range(0, users_id_info[event.object.user_id][13], 4)]
                    users_id_info[event.object.user_id][6] = [i for i in range(4, users_id_info[event.object.user_id][13], 4)] + \
                                                             [users_id_info[event.object.user_id][13]]
                    users_id_info[event.object.user_id][7] = 0
                    users_id_info[event.object.user_id][8] = users_id_info[event.object.user_id][11]
                    users_id_info[event.object.user_id][9] = "cart"
                    users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Корзина заказа:',
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id)

            '''Просмотр сформированных заказов'''
            if event.object.payload.get("type") == "orders":
                users_id_info[event.object.user_id][14] = show_order_info(event.object.user_id)

                if users_id_info[event.object.user_id][14] == 'Заказы не найдены':
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Нет сформированных заказов.',
                        conversation_message_id=event.obj.conversation_message_id)
                    len_category = len(categories)
                    users_id_info[event.object.user_id][5] = [i for i in range(0, len_category, 4)]
                    users_id_info[event.object.user_id][6] = [i for i in range(4, len_category, 4)] + [len_category]
                    users_id_info[event.object.user_id][7] = 0
                    users_id_info[event.object.user_id][8] = categories
                    users_id_info[event.object.user_id][9] = "category"
                    users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)

                    vk.messages.send(
                        user_id=event.object.user_id,
                        random_id=get_random_id(),
                        peer_id=event.object.peer_id,
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                        message="Выберите доступную категорию товаров:")
                else:
                    users_id_info[event.object.user_id][10] = VkKeyboard(**settings_keyboard_inline)
                    users_id_info[event.object.user_id][10].add_button(label='Меню категорий',
                                                                       color=VkKeyboardColor.POSITIVE)
                    users_id_info[event.object.user_id][10].add_callback_button(label='Отменить',
                                                                                color=VkKeyboardColor.NEGATIVE,
                                                                                payload={"order": "cancel"})
                    for info in users_id_info[event.object.user_id][14]:
                        users_id_info[event.object.user_id][15] += "Номер заказа: " + str(info[0]) + "\n"
                        users_id_info[event.object.user_id][15] += "Статус: " + str(info[1]) + "\n"
                        users_id_info[event.object.user_id][15] += "Время готовности: " + str(info[2]) + "\n"
                        users_id_info[event.object.user_id][15] += "---\n"
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message=users_id_info[event.object.user_id][15],
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id)

            '''Переход между страницами категорий/товаров'''
            if event.object.payload.get('type') == "next":
                if users_id_info[event.object.user_id][9] == "category":
                    users_id_info[event.object.user_id][7] += 1
                    users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную категорию товаров:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard())
                elif users_id_info[event.object.user_id][9] == "goods":
                    users_id_info[event.object.user_id][7] += 1
                    users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную товары:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard())

            elif event.object.payload.get('type') == "previous":
                if users_id_info[event.object.user_id][9] == "category":
                    users_id_info[event.object.user_id][7] -= 1
                    users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную категорию товаров:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard())
                elif users_id_info[event.object.user_id][9] == "goods":
                    users_id_info[event.object.user_id][7] -= 1
                    users_id_info[event.object.user_id][10] = keyboard_spawn(event.object.user_id)
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную товары:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=users_id_info[event.object.user_id][10].get_keyboard())
