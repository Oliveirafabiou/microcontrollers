\# Automação Industrial de Baixo Custo com Raspberry Pi Pico 2 W



Sistema embarcado desenvolvido em MicroPython para integrar identificação por RFID e acionamento de um motor de passo. O projeto utiliza um Raspberry Pi Pico 2 W, um leitor RFID-RC522 e um driver BL-TB6560-v2.0 para demonstrar como microcontroladores podem automatizar etapas de um processo industrial com hardware acessível.



\*\*Objetivo:\*\* explorar uma solução de automação que possa reduzir intervenções manuais, simplificar operações repetitivas e contribuir para a redução dos custos de implementação de processos industriais.



\*\*Repositório:\*\* \[Oliveirafabiou/microcontrollers](https://github.com/Oliveirafabiou/microcontrollers)



\---



\## Visão geral



O sistema identifica a aproximação de uma tag RFID e, quando detectada, aciona um motor de passo por um intervalo de tempo configurado. O firmware também oferece recursos de acesso remoto ao microcontrolador por meio de uma interface Wi-Fi e do WebREPL do MicroPython.



A proposta reúne conceitos de sistemas embarcados, integração de periféricos, controle de atuadores e automação de processos.



\### Como funciona



1\. \*\*Inicialização:\*\* o Raspberry Pi Pico 2 W inicializa a configuração de rede e o acesso remoto.

2\. \*\*Leitura RFID:\*\* o leitor RC522 verifica a presença de uma tag compatível e obtém seu identificador (UID).

3\. \*\*Processamento do evento:\*\* o programa identifica uma nova aproximação e evita repetir o acionamento enquanto a tag permanece detectada.

4\. \*\*Acionamento do motor:\*\* o Pico gera pulsos de controle para o driver BL-TB6560-v2.0, que comanda o motor de passo.

5\. \*\*Sinalização:\*\* o LED integrado indica o estado associado à detecção da tag.

6\. \*\*Retorno à espera:\*\* após o acionamento, o sistema continua monitorando o leitor para detectar novas aproximações.



\## Tecnologias e componentes



| Categoria | Tecnologia ou componente |

|---|---|

| Microcontrolador | Raspberry Pi Pico 2 W (RP2350) |

| Firmware | MicroPython |

| Identificação | Leitor RFID-RC522 |

| Acionamento | Driver de motor de passo BL-TB6560-v2.0 |

| Atuador | Motor de passo NEMA 17 |

| Comunicação com o leitor | SPI |

| Acesso remoto | Wi-Fi e WebREPL |

| Controle do motor | PWM para geração de pulsos de passo |

| Desenvolvimento | Python, Thonny e Git |



\## Estrutura do projeto



| Arquivo | Responsabilidade |

|---|---|

| `boot.py` | Inicialização da rede Wi-Fi em modo Access Point e do WebREPL para acesso remoto ao microcontrolador. |

| `main.py` | Programa principal: inicializa o leitor RFID, identifica tags, gerencia o estado de presença, sinaliza eventos e aciona o motor. |

| `mfrc522.py` | Implementação da comunicação e das operações de leitura RFID com o módulo RC522. |

| `motor.py` | Encapsula o controle do motor de passo, incluindo direção, frequência dos pulsos, aceleração inicial e parada. |

| `oldmain.txt` | Arquivo de referência com uma versão anterior do programa. |



\## Arquitetura de hardware



\### 1. Raspberry Pi Pico 2 W e RFID-RC522



O leitor RC522 comunica-se com o microcontrolador por SPI. A ligação utilizada pelo programa é:



| RC522 | Raspberry Pi Pico 2 W |

|---|---|

| 3.3V | 3V3(OUT) |

| GND | GND |

| MISO | GP0 |

| SDA / CS | GP1 |

| SCK | GP2 |

| MOSI | GP3 |

| RST | GP4 |



O firmware consulta o leitor, solicita a presença de uma tag, obtém o UID e utiliza essa informação para iniciar o evento de automação.



\### 2. Driver BL-TB6560-v2.0 e motor de passo



O driver recebe sinais lógicos do microcontrolador e controla a corrente fornecida às bobinas do motor.



| Sinal | Raspberry Pi Pico 2 W | Driver |

|---|---|---|

| Pulso de passo (CLK) | GP10 | CLK+ |

| Direção (CW) | GP11 | CW+ |

| Referência dos sinais | GND | CLK− e CW− |



A configuração acima utiliza a ligação de cátodo comum indicada no código. A alimentação do motor é fornecida separadamente ao driver. Os terminais de saída do driver devem ser ligados às bobinas do motor conforme o diagrama elétrico do equipamento.



> \*\*Segurança:\*\* não conecte o motor diretamente aos pinos do Pico. Confira a pinagem, a tensão de alimentação, o limite de corrente e a configuração de microstepping do driver antes de energizar o circuito.



\## Estratégia de controle do motor



O módulo `motor.py` concentra a lógica de acionamento para manter o controle do motor separado do fluxo principal de leitura RFID.



Os parâmetros principais são configuráveis:



\- \*\*Duração do acionamento:\*\* 3 segundos por detecção, definida em `main.py`.

\- \*\*Frequência inicial:\*\* 200 pulsos por segundo.

\- \*\*Frequência de operação:\*\* 800 pulsos por segundo.

\- \*\*Rampa de aceleração:\*\* 300 ms.

\- \*\*Direção:\*\* configurada por um nível lógico no pino de direção.



O módulo também utiliza uma rotina de parada para desabilitar a geração de pulsos ao final do acionamento ou quando a execução é interrompida.



Esses parâmetros são valores iniciais de teste e devem ser ajustados de acordo com a carga mecânica, o torque necessário, a corrente configurada no driver e o microstepping utilizado.



\## Como executar



\### Requisitos



\- Raspberry Pi Pico 2 W com firmware MicroPython compatível.

\- Leitor RFID-RC522 e uma tag compatível.

\- Driver BL-TB6560-v2.0 e motor de passo compatível.

\- Fonte adequada ao driver e ao motor.

\- Thonny ou outra ferramenta compatível com MicroPython.

\- Arquivos do projeto disponíveis no dispositivo.



\### Configuração



1\. Clone o repositório:



&#x20;  ```bash

&#x20;  git clone https://github.com/Oliveirafabiou/microcontrollers.git

&#x20;  cd microcontrollers

&#x20;  ```



2\. Instale o firmware MicroPython apropriado para o Raspberry Pi Pico 2 W.



3\. Transfira os arquivos `boot.py`, `main.py`, `mfrc522.py` e `motor.py` para a raiz do sistema de arquivos do Pico.



4\. Revise a configuração de rede em `boot.py`. Configure credenciais próprias e mantenha senhas fora do repositório público.



5\. Confira toda a ligação elétrica antes de ligar o driver e o motor.



6\. Reinicie o microcontrolador e acompanhe as mensagens de inicialização pelo terminal do Thonny.



7\. Aproxime uma tag RFID do leitor para testar a identificação e o acionamento do motor.



\### Parâmetros de operação



Em `main.py`, o tempo de acionamento pode ser ajustado por meio de:



```python

SEGUNDOS\_MOTOR = 3

```



Em `motor.py`, os parâmetros de velocidade e aceleração podem ser alterados por meio de:



```python

PASSOS\_POR\_SEGUNDO = 800

FREQ\_INICIAL = 200

RAMPA\_MS = 300

```



As alterações devem ser testadas gradualmente para evitar perda de passos ou funcionamento inadequado da mecânica.



\## Aplicação industrial



A proposta é explorar o uso de identificação sem contato para iniciar uma ação mecânica de forma automatizada. Em um cenário industrial, uma abordagem desse tipo pode servir como base para protótipos de:



\- Acionamento de mecanismos mediante identificação de uma tag.

\- Automatização de movimentos repetitivos.

\- Identificação de itens ou etapas de um fluxo operacional.

\- Prototipagem de dispositivos de baixo custo para validação de conceitos de automação.



O benefício econômico depende do processo em que a solução será aplicada. Para uma implementação industrial efetiva, seria necessário avaliar confiabilidade, tempo de resposta, segurança funcional, durabilidade, integração com equipamentos existentes e custo total de operação.



\## Competências técnicas demonstradas



Este projeto permite demonstrar experiência prática ou desenvolvimento de conhecimentos nas seguintes áreas:



\- \*\*Sistemas embarcados:\*\* desenvolvimento de firmware em MicroPython.

\- \*\*Integração de hardware:\*\* conexão de periféricos e atuadores a um microcontrolador.

\- \*\*Protocolos de comunicação:\*\* utilização de SPI para comunicação com o leitor RFID.

\- \*\*Controle de movimento:\*\* geração de pulsos, direção, ajuste de frequência e rampa de aceleração.

\- \*\*Automação:\*\* transformação de um evento de identificação em uma ação física.

\- \*\*Organização de software:\*\* separação entre lógica de aplicação, controle do motor e comunicação RFID.

\- \*\*Depuração:\*\* testes de comunicação, validação de sinais e investigação de problemas de hardware e firmware.

\- \*\*Acesso remoto:\*\* configuração de conectividade Wi-Fi e ferramentas de desenvolvimento remoto.



\## Próximos passos



Possíveis evoluções do projeto incluem:



\- Adicionar uma lista de UIDs autorizados para restringir o acionamento.

\- Implementar tempos de espera e tratamento de falhas de leitura.

\- Adicionar sensores de fim de curso ou confirmação de posição.

\- Registrar eventos de operação para análise de desempenho.

\- Criar uma interface de configuração para parâmetros de operação.

\- Avaliar a confiabilidade do sistema em ciclos repetidos e em condições próximas às de uso industrial.

\- Estudar a integração com sistemas supervisórios ou outros dispositivos de automação.



\## Autor



\*\*Fábio Silveira\*\*



Projeto de estudo e desenvolvimento aplicado à automação industrial, sistemas embarcados e integração de hardware e software.



\[GitHub](https://github.com/Oliveirafabiou)



\---



\*Este projeto é um protótipo de desenvolvimento. A utilização em ambiente industrial exige validação elétrica, mecânica e operacional, além da implementação das proteções adequadas à aplicação.\*



