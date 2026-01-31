var selectionNodes = selection.selectedNodes(); // Получаем массив всех выделенных нод
		for (var i = 0; i < selectionNodes.length; i++) {
			var sNode = selectionNodes[i]; // Текущая нода из выделения

			var nodeName = node.getName(sNode);
			var parent = node.parentNode(sNode);
			var x = node.coordX(sNode);
			var y = node.coordY(sNode);
			var z = node.coordZ(sNode);

			
			var cutterNode = node.add(parent,"Cut", "CUTTER", x, y + 80, z);
			node.link(sNode, 0, cutterNode, 0);
		}

