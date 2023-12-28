import PySimpleGUI as sg
from datetime import datetime
import select
import psycopg2
import limiter
import robot
import csv, os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import functions


working_directory = os.getcwd()
conn = psycopg2.connect(dbname='Authentication', user='postgres', password=' ')

sg.theme('Black')

information_array = []
headings_workers = ['Login', 'ФИО']

layoutCheck = [
    [sg.Text(' '*10),sg.Text('', visible = True, key = 'check')]
]
layoutButtons = [
    [sg.Text(' '*8), sg.Image(), sg.Text('Добро пожаловать!', font = 'Helvetica 32')], 
    # [
    #     sg.Text(' '*10), sg.Button('Я - работодатель', size = (20, 2), font = 'Courier 16'), 
    #     sg.Button('Я - работник', size = (20, 2), font = 'Courier 16')
    # ], 
    [sg.Text(' '*10),sg.Text('Login', size=(20,1)), sg.Input(key='Login1', size=(20,1))],
    [sg.Text(' '*10),sg.Text('Password', size=(20,1)), sg.Input(key='Password1', size=(20,1))],
    [sg.Text(' '*10),sg.Button('Вход', size = (20, 2), font = 'Courier 16', key = 'Вход1'),
     sg.Button('Регистрация', size = (20, 2), font = 'Courier 16')],
    [sg.Text(' ')],
    [sg.Image(size = (700, 700)), sg.Text(' '*10)]
]

#here input all of employer window 

layoutEmployer = [
    [sg.Text('Работодатель', font = 'Helvetica 18', key = 'headingEmployer', size = (20)), sg.Button('Your Profile', key = 'ProfileEmpl'), sg.Text(' '*3), sg.Text('Список работников')],
    [sg.Multiline(size = (50, 15), key = 'task'),
    sg.Listbox(values = information_array, size = (25, 14), key = 'list')
    ],
    
    # [sg.FileBrowse('Прикрепить файл', initial_folder=working_directory, file_types=(("All Files", "*.*"),), font = 'Courier 16', key = 'file'), sg.InputText('', key = '-FILE-'), sg.Button("Submit")],
    [sg.Button('Список мероприятий', font = 'Courier 16', key = 'OpenListEmpl'),sg.Text(' '*20), sg.Button('Проверить отчет', font = 'Courier 16', key = 'CheckReport')],
    [sg.Text('', key = 'loginWorker'), sg.Text('', key = 'nameWorker')]
]   

layoutCheckReport = [
    [sg.Text('', font = 'Courier 18', key='NameOfCheckingReport')],
    [sg.Text('Скачать отчет', font='Courier 16'), sg.Button("Download PDF")],
    [sg.Button('Изменить статус работы', font= 'Courier 16', key = 'Verdict')],
    [sg.Text('Работа завершена?', font='Courier 16', key='Finish', visible=False), sg.Radio('Да', "answ", key = 'answ1', visible=False), sg.Radio('Нет', "answ", key = 'answ2', visible=False)],
    [sg.Text('Комментарий: ', font='Courier 16', key = 'CommentTextReport',visible=False)],
    [sg.Multiline('', key = 'CommentReport', font='Courier 16', size=(30,10), visible=False)],
    [sg.Button('Внести изменения', font='Courier 16', key='Verdict2', visible=False), sg.Button('Отменить', font='Courier 16', key='Cancel2', visible=False), sg.Button('Назад', font = 'Courier 16', key = 'Back9')]
]

layoutEventsEmpl = [
    [sg.Text('Список мероприятий', font = 'Courier 16')],
    [sg.Listbox(values = information_array, size = (67, 14), key = 'listEventsEmpl')],
    [sg.Text('Мероприятие', size = (16), font = 'Courier 16'), sg.Input(key = 'NameEventEmpl',font = 'Courier 16', size = (20,5))],
    [sg.CalendarButton("Дата мероприятия", format='%Y-%m-%d', close_when_date_chosen=True, font = 'Courier 16',  target='DateEventEmpl', size = (16)), sg.Input(key='DateEventEmpl',font = 'Courier 16', size=(20,5))],
    [sg.Button('Добавить мероприятие', size = (18), font = 'Courier 16', key = 'AddEventEmpl'), sg.Button('Удалить мероприятие', size = (18), font = 'Courier 16', key = 'DeleteEventEmpl')],
    [sg.Button('Назад',font = 'Courier 16', key = 'Назад6')]
]

