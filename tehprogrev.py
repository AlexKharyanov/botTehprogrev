import logging
import re
import telebot
from telebot import types
import sqlite3
import datetime
import time


bot = telebot.TeleBot('1456092584:AAHqNDORKWcBBFttKxhYVMuQ2_Sjnp4H11c')
CHAT = '-407748812'
id = 0
numTanka = '';
nameZakaz = '';
tempPrib ='';
dataPostup = '';
data = '';
numAvto = '';
vid = '';
vodit= '';
neobTemp = '';
dlinna = '';
tankIzmen = '';
uznat_temp = '';
imyaOform = '';
telOform = '';
infoKlienta = '';
tempPara = '';
produvRubaschki = '';
now = datetime.datetime.now()
local_time = time.localtime()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(CHAT, f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id} подписался на бота. {now.strftime("%d-%m-%Y")}')
    keyboards = telebot.types.ReplyKeyboardMarkup(True)
    keyboards.row('Получить данные по вашей заявке')
    keyboards.row('Оформить заявку на прогрев')
    keyboards.row('Узнать текущую температуру')
    keyboards.row('Отключить от прогрева', 'Телефон отделов')
    keyboards.row('Запросить PDF-файл наряд-заказа по вашей заявке')
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}', reply_markup=keyboards)
    bot.send_message(message.from_user.id, f'<b><u>ИНСТРУКЦИЯ:</u></b>\n\n<b>👉</b>\tДля того чтобы <b>оформить заявку на прогрев</b>, в меню нажмите на кнопку <b>"оформить заявку на прогрев"</b> и следуйте инструкциям бота. После успешного оформления, бот напишет вам о том, что ваша заявка успешно оформлена.\n\n<b>👉</b>\tЧтобы <b>получить данные по вашей заявке</b>, в меню нажмите кнопку <b>"получить данные по вашей заявке"</b>,  после чего бот попросит вас <b>ввести индивидуальный номер вашего танк-контейнера</b>, если данный номер присутствует в базе данных, вы получите информацию по вашей заявке.\n\n<b>👉</b>Чтобы узнать <b>текущюю температуру</b>, подать заявку на <b>отключение от прогрева</b>, а также <b>запросить pdf-файл наряд-заказа</b>, воспользуйтесь соответствующей кнопкой в меню бота, и следуйте его инструкция.', parse_mode= 'HTML')
    conn = sqlite3.connect('bd.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users ( numTanka TEXT NOT NULL, imyaOform TEXT, telOform TEXT, nameZakaz TEXT, data TEXT, tempPr TEXT, numAvto TEXT, vid TEXT, vodit TEXT, neobTemp TEXT, dlinna TEXT, timeJob TEXT, dataOform TEXT, tempPara TEXT); """)
    cur.execute("""ALTER TABLE users ADD COLUMN produvRubaschki TEXT;""")
    conn.commit()
    ##bot.send_message(message.from_user.id, 'Вcё норм');
    idTeleg = message.from_user.id
    imyaTeleg = message.from_user.first_name
    conn = sqlite3.connect('bd2.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS idusers ( id INT NOT NULL PRIMARY KEY, imya TEXT); """)
    cur.execute(f"""SELECT * FROM idusers WHERE id = '{idTeleg}' """)
    rows = cur.fetchall()
    #if len(rows) == 1:
     #   bot.send_message(message.from_user.id, f'💈снова рады видеть')
    #else:
    if len(rows) < 1:
        cur.execute("""INSERT INTO idusers(id, imya) VALUES(?, ?);""", (idTeleg, imyaTeleg))
    conn.commit()



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'получить данные по вашей заявке':
        bot.send_message(message.from_user.id, 'Введите № танк-контейнера:');
        bot.register_next_step_handler(message, get_zayavka); #следующий шаг – функция get_zayavka

    elif message.text.lower() == 'телефон отделов':
        bot.send_message(message.from_user.id, f'<b>Единый номер ООО "ТЕХПРОГРЕВ"</b>\n+7(812)407-29-17\n<b>Добавочный 1:</b> узнать стоимость услуг\n<b>Добавочный 2:</b> узнать информацию по текущей температуре вашего танк-контейнера\n<b>Добавочный 3:</b> бухгалтерия', parse_mode= 'HTML')

    elif message.text.lower() == 'зарегистрировать':
        bot.send_message(message.from_user.id, "Введите индивидуальный № танк-контейнера клиента:");
        bot.register_next_step_handler(message, get_tank); #следующий шаг – функция get_tank\
    elif message.text.lower() == 'дата и температура':
        bot.send_message(CHAT, f'Укажите № танк-контейнера:')
        bot.register_next_step_handler(message, get_vnesenie_tem_i_daty); #следующий шаг – функция get_vnesenie_tem_i_daty\
    elif message.text.lower() == 'связаться со мной':
        bot.forward_message(CHAT, message.chat.id, message.message_id)
        bot.send_message(message.from_user.id, "Ожидайте, в ближайшее время с вами свяжется наш специалист.");
        bot.send_message(CHAT, f'{message.from_user.first_name} {message.from_user.last_name} просит чтобы с ним связались.')
    elif message.text.lower() == 'узнать текущую температуру':
        bot.forward_message(CHAT, message.chat.id, message.message_id)
        bot.send_message(message.from_user.id, "Введите №танк-контейнера, температуру которого нужно узнать.");
        ##bot.send_message(CHAT, f'{message.from_user.first_name} {message.from_user.last_name} хочет узнать текущую температуру танк-контейнера:.')
        bot.register_next_step_handler(message, get_uznat_tem);
    elif message.text.lower() == 'отключить от прогрева':
        bot.forward_message(CHAT, message.chat.id, message.message_id)
        bot.send_message(message.from_user.id, "Введите №танк-контейнера который нужно отключить от прогрева");
        bot.register_next_step_handler(message, get_otkl);
    elif message.text.lower() == 'оформить заявку на прогрев':
        bot.send_message(message.from_user.id, "Для оформления заявки введите следующие данные:");
        bot.send_message(message.from_user.id, "Введите индивидуальный № танк-контейнера клиента:");
        bot.register_next_step_handler(message, get_tank); #следующий шаг – функция get_tank
    elif message.text.lower() == 'запросить pdf-файл наряд-заказа по вашей заявке':
        bot.forward_message(CHAT, message.chat.id, message.message_id)
        bot.send_message(message.from_user.id, "Введите №танк-контейнера");
        bot.register_next_step_handler(message, get_pdf);
    elif message.text.lower() == 'информация по клиенту':
        bot.send_message(CHAT, "Введите №танк-контейнера");
        bot.register_next_step_handler(message, get_infoKlienta);
        conn = sqlite3.connect('bd.db')
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM users WHERE numTanka = '{id}' """)
        rows = cur.fetchall()
        bot.send_message(CHAT, f'')

    elif message.text.lower() == "публикация":
        bot.send_message(CHAT, f'Введите текст публикации')
        bot.register_next_step_handler(message, sender);



    else:
        bot.send_message(message.from_user.id, "Я вас не понимаю, воспользуйтесь меню или напишите мне 'cвязаться со мной', и с вами свяжется наш специалист.");
        ##bot.send_message(CHAT, f'{message.from_user.first_name} {message.from_user.last_name} просит чтобы с ним связались.')

def get_zayavka(message):
    id = message.text.upper();
    conn = sqlite3.connect('bd.db')
    cur = conn.cursor()
    cur.execute(f"""SELECT * FROM users WHERE numTanka = '{id}' """)
    rows = cur.fetchall()
    if len(rows) < 1:
        bot.send_message(message.from_user.id, f'Такой номер отсутствует, проверьте правильно ли вы указали номер танк-контейнера и нажмите пункт меню "Получить данные по вашей заявке" . ')
        ##bot.send_message(message.from_user.id, f'получить данные по вашей заявке')
    else:
        for row in rows:
            bot.send_message(message.from_user.id, f'Информация по танк-контейнеру <b><u>№ {row[0]}</u></b>: \nДата и время поступления в работу: <b><u>{row[11]}</u></b>\nДата и время окончания работ: <b><u>{row[16]}</u></b>\nТемпература прибытия: <b><u>{row[5]}</u></b> \nНеобходимая температура прогрева: <b><u>{row[9]}</u></b>\nПродувка паровой рубашки ТК:  <b><u>{row[14]}</u></b>\nЗаявка оформлена: <b><u>{row[12]}</u></b>\nКонтактное лицо: <b><u>{row[1]}</u></b>\nСсылка на фотографию термометра: <b><u>{row[17]}</u></b> \n\nЧтобы узнать текущую температуру, нажмите пункт меню "Узнать текущую температуру"', parse_mode= 'HTML')
    conn.commit()


def get_tank(message): #получаем
    global numTanka; #Заказчик
    numTanka = message.text.upper();
    bot.send_message(message.from_user.id, 'Введите название заказчика:');
    bot.register_next_step_handler(message, get_zakaz);

def get_zakaz(message):
    global nameZakaz;
    nameZakaz = message.text;
    bot.send_message(message.from_user.id, 'Введите дату прибытия танк-контейнера:');
    bot.register_next_step_handler(message, get_data);

def get_data(message):
    global data;
    data = message.text;
    bot.send_message(message.from_user.id, 'Введите Гос.номер автомобиля:');
    bot.register_next_step_handler(message, get_numAvto);

def get_numAvto(message):
    global numAvto;
    numAvto = message.text;
    bot.send_message(message.from_user.id, 'Введите вид сырья (на русском языке):');
    bot.register_next_step_handler(message, get_vid);

def get_vid(message):
    global vid;
    vid = message.text;
    bot.send_message(message.from_user.id, 'Ф.И.О. водителя, паспортные данные и телефон:');
    bot.register_next_step_handler(message, get_vodit);

def get_vodit(message):
    global vodit;
    vodit = message.text;
    bot.send_message(message.from_user.id, 'Введите необходимую температуру прогрева:');
    bot.register_next_step_handler(message, get_neobTemp);

def get_neobTemp(message):
    global neobTemp;
    neobTemp = message.text;
    bot.send_message(message.from_user.id, 'Введите температуру пара:');
    bot.register_next_step_handler(message, get_tempPara);


def get_tempPara(message):
    global tempPara;
    tempPara = message.text;
    bot.send_message(message.from_user.id, 'Продувка паровой рубашки ТК:');
    bot.register_next_step_handler(message, get_produvRubaschki);

def get_produvRubaschki(message):
    global produvRubaschki;
    produvRubaschki = message.text;
    bot.send_message(message.from_user.id, 'Введите длину прицепа авто:');
    bot.register_next_step_handler(message, get_dlinna);

def get_dlinna(message):
    global dlinna;
    dlinna = message.text;
    bot.send_message(message.from_user.id, 'Введите ваше имя и фамилию (того кто оформяет заявку):');
    bot.register_next_step_handler(message, get_imyaOform);

def get_imyaOform(message):
    global imyaOform;
    imyaOform = message.text;
    bot.send_message(message.from_user.id, 'Введите контактный телефон:');
    bot.register_next_step_handler(message, get_telOform);

def get_telOform(message):
    global telOform;
    telOform = message.text;
    dataOform = now.strftime("%d-%m-%Y");
    conn = sqlite3.connect('bd.db')
    cur = conn.cursor()
    cur.execute("""INSERT INTO users(numTanka, nameZakaz, data, numAvto, vid, vodit, neobTemp, dlinna, imyaOform, telOform, dataOform, tempPara, produvRubaschki)
    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (numTanka, nameZakaz, data, numAvto, vid, vodit, neobTemp, dlinna, imyaOform, telOform, dataOform, tempPara, produvRubaschki))
    conn.commit()
    bot.send_message(message.from_user.id, f'Оформлена новая заявка\nЗаявка записана в базу данных: <b><u>{now.strftime("%d-%m-%Y")}</u></b>\n№ танк-контейнера: <b><u>{numTanka}</u></b>\nНазвание заказчика: <b><u>{nameZakaz}</u></b>\nДата прибытия танк-контейнера: <b><u>{data}</u></b>\nГос.номер автомобиля: <b><u>{numAvto}</u></b>\nВид сырья: <b><u>{vid}</u></b>\nНеобходимая температура прогрева: <b><u>{neobTemp}</u></b>\nТемпература пара: <b><u>{tempPara}</u></b>\nПродувка паровой рубашки ТК:  <b><u>{produvRubaschki}</u></b>\nФ.И.О. водителя, паспортные данные и телефон: <b><u>{vodit}</u></b>\nДлина прицепа авто: <b><u>{dlinna}</u></b>\nЗаявку оформил: <b><u>{imyaOform}</u></b>\nКонтактный телефон: <b><u>{telOform}</u></b>', parse_mode= 'HTML')
    bot.send_message(CHAT, f'Оформлена новая заявка\nЗаявка записана в базу данных: <b><u>{now.strftime("%d-%m-%Y")}</u></b>\n№ танк-контейнера: <b><u>{numTanka}</u></b>\nНазвание заказчика: <b><u>{nameZakaz}</u></b>\nДата прибытия танк-контейнера: <b><u>{data}</u></b>\nГос.номер автомобиля: <b><u>{numAvto}</u></b>\nВид сырья: <b><u>{vid}</u></b>\nНеобходимая температура прогрева: <b><u>{neobTemp}</u></b>\nТемпература пара: <b><u>{tempPara}</u></b>\nПродувка паровой рубашки ТК:  <b><u>{produvRubaschki}</u></b>\nФ.И.О. водителя, паспортные данные и телефон: <b><u>{vodit}</u></b>\nДлина прицепа авто: <b><u>{dlinna}</u></b>\nЗаявку оформил: <b><u>{imyaOform}</u></b>\nКонтактный телефон: <b><u>{telOform}</u></b>', parse_mode= 'HTML')

def get_vnesenie_tem_i_daty(message):
    global tankIzmen;
    tankIzmen = message.text;
    conn = sqlite3.connect('bd.db')
    cur = conn.cursor()
    cur.execute(f"""SELECT * FROM users WHERE numTanka = '{tankIzmen}' """)
    rows = cur.fetchall()
    if len(rows) < 1:
        bot.send_message(CHAT, f'Такой номер отсутствует, проверьте правильно ли вы указали номер танк-контейнера и вновь введите команду "дата и температура"')
    else:
        bot.send_message(CHAT, 'Введите температуру прибытия:');
        bot.register_next_step_handler(message, get_tempPrib);
    conn.commit()

def get_tempPrib(message):
    global tempPrib;
    tempPrib = message.text;
    bot.send_message(CHAT, 'Введите дату и время поступления в работу:');
    bot.register_next_step_handler(message, get_dataPostup);

def get_dataPostup(message):
    global dataPostup;
    dataPostup = message.text;
    conn = sqlite3.connect('bd.db')
    cur = conn.cursor()
    cur.execute("""UPDATE users SET tempPr = ?, timeJob = ? WHERE numTanka = ?""", (tempPrib, dataPostup, tankIzmen))
    conn.commit()
    bot.send_message(CHAT, f'Данные успешно внесены в базу данных для танк-контейнера №{tankIzmen} ');

        ##bot.send_message(CHAT, f'такого танк-контейнера нет');

    ##bot.register_next_step_handler(message, get_dlinna);

def get_uznat_tem(message):
    global uznat_temp;
    uznat_temp = message.text;
    bot.send_message(message.from_user.id, 'Я отправил нашему специалисту сообщение, что вы хотите узнать текущую температуру вашего танк-контейнера. Ожидайте, скоро он свяжется с вами.');
    bot.send_message(CHAT, f'{message.from_user.first_name} {message.from_user.last_name} хочет узнать текущую температуру танк-контейнера:.')
    bot.send_message(CHAT, f'№ танк-контейнера {uznat_temp}');

def get_otkl(message):
    global uznat_temp;
    uznat_temp = message.text;
    bot.send_message(message.from_user.id, 'Я отправил нашему специалисту сообщение, что вы хотите отключить танк-контейнер от прогрева. Ожидайте, скоро он свяжется с вами.');
    bot.send_message(CHAT, f'{message.from_user.first_name} {message.from_user.last_name} хочет отключить танк-контейнер от прогрева.')
    bot.send_message(CHAT, f'№ танк-контейнера {uznat_temp}');

def get_pdf(message):
    global uznat_temp;
    uznat_temp = message.text;
    bot.send_message(message.from_user.id, 'Я отправил нашему специалисту сообщение, что вы хотите PDF-файл наряд-заказа по вашей заявке. Ожидайте, скоро он свяжется с вами.');
    bot.send_message(CHAT, f'{message.from_user.first_name} {message.from_user.last_name} хочет получить PDF-файл наряд-заказа по вашей заявке.')
    bot.send_message(CHAT, f'№ танк-контейнера {uznat_temp}');

def get_infoKlienta(message):
    global infoKlienta;
    infoKlienta = message.text;
    conn = sqlite3.connect('bd.db')
    cur = conn.cursor()
    cur.execute(f"""SELECT * FROM users WHERE numTanka = '{infoKlienta}' """)
    rows = cur.fetchall()
    if len(rows) < 1:
        bot.send_message(CHAT, f'Такой номер отсутствует, проверьте правильно ли вы указали номер танк-контейнера и снова введите команду "информация по клиенту" . ')
        ##bot.send_message(message.from_user.id, f'получить данные по вашей заявке')
    else:
        for row in rows:
            bot.send_message(CHAT, f'Информация клиенту <b><u>№ {row[0]}</u></b>: \nИмя: <b><u>{row[1]}</u></b>\nКонтактный телефон: <b><u>{row[2]}</u></b>\nНазвание заказчика: <b><u>{row[3]}</u></b>\nГос.номер автомобиля: <b><u>{row[6]}</u></b>\nВид сырья (на русском языке): <b><u>{row[7]}</u></b>\nНеобходимая температура прогрева: <b><u>{row[9]}</u></b>\nТемпература пара: <b><u>{row[13]}</u></b>\nПродувка паровой рубашки ТК:  <b><u>{row[14]}</u></b>\nФ.И.О. водителя, паспортные данные и телефон: <b><u>{row[8]}</u></b>\nДлина прицепа авто: <b><u>{row[10]}</u></b>\nДата поступления в работу: <b><u>{row[11]}</u></b>\nДата и время окончания работ: <b><u>{row[16]}</u></b>\nДата оформления заявки: <b><u>{row[12]}</u></b>\nСсылка на фотографию термометра: <b><u>{row[17]}</u></b>', parse_mode= 'HTML')
    conn.commit()

def sender(message):
    textSend = message.text;
    conn = sqlite3.connect('bd2.db')
    cur = conn.cursor()
    cur.execute(f"""SELECT * FROM idusers""")
    rows = cur.fetchall()
    for row in rows:
        bot.send_message(row[0], f'{textSend}')
        time.sleep(2)
    conn.commit()

def main(use_logging, level_name):
    if use_logging:
        telebot.logger.setLevel(logging.getLevelName(level_name))
    bot.polling(none_stop=True, interval=.5)
if __name__ == '__main__':
    main(True, 'DEBUG')