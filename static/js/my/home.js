//# sourceURL=../static/js/my/home.js
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

		var makeStore = function(nodes,parent,template){
			var data = [];
			nodes.forEach(function(node){
				data.push(
					{
						id: (node.name ? node.name : node), //default to a simple node string
						name: (node.name ? node.name : node),
						parent: parent,
						clickable: (node.clickable == false ? false : true),//default to true
						template:(node.template ? node.template : template)
				});
			});
			return data;
		};
		
		var activoNodes = makeStore([{name:'ActivoFijo', clickable:true},{name:'Activos Circulantes', clickable:false}],'Activos');
		var activoNodes2 = makeStore(['SaldoCuentaBancaria',{name:'CuentasPorCobrar',template:'CuentasPorCobrar'},'Inventario'],'Activos Circulantes'); 
		var pasivoNodes = makeStore(['CapitalSocial',{name:'Deudas',clickable:false}],'Pasivos');
		var deudaNodes = makeStore(['Acreedor','Deuda','TipoAcreedor'],'Deudas');
		var ingresoNodes = makeStore(['Factura','Remision','Cliente','Producto','Porcion','GrupoDePrecios','Precio','OtrosIngresos'],'Ingresos');
		var egresoNodes = makeStore(['Egreso','Proveedor','Bienoservicio','TipoEgreso'],'Egresos');
		var adminNodes1 = makeStore(['Sucursal','Empleado','Ciudad','CapitalPagado','CuentaBancaria','Banco','TipoDeCuenta',{name:'PUC', clickable:false}],'Admin');
		var adminNodes2 = makeStore(['Clase','Cuenta','Grupo','SubCuenta'],'PUC');
		var adminNodes3 = makeStore(['Numeros'],'Admin','numeros');
		var informeNodes = makeStore(['Ventas','Gastos','Tendencias','IVA'],'Informes','tablaDinamica');
		var informeNodes2 = makeStore(['PyG'],'Informes','pYg');
		var data = [{id : 'root', name : 'root'},
					{id : 'Activos', name:'Activos', parent:'root', clickable:false},
					{id : 'Pasivos', name:'Pasivos', parent:'root', clickable:false},
					{id : 'Ingresos', name : 'Ingresos', parent:'root', clickable:false},
					{id : 'Egresos', name : 'Egresos', parent:'root', clickable:false},
					{id : 'Informes', name : 'Informes', parent:'root', clickable:false},
					{id : 'Admin', name : 'Admin', parent:'root', clickable:false}];
		data.push.apply(data,activoNodes);
		data.push.apply(data,activoNodes2);
		data.push.apply(data,pasivoNodes);			
		data.push.apply(data,ingresoNodes);
		data.push.apply(data,egresoNodes);
		data.push.apply(data,deudaNodes);
		data.push.apply(data,adminNodes1);
		data.push.apply(data,adminNodes2);
		data.push.apply(data,adminNodes3);
		data.push.apply(data,informeNodes);
		data.push.apply(data,informeNodes2);
		
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
        store: myStore,
        query: {id: 'root'}
    });
    // Create the Tree.
    var tree = new Tree({
        model: myModel,
        showRoot : false
    });
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