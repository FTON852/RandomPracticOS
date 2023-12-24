class FileSystem:
    def __init__(self, block_count=2, block_size=512, symbol_size=3):
        self.block_count = block_count  # количество блоков памяти
        self.block_size = block_size * 8  # размер блока в битах
        self.symbol_size = symbol_size * 8  # размер одного символа в битах
        self.converter = Converter()  # класс который позволяет конвертить текст в биты (тело класса описано ниже)
        self.files = dict()  # {'file1.txt': [[[0 - номер блока, [0, 79] - диапозон ячеек в блоке занятыми памяти], [1, [0, 79]], [2, [0, 79]], [3, [0, 38]]], 275 - размер файла в битах]}
        self.free_space = {f"block{i}": [[0, self.block_size - 1]] for i in
                           range(self.block_count)}  # словарь (хеш таблица) с информацией о загрузке каждого блока
        self.free_space_bytes = self.block_size * self.block_count  # количествно свободной памяти
        self.memory = [[[0] for i in range(self.block_size)] for k in range(
            self.block_count)]  # реализация памяти через 3 вложеных списка, где 1 список оболочка всей памяти, 2 список блок памяти, 3 ячейка памяти равная 1 биту

    # метод обновляющий информацию о состоянии памяти
    def refresh(self):
        for key, values in self.free_space.items():  # получаем ключи и значения в переменные из словаря
            values.sort()  # сортируем масссивы по возрастанию в словаре с информацией о каждом блоке
        for i in range(self.block_count):
            block = self.free_space[f"block{i}"]  # выбираем блок памяти
            last = [-1,
                    -1]  # буфферная переменная хранящая в себе диапозон свободных ячеек (при иницилизации имеет не возможно значение для работы условия из нижнего цикла)
            for item in block:  # цикл проходящий по ячейкам памяти в каждом блоке
                if last[1] == item[
                    0]:  # условие проверяющие что прошлый сегмент блока заканчивается там где начинается следующий
                    block.remove(last)  # удаляем прошлый сегмент памяти
                    item[0] = last[
                        0]  # назначаем диапозону новое начально значение равное значанию начала прошлого диапозона
                else:
                    last = item  # если условие не выполняется обновляем переменную last на новый диапозон

    # метод переремещающий файл в нужный блок в памяти
    def move(self, file_name, block_num):
        parts = self.files[file_name][0]  # получаем инормацию о местоположению файла в блоках
        text_byte = []  # переменная хранящая в себе текст файла
        for part in parts:  # проходимся по частям файла
            text_byte += self.memory[part[0]][part[1][0]:part[1][1]]  # собираем файл во едино
        iter = 0  # переменная для интераций
        text = []  # буферная переменная для  хранения преобразованного текста
        letter = []  # буферная переменная для сивола из битов
        for byte in text_byte:
            if iter >= self.symbol_size: # проверка является ли ципочка битов символом или это
                for i in byte:
                    letter.append(i) # добавляем бит в буферную переменную
                text += letter # добавляем символ к тексту
                letter = [] # обнуляем переменую для следующей последу
                iter = 0 # обнуляем переменую итерации
            else:
                iter += 1
                for i in byte:
                    letter.append(i)
        bytes = text #
        file_size = len(text) #получаем количество битов в файле нужно для выделения участков памяти
        self.remove(file_name) # удаляем файл (участки памяти обнуляются)
        file_parts = list() # буфер для хранения частей файла
        if self.free_space_bytes - file_size > 0: # проверяем можем ли мы производить запись
            i = 0 # переменная для интераций
            while i <= file_size - 1 and block_num < self.block_count: # проверка в цикле на возможности записи (не кончились ли блоки памяти) и прохода по битам файла
                block = self.free_space[f"block{block_num}"] # берем блок памяти
                if len(block) > 0: # проверяем есть ли свободные ячейки
                    for cells in block: # проходимся по диапозонам ячеек в буфере
                        start, end = cells[0], cells[1] # берем начало диапозона свободных ячеек и конец
                        part = [start] # создаем буферную переменную которая будет хранить части ячеек в которых лежит чатси файла
                        while start < end and i <= file_size - 1: # проходимся по свободным ячейкам и записываем в них части файла
                            self.memory[block_num][start][0] = bytes[i] # запись в память
                            i += 1 # флаг итерации записи
                            start += 1 # шаг в ячейках
                        if start == end: # если место кончилось в блоке удаляем диапозон из свободных ячеек блока
                            block.remove(cells)
                        else:
                            cells[0], cells[1] = start, end # если место осталось изменяем границы свободных ячеев в блоке
                        part.append(start) # сохраняем последнюю ячейку в буферную переменную обявленую выше
                        final_parts = [block_num, part] # сохраняем информацию в каком блоке и в каком диапозоне ячеек находится части файла
                        file_parts.append(final_parts) # добовляем в список переменую выше ибо части файла божет быть на разных блоках
                block_num += 1 # переходим к следующему блоку
            self.free_space_bytes -= file_size # уменьшаем свободную память
            self.files[file_name] = [file_parts, file_size] # добавляем информацию о файле в систему
            self.refresh() # проверям память

        else:
            return "Out of Memory"

    # метод позволяющий переименовать файл
    def rename(self, file_name, new_name):
        self.files[new_name] = self.files.pop(file_name) # меняем название файла в хэш таблице с файлмаи

    # метод копирующий файл
    def copy_file(self, file_name, new_name=False):
        if not new_name: # проверяем есть ли файл с таким названием
            new_name = file_name.replace(".txt", "") + "_copy.txt" # добавляем приписку что это копия
        file_parts = list() # буферная переменная для хранения частей файла (диапозонов ячеек в блоках)
        parts = self.files[file_name][0] # получаем в каких ячейках и блоках храниться файл
        text_byte = [] # буферная переменная для хранения битов текста
        for part in parts: # проходимся по частям
            text_byte += self.memory[part[0]][part[1][0]:part[1][1]] # считываем файл из памяти
        iter = 0 # перменная для цикла
        text = [] # буфер для хранения текста
        letter = [] # буфер для хранения символа
        for byte in text_byte:
            if iter >= self.symbol_size: # если набираются биты до размера символа
                for i in byte:
                    letter.append(i) # записываем биты в переменную для символа
                text += letter # добавляем символ к тексту
                letter = [] # обнуляем переменную с символом
                iter = 0 # обнуляем переменную
            else:
                iter += 1  # добавляем итерацию
                for i in byte: # добавляем биты к символу
                    letter.append(i)
        bytes = text # схожий код был рассмотрен выше
        file_size = len(text)
        if self.free_space_bytes - file_size > 0:
            i = 0
            block_num = 0
            while i <= file_size - 1 and block_num < self.block_count:
                block = self.free_space[f"block{block_num}"]
                if len(block) > 0:
                    for cells in block:
                        start, end = cells[0], cells[1]
                        part = [start]
                        while start < end and i <= file_size - 1:
                            self.memory[block_num][start][0] = bytes[i]
                            i += 1
                            start += 1
                        if start == end:
                            block.remove(cells)
                        else:
                            cells[0], cells[1] = start, end
                        part.append(start)
                        final_parts = [block_num, part]
                        file_parts.append(final_parts)

                block_num += 1
            self.free_space_bytes -= file_size
            self.files[new_name] = [file_parts, file_size]
            self.refresh()
        else:
            return "Out of Memory"

    # метод записи в программу
    def write(self, file_name, file): # схожий код был рассмотрен выше
        file_parts = list()
        bytes = self.converter.get_binary(file)
        file_size = len(bytes)
        write_flag = True
        if file_name in self.files:
            print(f"File: {file_name} already exist")
            answ = input(f"Rewrite it? (Yes/No) (y/n):")
            if answ.lower() == "yes" or answ.lower() == "y":
                self.remove(file_name)
            else:
                return None
        if self.free_space_bytes - file_size > 0:
            i = 0
            block_num = 0
            while i <= file_size - 1 and block_num < self.block_count:
                block = self.free_space[f"block{block_num}"]
                if len(block) > 0:
                    for cells in block:
                        start, end = cells[0], cells[1]
                        part = [start]
                        while start < end and i <= file_size - 1:
                            self.memory[block_num][start][0] = bytes[i]
                            i += 1
                            start += 1
                        if start == end:
                            block.remove(cells)
                        else:
                            cells[0], cells[1] = start, end
                        part.append(start)
                        final_parts = [block_num, part]
                        file_parts.append(final_parts)

                block_num += 1
            self.free_space_bytes -= file_size
            self.files[file_name] = [file_parts, file_size]
            self.refresh()
        else:
            return "Out of Memory"

    # метод чтения в программе
    def read(self, file_name):
        parts = self.files[file_name][0] # берем информацию в каких блоках и ячейках хранится файл
        text_byte = [] # буферная переменная
        for part in parts:
            text_byte += self.memory[part[0]][part[1][0]:part[1][1]] # читаем из памяти файл
        iter = 0
        text = ""
        letter = []
        for byte in text_byte: # прохожимся по битам
            if iter >= self.symbol_size: # схолжий код был рассмотрен выше
                for i in byte:
                    letter.append(i)
                text += chr(int("".join(str(x) for x in letter), 2)) # преобразуем биты в 10 ое число затем конвертим в символ
                letter = []
                iter = 0
            else:
                iter += 1
                for i in byte:
                    letter.append(i)
        return text
    # метод по удалению файла
    def remove(self, file_name):
        parts = self.files[file_name][0]  # берем информацию где лежат части файла
        for part in parts:
            block = self.memory[part[0]] # схожая часть кода была рассмотрена выше
            start = part[1][0]
            end = part[1][1]
            while start < end:
                block[start] = [0] # чистим ячейки
                start += 1
            self.free_space[f"block{part[0]}"].append([part[1][0], end]) # добавляем свободный сегмент памяти
        self.free_space_bytes += self.files[file_name][1] # добавляем очищенную память
        self.refresh() # обновляем данные


