//# sourceURL=../static/js/my/crearEgresoFruta.js

require(['dojo/dom',
		'dojo/dom-attr',
		'dijit/registry',
		'dojo/parser',
		'dojo/store/Memory',
		'dojo/request',
		'dijit/form/Select',
		'dijit/form/Button',
		'dijit/form/CheckBox',
		'dojo/query',
		"dojo/on",
		"dojo/json",
		"dojo/number",
		'dojo/dom-class',
		'dojox/html/entities',
		'dojo/ready',
		'dojo/topic',
		'gridx/Grid',
		'gridx/core/model/cache/Sync',
		"gridx/modules/CellWidget",		
		'gridx/modules/SingleSort',
		'dojo/domReady!'], 
function(dom, domAttr, registry, parser, Store, request, Select, Button, Checkbox,  
	query, on,json,number,domClass, html, ready,topic,Grid,Cache,CellWidget) {
	var entityClass = saludable.entity_class;
	
	var resetProveedor = function(){	
		request('/getProveedores?bienoservicio=Materia.Prima-Fruta', {handleAs:'json'}).then(
		function(response){
			var items = [];
			if (response.length == 0){
				items.push({ "value": 'No.reportado', "label": 'No reportado' });
			}else{
				response.forEach(function(proveedor){
					items.push({ "value": proveedor.value, "label": proveedor.name });
				});			
			}
			var proveedorSelect = registry.byId('proveedor_Egreso_fruta');
			proveedorSelect.options = [];
			proveedorSelect.addOption(items);
			proveedorSelect.reset();
		});
	};
	
	var resetGrid = function (){
		var grid = registry.byId('grid_Egreso_fruta');
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		grid.total=updateTotal();		
	};
	
	var resetEgreso = function(){
		dom.byId('mensaje_Egreso_fruta').innerHTML = '';
		dom.byId('total').innerHTML = '';
		dom.byId('numero_Egreso_fruta').innerHTML = '';
		registry.byId('fruta_Egreso_fruta').set('value','');
		registry.byId('cantidad_Egreso_fruta').set('value','');
		registry.byId('precio_Egreso_fruta').set('value','');
		resetGrid();
	};

    parser.instantiate([dom.byId('proveedor_Egreso_fruta')]);
    var proveedorSelect = registry.byId('proveedor_Egreso_fruta');    
	resetProveedor();
	
	var selects = [proveedorSelect];
	selects.forEach(function(select){
		select.listenerfunc = function(data){
    		select.addOption({ disabled:false, label:data.label, selected:true, value:data.value});
    		var store = new Memory({data: select.options});
    		var sorted = store.query({},{sort: [{ attribute: "label"}]});
    		select.options = sorted;
    		select.set("value",sorted[0].value);
   		};
   		topic.subscribe(select.id.replace('_' + entityClass,'').toUpperCase(), select.listenerfunc);
	});
  	
	var updateTotal = function(){
		var data = getGridData();
		var sumTotal=0;
		data.forEach(function(entry){
			sumTotal = sumTotal + entry.precio * entry.cantidad ;
		});
		dom.byId('total').innerHTML = number.format(sumTotal,{pattern:'###,###.#'});
		return sumTotal;
	};
	
	var getEgresoFormData = function(entityClass){
		var formdata = registry.byId('addEntityForm' +  '_' + entityClass + '_fruta').get('value');
		for (var prop in formdata) {
			formdata[prop.replace('_Egreso_fruta', '')] = formdata[prop];
			delete formdata[prop];
		}
		return formdata;
	};
	
	var getGridData = function(){
		var store = registry.byId('grid_Egreso_fruta').store;
		return store.query();
	};
	
	var actualizarEgresos = function(response, data){
		var grid = registry.byId('gridNode_Egreso_fruta');
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
	
	parser.instantiate([dom.byId('guardar_EgresoBtn_fruta')]);
	on(registry.byId('guardar_EgresoBtn_fruta'),'click',
		function(e){
			var tipo = 'Costo.Variable';
			var proveedor = registry.byId('proveedor_Egreso_fruta').value;		
			var fecha = registry.byId('fecha_Egreso_fruta').toString();
			var fuente = registry.byId('fuente_Egreso_fruta').value;
			var numero = dom.byId('numero_Egreso_fruta').innerHTML.replace('No.','');
			var gridData = getGridData();
			var comentario = registry.byId('comentario_Egreso_fruta').value;
			var sucursal = registry.byId('sucursal_Egreso_fruta').value;
			var egreso_data = {'proveedor':proveedor,'fecha':fecha,'sucursal':sucursal,'fuente':fuente,'compras':gridData, 'total':updateTotal(), 
			'numero':numero, 'tipo':tipo, 'comentario': comentario};
			request.post('/guardarEgreso', {
					data : json.stringify(egreso_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este pedido!: ' + response.egresoId;
						egreso_data['proveedor']=registry.byId('proveedor_Egreso_fruta').attr('displayedValue');
						egreso_data['resumen']= gridData[0].bienoservicio;
						actualizarEgresos(response, egreso_data);
						request('/guardarLoteDeCompra?egresoId='+response.egresoId).then(
							function(response) {
								console.log(response);
							}
						);
					}else{
						message = 'No se pudo guardar este Egreso!';
					}
					dom.byId('mensaje_Egreso_fruta').innerHTML = message;
					setTimeout(function() {
						resetEgreso();
					}, 3000);
				});
		});
	
	parser.instantiate([dom.byId('agregarCompraBtn_fruta')]);
	on(registry.byId('agregarCompraBtn_fruta'),'click',function(e){
		var form = registry.byId('addEntityForm' +  '_' + entityClass + '_fruta');
		if (!form.validate()){
			alert("'Cantidad' no puede estar vacio!");
			return;
		}
		var formdata = getEgresoFormData(entityClass);
		var grid = registry.byId('grid_Egreso_fruta');
		var id = formdata['fruta'];
		var row = grid.store.get(id);
		if (row){
			grid.store.remove(id);	
		}
		var total = formdata.cantidad * formdata.precio;
		grid.store.add({'id':id,'bienoservicio':'Materia.Prima-Fruta','detalle':formdata.fruta, 'cantidad':formdata.cantidad, 
						'precio': formdata.precio, 'compra':total});
		grid.total=updateTotal();

		
	});
	
	
	var store = new Store();
	var columns = [
		{field : 'detalle', name : 'Fruta', style: "text-align: center"},
		{field : 'cantidad', name : 'Cantidad(kg)', style: "text-align: center",
				formatter: function(data){
					return number.format(data.cantidad,{pattern:'###,###.#'});
				}},
		{field : 'precio', name : 'Precio($/kg)', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.precio,{pattern:'###,###'});
				}
		},
		{field : 'compra', name : 'Valor Total', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.compra,{pattern:'###,###.#'});
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
	}, 'grid_Egreso_fruta');
	grid.startup();
	grid.updateTotal = updateTotal;
	domClass.add(dom.byId('grid_Egreso_fruta'),'egreso-grid');
	
	//This is a temporary solution. This code is repeated in addEntity.js and should be made reusable.
	// One approach is to create thsi view through addEntity.js and no as a custom view.
	// The other is to compenentize the logic of fillForm and include it in the custom crearFactura.js
	
  
	var getValueFromLabel = function(dijit, label){
		if (!dijit.options){
			return label;
		} 
		var options = dijit.getOptions();
		var lookup = {};
		for (var i = 0, len = options.length; i < len; i++) {
			lookup[html.decode(options[i].label)] = options[i].value;
		}
		if (label in lookup){
			return lookup[label];	
		}else{
			dijit.addOption({label:label.replace('.',' '),selected:true, value:label.replace(' ','.')});
		}
	return label;
	};
	
	
	
	registry.byId('standby_centerPane').hide();
}); 