layoutEmployerAccount = [
    [sg.Text('Login: ', font='Courier 16', size = (12)), sg.Text('', key = 'LoginAccEmpl', font='Courier 16', visible=True), sg.Input('', font='Courier 16', key = 'LoginAccEmplChange', visible=False)],
    [sg.Text('Full Name: ', font='Courier 16', size = (12)), sg.Text('', key = 'FullNameAccEmpl', font='Courier 16', visible=True), sg.Input('', font='Courier 16', key = 'FullNameAccEmplChange', visible=False)],
    [sg.Text('Password: ', font='Courier 16', size = (12)), sg.Text('', key = 'PasswordAccEmpl', font='Courier 16', visible=True), sg.Input('', font='Courier 16', key = 'PasswordAccEmplChange', visible=False)],
    [sg.Text('Company: ', font='Courier 16', size = (12)), sg.Text('', font='Courier 16', key = 'CompanyAccEmpl', visible=True), sg.Input('', font='Courier 16', key = 'CompanyAccEmplChange', visible=False)],
    [sg.Button('Edit Profile', font='Courier 16', key = 'EditProfileEmpl', visible = True), sg.Button('Cancel', font='Courier 16', key = 'CancelEmpl', visible = False), sg.Button('Save Changes', font='Courier 16', key = 'SaveChagesEmpl', visible=False), sg.Button('Back', font='Courier 16', key = 'Back4')],
    [sg.Button('Выход', font='Courier 16', key = 'Назад1')]
]

#here input all of worker window
col1 = [
    [sg.Text('Режим работы: ', font='Courier 16'), sg.Text('Выключен', font='Courier 16', key='statusBlock')],
    # [sg.Input(key='-DEPARTURE-', font='Courier 16', size=(20,1)), sg.CalendarButton("Начало работы", font='Courier 16', close_when_date_chosen=True,  target='-DEPARTURE-', location=(0,0), no_titlebar=False)],
    # [sg.Input(key='-ARRIVAL-', font='Courier 16', size=(20,1)), sg.CalendarButton("Конец работы", font='Courier 16', close_when_date_chosen=True,  target='-ARRIVAL-', location=(0,0), no_titlebar=False)],
    # [sg.Text('Продолжительность работы')],
    # [sg.Text(size=(20, 2), font=('Helvetica', 20), justification='center', key='-TIME_DIFFERENCE-')],
    # [sg.Button('Calculate Difference')],
    [sg.Button('Включить блокировку', font='Courier 16', key = 'TurnOn'), sg.Button('Выключить блокировку', font='Courier 16', key = 'TurnOff')],
    [sg.Button('Назад', font='Courier 16', key = 'Назад7', size = (10))]
]


layoutWorker = [
    [sg.Text('Работник', font = 'Helvetica 18', key = 'headingWorker'), sg.Button('Your Profile', key = 'ProfileWorker')],
    [sg.Text('Список мероприятий', font = 'Courier 16')], 
    [sg.Listbox(values = information_array, size = (67, 14), key = 'listEventsWorker')],
    [sg.Text('Мероприятие', size = (16), font = 'Courier 16'), sg.Input(key = 'NameEventWorker',font = 'Courier 16', size = (20,5))],
    [sg.CalendarButton("Дата мероприятия", format='%Y-%m-%d', close_when_date_chosen=True, font = 'Courier 16',  target='DateEventWorker', size = (16)), sg.Input(key='DateEventWorker',font = 'Courier 16', size=(20,5))],
    [sg.Button('Добавить мероприятие', font = 'Courier 16', size = (18), key = 'AddEventWorker'), sg.Button('Удалить мероприятие', size = (18), font='Courier 16', key='DeleteEventWorker')],
    [sg.Button('Режим работы',font = 'Courier 16', size = (18), key = 'OpenListWorker'), sg.Button('Сформировать отчет',font = 'Courier 16', size = (18), key = 'CreateReport')]
 ]

