import os
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import shutil
from PyPDF2 import PdfReader
import re
import hashlib
import random
import PyPDF2
from pathlib import Path

#path_source = ''
#path_target = ''

path_source = 'C:\\Users\\user\\WORK\\WorkingProjects\\Michaylov\\files_for_sorting' #del
path_target = 'C:\\Users\\user\\WORK\\WorkingProjects\\Michaylov\\ResultsProgram'  #del
path_target_list = []

params = [
    ["ОСП по Киевскому району г. Симферополя", "Отделение судебных приставов по Киевскому району г. Симферополя", "Киевский_ОСП"],
    ["ОСП по Железнодорожному району г. Симферополя", "Отделение судебных приставов по Железнодорожному району г. Симферополя", "Ж_д_ОСП"],
    ["ОСП по Симферопольскому району г. Симферополя", "Отделение судебных приставов по Симферопольскому району г. Симферополя", "Симф_р-н_ОСП"],
    ["ОСП по Центральному району г. Симферополя", "Отделение судебных приставов по Центральному району г. Симферополя", "Центральный_ОСП"]
]

search_strings = [
    ["Постановление о возбуждении исполнительного производства", "ПОСТ_о_возб"],
    ["Постановление об окончании исполнительного производства", "ПОСТ_об_оконч"],
    ["Постановление об окончании и возвращении ИД взыскателю", "ПОСТ об оконч и возвр ИД"],
    ["Постановление об временном ограничении на выезд", "ПОСТ_об_врем_огран_на_выезд"],
    ["Постановление об обращении взыскания на денежные средства", "ПОСТ_об_обращ_взыскан_на_ден_средства"],
    ["Постановление об объединении ИП", "ПОСТ_об_объед_ИП"],
    ["Постановление о снятии ареста", "ПОСТ_о_снятии_ареста"],
    ["Постановление об отмене постановления", "ПОСТ_об_отмене_пост"],
    ["ИЗВЕЩЕНИЕ о возвращении исполнительного документа в орган", "ИЗВЕЩЕНИЕ"]
]

prikaz_pattern = r'(Судебный приказ|судебный приказ|c судебным приказом|по делу)(.*?)(выданный органом|,|предмет исполнения)'



def finish():
    root.destroy()
    print("Closing app")

def get_directory(param):
    path = filedialog.askdirectory()
    cat_path = path.rsplit('/', 1)[-1]
    global path_source
    global path_target
   
    if path and param == 'source':
        # Обновляем текст метки
        lb_source.config(text=cat_path)
        print(f"Выбранная папка: {path}")
        path_source = path
    elif path and param == 'target':
        # Обновляем текст метки
        lb_target.config(text=cat_path)
        print(f"Выбранная папка: {path}")
        path_target = path
    elif path == '' and param == 'source':
        lb_source.config(text='Выбор отменен!')
        print("Выбор отменен")
    elif path == '' and param == 'target':
        lb_target.config(text='Выбор отменен!')
        print("Выбор отменен")


def check_values(path_source, path_target):
    if path_source == '' or path_target == '':
        lb_message.config(text = 'Недостаточно данных поиска!')
        print('Недостаточно данных для поиска!')
    else:
       #find_files(path_source)
        
        for p in params:
            copy_files(path_source, path_target, *p)
        # rename after sorting
        global f_str
        for s in search_strings:
            rename_files(path_target, *s)

def copy_files(path_source, path_target, search_str1, search_str2, folder_name):
    #временная директория для скопированных файлов
    global path_target_list
    new_path_temp = os.path.join(path_target, folder_name)
   
    path_target_list.append(new_path_temp)
    os.makedirs(new_path_temp, exist_ok=True)
    for root, dirs, files in os.walk(path_source):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                try:
                        reader = PdfReader(full_path)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() or ""
                        if search_str1 in text or search_str2 in text:
                            shutil.copy2(full_path, new_path_temp)
                            print(f"Файл скопирован: {full_path} -> {new_path_temp}")
                except Exception as e:
                        print(f"Ошибка при обработке файла {full_path}: {e}")
        lb_message.configure(text='Файлы отсортированы!')

