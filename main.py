from machine import Pin
from mfrc522 import MFRC522
import motor
import time

# Ligacao do RC522 (SPI0 de hardware):
# 3.3V -> 3V3 | GND -> GND | MISO -> GP0 | SDA/CS -> GP1
# SCK -> GP2 | MOSI -> GP3 | RST -> GP4
# Ligacao do motor: veja o inicio do motor.py (GP10 e GP11)

SEGUNDOS_MOTOR = 3     # quantos segundos o motor gira ao aproximar a tag
PRESENCA_MS = 500      # LED continua piscando ate 0,5 s apos a ultima leitura

led = Pin("LED", Pin.OUT)

reader = MFRC522(sck=2, mosi=3, miso=0, rst=4, cs=1, spi_id=0)

versao = reader.version()
print("VersionReg: 0x%02X" % versao)
if versao in (0x00, 0xFF):
    print("ERRO: o RC522 nao responde. Confira 3V3, GND, MISO, MOSI, SCK, SDA/CS e RST.")


def ler_cartao():
    # WUPA -> anticolisao/selecao (pega o UID) -> HLTA (cartao "dorme")
    stat, _ = reader.request(reader.REQALL)
    if stat != reader.OK:
        return None
    stat, uid = reader.SelectTagSN()
    if stat != reader.OK:
        return None
    reader.halt()
    return uid


def ao_detectar_tag(uid):
    print("Cartao detectado! UID:", [hex(b) for b in uid])
    led.value(1)
    motor.girar_horario(SEGUNDOS_MOTOR)


ultima = None
ultimo_uid = None
estava_presente = False

print("Aproxime o cartao do leitor. Para parar, clique em Stop.")

try:
    while True:
        uid = ler_cartao()
        agora = time.ticks_ms()

        if uid:
            ultima = agora
            ultimo_uid = uid

        presente = ultima is not None and time.ticks_diff(agora, ultima) < PRESENCA_MS

        if presente and not estava_presente:
            ao_detectar_tag(ultimo_uid)
            # O cartao pode continuar sobre o leitor: considera "presente" agora,
            # para so disparar de novo depois que ele for afastado.
            ultima = time.ticks_ms()
        elif estava_presente and not presente:
            print("Cartao removido")
        estava_presente = presente

        if presente:
            led.toggle()      # pisca enquanto o cartao esta perto
        else:
            led.value(0)

        time.sleep_ms(100)

except KeyboardInterrupt:
    motor.parar()
    led.value(0)
    print("Parado.")