layoutWorkerAccount = [
    [sg.Text('Login: ', font='Courier 16', size = (12)), sg.Text('', font='Courier 16', key = 'LoginAccWorker', visible=True), sg.Input('', font='Courier 16', key = 'LoginAccWorkerChange', visible=False)],
    [sg.Text('Full Name: ', font='Courier 16', size = (12)), sg.Text('', font='Courier 16', key = 'FullNameAccWorker', visible=True), sg.Input('', font='Courier 16', key = 'FullNameAccWorkerChange', visible=False)],
    [sg.Text('Password: ', font='Courier 16', size = (12)), sg.Text('', font='Courier 16', key = 'PasswordAccWorker', visible=True), sg.Input('', font='Courier 16', key = 'PasswordAccWorkerChange', visible=False)],
    [sg.Text('Company: ', font='Courier 16', size = (12)), sg.Text('', font='Courier 16', key = 'CompanyAccWorker', visible=True), sg.Input('', font='Courier 16', key = 'CompanyAccWorkerChange', visible=False)],
    [sg.Button('Edit Profile', font='Courier 16', key = 'EditProfileWorker', visible = True), sg.Button('Cancel', font='Courier 16', key = 'CancelWorker', visible = False), sg.Button('Save Changes', font='Courier 16', key = 'SaveChagesWorker', visible=False), sg.Button('Back', font='Courier 16', key = 'Back5')],
    [sg.Button('Выход', font='Courier 16', key = 'Назад2')]
]
layoutEventsWorker = [
        [sg.Text('Список мероприятий', font = 'Courier 16')], 
        [sg.Listbox(values = information_array, size = (67, 14), key = 'listEventsWorker')],
        [sg.Text('Мероприятие', size = (16), font = 'Courier 16'), sg.Input(key = 'NameEventWorker',font = 'Courier 16', size = (20,5))],
        [sg.CalendarButton("Дата мероприятия", format='%Y-%m-%d', close_when_date_chosen=True, font = 'Courier 16',  target='DateEventWorker', size = (16)), sg.Input(key='DateEventWorker',font = 'Courier 16', size=(20,5))],
        [sg.Button('Добавить мероприятие', font = 'Courier 16', key = 'AddEventWorker'), sg.Text(' '*26), sg.Button('Назад',font = 'Courier 16', key = 'Назад7')]
]
layoutCreateReportWorker = [
    [sg.Input('', key = 'nameReportWorker', size=(73)), sg.Text('Название отчета', font = 'Courier 16')],
    [sg.Multiline(size = (100, 15), key = 'textReportWorker')],
    # [sg.Input(size = 47, key = 'ImageReport'), sg.FileBrowse('Прикрепить изображение', size = (15), font = 'Courier 16'), sg.Submit('Подтвердить', font = 'Courier 16')],
    [sg.Button('Загрузить отчет', font='Courier 16', size=(25), key = 'AddReportWorker'),sg.Button('Последний отчет', font='Courier 16', key = 'lastReport'), sg.Text(' '*14), sg.Button('Назад', font = 'Courier 16', key = 'Back8')]
]
layoutLastReport = [
    [sg.Text('NameOfReport', font='Courier 18', key = 'NameLastReport')],
    [sg.Text('Статус работы: ', font='Courier 16'), sg.Text('', font='Courier 16', key='StatusWork')],
    [sg.Text('Комментарий работодателя: ', font='Courier 16'), sg.Text('', font='Courier 16', key='CommentWork')],
    [sg.Text('Исправить', font='Courier 16', key='ChangeWork', visible=False), sg.Button('Назад', font='Courier 16', key='Back10')]
]
layoutRegistration = [
    [sg.Text('Login', size=(20,1)), sg.Input(key='Login2', size=(20,1))],
    [sg.Text('Full Name', size=(20,1)), sg.Input(key='FName', size=(20,1))],
    [sg.Text('Password', size=(20,1)), sg.Input(key='Password2', size=(20,1))],
    [sg.Text('Company', size=(20,1)), sg.Input(key='Company', size=(20,1))],
    [sg.Radio('Employer', "reg", key = 'employer1'), sg.Radio('Worker', "reg", key = 'worker1')],
    [sg.Button('Вход', size = (20, 2), font = 'Courier 16', key = 'Вход2')],
    [sg.Button('Назад',font = 'Courier 16', key = 'Назад3')]
]

#this is main window with autenfication
layoutMain = [
    [
    sg.Column(layoutButtons, key = 'buttons'), 
    sg.Column(layoutEmployer, visible=False, key = 'employer'),
    sg.Column(layoutWorker, visible=False, key = 'worker'),
    sg.Column(layoutRegistration, visible=False, key = 'registration'),
    sg.Column(layoutEmployerAccount, visible=False, key = 'employerProfile'),
    sg.Column(layoutWorkerAccount, visible=False, key = 'workerProfile'),
    sg.Column(layoutEventsEmpl, visible=False, key = 'layoutEvents'),
    sg.Column(col1, visible=False, key = 'layoutEventsWorker'),
    sg.Column(layoutCreateReportWorker, visible=False, key = 'layoutReportWorker'),
    sg.Column(layoutCheckReport, visible=False, key='layoutCheckReport'),
    sg.Column(layoutLastReport, visible=False, key='layoutLastReport'),
    layoutCheck
    ]
    ]

