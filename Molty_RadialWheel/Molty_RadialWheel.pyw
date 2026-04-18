import sys
import math
import threading
import time
import json
import os
import ctypes # Для проверки активного окна
from PySide6 import QtWidgets, QtCore, QtGui
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Key, Controller

# === ФУНКЦИЯ ПРОВЕРКИ ОКНА HARMONY ===
def is_harmony_active():
    """Проверяет, является ли окно Toon Boom Harmony активным."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return "harmony" in buff.value.lower()
    except:
        return False

kb_controller = Controller()
current_keys = set()

# === НОВАЯ ЛОГИКА ОБРАБОТКИ КЛАВИШ (LAYOUT INDEPENDENT) ===
def get_canonical_key_name(key):
    """
    Преобразует клавишу в стандартное английское имя, 
    используя Virtual Key Code (vk), игнорируя текущую раскладку.
    """
    try:
        # 1. Попытка получить имя через Virtual Key Code (работает для букв и цифр)
        if hasattr(key, 'vk') and key.vk is not None:
            # A-Z (VK codes 65-90)
            if 65 <= key.vk <= 90:
                return chr(key.vk).lower()
            # 0-9 (VK codes 48-57)
            if 48 <= key.vk <= 57:
                return chr(key.vk)
            # F1-F12 и другие (можно добавить при необходимости, но pynput обычно обрабатывает их как Key.*)
            
        # 2. Если VK не подошел, пробуем стандартный char (для символов типа [, ], ;)
        if hasattr(key, 'char') and key.char:
            return key.char.lower()
            
    except: pass
    
    # 3. Возвращаем сам объект ключа (для Key.ctrl, Key.shift и т.д.)
    return key

def on_press(key):
    try:
        canonical = get_canonical_key_name(key)
        current_keys.add(canonical)
    except: pass
    # На всякий случай добавляем raw key объект тоже, для проверки модификаторов
    current_keys.add(key)

def on_release(key):
    try:
        canonical = get_canonical_key_name(key)
        current_keys.discard(canonical)
    except: pass
    current_keys.discard(key)

listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def is_key_pressed(key_name):
    key_name = key_name.lower()
    
    # Проверка модификаторов
    if key_name in ["ctrl", "control"]:
        return Key.ctrl in current_keys or Key.ctrl_l in current_keys or Key.ctrl_r in current_keys
    if key_name == "shift":
        return Key.shift in current_keys or Key.shift_l in current_keys or Key.shift_r in current_keys
    if key_name == "alt":
        return Key.alt in current_keys or Key.alt_l in current_keys or Key.alt_r in current_keys
    
    # Проверка спецклавиш
    if key_name == "tab": return Key.tab in current_keys
    if key_name == "space": return Key.space in current_keys
    if key_name == "enter": return Key.enter in current_keys
    if key_name == "backspace": return Key.backspace in current_keys
    if key_name == "escape": return Key.esc in current_keys
    
    # Прямая проверка символа (теперь здесь всегда английская буква благодаря get_canonical_key_name)
    return key_name in current_keys

PYNPUT_KEY_MAP = {"enter": Key.enter, "tab": Key.tab, "space": Key.space, "escape": Key.esc, "backspace": Key.backspace, "delete": Key.delete, "insert": Key.insert, "home": Key.home, "end": Key.end, "pageup": Key.page_up, "pagedown": Key.page_down, "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right}
for i in range(1, 13): PYNPUT_KEY_MAP[f"f{i}"] = getattr(Key, f"f{i}")

ALL_KEYS_LIST = ["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","z","x","c","v","b","n","m","0","1","2","3","4","5","6","7","8","9","tab", "space", "enter", "backspace", "escape","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","up","down","left","right", "home","end","pageup","pagedown","insert","delete"]

COMMAND_FILE = r"C:\HarmonyRadialWheel\harmony_command.json"
script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(script_dir, "wheel_config.json")
os.makedirs(os.path.dirname(COMMAND_FILE), exist_ok=True)

def load_config():
    default_wheel = {"name": "Main Wheel", "shortcut": "q", "modifiers": [], "segments": [], "outer_radius": 170, "logo": "", "harmony_only": False}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "wheels" not in data:
                    old_wheel = {"name": "Main Wheel", "shortcut": data.get("shortcut", "q"), "modifiers": data.get("modifiers", []), "segments": data.get("segments", []), "outer_radius": data.get("outer_radius", 170), "logo": "", "harmony_only": False}
                    return {"wheels": [old_wheel]}
                return data
        except: pass
    return {"wheels": [default_wheel]}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Error", f"Failed to save JSON:\n{e}")

def send_to_harmony_file(code):
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump({"js": code}, f)

def get_js_files():
    js_files = []
    actions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    if os.path.exists(actions_dir):
        for file in os.listdir(actions_dir):
            if file.endswith('.js'): js_files.append(file)
    return sorted(js_files)

def load_js_content(file_name):
    actions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    file_path = os.path.join(actions_dir, file_name)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: return f.read()
        except: return ""
    return ""

def find_icon_for_js(js_file):
    actions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    base_name = os.path.splitext(js_file)[0]
    for ext in ['.png', '.jpg', '.jpeg', '.ico']:
        icon_path = os.path.join(actions_dir, base_name + ext)
        if os.path.exists(icon_path): return icon_path
    return ""

class RadialWheel(QtWidgets.QWidget):
    show_signal = QtCore.Signal(int)
    hide_signal = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.scale = 1/1.5
        self.icon_radius = int(26 * self.scale)
        self.submenu_radius_offset = int(65 * self.scale)
        self.setFixedSize(900,900)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.full_config = load_config()
        self.wheels_data = self.full_config.get("wheels", [])
        self.current_wheel_index = -1
        self.segments = []
        self.outer_radius = 170
        self.inner_radius = 120
        self.center_offset = QtCore.QPointF(self.width()/2, self.height()/2)
        self.current_logo = ""
        self.icon_positions = []
        self.submenu_positions = []
        self.current_index = None
        self.last_main_index = None
        self.submenu_index = None
        self.hover_index = None
        self.wheel_visible = False
        self.key_pressed = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_selection)
        self.timer.start(16)
        self.show_signal.connect(self.show_wheel)
        self.hide_signal.connect(self.hide_wheel)

    def refresh_config(self):
        self.full_config = load_config()
        self.wheels_data = self.full_config.get("wheels", [])

    def show_wheel(self, wheel_index):
        if self.key_pressed or self.wheel_visible: return
        if wheel_index < 0 or wheel_index >= len(self.wheels_data): return
        data = self.wheels_data[wheel_index]
        self.current_wheel_index = wheel_index
        self.segments = data.get("segments", [])
        self.outer_radius = int(data.get("outer_radius", 170) * self.scale)
        self.inner_radius = self.outer_radius - 50
        self.current_logo = data.get("logo", "")
        self.key_pressed = True
        self.wheel_visible = True
        pos = QtGui.QCursor.pos()
        self.move(pos.x() - self.width()/2, pos.y() - self.height()/2)
        r = (self.inner_radius + self.outer_radius)/2
        count = len(self.segments)
        self.icon_positions.clear()
        for i in range(count):
            a = 2*math.pi*i/count - math.pi/2
            x = self.center_offset.x() + r*math.cos(a)
            y = self.center_offset.y() + r*math.sin(a)
            self.icon_positions.append((x, y))
        super().show()
        self.raise_()

    def hide_wheel(self):
        if not self.key_pressed or not self.wheel_visible: return
        if self.submenu_index is not None and self.last_main_index is not None:
            submenu = self.segments[self.last_main_index].get("submenu", [])
            if 0 <= self.submenu_index < len(submenu):
                self.execute_item(submenu[self.submenu_index])
        elif self.last_main_index is not None:
            self.execute_item(self.segments[self.last_main_index])
        self.key_pressed = False
        self.wheel_visible = False
        super().hide()
        self.current_index = self.last_main_index = self.submenu_index = self.hover_index = None
        self.current_wheel_index = -1

    def execute_item(self, item):
        if item.get("type") == "macro":
            self.execute_macro(item.get("macro", {}))
        else: send_to_harmony_file(item.get("js", ""))

    def execute_macro(self, macro_data):
        try:
            key_str = macro_data.get("key", "").lower()
            target_key = PYNPUT_KEY_MAP.get(key_str, key_str)
            mod_keys = []
            if "ctrl" in macro_data.get("modifiers", []): mod_keys.append(Key.ctrl)
            if "shift" in macro_data.get("modifiers", []): mod_keys.append(Key.shift)
            if "alt" in macro_data.get("modifiers", []): mod_keys.append(Key.alt)
            time.sleep(0.15)
            for mod in mod_keys: kb_controller.press(mod)
            kb_controller.press(target_key)
            kb_controller.release(target_key)
            for mod in reversed(mod_keys): kb_controller.release(mod)
        except: pass

    def update_selection(self):
        if not self.wheel_visible: return
        pos = self.mapFromGlobal(QtGui.QCursor.pos())
        self.hover_index = None
        for i, (x, y) in enumerate(self.icon_positions):
            if math.hypot(pos.x()-x, pos.y()-y) <= self.icon_radius:
                self.hover_index = i
                break
        if self.hover_index is not None:
            self.current_index = self.last_main_index = self.hover_index
            self.submenu_index = None
        self.submenu_positions.clear()
        if self.last_main_index is not None:
            submenu = self.segments[self.last_main_index].get("submenu")
            if submenu:
                base_angle = 2*math.pi*self.last_main_index/len(self.segments)-math.pi/2
                count = len(submenu)
                spread = math.pi / (16 if count==1 else 8 if count==2 else 4.5 if count==3 else (180/(count*8))/2)
                start, step = base_angle - spread/2, spread / max(1, count - 1)
                r_sub = self.outer_radius + self.submenu_radius_offset
                for i, item in enumerate(submenu):
                    a = start + step*i
                    x, y = self.center_offset.x() + r_sub*math.cos(a), self.center_offset.y() + r_sub*math.sin(a)
                    self.submenu_positions.append((x, y))
                    if math.hypot(pos.x()-x, pos.y()-y) <= self.icon_radius: self.submenu_index = i
        self.update()

    def draw_text_box(self, p, text, center):
        if not text or text.strip() == "": return
        p.save()
        metrics = p.fontMetrics()
        text_width, text_height = metrics.horizontalAdvance(text) + 12, metrics.height() + 6
        rect = QtCore.QRectF(center.x()-text_width/2, center.y()+self.icon_radius+5, text_width+10, text_height)
        p.setBrush(QtGui.QColor(0,0,0,150)); p.setPen(QtCore.Qt.NoPen); p.drawRoundedRect(rect, 5, 5)
        p.setPen(QtGui.QColor(255,255,255)); p.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        p.drawText(rect, QtCore.Qt.AlignCenter, text); p.restore()

    def draw_icon(self, p, center, icon_path):
        if icon_path and os.path.exists(icon_path):
            pix = QtGui.QPixmap(icon_path).scaled(self.icon_radius*2, self.icon_radius*2, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            p.drawPixmap(int(center.x()-self.icon_radius), int(center.y()-self.icon_radius), pix)
        else: p.drawEllipse(center, self.icon_radius, self.icon_radius)

    def paintEvent(self, e):
        if not self.wheel_visible: return
        p = QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing)
        ring = QtGui.QPainterPath(); ring.addEllipse(self.center_offset.x()-self.outer_radius, self.center_offset.y()-self.outer_radius, self.outer_radius*2, self.outer_radius*2)
        hole = QtGui.QPainterPath(); hole.addEllipse(self.center_offset.x()-self.inner_radius, self.center_offset.y()-self.inner_radius, self.inner_radius*2, self.inner_radius*2)
        p.setPen(QtCore.Qt.NoPen); p.setBrush(QtGui.QColor(20,20,20,185)); p.drawPath(ring.subtracted(hole))
        logo_path = self.current_logo if self.current_logo and os.path.exists(self.current_logo) else os.path.join(script_dir, "logo.png")
        if os.path.exists(logo_path):
            pix = QtGui.QPixmap(logo_path); size = (self.outer_radius - 50) * 1.8
            pix = pix.scaled(size, size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            p.drawPixmap(int(self.center_offset.x() - size/2), int(self.center_offset.y() - size/2), pix)
        for i, (x, y) in enumerate(self.icon_positions):
            if i == self.hover_index:
                p.setBrush(QtGui.QColor(120,120,120,120)); p.drawEllipse(QtCore.QPointF(x,y), self.icon_radius+5, self.icon_radius+5)
            self.draw_icon(p, QtCore.QPointF(x,y), self.segments[i].get("icon"))
        if self.last_main_index is not None:
            submenu = self.segments[self.last_main_index].get("submenu")
            if submenu:
                for i, (x, y) in enumerate(self.submenu_positions):
                    if i >= len(submenu): continue
                    center = QtCore.QPointF(x, y)
                    p.setBrush(QtGui.QColor(50, 50, 50, 200)); p.drawEllipse(center, self.icon_radius+5, self.icon_radius+5)
                    if i == self.submenu_index:
                        p.setBrush(QtGui.QColor(120,120,120,120)); p.drawEllipse(center, self.icon_radius+10, self.icon_radius+10)
                    self.draw_icon(p, center, submenu[i].get("icon"))
        if self.current_index is not None and self.current_index < len(self.segments):
            self.draw_text_box(p, self.segments[self.current_index].get("name", ""), QtCore.QPointF(*self.icon_positions[self.current_index]))
        if self.submenu_index is not None and self.last_main_index is not None:
            sub = self.segments[self.last_main_index].get("submenu")
            if sub and self.submenu_index < len(sub):
                self.draw_text_box(p, sub[self.submenu_index].get("name", ""), QtCore.QPointF(*self.submenu_positions[self.submenu_index]))

class SubItemWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self); self.layout.setContentsMargins(0,0,0,0)
        self.name_edit = QtWidgets.QLineEdit(); self.name_edit.setPlaceholderText("Name")
        self.type_combo = QtWidgets.QComboBox(); self.type_combo.addItems(["JS Script", "Keyboard Macro"])
        self.js_combo = QtWidgets.QComboBox(); self.js_combo.addItem("", ""); self.js_combo.setMaximumWidth(150)
        self.macro_container = QtWidgets.QWidget(); self.macro_layout = QtWidgets.QHBoxLayout(self.macro_container); self.macro_layout.setContentsMargins(0,0,0,0)
        self.key_combo = QtWidgets.QComboBox(); self.key_combo.addItems(ALL_KEYS_LIST)
        self.ctrl_check, self.shift_check, self.alt_check = QtWidgets.QCheckBox("Ctrl"), QtWidgets.QCheckBox("Shift"), QtWidgets.QCheckBox("Alt")
        for w in [self.key_combo, self.ctrl_check, self.shift_check, self.alt_check]: self.macro_layout.addWidget(w)
        self.icon_button, self.delete_button = QtWidgets.QPushButton(), QtWidgets.QPushButton("❌")
        self.icon_path = ""
        for w in [self.name_edit, self.type_combo, self.js_combo, self.macro_container, self.icon_button, self.delete_button]: self.layout.addWidget(w)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.js_combo.currentIndexChanged.connect(self.on_js_selected)
        self.icon_button.clicked.connect(self.choose_icon)
        for js in get_js_files(): self.js_combo.addItem(js, js)
        self.on_type_changed(0)

    def on_type_changed(self, idx):
        self.js_combo.setVisible(idx == 0); self.macro_container.setVisible(idx != 0)

    def on_js_selected(self, idx):
        js_file = self.js_combo.currentData()
        if js_file:
            self.js_content = load_js_content(js_file)
            self.icon_path = find_icon_for_js(js_file)
            if self.icon_path: self.icon_button.setIcon(QtGui.QIcon(QtGui.QPixmap(self.icon_path).scaled(24,24)))
            self.name_edit.setText(os.path.splitext(js_file)[0])

    def choose_icon(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.ico)")
        if path:
            self.icon_path = path
            self.icon_button.setIcon(QtGui.QIcon(QtGui.QPixmap(path).scaled(24,24)))

    def to_dict(self):
        if self.type_combo.currentIndex() == 0:
            return {"type": "js", "name": self.name_edit.text(), "js": getattr(self, "js_content", load_js_content(self.js_combo.currentData())), "icon": self.icon_path}
        return {"type": "macro", "name": self.name_edit.text(), "macro": {"key": self.key_combo.currentText(), "modifiers": [m for m, c in [("ctrl", self.ctrl_check), ("shift", self.shift_check), ("alt", self.alt_check)] if c.isChecked()]}, "icon": self.icon_path}

class MainItemWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self); self.frame = QtWidgets.QFrame(); self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_layout = QtWidgets.QVBoxLayout(self.frame); self.layout.addWidget(self.frame)
        top = QtWidgets.QHBoxLayout()
        self.move_up_btn, self.move_down_btn = QtWidgets.QPushButton("↑"), QtWidgets.QPushButton("↓")
        self.name_edit, self.type_combo = QtWidgets.QLineEdit(), QtWidgets.QComboBox()
        self.name_edit.setPlaceholderText("Main Item Name"); self.type_combo.addItems(["JS Script", "Keyboard Macro"])
        self.js_combo = QtWidgets.QComboBox(); self.js_combo.addItem("", ""); self.js_combo.setMaximumWidth(150)
        self.macro_container = QtWidgets.QWidget(); self.macro_layout = QtWidgets.QHBoxLayout(self.macro_container); self.macro_layout.setContentsMargins(0,0,0,0)
        self.key_combo = QtWidgets.QComboBox(); self.key_combo.addItems(ALL_KEYS_LIST)
        self.ctrl_check, self.shift_check, self.alt_check = QtWidgets.QCheckBox("Ctrl"), QtWidgets.QCheckBox("Shift"), QtWidgets.QCheckBox("Alt")
        for w in [self.key_combo, self.ctrl_check, self.shift_check, self.alt_check]: self.macro_layout.addWidget(w)
        self.icon_button, self.toggle_sub_btn, self.add_sub_button, self.delete_button = QtWidgets.QPushButton(), QtWidgets.QPushButton("▼"), QtWidgets.QPushButton("+ Sub"), QtWidgets.QPushButton("❌")
        self.toggle_sub_btn.setCheckable(True); self.toggle_sub_btn.setChecked(True)
        for w in [self.move_up_btn, self.move_down_btn, self.name_edit, self.type_combo, self.js_combo, self.macro_container, self.icon_button, self.toggle_sub_btn, self.add_sub_button, self.delete_button]: top.addWidget(w)
        self.frame_layout.addLayout(top); self.sub_container = QtWidgets.QWidget(); self.sub_list = QtWidgets.QVBoxLayout(self.sub_container)
        self.sub_list.setContentsMargins(40, 0, 0, 0); self.frame_layout.addWidget(self.sub_container)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.js_combo.currentIndexChanged.connect(self.on_js_selected)
        self.icon_button.clicked.connect(self.choose_icon); self.add_sub_button.clicked.connect(self.add_sub_item); self.toggle_sub_btn.clicked.connect(self.toggle_submenu)
        for js in get_js_files(): self.js_combo.addItem(js, js)
        self.on_type_changed(0)
        self.move_up_btn.clicked.connect(lambda: self.move_item(-1)); self.move_down_btn.clicked.connect(lambda: self.move_item(1))

    def toggle_submenu(self):
        visible = self.toggle_sub_btn.isChecked()
        self.sub_container.setVisible(visible); self.toggle_sub_btn.setText("▼" if visible else "▶")

    def move_item(self, direction):
        parent = self.parent().layout()
        if parent:
            idx = parent.indexOf(self)
            if 0 <= idx + direction < parent.count():
                w = parent.takeAt(idx).widget()
                parent.insertWidget(idx + direction, w)

    def on_type_changed(self, idx):
        self.js_combo.setVisible(idx == 0); self.macro_container.setVisible(idx != 0)

    def on_js_selected(self, idx):
        js_file = self.js_combo.currentData()
        if js_file:
            self.js_content = load_js_content(js_file)
            self.icon_path = find_icon_for_js(js_file)
            if self.icon_path: self.icon_button.setIcon(QtGui.QIcon(QtGui.QPixmap(self.icon_path).scaled(24,24)))
            self.name_edit.setText(os.path.splitext(js_file)[0])

    def choose_icon(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.ico)")
        if path:
            self.icon_path = path
            self.icon_button.setIcon(QtGui.QIcon(QtGui.QPixmap(path).scaled(24,24)))

    def add_sub_item(self, data=None):
        sub = SubItemWidget(); self.sub_list.addWidget(sub)
        if data:
            sub.name_edit.setText(data.get("name",""))
            if data.get("type") == "macro":
                sub.type_combo.setCurrentIndex(1)
                m = data.get("macro", {})
                sub.key_combo.setCurrentText(m.get("key", "a"))
                mods = m.get("modifiers", [])
                sub.ctrl_check.setChecked("ctrl" in mods); sub.shift_check.setChecked("shift" in mods); sub.alt_check.setChecked("alt" in mods)
            else:
                sub.type_combo.setCurrentIndex(0)
                js = data.get("js","")
                for f in get_js_files():
                    if load_js_content(f) == js: sub.js_combo.setCurrentIndex(sub.js_combo.findData(f)); break
            sub.icon_path = data.get("icon","")
            if sub.icon_path and os.path.exists(sub.icon_path): sub.icon_button.setIcon(QtGui.QIcon(QtGui.QPixmap(sub.icon_path).scaled(24,24)))
        sub.delete_button.clicked.connect(lambda: (self.sub_list.removeWidget(sub), sub.deleteLater()))

    def to_dict(self):
        subs = [self.sub_list.itemAt(i).widget().to_dict() for i in range(self.sub_list.count()) if self.sub_list.itemAt(i).widget()]
        base = {"name": self.name_edit.text(), "icon": getattr(self, "icon_path", ""), "submenu": subs}
        if self.type_combo.currentIndex() == 0:
            base.update({"type": "js", "js": getattr(self, "js_content", load_js_content(self.js_combo.currentData()))})
        else:
            base.update({"type": "macro", "macro": {"key": self.key_combo.currentText(), "modifiers": [m for m, c in [("ctrl", self.ctrl_check), ("shift", self.shift_check), ("alt", self.alt_check)] if c.isChecked()]}})
        return base

class WheelConfigWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); layout = QtWidgets.QVBoxLayout(self)
        settings = QtWidgets.QGroupBox("Wheel Settings"); s_layout = QtWidgets.QVBoxLayout(settings)
        
        name_l = QtWidgets.QHBoxLayout(); name_l.addWidget(QtWidgets.QLabel("Wheel Name:")); self.wheel_name_edit = QtWidgets.QLineEdit(); name_l.addWidget(self.wheel_name_edit); s_layout.addLayout(name_l)
        
        shortcut_l = QtWidgets.QHBoxLayout(); shortcut_l.addWidget(QtWidgets.QLabel("Shortcut:")); self.shortcut_combo = QtWidgets.QComboBox(); self.shortcut_combo.addItems(ALL_KEYS_LIST); shortcut_l.addWidget(self.shortcut_combo)
        self.ctrl_cb, self.shift_cb, self.alt_cb = QtWidgets.QCheckBox("Ctrl"), QtWidgets.QCheckBox("Shift"), QtWidgets.QCheckBox("Alt")
        for cb in [self.ctrl_cb, self.shift_cb, self.alt_cb]: shortcut_l.addWidget(cb)
        s_layout.addLayout(shortcut_l)
        
        self.harmony_only_cb = QtWidgets.QCheckBox("Toon Boom Only (appears only when Harmony is active)")
        s_layout.addWidget(self.harmony_only_cb)

        logo_l = QtWidgets.QHBoxLayout(); logo_l.addWidget(QtWidgets.QLabel("Center Logo:")); self.logo_path_edit = QtWidgets.QLineEdit(); self.logo_btn = QtWidgets.QPushButton("Browse..."); self.logo_btn.clicked.connect(self.browse_logo); logo_l.addWidget(self.logo_path_edit); logo_l.addWidget(self.logo_btn); s_layout.addLayout(logo_l)
        
        rad_l = QtWidgets.QHBoxLayout(); rad_l.addWidget(QtWidgets.QLabel("Outer Radius:")); self.radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal); self.radius_spin = QtWidgets.QSpinBox(); self.radius_slider.setRange(100,300); self.radius_spin.setRange(100,300); self.radius_slider.valueChanged.connect(self.radius_spin.setValue); self.radius_spin.valueChanged.connect(self.radius_slider.setValue); rad_l.addWidget(self.radius_slider); rad_l.addWidget(self.radius_spin); s_layout.addLayout(rad_l)
        
        layout.addWidget(settings); self.scroll = QtWidgets.QScrollArea(); self.scroll.setWidgetResizable(True); self.items_container = QtWidgets.QWidget(); self.items_layout = QtWidgets.QVBoxLayout(self.items_container); self.items_layout.addStretch(); self.scroll.setWidget(self.items_container); layout.addWidget(self.scroll)
        self.add_btn = QtWidgets.QPushButton("Add Main Item"); self.add_btn.clicked.connect(self.add_main_item); layout.addWidget(self.add_btn)

    def browse_logo(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.ico)")
        if path: self.logo_path_edit.setText(path)

    def add_main_item(self, data=None):
        item = MainItemWidget(); self.items_layout.insertWidget(self.items_layout.count()-1, item)
        if data:
            item.name_edit.setText(data.get("name",""))
            if data.get("type") == "macro":
                item.type_combo.setCurrentIndex(1)
                m = data.get("macro", {}); item.key_combo.setCurrentText(m.get("key", "a"))
                mods = m.get("modifiers", []); item.ctrl_check.setChecked("ctrl" in mods); item.shift_check.setChecked("shift" in mods); item.alt_check.setChecked("alt" in mods)
            else:
                item.type_combo.setCurrentIndex(0); js = data.get("js","")
                for f in get_js_files():
                    if load_js_content(f) == js: item.js_combo.setCurrentIndex(item.js_combo.findData(f)); break
            item.icon_path = data.get("icon","")
            if item.icon_path and os.path.exists(item.icon_path): item.icon_button.setIcon(QtGui.QIcon(QtGui.QPixmap(item.icon_path).scaled(24,24)))
            for sub in data.get("submenu", []): item.add_sub_item(sub)
        item.delete_button.clicked.connect(lambda: (self.items_layout.removeWidget(item), item.deleteLater()))

    def load_from_dict(self, data):
        self.wheel_name_edit.setText(data.get("name", "Wheel")); self.shortcut_combo.setCurrentText(data.get("shortcut", "q"))
        mods = data.get("modifiers", []); self.ctrl_cb.setChecked("ctrl" in mods); self.shift_cb.setChecked("shift" in mods); self.alt_cb.setChecked("alt" in mods)
        self.radius_slider.setValue(data.get("outer_radius", 170)); self.logo_path_edit.setText(data.get("logo", ""))
        self.harmony_only_cb.setChecked(data.get("harmony_only", False))
        while self.items_layout.count() > 1:
            child = self.items_layout.takeAt(0);
            if child.widget(): child.widget().deleteLater()
        for seg in data.get("segments", []): self.add_main_item(seg)

    def to_dict(self):
        segs = [self.items_layout.itemAt(i).widget().to_dict() for i in range(self.items_layout.count()) if isinstance(self.items_layout.itemAt(i).widget(), MainItemWidget)]
        return {"name": self.wheel_name_edit.text(), "shortcut": self.shortcut_combo.currentText(), "modifiers": [m for m, c in [("ctrl", self.ctrl_cb), ("shift", self.shift_cb), ("alt", self.alt_cb)] if c.isChecked()], "segments": segs, "outer_radius": self.radius_spin.value(), "logo": self.logo_path_edit.text(), "harmony_only": self.harmony_only_cb.isChecked()}

class JSONEditor(QtWidgets.QWidget):
    def __init__(self, wheel: RadialWheel):
        super().__init__(); self.wheel = wheel; self.setWindowTitle("Radial Wheel Editor"); self.resize(1100, 750)
        
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        icon_path = os.path.join(script_dir, "icon.png")
        if os.path.exists(icon_path): self.tray_icon.setIcon(QtGui.QIcon(icon_path))
        else: self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        
        tray_menu = QtWidgets.QMenu()
        show_action = tray_menu.addAction("Show Editor")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Exit")
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_activated)

        main_layout = QtWidgets.QVBoxLayout(self); self.tabs = QtWidgets.QTabWidget(); self.tabs.setTabsClosable(True); self.tabs.tabCloseRequested.connect(self.close_tab); main_layout.addWidget(self.tabs)
        btn_l = QtWidgets.QHBoxLayout(); self.add_wheel_btn = QtWidgets.QPushButton("+ New Wheel"); self.add_wheel_btn.clicked.connect(self.add_new_tab); self.save_btn = QtWidgets.QPushButton("Save Config"); self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;"); self.save_btn.clicked.connect(self.save_json); btn_l.addWidget(self.add_wheel_btn); btn_l.addStretch(); btn_l.addWidget(self.save_btn); main_layout.addLayout(btn_l)
        self.load_json()

    def on_tray_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger: self.show()

    def closeEvent(self, event):
        """Вместо закрытия сворачиваем в трей."""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()

    def add_new_tab(self, data=None):
        tab = WheelConfigWidget()
        if data: tab.load_from_dict(data)
        else: tab.load_from_dict({"name": "New Wheel", "shortcut": "q", "outer_radius": 170})
        idx = self.tabs.addTab(tab, tab.wheel_name_edit.text()); self.tabs.setCurrentIndex(idx)
        tab.wheel_name_edit.textChanged.connect(lambda text, t=tab: self.tabs.setTabText(self.tabs.indexOf(t), text))

    def close_tab(self, idx):
        if self.tabs.count() > 1: self.tabs.removeTab(idx)

    def load_json(self):
        wheels = load_config().get("wheels", []); self.tabs.clear()
        for w in wheels: self.add_new_tab(w)
        if self.tabs.count() == 0: self.add_new_tab()

    def save_json(self):
        data = {"wheels": [self.tabs.widget(i).to_dict() for i in range(self.tabs.count()) if isinstance(self.tabs.widget(i), WheelConfigWidget)]}
        save_config(data); self.wheel.refresh_config()
        QtWidgets.QMessageBox.information(self, "Saved", "Configuration saved!")

def keyboard_thread(wheel: RadialWheel):
    last_states = {}
    while True:
        try:
            for i, data in enumerate(wheel.wheels_data):
                sc = data.get("shortcut", "").lower()
                mods = data.get("modifiers", [])
                harmony_only = data.get("harmony_only", False)
                
                key_pressed = is_key_pressed(sc)
                mods_ok = all(is_key_pressed(m) for m in mods)
                
                is_active = key_pressed and mods_ok
                if is_active and harmony_only:
                    if not is_harmony_active():
                        is_active = False

                was_active = last_states.get(i, False)
                if is_active and not was_active:
                    if not wheel.wheel_visible: wheel.show_signal.emit(i)
                if not is_active and was_active:
                    if wheel.current_wheel_index == i: wheel.hide_signal.emit()
                last_states[i] = is_active
        except: pass
        time.sleep(0.02)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv); app.setStyle("Fusion")
    p = QtGui.QPalette()
    for color, roles in [(QtGui.QColor(53, 53, 53), [QtGui.QPalette.Window, QtGui.QPalette.Button, QtGui.QPalette.AlternateBase]), (QtCore.Qt.white, [QtGui.QPalette.WindowText, QtGui.QPalette.ToolTipBase, QtGui.QPalette.ToolTipText, QtGui.QPalette.Text, QtGui.QPalette.ButtonText]), (QtGui.QColor(25, 25, 25), [QtGui.QPalette.Base]), (QtGui.QColor(42, 130, 218), [QtGui.QPalette.Link, QtGui.QPalette.Highlight])]:
        for role in roles: p.setColor(role, color)
    app.setPalette(p)
    
    wheel = RadialWheel()
    threading.Thread(target=keyboard_thread, args=(wheel,), daemon=True).start()
    editor = JSONEditor(wheel); editor.show()
    sys.exit(app.exec())