from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
from DB_project import *

GROUP_ID = '223946162'
GROUP_TOKEN = 'vk1.a.zhRXKGyzrpgcWWQ5aSSFSdckc_EuQLXdT2PLoiX_5ZvTVu1HYMdcaezUMqjQVNKMQmffElYVvu39gBLIFVWYabtm3lQP_Fv8HO5yELeBKK09PXuldnTY2SzcM3dFGtBlpiJijl_xfT-gc8Y7lk1QXHIGDJv2fde9vGqN3x6-9S_plpAa9NWfKaXJKk5mJq4MOwRA_SQSPUQBCzit13VRlg'
API_VERSION = '5.120'
#asvsdvs
# Запуск бота
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

settings_keyboard_not_inline = dict(one_time=False, inline=False)
settings_keyboard_inline = dict(one_time=False, inline=True)

# users_id_info = []
# user_first = True
step = 0

start_bot_msg = ("start", "старт", "начать", "начало", "бот")
CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app", "text")

# # Основное меню (3 поля)
# keyboard_main_menu = VkKeyboard(**settings_keyboard_not_inline)
#
# keyboard_main_menu.add_callback_button(label='Таблица со всеми промокодами!', color=VkKeyboardColor.POSITIVE,
#                                        payload={"type": "open_link",
#                                                 "link": "https://docs.google.com/spreadsheets/d/1FhYGE5IODqbtXSfQGBs0BGUaUJYAWBGAC2SRWqYzf6M"})
# keyboard_main_menu.add_line()
# keyboard_main_menu.add_button(label='Запустить бота!', color=VkKeyboardColor.NEGATIVE,
#                               payload={"type": "text"})


text_instruction = """
1. Для начала работы нажмите : "запустить бота"
2. Выберите нужную Вам  категорию, если не нашли на первой странице, нажмите : "далее"
Затем введите номер нужной услуги и отправьте сообщением боту. 
3. Также вы всегда можете найти актуальный перечень всех акций и предложений нажав кнопку : "таблица со всеми промокодами"
4. Чтобы всегда оставаться на связи, подпишитесь на нас в телеграмм канале, нажав кнопку : "Мы в Телеграме"
"""

print("Ready")

for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:

        if event.obj.message["text"] != '':
            if event.from_user:
                # print(event.obj)
                # print(event.obj.message["from_id"])

                if event.obj.message["text"].lower() in start_bot_msg:
                    
                    if is_new(event.obj.message["from_id"]):
                        step = 1
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            # keyboard=keyboard_main_menu.get_keyboard(),
                            message="Привет, ты у нас впервые, давай пройдем регистрацию\nВведите ваше ФИО:")
                elif step == 1:
                    users_id_info = [event.obj.message["from_id"], event.obj.message["text"]]
                    step = 2
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        message="Введите номер телефона (с кодом +375 или 80):")
                elif step == 2:
                    tel = event.obj.message["text"].strip()
                    scheme = "('{0}'[:4] == '+375' and '{0}'[1:].isdigit() and len('{0}') == 13) or" \
                             "('{0}'[:2] == '80' and '{0}'[1:].isdigit() and len('{0}') == 11)"

                    if eval(scheme.format(tel)):
                        users_id_info.append(event.obj.message["text"])
                        step = 3
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
                elif step == 3:
                    users_id_info.append(event.obj.message["text"])

                    keyboard_accept_decline = VkKeyboard(**settings_keyboard_inline)
                    keyboard_accept_decline.add_callback_button(label='Подтвердить', color=VkKeyboardColor.POSITIVE,
                                                                payload={"reg_user": "yes"})
                    keyboard_accept_decline.add_callback_button(label='Заполнить заново', color=VkKeyboardColor.NEGATIVE,
                                                                payload={"reg_user": "no"})

                    user_info = f"Подтвердите введенные вами данные:\nИмя: {users_id_info[1]}\nТелефон: " \
                                f"{users_id_info[2]}\nДата рождения: {users_id_info[3]}"
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=keyboard_accept_decline.get_keyboard(),
                        message=f"{user_info}")

    elif event.type == VkBotEventType.MESSAGE_EVENT:
        print(event.object)
        if event.object.payload.get('type') in CALLBACK_TYPES:
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
        else:
            '''Подтверждение или перезапись введенных пользователем данных'''
            if event.object.payload.get("reg_user") == "yes":
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message=registrator(users_id_info),
                    conversation_message_id=event.obj.conversation_message_id)

                # vk.messages.send(
                #     user_id=event.object.user_id,
                #     random_id=get_random_id(),
                #     peer_id=event.object.peer_id,
                #     message=registrator(users_id_info))
            elif event.object.payload.get("reg_user") == "no":
                step = 1
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Введите ваше ФИО:',
                    conversation_message_id=event.obj.conversation_message_id)

                # vk.messages.send(
                #     user_id=event.object.user_id,
                #     random_id=get_random_id(),
                #     peer_id=event.object.peer_id,
                #     message="Введите ваше ФИО:")







