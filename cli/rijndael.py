# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: rijndael.pyo
# Compiled at: 2012-10-05 14:14:59
import copy, string, struct
shifts = [
 [
  [
   0, 0], [1, 3], [2, 2], [3, 1]],
 [
  [
   0, 0], [1, 5], [2, 4], [3, 3]],
 [
  [
   0, 0], [1, 7], [3, 5], [4, 4]]]
num_rounds = {16: {16: 10, 24: 12, 32: 14}, 24: {16: 12, 24: 12, 32: 14}, 32: {16: 14, 24: 14, 32: 14}}
A = [
 [
  1, 1, 1, 1, 1, 0, 0, 0],
 [
  0, 1, 1, 1, 1, 1, 0, 0],
 [
  0, 0, 1, 1, 1, 1, 1, 0],
 [
  0, 0, 0, 1, 1, 1, 1, 1],
 [
  1, 0, 0, 0, 1, 1, 1, 1],
 [
  1, 1, 0, 0, 0, 1, 1, 1],
 [
  1, 1, 1, 0, 0, 0, 1, 1],
 [
  1, 1, 1, 1, 0, 0, 0, 1]]
alog = [
 1]
for i in range(255):
    j = alog[-1] << 1 ^ alog[-1]
    if j & 256 != 0:
        j ^= 283
    alog.append(j)

log = [0] * 256
for i in range(1, 255):
    log[alog[i]] = i

def mul(a, b):
    if a == 0 or b == 0:
        return 0
    return alog[(log[a & 255] + log[b & 255]) % 255]


box = [ [0] * 8 for i in range(256) ]
box[1][7] = 1
for i in range(2, 256):
    j = alog[255 - log[i]]
    for t in range(8):
        box[i][t] = j >> 7 - t & 1

B = [
 0, 1, 1, 0, 0, 0, 1, 1]
cox = [ [0] * 8 for i in range(256) ]
for i in range(256):
    for t in range(8):
        cox[i][t] = B[t]
        for j in range(8):
            cox[i][t] ^= A[t][j] * box[i][j]

S = [
 0] * 256
Si = [0] * 256
for i in range(256):
    S[i] = cox[i][0] << 7
    for t in range(1, 8):
        S[i] ^= cox[i][t] << 7 - t

    Si[S[i] & 255] = i

G = [
 [
  2, 1, 1, 3],
 [
  3, 2, 1, 1],
 [
  1, 3, 2, 1],
 [
  1, 1, 3, 2]]
AA = [ [0] * 8 for i in range(4) ]
for i in range(4):
    for j in range(4):
        AA[i][j] = G[i][j]
        AA[i][i + 4] = 1

for i in range(4):
    pivot = AA[i][i]
    if pivot == 0:
        t = i + 1
        while AA[t][i] == 0 and t < 4:
            t += 1
            for j in range(8):
                AA[i][j], AA[t][j] = AA[t][j], AA[i][j]

            pivot = AA[i][i]

    for j in range(8):
        if AA[i][j] != 0:
            AA[i][j] = alog[(255 + log[AA[i][j] & 255] - log[pivot & 255]) % 255]

    for t in range(4):
        if i != t:
            for j in range(i + 1, 8):
                AA[t][j] ^= mul(AA[i][j], AA[t][i])

            AA[t][i] = 0

iG = [ [0] * 4 for i in range(4) ]
for i in range(4):
    for j in range(4):
        iG[i][j] = AA[i][j + 4]

def mul4(a, bs):
    if a == 0:
        return 0
    r = 0
    for b in bs:
        r <<= 8
        if b != 0:
            r = r | mul(a, b)

    return r


T1 = []
T2 = []
T3 = []
T4 = []
T5 = []
T6 = []
T7 = []
T8 = []
U1 = []
U2 = []
U3 = []
U4 = []
for t in range(256):
    s = S[t]
    T1.append(mul4(s, G[0]))
    T2.append(mul4(s, G[1]))
    T3.append(mul4(s, G[2]))
    T4.append(mul4(s, G[3]))
    s = Si[t]
    T5.append(mul4(s, iG[0]))
    T6.append(mul4(s, iG[1]))
    T7.append(mul4(s, iG[2]))
    T8.append(mul4(s, iG[3]))
    U1.append(mul4(t, iG[0]))
    U2.append(mul4(t, iG[1]))
    U3.append(mul4(t, iG[2]))
    U4.append(mul4(t, iG[3]))

rcon = [
 1]
r = 1
for t in range(1, 30):
    r = mul(2, r)
    rcon.append(r)

del A
del AA
del pivot
del B
del G
del box
del log
del alog
del i
del j
del r
del s
del t
del mul
del mul4
del cox
del iG

