//# sourceURL=../static/js/my/crearEgreso.js

require(['dojo/dom','dojo/dom-attr','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 
		'dijit/form/Button', "gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/json","dojo/number",'dijit/form/Select',
		'dojo/dom-class', 'dojo/ready', 'dojo/topic','dojo/store/Memory','gridx/modules/SingleSort','dojo/domReady!'], 
function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, CellWidget, 
	query, on,json,number,Select,domClass, ready,topic, Memory) {
	var entity_class = saludable.entity_class;
	

	var resetBienoservicio = function(tipo){	
			request('/getBienesoServicios?tipo=' + tipo, 
					{handleAs:'json'}).then(
				function(response) {
					var items = [];
					response.forEach(function(bienoservicio){
						items.push({ "value": bienoservicio.value, "label": bienoservicio.name });
					});
					var bienoservicioSelect = registry.byId('bienoservicio_Egreso');
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
			var proveedorSelect = registry.byId('proveedor_Egreso');
			proveedorSelect.options = [];
			proveedorSelect.addOption(items);
			proveedorSelect.reset();
		});
	};
	
	var resetGrid = function (){
		var grid = registry.byId('grid_Egreso');
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		grid.total=updateTotal();		
	};
	
	var resetEgreso = function(){
		dom.byId('mensaje_Egreso').innerHTML = '';
		dom.byId('total').innerHTML = '';
		dom.byId('numero_Egreso').innerHTML = '';
		registry.byId('detalle_Egreso').set('value','');
		registry.byId('cantidad_Egreso').set('value','');
		registry.byId('precio_Egreso').set('value','');
		resetGrid();
	};

	parser.instantiate([dom.byId('tipo_Egreso')]);
    var tipoSelect = registry.byId('tipo_Egreso');
	tipoSelect.onChange = resetBienoservicio; 
    resetBienoservicio(tipoSelect.value);

	parser.instantiate([dom.byId('bienoservicio_Egreso')]);
    var bienoservicioSelect = registry.byId('bienoservicio_Egreso');    
	bienoservicioSelect.onChange = resetProveedor; 
    resetProveedor(bienoservicioSelect.value);
    
    parser.instantiate([dom.byId('proveedor_Egreso')]);
    var proveedorSelect = registry.byId('proveedor_Egreso');    
	proveedorSelect.onChange = resetEgreso;
	
	var selects = [tipoSelect, bienoservicioSelect, proveedorSelect];
	selects.forEach(function(select){
		select.listenerfunc = function(data){
    		select.addOption({ disabled:false, label:data.label, selected:true, value:data.value});
    		var store = new Memory({data: select.options});
    		var sorted = store.query({},{sort: [{ attribute: "label"}]});
    		select.options = sorted;
    		select.set("value",sorted[0].value);
   		};
   		topic.subscribe(select.id.replace('_' + entity_class,'').toUpperCase(), select.listenerfunc);
	});
  	
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
		var formdata = registry.byId('addEntityForm' +  '_' + entity_class).get('value');
		for (prop in formdata) {
			formdata[prop.replace('_Egreso', '')] = formdata[prop];
			delete formdata[prop];
		}
		return formdata;
	};
	
	var getGridData = function(){
		var store = registry.byId('grid_Egreso').store;
		return store.query();
	};
	
	var actualizarEgresos = function(response, data){
		var grid = registry.byId('gridNode_Egreso');
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
	
	parser.instantiate([dom.byId('guardar_EgresoBtn')]);
	on(registry.byId('guardar_EgresoBtn'),'click',
		function(e){
			var tipo = registry.byId('tipo_Egreso').value;
			var proveedor = registry.byId('proveedor_Egreso').value;
			var empleado = registry.byId('empleado_Egreso').value;		
			var fecha = registry.byId('fecha_Egreso').toString();
			var numero = dom.byId('numero_Egreso').innerHTML.replace('No.','');
			var gridData = getGridData();
			var comentario = registry.byId('comentario_Egreso').value;
			var sucursal = registry.byId('sucursal_Egreso').value;
			var egreso_data = {'proveedor':proveedor,'empleado':empleado,'fecha':fecha,'sucursal':sucursal,'compras':gridData, 'total':updateTotal(), 
			'numero':numero, 'tipo':tipo, 'comentario': comentario};
			request.post('/guardarEgreso', {
					data : json.stringify(egreso_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este pedido!';
						egreso_data['proveedor']=registry.byId('proveedor_Egreso').attr('displayedValue');
						egreso_data['resumen']= gridData[0].bienoservicio;
						actualizarEgresos(response, egreso_data);
					}else{
						message = 'No se pudo guardar este Egreso!';
					}
					dom.byId('mensaje_Egreso').innerHTML = message;
					setTimeout(function() {
						resetEgreso();
					}, 3000);
				});
		});
	
	parser.instantiate([dom.byId('agregarCompraBtn')]);
	on(registry.byId('agregarCompraBtn'),'click',function(e){
		var form = registry.byId('addEntityForm' +  '_' + entity_class);
		if (!form.validate()){
			alert("'Cantidad' no puede estar vacio!");
			return;
		}
		var formdata = getEgresoFormData(entity_class);
		var grid = registry.byId('grid_Egreso');
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
	
	
	parser.instantiate([dom.byId('nuevo_EgresoBtn')]);
	on(registry.byId('nuevo_EgresoBtn'),'click',function(e){
		registry.byId('addEntityForm' +  '_' + entity_class).reset();
		resetGrid();
		dom.byId('numero_Egreso').innerHTML='';
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
	}, 'grid_Egreso');
	grid.startup();
	grid.updateTotal = updateTotal;
	domClass.add(dom.byId('grid_Egreso'),'egreso-grid');
}); 
