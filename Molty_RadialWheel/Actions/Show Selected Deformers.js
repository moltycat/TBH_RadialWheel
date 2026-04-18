var selectedNodes = selection.selectedNodes();
  
  for (var i = 0; i < selectedNodes.length; i++) {
    var currentNode = selectedNodes[i];
    Action.perform("onActionShowDeformer(QString)", "miniPegModuleResponder", currentNode);
  }