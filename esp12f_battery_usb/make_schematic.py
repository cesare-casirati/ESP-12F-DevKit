import os
import re
import math
import uuid
import subprocess

SYMBOLS_DIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
PROJECT_DIR = '/Users/mac/.gemini/antigravity/scratch/esp12f_battery_usb'
SCH_PATH = os.path.join(PROJECT_DIR, 'esp12f_battery_usb.kicad_sch')

def new_uuid():
    return str(uuid.uuid4())

def get_raw_symbol(lib, name):
    filepath = os.path.join(SYMBOLS_DIR, f"{lib}.kicad_sym")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    idx = content.find(f'(symbol "{name}"')
    if idx == -1:
        raise ValueError(f"Symbol {name} not found in {lib}")
    depth = 0
    start = idx
    for i in range(start, len(content)):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return content[start:i+1]

def parse_top_level_sexps(s):
    idx = s.find('(')
    if idx == -1: return []
    i = idx + 1
    while i < len(s) and s[i] in ' \t\r\n': i += 1
    while i < len(s) and s[i] not in ' \t\r\n()': i += 1
    while i < len(s) and s[i] in ' \t\r\n': i += 1
    if i < len(s) and s[i] == '"':
        i += 1
        while i < len(s) and s[i] != '"': i += 1
        i += 1
    
    children = []
    while i < len(s):
        while i < len(s) and s[i] in ' \t\r\n': i += 1
        if i >= len(s) or s[i] == ')':
            break
        if s[i] == '(':
            start_child = i
            depth = 0
            while i < len(s):
                if s[i] == '(': depth += 1
                elif s[i] == ')':
                    depth -= 1
                    if depth == 0:
                        child_str = s[start_child:i+1]
                        children.append(child_str)
                        i += 1
                        break
                elif s[i] == '"':
                    i += 1
                    while i < len(s):
                        if s[i] == '"' and s[i-1] != '\\':
                            break
                        i += 1
                i += 1
        else:
            i += 1
    return children

def extract_flat_symbol(lib, name):
    raw = get_raw_symbol(lib, name)
    children = parse_top_level_sexps(raw)
    extends = None
    for c in children:
        if c.startswith('(extends '):
            m = re.search(r'\(extends\s+"([^"]+)"\)', c)
            if m: extends = m.group(1)
            break
            
    if not extends:
        return re.sub(r'^\(symbol\s+"' + re.escape(name) + r'"', f'(symbol "{lib}:{name}"', raw, count=1)
        
    base_raw = get_raw_symbol(lib, extends)
    base_children = parse_top_level_sexps(base_raw)
    
    out_parts = [f'(symbol "{lib}:{name}"']
    for c in base_children:
        if any(c.startswith(f'({k}') for k in ['pin_names', 'pin_numbers', 'exclude_from_sim', 'in_bom', 'on_board', 'in_pos_files', 'duplicate_pin_numbers_are_jumpers']):
            out_parts.append('  ' + c)
            
    for c in children:
        if c.startswith('(property '):
            out_parts.append('  ' + c)
            
    for c in base_children:
        if c.startswith('(symbol '):
            renamed = re.sub(r'^\(symbol\s+"' + re.escape(extends) + r'_', f'(symbol "{name}_', c, count=1)
            out_parts.append('  ' + renamed)
            
    out_parts.append('  (embedded_fonts no)')
    out_parts.append(')')
    return '\n'.join(out_parts)

