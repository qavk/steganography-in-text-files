class SpeckCipher(object):
    """Реализация шифра Speck"""

    def encrypt_round(self, x, y, k):
        """Раунд шифра Speck"""
        rs_x = ((x << (self.word_size - self.alpha_shift)) + (x >> self.alpha_shift)) & self.mod_mask
        add_sxy = (rs_x + y) & self.mod_mask
        new_x = k ^ add_sxy
        ls_y = ((y >> (self.word_size - self.beta_shift)) + (y << self.beta_shift)) & self.mod_mask
        new_y = new_x ^ ls_y
        return new_x, new_y

    def __init__(self, key):
        self.key_size = 128
        self.block_size = 128
        self.word_size = self.block_size >> 1
        self.rounds = 32
        self.mod_mask = (2 ** self.word_size) - 1
        self.mod_mask_sub = (2 ** self.word_size)
        self.beta_shift = 3
        self.alpha_shift = 8

        self.key = key & ((2 ** self.key_size) - 1)

        # генерируем список раундовых ключей
        self.key_schedule = [self.key & self.mod_mask]
        l_schedule = [(self.key >> (x * self.word_size)) & self.mod_mask for x in
                      range(1, self.key_size // self.word_size)]

        for x in range(self.rounds - 1):
            new_l_k = self.encrypt_round(l_schedule[x], self.key_schedule[x], x)
            l_schedule.append(new_l_k[0])
            self.key_schedule.append(new_l_k[1])

    def encrypt(self, plaintext):
        """Метод шифрования блока исходного текста"""
        b = (plaintext >> self.word_size) & self.mod_mask
        a = plaintext & self.mod_mask

        b, a = self.encrypt_function(b, a)

        ciphertext = (b << self.word_size) + a
        return ciphertext

    def decrypt(self, ciphertext):
        """Метод расшифровывания блока шифр-текста"""
        b = (ciphertext >> self.word_size) & self.mod_mask
        a = ciphertext & self.mod_mask

        b, a = self.decrypt_function(b, a)

        plaintext = (b << self.word_size) + a
        return plaintext

    def encrypt_function(self, upper_word, lower_word):
        """Раундовая функция шифрования Speck"""
        x = upper_word
        y = lower_word

        for k in self.key_schedule:
            rs_x = ((x << (self.word_size - self.alpha_shift)) + (x >> self.alpha_shift)) & self.mod_mask
            add_sxy = (rs_x + y) & self.mod_mask
            x = k ^ add_sxy
            ls_y = ((y >> (self.word_size - self.beta_shift)) + (y << self.beta_shift)) & self.mod_mask
            y = x ^ ls_y
        return x, y

    def decrypt_function(self, upper_word, lower_word):
        """Раундовая функция расшифровывания Speck"""
        x = upper_word
        y = lower_word

        for k in reversed(self.key_schedule):
            xor_xy = x ^ y
            y = ((xor_xy << (self.word_size - self.beta_shift)) + (xor_xy >> self.beta_shift)) & self.mod_mask
            xor_xk = x ^ k
            msub = ((xor_xk - y) + self.mod_mask_sub) % self.mod_mask_sub
            x = ((msub >> (self.word_size - self.alpha_shift)) + (msub << self.alpha_shift)) & self.mod_mask
        return x, y



