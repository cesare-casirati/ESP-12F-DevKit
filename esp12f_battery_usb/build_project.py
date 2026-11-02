import os
import subprocess
from make_schematic import SchematicBuilder

PROJECT_DIR = '/Users/mac/.gemini/antigravity/scratch/esp12f_battery_usb'
SCH_PATH = os.path.join(PROJECT_DIR, 'esp12f_battery_usb.kicad_sch')

b = SchematicBuilder()

# ==============================================================================
# BLOCK 1: USB-C POWER INPUT & ESD PROTECTION
# ==============================================================================
b.add_box(25.4, 25.4, 114.3, 114.3, "1. USB-C POWER INPUT & PROTECTION")

# J1: USB-C Receptacle 16-pin USB 2.0
b.add_component(
    ref='J1', lib='Connector', name='USB_C_Receptacle_USB2.0_16P',
    val='USB_C_16P', x=50.8, y=66.04, rot=0,
    fp='Connector_USB:USB_C_Receptacle_Palconn_UTC16-G'
)

# Connect GND pins & Shield
gnd_x, gnd_y = b.get_pin('J1', 'A1') # (50.8, 88.9)
sh_x, sh_y = b.get_pin('J1', 'SH')   # (43.18, 88.9)
b.add_wire(sh_x, sh_y, gnd_x, gnd_y)
b.add_junction(gnd_x, gnd_y)
b.add_power('GND', gnd_x, gnd_y + 5.08)
b.add_wire(gnd_x, gnd_y, gnd_x, gnd_y + 5.08)
b.add_pwr_flag(gnd_x, gnd_y + 10.16)
b.add_wire(gnd_x, gnd_y + 5.08, gnd_x, gnd_y + 10.16)

# VBUS pins (A4, B4, A9, B9)
vbus_raw_x, vbus_raw_y = b.get_pin('J1', 'A4') # (66.04, 50.8)

# Polyfuse F1 (500mA PTC) placed horizontally (rot=90)
b.add_component(
    ref='F1', lib='Device', name='Polyfuse',
    val='500mA PTC', x=76.2, y=50.8, rot=90,
    fp='Fuse:Fuse_1206_3216Metric'
)
f1_p1_x, f1_p1_y = b.get_pin('F1', '1') # (72.39, 50.8)
f1_p2_x, f1_p2_y = b.get_pin('F1', '2') # (80.01, 50.8)
b.add_wire(vbus_raw_x, vbus_raw_y, f1_p1_x, f1_p1_y)

# Output of F1 is VBUS rail (+5V USB)
b.add_wire(f1_p2_x, f1_p2_y, 88.9, 50.8)
b.add_junction(88.9, 50.8)
b.add_power('VBUS', 88.9, 43.18)
b.add_wire(88.9, 50.8, 88.9, 43.18)
b.add_pwr_flag(88.9, 38.1)
b.add_wire(88.9, 43.18, 88.9, 38.1)

