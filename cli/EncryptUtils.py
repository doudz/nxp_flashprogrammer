# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: EncryptUtils.pyo
# Compiled at: 2012-10-19 14:46:25
import string, os
from stat import *
import struct
from rijndael import rijndael

def encryptFile(sSrcFilename, sDestFilename, nonce, key, partNo):
    bStatus = True
    try:
        inputFile = open(sSrcFilename, 'rb')
        image = inputFile.read()
        outputFile = open(sDestFilename, 'wb')
        data = image[48:]
        encryptedData = encryptFlashData(nonce, key, data, len(data))
        if partNo == 4:
            outputFile.write(image[0:8])
        else:
            outputFile.write(hextranslate('e1e1e1e1'))
            outputFile.write(image[4:8])
        hexstr = '%08x' % len(encryptedData)
        outputFile.write(hextranslate(hexstr))
        outputFile.write(image[12:48])
        outputFile.write(encryptedData)
    except:
        bStatus = False
        inputFile.close()

    outputFile.close()
    return bStatus


def encryptImage(oFirmwareImage, nonce, key, partNo):
    bStatus = True
    try:
        image = oFirmwareImage.sImage
        oFirmwareImage.sImage = ''
        data = image[48:]
        encryptedData = encryptFlashData(nonce, key, data, len(data))
        if partNo == 4:
            oFirmwareImage.sImage = image[0:8]
        else:
            oFirmwareImage.sImage = hextranslate('e1e1e1e1') + image[4:8]
        hexstr = '%08x' % len(encryptedData)
        oFirmwareImage.sImage += hextranslate(hexstr)
        oFirmwareImage.sImage += image[12:48]
        oFirmwareImage.sImage += encryptedData
    except:
        bStatus = False

    return bStatus


def encryptFlashData(nonce, key, data, imageLen):
    encyptedBlock = ''
    if imageLen % 16 != 0:
        for x in range(16 - imageLen % 16):
            data = data + chr(255)

        imageLen = len(data)
    r = rijndael(key, block_size=16)
    for x in range(imageLen / 16):
        encryptNonce = ''
        for i in nonce:
            tempString = '%08x' % i
            y = 0
            while y < 8:
                encryptNonce = encryptNonce + chr(string.atoi(tempString[y:y + 2], 16))
                y = y + 2

        encChunk = r.encrypt(encryptNonce)
        if nonce[3] == 4294967295:
            nonce[3] = 0
        else:
            nonce[3] += 1
        chunk = data[x * 16:(x + 1) * 16]
        lchunk = list(map(ord, chunk))
        lencChunk = list(map(ord, encChunk))
        outputString = ''
        loutChunk = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(16):
            loutChunk[i] = lchunk[i] ^ lencChunk[i]
            encyptedBlock = encyptedBlock + chr(lchunk[i] ^ lencChunk[i])

    return encyptedBlock


def hextranslate(s):
    res = ''
    for i in range(len(s) / 2):
        realIdx = i * 2
        res = res + chr(int(s[realIdx:realIdx + 2], 16))

    return res


def aParsePassKeyString(sPassKey):
    lstu32Passkey = [
     0, 0, 0, 0]
    try:
        lstStrPassKey = sPassKey.split(',')
    except:
        sPassKey = '0x00000000, 0x00000000, 0x00000000, 0x00000000'
        lstStrPassKey = self.sPassKey.split(',')
    else:
        if len(lstStrPassKey) == 4:
            for i in range(4):
                if '0x' in lstStrPassKey[i]:
                    lstu32Passkey[i] = int(lstStrPassKey[i], 16)
                else:
                    lstu32Passkey[i] = int(lstStrPassKey[i], 10)

    abEncryptKey = struct.pack('>LLLL', lstu32Passkey[0], lstu32Passkey[1], lstu32Passkey[2], lstu32Passkey[3])
    return abEncryptKey


def u32CRAChallenge(au8ChallengeEncrypted, abEncryptKey, abMACAddress):
    EncryptEngine = rijndael(abEncryptKey, block_size=16)
    encryptNonce = abMACAddress + abMACAddress
    encChunk = EncryptEngine.encrypt(encryptNonce)
    lchunk = list(map(ord, au8ChallengeEncrypted))
    lencChunk = list(map(ord, encChunk))
    DecryptedChunk = ''
    for i in range(16):
        DecryptedByte = lchunk[i] ^ lencChunk[i]
        DecryptedChunk = DecryptedChunk + chr(DecryptedByte)

    lstChallenge = struct.unpack('>LLLL', DecryptedChunk)
    return lstChallenge[0]


def au8CRAResponse(u32Response, abEncryptKey, abMACAddress):
    EncryptEngine = rijndael(abEncryptKey, block_size=16)
    DoubleMac = abMACAddress + abMACAddress
    encMac = EncryptEngine.encrypt(DoubleMac)
    lchunk = list(map(ord, struct.pack('>LLLL', u32Response, u32Response, u32Response, u32Response)))
    lencChunk = list(map(ord, encMac))
    EncryptedChunk = ''
    for i in range(16):
        EncryptedByte = lchunk[i] ^ lencChunk[i]
        EncryptedChunk = EncryptedChunk + chr(EncryptedByte)

    return EncryptedChunk


if __name__ == '__main__':
    print('This is not runnable')
