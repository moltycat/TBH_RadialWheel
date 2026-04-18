(function() {
    function Molty_SmartRename() {
        var selectionNodes = selection.selectedNodes(0);
        if (selectionNodes.length === 0) return;

        scene.beginUndoRedoAccum("Molty_SmartRename");

        // Проверяем наличие рисунков (READ нод) в выделении
        var readNodes = selectionNodes.filter(function(n) { return node.type(n) === "READ"; });

        if (readNodes.length > 0) {
            // ЛОГИКА С РИСУНКАМИ: берем имя первого выбранного рисунка
            var baseName = node.getName(readNodes[0]);
            var newCompName = "C-" + baseName;
            var newPegName = baseName + "-P";
            var newGroupName = "Def-" + baseName;

            for (var i = 0; i < selectionNodes.length; i++) {
                var sNode = selectionNodes[i];
                var type = node.type(sNode);
                if (type === "COMPOSITE") safeRename(sNode, newCompName);
                else if (type === "PEG") safeRename(sNode, newPegName);
                else if (type === "GROUP") safeRename(sNode, newGroupName);
            }
        } else {
            // ЛОГИКА БЕЗ РИСУНКОВ: Пеги от Пегов, Композы от Композов
            for (var i = 0; i < selectionNodes.length; i++) {
                var sNode = selectionNodes[i];
                var type = node.type(sNode);

                if (type === "PEG") {
                    var childPegNames = [];
                    var numOutput = node.numberOfOutputLinks(sNode, 0);
                    
                    for (var j = 0; j < numOutput; j++) {
                        var dNode = node.dstNode(sNode, 0, j);
                        // Берем имя только если это PEG
                        if (node.type(dNode) === "PEG") {
                            childPegNames.push(node.getName(dNode).replace("-P", ""));
                        }
                    }

                    applyNewName(sNode, childPegNames, "", "-P");
                } 
                
                else if (type === "COMPOSITE") {
                    var parentCompNames = [];
                    var numInput = node.numberOfInputPorts(sNode);
                    
                    for (var j = 0; j < numInput; j++) {
                        var src = node.srcNode(sNode, j);
                        // Берем имя только если это COMPOSITE
                        if (src && node.type(src) === "COMPOSITE") {
                            var cName = node.getName(src).replace("C-", "");
                            if (parentCompNames.indexOf(cName) === -1) {
                                parentCompNames.push(cName);
                            }
                        }
                    }

                    applyNewName(sNode, parentCompNames, "C-", "");
                }
            }
        }

        scene.endUndoRedoAccum("Molty_SmartRename");
    }

    // Вспомогательная функция формирования имени и приставки _master
    function applyNewName(sNode, namesArray, prefix, suffix) {
        if (namesArray.length === 0) return;

        var finalName = "";
        if (namesArray.length === 1) {
            finalName = prefix + namesArray[0] + "_master" + suffix;
        } else {
            finalName = prefix + namesArray.join("+") + suffix;
        }
        
        safeRename(sNode, finalName);
    }

    // Безопасное переименование с проверкой уникальности
    function safeRename(sNode, newName) {
        if (!node.rename(sNode, newName)) {
            for (var x = 1; x < 2000; x++) {
                if (node.rename(sNode, newName + "_" + x)) break;
            }
        }
    }

    // Запуск
    Molty_SmartRename();

})();