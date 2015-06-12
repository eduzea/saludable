//# sourceURL=../static/js/my/crearFactura.js

require(['dojo/dom','dojo/dom-attr','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 
		'dijit/form/Button', "gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/json","dojo/number",'dijit/form/Select',
		'dojo/dom-class', 'dojo/ready', 'dojo/topic','dojo/store/Memory','gridx/modules/SingleSort', 'dijit/form/CheckBox'], 
function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number,Select,domClass, ready,topic,Memory) {
	var entity_class = saludable.entity_class;	
	
	var resetCliente = function(cliente){	
		request.post('/getClientes', {handleAs:'json'}).then(function(response){
			var items = [];
			response.forEach(function(cliente){
				items.push({ "value": cliente.value, "label": cliente.name });
			});
			var clienteSelect = registry.byId('cliente'+entity_class);
			clienteSelect.options = items;
			clienteSelect.reset();
			console.log('RESET CLIENTE!');
		});
	};
	
	
	var resetProducto = function(cliente){	
			request.post('/getProducto', {
					data : {'cliente':cliente},
					handleAs:'json'
				}).then(function(response) {
					var items = [];
					response.forEach(function(producto){
						items.push({ "value": producto, "name": producto });
					});
					var productoStore = new Store({
			        	idProperty: "value",
			            data: items
			        });
					var productoSelect = registry.byId('producto'+entity_class);
					productoSelect.setStore(productoStore);
					productoSelect.reset();
					resetPorcion(productoSelect.value);
			});
		};	
	
	var resetPorcion = function(producto){
			if (producto == 'No hay precios definidos') return;
			cliente = registry.byId('cliente'+entity_class).value;	
			request.post('/getPorcion', {
					data : {'cliente':cliente, 'producto': producto},
					handleAs:'json'
				}).then(function(response) {
					var items = [];
					response.forEach(function(producto){
						items.push({ "value": producto, "name": producto });
					});
					var porcionStore = new Store({
			        	idProperty: "value",
			            data: items
			        });
					var porcionSelect = registry.byId('porcion'+entity_class);
					porcionSelect.setStore(porcionStore);
					porcionSelect.reset();
			});
		};
		
    parser.instantiate([dom.byId('cliente'+entity_class)]);
    var clienteSelect = registry.byId('cliente'+entity_class);
    clienteSelect.onChange = resetProducto; 
    clienteSelect.set('style','font-size:70%');
    resetProducto(clienteSelect.value);
    	
    var productoSelect = new Select({
        name: "producto"+entity_class,
        style: "width: 200px;font-size:70%",
        store: new Store(),
        labelAttr: "name",
        maxHeight: -1, // tells _HasDropDown to fit menu within viewport
        onChange: resetPorcion
	}, "producto"+entity_class);
	productoSelect.startup();
	
    var porcionSelect = new Select({
        name: "porcion"+entity_class,
        style: "font-size:70%",
        labelAttr: "name",
        maxHeight: -1, // tells _HasDropDown to fit menu within viewport
	}, "porcion"+entity_class);
	porcionSelect.startup();
	
	var selects = [registry.byId('cliente'+entity_class), registry.byId('producto'+entity_class), registry.byId('porcion'+entity_class)];
	selects.forEach(function(select){
		select.listenerfunc = function(data){
    		select.addOption({ disabled:false, label:data.label, selected:true, value:data.value});
    		var store = new Memory({data: select.options});
    		var sorted = store.query({},{sort: [{ attribute: "label"}]});
    		select.options = sorted;
    		select.set("value",sorted[0].value);
   		};
   		topic.subscribe(select.id.replace(entity_class,'').toUpperCase(), select.listenerfunc);
	});

  	
	var updateTotal = function(){
		var data = getGridData();
		var sumTotal=0;
		data.forEach(function(entry){
			sumTotal = sumTotal + entry.precio * entry.cantidad ;
		});
		var grid = registry.byId('grid'+entity_class);
		var conIva = registry.byId('iva'+entity_class).checked;
		var iva = conIva ? 0.16 : 0;
		grid.subtotal = sumTotal;
		grid.iva = sumTotal * iva;
		grid.total = sumTotal* (1 + iva);
		dom.byId('subtotal').innerHTML = number.format(grid.subtotal,{pattern:'###,###'});
		dom.byId('iva').innerHTML = number.format(grid.iva,{pattern:'###,###'});
		dom.byId('total').innerHTML = number.format(grid.total,{pattern:'###,###'});
	};
	
	parser.instantiate([dom.byId('iva'+entity_class)]);
    on(registry.byId('iva'+entity_class), 'change', updateTotal);
		
	var getFormData = function(entity_class){
		var formdata = registry.byId('addEntityForm' + entity_class).get('value');
		for (prop in formdata) {
			formdata[prop.replace(entity_class, '')] = formdata[prop];
			delete formdata[prop];
		}
		return formdata;
	};
	
	var getGridData = function(){
		var store = registry.byId('grid'+entity_class).store;
		return store.query();
	};
	
	var actualizarFacturas = function(response, data, entity_class){
		var id = 'gridNode'+entity_class;
		var grid = registry.byId(id);
		var key = response.facturaId;
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
	
	var toggle = function(e){
		e.value = !e.value;
	};
	
	parser.instantiate([dom.byId('guardar'+entity_class+'Btn')]);
	on(registry.byId('guardar'+entity_class+'Btn'),'click',
		function(e){
			var cliente = registry.byId('cliente'+entity_class).value;
			var empleado = registry.byId('empleado'+entity_class).value;		
			var fecha = registry.byId('fecha'+entity_class).toString();
			var numero = dom.byId('numero'+entity_class).innerHTML.replace('No.','');
			var gridData = getGridData();
			var grid = registry.byId('grid'+entity_class);
			updateTotal();
			var factura_data = {'cliente':cliente,'empleado':empleado,'fecha':fecha,'ventas':gridData, 'subtotal':grid.subtotal,'iva':grid.iva,'total':grid.total,  
			'numero':numero, 'entity_class':entity_class};
			request.post('/guardarFactura', {
					data : json.stringify(factura_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este pedido!';
						factura_data['cliente']=registry.byId('cliente'+entity_class).attr('displayedValue');
						actualizarFacturas(response, factura_data, entity_class);
						var pagina = registry.byId(entity_class+'PorPagina').checked;
						var url = '/mostrarFactura?facturaId='+response.facturaId + '&tipo=' + entity_class+ '&pagina='+ pagina.toString();
						window.open(url);
					}else{
						message = 'No se pudo guardar este pedido!';
					}
					dom.byId('mensaje'+entity_class).innerHTML = message;
					setTimeout(function() {
						var grid =registry.byId('grid'+entity_class);
						grid.model.clearCache();
						grid.model.store.setData([]);
        				grid.body.refresh();
						dom.byId('mensaje'+entity_class).innerHTML = '';
						dom.byId('total').innerHTML = '';
						dom.byId('subtotal').innerHTML = '';
						dom.byId('iva').innerHTML = '';
						dom.byId('numero'+entity_class).innerHTML = '';
					}, 3000);
				});
		});
	
	parser.instantiate([dom.byId('agregarPedidoBtn'+entity_class)]);
	on(registry.byId('agregarPedidoBtn'+entity_class),'click',function(e){
		var form = registry.byId('addEntityForm' + entity_class);
		if (!form.validate()){
			alert("'Cantidad' no puede estar vacio!");
			return;
		}
		var formdata = getFormData(entity_class);
		request.post("getPrice",
		{
			data: {'producto':formdata['producto'], 'cliente':formdata['cliente'], 'porcion': formdata['porcion']}
		}).then(function(precio){
			if (precio == 'list index out of range'){
				alert("No hay precio definido para esta combinacion producto x cliente! Definelo primero.");
				return;	
			}
			var grid = registry.byId('grid'+entity_class);
			var id = formdata['producto'] + formdata['porcion'];
			var row = grid.store.get(id);
			if (row){
				grid.store.remove(id);	
			}
			var total = formdata.cantidad * parseInt(precio);
			grid.store.add({'id':id,'producto':formdata.producto, 'cliente':formdata.cliente, 'porcion': formdata.porcion,'cantidad':formdata.cantidad, 
							'precio': parseInt(precio), 'venta':total});
			updateTotal(); 
		});

		
	});
	
	parser.instantiate([dom.byId('nueva'+entity_class+'Btn')]);
	on(registry.byId('nueva'+entity_class+'Btn'),'click',function(e){
		registry.byId('addEntityForm' + entity_class).reset();
		var grid = registry.byId('grid'+entity_class);
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		updateTotal();
		dom.byId('numero'+entity_class).innerHTML='';
	});
	
	if (dom.byId('anular'+entity_class+'Btn')){
		parser.instantiate([dom.byId('anular'+entity_class+'Btn')]);
		on(registry.byId('anular'+entity_class+'Btn'),'click',function(e){
			var numero = dom.byId('numero'+entity_class).innerHTML;
			request('/anularFactura?tipo=' + entity_class + '&id=' + numero).then(function(){
				registry.byId('anulada'+entity_class).set('value','ANULADA');
				domAttr.set('anulada'+entity_class, 'style', 'visibility:visible;color:red');
			});
		});		
	}
	parser.instantiate([dom.byId('anulada'+entity_class)]);
	var anuladaText= registry.byId('anulada'+entity_class);
	anuladaText.onChange = function(anulada){
		this.set('value',anulada ? 'ANULADA' : '');
		domAttr.set('anulada'+entity_class, 'style', 'width:100px;border:none;color:red');
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
	}, 'grid'+entity_class);
	grid.startup();
	grid.updateTotal = updateTotal;
	domClass.add(dom.byId('grid'+entity_class),'factura-grid');
}); 
