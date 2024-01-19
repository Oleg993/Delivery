from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
from db_class import DataBase

GROUP_ID = '223946162'
GROUP_TOKEN = 'vk1.a.zhRXKGyzrpgcWWQ5aSSFSdckc_EuQLXdT2PLoiX_5ZvTVu1HYMdcaezUMqjQVNKMQmffElYVvu39gBLIFVWYabtm3lQP_Fv8' \
              'HO5yELeBKK09PXuldnTY2SzcM3dFGtBlpiJijl_xfT-gc8Y7lk1QXHIGDJv2fde9vGqN3x6-9S_plpAa9NWfKaXJKk5mJq4MOwRA_S' \
              'QSPUQBCzit13VRlg'
API_VERSION = '5.120'

# Запуск бота
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

settings_keyboard_not_inline = dict(one_time=False, inline=False)
settings_keyboard_inline = dict(one_time=False, inline=True)

start_bot_msg = ("start", "старт", "начать", "начало", "бот", "меню категорий", "н")
CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app", "text")

users_id_info = dict()
category_goods = dict()
categories = DataBase().get_categories()
goods = []
basket = dict()

for category in categories:
    goods_sql = DataBase().get_from_category(category)
    category_goods[category] = goods_sql
    for pr in goods_sql:
        goods.append(pr[0])
len_category = len(categories)


def create_new_keyboard(info_for_keyboard):
    begin, finish, index, name, text_for_buttons = info_for_keyboard
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
        keyboard.add_callback_button(label='Подтвердить заказ', color=VkKeyboardColor.POSITIVE,
                                     payload={"order": "accept"})
        keyboard.add_line()
        keyboard.add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE, payload={"type": "basket"})
        keyboard.add_callback_button(label='Отменить', color=VkKeyboardColor.NEGATIVE, payload={"order": "cancel"})
    return keyboard


def keyboard_good_info(id):
    keyboard = VkKeyboard(**settings_keyboard_inline)
    if users_id_info[id][3][1] > 1:
        keyboard.add_callback_button(label='-1', color=VkKeyboardColor.NEGATIVE,
                                     payload={"count": "-1", "count_good": "change"})
    keyboard.add_callback_button(label=f"Количество - {users_id_info[id][3][1]}",
                                 color=VkKeyboardColor.PRIMARY, payload={"count": "0"})
    keyboard.add_callback_button(label='+1', color=VkKeyboardColor.POSITIVE,
                                 payload={"count": "+1", "count_good": "change"})
    keyboard.add_line()
    keyboard.add_callback_button(label='Добавить', color=VkKeyboardColor.POSITIVE, payload={"type": "add"})
    keyboard.add_callback_button(label='Корзина', color=VkKeyboardColor.NEGATIVE, payload={"type": "basket"})
    keyboard.add_line()
    keyboard.add_callback_button(label='< Блюда', color=VkKeyboardColor.POSITIVE, payload={"type": "dishes left"})
    keyboard.add_callback_button(label='Блюда >', color=VkKeyboardColor.POSITIVE, payload={"type": "dishes right"})
    keyboard.add_line()
    keyboard.add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE)
    keyboard.add_callback_button(label='Комментарии', color=VkKeyboardColor.POSITIVE, payload={"type": "commentary"})
    return keyboard


def keyboard_commentary():
    keyboard = VkKeyboard(**settings_keyboard_inline)
    keyboard.add_callback_button(label="Добавить", color=VkKeyboardColor.POSITIVE,
                                 payload={"commentary": "add commentary"})
    keyboard.add_callback_button(label='Продолжить без комментария', color=VkKeyboardColor.POSITIVE,
                                 payload={"commentary": "skip"})
    return keyboard


def keyboard_order_ordered():
    keyboard = VkKeyboard(**settings_keyboard_inline)
    keyboard.add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE)
    keyboard.add_callback_button(label='Заказы', color=VkKeyboardColor.POSITIVE, payload={"type": "orders"})
    return keyboard


