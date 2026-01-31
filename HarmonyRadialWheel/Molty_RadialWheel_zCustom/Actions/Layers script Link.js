(function() {
    // 1. Указываем имя файла
    var scriptName = "Molty Layers script.js";
    var scriptPath = "C:/Program Files (x86)/Toon Boom Animation/Toon Boom Harmony 25 Premium/resources/scripts/" + scriptName;
    // 2. Загружаем файл в память
    try {
        include(scriptPath);
        
        // 3. Вызываем функцию через глобальный контекст (this)
        if (typeof this.Molty_Layers_script === 'function') {
            this.Molty_Layers_script();
        } else if (typeof Molty_Layers_script === 'function') {
            Molty_Layers_script();
        } else {
            MessageBox.information("Файл загружен, но функция Molty_Layers_script не найдена внутри него.");
        }
    } catch (e) {
        MessageBox.information("Не удалось найти файл по пути: " + scriptPath);
    }
})();