def employer(employer_login):
    with conn.cursor() as curs:            
            curs.execute(f'''select worker_login, worker_name from worker 
                             where worker_company = (select employer_company from employer 
					                                where employer_login = '{employer_login}') ''')
            data = curs.fetchall()
            print(data, len(data))
            for i in range(len(data)):
                information_array.append(str([data[i][1]])[2:-2])
            window.Element('list').Update(values = information_array)
    


def ChangeProfileHide(status, bool):
    # window.Element(f'LoginAcc{status}').Update(visible = bool)
    window.Element(f'FullNameAcc{status}').Update(visible = bool)
    window.Element(f'PasswordAcc{status}').Update(visible = bool)
    window.Element(f'CompanyAcc{status}').Update(visible = bool)
    window.Element(f'EditProfile{status}').Update(visible = bool)
    window.Element(f'SaveChages{status}').Update(visible = bool)

def ChangeProfileShow(status, bool):
    # window.Element(f'LoginAcc{status}Change').Update(visible = bool)
    window.Element(f'FullNameAcc{status}Change').Update(visible = bool)
    window.Element(f'PasswordAcc{status}Change').Update(visible = bool)
    window.Element(f'CompanyAcc{status}Change').Update(visible = bool)
    window.Element(f'Cancel{status}').Update(visible = bool)
    window.Element(f'SaveChages{status}').Update(visible = bool)



def ShowEvents(status, login):
    with conn.cursor() as curs:
        curs.execute(f'''select event_name, event_date from event where {status}_id = (select {status}_id from {status} 
										where {status}_login = '{login}') ''')
        events = curs.fetchall()
        information_array.clear()
        string = ''
        for i in range(len(events)):
                string = events[i][0] + ', ' + events[i][1]
                information_array.append(string)
        if status == 'employer':
            window.Element('listEventsEmpl').Update(values = information_array)
        elif status == 'worker':
            window.Element('listEventsWorker').Update(values = information_array)


def AddEvent(status, name, date, login):
    with conn.cursor() as curs:
        curs.execute(f'''select count(*) from event''')
        id = curs.fetchone()
        curs.execute(f'''select {status}_id from {status} where {status}_login = '{login}' ''')
        id_human = curs.fetchone()
        curs.execute(f'''insert into event (event_id, event_name, event_date, {status}_id) values ({id[0]+1}, '{name}', '{date}', {id_human[0]})''')       
        conn.commit()
        ShowEvents(status=status, login=login)  