print("Ready")
for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:

        if event.obj.message["text"] != '':
            if event.from_user:
                if event.obj.message['from_id'] not in users_id_info:
                    '''0 - шаг регистрации + информация для регистрации: [шаг регистрации, id пользователя, имя, 
                                                                          номер телефона, дата рождения]
                       1- данные для клавиатуры категорий и товаров, 2- корзина, 3- добавляемый товар и количество,
                       4- карточка товара, 5- индикатор добавления адреса/комментария
                    '''
                    users_id_info[event.obj.message['from_id']] = [[0, event.obj.message['from_id']], "data kw", [],
                                                                   ["", 1], "info", "key", "6"]

                '''Проверка на первый вход в бота с регистрацией'''
                if DataBase().is_new(event.obj.message["from_id"]):
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

                    # '''Отправка сообщения с подтверждением или перезаписью введенных данных'''
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
                            message=user_info)

                # '''Вывод первичного меню категорий товаров'''
                elif not DataBase().is_new(event.obj.message["from_id"]):
                    if event.obj.message["text"].lower() in start_bot_msg:
                        users_id_info[event.obj.message['from_id']][2] = []  # создание пустой корзины
                        users_id_info[event.obj.message['from_id']][1] = [[i for i in range(0, len_category, 4)],
                                                                          [i for i in range(4, len_category, 4)] +
                                                                          [len_category], 0, categories, "category"]
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=create_new_keyboard(users_id_info[event.obj.message['from_id']][1]).get_keyboard(),
                            message="Выберите доступную категорию товаров:")

                if event.obj.message["text"] in categories:
                    len_goods = len(category_goods[event.obj.message["text"]])
                    users_id_info[event.obj.message['from_id']][1] = [[i for i in range(0, len_goods, 4)],
                                                                      [i for i in range(4, len_goods, 4)] + [len_goods],
                                                                      0, [name[0] for name in
                                                                          category_goods[event.obj.message["text"]]],
                                                                      "goods"]
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=create_new_keyboard(users_id_info[event.obj.message['from_id']][1]).get_keyboard(),
                        message="Выберите доступную товары:")

                elif event.obj.message["text"] in goods:
                    params = ["Название: ", "Описание: ", "Граммовка: ", "Цена: ", "Рейтинг: "]
                    good_card_info = DataBase().show_product_card(event.obj.message["text"])
                    users_id_info[event.obj.message['from_id']][3] = [good_card_info[2], 1]
                    users_id_info[event.obj.message['from_id']][4] = params[0] + good_card_info[2] + "\n" + \
                                                                     params[1] + good_card_info[3] + "\n" + \
                                                                     params[2] + str(good_card_info[7]) + "\n" + \
                                                                     params[3] + str(good_card_info[4]) + "\n" + \
                                                                     params[4] + str(good_card_info[6])
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=keyboard_good_info(event.obj.message['from_id']).get_keyboard(),
                        message=users_id_info[event.obj.message['from_id']][4])

                '''Добавление нового адреса пользователя'''
                if users_id_info[event.obj.message['from_id']][5] == "add address":
                    users_id_info[event.obj.message['from_id']][5] = " "
                    DataBase().correct_delivery_address(event.obj.message["text"], event.obj.message['from_id'])

                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=keyboard_commentary().get_keyboard(),
                        message="Хотите оставить комментарий ?")

                # '''Добавление комментария к заказу'''
                elif users_id_info[event.obj.message['from_id']][5] == "add commentary":
                    users_id_info[event.obj.message['from_id']][5] = " "
                    user_data = DataBase().get_user_data(event.obj.message['from_id'])

                    DataBase().from_cart_into_db([user_data[i] for i in [0, 2, 6]],
                                                 DataBase().get_total_price(
                                                     users_id_info[event.obj.message['from_id']][2]),
                                                 users_id_info[event.obj.message['from_id']][2],
                                                 30, event.obj.message["text"])
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=keyboard_order_ordered().get_keyboard(),
                        message="Заказ успешно сформирован.")

    elif event.type == VkBotEventType.MESSAGE_EVENT:
        if event.object.payload.get('type') in CALLBACK_TYPES:
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
        else:
            '''Подтверждение или перезапись введенных пользователем данных регистрации'''
            if event.object.payload.get("reg_user") == "yes":
                DataBase().registrator(users_id_info[event.object.user_id][0][1:])

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message="Регистрация прошла успешно.",
                    conversation_message_id=event.obj.conversation_message_id)

                '''Вывод сообщения с категориями доступных товаров'''
                users_id_info[event.object.user_id][1] = [[i for i in range(0, len_category, 4)],
                                                          [i for i in range(4, len_category, 4)] + [len_category],
                                                          0, categories, "category"]
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard(),
                    message="Выберите доступную категорию товаров:")
            elif event.object.payload.get("reg_user") == "no":
                users_id_info[event.object.user_id][0] = [1, event.object.user_id]

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Введите ваше ФИО:',
                    conversation_message_id=event.obj.conversation_message_id)

            '''Переход между страницами категорий/товаров'''
            if event.object.payload.get('type') == "next":
                if users_id_info[event.object.user_id][1][4] == "category":
                    users_id_info[event.object.user_id][1][2] += 1

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную категорию товаров:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard())
                elif users_id_info[event.object.user_id][1][4] == "goods":
                    users_id_info[event.object.user_id][1][2] += 1

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную товары:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard())

            elif event.object.payload.get('type') == "previous":
                if users_id_info[event.object.user_id][1][4] == "category":
                    users_id_info[event.object.user_id][1][2] -= 1

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную категорию товаров:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard())
                elif users_id_info[event.object.user_id][1][4] == "goods":
                    users_id_info[event.object.user_id][1][2] -= 1

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Выберите доступную товары:',
                        conversation_message_id=event.obj.conversation_message_id,
                        keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard())

            '''Изменение количества выбранного товара для добавления в корзину'''
            if event.object.payload.get('count_good') == "change":
                users_id_info[event.object.user_id][3][1] += int(event.object.payload.get('count'))

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message=users_id_info[event.object.user_id][4],
                    keyboard=keyboard_good_info(event.object.user_id).get_keyboard(),
                    conversation_message_id=event.obj.conversation_message_id)

            '''Добавление товара во временную корзину'''
            if event.object.payload.get('type') == "add":
                users_id_info[event.object.user_id][2].append(users_id_info[event.object.user_id][3])
                users_id_info[event.object.user_id][3] = ["", 1]

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Товар успешно добавлен.',
                    conversation_message_id=event.obj.conversation_message_id)
                users_id_info[event.object.user_id][1] = [[i for i in range(0, len_category, 4)],
                                                          [i for i in range(4, len_category, 4)] + [len_category],
                                                          0, categories, "category"]
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard(),
                    message="Выберите доступную категорию товаров:")

            '''Отмена текущего заказа / подтверждение'''
            if event.object.payload.get("order") == "cancel":
                users_id_info[event.object.user_id][2] = []
                users_id_info[event.object.user_id][1] = [[i for i in range(0, len_category, 4)],
                                                          [i for i in range(4, len_category, 4)] + [len_category],
                                                          0, categories, "category"]
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Заказ успешно отменен',
                    conversation_message_id=event.obj.conversation_message_id)
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard(),
                    message="Выберите доступную категорию товаров:")

            elif event.object.payload.get("order") == "accept":
                users_id_info[event.object.user_id][5] = DataBase().get_user_data(event.object.user_id)[-1]

                if users_id_info[event.object.user_id][5] == "NONE" or event.object.payload.get("address") == "new":
                    users_id_info[event.object.user_id][5] = "add address"

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Введите адрес доставки:',
                        conversation_message_id=event.obj.conversation_message_id)
                elif event.object.payload.get("address") == "old":
                    vk.messages.send(
                        user_id=event.object.user_id,
                        random_id=get_random_id(),
                        peer_id=event.object.peer_id,
                        keyboard=keyboard_commentary().get_keyboard(),
                        message="Хотите оставить комментарий ?")

                elif users_id_info[event.object.user_id][5] != "NONE":
                    keyboard_address = VkKeyboard(**settings_keyboard_inline)
                    keyboard_address.add_callback_button(label="Добавить новый", color=VkKeyboardColor.POSITIVE,
                                                         payload={"order": "accept", "address": "new"})
                    keyboard_address.add_callback_button(label="Оставить прежний", color=VkKeyboardColor.POSITIVE,
                                                         payload={"order": "accept", "address": "old"})
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Доставить на последний добавленный адрес ?',
                        keyboard=keyboard_address.get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id)

            '''Переход в корзину'''
            if event.object.payload.get("type") == "basket":
                if not users_id_info[event.object.user_id][2]:
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Ваша корзина пустая, выберите что нибудь.',
                        conversation_message_id=event.obj.conversation_message_id)
                    users_id_info[event.object.user_id][1] = [[i for i in range(0, len_category, 4)],
                                                              [i for i in range(4, len_category, 4)] + [len_category],
                                                              0, categories, "category"]
                    vk.messages.send(
                        user_id=event.object.user_id,
                        random_id=get_random_id(),
                        peer_id=event.object.peer_id,
                        keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard(),
                        message="Выберите доступную категорию товаров:")
                else:
                    len_basket = len(users_id_info[event.object.user_id][2])
                    users_id_info[event.object.user_id][1] = [[i for i in range(0, len_basket, 4)],
                                                              [i for i in range(4, len_basket, 4)] + [len_basket],
                                                              0, users_id_info[event.object.user_id][2], "cart"]
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Корзина заказа:',
                        keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id)

            '''Изменение количества товара              изменение количества выбранного товара в магазине'''
            if event.object.payload.get("type") == "cart":
                pass

            '''Добавление комментария к заказу'''
            if event.object.payload.get("commentary") == "add commentary":
                users_id_info[event.object.user_id][5] = "add commentary"

                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Введите комментарий к заказу:',
                    conversation_message_id=event.obj.conversation_message_id)

            elif event.object.payload.get("commentary") == "skip":
                user_data = DataBase().get_user_data(event.object.user_id)
                DataBase().from_cart_into_db([user_data[i] for i in [0, 2, 6]],
                                             DataBase().get_total_price([event.object.user_id][2]),
                                             users_id_info[event.object.user_id][2], 30, " ")
                vk.messages.send(
                    user_id=event.object.user_id,
                    random_id=get_random_id(),
                    peer_id=event.object.peer_id,
                    keyboard=keyboard_order_ordered().get_keyboard(),
                    message="Заказ успешно сформирован.")

            '''Просмотр сформированных заказов'''
            if event.object.payload.get("type") == "orders":
                orders_information = DataBase().show_order_info(event.object.user_id)

                if orders_information == 'Заказы не найдены':
                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message='Нет сформированных заказов.',
                        conversation_message_id=event.obj.conversation_message_id)
                    users_id_info[event.object.user_id][1] = [[i for i in range(0, len_category, 4)],
                                                              [i for i in range(4, len_category, 4)] + [len_category],
                                                              0, categories, "category"]
                    vk.messages.send(
                        user_id=event.object.user_id,
                        random_id=get_random_id(),
                        peer_id=event.object.peer_id,
                        keyboard=create_new_keyboard(users_id_info[event.object.user_id][1]).get_keyboard(),
                        message="Выберите доступную категорию товаров:")
                else:
                    keyboard_order = VkKeyboard(**settings_keyboard_inline)
                    keyboard_order.add_button(label='Меню категорий', color=VkKeyboardColor.POSITIVE)
                    keyboard_order.add_callback_button(label='Отменить', color=VkKeyboardColor.NEGATIVE,
                                                       payload={"order": "cancel"})
                    all_orders_info = ""
                    for info in orders_information:
                        all_orders_info += "Номер заказа: " + str(info[0]) + "\n" + "Статус: " + str(info[1]) + "\n"
                        all_orders_info += "Время готовности: " + str(info[2]) + "\n" + "---\n"

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        message=all_orders_info,
                        keyboard=keyboard_order.get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id)