# def create_keyboard(begin, finish, index, name, text_for_buttons):
#     keyboard = VkKeyboard(**settings_keyboard__inline)
#
#     if len(begin) == 1:
#         for num in range(begin[index], finish[index]):
#             keyboard.add_button(label=f"{name[num]}", color=VkKeyboardColor.SECONDARY,
#                                 payload={"type": f"{text_for_buttons}"})
#             keyboard.add_line()
#         keyboard.add_button(label='Меню!', color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
#
#     else:
#         for num in range(begin[index], finish[index]):
#             keyboard.add_button(label=f"{name[num]}", color=VkKeyboardColor.SECONDARY,
#                                 payload={"type": f"{text_for_buttons}"})
#             keyboard.add_line()
#
#         if begin[index] == 0:
#             keyboard.add_callback_button(label='Далее', color=VkKeyboardColor.PRIMARY, payload={"type": "next"})
#         elif begin[index] + 5 < len(name):
#             keyboard.add_callback_button(label='Назад', color=VkKeyboardColor.PRIMARY, payload={"type": "previous"})
#             keyboard.add_callback_button(label='Далее', color=VkKeyboardColor.PRIMARY, payload={"type": "next"})
#         else:
#             keyboard.add_callback_button(label='Назад', color=VkKeyboardColor.PRIMARY, payload={"type": "previous"})
#
#     return keyboard


