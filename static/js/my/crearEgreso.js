//# sourceURL=../static/js/my/crearEgreso.js

require(['dojo/dom','dojo/dom-attr','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 
		'dijit/form/Button', "gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/json","dojo/number",'dijit/form/Select',
		'dojo/dom-class', 'dojo/ready', 'dojo/topic','gridx/modules/SingleSort'], 
function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number,Select,domClass, ready,topic) {
	var entity_class = saludable.entity_class;	
	
	resetProveedor = function(proveedor){	
		request.post('/getProveedores', {handleAs:'json'}).then(function(response){
			var items = [];
			response.forEach(function(proveedor){
				items.push({ "value": proveedor.value, "label": proveedor.name });
			});
			var proveedorSelect = registry.byId('proveedorEgreso');
			proveedorSelect.options = items;
			proveedorSelect.reset();
		});
	};
	
	
	resetBienServicio = function(proveedor){	
			request.post('/getBienServicio', {
					data : {'proveedor':proveedor},
					handleAs:'json'
				}).then(function(response) {
					var items = [];
					response.forEach(function(bienservicio){
						items.push({ "value": bienservicio, "name": bienservicio });
					});
					var bienservicioStore = new Store({
			        	idProperty: "value",
			            data: items
			        });
					var bienservicioSelect = registry.byId('productoFactura');
					bienservicioSelect.setStore(bienservicioStore);
					bienservicioSelect.reset();
					resetPorcion(bienservicioSelect.value);
			});
		};	
	
	resetPorcion = function(bienservicio){
			proveedor = registry.byId('proveedorEgreso').value;	
			request.post('/getPorcion', {
					data : {'proveedor':proveedor, 'bienoservicio': bienservicio},
					handleAs:'json'
				}).then(function(response) {
					var items = [];
					response.forEach(function(porcion){
						items.push({ "value": porcion, "name": porcion });
					});
					var porcionStore = new Store({
			        	idProperty: "value",
			            data: items
			        });
					var porcionSelect = registry.byId('porcionFactura');
					porcionSelect.setStore(porcionStore);
					porcionSelect.reset();
			});
		};
	
    parser.instantiate([dom.byId('proveedorEgreso')]);
    var proveedorSelect = registry.byId('proveedorEgreso');
    proveedorSelect.onChange = resetBienServicio; 
    resetBienServicio(proveedorSelect.value);
    	
    var bienservicioSelect = new Select({
        name: "bienservicioEgreso",
        store: new Store(),
        labelAttr: "name",
        maxHeight: -1, // tells _HasDropDown to fit menu within viewport
        onChange: resetPorcion
	}, "bienservicioEgreso");
	bienservicioSelect.startup();
	
    var porcionSelect = new Select({
        name: "porcionEgreso",
        labelAttr: "name",
        maxHeight: -1, // tells _HasDropDown to fit menu within viewport
	}, "porcionEgreso");
	porcionSelect.startup();
  	
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
		var store = registry.byId('gridEgreso').store;
		return store.query();
	};
	
	actualizarEgresos = function(response, data){
		var grid = registry.byId('gridNodeEgreso');
		var key = response.egresoId;
		data['id'] = key;
		data['numero']=key;
		if (grid){
			var row = grid.store.get(key);
			if (row){
				grid.store.remove(key);
			}
			grid.store.add(data);
		}
	};
	
	toggle = function(e){
		e.value = !e.value;
	};
	
	parser.instantiate([dom.byId('guardarFacturaBtn')]);
	on(registry.byId('guardarFacturaBtn'),'click',
		function(e){
			var cliente = registry.byId('clienteFactura').value;
			var empleado = registry.byId('empleadoFactura').value;		
			var fecha = registry.byId('fechaFactura').toString();
			var numero = dom.byId('numeroFactura').innerHTML.replace('No.','');
			var remision = registry.byId('remisionFactura').value;
			var gridData = getGridData();
			var factura_data = {'cliente':cliente,'empleado':empleado,'fecha':fecha,'ventas':gridData, 'total':updateTotal(), 
			'numero':numero, 'remision':remision};
			request.post('/guardarFactura', {
					data : json.stringify(factura_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este pedido!';
						factura_data['cliente']=registry.byId('clienteFactura').attr('displayedValue');
						actualizarFacturas(response, factura_data, remision);
						var pagina = registry.byId('facturasPorPagina').checked;
						var url = '/mostrarFactura?facturaId='+response.facturaId + '&tipo=' + (remision ? 'Remision':'Factura')+ '&pagina='+ pagina.toString();
						window.open(url);
					}else{
						message = 'No se pudo guardar este pedido!';
					}
					dom.byId('mensajeFactura').innerHTML = message;
					setTimeout(function() {
						var grid =registry.byId('gridFactura');
						grid.model.clearCache();
						grid.model.store.setData([]);
        				grid.body.refresh();
						dom.byId('mensajeFactura').innerHTML = '';
						dom.byId('total').innerHTML = '';
						dom.byId('numeroFactura').innerHTML = '';
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
							'precio': parseInt(precio), 'venta':total});
			grid.total=updateTotal();
		});

		
	});
	
	parser.instantiate([dom.byId('nuevaFacturaBtn')]);
	on(registry.byId('nuevaFacturaBtn'),'click',function(e){
		registry.byId('addEntityForm' + entity_class).reset();
		registry.byId('remisionFactura').set('readOnly',false);
		var grid = registry.byId('gridFactura');
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		grid.total=updateTotal();
		dom.byId('numeroFactura').innerHTML='';
	});
	
	if (dom.byId('anularFacturaBtn')){
		parser.instantiate([dom.byId('anularFacturaBtn')]);
		on(registry.byId('anularFacturaBtn'),'click',function(e){
			var remision = registry.byId('remisionFactura').checked;
			var tipo = remision ? 'Remision' : 'Factura';
			var numero = dom.byId('numeroFactura').innerHTML;
			request('/anularFactura?tipo=' + tipo + '&id=' + numero).then(function(){
				registry.byId('anuladaFactura').set('value','ANULADA');
				domAttr.set('anuladaFactura', 'style', 'visibility:visible;color:red');
			});
		});		
	}
	parser.instantiate([dom.byId('anuladaFactura')]);
	var anuladaText= registry.byId('anuladaFactura');
	anuladaText.onChange = function(anulada){
		this.set('value',anulada ? 'ANULADA' : '');
		domAttr.set('anuladaFactura', 'style', 'width:100px;border:none;color:red');
		};

	
	var store = new Store();
	var columns = [
		{field : 'producto', name : 'Producto', style: "text-align: center"},
		{field : 'porcion', name : 'Porcion', style: "text-align: center"},
		{field : 'cantidad', name : 'Cantidad', style: "text-align: center"},
		{field : 'precio', name : 'Precio Unitario', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.precio,{pattern:'###,###'});
				}
		},
		{field : 'venta', name : 'Valor Total', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.venta,{pattern:'###,###'});
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
		modules : ["gridx/modules/CellWidget",'gridx/modules/SingleSort']
	}, 'gridFactura');
	grid.startup();
	domClass.add(dom.byId('gridFactura'),'factura-grid');
}); 
