require(['dojo/dom',
		 "dojo/dom-construct",
		'dojo/parser',
		"dijit/registry",
		"dojo/on",
		'dijit/layout/ContentPane', 
		"dijit/tree/ObjectStoreModel",
		"dijit/Tree", 
		"dojo/store/Memory", 
		"dojo/ready",
		'dojo/request', 
		"dojo/domReady!"], 
function(dom, domConstruct, parser, registry, on, ContentPane, Model, Tree, Memory, ready,request) {
	ready(function() {
		
		var makeStore = function(nodes,parent){
			var data = [];
			nodes.forEach(function(node){
				data.push(
					{
						id: node,
						name: node,
						parent: parent,
						clickable: true
				});
			});
			return data;
		};
		
		var ingresoNodes = makeStore(['Cliente','Producto','GrupoDePrecios','Precio','Factura'],'Ingresos');
		var egresoNodes = makeStore(['TipoEgreso','Egreso','Bienoservicio','PorcionInsumo','Proveedor'],'Egresos');
		var data = [{id : 'root', name : 'root'},
					{id : 'Ingresos', name : 'Ingresos', parent:'root', clickable:false},
					{id : 'Egresos', name : 'Egresos', parent:'root', clickable:false}];
		data.push.apply(data,ingresoNodes);
		data.push.apply(data,egresoNodes);
		data.push.apply(data,[
			{id: 'Analisis', name: 'Analisis', parent: 'root'},
			{id: 'Clientes', name: 'Clientes', parent: 'Analisis', clickable: true, template: 'pivot'},
			{id: 'Productos', name: 'Productos', parent: 'Analisis', clickable: true, template: 'pivot'}
		]);
		
		var myStore = new Memory({
		data : data,
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
		showRoot : false,
		getIconClass: function(item){
    		return "dijitFolderClosed";
		}
	});
	tree.model.mayHaveChildren = function (item){
		return item.leaf;
	};

	tree.placeAt(dom.byId('tree'));
	tree.startup();
	registry.byId('layout').resize();
	
	
	tree.onOpen = function(item,node){
		registry.byId('layout').resize();
	};
	
	saludable.widgetCache = {};
	
	tree.onClick = function(item, node, evt){
		if (!item.clickable) return;
		var entityClass = item.id;
		saludable.entity_class = entityClass;
		if (saludable.widgetCache.hasOwnProperty('widget'+entityClass)){ 
			var widget = saludable.widgetCache['widget'+entityClass];
			domConstruct.empty("centerPane");
			registry.byId('centerPane').addChild(widget);
		}else{
			request('/getWidget?entityClass=' + entityClass + '&template=' + item.template).then(
				function(response){
					var contentPane = new ContentPane({content:response});
					saludable.widgetCache['widget'+entityClass]=contentPane;
					domConstruct.empty("centerPane");
					registry.byId('centerPane').addChild(contentPane);
					registry.byId('layout').resize();
				}
			);	
		}
	};		
	});

}); 