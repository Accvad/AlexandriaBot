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
        if id[0] == int(message.chat.id):            # Проверка регистрации
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
        searchButton = types.InlineKeyboardButton(text="Поиск(UС)", callback_data="search")
        finishedButton = types.InlineKeyboardButton(text="ЗаконченноеUC)", callback_data="finished")
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
        if call.data == "reg":
            if id_checker(call.message):                         # Если зарегистрирован
                bot.send_message(call.message.chat.id,
                                 'Вы уже зарегистрированы в Lighthouse! =)\nВаш ID: {0}'.format(call.message.chat.id))
            else:                                                # Если не зарегестрирован
                cur = bdconnect.cursor()
                cur.execute('INSERT INTO users (id_user) VALUES ({0});'.format(call.message.chat.id))
                bdconnect.commit()
                bot.delete_message(call.message.chat.id,call.message.message_id)
                bot.send_message(call.message.chat.id, 'Howdy! Добро пожаловать в Альфа-версию Lighthouse! \n'
                                                       'Вы были успешно зарегистрированы!\n\nДля продолжения просто напишите /menu')
        elif call.data == "profile":
            if id_checker(call.message):
                bot.send_message(call.message.chat.id, 'Профиль\n\nВаш ID: {0}'.format(call.message.chat.id))



@bot.message_handler(func=lambda message: True)
def repeat_all_messages(message):
    bot.reply_to(message, 'Не спамь ;)')

if __name__ == '__main__':
    bot.polling(none_stop=True)