class rijndael:

    def __init__(self, key, block_size=16):
        if block_size != 16 and block_size != 24 and block_size != 32:
            raise ValueError('Invalid block size: ' + str(block_size))
        if len(key) != 16 and len(key) != 24 and len(key) != 32:
            raise ValueError('Invalid key size: ' + str(len(key)))
        self.block_size = block_size
        ROUNDS = num_rounds[len(key)][block_size]
        BC = block_size / 4
        Ke = [ [0] * BC for i in range(ROUNDS + 1) ]
        Kd = [ [0] * BC for i in range(ROUNDS + 1) ]
        ROUND_KEY_COUNT = (ROUNDS + 1) * BC
        KC = len(key) / 4
        tk = []
        for i in range(0, KC):
            tk.append(ord(key[i * 4]) << 24 | ord(key[i * 4 + 1]) << 16 | ord(key[i * 4 + 2]) << 8 | ord(key[i * 4 + 3]))

        t = 0
        j = 0
        while j < KC and t < ROUND_KEY_COUNT:
            Ke[t / BC][t % BC] = tk[j]
            Kd[ROUNDS - t / BC][t % BC] = tk[j]
            j += 1
            t += 1

        tt = 0
        rconpointer = 0
        while t < ROUND_KEY_COUNT:
            tt = tk[KC - 1]
            tk[0] ^= (S[tt >> 16 & 255] & 255) << 24 ^ (S[tt >> 8 & 255] & 255) << 16 ^ (S[tt & 255] & 255) << 8 ^ S[tt >> 24 & 255] & 255 ^ (rcon[rconpointer] & 255) << 24
            rconpointer += 1
            if KC != 8:
                for i in range(1, KC):
                    tk[i] ^= tk[i - 1]

            for i in range(1, KC / 2):
                tk[i] ^= tk[i - 1]

            tt = tk[KC / 2 - 1]
            tk[(KC / 2)] ^= S[tt & 255] & 255 ^ (S[tt >> 8 & 255] & 255) << 8 ^ (S[tt >> 16 & 255] & 255) << 16 ^ (S[tt >> 24 & 255] & 255) << 24
            for i in range(KC / 2 + 1, KC):
                tk[i] ^= tk[i - 1]

            j = 0
            while j < KC and t < ROUND_KEY_COUNT:
                Ke[t / BC][t % BC] = tk[j]
                Kd[ROUNDS - t / BC][t % BC] = tk[j]
                j += 1
                t += 1

        for r in range(1, ROUNDS):
            for j in range(BC):
                tt = Kd[r][j]
                Kd[r][j] = U1[tt >> 24 & 255] ^ U2[tt >> 16 & 255] ^ U3[tt >> 8 & 255] ^ U4[tt & 255]

        self.Ke = Ke
        self.Kd = Kd

    def encrypt(self, plaintext):
        if len(plaintext) != self.block_size:
            raise ValueError('wrong block length, expected ' + str(self.block_size) + ' got ' + str(len(plaintext)))
        Ke = self.Ke
        BC = self.block_size / 4
        ROUNDS = len(Ke) - 1
        if BC == 4:
            SC = 0
        else:
            if BC == 6:
                SC = 1
            else:
                SC = 2
        s1 = shifts[SC][1][0]
        s2 = shifts[SC][2][0]
        s3 = shifts[SC][3][0]
        a = [0] * BC
        t = []
        for i in range(BC):
            t.append((ord(plaintext[i * 4]) << 24 | ord(plaintext[i * 4 + 1]) << 16 | ord(plaintext[i * 4 + 2]) << 8 | ord(plaintext[i * 4 + 3])) ^ Ke[0][i])

        for r in range(1, ROUNDS):
            for i in range(BC):
                a[i] = T1[t[i] >> 24 & 255] ^ T2[t[(i + s1) % BC] >> 16 & 255] ^ T3[t[(i + s2) % BC] >> 8 & 255] ^ T4[t[(i + s3) % BC] & 255] ^ Ke[r][i]

            t = copy.copy(a)

        result = []
        for i in range(BC):
            tt = Ke[ROUNDS][i]
            result.append((S[t[i] >> 24 & 255] ^ tt >> 24) & 255)
            result.append((S[t[(i + s1) % BC] >> 16 & 255] ^ tt >> 16) & 255)
            result.append((S[t[(i + s2) % BC] >> 8 & 255] ^ tt >> 8) & 255)
            result.append((S[t[(i + s3) % BC] & 255] ^ tt) & 255)

        return string.join(list(map(chr, result)), '')

    def decrypt(self, ciphertext):
        if len(ciphertext) != self.block_size:
            raise ValueError('wrong block length, expected ' + str(self.block_size) + ' got ' + str(len(ciphertext)))
        Kd = self.Kd
        BC = self.block_size / 4
        ROUNDS = len(Kd) - 1
        if BC == 4:
            SC = 0
        else:
            if BC == 6:
                SC = 1
            else:
                SC = 2
        s1 = shifts[SC][1][1]
        s2 = shifts[SC][2][1]
        s3 = shifts[SC][3][1]
        a = [0] * BC
        t = [
         0] * BC
        for i in range(BC):
            t[i] = (ord(ciphertext[i * 4]) << 24 | ord(ciphertext[i * 4 + 1]) << 16 | ord(ciphertext[i * 4 + 2]) << 8 | ord(ciphertext[i * 4 + 3])) ^ Kd[0][i]

        for r in range(1, ROUNDS):
            for i in range(BC):
                a[i] = T5[t[i] >> 24 & 255] ^ T6[t[(i + s1) % BC] >> 16 & 255] ^ T7[t[(i + s2) % BC] >> 8 & 255] ^ T8[t[(i + s3) % BC] & 255] ^ Kd[r][i]

            t = copy.copy(a)

        result = []
        for i in range(BC):
            tt = Kd[ROUNDS][i]
            result.append((Si[t[i] >> 24 & 255] ^ tt >> 24) & 255)
            result.append((Si[t[(i + s1) % BC] >> 16 & 255] ^ tt >> 16) & 255)
            result.append((Si[t[(i + s2) % BC] >> 8 & 255] ^ tt >> 8) & 255)
            result.append((Si[t[(i + s3) % BC] & 255] ^ tt) & 255)

        return string.join(list(map(chr, result)), '')


def encrypt(key, block):
    return rijndael(key, len(block)).encrypt(block)


def decrypt(key, block):
    return rijndael(key, len(block)).decrypt(block)


def test():

    def t(kl, bl):
        b = 'b' * bl
        r = rijndael('a' * kl, bl)

    t(16, 16)
    t(16, 24)
    t(16, 32)
    t(24, 16)
    t(24, 24)
    t(24, 32)
    t(32, 16)
    t(32, 24)
    t(32, 32)