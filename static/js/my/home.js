require(['dojo/dom',
		'dojo/parser',
		"dijit/registry",
		"dojo/on", 
		"dijit/tree/ObjectStoreModel", 
		"dijit/Tree", 
		"dojo/store/Memory", 
		"dojo/ready",
		'dojo/request', 
		"dojo/domReady!"], 
function(dom, parser, registry, on, Model, Tree, Memory, ready,request) {
	ready(function() {
			var myStore = new Memory({
		data : [{
			id : 'root',
			name : 'root'
		}, {
			id : 'Ingresos',
			name : 'Ingresos',
			parent:'root'
		}, {
			id : 'Egresos',
			name : 'Egresos',
			parent:'root'
		}, {
			id : 'addDataIngresos',
			name : 'Agregar Datos',
			parent : 'Ingresos'
		}, {
			id : 'showDataIngresos',
			name : 'Mostrar Datos Existentes',
			parent : 'Ingresos'
		}, {
			id : 'addDataEgresos',
			name : 'Agregar Datos',
			parent : 'Egresos'
		}, {
			id : 'showDataEgresos',
			name : 'Mostrar Datos Existentes',
			parent : 'Egresos'
		}],
		getChildren : function(object) {
			return this.query({
				parent : object.id
			});
		}
	});

	// Create the model
	var myModel = new Model({
		store : myStore,
		query : {
			id : 'root'
		}
	});

	// Create the Tree.
	var tree = new Tree({
		model : myModel,
		showRoot : false
	});
	tree.placeAt(dom.byId('tree'));
	tree.startup();
	
	tree.onClick = function(item, node, evt){
		var info = item.id.split('Data');
		var params = 'accion=' + info[0] + '&tipo='+info[1];
		request('/getWidget?'+params).then(); 
	};

	//ready(function() {
	//	var setEntityClass = function(event) {
	//		saludable.entity_class = this.selectedChildWidget.id.split('_')[0];
	//	};

	//	parser.instantiate([dom.byId('addTabContainer'), dom.byId('showTabContainer'), dom.byId('pivotTabContainer')]);

	//	var panelIngresosAdd = registry.byId('addIngresosTabContainer');
	//	var panelEgresosAdd = registry.byId('addEgresosTabContainer');
	//	var panelIngresoShow = registry.byId('showIngresosTabContainer');
	//	var panelEgresoShow = registry.byId('showEgresosTabContainer');

	//	on(panelIngresosAdd, "Click", setEntityClass);
	//	on(panelEgresosAdd, "Click", setEntityClass);
	//	on(panelIngresoShow, "Click", setEntityClass);
	//	on(panelEgresoShow, "Click", setEntityClass);
	//});
		
	});

}); 