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
		
		//Financiero y contable
		var activoNodes = makeStore([{name:'ActivoFijo', clickable:true},{name:'Activos Circulantes', clickable:false}],'Activos');
		var activoCirculanteNodes = makeStore(['SaldoCuentaBancaria',{name:'CuentasPorCobrar',template:'CuentasPorCobrar'},{name:'Inventarios',clickable:false}],'Activos Circulantes'); 
		var inventarioNodes = makeStore(['MovimientoDeInventario','UnidadDeAlmacenamiento',{name:'Existencias',clickable:true, template:'Existencias'}],'Inventarios');
		var pasivoNodes = makeStore(['CapitalSocial',{name:'Deudas',clickable:false}],'Pasivos');
		var deudaNodes = makeStore(['Deuda',{name:'AdminDeudas',clickable:false}],'Deudas');
		var adminDeudasNodes = makeStore(['Acreedor','TipoAcreedor'],'AdminDeudas');
		var ingresoNodes = makeStore(['Pedido','Factura',{name:'Remisiones',clickable:false},'PagoRecibido','OtrosIngresos',{name:'AdminIngresos',clickable:false}],'Ingresos');
		var adminIngresoNodes = makeStore(['Cliente','Producto','Porcion','GrupoDePrecios','Precio'],'AdminIngresos');
		var remisionNodes = makeStore(['Remision',{name:'Consolidar Factura', clickable:true, template:'ConsolidarFactura'}],'Remisiones');
		var egresoNodes = makeStore(['Egreso', {name:'Fruta', clickable:true, template:'EgresoFruta'},'LoteDeCompra' ,{name:'AdminEngresos',clickable:false} ],'Egresos');
		var adminEgresoNodes = makeStore(['Proveedor','Bienoservicio','TipoEgreso'],'AdminEngresos');
		var adminNodes = makeStore(['Sucursal','Empleado','Ciudad','CapitalPagado','CuentaBancaria','Banco','TipoDeCuenta','MedioDePago','CuentaTransferencias',{name:'PUC', clickable:false},'Fruta','Fuente','TipoMovimiento'],'Admin');
		var pucNodes = makeStore(['Clase','Cuenta','Grupo','SubCuenta'],'PUC');
		var numeroNodes = makeStore(['Numeros'],'Admin','numeros');
		
		//Informes
		var informeNodes = makeStore(['Ventas','Gastos',{name:'Pagos',clickable:true,template:'InformeDePagos'}],'Informes','tablaDinamica');
		var utilidadesNodes1 = makeStore([{name:'Utilidades',clickable:false}],'Informes');
		var utilidadesNodes2 = makeStore([{name:'Utilidades Simple',clickable:true, template:'Utilidades'}, 
		                                  {name:'UtilidadesDetallado',clickable:true, template:'tablaDinamica'},],'Utilidades');
		//var pYgNodes = makeStore(['PyG'],'Informes','pYg');
		//var IVANodes = makeStore(['Recaudado','Pagado'],'IVA','tablaDinamica');
		var data = [{id : 'root', name : 'root'},
		            //Financiero
		            {id : 'Financiero', name:'Financiero', parent:'root', clickable:false},
					{id : 'Activos', name:'Activos', parent:'Financiero', clickable:false},
					{id : 'Pasivos', name:'Pasivos', parent:'Financiero', clickable:false},
					{id : 'Ingresos', name : 'Ingresos', parent:'Financiero', clickable:false},
					{id : 'Egresos', name : 'Egresos', parent:'Financiero', clickable:false},
					//Industrial
					{id : 'Industrial', name:'Industrial', parent:'root', clickable:false},
					{id : 'Produccion', name : 'Produccion', parent:'Industrial', clickable:true},
					//Cumplimiento Legal
					{id : 'Cumplimiento', name:'Cumplimiento Legal', parent:'root', clickable:false},
					{id : 'ResiduosSolidos', name:'Residuos Solidos', parent:'Cumplimiento', template:'ResiduosSolidos', clickable:true},
					{id : 'AguaPotable', name:'Agua Potable', parent:'Cumplimiento', template:'AguaPotable', clickable:true},
					{id : 'LimpiezaDesinfeccion', name:'Limpieza y Desinfeccion', parent:'Cumplimiento', template:'LimpiezaDesinfeccion', clickable:true},
					{id : 'ControlDePlagas', name:'Control de Plagas', parent:'Cumplimiento', template:'ControlDePlagas',clickable:true},
					{id : 'TemperaturaCuartoFrio', name:'Temperatura Cuarto Frio', parent:'Cumplimiento', template:'TemperaturaCuartoFrio',clickable:true},
					{id : 'Capacitacion', name:'Capacitacion', parent:'Cumplimiento', template:'Capacitacion',clickable:true},
					//Informes
					{id : 'Informes', name : 'Informes', parent:'root', clickable:false},
					//Admin sistema
					{id : 'Admin', name : 'Admin Sistema', parent:'root', clickable:false}];
		data.push.apply(data,activoNodes);
		data.push.apply(data,activoCirculanteNodes);
		data.push.apply(data,inventarioNodes);
		data.push.apply(data,pasivoNodes);			
		data.push.apply(data,ingresoNodes);
		data.push.apply(data,remisionNodes);
		data.push.apply(data,adminIngresoNodes);
		data.push.apply(data,egresoNodes);
		data.push.apply(data,adminEgresoNodes);
		data.push.apply(data,deudaNodes);
		data.push.apply(data,adminDeudasNodes);
		data.push.apply(data,adminNodes);
		data.push.apply(data,pucNodes);
		data.push.apply(data,numeroNodes);
		data.push.apply(data,informeNodes);
		data.push.apply(data,utilidadesNodes1);
		data.push.apply(data,utilidadesNodes2);
		//data.push.apply(data,pYgNodes);
		//data.push.apply(data,IVANodes);		
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
        id: 'rootTree',
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
			if (item.alreadyClicked) return;
			item.alreadyClicked=true;
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