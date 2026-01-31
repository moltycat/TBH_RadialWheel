(function() {
    // 1. Указываем прямой путь к файлу скрипта
    var scriptName = "Molty Line Thickness script.js";
    var scriptPath = "C:/Program Files (x86)/Toon Boom Animation/Toon Boom Harmony 25 Premium/resources/scripts/" + scriptName;
	
    // 2. Загружаем файл в память
    try {
        include(scriptPath);
        
        // 3. Вызываем функцию Molty_line_scale_dependent из загруженного файла
        if (typeof this.Molty_line_scale_dependent === 'function') {
            this.Molty_line_scale_dependent();
        } else if (typeof Molty_line_scale_dependent === 'function') {
            Molty_line_scale_dependent();
        } else {
            MessageBox.information("Файл загружен, но функция Molty_line_scale_dependent не найдена внутри него.");
        }
    } catch (e) {
        // Заменяем обратные слеши на прямые для корректного отображения в алерте Harmony
        MessageBox.information("Не удалось найти файл по пути: " + scriptPath);
    }
})();