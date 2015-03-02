//# sourceURL=../static/js/my/crearEgreso.js

require(['dojo/dom','dojo/dom-attr','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 
		'dijit/form/Button', "gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/json","dojo/number",'dijit/form/Select',
		'dojo/dom-class', 'dojo/ready', 'dojo/topic','gridx/modules/SingleSort','dojo/domReady!'], 
function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number,Select,domClass, ready,topic) {
	var entity_class = saludable.entity_class;
	

	var resetBienoservicio = function(tipo){	
			request('/getBienesoServicios?tipo=' + tipo, 
					{handleAs:'json'}).then(
				function(response) {
					var items = [];
					response.forEach(function(bienoservicio){
						items.push({ "value": bienoservicio.value, "label": bienoservicio.name });
					});
					var bienoservicioSelect = registry.byId('bienoservicioEgreso');
					bienoservicioSelect.options = [];
					bienoservicioSelect.addOption(items);
					bienoservicioSelect.reset();
			});
		};	

	var resetProveedor = function(bienoservicio){	
		request('/getProveedores?bienoservicio=' + bienoservicio, {handleAs:'json'}).then(
		function(response){
			var items = [];
			if (response.length == 0){
				items.push({ "value": 'No.reportado', "label": 'No reportado' });
			}else{
				response.forEach(function(proveedor){
					items.push({ "value": proveedor.value, "label": proveedor.name });
				});			
			}
			var proveedorSelect = registry.byId('proveedorEgreso');
			proveedorSelect.options = [];
			proveedorSelect.addOption(items);
			proveedorSelect.reset();
		});
	};
	
	var resetGrid = function (){
		var grid = registry.byId('gridEgreso');
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		grid.total=updateTotal();		
	};
	
	var resetEgreso = function(){
		dom.byId('mensajeEgreso').innerHTML = '';
		dom.byId('total').innerHTML = '';
		dom.byId('numeroEgreso').innerHTML = '';
		registry.byId('detalleEgreso').set('value','');
		registry.byId('cantidadEgreso').set('value','');
		registry.byId('precioEgreso').set('value','');
		resetGrid();
	};

	parser.instantiate([dom.byId('tipoEgreso')]);
    var tipoSelect = registry.byId('tipoEgreso');
	tipoSelect.onChange = resetBienoservicio; 
    resetBienoservicio(tipoSelect.value);

	parser.instantiate([dom.byId('bienoservicioEgreso')]);
    var bienoservicioSelect = registry.byId('bienoservicioEgreso');    
	bienoservicioSelect.onChange = resetProveedor; 
    resetProveedor(bienoservicioSelect.value);
    
    parser.instantiate([dom.byId('proveedorEgreso')]);
    var proveedorSelect = registry.byId('proveedorEgreso');    
	proveedorSelect.onChange = resetEgreso; 
  	
	var updateTotal = function(){
		var data = getGridData();
		var sumTotal=0;
		data.forEach(function(entry){
			sumTotal = sumTotal + entry.precio * entry.cantidad ;
		});
		dom.byId('total').innerHTML = number.format(sumTotal,{pattern:'###,###'});
		return sumTotal;
	};
	
	var getEgresoFormData = function(entity_class){
		var formdata = registry.byId('addEntityForm' + entity_class).get('value');
		for (prop in formdata) {
			formdata[prop.replace('Egreso', '')] = formdata[prop];
			delete formdata[prop];
		}
		return formdata;
	};
	
	var getGridData = function(){
		var store = registry.byId('gridEgreso').store;
		return store.query();
	};
	
	var actualizarEgresos = function(response, data){
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
	
	var toggle = function(e){
		e.value = !e.value;
	};
	
	parser.instantiate([dom.byId('guardarEgresoBtn')]);
	on(registry.byId('guardarEgresoBtn'),'click',
		function(e){
			var tipo = registry.byId('tipoEgreso').value;
			var proveedor = registry.byId('proveedorEgreso').value;
			var empleado = registry.byId('empleadoEgreso').value;		
			var fecha = registry.byId('fechaEgreso').toString();
			var numero = dom.byId('numeroEgreso').innerHTML.replace('No.','');
			var gridData = getGridData();
			var comentario = registry.byId('comentarioEgreso').value;
			var sucursal = registry.byId('sucursalEgreso').value;
			var egreso_data = {'proveedor':proveedor,'empleado':empleado,'fecha':fecha,'sucursal':sucursal,'compras':gridData, 'total':updateTotal(), 
			'numero':numero, 'tipo':tipo, 'comentario': comentario};
			request.post('/guardarEgreso', {
					data : json.stringify(egreso_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este pedido!';
						egreso_data['proveedor']=registry.byId('proveedorEgreso').attr('displayedValue');
						egreso_data['resumen']= gridData[0].bienoservicio;
						actualizarEgresos(response, egreso_data);
					}else{
						message = 'No se pudo guardar este Egreso!';
					}
					dom.byId('mensajeEgreso').innerHTML = message;
					setTimeout(function() {
						resetEgreso();
					}, 3000);
				});
		});
	
	parser.instantiate([dom.byId('agregarCompraBtn')]);
	on(registry.byId('agregarCompraBtn'),'click',function(e){
		var form = registry.byId('addEntityForm' + entity_class);
		if (!form.validate()){
			alert("'Cantidad' no puede estar vacio!");
			return;
		}
		var formdata = getEgresoFormData(entity_class);
		var grid = registry.byId('gridEgreso');
		var id = formdata['bienoservicio'] + formdata['detalle'].replace(/ /g,'');
		var row = grid.store.get(id);
		if (row){
			grid.store.remove(id);	
		}
		var total = formdata.cantidad * formdata.precio;
		grid.store.add({'id':id,'bienoservicio':formdata.bienoservicio, 'proveedor':formdata.proveedor, 'detalle': formdata.detalle,'cantidad':formdata.cantidad, 
						'precio': formdata.precio, 'compra':total});
		grid.total=updateTotal();

		
	});
	
	
	parser.instantiate([dom.byId('nuevoEgresoBtn')]);
	on(registry.byId('nuevoEgresoBtn'),'click',function(e){
		registry.byId('addEntityForm' + entity_class).reset();
		resetGrid();
		dom.byId('numeroEgreso').innerHTML='';
	});
	
	
	var store = new Store();
	var columns = [
		{field : 'bienoservicio', name : 'Bien o Servicio', style: "text-align: center"},
		{field : 'detalle', name : 'Detalle', style: "text-align: center"},
		{field : 'cantidad', name : 'Cantidad', style: "text-align: center"},
		{field : 'precio', name : 'Precio Unitario', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.precio,{pattern:'###,###'});
				}
		},
		{field : 'compra', name : 'Valor Total', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.compra,{pattern:'###,###'});
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
	}, 'gridEgreso');
	grid.startup();
	grid.updateTotal = updateTotal;
	domClass.add(dom.byId('gridEgreso'),'egreso-grid');
}); 
