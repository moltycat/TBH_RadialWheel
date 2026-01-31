import sys
import math
import threading
import time
import json
import os
from PySide6 import QtWidgets, QtCore, QtGui

from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Key, Controller

keep_running = True
# Создаем контроллер для эмуляции нажатий
kb_controller = Controller()

# Глобальное хранилище нажатых клавиш для проверки состояния (аналог keyboard.is_pressed)
current_keys = set()

def on_press(key):
    try:
        # Для обычных букв/цифр сохраняем строковое представление
        if hasattr(key, 'char') and key.char:
            current_keys.add(key.char.lower())
    except:
        pass
    # Сохраняем сам объект ключа (для Ctrl, Shift, F1 и т.д.)
    current_keys.add(key)

def on_release(key):
    try:
        if hasattr(key, 'char') and key.char:
            current_keys.discard(key.char.lower())
    except:
        pass
    current_keys.discard(key)

# Запускаем слушатель в неблокирующем режиме
listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def is_key_pressed(key_name):
    """Аналог keyboard.is_pressed для pynput"""
    key_name = key_name.lower()
    
    # Проверка модификаторов (они могут быть левыми или правыми)
    if key_name in ["ctrl", "control"]:
        return Key.ctrl in current_keys or Key.ctrl_l in current_keys or Key.ctrl_r in current_keys
    if key_name == "shift":
        return Key.shift in current_keys or Key.shift_l in current_keys or Key.shift_r in current_keys
    if key_name == "alt":
        return Key.alt in current_keys or Key.alt_l in current_keys or Key.alt_r in current_keys
    
    # Проверка обычных клавиш
    return key_name in current_keys

# Словарь для маппинга названий клавиш из UI в объекты pynput
PYNPUT_KEY_MAP = {
    "enter": Key.enter, "tab": Key.tab, "space": Key.space, "escape": Key.esc,
    "backspace": Key.backspace, "delete": Key.delete, "insert": Key.insert,
    "home": Key.home, "end": Key.end, "pageup": Key.page_up, "pagedown": Key.page_down,
    "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
    "print_screen": Key.print_screen, "scroll_lock": Key.scroll_lock, 
    "pause": Key.pause, "caps_lock": Key.caps_lock, "num_lock": Key.num_lock
}
# Добавляем F1-F12
for i in range(1, 13):
    PYNPUT_KEY_MAP[f"f{i}"] = getattr(Key, f"f{i}")

# ==============================
COMMAND_FILE = r"C:\HarmonyRadialWheel\harmony_command.json"
script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(script_dir, "wheel_config.json")
os.makedirs(os.path.dirname(COMMAND_FILE), exist_ok=True)

# ------------------------------
def load_segments():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    data = {"shortcut": "Q", "segments": data, "outer_radius": 170, "modifiers": []}
                elif not isinstance(data, dict) or "segments" not in data:
                    raise ValueError("JSON format invalid")
                return data
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "Warning", f"Failed to load JSON. Creating new file.\nError: {e}")
    return {"shortcut": "Q", "segments": [], "outer_radius": 170, "modifiers": []}

