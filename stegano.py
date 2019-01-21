import argparse
from encryption import SpeckCipher


def create_parser():
    """Создание парсера аргументов"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--container', required=True)
    parser.add_argument('-m', '--message')
    parser.add_argument('-k', '--key', default="fjJD2Yf3FNJ1933wy532fdsd30283HhfbFHEjsfgycurcn372t7f284dg2d27egf624")
    return parser


def check_input(container, message):
    """Проверка введённых пользователем данных"""
    if container and message and container.endswith(".txt") and message.endswith(".txt"):
        return 1
    elif container and not message and container.endswith(".txt"):
        return 2
    else:
        exit("Введённые данные некорректны!")


def check_container(container, message):
    """Проверка вместимости контейнера"""
    if len(message) > container.count(" "):
        exit("Сообщение не поместится в данный контейнер!")


def convert_key(key):
    """Преобразование исходного ключа в криптографический и стеганографический ключи"""
    if len(key) < 10:
        key = "fjJD2Yf3FNJ1933wy532fdsd30283HhfbFHEjsfgycurcn372t7f284dg2d27egf624"
        print(f"Длина введённого ключа менее 10 символов.\n"
              f"Установлен ключ по умолчанию: {key}")

    crypto_key = key[0:len(key)//2]
    stego_key = key[len(key)//2:]

    crypto_key_int = sum([ord(c) << (8 * x) for x, c in enumerate(reversed(crypto_key))])
    stego_key_int = sum([ord(c) << (8 * x) for x, c in enumerate(reversed(stego_key))])
    return crypto_key_int, stego_key_int


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
                if num_of_spaces >= 8 and (last_byte == "11111111" or last_byte == "00000000"):
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


def prepare_blocks(message):
    """Разбиение секретного сообщения на блоки"""
    blocks = []
    step = 16

    if len(message) % 16 == 0:
        blocks_count = len(message) // 16
        for i in range(blocks_count):
            block = message[i*16:step]
            step += 16
            blocks.append(block)
        last_block = chr(128) + "0" * 15
        blocks.append(last_block)
    else:
        blocks_count = len(message) // 16 + 1
        for i in range(blocks_count-1):
            block = message[i*16:step]
            step += 16
            blocks.append(block)

        last_block_count = 16 - (blocks_count * 16 - len(message))
        last_block = message[(blocks_count-1) * 16: (blocks_count-1) * 16 + last_block_count] + \
            chr(128) + "0" * (blocks_count * 16 - len(message) - 1)
        blocks.append(last_block)

    for i in range(len(blocks)):
        blocks[i] = sum([ord(c) << (8 * x) for x, c in enumerate(reversed(blocks[i]))])
    return blocks


def encrypt_message(message, key):
    """Шифрование секретного сообщения"""
    encrypted_message = ""
    cipher = SpeckCipher(key)

    blocks_count = len(message) // 16 + 1
    blocks = prepare_blocks(message)

    for i in range(blocks_count):
        encrypted_block = cipher.encrypt(blocks[i])
        encrypted_message_bytes = bytearray.fromhex('{:08x}'.format(encrypted_block))
        for byte in encrypted_message_bytes:
            encrypted_message += chr(byte)
    return encrypted_message


def decrypt_message(encrypted_message, key):
    """Расшифровывание секретного сообщения"""
    decrypted_message = ""
    step = 16
    cipher = SpeckCipher(key)

    # print(len(encrypted_message))
    blocks_count = len(encrypted_message) // 16

    for i in range(blocks_count):
        block = encrypted_message[i * 16:step]

        encrypted_block_int = sum([ord(c) << (8 * x) for x, c in enumerate(reversed(block))])
        decrypted_block_int = cipher.decrypt(encrypted_block_int)
        decrypted_block_bytes = bytearray.fromhex('{:032x}'.format(decrypted_block_int))

        if i == blocks_count - 1:
            for j in range(len(decrypted_block_bytes)):
                if decrypted_block_bytes[j] == 0x80:
                    k = j
            for j in range(0, k):
                decrypted_message += chr(decrypted_block_bytes[j])
        else:
            for j in range(len(decrypted_block_bytes)):
                decrypted_message += chr(decrypted_block_bytes[j])
        step += 16

    return decrypted_message


def get_message(path):
    """Помещение содержимого файла с сообщением в переменную"""
    message = ""
    with open(path, "r") as file:
        for line in file:
            for char in line:
                if ord(char) == 10:
                    message += chr(13) + chr(10)
                else:
                    message += char
    if not message:
        exit("Скрываемое сообщение не может быть пустым!")
    return message


def get_container(path):
    """Помещение содержимого файла с контейнером в переменную"""
    with open(path, "r") as file:
        container = file.read()
    return container


def put_message(message):
    """Запись извлечённого сообщения в файл"""
    with open("secret_message.txt", "w") as file:
        for char in message:
            if ord(char) != 13:
                file.write(char)


def _main():
    """Реализация стеганографии в текстовых файлах"""
    # парсинг аргументов
    parser = create_parser()
    namespace = parser.parse_args()

    path_to_container = namespace.container
    path_to_message = namespace.message
    key = namespace.key

    # преобразуем пользовательский ключ в криптографический и стеганографический ключи
    crypto_key, stego_key = convert_key(key)

    # проверка правильности введённых аргументов и определение типа операции
    operation_type = check_input(path_to_container, path_to_message)

    # извлечение контейнера из файла
    container = get_container(path_to_container)

    if operation_type == 1:
        # извлечение сообщения из файла
        message = get_message(path_to_message)
        # print(f"Секретное сообщение:\n{message}")

        # шифрование сообщения
        message = encrypt_message(message, crypto_key)
        # print(f"Зашифрованное сообщение: {message}")

        # преобразование сообщения в двочиный код
        message = text2bin(message)

        # проверка контейнера на вместимость сообщения
        check_container(container, message)

        # встраивание сообщения в контейнер
        stego_message(container, message, stego_key)

    elif operation_type == 2:
        # извлечение сообщения из контейнера
        message = destego_message(container, stego_key)

        # преобразование двоичного кода в десятичный
        message = bin2text(message)
        # print(f"Зашифрованное сообщение: {message},\nДлина: {len(message)}")

        # расшифрование секретного сообщения
        message = decrypt_message(message, crypto_key)

        # запись извлечённого сообщения в файл и вывод его на экран
        put_message(message)
        print(f"Секретное сообщение:\n{message}")


if __name__ == "__main__":
    _main()