# Parser for symbol pin offsets
def parse_symbol_pins(lib_name, sym_name):
    filepath = os.path.join(SYMBOLS_DIR, f'{lib_name}.kicad_sym')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    idx = content.find(f'(symbol "{sym_name}"')
    if idx == -1:
        return {}
    depth = 0
    start = idx
    end = -1
    for i in range(start, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    sym_body = content[start:end]
    m_ext = re.search(r'\(extends "([^"]+)"\)', sym_body)
    if m_ext:
        return parse_symbol_pins(lib_name, m_ext.group(1))
    
    pins = {}
    matches = re.findall(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\).*?\(name\s+"([^"]*)".*?\(number\s+"([^"]*)"', sym_body, re.DOTALL)
    for m in matches:
        ptype, px, py, prot, pname, pnum = m
        pins[pnum] = {
            'name': pname,
            'type': ptype,
            'dx': float(px),
            'dy': float(py),
            'rot': float(prot)
        }
    return pins

def get_pin_pos(sym_x, sym_y, pin_dx, pin_dy, rot_deg=0):
    rad = math.radians(rot_deg)
    cos_a = round(math.cos(rad))
    sin_a = round(math.sin(rad))
    rx = pin_dx * cos_a - pin_dy * sin_a
    ry = pin_dx * sin_a + pin_dy * cos_a
    return round(sym_x + rx, 2), round(sym_y - ry, 2)

class SchematicBuilder:
    def __init__(self, sch_uuid=None):
        self.sch_uuid = sch_uuid or new_uuid()
        self.lib_symbols = {}
        self.symbol_instances = []
        self.wires = []
        self.junctions = set()
        self.labels = []
        self.no_connects = []
        self.rectangles = []
        self.texts = []
        self.components = {}

    def register_symbol(self, lib, name):
        key = f"{lib}:{name}"
        if key not in self.lib_symbols:
            self.lib_symbols[key] = extract_flat_symbol(lib, name)

    def add_component(self, ref, lib, name, val, x, y, rot=0, fp="", dnp=False):
        self.register_symbol(lib, name)
        comp_uuid = new_uuid()
        pins_data = parse_symbol_pins(lib, name)
        
        comp_info = {
            'ref': ref,
            'lib_id': f"{lib}:{name}",
            'val': val,
            'fp': fp,
            'x': round(x, 2),
            'y': round(y, 2),
            'rot': rot,
            'uuid': comp_uuid,
            'pins': pins_data,
            'dnp': dnp
        }
        self.components[ref] = comp_info
        self.symbol_instances.append(comp_info)
        return comp_info

    def get_pin(self, ref, pin_num):
        comp = self.components[ref]
        pnum_str = str(pin_num)
        if pnum_str not in comp['pins']:
            raise KeyError(f"Pin {pin_num} not in component {ref} ({comp['lib_id']})")
        p = comp['pins'][pnum_str]
        px, py = get_pin_pos(comp['x'], comp['y'], p['dx'], p['dy'], comp['rot'])
        return px, py

    def add_wire(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)
        if x1 == x2 and y1 == y2:
            return
        if x1 != x2 and y1 != y2:
            self.wires.append(((x1, y1), (x2, y1), new_uuid()))
            self.wires.append(((x2, y1), (x2, y2), new_uuid()))
        else:
            self.wires.append(((x1, y1), (x2, y2), new_uuid()))

    def add_junction(self, x, y):
        self.junctions.add((round(x, 2), round(y, 2)))

    def add_label(self, net_name, x, y, rot=0, justify="left bottom"):
        self.labels.append({
            'net': net_name,
            'x': round(x, 2),
            'y': round(y, 2),
            'rot': rot,
            'justify': justify,
            'uuid': new_uuid()
        })

    def add_no_connect(self, x, y):
        self.no_connects.append((round(x, 2), round(y, 2), new_uuid()))

    def add_power(self, power_net, x, y, rot=0):
        ref = f"#PWR?{len(self.symbol_instances)+1}"
        sym_name = power_net
        if power_net == 'VBAT':
            sym_name = '+BATT'
        self.add_component(ref, 'power', sym_name, power_net, x, y, rot)

    def add_pwr_flag(self, x, y):
        ref = f"#FLG?{len(self.symbol_instances)+1}"
        self.add_component(ref, 'power', 'PWR_FLAG', 'PWR_FLAG', x, y, 0)

    def add_box(self, x1, y1, x2, y2, title=None):
        self.rectangles.append((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2), new_uuid()))
        if title:
            self.texts.append({
                'text': title,
                'x': round(x1 + 3.81, 2),
                'y': round(y1 + 5.08, 2),
                'size': 2.0,
                'bold': True,
                'uuid': new_uuid()
            })

    def add_text(self, text, x, y, size=1.5, bold=False):
        self.texts.append({
            'text': text,
            'x': round(x, 2),
            'y': round(y, 2),
            'size': size,
            'bold': bold,
            'uuid': new_uuid()
        })

    def export(self, filepath):
        lines = [
            '(kicad_sch',
            '  (version 20250610)',
            '  (generator "konnect_agent")',
            '  (generator_version "10.0")',
            f'  (uuid "{self.sch_uuid}")',
            '  (paper "A3")',
            '  (title_block',
            '    (title "ESP-12F System - Dual USB / LiPo Power Path & Auto-Programming")',
            '    (date "2026-10-30")',
            '    (rev "1.0")',
            '    (company "Antigravity Engineering")',
            '    (comment 1 "Power Path with AO3401 P-MOSFET, TP4056 Charger, AP2112 3.3V LDO")',
            '    (comment 2 "CH340C USB-UART Bridge with Auto-Reset DTR/RTS Circuit")',
            '  )',
            '  (lib_symbols'
        ]

        # Embed flattened symbols
        for key in sorted(self.lib_symbols.keys()):
            formatted = self.lib_symbols[key]
            lines.append('    ' + formatted.replace('\n', '\n    '))
        lines.append('  )')

        # Rectangles
        for x1, y1, x2, y2, u in self.rectangles:
            lines.append(f'  (rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type dash)) (fill (type none)) (uuid "{u}"))')

        # Texts
        for t in self.texts:
            bold_str = " (bold yes)" if t['bold'] else ""
            lines.append(f'  (text "{t["text"]}" (exclude_from_sim no) (at {t["x"]} {t["y"]} 0) (effects (font (size {t["size"]} {t["size"]}){bold_str}) (justify left bottom)) (uuid "{t["uuid"]}"))')

        # Junctions
        for jx, jy in self.junctions:
            lines.append(f'  (junction (at {jx} {jy}) (diameter 0.9144) (color 0 0 0 0) (uuid "{new_uuid()}"))')

        # No connects
        for ncx, ncy, u in self.no_connects:
            lines.append(f'  (no_connect (at {ncx} {ncy}) (uuid "{u}"))')

        # Labels
        for lbl in self.labels:
            lines.append(f'  (label "{lbl["net"]}" (at {lbl["x"]} {lbl["y"]} {lbl["rot"]}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {lbl["justify"]})) (uuid "{lbl["uuid"]}"))')

        # Wires
        for (x1, y1), (x2, y2), u in self.wires:
            lines.append(f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{u}"))')

        # Symbols
        for comp in self.symbol_instances:
            ref = comp['ref']
            val = comp['val']
            fp = comp['fp']
            cx = comp['x']
            cy = comp['y']
            rot = comp['rot']
            u = comp['uuid']
            lib_id = comp['lib_id']
            dnp_str = " (dnp yes)" if comp['dnp'] else " (dnp no)"

            is_pwr = ref.startswith('#PWR') or ref.startswith('#FLG')
            hide_ref = " (hide yes)" if is_pwr else ""

            ref_y = round(cy - 2.54, 2)
            val_y = round(cy + 2.54, 2)

            lines.append('  (symbol')
            lines.append(f'    (lib_id "{lib_id}")')
            lines.append(f'    (at {cx} {cy} {rot})')
            lines.append('    (unit 1)')
            lines.append('    (in_bom yes)')
            lines.append('    (on_board yes)')
            lines.append(f'   {dnp_str}')
            lines.append(f'    (uuid "{u}")')
            lines.append(f'    (property "Reference" "{ref}" (at {cx} {ref_y} 0) (effects (font (size 1.27 1.27))){hide_ref})')
            lines.append(f'    (property "Value" "{val}" (at {cx} {val_y} 0) (effects (font (size 1.27 1.27))))')
            lines.append(f'    (property "Footprint" "{fp}" (at {cx} {cy} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
            lines.append(f'    (property "Datasheet" "" (at {cx} {cy} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
            
            for pnum in comp['pins'].keys():
                lines.append(f'    (pin "{pnum}" (uuid "{new_uuid()}"))')

            lines.append('    (instances')
            lines.append('      (project "esp12f_battery_usb"')
            lines.append(f'        (path "/{self.sch_uuid}"')
            lines.append(f'          (reference "{ref}")')
            lines.append('          (unit 1)))))')

        lines.append(f'  (sheet_instances (path "/" (page "1")))')
        lines.append(')')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print(f"Schematic written successfully: {filepath}")