window = sg.Window('Window Title',  layoutMain, size = (1000, 600), resizable = True, element_justification = 'center')

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Вход1':
        values['Login1']
        values['Password1']
        with conn.cursor() as curs:
            curs.execute(f'''SELECT * FROM 
                    (SELECT 'таблица1' AS Таблица, 
                        CASE WHEN EXISTS (SELECT * FROM employer WHERE employer_login = '{values['Login1']}' and employer_password = '{values['Password1']}') THEN 'true' ELSE 'false' END as содержание_найдено
                        UNION ALL
                        SELECT 'таблица2' AS Таблица, 
                        CASE WHEN EXISTS (SELECT * FROM worker WHERE worker_login = '{values['Login1']}' and worker_password = '{values['Password1']}') THEN 'true' ELSE 'false' END as содержание_найдено
                    ) AS subquery''')
            data = curs.fetchall()
            if data[0][1] == 'true' or data[1][1] == 'true':
                window.Element('check').Update('')
                curs.execute(f'''SELECT CASE WHEN EXISTS (SELECT * FROM worker WHERE worker_login = '{values['Login1']}') THEN 'true' ELSE 'false' END as содержание_найдено''')
                data = curs.fetchone()
                print(data[0])
                if data[0] == 'true':
                    window.Element('employer').Update(visible = False)
                    window.Element('worker').Update(visible = True)
                    window.Element('buttons').Update(visible = False)
                    window.Element('registration').Update(visible = False)
                    window.Element('headingWorker').Update(f'''Работник - {values['Login1']}''')
                    # Will be done after Empl
                    dataHuman = functions.FindInfoAboutHuman(status = 'worker', login = values['Login1'])
                    window.Element('LoginAccWorker').Update(values['Login1'])
                    window.Element('FullNameAccWorker').Update(dataHuman[0][2])
                    window.Element('PasswordAccWorker').Update(dataHuman[0][3])
                    window.Element('CompanyAccWorker').Update(dataHuman[0][4])
                    ShowEvents(status='worker', login=values['Login1'])
                elif data[0] == 'false':
                    employer(values['Login1'])
                    window.Element('worker').Update(visible = False)
                    window.Element('buttons').Update(visible = False)
                    window.Element('registration').Update(visible = False)
                    window.Element('headingEmployer').Update(f'''Работодатель - {values['Login1']}''')
                    window.Element('employer').Update(visible = True)
                    # 
                    dataHuman = functions.FindInfoAboutHuman(status = 'employer', login = values['Login1'])
                    window.Element('LoginAccEmpl').Update(values['Login1'])
                    print(window.Element('LoginAccEmpl').get())
                    window.Element('FullNameAccEmpl').Update(dataHuman[0][2])
                    window.Element('PasswordAccEmpl').Update(dataHuman[0][3])
                    window.Element('CompanyAccEmpl').Update(dataHuman[0][4])
                    ShowEvents(status='employer', login=values['Login1'])
            elif data[0][1] == 'false' or data[1][1] == 'false':
                window.Element('check').Update('Incorrect login or password')
    if event == 'Я - работодатель':
        window.Element('employer').Update(visible = True)
        window.Element('worker').Update(visible = False)
        window.Element('buttons').Update(visible = False)
        window.Element('registration').Update(visible = False) 
    if event == 'ProfileEmpl':
        window.Element('employerProfile').Update(visible = True)
        window.Element('employer').Update(visible = False)
    if event == 'Back4':
        window.Element('employerProfile').Update(visible = False)
        window.Element('employer').Update(visible = True)
    if event == 'EditProfileEmpl':
        ChangeProfileHide(status='Empl', bool=False)
        ChangeProfileShow(status='Empl', bool=True)
    if event == 'CancelEmpl':
        ChangeProfileHide(status='Empl', bool=True)
        ChangeProfileShow(status='Empl', bool=False)
        window.Element('FullNameAccEmplChange').Update('')
        window.Element('PasswordAccEmplChange').Update('')
        window.Element('CompanyAccEmplChange').Update('')
    if event == 'SaveChagesEmpl':
        functions.SaveChagesProfile(status='employer', login=window.Element('LoginAccEmpl').get(), name=values['FullNameAccEmplChange'], password=values['PasswordAccEmplChange'], company=values['CompanyAccEmplChange'])
        window.Element('FullNameAccEmplChange').Update('')
        window.Element('PasswordAccEmplChange').Update('')
        window.Element('CompanyAccEmplChange').Update('')
        if values['FullNameAccEmplChange'] != '':
            window.Element('FullNameAccEmpl').Update(f'''{values['FullNameAccEmplChange']}''')
        elif values['PasswordAccEmplChange']:
            window.Element('PasswordAccEmpl').Update(f'''{values['PasswordAccEmplChange']}''')
        elif values['CompanyAccEmplChange']:
            window.Element('CompanyAccEmpl').Update(f'''{values['CompanyAccEmplChange']}''')
        ChangeProfileHide(status='Empl', bool=True)
        ChangeProfileShow(status='Empl', bool=False)
    if event == 'ProfileWorker':
        window.Element('workerProfile').Update(visible = True)
        window.Element('worker').Update(visible = False)
    if event == 'Back5':
        window.Element('workerProfile').Update(visible = False)
        window.Element('worker').Update(visible = True)
    if event == 'EditProfileWorker':
        ChangeProfileHide(status='Worker', bool=False)
        ChangeProfileShow(status='Worker', bool=True)
    if event == 'CancelWorker':
        ChangeProfileHide(status='Worker', bool=True)
        ChangeProfileShow(status='Worker', bool=False)
        window.Element('FullNameAccWorkerChange').Update('')
        window.Element('PasswordAccWorkerChange').Update('')
        window.Element('CompanyAccWorkerChange').Update('')
    if event == 'SaveChagesWorker':
        functions.SaveChagesProfile(status='worker', login=window.Element('LoginAccWorker').get(), name=values['FullNameAccWorkerChange'], password=values['PasswordAccWorkerChange'], company=values['CompanyAccWorkerChange'])
        window.Element('FullNameAccWorkerChange').Update('')
        window.Element('PasswordAccWorkerChange').Update('')
        window.Element('CompanyAccWorkerChange').Update('')
        if values['FullNameAccWorkerChange'] != '':
            window.Element('FullNameAccWorker').Update(f'''{values['FullNameAccWorkerChange']}''')
        elif values['PasswordAccWorkerChange']:
            window.Element('PasswordAccWorker').Update(f'''{values['PasswordAccWorkerChange']}''')
        elif values['CompanyAccWorkerChange']:
            window.Element('CompanyAccWorker').Update(f'''{values['CompanyAccWorkerChange']}''')
        ChangeProfileHide(status='Worker', bool=True)
        ChangeProfileShow(status='Worker', bool=False)
    if event == 'OpenListEmpl':
        window.Element('layoutEvents').Update(visible=True)
        window.Element('employer').Update(visible=False)
    if event == 'Назад6':
        window.Element('layoutEvents').Update(visible=False)
        window.Element('employer').Update(visible=True)     
    if event == 'OpenListWorker':
        window.Element('layoutEventsWorker').Update(visible=True)
        window.Element('worker').Update(visible=False)
    if event == 'Назад7':
        window.Element('layoutEventsWorker').Update(visible=False)
        window.Element('worker').Update(visible=True)  
    if event == 'AddEventEmpl':
        if values['NameEventEmpl'] != '' and values['DateEventEmpl'] != '':
            AddEvent(status='employer', name=values['NameEventEmpl'], date=values['DateEventEmpl'], login=window.Element('LoginAccEmpl').get())
            window.Element('check').Update('')
        else:
            window.Element('check').Update('Some inputs are empty')
        window.Element('NameEventEmpl').Update('')
        window.Element('DateEventEmpl').Update('')
    if event == 'AddEventWorker':
        if values['NameEventWorker'] != '' and values['DateEventWorker'] != '':
            AddEvent(status='worker', name=values['NameEventWorker'], date=values['DateEventWorker'], login=window.Element('LoginAccWorker').get())
            window.Element('check').Update('')
        else:
            window.Element('check').Update('Some inputs are empty')
        window.Element('NameEventWorker').Update('')
        window.Element('DateEventWorker').Update('')
    if event == 'CreateReport':
        window.Element('worker').Update(visible=False)
        window.Element('layoutReportWorker').Update(visible=True)
    if event == 'Back8':
        window.Element('worker').Update(visible=True)
        window.Element('layoutReportWorker').Update(visible=False)
    if event == 'AddReportWorker':
        with conn.cursor() as curs:
            curs.execute(f'''select worker_id from worker where worker_login = '{window.Element('LoginAccWorker').get()}' ''')
            data = curs.fetchone()
            if values['nameReportWorker'] != '' and values['textReportWorker'] != '':
                functions.CreateReport(id_worker=data[0], name=values['nameReportWorker'], body=values['textReportWorker'])
                window.Element('check').Update('')
            else:
                window.Element('check').Update('Some inputs are empty')
        window.Element('nameReportWorker').Update('')
        window.Element('textReportWorker').Update('')
    if event == 'CheckReport':
        with conn.cursor() as curs:
            curs.execute(f'''select * from work where worker_id = (select worker_id from worker where worker_name = '{window.Element('list').get()[0]}')''')
            data = curs.fetchall()
            print(data[-1])
        print(window.Element('list').get())
        window.Element('NameOfCheckingReport').Update(data[-1][1])
        window.Element('layoutCheckReport').Update(visible=True)
        window.Element('employer').Update(visible=False)
    if event == 'Verdict2':
        print(window.Element('NameOfCheckingReport').get())
        if values['answ1']:
            with conn.cursor() as curs:
                curs.execute(f'''UPDATE work
                                    SET work_status = 'Да', work_comment = '{values['CommentReport']}'
                                    WHERE work_name = '{window.Element('NameOfCheckingReport').get()}' ''')
                conn.commit()
        elif values['answ2']:
            with conn.cursor() as curs:
                curs.execute(f'''UPDATE work
                                    SET work_status = 'Нет', work_comment = '{values['CommentReport']}'
                                    WHERE work_name = '{window.Element('NameOfCheckingReport').get()}' ''')
                conn.commit()
        window.Element('CommentReport').Update('')
        window.Element('Finish').Update(visible=False)
        window.Element('answ1').Update(visible=False)
        window.Element('answ2').Update(visible=False)
        window.Element('CommentTextReport').Update(visible=False)
        window.Element('CommentReport').Update(visible=False)
        window.Element('Verdict').Update(visible=True)
        window.Element('Verdict2').Update(visible=False)
        window.Element('Cancel2').Update(visible=False)
    if event == 'Back9':
        window.Element('layoutCheckReport').Update(visible=False)
        window.Element('employer').Update(visible=True)
    if event == 'Download PDF':
        data = functions.get_data_from_db(window.Element('NameOfCheckingReport').get())
        
        table = []
        table.append(('Name of Report', 'Content of Report'))
        table.append((data[0]))
        print(table)
        print(data)
        # Генерация PDF
        pdf_bytes = functions.generate_pdf(table)
        # Сохранение PDF в файл
        file_path = sg.popup_get_file("Сохранить PDF как:", save_as=True, file_types=(("PDF Files", "*.pdf"),))
        if file_path:  # Если пользователь выбрал путь для сохранения
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
            sg.popup("PDF успешно сохранен")
    if event == 'Verdict':
    #     [sg.Button('Изменить статус работы', font= 'Courier 16', key = 'Verdict')],
    # [sg.Text('Работа завершена?', font='Courier 16', visible=False), sg.Radio('Да', "answ", key = 'answ1', visible=False), sg.Radio('Нет', "answ", key = 'answ2', visible=False)],
    # [sg.Text('Комментарий: ', font='Courier 16', visible=False), sg.Input('', key = 'CommentReport', font='Courier 16', visible=False)]
    # [sg.Button('Внести изменения', font='Courier 16', visible=False), sg.Button('Отменить', font='Courier 16', visible=False), sg.Button('Назад', font = 'Courier 16', key = 'Back9')]
        window.Element('Verdict').Update(visible=False)
        window.Element('Finish').Update(visible=True)
        window.Element('answ1').Update(visible=True)
        window.Element('answ2').Update(visible=True)
        window.Element('CommentTextReport').Update(visible=True)
        window.Element('CommentReport').Update(visible=True)
        window.Element('Verdict2').Update(visible=True)
        window.Element('Cancel2').Update(visible=True)
    if event == 'Cancel2':
        window.Element('Finish').Update(visible=False)
        window.Element('answ1').Update(visible=False)
        window.Element('answ2').Update(visible=False)
        window.Element('CommentTextReport').Update(visible=False)
        window.Element('CommentReport').Update(visible=False)
        window.Element('Verdict').Update(visible=True)
        window.Element('Verdict2').Update(visible=False)
        window.Element('Cancel2').Update(visible=False)
    if event == 'lastReport':
        with conn.cursor() as curs:
            curs.execute(f'''Select * from work where worker_id = (select worker_id from worker where worker_login = '{window.Element('LoginAccWorker').get()}')''')
            data = curs.fetchall()
        print(data[-1])
        window.Element('NameLastReport').Update(data[-1][1])
        if data[-1][3] == 'Да':
            window.Element('StatusWork').Update('Принято')
        if data[-1][3] == 'Нет':
            window.Element('StatusWork').Update('Не принято')
        window.Element('CommentWork').Update(data[-1][4])
        window.Element('layoutLastReport').Update(visible=True)
        window.Element('layoutReportWorker').Update(visible=False)
    if event == 'Back10':
        window.Element('layoutLastReport').Update(visible=False)
        window.Element('layoutReportWorker').Update(visible=True)
    if event == 'Я - работник':
        window.Element('employer').Update(visible = False)
        window.Element('worker').Update(visible = True)
        window.Element('buttons').Update(visible = False)
        window.Element('registration').Update(visible = False)
    if event == 'Регистрация':
        window.Element('employer').Update(visible = False)
        window.Element('worker').Update(visible = False)
        window.Element('buttons').Update(visible = False)
        window.Element('registration').Update(visible = True)
    if event == 'DeleteEventWorker':
        with conn.cursor() as curs:
            print(window.Element('listEventsWorker').get()[0][0:-12])
            curs.execute(f'''delete from event where event_name = '{window.Element('listEventsWorker').get()[0][0:-12]}' ''')
            conn.commit()
            ShowEvents(status='worker', login=values['Login1'])
        window.Element('NameEventWorker').Update('')
        window.Element('DateEventWorker').Update('')
    if event == 'DeleteEventEmpl':
        with conn.cursor() as curs:
            print(window.Element('listEventsEmpl').get()[0][0:-12])
            curs.execute(f'''delete from event where event_name = '{window.Element('listEventsEmpl').get()[0][0:-12]}' ''')
            conn.commit()
            ShowEvents(status='employer', login=values['Login1'])
        window.Element('NameEventEmpl').Update('')
        window.Element('DateEventEmpl').Update('')
    if event == 'Вход2':
        print('Hello')
        print(values['Login2'], values['Password2'])
        with conn.cursor() as curs:
            curs.execute(f'''SELECT * FROM 
                    (SELECT 'таблица1' AS Таблица, 
                        CASE WHEN EXISTS (SELECT * FROM employer WHERE employer_login = '{values['Login2']}') THEN 'true' ELSE 'false' END as содержание_найдено
                        UNION ALL
                        SELECT 'таблица2' AS Таблица, 
                        CASE WHEN EXISTS (SELECT * FROM worker WHERE worker_login = '{values['Login2']}') THEN 'true' ELSE 'false' END as содержание_найдено
                    ) AS subquery''')
            data = curs.fetchall()
            if data[0][1] == 'true' or data[1][1] == 'true':
                window.Element('check').Update('This user already exist')
            elif values['Login2'] != '' and values['Password2'] != '' and values['Company'] != '' and (values['employer1'] or values['worker1']):
                window.Element('check').Update('Registration successfully complete')
                if values['employer1']:
                    with conn.cursor() as curs:
                        curs.execute('''select count(*) from employer''')
                        data = curs.fetchone()
                        curs.execute('''
                        INSERT INTO employer (employer_id, employer_login, employer_name, employer_password, employer_company) 
                        VALUES (%s, %s, %s, %s, %s);
                        ''',
                        (data[0]+1, values['Login2'], values['FName'], values['Password2'], values['Company']))
                        conn.commit()
                        window.Element('check').Update('')
                        window.Element('registration').Update(visible=False)
                        window.Element('buttons').Update(visible=True)
                        window.Element('Login2').Update('')
                        window.Element('FName').Update('')
                        window.Element('Password2').Update('')
                        window.Element('Company').Update('')
                else:
                    with conn.cursor() as curs:
                        curs.execute('''select count(*) from worker''')
                        data = curs.fetchone()
                        curs.execute(f'''select * from employer where employer_company = '{values['Company']}' ''')
                        data1 = curs.fetchone()
                        if data1 is not None:
                            curs.execute('''
                                INSERT INTO worker (worker_id, worker_login, worker_name, worker_password, worker_company, employer_id) 
                                VALUES (%s, %s, %s, %s, %s, %s);
                            ''',
                        (data[0]+1, values['Login2'], values['FName'], values['Password2'], values['Company'], data1[0]))
                            conn.commit()
                            window.Element('Login2').Update('')
                            window.Element('FName').Update('')
                            window.Element('Password2').Update('')
                            window.Element('Company').Update('')
                            window.Element('check').Update('')
                            window.Element('registration').Update(visible=False)
                            window.Element('buttons').Update(visible=True)
                        else:
                            curs.execute('''
                                INSERT INTO worker (worker_id, worker_login, worker_name, worker_password, worker_company) 
                                VALUES (%s, %s, %s, %s, %s);
                            ''',
                        (data[0]+1, values['Login2'], values['FName'], values['Password2'], values['Company']))
                            conn.commit()
                            window.Element('Login2').Update('')
                            window.Element('Password2').Update('')
                            window.Element('FName').Update('')
                            window.Element('Company').Update('')
                            window.Element('check').Update('')
                            window.Element('registration').Update(visible=False)
                            window.Element('buttons').Update(visible=True)
            else:
                window.Element('check').Update('Some inputs are empty')
    if event == 'TurnOn':
        window.Element('statusBlock').Update('Включен')
        robot.close_browser()
        robot.start()
        limiter.killlife()
    if event == 'TurnOff':
        window.Element('statusBlock').Update('Выключен')
        limiter.stop()
        robot.stop()
    if event == 'Назад1' or event == 'Назад2' or event == 'Назад3':
        information_array.clear()
        window.Element('list').Update(values=information_array)
        window.Element('worker').Update(visible = False)
        window.Element('employer').Update(visible = False)
        window.Element('buttons').Update(visible = True)
        window.Element('registration').Update(visible = False)
        window.Element('employerProfile').Update(visible = False)
        window.Element('workerProfile').Update(visible = False)
        window.Element('Login1').Update('')
        window.Element('Password1').Update('')
        window.Element('check').Update('')
    # elif event == 'Calculate Difference':
    #     difference = arrival_departure_difference(values['-DEPARTURE-'], values['-ARRIVAL-'])
    #     print(difference)
    #     window['-TIME_DIFFERENCE-'].update(difference)


window.close()