//# sourceURL=../static/js/my/InformeDePagos.js
require(['dojo/request',
		 "dijit/registry",
		 'dojo/parser',
		 'dojo/dom',
		 'dojo/on',
		 'dojo/query',
		 "dojox/widget/Standby",
		 'dojo/store/Memory',
		 'dojo/aspect',
		 'dojo/dom-class',
		 "dojo/number",
		 'gridx/Grid',
		 'gridx/core/model/cache/Sync',
		 'gridx/modules/SingleSort'
], 
function(request,registry,parser,dom,on,query,Standby, Store, aspect, domClass, number, Grid, Cache) {
	parser.instantiate([dom.byId('GenerarInformeBtn_Pagos')]);
	//Modal to show its loading
	var standby = new Standby({target: 'pagos_standby'});
	document.body.appendChild(standby.domNode);
	standby.startup();
	
	var facturaStore = new Store();
	var factura_columns = [
		{field : 'numero', name : '#', style: "text-align: center;", width:'2em'},
		{field : 'cliente', name : 'Negocio', style: "text-align: center",width:'15em'},
		{field : 'total', name : 'Monto', style: "text-align: center", width:'4.5em',
				formatter: function(data){
					return number.format(data.total,{pattern:'###,###'});
				}		
		},
		{field : 'fecha', name : 'Fecha', style: "text-align: center",width:'5em'},
		{field : 'fechaVencimiento', name : 'Vence', style: "text-align: center"},
	];
	
	var facturasGrid = new Grid({
	cacheClass : Cache,
	store : facturaStore,
	structure : factura_columns,
	modules : [	'gridx/modules/SingleSort'
				]
	}, 'pagos_facturas');
	
	//Colorear factura pagadas o vencidas
	aspect.after(facturasGrid.body, 'onAfterRow', function(row) {
		var key = row.id;
		var record = row.grid.store.get(key); 
		var vence = record ['fechaVencimiento'].replace(/-/g, '\/').replace(/T.+/, '');
		if (record['pagada'] == true){
			row.node().style.color = 'green';
		}else if (new Date(vence) < new Date()){
			row.node().style.color = 'red';
		}
	}, true);
	
	facturasGrid.startup();
	domClass.add(dom.byId('pagos_facturas'),'pagos-factura-grid');

	var pagoStore = new Store();
	var pago_columns = [
		{field : 'numero', name : '#', style: "text-align: center",width:'2.5em'},
		{field : 'fecha', name : 'Fecha', style: "text-align: center",width:'5em'},
		{field : 'monto', name : 'Monto', style: "text-align: center",width:'5em',
				formatter: function(data){
					return number.format(data.monto,{pattern:'###,###'});
				}		
		},
		{field : 'medio', name : 'Medio', style: "text-align: center",width:'4.5em'},
		{field : 'facturas', name : 'Facturas', style: "text-align: center", width:'15em'}
	];
	
	var pagosGrid = new Grid({
	cacheClass : Cache,
	store : pagoStore,
	structure : pago_columns,
	modules : [	'gridx/modules/SingleSort'
				]
	}, 'pagos_pagos');
	facturasGrid.startup();
	domClass.add(dom.byId('pagos_pagos'),'pagos-pagos-grid');
	
	on(registry.byId('GenerarInformeBtn_Pagos'),'click', function(e){
		var desde = registry.byId('fecha_pagos_1').value.toISOString().split('T')[0];
		var hasta =  registry.byId('fecha_pagos_2').value.toISOString().split('T')[0];
		var cliente = registry.byId('pagos_cliente').value;
		var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta + '&cliente=' + encodeURIComponent(cliente) ;
		standby.show(); 
		request('/informePagos?' + appendUrl, {handleAs:'json'}).then(function(response) {
			var facturas = response.facturas;
			var pagos = response.pagos;
			facturas_grid = registry.byId('pagos_facturas');
			pagos_grid = registry.byId('pagos_pagos'); 
			facturas_grid.model.clearCache();
			facturas_grid.model.store.setData([]);
			facturas.forEach(function(item){
							facturas_grid.store.add(item);								
			});
			facturas_grid.body.refresh();
			pagos_grid.model.clearCache();
			pagos_grid.model.store.setData([]);
			pagos.forEach(function(item){
							pagos_grid.store.add(item);								
			});			
			pagos_grid.body.refresh();
			standby.hide();
		});		
	});
	registry.byId('standby_centerPane').hide();
}); 