def save_segments(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Error", f"Failed to save JSON:\n{e}")

def send_to_harmony_file(code):
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump({"js": code}, f)
    print(f"[DEBUG] Command written: {code}")

def get_js_files():
    """Получить список всех JS файлов из папки actions"""
    js_files = []
    actions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    
    if os.path.exists(actions_dir):
        for file in os.listdir(actions_dir):
            if file.endswith('.js'):
                js_files.append(file)
    return sorted(js_files)

def load_js_content(file_name):
    """Загрузить содержимое JS файла по имени"""
    actions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    file_path = os.path.join(actions_dir, file_name)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""
    return ""

def find_icon_for_js(js_file):
    """Найти иконку для JS файла"""
    actions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    base_name = os.path.splitext(js_file)[0]
    
    # Проверяем различные форматы иконок
    icon_extensions = ['.png', '.jpg', '.jpeg', '.ico']
    for ext in icon_extensions:
        icon_path = os.path.join(actions_dir, base_name + ext)
        if os.path.exists(icon_path):
            return icon_path
    
    return ""

# ==============================
class RadialWheel(QtWidgets.QWidget):
    show_signal = QtCore.Signal()
    hide_signal = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.scale = 1/1.5
        self.icon_radius = int(26 * self.scale)
        self.submenu_radius_offset = int(65 * self.scale)
        self.widget_extra = self.submenu_radius_offset + 50
        self.setFixedSize(900,900)
        self.center_offset = QtCore.QPointF(self.width()/2, self.height()/2)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.Tool |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.data = load_segments()
        self.outer_radius = int(self.data.get("outer_radius",170)*self.scale)
        self.inner_radius = self.outer_radius - 50

        self.segments = self.data.get("segments", [])
        self.modifiers = self.data.get("modifiers", [])
        self.icon_positions = []
        self.submenu_positions = []

        self.current_index = None
        self.last_main_index = None
        self.submenu_index = None
        self.hover_index = None

        self.wheel_visible = False
        self.key_pressed = False
        self.shortcut = self.data.get("shortcut","Q").lower()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_selection)
        self.timer.start(16)

        self.show_signal.connect(self.show_wheel)
        self.hide_signal.connect(self.hide_wheel)

    def refresh_segments(self):
        self.data = load_segments()
        self.segments = self.data.get("segments", [])
        self.modifiers = self.data.get("modifiers", [])
        self.outer_radius = int(self.data.get("outer_radius",170)*self.scale)
        self.inner_radius = self.outer_radius - 50
        self.shortcut = self.data.get("shortcut","Q").lower()
        r = (self.inner_radius + self.outer_radius)/2
        self.center_offset = QtCore.QPointF(self.width()/2, self.height()/2)
        count = len(self.segments)
        self.icon_positions.clear()
        for i in range(count):
            a = 2*math.pi*i/count - math.pi/2
            x = self.center_offset.x() + r*math.cos(a)
            y = self.center_offset.y() + r*math.sin(a)
            self.icon_positions.append((x, y))
        self.update()

    # -------------------------
    def show_wheel(self):
        if self.key_pressed or self.wheel_visible:
            return
        
        # Проверка модификаторов
        if self.modifiers:
            ctrl_required = "ctrl" in self.modifiers
            shift_required = "shift" in self.modifiers
            alt_required = "alt" in self.modifiers
            
            # Используем нашу функцию is_key_pressed вместо keyboard.is_pressed
            ctrl_pressed = is_key_pressed("ctrl")
            shift_pressed = is_key_pressed("shift")
            alt_pressed = is_key_pressed("alt")
            
            # Проверяем, что все требуемые модификаторы нажаты, а не требуемые - не нажаты
            if (ctrl_required != ctrl_pressed) or (shift_required != shift_pressed) or (alt_required != alt_pressed):
                return

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
        if not self.key_pressed or not self.wheel_visible:
            return
        self.key_pressed = False
        self.wheel_visible = False

        if self.submenu_index is not None and self.last_main_index is not None:
            submenu = self.segments[self.last_main_index].get("submenu", [])
            if 0 <= self.submenu_index < len(submenu):
                item = submenu[self.submenu_index]
                if item.get("type") == "macro":
                    self.execute_macro(item.get("macro", {}))
                else:
                    send_to_harmony_file(item.get("js", ""))
        elif self.last_main_index is not None:
            item = self.segments[self.last_main_index]
            if item.get("type") == "macro":
                self.execute_macro(item.get("macro", {}))
            else:
                send_to_harmony_file(item.get("js", ""))

        super().hide()
        self.current_index = None
        self.last_main_index = None
        self.submenu_index = None
        self.hover_index = None

    def execute_macro(self, macro_data):
        """Выполнить макрос клавиатуры через pynput"""
        try:
            key_str = macro_data.get("key", "").lower()
            modifiers = macro_data.get("modifiers", [])
            
            # Определяем целевую клавишу (pynput объект или символ)
            target_key = PYNPUT_KEY_MAP.get(key_str, key_str)
            
            # Подготавливаем список модификаторов pynput
            mod_keys = []
            if "ctrl" in modifiers: mod_keys.append(Key.ctrl)
            if "shift" in modifiers: mod_keys.append(Key.shift)
            if "alt" in modifiers: mod_keys.append(Key.alt)

            print(f"[DEBUG] Executing pynput macro: {modifiers} + {key_str}")
            time.sleep(0.15)
            
            # Нажимаем модификаторы
            for mod in mod_keys:
                kb_controller.press(mod)
            
            # Нажимаем и отпускаем основную клавишу
            kb_controller.press(target_key)
            kb_controller.release(target_key)
            
            # Отпускаем модификаторы (в обратном порядке)
            for mod in reversed(mod_keys):
                kb_controller.release(mod)
            
            time.sleep(0.05)
            
        except Exception as e:
            print(f"[ERROR] Failed to execute macro: {e}")

    # -------------------------
    def update_selection(self):
        if not self.wheel_visible:
            return

        pos = self.mapFromGlobal(QtGui.QCursor.pos())
        cx, cy = self.center_offset.x(), self.center_offset.y()
        dist = math.hypot(pos.x()-cx, pos.y()-cy)
        if dist < self.inner_radius:
            self.hover_index = None
        else:
            self.hover_index = None
            for i, (x, y) in enumerate(self.icon_positions):
                if math.hypot(pos.x()-x, pos.y()-y) <= self.icon_radius:
                    self.hover_index = i
                    break

        hovered_main = self.hover_index
        if hovered_main is not None:
            self.current_index = hovered_main
            self.last_main_index = hovered_main
            self.submenu_index = None

        self.submenu_positions.clear()
        if self.last_main_index is not None:
            submenu = self.segments[self.last_main_index].get("submenu")
            if submenu:
                base_angle = 2*math.pi*self.last_main_index/len(self.segments)-math.pi/2
                count = len(submenu)

                if count == 1:
                   spread = math.pi / 16
                elif count == 2:
                   spread = math.pi / 8
                elif count == 3:
                   spread = math.pi / 4.5
                else:
                    spread = math.pi * 2 / (180 / (count * 8))
                
                start = base_angle - spread/2
                step = spread / max(1, count - 1)
                
                r_sub = self.outer_radius + self.submenu_radius_offset
                for i, item in enumerate(submenu):
                    a = start + step*i
                    x = self.center_offset.x() + r_sub * math.cos(a)
                    y = self.center_offset.y() + r_sub * math.sin(a)
                    self.submenu_positions.append((x, y))
                    if math.hypot(pos.x()-x, pos.y()-y) <= self.icon_radius:
                        self.submenu_index = i

        self.update()

    # -------------------------
    def draw_icon(self, p, center, icon_path):
        if icon_path and os.path.exists(icon_path):
            pix = QtGui.QPixmap(icon_path)
            pix = pix.scaled(self.icon_radius*2, self.icon_radius*2, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            p.drawPixmap(center.x()-self.icon_radius, center.y()-self.icon_radius, pix)
        else:
            p.drawEllipse(center, self.icon_radius, self.icon_radius)

    def draw_hover_circle(self, p, center):
        p.setBrush(QtGui.QColor(120,120,120,120))
        p.setPen(QtCore.Qt.NoPen)
        p.drawEllipse(center, self.icon_radius+5, self.icon_radius+5)

    def draw_text_box(self, p, text, center):
        # Создаем отдельный слой для текста поверх всего
        p.save()
        p.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        
        metrics = p.fontMetrics()
        text_width = metrics.horizontalAdvance(text) + 12
        text_height = metrics.height() + 6
        rect = QtCore.QRectF(center.x()-text_width/2, center.y()+self.icon_radius+5, text_width+10, text_height)
        p.setBrush(QtGui.QColor(0,0,0,150))  # Более непрозрачный фон
        p.setPen(QtCore.Qt.NoPen)
        p.drawRoundedRect(rect, 5, 5)
        p.setPen(QtGui.QColor(255,255,255))
        p.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        p.drawText(rect, QtCore.Qt.AlignCenter, text)
        p.restore()

    def paintEvent(self, e):
        if not self.wheel_visible:
            return

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # кольцо с прозрачным центром
        ring = QtGui.QPainterPath()
        ring.addEllipse(self.center_offset.x()-self.outer_radius,
                        self.center_offset.y()-self.outer_radius,
                        self.outer_radius*2,
                        self.outer_radius*2)
        hole = QtGui.QPainterPath()
        hole.addEllipse(self.center_offset.x()-self.inner_radius,
                         self.center_offset.y()-self.inner_radius,
                         self.inner_radius*2,
                         self.inner_radius*2)
        ring = ring.subtracted(hole)
        p.setPen(QtCore.Qt.NoPen)
        p.setBrush(QtGui.QColor(20,20,20,185))
        p.drawPath(ring)

        # рисуем логотип в центре
        logo_path = os.path.join(script_dir, "logo.png")
        if os.path.exists(logo_path):
            pix = QtGui.QPixmap(logo_path)
            logo_size = ((self.outer_radius - 50) * 1.8)
            pix = pix.scaled(logo_size, logo_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            p.drawPixmap(int(self.center_offset.x() - logo_size/2), 
                        int(self.center_offset.y() - logo_size/2), 
                        pix)

        # иконки
        for i, (x, y) in enumerate(self.icon_positions):
            if i == self.hover_index:
                self.draw_hover_circle(p, QtCore.QPointF(x,y))
            self.draw_icon(p, QtCore.QPointF(x,y), self.segments[i].get("icon"))

        # подменю
        if self.last_main_index is not None:
            submenu = self.segments[self.last_main_index].get("submenu")
            if submenu:
                for i, (x, y) in enumerate(self.submenu_positions):
                    if i >= len(submenu): 
                        continue

                    center = QtCore.QPointF(x, y)

                    # Подложка под иконкой подменю
                    radius_bg = self.icon_radius + 5
                    p.setBrush(QtGui.QColor(50, 50, 50, 200))
                    p.setPen(QtCore.Qt.NoPen)
                    p.drawEllipse(center, radius_bg, radius_bg)

                    # Hover-круг поверх подложки
                    if i == self.submenu_index:
                        self.draw_hover_circle(p, center)

                    # Иконка поверх подложки
                    self.draw_icon(p, center, submenu[i].get("icon"))

        # Рисуем текст поверх всего в конце
        if self.current_index is not None and self.current_index < len(self.icon_positions):
            x, y = self.icon_positions[self.current_index]
            self.draw_text_box(p, self.segments[self.current_index]["name"], QtCore.QPointF(x, y))
        
        if self.submenu_index is not None and self.last_main_index is not None:
            submenu = self.segments[self.last_main_index].get("submenu")
            if submenu and self.submenu_index < len(self.submenu_positions):
                x, y = self.submenu_positions[self.submenu_index]
                self.draw_text_box(p, submenu[self.submenu_index]["name"], QtCore.QPointF(x, y))

# ==============================
class SubItemWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.name_edit = QtWidgets.QLineEdit()
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["JS Script", "Keyboard Macro"])
        self.type_combo.setMaximumWidth(120)
        
        # Виджеты для JS
        self.js_combo = QtWidgets.QComboBox()
        self.js_combo.addItem("", "")
        self.js_combo.setMaximumWidth(150)
        
        # Виджеты для макроса
        self.macro_container = QtWidgets.QWidget()
        self.macro_layout = QtWidgets.QHBoxLayout(self.macro_container)
        self.macro_layout.setContentsMargins(0,0,0,0)
        
        self.key_combo = QtWidgets.QComboBox()
        self.key_combo.setMaximumWidth(80)
        
        # Заполняем список клавиш
        keys = [
            "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
            "0","1","2","3","4","5","6","7","8","9",
            "F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12",
            "enter","tab","space","escape","backspace","delete","insert","home","end","pageup","pagedown",
            "up","down","left","right",
            "print_screen","scroll_lock","pause","caps_lock","num_lock"
        ]
        for key in keys:
            self.key_combo.addItem(key)
        
        self.ctrl_check = QtWidgets.QCheckBox("Ctrl")
        self.shift_check = QtWidgets.QCheckBox("Shift")
        self.alt_check = QtWidgets.QCheckBox("Alt")
        
        self.macro_layout.addWidget(self.key_combo)
        self.macro_layout.addWidget(self.ctrl_check)
        self.macro_layout.addWidget(self.shift_check)
        self.macro_layout.addWidget(self.alt_check)
        
        self.icon_button = QtWidgets.QPushButton()
        self.icon_path = ""
        self.icon_button.setFixedSize(40,40)
        self.delete_button = QtWidgets.QPushButton("❌")

        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.js_combo)
        self.layout.addWidget(self.macro_container)
        self.layout.addWidget(self.icon_button)
        self.layout.addWidget(self.delete_button)

        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.js_combo.currentIndexChanged.connect(self.on_js_selected)
        self.icon_button.clicked.connect(self.choose_icon)
        
        # Заполняем комбобокс JS файлами
        js_files = get_js_files()
        for js_file in js_files:
            self.js_combo.addItem(js_file, js_file)
        
        # Изначально показываем JS виджеты
        self.on_type_changed(0)

    def on_type_changed(self, index):
        if index == 0:  # JS Script
            self.js_combo.show()
            self.macro_container.hide()
        else:  # Keyboard Macro
            self.js_combo.hide()
            self.macro_container.show()

    def on_js_selected(self, index):
        js_file = self.js_combo.currentData()
        if js_file:
            # Загружаем содержимое JS
            self.js_content = load_js_content(js_file)
            
            # Автоматически загружаем иконку
            self.icon_path = find_icon_for_js(js_file)
            if self.icon_path:
                pix = QtGui.QPixmap(self.icon_path).scaled(32,32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.icon_button.setIcon(QtGui.QIcon(pix))
                self.icon_button.setIconSize(pix.size())
            
            # Автоматически устанавливаем имя из названия файла
            if not self.name_edit.text():
                file_name = os.path.splitext(js_file)[0]
                self.name_edit.setText(file_name)

    def choose_icon(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.ico)")
        if path:
            self.icon_path = path
            pix = QtGui.QPixmap(path).scaled(32,32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.icon_button.setIcon(QtGui.QIcon(pix))
            self.icon_button.setIconSize(pix.size())

    def set_js_file(self, js_file):
        """Установить JS файл по имени"""
        index = self.js_combo.findData(js_file)
        if index >= 0:
            self.js_combo.setCurrentIndex(index)

    def to_dict(self):
        if self.type_combo.currentIndex() == 0:  # JS Script
            js_file = self.js_combo.currentData()
            js_content = getattr(self, "js_content", "")
            if not js_content and js_file:
                js_content = load_js_content(js_file)
            
            return {
                "type": "js",
                "name": self.name_edit.text(),
                "js": js_content,
                "icon": self.icon_path
            }
        else:  
            modifiers = []
            if self.ctrl_check.isChecked():
                modifiers.append("ctrl")
            if self.shift_check.isChecked():
                modifiers.append("shift")
            if self.alt_check.isChecked():
                modifiers.append("alt")
            
            return {
                "type": "macro",
                "name": self.name_edit.text(),
                "macro": {
                    "key": self.key_combo.currentText(),
                    "modifiers": modifiers
                },
                "icon": self.icon_path
            }

# ==============================
# Основной элемент с кнопками перемещения
class MainItemWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        top_layout = QtWidgets.QHBoxLayout()

        # Кнопки перемещения
        self.move_up_btn = QtWidgets.QPushButton("↑")
        self.move_up_btn.setFixedSize(30, 30)
        self.move_down_btn = QtWidgets.QPushButton("↓")
        self.move_down_btn.setFixedSize(30, 30)
        
        self.name_edit = QtWidgets.QLineEdit()
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["JS Script", "Keyboard Macro"])
        self.type_combo.setMaximumWidth(120)
        
        # Виджеты для JS
        self.js_combo = QtWidgets.QComboBox()
        self.js_combo.addItem("", "")
        self.js_combo.setMaximumWidth(150)
        
        # Виджеты для макроса
        self.macro_container = QtWidgets.QWidget()
        self.macro_layout = QtWidgets.QHBoxLayout(self.macro_container)
        self.macro_layout.setContentsMargins(0,0,0,0)
        
        self.key_combo = QtWidgets.QComboBox()
        self.key_combo.setMaximumWidth(80)
        
        # Заполняем список клавиш
        keys = [
            "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
            "0","1","2","3","4","5","6","7","8","9",
            "F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12",
            "enter","tab","space","escape","backspace","delete","insert","home","end","pageup","pagedown",
            "up","down","left","right",
            "print_screen","scroll_lock","pause","caps_lock","num_lock"
        ]
        for key in keys:
            self.key_combo.addItem(key)
        
        self.ctrl_check = QtWidgets.QCheckBox("Ctrl")
        self.shift_check = QtWidgets.QCheckBox("Shift")
        self.alt_check = QtWidgets.QCheckBox("Alt")
        
        self.macro_layout.addWidget(self.key_combo)
        self.macro_layout.addWidget(self.ctrl_check)
        self.macro_layout.addWidget(self.shift_check)
        self.macro_layout.addWidget(self.alt_check)
        
        self.icon_button = QtWidgets.QPushButton()
        self.icon_path = ""
        self.icon_button.setFixedSize(40,40)
        self.add_sub_button = QtWidgets.QPushButton("Add Sub")
        self.delete_button = QtWidgets.QPushButton("❌")

        top_layout.addWidget(self.move_up_btn)
        top_layout.addWidget(self.move_down_btn)
        top_layout.addWidget(self.name_edit)
        top_layout.addWidget(self.type_combo)
        top_layout.addWidget(self.js_combo)
        top_layout.addWidget(self.macro_container)
        top_layout.addWidget(self.icon_button)
        top_layout.addWidget(self.add_sub_button)
        top_layout.addWidget(self.delete_button)

        self.layout.addLayout(top_layout)
        self.sub_list = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.sub_list)

        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.js_combo.currentIndexChanged.connect(self.on_js_selected)
        self.icon_button.clicked.connect(self.choose_icon)
        self.add_sub_button.clicked.connect(self.add_sub_item)
        
        # Заполняем комбобокс JS файлами
        js_files = get_js_files()
        for js_file in js_files:
            self.js_combo.addItem(js_file, js_file)
        
        # Изначально показываем JS виджеты
        self.on_type_changed(0)

        # Связываем кнопки перемещения
        self.move_up_btn.clicked.connect(lambda: self.move_item(-1))
        self.move_down_btn.clicked.connect(lambda: self.move_item(1))

    def move_item(self, direction):
        """Переместить элемент вверх или вниз"""
        parent_layout = self.parent().layout()
        if parent_layout:
            index = parent_layout.indexOf(self)
            if 0 <= index + direction < parent_layout.count():
                # Получаем текущий виджет
                current_widget = parent_layout.itemAt(index).widget()
                # Удаляем текущий виджет
                parent_layout.removeWidget(current_widget)
                # Вставляем его на новую позицию
                parent_layout.insertWidget(index + direction, current_widget)

    def on_type_changed(self, index):
        if index == 0:  # JS Script
            self.js_combo.show()
            self.macro_container.hide()
        else:   # Keyboard Macro
            self.js_combo.hide()
            self.macro_container.show()

    def on_js_selected(self, index):
        js_file = self.js_combo.currentData()
        if js_file:
            # Загружаем содержимое JS
            self.js_content = load_js_content(js_file)
            
            # Автоматически загружаем иконку
            self.icon_path = find_icon_for_js(js_file)
            if self.icon_path:
                pix = QtGui.QPixmap(self.icon_path).scaled(32,32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.icon_button.setIcon(QtGui.QIcon(pix))
                self.icon_button.setIconSize(pix.size())
            
            # Автоматически устанавливаем имя из названия файла
            if not self.name_edit.text():
                file_name = os.path.splitext(js_file)[0]
                self.name_edit.setText(file_name)

    def choose_icon(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.ico)")
        if path:
            self.icon_path = path
            pix = QtGui.QPixmap(path).scaled(32,32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.icon_button.setIcon(QtGui.QIcon(pix))
            self.icon_button.setIconSize(pix.size())

    def set_js_file(self, js_file):
        """Установить JS файл по имени"""
        index = self.js_combo.findData(js_file)
        if index >= 0:
            self.js_combo.setCurrentIndex(index)

    def add_sub_item(self, data=None):
        sub_item = SubItemWidget()
        if data:
            sub_item.name_edit.setText(data.get("name",""))
            
            # Определяем тип элемента
            if data.get("type") == "macro":
                sub_item.type_combo.setCurrentIndex(1)  # Keyboard Macro
                macro_data = data.get("macro", {})
                sub_item.key_combo.setCurrentText(macro_data.get("key", "a"))
                modifiers = macro_data.get("modifiers", [])
                sub_item.ctrl_check.setChecked("ctrl" in modifiers)
                sub_item.shift_check.setChecked("shift" in modifiers)
                sub_item.alt_check.setChecked("alt" in modifiers)
            else:
                sub_item.type_combo.setCurrentIndex(0)  # JS Script
                js_content = data.get("js","")
                if js_content:
                    # Пытаемся найти файл, который содержит этот код
                    js_files = get_js_files()
                    for js_file in js_files:
                        file_content = load_js_content(js_file)
                        if file_content == js_content:
                            sub_item.set_js_file(js_file)
                            break
            
            sub_item.icon_path = data.get("icon","")
            if sub_item.icon_path and os.path.exists(sub_item.icon_path):
                pix = QtGui.QPixmap(sub_item.icon_path).scaled(32,32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                sub_item.icon_button.setIcon(QtGui.QIcon(pix))
                sub_item.icon_button.setIconSize(pix.size())

        self.sub_list.addWidget(sub_item)
        sub_item.delete_button.clicked.connect(lambda _, w=sub_item: self.sub_list.removeWidget(w) or w.deleteLater())

    def to_dict(self):
        sub_items = []
        for i in range(self.sub_list.count()):
            w = self.sub_list.itemAt(i).widget()
            if w:
                sub_items.append(w.to_dict())
        
        if self.type_combo.currentIndex() == 0:  # JS Script
            js_file = self.js_combo.currentData()
            js_content = getattr(self, "js_content", "")
            if not js_content and js_file:
                js_content = load_js_content(js_file)
            
            return {
                "type": "js",
                "name": self.name_edit.text(),
                "js": js_content,
                "icon": self.icon_path,
                "submenu": sub_items
            }
        else:  # Keyboard Macro
            modifiers = []
            if self.ctrl_check.isChecked():
                modifiers.append("ctrl")
            if self.shift_check.isChecked():
                modifiers.append("shift")
            if self.alt_check.isChecked():
                modifiers.append("alt")
            
            return {
                "type": "macro",
                "name": self.name_edit.text(),
                "macro": {
                    "key": self.key_combo.currentText(),
                    "modifiers": modifiers
                },
                "icon": self.icon_path,
                "submenu": sub_items
            }

# ==============================
# JSON Editor
class JSONEditor(QtWidgets.QWidget):
    def __init__(self, wheel: RadialWheel):
        super().__init__()
        self.wheel = wheel
        self.setWindowTitle("Radial Wheel JSON Editor")
        self.resize(1100,650)
        layout = QtWidgets.QVBoxLayout(self)

        # Первая строка: комбинация клавиш
        shortcut_layout = QtWidgets.QHBoxLayout()
        shortcut_layout.addWidget(QtWidgets.QLabel("Shortcut Key:"))
        self.shortcut_edit = QtWidgets.QLineEdit()
        self.shortcut_edit.setMaxLength(1)
        shortcut_layout.addWidget(self.shortcut_edit)
        
        # Чекбоксы для модификаторов
        self.ctrl_checkbox = QtWidgets.QCheckBox("Ctrl")
        self.shift_checkbox = QtWidgets.QCheckBox("Shift")
        self.alt_checkbox = QtWidgets.QCheckBox("Alt")
        shortcut_layout.addWidget(self.ctrl_checkbox)
        shortcut_layout.addWidget(self.shift_checkbox)
        shortcut_layout.addWidget(self.alt_checkbox)
        
        # Слайдер радиуса
        radius_label = QtWidgets.QLabel("Outer Radius:")
        self.radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radius_slider.setRange(100,300)
        self.radius_spin = QtWidgets.QSpinBox()
        self.radius_spin.setRange(100,300)
        shortcut_layout.addWidget(radius_label)
        shortcut_layout.addWidget(self.radius_slider)
        shortcut_layout.addWidget(self.radius_spin)

        layout.addLayout(shortcut_layout)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QtWidgets.QWidget()
        self.scroll.setWidget(self.container)
        self.items_layout = QtWidgets.QVBoxLayout(self.container)
        layout.addWidget(self.scroll)

        button_layout = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton("Add Item")
        self.save_button = QtWidgets.QPushButton("Save JSON")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.add_main_item)
        self.save_button.clicked.connect(self.save_json)

        # связь слайдер/спинбокс
        self.radius_slider.valueChanged.connect(self.radius_spin.setValue)
        self.radius_spin.valueChanged.connect(self.radius_slider.setValue)

        self.load_json()

    def add_main_item(self,data=None):
        item = MainItemWidget()
        if data:
            item.name_edit.setText(data.get("name",""))
            
            # Определяем тип элемента
            if data.get("type") == "macro":
                item.type_combo.setCurrentIndex(1)  # Keyboard Macro
                macro_data = data.get("macro", {})
                item.key_combo.setCurrentText(macro_data.get("key", "a"))
                modifiers = macro_data.get("modifiers", [])
                item.ctrl_check.setChecked("ctrl" in modifiers)
                item.shift_check.setChecked("shift" in modifiers)
                item.alt_check.setChecked("alt" in modifiers)
            else:
                item.type_combo.setCurrentIndex(0)  # JS Script
                js_content = data.get("js","")
                if js_content:
                    # Пытаемся найти файл, который содержит этот код
                    js_files = get_js_files()
                    for js_file in js_files:
                        file_content = load_js_content(js_file)
                        if file_content == js_content:
                            item.set_js_file(js_file)
                            break
            
            item.icon_path = data.get("icon","")
            if item.icon_path and os.path.exists(item.icon_path):
                pix = QtGui.QPixmap(item.icon_path).scaled(32,32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                item.icon_button.setIcon(QtGui.QIcon(pix))
                item.icon_button.setIconSize(pix.size())
            for sub in data.get("submenu", []):
                item.add_sub_item(sub)
        self.items_layout.addWidget(item)
        item.delete_button.clicked.connect(lambda _, w=item: self.items_layout.removeWidget(w) or w.deleteLater())

    def load_json(self):
        data = load_segments()
        self.shortcut_edit.setText(data.get("shortcut","Q"))
        
        # Загружаем модификаторы
        modifiers = data.get("modifiers", [])
        self.ctrl_checkbox.setChecked("ctrl" in modifiers)
        self.shift_checkbox.setChecked("shift" in modifiers)
        self.alt_checkbox.setChecked("alt" in modifiers)
        
        self.radius_slider.setValue(data.get("outer_radius",170))
        for seg in data.get("segments", []):
            self.add_main_item(seg)

    def save_json(self):
        segments = []
        for i in range(self.items_layout.count()):
            w = self.items_layout.itemAt(i).widget()
            if w:
                segments.append(w.to_dict())
        
        # Собираем модификаторы
        modifiers = []
        if self.ctrl_checkbox.isChecked():
            modifiers.append("ctrl")
        if self.shift_checkbox.isChecked():
            modifiers.append("shift")
        if self.alt_checkbox.isChecked():
            modifiers.append("alt")
        
        data = {
            "shortcut": self.shortcut_edit.text(),
            "modifiers": modifiers,
            "segments": segments,
            "outer_radius": self.radius_spin.value()
        }
        save_segments(data)
        self.wheel.refresh_segments()
        QtWidgets.QMessageBox.information(self, "Saved", "JSON saved and wheel updated!")

# ==============================
def keyboard_thread(wheel: RadialWheel):
    global keep_running
    last = False
    while keep_running: # Цикл завершится при изменении флага
        state = is_key_pressed(wheel.shortcut)
        if state and not last:
            wheel.show_signal.emit()
        if not state and last:
            wheel.hide_signal.emit()
        last = state
        time.sleep(0.02)

# ==============================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    wheel = RadialWheel()
    wheel.hide()
    
    # Запускаем поток
    thread = threading.Thread(target=keyboard_thread, args=(wheel,), daemon=True)
    thread.start()
    
    editor = JSONEditor(wheel)
    editor.show()
    
    # Сначала выполняем приложение Qt
    exit_code = app.exec()
    
    # ПОСЛЕ закрытия окон останавливаем всё остальное:
    keep_running = False  # Останавливаем цикл в keyboard_thread
    listener.stop()       # Принудительно отключаем хук pynput 
    
    sys.exit(exit_code)