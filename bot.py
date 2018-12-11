import config
import telebot
import psycopg2
from telebot import types

bot = telebot.TeleBot(config.token)

bdconnect = psycopg2.connect(
    dbname="LighthouseBotDB",
    user="Accvad",
    password="wololo",
    host="127.0.0.1",
    port="5432"
)
def id_checker(message):
    cur = bdconnect.cursor()
    cur.execute('SELECT id_user FROM users;')         # Вытаскиваем ID для проверки регистрации
    ids = cur.fetchall()
    id_flag = bool()
    for id in ids:
        if id[0] == int(message.chat.id):             # Проверка регистрации
            id_flag = True
            break
        else:
            id_flag = False
    return id_flag

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if id_checker(message):
        bot.send_message(message.chat.id, "Howdy! Добро пожаловать в Альфа-версию Lighthouse! \n"
                                          "Вы уже зарегистрированы!\n\n Для продолжения просто напишите /menu")
    else:
        button = types.InlineKeyboardMarkup()
        reg_button = types.InlineKeyboardButton(text="Нажмите на кнопку чтобы зарегистрироваться C;", callback_data="reg")
        button.add(reg_button)
        bot.send_message(message.chat.id, "Howdy! Добро пожаловать в Альфа-версию Lighthouse! \n"
                                          "Для начала нужно пройти регистрацию", reply_markup=button)


