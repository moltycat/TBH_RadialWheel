# 🎡 TBH_RadialWheel
[Русская Версия Readme](README_RU.md)
<p align="center">
  <img width="300" height="300" alt="LogoMain" src="https://github.com/user-attachments/assets/0d10e0db-fa84-4a9f-8ea3-e66c29ee1b6b" />
</p>

**Harmony Radial Wheel** is a highly customizable radial menu designed to accelerate your workflow in **Toon Boom Harmony**. It allows you to instantly trigger JS scripts and keyboard macros through a visual interface that appears directly under your mouse cursor.

---

## ✨ Key Features
* **Full Customization**: Add any number of segments and submenus via the built-in graphical editor.
* **Two Types of Actions**:
  1. **JS Script**: Execute JavaScript code (integrated with Harmony via a command file).
  2. **Keyboard Macro**: Emulate key presses with modifier support (Ctrl, Shift, Alt).
* **Smart Hotkeys**: Assign menu activation to any key.
* **Visual Editor**: Configure menu radius, item names, and select custom PNG icons.
* **Automation**: Automatic detection of icons and names when selecting a script from the `actions` folder.

---

## 💻 System Requirements
* **OS**: Windows
* **Environment**: Toon Boom Harmony (Premium recommended)
* **Language**: Python 3.13+

---

## 🚀 Installation

1. **Download**: Download the archive from the latest release.
2. **Unpack**: Extract the `HarmonyRadialWheel` folder to the root of your `C:\` drive.
   > ⚠️ **Verification**: Ensure the command file is located at: `C:\HarmonyRadialWheel\harmony_command.json`
3. **Python**: Install Python 3.13 from the [official website](https://www.python.org/downloads/) or use the installer in the folder:
   `C:\HarmonyRadialWheel\Setup\Setup 1 python 3.13.7.exe`
4. **Libraries**: Run `pip install PySide6 pynput` in your console or launch:
   `C:\HarmonyRadialWheel\Setup\Setup 2.bat`
5. **Harmony Files**:
   * Move `Molty_RadialWheel.js` to the Harmony scripts folder:
     `%AppData%\Roaming\Toon Boom Animation\Toon Boom Harmony Premium\2500-scripts\`
   * Move the `Molty_RadialWheel.png` icon to:
     `.../2500-scripts/script-icons/`
   * *(Optional for Rigging)* Move scripts from `Setup\HarmonyFiles\Scripts` to the Harmony resources folder:
     `C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 25 Premium\resources\scripts\`
6. **Activation**: Add the `Molty_RadialWheel` script to your toolbar inside Harmony.

---

## 🛠 Usage

1. **Start Host**: Run the script inside Harmony. The window should display: `✅RadialWheelHost started✅`.
2. **Input Language**: **Important!** Switch your keyboard layout to English before launching `.pyw` files.
3. **Select Wheel**: In `C:\HarmonyRadialWheel`, choose a template and run the shortcut or `Molty_RadialWheel.pyw`.
   * `Animation` — for animation tasks.
   * `Drawing` — for drawing tools.
   * `NodeView` — for rigging.
   * `Custom` — your own custom template.
4. You can use multiple widgets simultaneously by assigning them to different keys.
5. You can create as many widget folders and new templates as you need.
6. **Operation**: Hold the hotkey → Hover over a sector → Release the key.

---

## ⚙️ Widget Configuration

In the editor window, you can:
* **Top Bar**: Configure the hotkey and external wheel radius.
* **Add Item / Add Sub**: Add main sectors or submenus.
* **Modes**: Switch between JS templates and Keyboard Macros.
* **Icons**: Manually set PNG paths or use auto-pick.
* **Order**: Reorder sectors using arrows.
* **Save JSON**: Save settings and apply changes instantly.

---

## 📂 File Structure
* `logo.png` — the center icon of the wheel.
* `Molty_RadialWheel.pyw` — main executable file.
* `wheel_config.json` — current wheel configuration.
* `actions/` — folder containing your scripts.

---

## 🔗 Additional Scripts (NodeView)
The package includes custom scripts:
* **Standalone Scripts** (Require separate installation):
  1. `Molty_Layers_script`: Allows choosing layer templates under the selected drawing.
  2. `Molty_Line_Thickness_script`: Sets render line thickness to specific pixel sizes (supports 1080p and 4k).
* **Built-in JS Templates**:
  1. `Molty_rename_CompPeg`: Renames selected pegs, composites, and deformers. If selected with a drawing, it inherits the drawing's name.
  2. `Molty_xPivot_to_0`: Resets the peg's X pivot coordinate to 0.
  3. `Molty_BG_Group_clean`: Select a group with drawings; it automatically enters all folders and assigns pegs to drawings.
  4. `Molty_def_rename`: Renames "deformation" to "def".
  5. `Molty_composite_AP_rename`: Renames composites based on connected nodes to assist in Autopatch system creation.
