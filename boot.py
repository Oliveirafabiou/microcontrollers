import network, time
from machine import Pin

network.country('BR')

ap = network.WLAN(network.AP_IF)
ap.config(ssid="vizlabmicro", password="senh@fort3")  # senha: mínimo 8 caracteres
ap.active(True)

while not ap.active():
    time.sleep(0.1)

print("AP ativo:", ap.ifconfig())

import webrepl
webrepl.start(password="123456")  # máximo 9 caracteres

# 5 piscadas = rede e WebREPL no ar
led = Pin("LED", Pin.OUT)
for _ in range(5):
    led.toggle(); time.sleep(0.1)
    led.toggle(); time.sleep(0.1)
