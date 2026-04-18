# 🎡 TBH_RadialWheel
[Русская Версия Readme](README_RU.md)
<p align="center">
  <img width="300" height="300" alt="LogoMain" src="https://github.com/user-attachments/assets/0d10e0db-fa84-4a9f-8ea3-e66c29ee1b6b" />
</p>

**Harmony Radial Wheel** is a highly customizable radial menu designed to accelerate your workflow in **Toon Boom Harmony**. It allows you to instantly trigger JS scripts and keyboard macros through a visual interface that appears directly under your mouse cursor.

---

## ✨ Key Features
* **Full Customization**: Add any number of radial wheels, segments and submenus via the built-in graphical editor.
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

1. **Download**: Download the archive from the [latest release](https://github.com/moltycat/TBH_RadialWheel/releases/latest) 
2. **Unpack**: Extract the `HarmonyRadialWheel` folder to the root of your `C:\` drive.
   > ⚠️ **Verification**: Ensure the command file is located at: `C:\HarmonyRadialWheel\harmony_command.json`
3. **Python**: Install Python 3.13 from the [official website](https://www.python.org/downloads/) or use the installer in the folder:
   `C:\HarmonyRadialWheel\Setup\Setup 1 python 3.13.7.exe`
4. **Libraries**: Run `pip install pyside6 keyboard pynput` in your console or launch:
   `C:\HarmonyRadialWheel\Setup\Setup 2.bat`
5. **Harmony Files**:
   * Move `Molty_RadialWheel.js` to the Harmony scripts folder (ex. for TBH 25):
     `%AppData%\Roaming\Toon Boom Animation\Toon Boom Harmony Premium\2500-scripts\`
   * Move the `Molty_RadialWheel.png` icon to:
     `.../2500-scripts/script-icons/`
6. **Activation**: Add the `Molty_RadialWheel` script to your toolbar inside Harmony.

---

## 🛠 Usage

1. **Start Host**: Run the script inside Harmony. The window should display: `✅RadialWheelHost started✅`.
2. **Starting the wheel**: In the folder `C:\HarmonyRadialWheel\Molty_RadialWheel `run `Molty_RadialWheel.pyw'.
3. You can use multiple widgets simultaneously by assigning them to different keys.
4. **Operation**: Hold the hotkey → Hover over a sector → Release the key.
	> ⚠️ When the window is closed, it collapses into the tray, to close it completely, you need to press exit in the tray!

---

## ⚙️ Widget Configuration

In the editor window, you can:
* **Top Bar**: Configure the hotkey and external wheel radius.
* **Add Main Item / Add Sub**: Add main sectors or submenus.
* **Modes**: Switch between JS templates and Keyboard Macros.
* **Icons**: Manually set PNG paths or use auto-pick.
* **Order**: Reorder sectors using arrows.
* **Save JSON**: Save settings and apply changes instantly.

---

## 📂 File Structure
* `Molty_RadialWheel.pyw` — main executable file.
* `wheel_config.json` — current wheel configuration.
* `actions/` — folder containing your scripts.

---

## 🔗 Additional Scripts (NodeView)
The package includes built-in custom scripts:
  1. `Molty_rename_CompPeg` - renames selected composite pegs and deformers. If selected together with a drawing, it assigns its name.
  2. `Molty_xPivot_to_0` - sets the peg's X pivot coordinate to 0.
  3. `Molty_BG_Group_cleanV2` - you need to select a group with drawings, it automatically enters all folders and assigns pegs to drawings.
  4. `Molty_def_rename` - renames "deformation" to "def".
  5. `Molty_composite_AP_rename` - renames the composite based on nodes connected to it to create autopatch systems.
  6. `Molty_Layers_script` - allows you to choose layer templates under the selected drawing.
  7. `Molty_Line_Thickness_script` - adjusts the line thickness on the render to the specified pixel size.

---

## ✉️ Contacts
* **telegram**: @moltycat
* **email**: gnev112@yandex.ru
* **discord**: moltycat
