//# sourceURL=../static/my/js/home.js
require(["dijit/layout/AccordionContainer",
		"dijit/Dialog",
		"dijit/ConfirmDialog",
		"dijit/form/Button",
		'dojo/dom',
		"dojo/dom-style",
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
		"dijit/ProgressBar",
		"dojo/domReady!"], 
function(AccordionContainer,Dialog,ConfirmDialog,Button,dom,domStyle, domConstruct, parser, registry, on, ContentPane, ExpandoPane, TabContainer, Model, Tree, Memory, ready,request,Standby,ProgressBar) {
	ready(function() {

		////////// CONFIGURATION //////////////////
		
		var viewsConfig = {}; //holds view config		
		viewsConfig['Comercial'] = [
			{'title':'FACTURAS', 'id':'Factura','template':'customCRUD','entityClass':'Factura'},
			{'title':'PEDIDOS', 'id':'Pedido','template':'','entityClass':'Pedido'},
			{'title':'CLIENTES', 'id':'Cliente','template':'','entityClass':'Cliente'},
			{'title':'PRODUCTOS', 'id':'Producto','template':'','entityClass':'Producto'},
			{'title':'PORCIONES', 'id':'Porcion','template':'','entityClass':'Porcion'},
			{'title':'GRUPOS DE PRECIOS', 'id':'GrupoDePrecios','template':'','entityClass':'GrupoDePrecios'},
			{'title':'PRECIOS', 'id':'Precio','template':'','entityClass':'Precio'},
		];
		
		viewsConfig["ContableFinanciero"] = [
			{'title':'EGRESOS', 'id':'Egreso','template':'customCRUD','entityClass':'Egreso'},
			{'title':'PROVEEDORES', 'id':'Proveedor','template':'','entityClass':'Proveedor'},
			{'title':'BIENES O SERVICIOS', 'id':'Bienoservicio','template':'','entityClass':'Bienoservicio'},
			{'title':'PAGOS', 'id':'PagoRecibido','template':'','entityClass':'PagoRecibido'},
			{'title':'ACTIVOS', 'id':'Activo','template':'','entityClass':'Activo'},
			{'title':'CAPITAL SOCIAL', 'id':'CapitalSocial','template':'','entityClass':'CapitalSocial'},
			{'title':'PASIVOS', 'id':'Pasivo','template':'','entityClass':'Pasivo'},
			{'title':'ACREEDORES', 'id':'Acreedor','template':'','entityClass':'Acreedor'},
			{'title':'SALDOS BANCOS', 'id':'SaldoCuentaBancaria','template':'','entityClass':'SaldoCuentaBancaria'},			
			{'title':'PUC', 'id':'PUC','template':'PUCSearch','entityClass':''},
		];
		
		viewsConfig["Operativo"] = [
			{'title':'MOV. INVENTARIO', 'id':'MovimientoDeInventario','template':'','entityClass':'MovimientoDeInventario'},
			{'title':'UNIDAD ALMACENAMIENTO', 'id':'UnidadDeAlmacenamiento','template':'','entityClass':'UnidadDeAlmacenamiento'},
			{'title':'CONSULTAR INVENTARIO', 'id':'ConsultarInventario','template':'existencias','entityClass':''},
			{'title':'MATERIA PRIMA', 'id':'MateriaPrima','template':'','entityClass':'MateriaPrima'},
			{'title':'PRODUCCION', 'id':'Produccion','template':'','entityClass':'Produccion'},
		];
		
		viewsConfig["Informes"] = [
			{'title':'VENTAS', 'id':'Ventas','template':'tablaDinamica','entityClass':'Ventas'},
			{'title':'GASTOS', 'id':'Gastos','template':'tablaDinamica','entityClass':'Gastos'},
			{'title':'CUENTAS POR COBRAR', 'id':'CuentasPorCobrar','template':'cuentasPorCobrar','entityClass':'CuentasPorCobrar'},
			{'title':'PAGOS VS FACTURAS', 'id':'Pagos','template':'InformeDePagos','entityClass':'Pagos'},
			{'title':'ESTADO DE RESULTADOS', 'id':'EstadoDeResultados','template':'estadoDeResultados','entityClass':''},
			{'title':'BALANCE', 'id':'Balance','template':'balance','entityClass':''},
			{'title':'IVA PAGADO', 'id':'IVA_PAGADO','template':'tablaDinamica','entityClass':'IVA_PAGADO'},
			{'title':'IVA RECAUDADO', 'id':'IVA_RECAUDADO','template':'tablaDinamica','entityClass':'IVA_RECAUDADO'},
			//{'title':'SALUDABLE HOY', 'id':'SaludableHoy','template':'SaludableHoy','entityClass':''}
		];

		viewsConfig["Admin"] = [
			{'title':'EMPLEADOS', 'id':'Empleado','template':'','entityClass':'Empleado'},
			{'title':'CUENTAS BANCARIAS', 'id':'CuentaBancaria','template':'','entityClass':'CuentaBancaria'},
			{'title':'BANCOS', 'id':'Banco','template':'','entityClass':'Banco'},
			{'title':'CIUDADES', 'id':'Ciudad','template':'','entityClass':'Ciudad'},
			{'title':'NUMEROS', 'id':'Numero','template':'numeros','entityClass':'Numero'}
		];

		///////////////////////////
		
		//Function to get views from server and load them in the center pane 
		var setView = function(contentPane, viewObj, viewsMap){
			if (!(viewObj['id'] in viewsMap)){
				request('/getWidget?template=' + viewObj['template'] + '&entityClass=' + viewObj['entityClass']).then(
						function(response){
							var cp = new ContentPane({content:response});
							viewsMap[viewObj['id']]=cp;
							domConstruct.empty("centerPane");
							contentPane.addChild(cp);
							registry.byId('layout').resize();
						}
				);					
			}else{
				domConstruct.empty("centerPane");
				contentPane.addChild(viewsMap[viewObj['id']]);
				registry.byId('layout').resize();
			}
		}
		
		saludable.widgetMap = {};//global widget cache
		
		var aContainer = new AccordionContainer({style:"height: 300px"}, "markup");
		var processCategories = ['Comercial','ContableFinanciero', 'Operativo', 'Informes','Admin']

		var createButtons = function (process, cp){
			views = viewsConfig[process];
			views.forEach(function(viewObj){
				var button = new Button({
			        label: viewObj['title'],
			        onClick: function(){
			        	setView(registry.byId('centerPane'), viewObj, saludable.widgetMap)	            
			        }
			    });
				button.startup()
				button.placeAt(cp);
			})
		}

		processCategories.forEach(function(process){
			var cp = new ContentPane({
		        title: process,
		        id : process,
		    });
			createButtons(process,cp);
			aContainer.addChild(cp);			
		});
		
		
	    //////////////////////////////////////////////////////////
	    registry.byId('launchpad').addChild(aContainer);
	    aContainer.startup();
	
		domStyle.set("Comercial_wrapper", "background-color", "#04f904");
		domStyle.set("ContableFinanciero_wrapper", "background-color", "#8482ff");
		domStyle.set("Operativo_wrapper", "background-color", "#0fefbb");
		domStyle.set("Informes_wrapper", "background-color", "#c0ff00");
		domStyle.set("Admin_wrapper", "background-color", "#ff9900");
	    
	    registry.byId('layout').resize();
	    
		//App-level spinner to show the server is working
		var standby = new Standby({id:'standby_centerPane', target: 'centerPane'});
		document.body.appendChild(standby.domNode);
		standby.startup();
		
		//App-level progress bar
		var progressDialog = new Dialog({
			title: "Obteniendo datos del servidor...",
	        style: "width: 300px",
	        id:'progress_dialog'
	    });
		
		var progressBar = new ProgressBar({
	        style: "width: 280px",
	        id: 'progress_bar'
	    })

		//App-level dialog to allow server to send messages to the user.
		var serverMessage = new Dialog({
	        title: "El servidor dice...",
	        style: "width: 300px",
	        id:'server_message'
	    });
		
		//App-level comnfirm dialog to allow server to send messages to the user.
		var confirmServerMessage = new ConfirmDialog({
	        title: "El servidor dice...",
	        style: "width: 500px",
	        id:'confirm_server_message'
	    });
	
		
	  });

}); 