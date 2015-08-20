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
		"dojox/widget/Standby", 
		"dojo/domReady!"], 
function(dom, domConstruct, parser, registry, on, ContentPane, Model, Tree, Memory, ready,request,Standby) {
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
		var activoCirculanteNodes = makeStore(['SaldoCuentaBancaria',{name:'CuentasPorCobrar',template:'CuentasPorCobrar'},{name:'Inventarios',clickable:false}],'Activos Circulantes'); 
		var inventarioNodes = makeStore(['Inventario',{name:'Existencias',clickable:true, template:'Existencias'}],'Inventarios');
		var pasivoNodes = makeStore(['CapitalSocial',{name:'Deudas',clickable:false}],'Pasivos');
		var deudaNodes = makeStore(['Acreedor','Deuda','TipoAcreedor'],'Deudas');
		var ingresoNodes = makeStore(['Factura','Remision','PagoRecibido','Cliente','Producto','Porcion','GrupoDePrecios','Precio','OtrosIngresos'],'Ingresos');
		var egresoNodes = makeStore(['Egreso','Proveedor','Bienoservicio','TipoEgreso'],'Egresos');
		var adminNodes = makeStore(['Sucursal','Empleado','Ciudad','CapitalPagado','CuentaBancaria','Banco','TipoDeCuenta','MedioDePago','CuentaTransferencias',{name:'PUC', clickable:false}],'Admin');
		var pucNodes = makeStore(['Clase','Cuenta','Grupo','SubCuenta'],'PUC');
		var numeroNodes = makeStore(['Numeros'],'Admin','numeros');
		var informeNodes = makeStore(['Ventas','Gastos','Tendencias',{name:'IVA',clickable:false}],'Informes','tablaDinamica');
		var pYgNodes = makeStore(['PyG'],'Informes','pYg');
		var IVANodes = makeStore(['Recaudado','Pagado'],'IVA','tablaDinamica');
		var data = [{id : 'root', name : 'root'},
					{id : 'Activos', name:'Activos', parent:'root', clickable:false},
					{id : 'Pasivos', name:'Pasivos', parent:'root', clickable:false},
					{id : 'Ingresos', name : 'Ingresos', parent:'root', clickable:false},
					{id : 'Egresos', name : 'Egresos', parent:'root', clickable:false},
					{id : 'Produccion', name : 'Produccion', parent:'root', clickable:true},
					{id : 'Informes', name : 'Informes', parent:'root', clickable:false},
					{id : 'Admin', name : 'Admin', parent:'root', clickable:false}];
		data.push.apply(data,activoNodes);
		data.push.apply(data,activoCirculanteNodes);
		data.push.apply(data,inventarioNodes);
		data.push.apply(data,pasivoNodes);			
		data.push.apply(data,ingresoNodes);
		data.push.apply(data,egresoNodes);
		data.push.apply(data,deudaNodes);
		data.push.apply(data,adminNodes);
		data.push.apply(data,pucNodes);
		data.push.apply(data,numeroNodes);
		data.push.apply(data,informeNodes);
		data.push.apply(data,pYgNodes);
		data.push.apply(data,IVANodes);		
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
	
	var standby = new Standby({id:'standby_centerPane', target: 'centerPane'});
	document.body.appendChild(standby.domNode);
	standby.startup();	

	tree.onClick = function(item, node, evt){
		if (!item.clickable) return;
		var entityClass = item.id;
		saludable.entity_class = entityClass;
		if (saludable.widgetCache.hasOwnProperty('widget'+entityClass)){ 
			var widget = saludable.widgetCache['widget'+entityClass];
			domConstruct.empty("centerPane");
			registry.byId('centerPane').addChild(widget);
		}else{
			standby.show();
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