'''
    for item in path_target_list:
        print(f'path_target_list is {item}')
'''      
   
def remove_dir_temp(path_target_list):
    if path_target_list:
        for item in path_target_list:
            try:
                shutil.rmtree(item)
                print(f"Директория {item} успешно удалена.")
                lb_message.configure(text='Файлы удалены!')
            except Exception as e:
                print(f"Не удалось удалить директорию {dir_temp}. Ошибка: {e}")
                lb_message.configure(text='Файлы уже удалены!')
    else:
        lb_message.configure(text='Нет файлов для удаления!')
        

def extract_sudebny_prikaz(text):
    # Ищем вариации 'Судебный приказ' или 'c судебным приказом'
    pattern = r'(Судебный приказ|судебный приказ|c судебным приказом|по делу)(.*?)(выданный органом|,|предмет исполнения)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        # Берем все символы между найденными фразами
        part = match.group(2).strip()
        # Удаляем переносы строк, табуляции, запятые и кириллические символы
        part = re.sub(r'[\n\r\t,а-яА-Я]', '', part).strip()
        return part
    return None


def find_string_in_pdf(pdf_path, search_string, cat_string):
    #прочитать файл по-странично, получить текст
    try:
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and search_string in text:
                return True
        return False
    except Exception as e:
        print(f"Ошибка при чтении файла {pdf_path}: {e}")
        return False

def rename_files(path_target, search_str, cat_string):
    form_path_target = Path(path_target)
    #найти в указанной директории файлы с совпадениями
    for root, dirs, files in os.walk(path_target):
        for file in files:
            if file.lower().endswith('.pdf'):
                #получить абсолютный путь к файлу
                pdf_path = os.path.join(root, file)
                if find_string_in_pdf(pdf_path, search_str, cat_string):
                    print(f"Найдено в файле: {pdf_path}")
   
    
        
    
 
################# interface ##########################################################           
# Создаем главное окно
root = Tk()
root.title("26Docs")
root.geometry("600x350+500+200")
root.update_idletasks()


style = ttk.Style()
style.configure('.', font=('Courier New', 22))


# Назначаем обработчик закрытия окна
root.protocol("WM_DELETE_WINDOW", finish)

# Создаем интерфейс
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Откуда взять файлы?
ttk.Label(mainframe, text="Откуда взять файлы?").grid(column=1, row=1, sticky=W)
ttk.Button(mainframe, text='Выбрать', command=lambda:get_directory('source')).grid(column=2, row=1, columnspan=2, sticky=(W,E))
ttk.Label(mainframe, text="Выбранная папка: ").grid(column=1, row=2, sticky=W)
lb_source = ttk.Label(mainframe, text="нет данных...")
lb_source.grid(column=2, row=2, sticky=W)

# Куда положить файлы?
ttk.Label(mainframe, text="Куда положить файлы?").grid(column=1, row=3, sticky=W)
ttk.Button(mainframe, text='Выбрать', command=lambda:get_directory('target')).grid(column=2, row=3,columnspan=2,  sticky=(W,E))
ttk.Label(mainframe, text="Выбранная папка: ").grid(column=1, row=4, sticky=W)
lb_target = ttk.Label(mainframe, text="нет данных...")
lb_target.grid(column=2, row=4, sticky=W)


mainframe.grid_columnconfigure(1, weight=1)
mainframe.grid_columnconfigure(2, weight=1)
ttk.Button(mainframe, text='Сортировать', command=lambda:check_values(path_source, path_target)).grid(column=1, row=5, columnspan=2, sticky=(W, E))
lb_message = ttk.Label(mainframe, text='')
lb_message.grid(column=1, row=6, columnspan=2, sticky=(W, E))
ttk.Button(mainframe, text='Удалить исходные файлы', command=lambda:remove_dir_temp(path_target_list)).grid(column=1, row=7, columnspan=2, sticky=(W, E))
 

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Обработчик закрытия окна
root.protocol("WM_DELETE_WINDOW", finish)


root.mainloop()

 
    

