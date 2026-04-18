(function() {
    var selectionNodes = selection.selectedNodes();
    scene.beginUndoRedoAccum("Rename Comp by Source");

    for (var i = 0; i < selectionNodes.length; ++i) {
        var sNode = selectionNodes[i];
        
        // Работаем только с Композитами
        if (node.type(sNode) === "COMPOSITE") {
            
            // Устанавливаем красный цвет, как в оригинале
            node.setColor(sNode, new ColorRGBA(255, 0, 0, 255));
            
            var newCompName = "";
            var numInput = node.numberOfInputPorts(sNode);

            for (var j = 0; j < numInput; ++j) {
                var parentNode = node.srcNode(sNode, j);
                if (!parentNode) continue;

                var finalRead = null;

                // Если это сразу Read-нода
                if (node.type(parentNode) === "READ") {
                    finalRead = parentNode;
                } else {
                    // Ищем Read-ноду вверх по иерархии (до 10 уровней)
                    var tempNode = parentNode;
                    for (var z = 0; z < 10; ++z) {
                        var nextNode = node.srcNode(tempNode, node.numberOfInputPorts(tempNode) - 1);
                        if (!nextNode) break;
                        if (node.type(nextNode) === "READ") {
                            finalRead = nextNode;
                            break;
                        }
                        tempNode = nextNode;
                    }
                }

                if (finalRead) {
                    var readName = node.getName(finalRead);
                    if (newCompName === "") {
                        newCompName = "AP-" + readName;
                    } else {
                        newCompName += "+" + readName;
                    }
                }
            }

            // Переименовываем с проверкой на уникальность
            if (newCompName !== "") {
                if (!node.rename(sNode, newCompName)) {
                    for (var x = 1; x < 100; ++x) { // Уменьшил цикл до 100 для скорости
                        if (node.rename(sNode, newCompName + "_" + x)) break;
                    }
                }
            }
        }
    }
    scene.endUndoRedoAccum();
})();