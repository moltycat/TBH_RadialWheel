(function() {
    function Molty_xPivot_to_zero() {
        var exeDialog = new private_exeDialog();

        scene.beginUndoRedoAccum("Molty_xPivot_to_zero");
        exeDialog.main();
        scene.endUndoRedoAccum("Molty_xPivot_to_zero");
    }

    function private_exeDialog() {
        this.main = function() {
            var selectionNodes = selection.selectedNodes(0);
            var successCount = 0;

            for (var i = 0; i < selectionNodes.length; ++i) {
                var sNode = selectionNodes[i];
                var type = node.type(sNode);

                // Работаем только с PEG и READ нодами
                if (type == "PEG" || type == "READ") {
                    var pivotAttr = node.getAttr(sNode, frame.current(), "pivot.x");
                    
                    // Если атрибут pivot существует (проверка через наличие списка атрибутов)
                    if (pivotAttr) {
                        var yAttr = node.getAttr(sNode, frame.current(), "pivot.y");
                        var zAttr = node.getAttr(sNode, frame.current(), "pivot.z");
                        
                        // Создаем новую точку с X = 0 и сохраняем текущие Y и Z
                        var newPivot = new Point3d(0, yAttr.doubleValue(), zAttr.doubleValue());
                        
                        // Находим основной атрибут Pivot для установки значения Point3d
                        var myAttrs = node.getAttrList(sNode, frame.current(), "");
                        for (var j = 0; j < myAttrs.length; j++) {
                            if (myAttrs[j].name() == "Pivot") {
                                myAttrs[j].setValue(newPivot);
                                successCount = 1;
                                break;
                            }
                        }
                    }
                }
            }

            if (successCount == 1) {
                MessageBox.information("!!!Success!!!");
            }
        };
    }

    // Автоматический запуск функции при вызове скрипта
    Molty_xPivot_to_zero();

})();