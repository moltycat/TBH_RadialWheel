(function() {
    function Molty_BG_Group_clean() {
        var exeDialog = new private_exeDialog();

        scene.beginUndoRedoAccum("Molty_BG_Group_clean");
        exeDialog.main();
        scene.endUndoRedoAccum("Molty_BG_Group_clean");
    }

    function private_exeDialog() {
        this.main = function() {
            var selectionNodes = selection.selectedNodes(0);
            if (selectionNodes.length === 0) return;

            var sNode = selectionNodes[0];
            var x = node.coordX(sNode);
            var y = node.coordY(sNode);
            var z = node.coordZ(sNode);
            
            // Создаем мастер-пег для всей выделенной иерархии
            var MasterPEG = node.add(node.parentNode(sNode), "BG-Master-P", "PEG", x, y - 160, z);

            for (var i = 0; i < selectionNodes.length; ++i) {
                sNode = selectionNodes[i];
                processNode(sNode, MasterPEG);
            }

            // Если была выбрана только одна нода, удаляем лишний мастер-пег сверху
            if (selectionNodes.length <= 1) {
                node.deleteNode(MasterPEG, false, false);
            }
        };
    }

    // Универсальная функция обработки ноды (READ или GROUP)
    function processNode(targetNode, parentPeg) {
        var type = node.type(targetNode);
        var x = node.coordX(targetNode);
        var y = node.coordY(targetNode);
        var z = node.coordZ(targetNode);
        var parentPath = node.parentNode(targetNode);

        if (type === "READ") {
            var NewPEG = node.add(parentPath, node.getName(targetNode) + "-P", "PEG", x, y - 80, z);
            node.unlink(targetNode, 0);
            node.link(NewPEG, 0, targetNode, 0);
            node.link(parentPeg, 0, NewPEG, 0);
        } 
        else if (type === "GROUP") {
            // Очистка и пересоздание входного порта группы
            var inputModule = node.getGroupInputModule(targetNode, "", 0, 0, 0);
            var inx = node.coordX(inputModule);
            var iny = node.coordY(inputModule);
            var inz = node.coordZ(inputModule);
            node.deleteNode(inputModule, false, false);
            inputModule = node.getGroupInputModule(targetNode, "", inx, iny - 300, inz);

            var groupPeg = node.add(parentPath, node.getName(targetNode) + "-P", "PEG", x, y - 80, z);
            var tempPEG = node.add(targetNode, "temp-P", "PEG", 0, 0, 0);

            node.unlink(targetNode, 0);
            node.link(inputModule, 0, tempPEG, 0, true, true);
            node.link(groupPeg, 0, targetNode, 0, true, true);
            node.link(parentPeg, 0, groupPeg, 0);
            node.deleteNode(tempPEG, false, false);

            // Рекурсивный вызов для внутренностей группы
            GroupClean(targetNode);
        }
    }

    function GroupClean(Gnode) {
        var subNodes = node.subNodes(Gnode);
        var GinputModule = node.getGroupInputModule(Gnode, "", 0, 0, 0);
        var Ginx = node.coordX(GinputModule);
        var Giny = node.coordY(GinputModule);
        var Ginz = node.coordZ(GinputModule);
        
        // Создаем временный внутренний мастер-пег для организации структуры внутри
        var InternalMaster = node.add(Gnode, node.getName(Gnode) + "_master-P", "PEG", Ginx, Giny + 160, Ginz);
        node.link(GinputModule, 0, InternalMaster, 0, false, false);

        for (var i = 0; i < subNodes.length; ++i) {
            var sNode = subNodes[i];
            var type = node.type(sNode);
            
            // Те же действия, что и в основном цикле, но внутри группы
            if (type === "READ" || type === "GROUP") {
                processNode(sNode, InternalMaster);
            }
        }
        
        // Удаляем временный мастер-пег, если он не нужен или для очистки иерархии (согласно вашей логике)
        node.deleteNode(InternalMaster, false, false);
    }

    // Запуск основной функции
    Molty_BG_Group_clean();

})();