import config
import telebot
import psycopg2

bot = telebot.TeleBot(config.token)

bdconnect = psycopg2.connect(
    dbname="LighthouseBotDB",
    user="Accvad",
    password="wololo",
    host="127.0.0.1",
    port="5432"
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Howdy! Добро пожаловать в Альфа-версию Lighthouse! На данный момент реализована только регистрация, но разработка уже перешла в каждодневную. Для продолжения напишите /register")

@bot.message_handler(commands=['register'])
def user_register(message):
    cur = bdconnect.cursor()
    cur.execute('SELECT id_user FROM users;')        # Вытаскиваем ID для проверки регистрации
    ids = cur.fetchall()
    id_flag = bool()
    for id in ids:
        if id[0] == int(message.chat.id):            # Проверка регистрации
            chosenId = id[0]
            id_flag = True
            break
        else:
            id_flag = False
    if id_flag == True:                              # Если зарегистрирован
        bot.send_message(message.chat.id,
                         'Вы уже зарегистрированы в Lighthouse! =)\nВаш ID: {0}'.format(chosenId))
    else:                                            # Если не зарегестрирован
        cur.execute('INSERT INTO users (id_user) VALUES ({0});'.format(message.chat.id))
        bdconnect.commit()
        bot.send_message(message.chat.id,
                         'Вы были успешно зарегистрированы!\n\nДля проверки регистрации введите еще раз /register\nДа, пока что это вся альфа :D')

@bot.message_handler(func=lambda message: True)
def repeat_all_messages(message):
    bot.reply_to(message, 'Не спамь ;)')

if __name__ == '__main__':
    bot.polling(none_stop=True)