# Capacitors C1 (10uF) and C2 (100nF) on VBUS
b.add_component(
    ref='C1', lib='Device', name='C',
    val='10uF 16V', x=96.52, y=60.96, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c1_p1_x, c1_p1_y = b.get_pin('C1', '1') # (96.52, 57.15)
c1_p2_x, c1_p2_y = b.get_pin('C1', '2') # (96.52, 64.77)
b.add_wire(88.9, 50.8, c1_p1_x, 50.8)
b.add_wire(c1_p1_x, 50.8, c1_p1_x, c1_p1_y)
b.add_junction(c1_p1_x, 50.8)
b.add_power('GND', c1_p2_x, c1_p2_y + 5.08)
b.add_wire(c1_p2_x, c1_p2_y, c1_p2_x, c1_p2_y + 5.08)

b.add_component(
    ref='C2', lib='Device', name='C',
    val='100nF', x=106.68, y=60.96, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c2_p1_x, c2_p1_y = b.get_pin('C2', '1')
c2_p2_x, c2_p2_y = b.get_pin('C2', '2')
b.add_wire(c1_p1_x, 50.8, c2_p1_x, 50.8)
b.add_wire(c2_p1_x, 50.8, c2_p1_x, c2_p1_y)
b.add_power('GND', c2_p2_x, c2_p2_y + 5.08)
b.add_wire(c2_p2_x, c2_p2_y, c2_p2_x, c2_p2_y + 5.08)

# CC Resistors R1 & R2 (5.1k)
cc1_x, cc1_y = b.get_pin('J1', 'A5') # (66.04, 55.88)
b.add_component(
    ref='R1', lib='Device', name='R',
    val='5.1k', x=76.2, y=63.5, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r1_p1_x, r1_p1_y = b.get_pin('R1', '1') # (76.2, 59.69)
r1_p2_x, r1_p2_y = b.get_pin('R1', '2') # (76.2, 67.31)
b.add_wire(cc1_x, cc1_y, r1_p1_x, cc1_y)
b.add_wire(r1_p1_x, cc1_y, r1_p1_x, r1_p1_y)
b.add_power('GND', r1_p2_x, r1_p2_y + 5.08)
b.add_wire(r1_p2_x, r1_p2_y, r1_p2_x, r1_p2_y + 5.08)

cc2_x, cc2_y = b.get_pin('J1', 'B5') # (66.04, 58.42)
b.add_component(
    ref='R2', lib='Device', name='R',
    val='5.1k', x=86.36, y=66.04, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r2_p1_x, r2_p1_y = b.get_pin('R2', '1')
r2_p2_x, r2_p2_y = b.get_pin('R2', '2')
b.add_wire(cc2_x, cc2_y, r2_p1_x, cc2_y)
b.add_wire(r2_p1_x, cc2_y, r2_p1_x, r2_p1_y)
b.add_power('GND', r2_p2_x, r2_p2_y + 5.08)
b.add_wire(r2_p2_x, r2_p2_y, r2_p2_x, r2_p2_y + 5.08)

# USB D- and D+ series resistors R3 & R4 (22R)
dm_a_x, dm_a_y = b.get_pin('J1', 'A7') # (66.04, 63.5)
dm_b_x, dm_b_y = b.get_pin('J1', 'B7') # (66.04, 66.04)
b.add_wire(dm_a_x, dm_a_y, 71.12, dm_a_y)
b.add_wire(dm_b_x, dm_b_y, 71.12, dm_b_y)
b.add_wire(71.12, dm_a_y, 71.12, dm_b_y)
b.add_junction(71.12, (dm_a_y + dm_b_y)/2)

b.add_component(
    ref='R3', lib='Device', name='R',
    val='22R', x=81.28, y=78.74, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r3_p1_x, r3_p1_y = b.get_pin('R3', '1') # (77.47, 78.74)
r3_p2_x, r3_p2_y = b.get_pin('R3', '2') # (85.09, 78.74)
b.add_wire(71.12, (dm_a_y + dm_b_y)/2, 71.12, 78.74)
b.add_wire(71.12, 78.74, r3_p1_x, r3_p1_y)
b.add_wire(r3_p2_x, r3_p2_y, 96.52, r3_p2_y)
b.add_label('USB_DN', 96.52, r3_p2_y)

dp_a_x, dp_a_y = b.get_pin('J1', 'A6') # (66.04, 68.58)
dp_b_x, dp_b_y = b.get_pin('J1', 'B6') # (66.04, 71.12)
b.add_wire(dp_a_x, dp_a_y, 69.85, dp_a_y)
b.add_wire(dp_b_x, dp_b_y, 69.85, dp_b_y)
b.add_wire(69.85, dp_a_y, 69.85, dp_b_y)
b.add_junction(69.85, (dp_a_y + dp_b_y)/2)

b.add_component(
    ref='R4', lib='Device', name='R',
    val='22R', x=81.28, y=86.36, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r4_p1_x, r4_p1_y = b.get_pin('R4', '1') # (77.47, 86.36)
r4_p2_x, r4_p2_y = b.get_pin('R4', '2') # (85.09, 86.36)
b.add_wire(69.85, (dp_a_y + dp_b_y)/2, 69.85, 86.36)
b.add_wire(69.85, 86.36, r4_p1_x, r4_p1_y)
b.add_wire(r4_p2_x, r4_p2_y, 96.52, r4_p2_y)
b.add_label('USB_DP', 96.52, r4_p2_y)

# SBU pins: A8, B8
sbu1_x, sbu1_y = b.get_pin('J1', 'A8')
sbu2_x, sbu2_y = b.get_pin('J1', 'B8')
b.add_no_connect(sbu1_x, sbu1_y)
b.add_no_connect(sbu2_x, sbu2_y)


# ==============================================================================
# BLOCK 2: Li-Ion CHARGER (TP4056) & BATTERY CONNECTOR
# ==============================================================================
b.add_box(121.92, 25.4, 231.14, 114.3, "2. Li-Ion/LiPo CHARGER (TP4056) & JST-PH PORT")

# U1: TP4056
b.add_component(
    ref='U1', lib='Battery_Management', name='TP4056-42-ESOP8',
    val='TP4056', x=165.1, y=66.04, rot=0,
    fp='Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm'
)

# VCC (Pin 4) & CE (Pin 8)
tp_vcc_x, tp_vcc_y = b.get_pin('U1', '4') # (165.1, 53.34)
tp_ce_x, tp_ce_y = b.get_pin('U1', '8')   # (154.94, 60.96)
b.add_power('VBUS', tp_vcc_x, tp_vcc_y - 7.62)
b.add_wire(tp_vcc_x, tp_vcc_y, tp_vcc_x, tp_vcc_y - 7.62)
b.add_wire(tp_ce_x, tp_ce_y, tp_ce_x, tp_vcc_y - 3.81)
b.add_wire(tp_ce_x, tp_vcc_y - 3.81, tp_vcc_x, tp_vcc_y - 3.81)
b.add_junction(tp_vcc_x, tp_vcc_y - 3.81)

# GND (Pin 3) & EPAD (Pin 9)
tp_gnd_x, tp_gnd_y = b.get_pin('U1', '3')   # (165.1, 78.74)
tp_epad_x, tp_epad_y = b.get_pin('U1', '9') # (162.56, 78.74)
b.add_wire(tp_epad_x, tp_epad_y, tp_gnd_x, tp_gnd_y)
b.add_junction(tp_gnd_x, tp_gnd_y)
b.add_power('GND', tp_gnd_x, tp_gnd_y + 5.08)
b.add_wire(tp_gnd_x, tp_gnd_y, tp_gnd_x, tp_gnd_y + 5.08)

# TEMP (Pin 1) to GND
tp_temp_x, tp_temp_y = b.get_pin('U1', '1') # (175.26, 66.04)
b.add_power('GND', tp_temp_x + 5.08, tp_temp_y)
b.add_wire(tp_temp_x, tp_temp_y, tp_temp_x + 5.08, tp_temp_y)

# PROG (Pin 2) -> R5 (2.4k) -> GND (sets 500mA charge current)
tp_prog_x, tp_prog_y = b.get_pin('U1', '2') # (175.26, 68.58)
b.add_component(
    ref='R5', lib='Device', name='R',
    val='2.4k (500mA)', x=185.42, y=68.58, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r5_p1_x, r5_p1_y = b.get_pin('R5', '1')
r5_p2_x, r5_p2_y = b.get_pin('R5', '2')
b.add_wire(tp_prog_x, tp_prog_y, r5_p1_x, r5_p1_y)
b.add_power('GND', r5_p2_x + 5.08, r5_p2_y)
b.add_wire(r5_p2_x, r5_p2_y, r5_p2_x + 5.08, r5_p2_y)

# CHRG (Pin 7) -> LED1 (Red) -> R6 (1k) -> VBUS
tp_chrg_x, tp_chrg_y = b.get_pin('U1', '7') # (154.94, 66.04)
b.add_component(
    ref='LED1', lib='Device', name='LED',
    val='RED (CHRG)', x=142.24, y=66.04, rot=180,
    fp='LED_SMD:LED_0805_2012Metric'
)
led1_k_x, led1_k_y = b.get_pin('LED1', '1')
led1_a_x, led1_a_y = b.get_pin('LED1', '2')
b.add_wire(tp_chrg_x, tp_chrg_y, led1_k_x, led1_k_y)

b.add_component(
    ref='R6', lib='Device', name='R',
    val='1k', x=132.08, y=66.04, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r6_p1_x, r6_p1_y = b.get_pin('R6', '1')
r6_p2_x, r6_p2_y = b.get_pin('R6', '2')
b.add_wire(led1_a_x, led1_a_y, r6_p2_x, r6_p2_y)
b.add_power('VBUS', r6_p1_x - 3.81, r6_p1_y)
b.add_wire(r6_p1_x, r6_p1_y, r6_p1_x - 3.81, r6_p1_y)

# STDBY (Pin 6) -> LED2 (Green) -> R7 (1k) -> VBUS
tp_stdby_x, tp_stdby_y = b.get_pin('U1', '6') # (154.94, 68.58)
b.add_component(
    ref='LED2', lib='Device', name='LED',
    val='GREEN (DONE)', x=142.24, y=74.93, rot=180,
    fp='LED_SMD:LED_0805_2012Metric'
)
led2_k_x, led2_k_y = b.get_pin('LED2', '1')
led2_a_x, led2_a_y = b.get_pin('LED2', '2')
b.add_wire(tp_stdby_x, tp_stdby_y, tp_stdby_x - 3.81, tp_stdby_y)
b.add_wire(tp_stdby_x - 3.81, tp_stdby_y, tp_stdby_x - 3.81, led2_k_y)
b.add_wire(tp_stdby_x - 3.81, led2_k_y, led2_k_x, led2_k_y)

b.add_component(
    ref='R7', lib='Device', name='R',
    val='1k', x=132.08, y=74.93, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r7_p1_x, r7_p1_y = b.get_pin('R7', '1')
r7_p2_x, r7_p2_y = b.get_pin('R7', '2')
b.add_wire(led2_a_x, led2_a_y, r7_p2_x, r7_p2_y)
b.add_power('VBUS', r7_p1_x - 3.81, r7_p1_y)
b.add_wire(r7_p1_x, r7_p1_y, r7_p1_x - 3.81, r7_p1_y)

# BAT (Pin 5) -> Battery + rail
tp_bat_x, tp_bat_y = b.get_pin('U1', '5') # (175.26, 60.96)
b.add_wire(tp_bat_x, tp_bat_y, 198.12, tp_bat_y)
b.add_junction(198.12, tp_bat_y)

# C3 (10uF) on BAT
b.add_component(
    ref='C3', lib='Device', name='C',
    val='10uF 10V', x=198.12, y=74.93, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c3_p1_x, c3_p1_y = b.get_pin('C3', '1')
c3_p2_x, c3_p2_y = b.get_pin('C3', '2')
b.add_wire(198.12, tp_bat_y, c3_p1_x, c3_p1_y)
b.add_power('GND', c3_p2_x, c3_p2_y + 5.08)
b.add_wire(c3_p2_x, c3_p2_y, c3_p2_x, c3_p2_y + 5.08)

# Connect to J2 Battery Connector (JST-PH 2-pin)
b.add_component(
    ref='J2', lib='Connector_Generic', name='Conn_01x02',
    val='JST-PH (3.7V LiPo)', x=218.44, y=63.5, rot=180,
    fp='Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal'
)
j2_p1_x, j2_p1_y = b.get_pin('J2', '1') # (223.52, 63.5)
j2_p2_x, j2_p2_y = b.get_pin('J2', '2') # (223.52, 66.04)

b.add_wire(198.12, tp_bat_y, 210.82, tp_bat_y)
b.add_wire(210.82, tp_bat_y, 210.82, j2_p1_y)
b.add_wire(210.82, j2_p1_y, j2_p1_x, j2_p1_y)
b.add_junction(210.82, tp_bat_y)

# Label on VBAT (TP4056 BAT is power_out, no PWR_FLAG needed)
b.add_power('VBAT', 210.82, 50.8)
b.add_wire(210.82, tp_bat_y, 210.82, 50.8)

# J2 Pin 2 to GND
b.add_power('GND', j2_p2_x + 3.81, j2_p2_y)
b.add_wire(j2_p2_x, j2_p2_y, j2_p2_x + 3.81, j2_p2_y)


# ==============================================================================
# BLOCK 3: POWER-PATH (AO3401A) & 3.3V LDO REGULATOR (AP2112K)
# ==============================================================================
b.add_box(238.76, 25.4, 396.24, 114.3, "3. POWER-PATH AUTO-SWITCHING & 3.3V LDO REGULATOR")

# Q1: AO3401A P-MOSFET (SOT-23)
b.add_component(
    ref='Q1', lib='Transistor_FET', name='AO3401A',
    val='AO3401A (-30V -4A)', x=261.62, y=66.04, rot=0,
    fp='Package_TO_SOT_SMD:SOT-23'
)
q1_g_x, q1_g_y = b.get_pin('Q1', '1') # (256.54, 66.04)
q1_s_x, q1_s_y = b.get_pin('Q1', '2') # (264.16, 71.12)
q1_d_x, q1_d_y = b.get_pin('Q1', '3') # (264.16, 60.96)

# Source connects to VBAT (+BATT)
b.add_power('VBAT', q1_s_x, q1_s_y + 7.62, rot=180)
b.add_wire(q1_s_x, q1_s_y, q1_s_x, q1_s_y + 7.62)

# Gate connects to VBUS and has R8 (100k) pull-down to GND
b.add_power('VBUS', q1_g_x - 7.62, q1_g_y - 7.62)
b.add_wire(q1_g_x, q1_g_y, q1_g_x - 7.62, q1_g_y)
b.add_wire(q1_g_x - 7.62, q1_g_y, q1_g_x - 7.62, q1_g_y - 7.62)
b.add_junction(q1_g_x - 7.62, q1_g_y)

b.add_component(
    ref='R8', lib='Device', name='R',
    val='100k', x=q1_g_x - 7.62, y=q1_g_y + 11.43, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r8_p1_x, r8_p1_y = b.get_pin('R8', '1')
r8_p2_x, r8_p2_y = b.get_pin('R8', '2')
b.add_wire(q1_g_x - 7.62, q1_g_y, r8_p1_x, r8_p1_y)
b.add_power('GND', r8_p2_x, r8_p2_y + 5.08)
b.add_wire(r8_p2_x, r8_p2_y, r8_p2_x, r8_p2_y + 5.08)

# D1: Schottky Diode SS14 between VBUS and VSYS (rot=180: A at x-3.81, K at x+3.81)
b.add_component(
    ref='D1', lib='Device', name='D_Schottky',
    val='SS14 (1A Schottky)', x=261.62, y=50.8, rot=180,
    fp='Diode_SMD:D_SOD-123'
)
d1_k_x, d1_k_y = b.get_pin('D1', '1') # (265.43, 50.8)
d1_a_x, d1_a_y = b.get_pin('D1', '2') # (257.81, 50.8)
b.add_power('VBUS', d1_a_x - 5.08, d1_a_y)
b.add_wire(d1_a_x, d1_a_y, d1_a_x - 5.08, d1_a_y)

# Join Drain of Q1 and Cathode of D1 into VSYS rail
b.add_wire(d1_k_x, d1_k_y, 274.32, d1_k_y)
b.add_wire(q1_d_x, q1_d_y, 274.32, q1_d_y)
b.add_wire(274.32, d1_k_y, 274.32, q1_d_y)
vsys_node_y = 55.88
b.add_junction(274.32, vsys_node_y)
b.add_label('VSYS', 274.32, vsys_node_y - 5.08, justify='left bottom')
b.add_wire(274.32, vsys_node_y, 274.32, vsys_node_y - 5.08)

# VSYS Capacitors C4 (10uF) and C5 (100nF)
b.add_component(
    ref='C4', lib='Device', name='C',
    val='10uF 10V', x=284.48, y=66.04, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c4_p1_x, c4_p1_y = b.get_pin('C4', '1')
c4_p2_x, c4_p2_y = b.get_pin('C4', '2')
b.add_wire(274.32, vsys_node_y, c4_p1_x, vsys_node_y)
b.add_wire(c4_p1_x, vsys_node_y, c4_p1_x, c4_p1_y)
b.add_junction(c4_p1_x, vsys_node_y)
b.add_power('GND', c4_p2_x, c4_p2_y + 5.08)
b.add_wire(c4_p2_x, c4_p2_y, c4_p2_x, c4_p2_y + 5.08)

b.add_component(
    ref='C5', lib='Device', name='C',
    val='100nF', x=294.64, y=66.04, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c5_p1_x, c5_p1_y = b.get_pin('C5', '1')
c5_p2_x, c5_p2_y = b.get_pin('C5', '2')
b.add_wire(c4_p1_x, vsys_node_y, c5_p1_x, vsys_node_y)
b.add_wire(c5_p1_x, vsys_node_y, c5_p1_x, c5_p1_y)
b.add_junction(c5_p1_x, vsys_node_y)
b.add_power('GND', c5_p2_x, c5_p2_y + 5.08)
b.add_wire(c5_p2_x, c5_p2_y, c5_p2_x, c5_p2_y + 5.08)

# Power Switch SW1 (SPDT Slide Switch)
b.add_component(
    ref='SW1', lib='Switch', name='SW_SPDT',
    val='PWR_SWITCH', x=312.42, y=60.96, rot=0,
    fp='Button_Switch_SMD:SW_SPDT_PCM12'
)
sw1_a_x, sw1_a_y = b.get_pin('SW1', '1') # (317.5, 58.42) - ON
sw1_b_x, sw1_b_y = b.get_pin('SW1', '2') # (307.34, 60.96) - Common
sw1_c_x, sw1_c_y = b.get_pin('SW1', '3') # (317.5, 63.5) - OFF

# Connect Common of SW1 to VSYS
b.add_wire(c5_p1_x, vsys_node_y, sw1_b_x, vsys_node_y)
b.add_wire(sw1_b_x, vsys_node_y, sw1_b_x, sw1_b_y)

# Off position to 100k pull-down
b.add_component(
    ref='R9', lib='Device', name='R',
    val='100k', x=317.5, y=74.93, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r9_p1_x, r9_p1_y = b.get_pin('R9', '1')
r9_p2_x, r9_p2_y = b.get_pin('R9', '2')
b.add_wire(sw1_c_x, sw1_c_y, r9_p1_x, r9_p1_y)
b.add_power('GND', r9_p2_x, r9_p2_y + 5.08)
b.add_wire(r9_p2_x, r9_p2_y, r9_p2_x, r9_p2_y + 5.08)

# U2: AP2112K-3.3 (SOT-23-5)
b.add_component(
    ref='U2', lib='Regulator_Linear', name='AP2112K-3.3',
    val='AP2112K-3.3 (600mA)', x=337.82, y=60.96, rot=0,
    fp='Package_TO_SOT_SMD:SOT-23-5'
)
ldo_vin_x, ldo_vin_y = b.get_pin('U2', '1') # (330.2, 58.42)
ldo_en_x, ldo_en_y = b.get_pin('U2', '3')   # (330.2, 60.96)
ldo_gnd_x, ldo_gnd_y = b.get_pin('U2', '2') # (337.82, 68.58)
ldo_nc_x, ldo_nc_y = b.get_pin('U2', '4')   # (342.9, 60.96)
ldo_vout_x, ldo_vout_y = b.get_pin('U2', '5') # (345.44, 58.42)

# SW1 ON terminal (sw1_a) feeds both VIN and EN
b.add_wire(sw1_a_x, sw1_a_y, ldo_vin_x, ldo_vin_y)
b.add_wire(ldo_vin_x, ldo_vin_y, ldo_vin_x, ldo_en_y)
b.add_wire(ldo_vin_x, ldo_en_y, ldo_en_x, ldo_en_y)
b.add_junction(ldo_vin_x, ldo_en_y)
b.add_pwr_flag(ldo_vin_x, ldo_vin_y - 5.08)
b.add_wire(ldo_vin_x, ldo_vin_y, ldo_vin_x, ldo_vin_y - 5.08)

# GND & NC
b.add_power('GND', ldo_gnd_x, ldo_gnd_y + 5.08)
b.add_wire(ldo_gnd_x, ldo_gnd_y, ldo_gnd_x, ldo_gnd_y + 5.08)
b.add_no_connect(ldo_nc_x, ldo_nc_y)

# VOUT Rail (+3.3V) - AP2112K VOUT is power_out!
b.add_wire(ldo_vout_x, ldo_vout_y, 358.14, ldo_vout_y)
b.add_junction(358.14, ldo_vout_y)
b.add_power('+3.3V', 358.14, ldo_vout_y - 7.62)
b.add_wire(358.14, ldo_vout_y, 358.14, ldo_vout_y - 7.62)

# C6 (10uF Ceramic)
b.add_component(
    ref='C6', lib='Device', name='C',
    val='10uF 10V', x=365.76, y=68.58, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c6_p1_x, c6_p1_y = b.get_pin('C6', '1')
c6_p2_x, c6_p2_y = b.get_pin('C6', '2')
b.add_wire(358.14, ldo_vout_y, c6_p1_x, ldo_vout_y)
b.add_wire(c6_p1_x, ldo_vout_y, c6_p1_x, c6_p1_y)
b.add_junction(c6_p1_x, ldo_vout_y)
b.add_power('GND', c6_p2_x, c6_p2_y + 5.08)
b.add_wire(c6_p2_x, c6_p2_y, c6_p2_x, c6_p2_y + 5.08)

# C7 (100uF Tantalum Bulk Capacitor)
b.add_component(
    ref='C7', lib='Device', name='C_Polarized',
    val='100uF 6.3V (Bulk)', x=375.92, y=68.58, rot=0,
    fp='Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B'
)
c7_p1_x, c7_p1_y = b.get_pin('C7', '1')
c7_p2_x, c7_p2_y = b.get_pin('C7', '2')
b.add_wire(c6_p1_x, ldo_vout_y, c7_p1_x, ldo_vout_y)
b.add_wire(c7_p1_x, ldo_vout_y, c7_p1_x, c7_p1_y)
b.add_junction(c7_p1_x, ldo_vout_y)
b.add_power('GND', c7_p2_x, c7_p2_y + 5.08)
b.add_wire(c7_p2_x, c7_p2_y, c7_p2_x, c7_p2_y + 5.08)

# C8 (100nF High Freq Decoupling)
b.add_component(
    ref='C8', lib='Device', name='C',
    val='100nF', x=386.08, y=68.58, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c8_p1_x, c8_p1_y = b.get_pin('C8', '1')
c8_p2_x, c8_p2_y = b.get_pin('C8', '2')
b.add_wire(c7_p1_x, ldo_vout_y, c8_p1_x, ldo_vout_y)
b.add_wire(c8_p1_x, ldo_vout_y, c8_p1_x, c8_p1_y)
b.add_junction(c8_p1_x, ldo_vout_y)
b.add_power('GND', c8_p2_x, c8_p2_y + 5.08)
b.add_wire(c8_p2_x, c8_p2_y, c8_p2_x, c8_p2_y + 5.08)

# LED3 (Blue Power Indicator) & R10 (1k)
b.add_component(
    ref='LED3', lib='Device', name='LED',
    val='BLUE (3V3 PWR)', x=386.08, y=88.9, rot=0,
    fp='LED_SMD:LED_0805_2012Metric'
)
led3_k_x, led3_k_y = b.get_pin('LED3', '1') # (382.27, 88.9)
led3_a_x, led3_a_y = b.get_pin('LED3', '2') # (389.89, 88.9)
b.add_power('+3.3V', led3_a_x + 3.81, led3_a_y)
b.add_wire(led3_a_x, led3_a_y, led3_a_x + 3.81, led3_a_y)

b.add_component(
    ref='R10', lib='Device', name='R',
    val='1k', x=373.38, y=88.9, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r10_p1_x, r10_p1_y = b.get_pin('R10', '1')
r10_p2_x, r10_p2_y = b.get_pin('R10', '2')
b.add_wire(led3_k_x, led3_k_y, r10_p2_x, r10_p2_y)
b.add_power('GND', r10_p1_x - 3.81, r10_p1_y)
b.add_wire(r10_p1_x, r10_p1_y, r10_p1_x - 3.81, r10_p1_y)


# ==============================================================================
# BLOCK 4: USB-UART BRIDGE (CH340C) & AUTO-PROGRAMMING (DTR/RTS)
# ==============================================================================
b.add_box(25.4, 127.0, 172.72, 266.7, "4. USB-TO-UART BRIDGE (CH340C) & AUTO-DOWNLOAD")

# U3: CH340C (SOIC-16)
# Power CH340C from VBUS (5V), V3 has 100nF to GND
b.add_component(
    ref='U3', lib='Interface_USB', name='CH340C',
    val='CH340C', x=76.2, y=177.8, rot=0,
    fp='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm'
)
ch_gnd_x, ch_gnd_y = b.get_pin('U3', '1')     # (76.2, 193.04)
ch_txd_x, ch_txd_y = b.get_pin('U3', '2')     # (86.36, 167.64)
ch_rxd_x, ch_rxd_y = b.get_pin('U3', '3')     # (86.36, 170.18)
ch_v3_x, ch_v3_y = b.get_pin('U3', '4')       # (76.2, 162.56)
ch_udp_x, ch_udp_y = b.get_pin('U3', '5')     # (66.04, 175.26)
ch_udm_x, ch_udm_y = b.get_pin('U3', '6')     # (66.04, 177.8)
ch_nc7_x, ch_nc7_y = b.get_pin('U3', '7')
ch_nc8_x, ch_nc8_y = b.get_pin('U3', '8')
ch_cts_x, ch_cts_y = b.get_pin('U3', '9')
ch_dsr_x, ch_dsr_y = b.get_pin('U3', '10')
ch_ri_x, ch_ri_y = b.get_pin('U3', '11')
ch_dcd_x, ch_dcd_y = b.get_pin('U3', '12')
ch_dtr_x, ch_dtr_y = b.get_pin('U3', '13')   # (86.36, 185.42)
ch_rts_x, ch_rts_y = b.get_pin('U3', '14')   # (86.36, 187.96)
ch_r232_x, ch_r232_y = b.get_pin('U3', '15')
ch_vcc_x, ch_vcc_y = b.get_pin('U3', '16')   # (73.66, 162.56)

# VCC connected to VBUS (+5V USB)
b.add_power('VBUS', ch_vcc_x, ch_vcc_y - 7.62)
b.add_wire(ch_vcc_x, ch_vcc_y, ch_vcc_x, ch_vcc_y - 7.62)

# V3 has 100nF capacitor to GND (internal 3.3V LDO filter for 5V operation)
b.add_component(
    ref='C14', lib='Device', name='C',
    val='100nF', x=81.28, y=152.4, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c14_p1_x, c14_p1_y = b.get_pin('C14', '1') # (81.28, 148.59)
c14_p2_x, c14_p2_y = b.get_pin('C14', '2') # (81.28, 156.21)
b.add_wire(ch_v3_x, ch_v3_y, c14_p2_x, ch_v3_y)
b.add_wire(c14_p2_x, ch_v3_y, c14_p2_x, c14_p2_y)
b.add_power('GND', c14_p1_x, c14_p1_y - 3.81, rot=180)
b.add_wire(c14_p1_x, c14_p1_y, c14_p1_x, c14_p1_y - 3.81)

# GND
b.add_power('GND', ch_gnd_x, ch_gnd_y + 5.08)
b.add_wire(ch_gnd_x, ch_gnd_y, ch_gnd_x, ch_gnd_y + 5.08)

# Decoupling Cap C9 (100nF) on VCC
b.add_component(
    ref='C9', lib='Device', name='C',
    val='100nF', x=63.5, y=162.56, rot=90,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c9_p1_x, c9_p1_y = b.get_pin('C9', '1') # (59.69, 162.56)
c9_p2_x, c9_p2_y = b.get_pin('C9', '2') # (67.31, 162.56)
b.add_wire(ch_vcc_x, ch_vcc_y, c9_p2_x, c9_p2_y)
b.add_power('GND', c9_p1_x - 3.81, c9_p1_y)
b.add_wire(c9_p1_x, c9_p1_y, c9_p1_x - 3.81, c9_p1_y)

# USB DP / DN
b.add_label('USB_DP', ch_udp_x, ch_udp_y, rot=180, justify='right bottom')
b.add_label('USB_DN', ch_udm_x, ch_udm_y, rot=180, justify='right bottom')

# Unused pins marked no-connect
for ncx, ncy in [
    (ch_nc7_x, ch_nc7_y), (ch_nc8_x, ch_nc8_y),
    (ch_cts_x, ch_cts_y), (ch_dsr_x, ch_dsr_y),
    (ch_ri_x, ch_ri_y), (ch_dcd_x, ch_dcd_y),
    (ch_r232_x, ch_r232_y)
]:
    b.add_no_connect(ncx, ncy)

# TXD / RXD series damping resistors R11 & R12 (470R)
b.add_component(
    ref='R11', lib='Device', name='R',
    val='470R', x=99.06, y=ch_txd_y, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r11_p1_x, r11_p1_y = b.get_pin('R11', '1')
r11_p2_x, r11_p2_y = b.get_pin('R11', '2')
b.add_wire(ch_txd_x, ch_txd_y, r11_p1_x, r11_p1_y)
b.add_wire(r11_p2_x, r11_p2_y, 114.3, r11_p2_y)
b.add_label('ESP_RXD', 114.3, r11_p2_y)

b.add_component(
    ref='R12', lib='Device', name='R',
    val='470R', x=99.06, y=ch_rxd_y, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r12_p1_x, r12_p1_y = b.get_pin('R12', '1')
r12_p2_x, r12_p2_y = b.get_pin('R12', '2')
b.add_wire(ch_rxd_x, ch_rxd_y, r12_p1_x, r12_p1_y)
b.add_wire(r12_p2_x, r12_p2_y, 114.3, r12_p2_y)
b.add_label('ESP_TXD', 114.3, r12_p2_y)

# DTR & RTS
b.add_wire(ch_dtr_x, ch_dtr_y, 96.52, ch_dtr_y)
b.add_label('DTR', 96.52, ch_dtr_y)

b.add_wire(ch_rts_x, ch_rts_y, 96.52, ch_rts_y)
b.add_label('RTS', 96.52, ch_rts_y)

# Auto-Download Circuit (Q2 & Q3)
b.add_component(
    ref='Q2', lib='Transistor_BJT', name='Q_NPN_BEC',
    val='MMBT3904', x=142.24, y=177.8, rot=0,
    fp='Package_TO_SOT_SMD:SOT-23'
)
q2_b_x, q2_b_y = b.get_pin('Q2', '1') # (137.16, 177.8)
q2_e_x, q2_e_y = b.get_pin('Q2', '2') # (144.78, 182.88)
q2_c_x, q2_c_y = b.get_pin('Q2', '3') # (144.78, 172.72)

b.add_component(
    ref='R13', lib='Device', name='R',
    val='10k', x=127.0, y=177.8, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r13_p1_x, r13_p1_y = b.get_pin('R13', '1')
r13_p2_x, r13_p2_y = b.get_pin('R13', '2')
b.add_label('RTS', r13_p1_x - 2.54, r13_p1_y, rot=180, justify='right bottom')
b.add_wire(r13_p1_x, r13_p1_y, r13_p1_x - 2.54, r13_p1_y)
b.add_wire(r13_p2_x, r13_p2_y, q2_b_x, q2_b_y)

b.add_label('DTR', q2_e_x + 7.62, q2_e_y)
b.add_wire(q2_e_x, q2_e_y, q2_e_x + 7.62, q2_e_y)

b.add_label('ESP_RST', q2_c_x + 7.62, q2_c_y)
b.add_wire(q2_c_x, q2_c_y, q2_c_x + 7.62, q2_c_y)

# Q3
b.add_component(
    ref='Q3', lib='Transistor_BJT', name='Q_NPN_BEC',
    val='MMBT3904', x=142.24, y=208.28, rot=0,
    fp='Package_TO_SOT_SMD:SOT-23'
)
q3_b_x, q3_b_y = b.get_pin('Q3', '1') # (137.16, 208.28)
q3_e_x, q3_e_y = b.get_pin('Q3', '2') # (144.78, 213.36)
q3_c_x, q3_c_y = b.get_pin('Q3', '3') # (144.78, 203.2)

b.add_component(
    ref='R14', lib='Device', name='R',
    val='10k', x=127.0, y=208.28, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r14_p1_x, r14_p1_y = b.get_pin('R14', '1')
r14_p2_x, r14_p2_y = b.get_pin('R14', '2')
b.add_label('DTR', r14_p1_x - 2.54, r14_p1_y, rot=180, justify='right bottom')
b.add_wire(r14_p1_x, r14_p1_y, r14_p1_x - 2.54, r14_p1_y)
b.add_wire(r14_p2_x, r14_p2_y, q3_b_x, q3_b_y)

b.add_label('RTS', q3_e_x + 7.62, q3_e_y)
b.add_wire(q3_e_x, q3_e_y, q3_e_x + 7.62, q3_e_y)

b.add_label('ESP_IO0', q3_c_x + 7.62, q3_c_y)
b.add_wire(q3_c_x, q3_c_y, q3_c_x + 7.62, q3_c_y)

# Manual Buttons SW2 (RESET) and SW3 (FLASH)
b.add_component(
    ref='SW2', lib='Switch', name='SW_Push',
    val='SW_RESET', x=50.8, y=236.22, rot=0,
    fp='Button_Switch_SMD:SW_SPST_PTS645Sx43SMTR92'
)
sw2_p1_x, sw2_p1_y = b.get_pin('SW2', '1') # (45.72, 236.22)
sw2_p2_x, sw2_p2_y = b.get_pin('SW2', '2') # (55.88, 236.22)
b.add_label('ESP_RST', sw2_p1_x - 5.08, sw2_p1_y, rot=180, justify='right bottom')
b.add_wire(sw2_p1_x, sw2_p1_y, sw2_p1_x - 5.08, sw2_p1_y)
b.add_power('GND', sw2_p2_x + 3.81, sw2_p2_y)
b.add_wire(sw2_p2_x, sw2_p2_y, sw2_p2_x + 3.81, sw2_p2_y)

b.add_component(
    ref='SW3', lib='Switch', name='SW_Push',
    val='SW_FLASH', x=101.6, y=236.22, rot=0,
    fp='Button_Switch_SMD:SW_SPST_PTS645Sx43SMTR92'
)
sw3_p1_x, sw3_p1_y = b.get_pin('SW3', '1')
sw3_p2_x, sw3_p2_y = b.get_pin('SW3', '2')
b.add_label('ESP_IO0', sw3_p1_x - 5.08, sw3_p1_y, rot=180, justify='right bottom')
b.add_wire(sw3_p1_x, sw3_p1_y, sw3_p1_x - 5.08, sw3_p1_y)
b.add_power('GND', sw3_p2_x + 3.81, sw3_p2_y)
b.add_wire(sw3_p2_x, sw3_p2_y, sw3_p2_x + 3.81, sw3_p2_y)


# ==============================================================================
# BLOCK 5: ESP8266 (ESP-12F) MODULE & BOOT STRAPPING
# ==============================================================================
b.add_box(180.34, 127.0, 307.34, 266.7, "5. ESP8266 (ESP-12F) MODULE & STRAPPING")

# U4: ESP-12F
b.add_component(
    ref='U4', lib='RF_Module', name='ESP-12F',
    val='ESP-12F', x=243.84, y=193.04, rot=0,
    fp='RF_Module:ESP-12E'
)

esp_rst_x, esp_rst_y = b.get_pin('U4', '1')     # (228.6, 177.8)
esp_adc_x, esp_adc_y = b.get_pin('U4', '2')     # (228.6, 187.96)
esp_en_x, esp_en_y = b.get_pin('U4', '3')       # (228.6, 182.88)
esp_vcc_x, esp_vcc_y = b.get_pin('U4', '8')     # (243.84, 172.72)
esp_gnd_x, esp_gnd_y = b.get_pin('U4', '15')   # (243.84, 210.82)
esp_io16_x, esp_io16_y = b.get_pin('U4', '4')   # (259.08, 203.2)
esp_io14_x, esp_io14_y = b.get_pin('U4', '5')   # (259.08, 198.12)
esp_io12_x, esp_io12_y = b.get_pin('U4', '6')   # (259.08, 193.04)
esp_io13_x, esp_io13_y = b.get_pin('U4', '7')   # (259.08, 195.58)
esp_io15_x, esp_io15_y = b.get_pin('U4', '16') # (259.08, 200.66)
esp_io2_x, esp_io2_y = b.get_pin('U4', '17')   # (259.08, 182.88)
esp_io0_x, esp_io0_y = b.get_pin('U4', '18')   # (259.08, 177.8)
esp_io4_x, esp_io4_y = b.get_pin('U4', '19')   # (259.08, 187.96)
esp_io5_x, esp_io5_y = b.get_pin('U4', '20')   # (259.08, 190.5)
esp_rxd_x, esp_rxd_y = b.get_pin('U4', '21')   # (259.08, 185.42)
esp_txd_x, esp_txd_y = b.get_pin('U4', '22')   # (259.08, 180.34)

# SPI Flash internal pins (no-connect)
for p in ['9', '10', '11', '12', '13', '14']:
    px, py = b.get_pin('U4', p)
    b.add_no_connect(px, py)

# Power & Decoupling
vcc_bus_y = 152.4
b.add_wire(esp_vcc_x, esp_vcc_y, esp_vcc_x, vcc_bus_y)
b.add_power('+3.3V', esp_vcc_x, vcc_bus_y - 5.08)
b.add_wire(esp_vcc_x, vcc_bus_y, esp_vcc_x, vcc_bus_y - 5.08)
b.add_junction(esp_vcc_x, vcc_bus_y)

b.add_component(
    ref='C10', lib='Device', name='C',
    val='10uF', x=236.22, y=160.02, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c10_p1_x, c10_p1_y = b.get_pin('C10', '1') # (236.22, 156.21)
c10_p2_x, c10_p2_y = b.get_pin('C10', '2') # (236.22, 163.83)
b.add_wire(esp_vcc_x, vcc_bus_y, c10_p1_x, vcc_bus_y)
b.add_wire(c10_p1_x, vcc_bus_y, c10_p1_x, c10_p1_y)
b.add_junction(c10_p1_x, vcc_bus_y)
b.add_power('GND', c10_p2_x, 168.91)
b.add_wire(c10_p2_x, c10_p2_y, c10_p2_x, 168.91)

b.add_component(
    ref='C11', lib='Device', name='C',
    val='100nF', x=226.06, y=160.02, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c11_p1_x, c11_p1_y = b.get_pin('C11', '1') # (226.06, 156.21)
c11_p2_x, c11_p2_y = b.get_pin('C11', '2') # (226.06, 163.83)
b.add_wire(c10_p1_x, vcc_bus_y, c11_p1_x, vcc_bus_y)
b.add_wire(c11_p1_x, vcc_bus_y, c11_p1_x, c11_p1_y)
b.add_power('GND', c11_p2_x, 168.91)
b.add_wire(c11_p2_x, c11_p2_y, c11_p2_x, 168.91)

# GND
b.add_power('GND', esp_gnd_x, esp_gnd_y + 5.08)
b.add_wire(esp_gnd_x, esp_gnd_y, esp_gnd_x, esp_gnd_y + 5.08)

# RESET Circuit
b.add_wire(esp_rst_x, esp_rst_y, 213.36, esp_rst_y)
b.add_label('ESP_RST', 213.36, esp_rst_y, rot=180, justify='right bottom')
b.add_junction(213.36, esp_rst_y)

b.add_component(
    ref='R15', lib='Device', name='R',
    val='10k', x=205.74, y=170.18, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r15_p1_x, r15_p1_y = b.get_pin('R15', '1')
r15_p2_x, r15_p2_y = b.get_pin('R15', '2')
b.add_power('+3.3V', r15_p1_x, r15_p1_y - 5.08)
b.add_wire(r15_p1_x, r15_p1_y, r15_p1_x, r15_p1_y - 5.08)
b.add_wire(r15_p2_x, r15_p2_y, 213.36, esp_rst_y)

b.add_component(
    ref='C12', lib='Device', name='C',
    val='100nF (Filter)', x=195.58, y=170.18, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c12_p1_x, c12_p1_y = b.get_pin('C12', '1')
c12_p2_x, c12_p2_y = b.get_pin('C12', '2')
b.add_wire(213.36, esp_rst_y, c12_p1_x, esp_rst_y)
b.add_wire(c12_p1_x, esp_rst_y, c12_p1_x, c12_p1_y)
b.add_power('GND', c12_p2_x, c12_p2_y + 5.08)
b.add_wire(c12_p2_x, c12_p2_y, c12_p2_x, c12_p2_y + 5.08)

# EN Pull-up R16 (10k)
b.add_wire(esp_en_x, esp_en_y, 213.36, esp_en_y)
b.add_label('EN', 213.36, esp_en_y, rot=180, justify='right bottom')
b.add_junction(213.36, esp_en_y)

b.add_component(
    ref='R16', lib='Device', name='R',
    val='10k', x=205.74, y=182.88, rot=90,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r16_p1_x, r16_p1_y = b.get_pin('R16', '1') # (201.93, 182.88)
r16_p2_x, r16_p2_y = b.get_pin('R16', '2') # (209.55, 182.88)
b.add_power('+3.3V', r16_p1_x - 3.81, r16_p1_y)
b.add_wire(r16_p1_x, r16_p1_y, r16_p1_x - 3.81, r16_p1_y)
b.add_wire(r16_p2_x, r16_p2_y, 213.36, esp_en_y)

# ADC
b.add_wire(esp_adc_x, esp_adc_y, 213.36, esp_adc_y)
b.add_label('ESP_ADC', 213.36, esp_adc_y, rot=180, justify='right bottom')

# GPIO0 Pull-up R17 (10k)
b.add_wire(esp_io0_x, esp_io0_y, 274.32, esp_io0_y)
b.add_label('ESP_IO0', 274.32, esp_io0_y)
b.add_junction(274.32, esp_io0_y)

b.add_component(
    ref='R17', lib='Device', name='R',
    val='10k', x=284.48, y=170.18, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r17_p1_x, r17_p1_y = b.get_pin('R17', '1')
r17_p2_x, r17_p2_y = b.get_pin('R17', '2')
b.add_power('+3.3V', r17_p1_x, r17_p1_y - 5.08)
b.add_wire(r17_p1_x, r17_p1_y, r17_p1_x, r17_p1_y - 5.08)
b.add_wire(r17_p2_x, r17_p2_y, 274.32, esp_io0_y)

# GPIO2 Pull-up R18 (10k)
b.add_wire(esp_io2_x, esp_io2_y, 274.32, esp_io2_y)
b.add_label('ESP_IO2', 274.32, esp_io2_y)
b.add_junction(274.32, esp_io2_y)

b.add_component(
    ref='R18', lib='Device', name='R',
    val='10k', x=284.48, y=187.96, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r18_p1_x, r18_p1_y = b.get_pin('R18', '1')
r18_p2_x, r18_p2_y = b.get_pin('R18', '2')
b.add_power('+3.3V', r18_p1_x, r18_p1_y - 5.08)
b.add_wire(r18_p1_x, r18_p1_y, r18_p1_x, r18_p1_y - 5.08)
b.add_wire(r18_p2_x, r18_p2_y, 274.32, esp_io2_y)

# GPIO15 Pull-down R19 (10k)
b.add_wire(esp_io15_x, esp_io15_y, 274.32, esp_io15_y)
b.add_label('ESP_IO15', 274.32, esp_io15_y)
b.add_junction(274.32, esp_io15_y)

b.add_component(
    ref='R19', lib='Device', name='R',
    val='10k', x=284.48, y=208.28, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r19_p1_x, r19_p1_y = b.get_pin('R19', '1')
r19_p2_x, r19_p2_y = b.get_pin('R19', '2')
b.add_power('GND', r19_p2_x, r19_p2_y + 5.08)
b.add_wire(r19_p2_x, r19_p2_y, r19_p2_x, r19_p2_y + 5.08)
b.add_wire(r19_p1_x, r19_p1_y, 274.32, esp_io15_y)

# Other GPIO labels
b.add_wire(esp_txd_x, esp_txd_y, 269.24, esp_txd_y)
b.add_label('ESP_TXD', 269.24, esp_txd_y)

b.add_wire(esp_rxd_x, esp_rxd_y, 269.24, esp_rxd_y)
b.add_label('ESP_RXD', 269.24, esp_rxd_y)

b.add_wire(esp_io4_x, esp_io4_y, 269.24, esp_io4_y)
b.add_label('ESP_IO4', 269.24, esp_io4_y)

b.add_wire(esp_io5_x, esp_io5_y, 269.24, esp_io5_y)
b.add_label('ESP_IO5', 269.24, esp_io5_y)

b.add_wire(esp_io12_x, esp_io12_y, 269.24, esp_io12_y)
b.add_label('ESP_IO12', 269.24, esp_io12_y)

b.add_wire(esp_io13_x, esp_io13_y, 269.24, esp_io13_y)
b.add_label('ESP_IO13', 269.24, esp_io13_y)

b.add_wire(esp_io14_x, esp_io14_y, 269.24, esp_io14_y)
b.add_label('ESP_IO14', 269.24, esp_io14_y)

b.add_wire(esp_io16_x, esp_io16_y, 269.24, esp_io16_y)
b.add_label('ESP_IO16', 269.24, esp_io16_y)


# ==============================================================================
# BLOCK 6: BATTERY VOLTAGE ADC MONITOR & BREAKOUT HEADERS
# ==============================================================================
b.add_box(314.96, 127.0, 396.24, 266.7, "6. BATTERY SENSE (ADC) & HEADERS")

# Voltage Divider for Battery Monitoring (0-4.2V -> 0-0.89V for 1.0V ADC)
b.add_component(
    ref='R20', lib='Device', name='R',
    val='100k 1%', x=330.2, y=147.32, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r20_p1_x, r20_p1_y = b.get_pin('R20', '1') # (330.2, 143.51)
r20_p2_x, r20_p2_y = b.get_pin('R20', '2') # (330.2, 151.13)
b.add_power('VBAT', r20_p1_x, r20_p1_y - 5.08)
b.add_wire(r20_p1_x, r20_p1_y, r20_p1_x, r20_p1_y - 5.08)

b.add_component(
    ref='R21', lib='Device', name='R',
    val='27k 1%', x=330.2, y=162.56, rot=0,
    fp='Resistor_SMD:R_0805_2012Metric'
)
r21_p1_x, r21_p1_y = b.get_pin('R21', '1') # (330.2, 158.75)
r21_p2_x, r21_p2_y = b.get_pin('R21', '2') # (330.2, 166.37)
b.add_power('GND', r21_p2_x, r21_p2_y + 5.08)
b.add_wire(r21_p2_x, r21_p2_y, r21_p2_x, r21_p2_y + 5.08)

div_node_y = 154.94
b.add_wire(r20_p2_x, r20_p2_y, r20_p2_x, div_node_y)
b.add_wire(r21_p1_x, r21_p1_y, r21_p1_x, div_node_y)
b.add_junction(r20_p2_x, div_node_y)

# Filter cap C13 (100nF)
b.add_component(
    ref='C13', lib='Device', name='C',
    val='100nF', x=340.36, y=162.56, rot=0,
    fp='Capacitor_SMD:C_0805_2012Metric'
)
c13_p1_x, c13_p1_y = b.get_pin('C13', '1')
c13_p2_x, c13_p2_y = b.get_pin('C13', '2')
b.add_wire(r20_p2_x, div_node_y, c13_p1_x, div_node_y)
b.add_wire(c13_p1_x, div_node_y, c13_p1_x, c13_p1_y)
b.add_junction(c13_p1_x, div_node_y)
b.add_power('GND', c13_p2_x, c13_p2_y + 5.08)
b.add_wire(c13_p2_x, c13_p2_y, c13_p2_x, c13_p2_y + 5.08)

# Solder Jumper JP1 (Connects battery divider to ESP_ADC)
b.add_component(
    ref='JP1', lib='Jumper', name='Jumper_2_Open',
    val='BAT_ADC_EN', x=350.52, y=div_node_y, rot=90,
    fp='Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'
)
jp1_p1_x, jp1_p1_y = b.get_pin('JP1', '1')
jp1_p2_x, jp1_p2_y = b.get_pin('JP1', '2')
b.add_wire(c13_p1_x, div_node_y, jp1_p1_x, jp1_p1_y)
b.add_label('ESP_ADC', jp1_p2_x + 3.81, jp1_p2_y)
b.add_wire(jp1_p2_x, jp1_p2_y, jp1_p2_x + 3.81, jp1_p2_y)

# J3: Left Breakout Header (1x8)
b.add_component(
    ref='J3', lib='Connector_Generic', name='Conn_01x08',
    val='HDR_LEFT (1x8)', x=337.82, y=215.9, rot=0,
    fp='Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical'
)
hdr1_nets = ['ESP_RST', 'ESP_ADC', 'EN', 'ESP_IO16', 'ESP_IO14', 'ESP_IO12', 'ESP_IO13', '+3.3V']
for p_idx, net in enumerate(hdr1_nets, start=1):
    hx, hy = b.get_pin('J3', str(p_idx))
    if net == '+3.3V':
        b.add_power('+3.3V', hx - 5.08, hy, rot=270)
        b.add_wire(hx, hy, hx - 5.08, hy)
    else:
        b.add_label(net, hx - 2.54, hy, rot=180, justify='right bottom')
        b.add_wire(hx, hy, hx - 2.54, hy)

# J4: Right Breakout Header (1x8)
b.add_component(
    ref='J4', lib='Connector_Generic', name='Conn_01x08',
    val='HDR_RIGHT (1x8)', x=375.92, y=215.9, rot=180,
    fp='Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical'
)
hdr2_nets = ['ESP_TXD', 'ESP_RXD', 'ESP_IO5', 'ESP_IO4', 'ESP_IO0', 'ESP_IO2', 'ESP_IO15', 'GND']
for p_idx, net in enumerate(hdr2_nets, start=1):
    hx, hy = b.get_pin('J4', str(p_idx))
    if net == 'GND':
        b.add_power('GND', hx + 5.08, hy, rot=90)
        b.add_wire(hx, hy, hx + 5.08, hy)
    else:
        b.add_label(net, hx + 2.54, hy, rot=0, justify='left bottom')
        b.add_wire(hx, hy, hx + 2.54, hy)

# Write schematic file
b.export(SCH_PATH)
