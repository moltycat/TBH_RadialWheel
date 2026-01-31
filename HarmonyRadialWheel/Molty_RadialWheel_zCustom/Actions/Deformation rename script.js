(function() {
    var addedPrefics = "Def";
    var deletedPrefics = "Deformation";
    var selectionNodes = selection.selectedNodes();

    if (selectionNodes.length === 0) return;

    scene.beginUndoRedoAccum("Molty_def_rename");

    for (var i = 0; i < selectionNodes.length; ++i) {
        var sNode = selectionNodes[i];
        var nodeName = node.getName(sNode);
        
        // Заменяем "Deformation" на "Def" в имени узла
        if (nodeName.indexOf(deletedPrefics) !== -1) {
            var newNodeName = nodeName.replace(deletedPrefics, addedPrefics);
            node.rename(sNode, newNodeName);
        }
    }

    scene.endUndoRedoAccum();
})();