# for event in longpoll.listen():
#
#     if event.type == VkBotEventType.MESSAGE_NEW:
#
#         if event.obj.message["text"] != '':
#
#             if event.from_user:
#
#                 if event.obj.message["text"] in ('Запустить бота!', "Меню!"):
#
#                     if event.obj.message['from_id'] not in users_id_info:
#                         # 1 начало, 2 конец, 3 индекс, 4 список наименований (категорий или компаний категории),
#                         # 5 ключ категории
#                         users_id_info[event.obj.message['from_id']] = ["", "", "", "", ""]
#
#                     len_categories = len(categories)
#                     users_id_info[event.obj.message['from_id']][0] = [i for i in range(0, len_categories, 5)]
#                     users_id_info[event.obj.message['from_id']][1] = [i for i in range(5, len_categories, 5)] + [len_categories]
#                     users_id_info[event.obj.message['from_id']][2] = 0
#                     users_id_info[event.obj.message['from_id']][3] = categories
#                     users_id_info[event.obj.message['from_id']][4] = "category"
#                     keyboard_categories = create_keyboard(users_id_info[event.obj.message['from_id']][0],
#                                                           users_id_info[event.obj.message['from_id']][1],
#                                                           users_id_info[event.obj.message['from_id']][2],
#                                                           users_id_info[event.obj.message['from_id']][3],
#                                                           users_id_info[event.obj.message['from_id']][4])
#                     vk.messages.send(
#                         user_id=event.obj.message['from_id'],
#                         random_id=get_random_id(),
#                         peer_id=event.obj.message['from_id'],
#                         keyboard=keyboard_categories.get_keyboard(),
#                         message='Выбирай категорию:')
#
#                 elif event.obj.message["text"] == 'Инструкция!':
#                     vk.messages.send(
#                         user_id=event.obj.message['from_id'],
#                         random_id=get_random_id(),
#                         peer_id=event.obj.message['from_id'],
#                         keyboard=keyboard_main_menu.get_keyboard(),
#                         message=text_instruction)
#
#                 elif event.obj.message["text"] == '/stat1':
#                     vk.messages.send(
#                         user_id=event.obj.message['from_id'],
#                         random_id=get_random_id(),
#                         peer_id=event.obj.message['from_id'],
#                         message="Количество вызовов функций = "             )
#
#                 elif event.obj.message["text"] == '/stat2':
#                     vk.messages.send(
#                         user_id=event.obj.message['from_id'],
#                         random_id=get_random_id(),
#                         peer_id=event.obj.message['from_id'],
#                         message="Людей активно использующих бота = "        )
#
#                 elif event.obj.message["text"] == '/stat3':
#                     vk.messages.send(
#                         user_id=event.obj.message['from_id'],
#                         random_id=get_random_id(),
#                         peer_id=event.obj.message['from_id'],
#                         message="Детальная статистика: " + "\n"             )
#
#                 elif event.obj.message["text"].lower() in start_bot_msg:
#                     vk.messages.send(
#                         user_id=event.obj.message['from_id'],
#                         random_id=get_random_id(),
#                         peer_id=event.obj.message['from_id'],
#                         keyboard=keyboard_main_menu.get_keyboard(),
#                         message="Привет, {from_user_name} ты у нас впервые, давай пройдем регистрацию")
#
#                 elif event.obj.message["text"] in categories:
#                     # Вызов клавиатуры с категориями
#
#                     len_companies = len(category_companies[event.obj.message["text"]])
#                     users_id_info[event.obj.message['from_id']][0] = [i for i in range(0, len_companies, 5)]
#                     users_id_info[event.obj.message['from_id']][1] = [i for i in range(5, len_companies, 5)] + [len_companies]
#                     users_id_info[event.obj.message['from_id']][2] = 0
#                     users_id_info[event.obj.message['from_id']][3] = category_companies[event.obj.message["text"]]
#                     users_id_info[event.obj.message['from_id']][4] = "company"
#                     keyboard_companies = create_keyboard(users_id_info[event.obj.message['from_id']][0],
#                                                          users_id_info[event.obj.message['from_id']][1],
#                                                          users_id_info[event.obj.message['from_id']][2],
#                                                          users_id_info[event.obj.message['from_id']][3],
#                                                          users_id_info[event.obj.message['from_id']][4])
#                     users_id_info[event.obj.message['from_id']][4] = event.obj.message["text"]
#                     print(event.obj.message["text"])
#
#                     vk.messages.send(
#                         user_id=event.obj.message['from_id'],
#                         random_id=get_random_id(),
#                         peer_id=event.obj.message['from_id'],
#                         keyboard=keyboard_companies.get_keyboard(),
#                         message=event.obj.message["text"])
#
#                 elif event.obj.message["text"] in companies:
#                     # Вызов клавиатуры с компаниями
#
#                     def send_info(text):
#                         vk.messages.send(
#                             user_id=event.obj.message['from_id'],
#                             random_id=get_random_id(),
#                             peer_id=event.obj.message['from_id'],
#                             message=text)
#
#
#                     info_company = companies_text[event.obj.message["text"]]
#                     for info_line in info_company:
#                         text = ""
#                         text += "Название: " + info_line[0]
#                         text += "\nСкидка: " + info_line[3]
#                         text += "\nСсылка:\n" + info_line[4]
#                         text += "\nДействует до: " + info_line[5]
#                         text += "\nРегион: " + info_line[6]
#                         text += "\nУсловия акции: " + info_line[7]
#                         text += "\nПромокод ниже ⬇"
#                         send_info(text)
#                         send_info(info_line[2])
#                     send_info("Нажмите Запустить бота, для вызова главного меню")
#
#     elif event.type == VkBotEventType.MESSAGE_EVENT:
#         if event.object.payload.get('type') in CALLBACK_TYPES:
#             vk.messages.sendMessageEventAnswer(
#                 event_id=event.object.event_id,
#                 user_id=event.object.user_id,
#                 peer_id=event.object.peer_id,
#                 event_data=json.dumps(event.object.payload))
#         else:
#             flag = True
#             if event.object.payload.get('type') == "next":
#                 users_id_info[event.obj.user_id][2] += 1
#             elif event.object.payload.get('type') == "previous":
#                 users_id_info[event.obj.user_id][2] -= 1
#
#             if users_id_info[event.obj.user_id][4] == "category":
#                 keyboard = create_keyboard(users_id_info[event.obj.user_id][0], users_id_info[event.obj.user_id][1],
#                                            users_id_info[event.obj.user_id][2], users_id_info[event.obj.user_id][3],
#                                            users_id_info[event.obj.user_id][4])
#                 flag = False
#
#             elif users_id_info[event.obj.user_id][4] == "company":
#                 keyboard = create_keyboard(users_id_info[event.obj.user_id][0], users_id_info[event.obj.user_id][1],
#                                            users_id_info[event.obj.user_id][2], category_companies[users_id_info[event.obj.user_id][4]],
#                                            users_id_info[event.obj.user_id][4])
#                 flag = False
#
#             if flag:
#                 keyboard = create_keyboard(users_id_info[event.obj.user_id][0],
#                                            users_id_info[event.obj.user_id][1],
#                                            users_id_info[event.obj.user_id][2],
#                                            users_id_info[event.obj.user_id][3],
#                                            users_id_info[event.obj.user_id][4])
#             last_id = vk.messages.edit(
#                 peer_id=event.obj.peer_id,
#                 message='Выбирай категорию:',
#                 conversation_message_id=event.obj.conversation_message_id,
#                 keyboard=keyboard.get_keyboard())
