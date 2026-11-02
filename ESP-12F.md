### **File del Progetto Generati**

Tutti i file sono salvati e pronti all'uso in KiCad:

- **Progetto KiCad:** `esp12f_battery_usb.kicad_pro`
- **Schematico KiCad:** `esp12f_battery_usb.kicad_sch`
- **File PCB:** `esp12f_battery_usb.kicad_pcb`
- **Esportazione PDF stampabile (A3):** `schematic.pdf`
- **Esportazione grafica SVG:** `esp12f_battery_usb.svg`
- **Report ERC (Electrical Rules Check):** `erc.rpt` — **0 Errori, 0 Avvisi**

------

### **Architettura del Circuito**

Lo schema è suddiviso in 6 blocchi funzionali racchiusi in aree dedicate:

```
[USB-C 5V] ──(PTC 500mA)──┬──► [TP4056 Charger] ──► [Batteria LiPo 3.7V (JST)]
                          │                               │
                          ├──► [Diodo SS14] ──┐           │
                          │                   ▼           ▼
                          │         [Power-Path P-MOSFET AO3401A]
                          │                       │
                          │                       ▼
                          │                [Switch SPDT SW1]
                          │                       │
                          │                       ▼
                          │            [LDO AP2112K-3.3 (600mA)]
                          │             (10µF + 100µF Tantalio)
                          │                       │
                          │                       ▼ (+3.3V)
                          ├────────────────► [ESP-12F Module] ◄── [Header J3/J4]
                          ▼                       ▲
             [CH340C USB-UART Bridge] ────────────┘
             (Auto-Reset DTR/RTS MMBT3904)
```

------

#### **1. Ingresso USB-C & Protezioni**

- **Connettore `J1`**: Presa USB-C a 16 pin standard USB 2.0.
- **Resistenze di pull-down CC (`R1`, `R2` da 5.1kΩ 1%)**: Indispensabili per consentire l'erogazione di 5V da alimentatori USB-C moderni e cavi Type-C to Type-C (Power Delivery negotiation).
- **Protezione da sovracorrente `F1`**: Polyfuse ripristinabile PTC da 500mA su linea VBUS.
- **Filtraggio**: Condensatori di disaccoppiamento `C1` (10µF) e `C2` (100nF ceramico).
- **Resistenze di terminazione `R3`, `R4` (22Ω)**: Sulle linee D+ e D- per smorzare riflessioni sul segnale USB.

------

#### **2. Ricarica Batteria Li-Ion / LiPo (TP4056)**

- **Controller di carica `U1` (`TP4056-42-ESOP8`)**: Con thermal pad saldato a massa per dissipare calore in fase CC (corrente costante).
- **Corrente di carica programmata a 500mA (`R8` = 2.4kΩ)**: $I_{CHG} = \frac{1200\text{ V}}{R_{PROG}} = \frac{1200}{2400\ \Omega} = 0.50\text{ A}\ (500\text{ mA})$ Questa corrente rispetta le specifiche degli hub USB 2.0 standard ed è ideale per celle LiPo da $\ge 500\text{ mAh}$ (fino a diversi Ah).
- **Indicatori di stato bicolore**:    
  - `LED1` (Rosso): In carica (`CHRG` attivo a livello basso).
  - `LED2` (Verde): Ricarica completata / Standby (`STDBY`).
- **Connettore Batteria `J2`**: Passo 2.0mm standard JST-PH a 2 poli.

------

#### **3. Circuito di Power-Path Automatico & LDO 3.3V**

Questo blocco risolve il classico problema di far funzionare il circuito mentre la batteria è in ricarica, evitando carichi fittizi sul TP4056:

- **Transistor P-MOSFET `Q1` (`AO3401A`)**:    
  - *Source* connesso a `VBAT` (batteria).
  - *Drain* connesso a `VSYS` (ingresso alimentazione sistema).
  - *Gate* connesso a `VBUS` (5V USB) con resistenza di pull-down `R9` da 100kΩ a massa.
- **Diodo Schottky `D1` (`SS14`, $1\text{A}, V_F \approx 0.35\text{V}$)**: Anodo su `VBUS`, Catodo su `VSYS`.
- **Come funziona la commutazione automatica:**    
  1. **Solo Batteria (USB scollegata, $V_{BUS} = 0\text{V}$)**:
       Il pull-down `R9` porta il Gate di `Q1` a 0V. Poiché la batteria è a $3.7\text{V} - 4.2\text{V}$, si ha $V_{GS} \approx -3.7\text{V} \ll V_{GS(th)} (-0.9\text{V})$. Il MOSFET conduce pienamente con $R_{DS(on)} < 30\text{ m}\Omega$, provocando una caduta di tensione quasi nulla ($< 10\text{ mV}$ a $200\text{ mA}$). `D1` è interdetto.
  2. **USB collegata ($V_{BUS} = 5\text{V}$)**:
       Il Gate di `Q1` sale a 5V. Poiché il Source è a max 4.2V, $V_{GS} = 5\text{V} - 4.2\text{V} = +0.8\text{V} > 0\text{V}$. Il P-MOSFET si spegne istantaneamente e scollega la batteria dal carico. `VSYS` è alimentato da USB tramite `D1` a circa $4.65\text{V}$. Il TP4056 può caricare la batteria seguendo l'algoritmo CC/CV senza essere disturbato dall'assorbimento dell'ESP8266.
