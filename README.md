# TBH_RadialWheel

Harmony Radial Wheel — это настраиваемое радиальное меню, разработанное для ускорения рабочего процесса в Toon Boom Harmony (или других приложениях). Оно позволяет мгновенно вызывать JS-скрипты и клавиатурные макросы через визуальный интерфейс, который появляется прямо под курсором мыши. 

Основные возможности:
* Полная кастомизация: Добавляйте любое количество сегментов и подменю через встроенный графический редактор. 
* Два типа действий:
  1 JS Script: Выполнение JavaScript кода (интеграция с Harmony через файл команд). 
  2 Keyboard Macro: Эмуляция нажатий клавиш с поддержкой модификаторов (Ctrl, Shift, Alt). 
* Умные хоткеи: Возможность назначить активацию меню на любую клавишу в сочетании с модификаторами. 
* Визуальный редактор: Настройка радиуса меню, имен элементов и выбор иконок (PNG). 
* Автоматизация: Автоматическое подтягивание иконок и названий при выборе скрипта из папки actions. 


======================Установка===========================
* Скачать и распоковать файлы по пути "C:\HarmonyRadialWheel\", Убедитесь, что полсе распоковки файл с командами будет на нужном месте "C:\HarmonyRadialWheel\harmony_command.json"
* Установите Python 3.13 с офф сайта https://www.python.org/downloads/ или воспользуйтесь установщиком в "C:\HarmonyRadialWheel\Setup\Setup 1 python 3.13.7.exe"
* После установки python установите необходимые библиотеки через cmd (pip install PySide6 pynput) или воспользуйтесь установщиком "C:\HarmonyRadialWheel\Setup\Setup 2.bat"
* перместите файл "C:\HarmonyRadialWheel\Setup\HarmonyFiles\Molty_RadialWheel.js" по пути "C:\Users\****\AppData\Roaming\Toon Boom Animation\Toon Boom Harmony Premium\2500-scripts\Molty_RadialWheel.js"
если используете другую версию хармони, то вместо 2500-scripts выберете соответсвующую папку
* Переместите файл "C:\HarmonyRadialWheel\Setup\HarmonyFiles\Molty_RadialWheel.png" по пути "C:\Users\sok-g\AppData\Roaming\Toon Boom Animation\Toon Boom Harmony Premium\2500-scripts\script-icons\Molty_RadialWheel.png"
* Для полного функционала перместите файлы  Molty_Layers_script.js и Molty_Line_Thicknessю.js из папки "C:\HarmonyRadialWheel\Setup\HarmonyFiles\Scripts" по пути "C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 25 Premium\resources\scripts\"
если у вас не 25 версия, то необходимо выбрать нужну папку в "C:\Program Files (x86)\Toon Boom Animation\"
* добавьте скрипт Molty_RadialWheel в интерфейсе toon boom harmony как обычный скрипт

======================Использование===========================









Установка
Клонируйте репозиторий:

Bash

git clone https://github.com/vash-username/harmony-radial-wheel.git
cd harmony-radial-wheel
Установите зависимости:

Bash

pip install PySide6 pynput
Подготовьте структуру:

Создайте папку actions в директории скрипта и поместите туда свои .js скрипты. 

Поместите файл logo.png в корневую папку (он будет отображаться в центре колеса). 

Использование
Запустите основной скрипт:

Bash

python Molty_RadialWheel.pyw
В открывшемся окне JSON Editor:

Настройте Shortcut Key (по умолчанию Q). 

Добавьте элементы через кнопку Add Item. 

Нажмите Save JSON, чтобы применить изменения. 

Удерживайте заданную клавишу (например, Q), чтобы вызвать колесо. Наведите мышь на нужный сектор и отпустите клавишу для выполнения действия. 


Структура файлов

Molty_RadialWheel.pyw — основной исполняемый файл приложения. 


wheel_config.json — файл конфигурации вашего меню (создается автоматически). 


actions/ — папка для ваших скриптов и их иконок. 


C:\HarmonyRadialWheel\harmony_command.json — файл, через который передаются команды в Harmony. 

Хотите, чтобы я помог составить README.md на английском языке или добавил раздел с описанием того, как подключить этот инструмент к самой Harmony?