@bot.message_handler(commands=['menu'])
def send_(message):
    if id_checker(message):
        buttons = types.InlineKeyboardMarkup()
        searchButton = types.InlineKeyboardButton(text="Поиск(UС)", callback_data="search0/length0")
        finishedButton = types.InlineKeyboardButton(text="Законченное(UC)", callback_data="finished")
        wishButton = types.InlineKeyboardButton(text="Желаемое(UC)", callback_data="wish")
        subButton = types.InlineKeyboardButton(text="Подписки(UC)", callback_data="sub")
        suggestButton = types.InlineKeyboardButton(text="Предложить(UC)", callback_data="suggest")
        profileButton = types.InlineKeyboardButton(text="Профиль", callback_data="profile")
        buttons.add(searchButton, finishedButton, wishButton, subButton, suggestButton, profileButton)
        bot.send_message(message.chat.id, "Lighthouse menu (UNDER CONSTRUCTION)", reply_markup=buttons)
    else:
        button = types.InlineKeyboardMarkup()
        reg_button = types.InlineKeyboardButton(text="Нажмите на кнопку чтобы зарегистрироваться С;", callback_data="reg")
        button.add(reg_button)
        bot.send_message(message.chat.id, "Вы не можете использовать команду /menu без регистрации\n", reply_markup=button)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cur = bdconnect.cursor()

    if call.data == "reg":
        if id_checker(call.message):                         # Если зарегистрирован
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.send_message(call.message.chat.id,
                             'Вы уже зарегистрированы в Lighthouse! =)\nВаш ID: {0}'.format(call.message.chat.id))
        else:                                                # Если не зарегистрирован
            cur.execute('INSERT INTO users (id_user, name, level, exp) VALUES ({0}, \'{1}\', 1, 0);'.format(call.message.chat.id, call.message.chat.first_name))
            bdconnect.commit()
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.send_message(call.message.chat.id, 'Howdy! Добро пожаловать в Альфа-версию Lighthouse! \n'
                                                   'Вы были успешно зарегистрированы!\n\nДля продолжения просто напишите /menu')
    if id_checker(call.message): #Проверка регистрации
        if call.data == "profile":
            cur.execute('SELECT * FROM users WHERE id_user = {0};'.format(call.message.chat.id))  # Вытаскиваем людей
            user = cur.fetchall()
            bot.send_message(call.message.chat.id, 'Профиль\n\nВаш ID: {0}\nУровень: {1}\nУровень: {2}\nОпыт: {3}'.format(user[0][0], user[0][1], user[0][2], user[0][3]))
        elif "search" in call.data:
            splitCall = call.data.split("/")
            page = splitCall[0].replace("search", "")
            length = splitCall[1].replace("length", "")
            limit = 5
            last = int()
            i = limit * int(page) #Номер продукта на странице
            if i == 0:
                cur.execute('SELECT * FROM media JOIN types on types.id_type = media.id_type')  # Вытаскиваем медиа
                media = cur.fetchall()
                length = len(media)
            cur.execute('SELECT * FROM media JOIN types on types.id_type = media.id_type ORDER BY id_media LIMIT {1} OFFSET {0}'.format(i, limit))  # Вытаскиваем медиа
            media = cur.fetchall()
            for item in media:
                line = str()
                line += str(i+1)
                line += "\nРаздел:              " + item[9]
                line += "\nНазвание:        " + item[0]
                line += "\nДата выхода:  " + item[2]
                line += "\nЖанр:                 " + item[3]
                line += "\nОценка:             " + str(item[4]) + " из 5"
                line += "\n_______________________________"
                i += 1
                buttons = types.InlineKeyboardMarkup()
                selectButton = types.InlineKeyboardButton(text="Выбрать", callback_data="select{0}".format(item[5]))
                if i == (limit * int(page)) + limit and i != int(length):
                    nextButton = types.InlineKeyboardButton(text="Следующие {0}". format(limit),
                                                            callback_data="search{0}/length{1}".format(int(page)+1, length))
                    buttons.add(selectButton, nextButton)
                    bot.send_message(call.message.chat.id, line, reply_markup=buttons)
                else:
                    buttons.add(selectButton)
                    bot.send_message(call.message.chat.id, line, reply_markup=buttons)

        elif "select" in call.data:
            mediaId = call.data.replace("select", "")
            cur.execute('SELECT * FROM media JOIN types ON types.id_type = media.id_type WHERE id_media = {0}'.format(mediaId))  # Вытаскиваем медиа
            media = cur.fetchall()
            line = str()
            line += "\nРаздел:              " + media[0][9]
            line += "\nНазвание:        " + media[0][0]
            line += "\nДата выхода:  " + media[0][2]
            line += "\nЖанр:                 " + media[0][3]
            line += "\nОценка:             " + str(media[0][4]) + " из 5"
            line += "\n_______________________________"
            line += "\n" + media[0][1]
            #TODO: сделать проверку есть ли у пользователя выбранный продукт чтобы выводить соответствующие кнопки
            buttons = types.InlineKeyboardMarkup()
            addWishButton = types.InlineKeyboardButton(text="Посмотрю!(UC)", callback_data="a")
            addFinishedButton = types.InlineKeyboardButton(text="Посмотрел!(UC)", callback_data="a")
            buttons.add(addWishButton, addFinishedButton)
            bot.send_message(call.message.chat.id, line, reply_markup=buttons)
            #IDEA!!
            # call.data = "profile"
            # callback(call)

        # elif call.data == "finished":
        #     cur = bdconnect.cursor()
        #     cur.execute('SELECT * FROM finished_list WHERE')  # Вытаскиваем медиа
        #     media = cur.fetchall()
        #     i = 1
        #     for item in media:
        #         line = str()
        #         line += str(i)
        #         line += "\nРаздел:              " + item[9]
        #         line += "\nНазвание:        " + item[0]
        #         line += "\nДата выхода:  " + item[2]
        #         line += "\nЖанр:                 " + item[3]
        #         line += "\nОценка:             " + str(item[4]) + " из 5"
        #         line += "\n_______________________________\n"
        #         i += 1
        #         buttons = types.InlineKeyboardMarkup()
        #         selectButton = types.InlineKeyboardButton(text="Выбрать", callback_data="select{0}".format(item[5]))
        #         buttons.add(selectButton)
        #         bot.send_message(call.message.chat.id, line, reply_markup=buttons)
    else:
        button = types.InlineKeyboardMarkup()
        reg_button = types.InlineKeyboardButton(text="Нажмите на кнопку чтобы зарегистрироваться С;", callback_data="reg")
        button.add(reg_button)
        bot.send_message(call.message.chat.id, "Вы не зарегистрированы \n", reply_markup=button)


@bot.message_handler(func=lambda message: True)
def repeat_all_messages(message):
    bot.reply_to(message, 'Не спамь ;)')

if __name__ == '__main__':
    bot.polling(none_stop=True)