//# sourceURL=../static/my/js/home.js
require([
		"dijit/Dialog",
		'dojo/dom',
		 "dojo/dom-construct",
		'dojo/parser',
		"dijit/registry",
		"dojo/on",
		'dijit/layout/ContentPane',
		"dojox/layout/ExpandoPane",
		"dijit/layout/TabContainer",
		"dijit/tree/ObjectStoreModel",
		"dijit/Tree", 
		"dojo/store/Memory", 
		"dojo/ready",
		'dojo/request',
		"dojox/widget/Standby", 
		"dojo/domReady!"], 
function(Dialog,dom, domConstruct, parser, registry, on, ContentPane, ExpandoPane, TabContainer, Model, Tree, Memory, ready,request,Standby) {
	ready(function() {

		/* CREATER CENTER TAB CONTAINER */
		
		var centerTabContainer = new TabContainer({
	        style: "height: 100%; width: 100%;"
	    });

		/* CREATE TABS and wire them up*/
		
		var tabs = [
			{'title':'CREAR FACTURA', 'id':'Factura','template':'crearFactura','entityClass':'Factura'},
			{'title':'CREAR EGRESO', 'id':'Egreso','template':'crearEgreso','entityClass':'Egreso'},
			{'title':'REGISTRAR PAGO', 'id':'PagoRecibido','template':'','entityClass':'PagoRecibido'},
			{'title':'MOVIMIENTO DE INVENTARIO', 'id':'MovimientoDeInventario','template':'','entityClass':'MovimientoDeInventario'},
			{'title':'CONSULTAR INVENTARIO', 'id':'ConsultarInventario','template':'Existencias','entityClass':''},
			{'title':'CREAR CLIENTE', 'id':'Cliente','template':'','entityClass':'Cliente'},
			{'title':'CREAR PROVEEDOR', 'id':'Proveedor','template':'','entityClass':'Proveedor'},
			{'title':'VENTAS', 'id':'Ventas','template':'tablaDinamica','entityClass':'Ventas'},
			//{'title':'SALUDABLE HOY', 'id':'SaludableHoy','template':'SaludableHoy','entityClass':''}
		];
		
		var getTabContent = function(tab){
			request('/getWidget?template=' + tab['template'] + '&entityClass=' + tab['entityClass']).then(
					function(response){
						var cp = registry.byId(tab['id']);
						cp.set('content',response);
						saludable.widgetCache[tab['id']]=cp;
					}
			);	

		}
		
		var tabsMap = {};
		tabs.forEach(function(tab){
			tabsMap[tab['id']] = tab;
		    var newTab = new ContentPane({
		        id: tab['id'], 
		    	title: tab['title'],
		    });
		    tabsMap[tab['id']]['widget']=newTab;
		    
		    centerTabContainer.addChild(newTab);			
		})
		
		centerTabContainer.watch("selectedChildWidget", function(name, oval, nval){
		        console.log("selected child changed from ", oval.title, " to ", nval.title);
				if (!saludable.widgetCache.hasOwnProperty(nval.id)){ 
					getTabContent(tabsMap[nval.id]);
				}
		});
	    	    
	    //AQUI EMPIEZA LA CARGA DE LA APPLICACION
		centerTabContainer.startup();
		getTabContent(tabsMap['Factura']);
	    registry.byId('centerPane').addChild(centerTabContainer);
		
		
		
		/* CREATE NAVIGATION TREE*/
		
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
		var activoCirculanteNodes = makeStore(['MovimientoDeEfectivo','SaldoCuentaBancaria',{name:'CuentasPorCobrar',template:'CuentasPorCobrar'},{name:'Inventarios',clickable:false}],'Activos Circulantes'); 
		var inventarioNodes = makeStore(['MovimientoDeInventario','UnidadDeAlmacenamiento',{name:'Existencias',clickable:true, template:'Existencias'}],'Inventarios');
		var pasivoNodes = makeStore(['CapitalSocial',{name:'Deudas',clickable:false}],'Pasivos');
		var deudaNodes = makeStore(['Deuda',{name:'AdminDeudas',clickable:false}],'Deudas');
		var adminDeudasNodes = makeStore(['Acreedor','TipoAcreedor'],'AdminDeudas');
		var ingresoNodes = makeStore(['Pedido',{name:'Factura', clickable:true, template:'crearFactura'},{name:'Remisiones',clickable:false},'PagoRecibido','OtrosIngresos',{name:'AdminIngresos',clickable:false}],'Ingresos');
		var adminIngresoNodes = makeStore(['Cliente','Producto','Porcion','GrupoDePrecios','Precio'],'AdminIngresos');
		var remisionNodes = makeStore(['Remision',{name:'Consolidar Factura', clickable:true, template:'ConsolidarFactura'}],'Remisiones');
		var egresoNodes = makeStore(['Egreso','FacturaDeProveedor', 'Compra',{name:'Fruta', clickable:true, template:'crearEgresoFruta'},'LoteDeCompra' ,{name:'AdminEngresos',clickable:false} ],'Egresos');
		var adminEgresoNodes = makeStore(['Proveedor','Bienoservicio','TipoEgreso'],'AdminEngresos');
		var adminNodes = makeStore(['Sucursal','Empleado','Ciudad','CapitalPagado','CuentaBancaria','Banco','TipoDeCuenta','MedioDePago','CuentaTransferencias',{name:'PUC', clickable:false},'Fruta','Fuente','TipoMovimiento'],'Admin');
		var pucNodes = makeStore([{name:'Buscar Cuenta', clickable:true, template:'PUCSearch'},'Clase','Cuenta','Grupo','SubCuenta'],'PUC');
		var numeroNodes = makeStore(['Numeros'],'Admin','numeros');
		
		//Informes
		var informeNodes = makeStore(['Ventas','Gastos',{name:'Pagos',clickable:true,template:'InformeDePagos'}],'Informes','tablaDinamica');
		var estadosFinancierosNodes = makeStore([{name:'Estados Financieros',clickable:false}],'Informes');
		var estadoDeRedultadosNode = makeStore([{name:'Estado de Resultados',clickable:true, template:'EstadoDeResultados'}],'Estados Financieros');
		
		
		
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
		data.push.apply(data,estadosFinancierosNodes);
		data.push.apply(data,estadoDeRedultadosNode);
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
	
	saludable.getWidget = function(id){
		if(saludable.widgetCache.hasOwnProperty(id)){ 
			return saludable.widgetCache[id];
		}else if(tabsMap.hasOwnProperty(id)){
			return tabsMap[id]['widget']
		}
	};


	
	saludable.widgetCache['topTab'] = centerTabContainer;
	
	registry.byId('goHome').onClick = function(){
		domConstruct.empty("centerPane");
		registry.byId('centerPane').addChild(centerTabContainer);
	};

	//App-level spinner to show the server is working
	var standby = new Standby({id:'standby_centerPane', target: 'centerPane'});
	document.body.appendChild(standby.domNode);
	standby.startup();	
	
	//App-level dialog to allow server to send messages to the user.
	var serverMessage = new Dialog({
        title: "El servidor dice...",
        style: "width: 300px",
        id:'server_message'
    });


	tree.onClick = function(item, node, evt){
		if (!item.clickable) return;
		var entityClass = item.id;
		saludable.entityClass = entityClass;
		if (saludable.widgetCache.hasOwnProperty(entityClass)){ 
			var widget = saludable.widgetCache[entityClass];
			domConstruct.empty("centerPane");
			registry.byId('centerPane').addChild(widget);
		}else if(tabsMap.hasOwnProperty(entityClass)){
			registry.byId('goHome').onClick();
			centerTabContainer.selectChild(tabsMap[entityClass]['widget']);
		}else{
			if (item.alreadyClicked) return;
			item.alreadyClicked=true;
			standby.show();
			request('/getWidget?entityClass=' + entityClass + '&template=' + item.template).then(
				function(response){
					var contentPane = new ContentPane({content:response});
					saludable.widgetCache[entityClass]=contentPane;
					domConstruct.empty("centerPane");
					registry.byId('centerPane').addChild(contentPane);
					registry.byId('layout').resize();
				}
			);	
		}
	};
	
  });

}); 