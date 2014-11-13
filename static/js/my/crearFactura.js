//# sourceURL=../static/js/my/crearFactura.js

require(['dojo/dom','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 'dijit/form/Button', 
"gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/json","dojo/number"], 
function(dom,registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number) {
	
	updateTotal = function(){
		var data = getGridData();
		var sumTotal=0;
		data.forEach(function(entry){
			sumTotal = sumTotal + entry.precio * entry.cantidad ;
		});
		dom.byId('total').innerHTML = number.format(sumTotal,{pattern:'###,###'});
		return sumTotal;
	};
	
	getFormData = function(){
		var formdata = registry.byId('ventaForm').get('value');
		for (prop in formdata) {
			formdata[prop.replace('crearFactura', '')] = formdata[prop];
			delete formdata[prop];
		}
		return formdata;
	};
	
	getGridData = function(){
		var store = registry.byId('gridFactura').store;
		return store.query();
	};
	
	parser.instantiate([dom.byId('guardarFacturaBtn')]);
	on(registry.byId('guardarFacturaBtn'),'click',
		function(e){
			var cliente = registry.byId('clientecrearFactura').value;
			var empleado = registry.byId('empleadocrearFactura').value;		
			var fecha = registry.byId('fechacrearFactura').toString();
			var gridData = getGridData();//delete gridData.forEach;delete gridData.map;delete gridData.filter;
			var factura_data = {'cliente':cliente,'empleado':empleado,'fecha':fecha,'ventas':gridData, 'total':grid.total};
			request.post('/guardarFactura', {
					data : json.stringify(factura_data)
				}).then(function(response) {
					var message='';
					resp = response.split(':');
					if(resp[0] == 'Success'){
						message = 'Se grabo exitosamente este pedido!';
						window.open('/mostrarFactura?facturaId='+resp[1]);
					}else{
						message = 'No se pudo guardar este pedido!';
					}
					dom.byId('mensajecrearFactura').innerHTML = message;
					setTimeout(function() {
						var grid =registry.byId('gridFactura');
						grid.store.data=[];
						grid.model.clearCache();
        				grid.body.refresh();
						dom.byId('mensajecrearFactura').innerHTML = '';
						dom.byId('total').innerHTML = '';
					}, 3000);
				});
		});
	
	parser.instantiate([dom.byId('agregarPedidoBtn')]);
	on(registry.byId('agregarPedidoBtn'),'click',function(e){
		var form = registry.byId('ventaForm');
		if (!form.validate()){
			alert("'Cantidad' no puede estar vacio!");
			return;
		}
		var formdata = getFormData();
		request.post("getPrice",
		{
			data: {'producto':formdata['producto'], 'cliente':formdata['cliente'], 'porcion': formdata['porcion']}
		}).then(function(precio){
			if (precio == 'list index out of range'){
				alert("No hay precio definido para esta combinacion producto x cliente! Definelo primero.");
				return;	
			}
			var grid = registry.byId('gridFactura');
			var id = formdata['producto'] + formdata['cliente'] + formdata['porcion'];
			var row = grid.store.get(id);
			if (row){
				grid.store.remove(id);	
			}
			var total = formdata.cantidad * parseInt(precio);
			grid.store.add({'id':id,'producto':formdata.producto, 'cliente':formdata.cliente, 'porcion': formdata.porcion,'cantidad':formdata.cantidad, 
							'precio': parseInt(precio), 'valorTotal':total});
			grid.total=updateTotal();
			//registry.byId('ventaForm').reset();
		});

		
	});
	var store = new Store();
	var columns = [
		{field : 'producto', name : 'Producto', style: "text-align: center"},
		{field : 'porcion', name : 'Porcion', style: "text-align: center"},
		{field : 'cantidad', name : 'Cantidad', style: "text-align: center"},
		{field : 'precio', name : 'Precio Unitario', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.precio,{pattern:'0,000'});
				}
		},
		{field : 'valorTotal', name : 'Valor Total', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.valorTotal,{pattern:'###,###'});
				}
		},
		{ 	field : 'Borrar', 
			style: "text-align: center",
			name : '', 
			widgetsInCell : true, 
			onCellWidgetCreated : 
			function(cellWidget, column) {
				var btn = new Button({
					label : "Borrar",
					onClick : function() {
						// get the selected row's ID
						var selectedRowId = cellWidget.cell.row.id;
						// get the data
						var rowData = grid.row(selectedRowId, true).rawData();
						grid.store.remove(selectedRowId);
        				grid.model.clearCache();
        				grid.body.refresh();
        				updateTotal();
					}
				});
				btn.placeAt(cellWidget.domNode);
			}
		}
	];
	var grid = new Grid({
		cacheClass : Cache,
		store : store,
		structure : columns,
		modules : ["gridx/modules/CellWidget"]
	}, 'gridFactura');
	grid.startup();
}); 