# Класс конвертирующий в биты текст
class Converter:
    def get_binary(self, text):
        bytes = []
        for i in text:
            byte = bin(ord(i))[2:] # превращаем символ в код из кодировки и конвертим в биты
            while len(byte) <= 24: # наращиваем размер символа до нужного количеств битов в системе (24 бита = 3 байта)
                byte = "0" + byte
            for i in byte:
                bytes.append(int(i))
        return bytes


# Класс реализующий методы для задания
class SimpleUI:
    def __init__(self):
        self.system = FileSystem()

    def write_from_file_on_pc(self, file_name="file1.txt"):
        with open("input/" + file_name, "r") as file: # открываем файл из папки
            text = "".join(file.readlines()) # читаем файл
            self.system.write(file_name, text) # записываем файл в нашу систему

    def write_into_file_on_pc(self, text, file_name="output.txt"):
        with open("output/" + file_name, "w") as file: # открываем файл из папки
            file.writelines(text) # записываем файл в доманшнюю систему

    # Задание с подсчетом буквенных символов
    def count_letters(self):
        self.write_from_file_on_pc() # считываем первый файл и запиываем в нашу систему
        self.write_from_file_on_pc("file2.txt") # считываем 2 файл и запиываем в нашу систему
        count = 0 # счетчик
        string = self.system.read("file1.txt") # читаем файл из нашей системы
        for char in string:
            if char.isalpha(): # проверяем является ли символ буквой
                count += 1
        string = self.system.read("file2.txt")  # читаем файл из нашей системы
        for char in string:
            if char.isalpha():# проверяем является ли символ буквой
                count += 1
        self.write_into_file_on_pc(str(count), "output1.txt") # пишем результат в файл

    def count_numbers(self):
        self.write_from_file_on_pc()
        self.write_from_file_on_pc("file2.txt")
        count = 0
        string = self.system.read("file1.txt") # читаем файл из нашей системы
        for char in string:
            if char.isnumeric(): # проверяем является ли символ цифрой
                count += 1
        string = self.system.read("file2.txt") # читаем файл из нашей системы
        for char in string:
            if char.isnumeric(): # проверяем является ли символ цифрой
                count += 1
        self.write_into_file_on_pc(str(count), "output2.txt") # пишем результат в файл

    def get_info(self):  # метод выводящий онформацию о памяти
        print("Память:")
        print(self.system.memory)
        print("Доступно памяти в каждом блоке (0-n число свободно бит):")
        print(self.system.free_space)
        print("Доступно памяти в битах:")
        print(self.system.free_space_bytes)
        print("Файлы в памяти:")
        print(self.system.files)


prak5 = SimpleUI()
prak5.write_from_file_on_pc()

prak5.get_info()
# Выполнение задания 1
prak5.count_letters()
prak5.get_info()
# Выполнение задания 2
prak5.count_numbers()
prak5.get_info()
