# MFRC522 (RC522) para MicroPython no Raspberry Pi Pico / Pico 2 W
# Baseado em https://github.com/danjperron/micropython-mfrc522
# Simplificado para rp2: SPI de hardware, esperas corrigidas, HLTA e UID de 4/7 bytes.

from machine import Pin, SPI
import time


class MFRC522:
    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26     # REQA: acorda so cartoes no estado inicial
    REQALL = 0x52     # WUPA: acorda tambem cartoes "dormindo" (halt)
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    def __init__(self, sck, mosi, miso, rst, cs, baudrate=1000000, spi_id=0):
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.rst = Pin(rst, Pin.OUT, value=0)
        self.spi = SPI(
            spi_id,
            baudrate=baudrate,
            polarity=0,
            phase=0,
            sck=Pin(sck),
            mosi=Pin(mosi),
            miso=Pin(miso),
        )

        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(50)
        self.init()

    # ------------------------------------------------------------------
    # Acesso aos registradores
    # ------------------------------------------------------------------
    def _wreg(self, reg, val):
        self.cs.value(0)
        self.spi.write(bytes([(reg << 1) & 0x7E, val & 0xFF]))
        self.cs.value(1)

    def _rreg(self, reg):
        self.cs.value(0)
        self.spi.write(bytes([((reg << 1) & 0x7E) | 0x80]))
        val = self.spi.read(1)[0]
        self.cs.value(1)
        return val

    def _sflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def version(self):
        # 0x91 / 0x92 = RC522 normal. 0x00 ou 0xFF = sem comunicacao (fiacao).
        return self._rreg(0x37)

    # ------------------------------------------------------------------
    # Comunicacao com o cartao
    # ------------------------------------------------------------------
    def _tocard(self, cmd, send):
        recv = []
        bits = 0
        irq_en = 0
        wait_irq = 0

        if cmd == 0x0E:        # MFAuthent
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == 0x0C:      # Transceive
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)   # ComIEnReg
        self._cflags(0x04, 0x80)          # ComIrqReg: limpa flags
        self._sflags(0x0A, 0x80)          # FIFOLevelReg: limpa FIFO
        self._wreg(0x01, 0x00)            # Idle

        for c in send:
            self._wreg(0x09, c)           # grava no FIFO
        self._wreg(0x01, cmd)
        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)      # StartSend

        n = 0
        for _ in range(2000):
            n = self._rreg(0x04)
            if (n & 0x01) or (n & wait_irq):   # timer estourou ou evento esperado
                break
        else:
            self._cflags(0x0D, 0x80)
            return self.ERR, recv, bits

        self._cflags(0x0D, 0x80)

        if self._rreg(0x06) & 0x1B:       # erros de buffer/colisao/CRC/paridade/protocolo
            return self.ERR, recv, bits

        if n & irq_en & 0x01:             # timer estourou: nenhum cartao respondeu
            return self.NOTAGERR, recv, bits

        if cmd == 0x0C:
            n = self._rreg(0x0A)
            lbits = self._rreg(0x0C) & 0x07
            if lbits != 0:
                bits = (n - 1) * 8 + lbits
            else:
                bits = n * 8

            if n == 0:
                n = 1
            elif n > 16:
                n = 16

            for _ in range(n):
                recv.append(self._rreg(0x09))

        return self.OK, recv, bits

    def _crc(self, data):
        self._cflags(0x05, 0x04)          # limpa CRCIRq
        self._sflags(0x0A, 0x80)          # limpa FIFO
        for c in data:
            self._wreg(0x09, c)
        self._wreg(0x01, 0x03)            # CalcCRC

        for _ in range(255):
            if self._rreg(0x05) & 0x04:
                break

        self._wreg(0x01, 0x00)            # Idle
        return [self._rreg(0x22), self._rreg(0x21)]

    # ------------------------------------------------------------------
    # Inicializacao
    # ------------------------------------------------------------------
    def reset(self):
        self._wreg(0x01, 0x0F)
        time.sleep_ms(50)

    def init(self):
        self.reset()
        self._wreg(0x2A, 0x8D)   # TModeReg
        self._wreg(0x2B, 0x3E)   # TPrescalerReg
        self._wreg(0x2D, 30)     # TReloadRegH
        self._wreg(0x2C, 0)      # TReloadRegL
        self._wreg(0x15, 0x40)   # TxASKReg
        self._wreg(0x11, 0x3D)   # ModeReg
        self.antenna_on()

    def antenna_on(self, on=True):
        if on:
            self._sflags(0x14, 0x03)
        else:
            self._cflags(0x14, 0x03)

    # ------------------------------------------------------------------
    # Deteccao / selecao de cartao
    # ------------------------------------------------------------------
    def request(self, mode):
        self._wreg(0x0D, 0x07)
        stat, recv, bits = self._tocard(0x0C, [mode])
        if stat != self.OK or bits != 0x10:
            stat = self.ERR
        return stat, bits

    def anticoll(self, anticolN):
        ser = [anticolN, 0x20]
        self._wreg(0x0D, 0x00)
        stat, recv, bits = self._tocard(0x0C, ser)

        if stat == self.OK:
            if len(recv) == 5:
                chk = 0
                for i in range(4):
                    chk ^= recv[i]
                if chk != recv[4]:
                    stat = self.ERR
            else:
                stat = self.ERR

        return stat, recv

    def _select(self, ser5, anticolN):
        buf = [anticolN, 0x70] + ser5
        buf += self._crc(buf)
        stat, recv, bits = self._tocard(0x0C, buf)
        return stat == self.OK and bits == 0x18

    def SelectTagSN(self):
        # Retorna (OK, uid) com uid de 4 ou 7 bytes
        valid_uid = []
        for nivel in (0x93, 0x95, 0x97):
            stat, uid = self.anticoll(nivel)
            if stat != self.OK:
                return self.ERR, []
            if not self._select(uid, nivel):
                return self.ERR, []

            if uid[0] == 0x88:            # cascade tag: UID continua no proximo nivel
                valid_uid.extend(uid[1:4])
            else:
                valid_uid.extend(uid[0:4])
                return self.OK, valid_uid

        return self.ERR, []

    def halt(self):
        # HLTA: poe o cartao para "dormir" (ele nao responde a este comando)
        buf = [0x50, 0x00]
        buf += self._crc(buf)
        self._tocard(0x0C, buf)
        self.stop_crypto1()

    # ------------------------------------------------------------------
    # Leitura e escrita de blocos (MIFARE Classic)
    # ------------------------------------------------------------------
    def auth(self, mode, addr, key, uid):
        return self._tocard(0x0E, [mode, addr] + key + uid[:4])[0]

    def authKeys(self, uid, addr, keyA=None, keyB=None):
        if keyA is not None:
            return self.auth(self.AUTHENT1A, addr, keyA, uid)
        if keyB is not None:
            return self.auth(self.AUTHENT1B, addr, keyB, uid)
        return self.ERR

    def stop_crypto1(self):
        self._cflags(0x08, 0x08)

    def read(self, addr):
        data = [0x30, addr]
        data += self._crc(data)
        stat, recv, _ = self._tocard(0x0C, data)
        return stat, recv

    def write(self, addr, data):
        buf = [0xA0, addr]
        buf += self._crc(buf)
        stat, recv, bits = self._tocard(0x0C, buf)

        if stat != self.OK or bits != 4 or (recv[0] & 0x0F) != 0x0A:
            return self.ERR

        buf = []
        for i in range(16):
            buf.append(data[i])
        buf += self._crc(buf)
        stat, recv, bits = self._tocard(0x0C, buf)

        if stat != self.OK or bits != 4 or (recv[0] & 0x0F) != 0x0A:
            return self.ERR
        return self.OK

    def readSectorBlock(self, uid, sector, block, keyA=None, keyB=None):
        absolute = sector * 4 + (block % 4)
        if absolute > 63:
            return self.ERR, None
        if self.authKeys(uid, absolute, keyA, keyB) == self.OK:
            return self.read(absolute)
        return self.ERR, None

    def writeSectorBlock(self, uid, sector, block, data, keyA=None, keyB=None):
        absolute = sector * 4 + (block % 4)
        if absolute > 63 or len(data) != 16:
            return self.ERR
        if self.authKeys(uid, absolute, keyA, keyB) == self.OK:
            return self.write(absolute, data)
        return self.ERR
