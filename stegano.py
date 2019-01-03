# -*- coding: utf-8 -*-

# python stegano.py -c container.txt -m stego_message.txt -k somekey
# python stegano.py -c stego_container.txt -k somekey

import argparse


def create_parser():
    """Создание парсера аргументов"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--container', required=True)
    parser.add_argument('-m', '--message')
    parser.add_argument('-k', '--key', default=32)
    return parser


def check_input(container, message, key):
    """Проверка введённых пользователем данных"""
    if container and message and container.endswith(".txt") and message.endswith(".txt") and str(key).isdigit():
        return 1
    elif container and not message and container.endswith(".txt") and str(key).isdigit():
        return 2
    else:
        exit("Введённые данные некорректны!")


def check_container(container, message):
    """Проверка вместимости контейнера"""
    if len(message) > container.count(" "):
        exit("Сообщение не поместится в данный контейнер!")


def lin_rand_arr():
    """Генератор псевдослучайных чисел"""
    global g_random_seed
    a = 52  # множитель
    c = 65  # приращение
    m = 71  # модуль
    g_random_seed = (a * g_random_seed + c) % m


def stego_message(container, message, key):
    """Сокрытие сообщения в контейнере"""
    stego_container = ""
    p_container = 0  # указатель на символ в контейнере
    p_message = 0  # указатель на символ в сообщение

    global g_random_seed
    g_random_seed = key
    lin_rand_arr()

    stego_type = 1
    exit_flag = False

    while True:
        if exit_flag:
            break

        count = g_random_seed
        while count > 0:
            if container[p_container] == " ":
                if stego_type == 1:
                    stego_container += chr(0x0) if message[p_message] == "1" else chr(0x20)
                elif stego_type == 2:
                    stego_container += chr(0x0) if message[p_message] == "0" else chr(0x20)
                p_message += 1
                count -= 1
            else:
                stego_container += container[p_container]
            p_container += 1

            try:
                message[p_message]
            except IndexError:
                exit_flag = True
                stego_container += container[p_container:]
                break

        stego_type = 1 if stego_type == 2 else 2
        lin_rand_arr()

    with open("stego_container.txt", "w") as file:
        file.write(stego_container)


def destego_message(container, key):
    """Извлечение сообщения из контейнера"""
    message = ""
    last_byte = ""
    p_container = 0  # указатель на символ в контейнере
    num_of_spaces = 0

    global g_random_seed
    g_random_seed = key
    lin_rand_arr()

    stego_type = 1
    exit_flag = False

    while True:
        if exit_flag:
            break

        count = g_random_seed
        while count > 0:
            if len(last_byte) == 8:
                if num_of_spaces >= 8:
                    exit_flag = True
                    break
                message += last_byte
                last_byte = ""
            try:
                if ord(container[p_container]) == 0x0:
                    last_byte += "1" if stego_type == 1 else "0"
                    count -= 1
                    num_of_spaces = 0

                elif ord(container[p_container]) == 0x20:
                    last_byte += "0" if stego_type == 1 else "1"
                    count -= 1
                    num_of_spaces += 1
            except IndexError:
                exit_flag = True
                break
            p_container += 1

        stego_type = 1 if stego_type == 2 else 2
        lin_rand_arr()
    return message


def text2bin(message):
    """Преобразование текста в бинарный код"""
    return "".join(format(ord(ch), "08b") for ch in message)


def bin2text(message):
    """Преобразование бинарного кода в текст"""
    res = ""
    step = 8
    for i in range(0, len(message), 8):
        res += chr(int(message[i:step], 2))
        step += 8
    return res


def get_message(path):
    """Помещение содержимого файла с сообщением в переменную"""
    with open(path, "r") as file:
        message = file.read()
    if not message:
        exit("Скрываемое сообщение не может быть пустым")
    return message


def get_container(path):
    """Помещение содержимого файла с контейнером в переменную"""
    with open(path, "r") as file:
        container = file.read()
    return container


def put_message(message):
    """Запись извлечённого сообщения в файл"""
    with open("secret_message.txt", "w") as file:
        file.write(message)


def _main():
    """Реализация стеганографии в текстовых файлах"""
    # парсим аргументы
    parser = create_parser()
    namespace = parser.parse_args()

    path_to_container = namespace.container
    path_to_message = namespace.message
    key = int(namespace.key)

    # проверяем правильность введённых аргументов и определяем тип операции
    operation_type = check_input(path_to_container, path_to_message, key)

    # извлечём контейнер из файла
    container = get_container(path_to_container)

    if operation_type == 1:
        # извлечём сообщение из файла
        message = get_message(path_to_message)

        # преобразуем сообщение в двочиный код
        message = text2bin(message)

        # проверим контейнер на вместимость сообщения
        check_container(container, message)

        # встраиваем сообщение в контейнер
        stego_message(container, message, key)

    elif operation_type == 2:
        # извлекаем сообщение из контейнера
        message = destego_message(container, key)

        # преобразуем двоичный код в десятеричный
        message = bin2text(message)

        # запишем извлечённое сообщение в файл и выведем его на экран
        put_message(message)
        print(message)


if __name__ == "__main__":
    _main()


