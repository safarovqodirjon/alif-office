import smtplib
import sqlite3
from datetime import date
from datetime import timedelta as tmd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version
import requests
# создаем класс оффис
class Office:
    def __init__(self, s=0, number='', email='', name='', address='',
                 cindate='', countdate=0, endtime=None, rno="", satage_1=False, status='zanyat'):

        print("*****Alif Office*****\n")
        self.s = s
        self.email = email
        self.name = name
        self.address = address
        self.number = number
        self.cindate = cindate
        self.countdate = countdate
        self.endtime = endtime
        self.rno = rno
        self.status = status
        self.stage_1 = satage_1

    # функция для получения личних данних о клиенте
    def inputdata(self):
        self.name = input("\nВведите имя клиента:")
        self.address = input("\nВведите адресс клиената:")
        self.email = input("\nВведите эл-почту клиента:")
        self.number = input("\nВведите номер тел клиента:")
        self.cindate = date.today()
        self.stage_1 = True
        print("Нажмите 2:", "\n")


    # функция для оформления кабинет
    def rent(self):
        if self.stage_1:
            connection_obj = sqlite3.connect('office.db') # подключения к базе данных
            cursor_obj = connection_obj.cursor()

            table = """CREATE TABLE IF NOT EXISTS customer (
                            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            customer_name VARCHAR(255),
                            customer_address VARCHAR(255),
                            customer_number VARCHAR(255),
                            customer_email VARCHAR(255),
                            customer_cabinet VARCHAR(255),
                            customer_realtime TEXT,
                            customer_countday INTEGER,
                            customer_endtime TEXT,
                            customer_total INTEGER,
                            customer_status VARCHAR(10)
                        );"""

            cursor_obj.execute(table)
            connection_obj.commit()

            # провераяем не истек ли срок аренды определенного клиента в кабинете
            try:
                check_exp = """update customer
                set customer_status = 'svobodna'
                where JulianDay(DATE('now')) - JulianDay(customer_endtime)<=0;
                """
                cursor_obj.execute(check_exp)
                connection_obj.commit()
            except Exception:
                print("Еше нет записей!")

            office_list = ['Office number-1', 'Office number-2', 'Office number-3', 'Office number-4',
                           'Office number-5']

            # real = cursor_obj.execute(
            #     "select distinct customer_cabinet from customer where JulianDay(customer_endtime)-JulianDay(customer_realtime)>=0;").fetchall()

            # подбираем только свободные номера

            real = cursor_obj.execute("select distinct customer_cabinet from customer where customer_status != 'zanyat'")
            connection_obj.commit()
            db_list = []
            for val in real:
                db_list.append(val[0])

            office_list = set(office_list)
            db_list = set(db_list)
            empty_cobinet = sorted(office_list - db_list)

            if len(empty_cobinet) > 0:
                print("*" * 20)
                print("Список свободних кабинетов:")
                print("*" * 20)

                c = 0
                for office in empty_cobinet:
                    c += 1
                    print(str(c) + ".", office)

                x = int(input("Ведите номер из списка кабинетов:"))

                self.countdate = int(input("На сколько дней:"))
                self.endtime = self.cindate + tmd(days=self.countdate)

                try:
                    if x == 1:

                        print(f"You have choose {empty_cobinet[0]}")
                        self.rno = empty_cobinet[0]
                        self.s = 400 * self.countdate

                    elif x == 2:

                        print(f"Вы выбрали {empty_cobinet[1]}")

                        self.rno = empty_cobinet[1]
                        self.s = 300 * self.countdate

                    elif x == 3:
                        print(f"Вы выбрали {empty_cobinet[2]}")

                        self.rno = empty_cobinet[2]
                        self.s = 200 * self.countdate

                    elif x == 4:
                        print(f"Вы выбрали {empty_cobinet[3]}")

                        self.rno = empty_cobinet[3]
                        self.s = 100 * self.countdate

                    elif x == 5:
                        print(f"Вы выбрали {empty_cobinet[4]}")

                        self.rno = empty_cobinet[4]
                        self.s = 100 * self.countdate

                    else:
                        print("Пожайлуста выберите кабинет")

                except Exception as ex:
                    print("***Выберите только из номеров списка***")

            else:
                print("*" * 20)
                print("***В данний момент у нас нет свободних кабинетов***")
                print("*" * 20)
                self.rno = "!!!нет кабинетов!!!"
        else:
            print()
            print("****Пайжайлуст сначали нажмите 1 и заполните данные клиента***")
            print()


    # Функция для очистки данних из дата базы (если понадобится)
    def clean(self):
        try:

            connection_obj = sqlite3.connect('office.db')
            cursor_obj = connection_obj.cursor()
            clean_table = "delete from customer;"
            cursor_obj.execute(clean_table)
            connection_obj.commit()
        except Exception:
            print("Что то пошло не так!")

    def print_check(self):

        print("*" * 20)
        print("******Check******")
        print("Имя:", self.name)
        print("Адресс:", self.address)
        print("С - : ", self.cindate)
        print("По -: ", self.endtime)
        print("Кабинет: ", self.rno)
        print("Итого :", self.s)
        print("*" * 20)

    # сохраняяем в дата база
    def send_to_db(self):
        connection_obj = sqlite3.connect('office.db')
        cursor_obj = connection_obj.cursor()
        # self.status = "zanyat"
        val = (self.name, str(self.address), str(self.number), str(self.email),
               str(self.rno), self.cindate, self.countdate, self.endtime, self.s, self.status)

        query = """
        INSERT INTO customer (customer_name, customer_address,
        customer_number, customer_email, customer_cabinet, customer_realtime, 
        customer_countday, customer_endtime, customer_total, customer_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

        cursor_obj.execute(query, val)

        connection_obj.commit()
        cursor_obj.close()

    # Отправляяем сообшения лимит смс 1 в день а на эл-почту нет лимита
    def send_mess(self):

        recipients = str(self.email)
        subject = "Арендования кабинета в alif"
        server = "smtp.gmail.com"
        errors = []
        key = input('Что бы отправить СМС нажмите 1, а эл-почту  2: ')

        if str(key) == '2':

            sender = "officealif2@gmail.com"
            password = "mytestpasswordforalif"

            text = f"""<h1>Здраствуйте {self.name} вы<h1>
                        </b> вы арендовали {self.rno} за <h1 style="color: red">{self.s} сомонӣ</h1>
                        <h1 style="color":green>c {self.cindate} по {self.endtime}</h1>'
                        """
            html = '<html><head></head><body><p>' + text + '</p></body></html>'

            try:
                msg = MIMEMultipart('alternative')

                msg['Subject'] = subject
                msg['From'] = '<' + sender + '>'
                msg['To'] = recipients
                msg['Reply-To'] = sender
                msg['Return-Path'] = sender
                msg['X-Mailer'] = 'Python/' + (python_version())

                part_text = MIMEText(text, 'plain')
                part_html = MIMEText(html, 'html')

                msg.attach(part_text)
                msg.attach(part_html)

                mail = smtplib.SMTP_SSL(server, 465)
                try:
                    mail.login(sender, password)
                except TypeError:
                    errors.append('Ошыбака пароля')
                mail.sendmail(sender, recipients, msg.as_string())
                mail.quit()
                print(f"Сообшение отправлено с почты {sender} к клиенту {recipients}")
            except OSError:
                errors.append('Ошыбка с соединением при отпраке email')


        elif str(key) == '1':
            try:


                resp = requests.post('https://textbelt.com/text', {
                    'phone': '+992' + self.number,
                    'message': f'Салом {self.name} вы арендавали {self.rno} с {self.cindate} по {self.endtime} за {self.s} сомонӣ',
                    'key': 'textbelt',
                })

                dct = dict(resp.json())

                if not dct['success']:
                    errors.append(str("Толко один бесплатный СМС в день" + " >> " + str(dct['error'])))
            except OSError:
                errors.append(f'Ошыбка соединения при отправке СМС клиенту {self.name}')
                print(errors)



# финалная функция
def run():
    o = Office()
    while True:
        command_list = ['Введите данние клиента: ', 'Оформит кабинет: ',
                        'Напечатат чек: ', 'Послат сообшения (SMS 1 бесплатное в день, эл-почта бесплатно)',
                        'Очистит DataBase', 'Выход']
        c = 0
        for val in command_list:
            c += 1
            print(str(c) + ".", val)

        try:
            ch = int(input("\nВведиете номер из списка в верху списка: "))
            if ch == 1:
                o.inputdata()
            if ch == 2:
                o.rent()
                o.send_to_db()
            if ch == 3:
                o.print_check()

            if ch == 4:
                o.send_mess()

            if ch == 5:
                o.clean()
            if ch == 6:
                quit()

        except Exception:
            print("***Номера только из списка ***")
 # Запуск функции
run()