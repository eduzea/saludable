//# sourceURL=../static/js/my/crearEgreso.js

require(['dojo/dom','dojo/dom-attr','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 
		'dijit/form/Button', "gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/json","dojo/number",'dijit/form/Select',
		'dojo/dom-class', 'dojo/ready', 'dojo/topic','gridx/modules/SingleSort'], 
function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number,Select,domClass, ready,topic) {
	var entity_class = saludable.entity_class;
	

	resetBienoservicio = function(tipo){	
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
					resetProveedor(bienoservicioSelect.value);
			});
		};	

	resetProveedor = function(bienoservicio){	
		request('/getProveedores?bienoservicio=' + bienoservicio, {handleAs:'json'}).then(
		function(response){
			var items = [];
			response.forEach(function(proveedor){
				items.push({ "value": proveedor.value, "label": proveedor.name });
			});
			var proveedorSelect = registry.byId('proveedorEgreso');
			proveedorSelect.options = items;
			proveedorSelect.reset();
		});
	};

	
	resetPorcion = function(bienoservicio){
			proveedor = registry.byId('proveedorEgreso').value;	
			request.post('/getPorcion', {
					data : {'proveedor':proveedor, 'bienoservicio': bienoservicio},
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
					var porcionSelect = registry.byId('porcionEgreso');
					porcionSelect.setStore(porcionStore);
					porcionSelect.reset();
			});
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
    proveedorSelect.onChange = ''; //write logic for when proveedor changes.

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
			formdata[prop.replace('Egreso', '')] = formdata[prop];
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
	
	parser.instantiate([dom.byId('guardarEgresoBtn')]);
	on(registry.byId('guardarEgresoBtn'),'click',
		function(e){
			var proveedor = registry.byId('proveedorEgreso').value;
			var empleado = registry.byId('empleadoEgreso').value;		
			var fecha = registry.byId('fechaEgreso').toString();
			var numero = dom.byId('numeroEgreso').innerHTML.replace('No.','');
			var gridData = getGridData();
			var egreso_data = {'proveedor':proveedor,'empleado':empleado,'fecha':fecha,'compras':gridData, 'total':updateTotal(), 
			'numero':numero};
			request.post('/guardarEgreso', {
					data : json.stringify(egreso_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este pedido!';
						egreso_data['proveedor']=registry.byId('proveedorEgreso').attr('displayedValue');
						actualizarEgresos(response, egreso_data);
					}else{
						message = 'No se pudo guardar este Egreso!';
					}
					dom.byId('mensajeEgreso').innerHTML = message;
					setTimeout(function() {
						var grid =registry.byId('gridEgreso');
						grid.model.clearCache();
						grid.model.store.setData([]);
        				grid.body.refresh();
						dom.byId('mensajeEgreso').innerHTML = '';
						dom.byId('total').innerHTML = '';
						dom.byId('numeroEgreso').innerHTML = '';
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
		var formdata = getFormData();
		request.post("getPrice",
		{
			data: {'bienoservicio':formdata['bienoservicio'], 'proveedor':formdata['proveedor'], 'porcion': formdata['porcion']}
		}).then(function(precio){
			if (precio == 'list index out of range'){
				alert("No hay precio definido para esta combinacion bien o servcio x proveedor! Definelo primero.");
				return;	
			}
			var grid = registry.byId('gridEgreso');
			var id = formdata['producto'] + formdata['porcion'];
			var row = grid.store.get(id);
			if (row){
				grid.store.remove(id);	
			}
			var total = formdata.cantidad * parseInt(precio);
			grid.store.add({'id':id,'bienoservicio':formdata.bienoservicio, 'proveedor':formdata.proveedor, 'porcion': formdata.porcion,'cantidad':formdata.cantidad, 
							'precio': parseInt(precio), 'compra':total});
			grid.total=updateTotal();
		});

		
	});
	
	parser.instantiate([dom.byId('nuevoEgresoBtn')]);
	on(registry.byId('nuevoEgresoBtn'),'click',function(e){
		registry.byId('addEntityForm' + entity_class).reset();
		var grid = registry.byId('gridEgreso');
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		grid.total=updateTotal();
		dom.byId('numeroEgreso').innerHTML='';
	});
	
	if (dom.byId('anularEgresoBtn')){
		parser.instantiate([dom.byId('anularEgresoBtn')]);
		on(registry.byId('anularEgresoBtn'),'click',function(e){
			var numero = dom.byId('numeroEgreso').innerHTML;
			request('/anularEgreso?id=' + numero).then(function(){
				registry.byId('anuladaEgreso').set('value','ANULADA');
				domAttr.set('anuladaEgreso', 'style', 'visibility:visible;color:red');
			});
		});		
	}
	parser.instantiate([dom.byId('anuladaEgreso')]);
	var anuladaText= registry.byId('anuladaEgreso');
	anuladaText.onChange = function(anulada){
		this.set('value',anulada ? 'ANULADA' : '');
		domAttr.set('anuladaEgreso', 'style', 'width:100px;border:none;color:red');
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
	}, 'gridEgreso');
	grid.startup();
	domClass.add(dom.byId('gridEgreso'),'egreso-grid');
}); 