- **Interruttore generale `SW1`**: A slitta SPDT per spegnere l'alimentazione a valle di `VSYS`.
- **Regolatore LDO `U2` (`AP2112K-3.3`)**:
    Eroga fino a 600mA continui con una caduta di tensione bassissima ($V_{drop} \approx 250\text{ mV}$ a pieno carico), consentendo all'ESP8266 di funzionare anche quando la batteria LiPo è quasi scarica ($3.3\text{V} + 0.25\text{V} = 3.55\text{V}$).
- **Filtro Anti-Brownout (Critico per ESP8266)**:
    Oltre a `C6` (10µF) e `C8` (100nF ceramici), è presente **`C7` al tantalio da 100µF 6.3V** a basso ESR, fondamentale per assorbire i picchi transitori di corrente da 350-450mA tipici delle trasmissioni RF Wi-Fi dell'ESP8266 evitando riavvii improvvisi.
- **`LED3` (Blu)**: Segnala la presenza della linea 3.3V attiva.

------

#### **4. Programmazione USB-UART & Circuito Auto-Reset**

- **Ponte USB-UART `U3` (`CH340C`)**: Integra l'oscillatore a cristallo interno senza bisogno di quarzo esterno.
- **Zero consumo a batteria**: Il CH340C è alimentato a 5V direttamente da `VBUS`. Quando la USB è staccata, il CH340C è completamente spento, garantendo zero assorbimento di corrente a riposo dalla batteria.
- **Circuito Auto-Reset NodeMCU (`Q2`, `Q3` MMBT3904 NPN)**:
    Pilotato dai segnali DTR e RTS, permette ad ambienti come `esptool`, Arduino IDE, PlatformIO e VS Code di riavviare l'ESP8266 ed entrare automaticamente in bootloader mode (GPIO0 a GND, impulso su RST) prima di effettuare il flash del firmware.
- **Pulsanti manuali di override**:    
  - `SW2`: Pulsante di **RESET** manuale.
  - `SW3`: Pulsante di **FLASH / BOOT** manuale.
- **Resistenze di protezione `R11`, `R12` (470Ω)**: Su linee TXD e RXD verso l'ESP.

------

#### **5. Modulo RF ESP-12F**

- **Pull-up di configurazione boot**:    
  - `R15` (10kΩ) su `RST`.
  - `R16` (10kΩ) su `EN` (Chip Enable).
  - `R17` (10kΩ) su `GPIO0`.
  - `R18` (10kΩ) su `GPIO2`.
- **Pull-down di configurazione boot**:    
  - `R19` (10kΩ) su `GPIO15` (necessario per boot da Flash SPI interna).
- **Filtro antirumore `C12` (100nF)**: Su linea `RST` per prevenire falsi riavvii causati da disturbi RF.
- **Disaccoppiamento locale `C10` (10µF) + `C11` (100nF)**: Posizionati direttamente sull'ingresso di alimentazione del modulo.

------

#### **6. Monitoraggio Batteria (ADC) & Pin Header**

- **Partitore resistivo 1% (`R20` = 100kΩ, `R21` = 27kΩ)**:
    Scala la tensione della batteria da un massimo di $4.2\text{V}$ a: $V_{ADC} = 4.2\text{V} \times \frac{27\text{ k}\Omega}{100\text{ k}\Omega + 27\text{ k}\Omega} = 4.2\text{V} \times 0.2126 = 0.893\text{V}$ Rientrando perfettamente nel range $0 - 1.0\text{V}$ dell'ADC integrato dell'ESP8266.
- **Filtro `C13` (100nF)**: Riduce l'impedenza di campionamento e stabilizza la lettura analogica.
- **Solder Jumper `JP1` (`BAT_ADC_EN`)**: Permette di scollegare fisicamente il partitore per liberare il pin ADC se si desidera collegare un sensore analogico esterno.
- **Header di espansione `J3` e `J4`**: Due connettori a 8 pin (passo 2.54mm) che rendono accessibili tutti i pin dell'ESP-12F, oltre a +3.3V e GND.

------

### **Verifica Elettrica (ERC)**

Il controllo delle regole elettriche è stato eseguito via `kicad-cli`:

```
ERC report (esp12f_battery_usb.kicad_sch)
Report includes: Errors, Warnings
***** Sheet /
** ERC messages: 0  Errors 0  Warnings 0
```

Il progetto è pronto per essere aperto in KiCad per l'eventuale sbroglio del PCB o per la generazione della distinta base (BOM).

 