from machine import Pin, PWM
import time

# ==========================================
# LIGACAO COM O DRIVER BL-TB6560
# (entradas opto-isoladas, ligacao "catodo comum")
#
#   Pico 2 W   ->  Driver
#   GP10       ->  CLK+   (pulsos de passo)
#   GP11       ->  CW+    (direcao)
#   GND        ->  CLK-  e  CW-
#   EN+ / EN-  ->  deixar sem ligar (motor habilitado)
#
# O motor e a fonte (12 a 24 V) ligam so no driver, nunca no Pico.
# ==========================================
PIN_CLK = 10
PIN_DIR = 11

NIVEL_HORARIO = 1          # se girar ao contrario, troque para 0
PASSOS_POR_SEGUNDO = 800   # frequencia dos pulsos (ajuste conforme microstep/torque)
FREQ_INICIAL = 200         # frequencia de partida (evita perder passo)
RAMPA_MS = 300             # tempo da aceleracao suave no inicio

_dir = Pin(PIN_DIR, Pin.OUT, value=1 - NIVEL_HORARIO)
_clk = PWM(Pin(PIN_CLK), freq=FREQ_INICIAL, duty_u16=0)


def parar():
    _clk.duty_u16(0)


def girar_horario(segundos, passos_por_segundo=PASSOS_POR_SEGUNDO):
    """Gira o motor no sentido horario por 'segundos' segundos."""
    duracao = int(segundos * 1000)
    if duracao <= 0:
        return

    _dir.value(NIVEL_HORARIO)
    time.sleep_ms(5)                 # tempo para a direcao estabilizar

    f_atual = 0
    inicio = time.ticks_ms()

    try:
        _clk.duty_u16(32768)         # onda quadrada 50%
        while True:
            decorrido = time.ticks_diff(time.ticks_ms(), inicio)
            if decorrido >= duracao:
                break

            if decorrido < RAMPA_MS and passos_por_segundo > FREQ_INICIAL:
                f = FREQ_INICIAL + (passos_por_segundo - FREQ_INICIAL) * decorrido // RAMPA_MS
            else:
                f = passos_por_segundo

            f = int(f)
            if f != f_atual:
                _clk.freq(f)
                f_atual = f

            time.sleep_ms(10)
    finally:
        parar()                      # para mesmo se der Stop no Thonny