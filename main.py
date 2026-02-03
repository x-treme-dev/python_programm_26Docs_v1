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
text = ''

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
    ["Постановление о временном ограничении на выезд", "ПОСТ_об_врем_огран_на_выезд"],
    ["Постановление об обращении взыскания на денежные средства", "ПОСТ_об_обращ_взыскан_на_ден_средства"],
    ["Постановление об объединении ИП", "ПОСТ_об_объед_ИП"],
    ["Постановление о снятии ареста", "ПОСТ_о_снятии_ареста"],
    ["Постановление об отмене постановления", "ПОСТ_об_отмене_пост"],
    ["ИЗВЕЩЕНИЕ", "ИЗВЕЩЕНИЕ"]
]



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

def clean_string(s):
    # Удаляет все символы, кроме букв, цифр и пробелов
    s = re.sub(r'[^A-Za-zА-Яа-я0-9\s]', '', s)
    # Удаляет лишние пробелы и переводит в нижний регистр
    s = re.sub(r'\s+', ' ', s).strip()
    return s      
    
       

def extract_sudebny_prikaz(text):
    # Ищем вариации 'Судебный приказ' или 'c судебным приказом'
    pattern = r'(Судебный приказ|судебный приказ|c судебным приказом|по делу)(.*?)(выданный органом|,|предмет исполнения|,|вступившему в законную силу)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        # Берем все символы между найденными фразами
        part = match.group(2).strip()
        # Удаляем переносы строк, табуляции, запятые и кириллические символы
        part = re.sub(r'[\n\r\t,(4\),а-яА-Я]', '', part).strip().replace(' ', '_')
        return part
    return None

def sanitize_filename(name):
    # Заменяем недопустимые символы на _
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    # Удаляем управляющие символы, например, переносы строк
    name = re.sub(r'[\n\r\t]', '', name)
    # Убираем лишние пробелы
    name = name.strip()
    # Удаляем запятую, если она есть в конце
    name = re.sub(r',\s*$', '', name)
    # Удаляем нижнее подчеркивание и ноль, если они идут в конце
    name = re.sub(r'(_0)$', '', name)
    return name


# Сформировать строку с именем и переименовать найденный файл при условии совпадения со словарем
def rename_files(path_target, search_str, cat_string):
    new_path = None
    print(f'Обход директории: {path_target}')
    for root, dirs, files in os.walk(path_target):
        for filename in files:
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'rb') as f:
                        reader = PdfReader(f)
                        text_found = False
                        for page in reader.pages:
                            text = page.extract_text()
                            if text and search_str.lower() in text.lower():
                                #print(f"clean_string={clean_string(search_str.lower())}, clean_string(text.lower()) {clean_string(text.lower())}")
        
                                sudebny_prikaz = extract_sudebny_prikaz(text) or ''
                                new_name = sanitize_filename(cat_string + '_' + sudebny_prikaz + '.pdf') 
                                new_path = os.path.join(os.path.split(file_path)[0], new_name)
                                text_found = True
                                break
                    if new_path and not os.path.exists(new_path):
                        os.rename(file_path, new_path)
                        print(f'Переименовано: {new_path}')
                except Exception as e:
                    print(f"Ошибка при чтении файла {filename}: {e}")

                             
                       
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

 
    

