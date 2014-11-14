//# sourceURL=../static/js/my/crearFactura.js

require(['dojo/dom','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 'dijit/form/Button', 
"gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/json","dojo/number"], 
function(dom,registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number) {
	var entity_class = saludable.entity_class;
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
		var formdata = registry.byId('addEntityForm' + entity_class).get('value');
		for (prop in formdata) {
			formdata[prop.replace('Factura', '')] = formdata[prop];
			delete formdata[prop];
		}
		return formdata;
	};
	
	getGridData = function(){
		var store = registry.byId('gridFactura').store;
		return store.query();
	};
	
	actualizarFacturas = function(response, data){
		var grid = registry.byId("gridNodeFactura");
		var key = response.facturaId;
		if (response.action == 'Created') {
			data['id'] = key;
			grid ? grid.store.add(data) : '' ;
			response_user = 'Se creo Factura: ' + data.numero;
		} else {
			if(grid){
				var row = grid.store.get(key);
				grid.store.remove(key);
				data['id'] = key;
				grid.store.add(data);					
			}
		}
	};
	
	parser.instantiate([dom.byId('guardarFacturaBtn')]);
	on(registry.byId('guardarFacturaBtn'),'click',
		function(e){
			var cliente = registry.byId('clienteFactura').value;
			var empleado = registry.byId('empleadoFactura').value;		
			var fecha = registry.byId('fechaFactura').toString();
			var gridData = getGridData();//delete gridData.forEach;delete gridData.map;delete gridData.filter;
			var factura_data = {'cliente':cliente,'empleado':empleado,'fecha':fecha,'ventas':gridData, 'total':grid.total};
			request.post('/guardarFactura', {
					data : json.stringify(factura_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.action == 'Created'){
						message = 'Se grabo exitosamente este pedido!';
						factura_data['cliente']=registry.byId('clienteFactura').attr('displayedValue');
						actualizarFacturas(response, factura_data);
						window.open('/mostrarFactura?facturaId='+response.facturaId);
					}else{
						message = 'No se pudo guardar este pedido!';
					}
					dom.byId('mensajeFactura').innerHTML = message;
					setTimeout(function() {
						var grid =registry.byId('gridFactura');
						grid.store.data=[];
						grid.model.clearCache();
        				grid.body.refresh();
						dom.byId('mensajeFactura').innerHTML = '';
						dom.byId('total').innerHTML = '';
					}, 3000);
				});
		});
	
	parser.instantiate([dom.byId('agregarPedidoBtn')]);
	on(registry.byId('agregarPedidoBtn'),'click',function(e){
		var form = registry.byId('addEntityForm' + entity_class);
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
			var id = formdata['producto'] + formdata['porcion'];
			var row = grid.store.get(id);
			if (row){
				grid.store.remove(id);	
			}
			var total = formdata.cantidad * parseInt(precio);
			grid.store.add({'id':id,'producto':formdata.producto, 'cliente':formdata.cliente, 'porcion': formdata.porcion,'cantidad':formdata.cantidad, 
							'precio': parseInt(precio), 'valorTotal':total});
			grid.total=updateTotal();
			//registry.byId('addEntityForm' + entity_class).reset();
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
