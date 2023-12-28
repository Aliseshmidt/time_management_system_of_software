from datetime import datetime
import select
import psycopg2
from io import BytesIO
import csv, os
from reportlab.lib import colors
import PySimpleGUI as sg
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
layoutMain= []
information_array = []
conn = psycopg2.connect(dbname='Authentication', user='postgres', password=' ')
window = sg.Window('Window Title',  layoutMain, size = (1000, 600), resizable = True, element_justification = 'center')
def get_data_from_db(worker_id):
    # Здесь ваш запрос PostgreSQL
    with conn.cursor() as curs:
        curs.execute(f'''SELECT work_name, work_report FROM work where work_name = '{worker_id}' ''')
        data = curs.fetchall()
    return data

def generate_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                              ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                              ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                              ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                              ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                              ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                              ('GRID', (0, 0), (-1, -1), 1, colors.black)
                              ]))
    doc.build([table])

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# This is to make sure that the arrival date is not before the departure date
def is_arrival_before_departure(departure_string, arrival_string):
    # 2021-08-01 13:09:43
    departure_object = datetime.strptime(departure_string, '%Y-%m-%d %H:%M:%S')
    arrival_object = datetime.strptime(arrival_string, '%Y-%m-%d %H:%M:%S')
    return arrival_object < departure_object

# This is to make sure that the arrival date is not before the departure date
def arrival_departure_difference(departure_string, arrival_string):
    # 2021-08-01 13:09:43
    departure_object = datetime.strptime(departure_string, '%Y-%m-%d %H:%M:%S')
    arrival_object = datetime.strptime(arrival_string, '%Y-%m-%d %H:%M:%S')
    return arrival_object - departure_object

    

def FindInfoAboutHuman(status, login):
    with conn.cursor() as curs:
        curs.execute(f'''select * from {status} where {status}_login = '{login}' ''')
        return curs.fetchall()


def SaveChagesProfile(status, login, name, password, company):
    with conn.cursor() as curs:
        if name != '':
            print (name)
            curs.execute(f'''UPDATE {status}
                            SET {status}_name = '{name}'
                            WHERE {status}_login = '{login}' ''')
        if password != '':
            curs.execute(f'''UPDATE {status}
                            SET {status}_password = '{password}'
                            WHERE {status}_login = '{login}' ''')
        if company != '':
            if status == 'employer':
                curs.execute(f'''select employer_id from employer where employer_login = '{login}' ''')
                id = curs.fetchone()
                print(id[0])
                curs.execute(f'''select * from worker where employer_id = {id[0]} ''')
                all_workers = curs.fetchall()
                if all_workers is not None:
                    for worker in all_workers:
                        curs.execute(f'''UPDATE worker
                                    SET employer_id = null
                                    WHERE worker_id = {worker[0]} ''')
                curs.execute(f'''select * from worker where worker_company = '{company}' ''')
                all_workers = curs.fetchall()
                if all_workers is not None:
                    for worker in all_workers:
                        curs.execute(f'''UPDATE worker
                                    SET employer_id = {id[0]}
                                    WHERE worker_id = {worker[0]} ''')
                curs.execute(f'''UPDATE {status}
                                SET {status}_company = '{company}'
                                WHERE {status}_login = '{login}' ''')
            if status == 'worker':
                curs.execute(f'''select employer_id from employer where employer_company = '{company}' ''')
                id = curs.fetchone()
                if id is not None:
                    curs.execute(f'''UPDATE worker
                                SET employer_id = id
                                WHERE worker_login = '{login}' ''')
                else:
                    curs.execute(f'''UPDATE worker
                                SET employer_id = null
                                WHERE worker_login = '{login}' ''')
                curs.execute(f'''UPDATE {status}
                                SET {status}_company = '{company}'
                                WHERE {status}_login = '{login}' ''')
        conn.commit()
 

def CreateReport(id_worker, name, body):
    with conn.cursor() as curs:
        curs.execute('select count(*) from work')
        data = curs.fetchone()
        print(data[0])
        curs.execute(f'''insert into work (work_id, work_name, work_report, worker_id) VALUES ({data[0]+1}, '{name}', '{body}', {id_worker})''')
        conn.commit()
        
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