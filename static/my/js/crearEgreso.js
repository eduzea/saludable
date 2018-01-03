//# sourceURL=../static/js/my/crearEgreso.js

require(['dojo/dom',
		'dojo/dom-attr',
		'dijit/registry',
		'dojo/parser',
		'dojo/store/Memory',
		'dojo/request',
		'dijit/form/Select',
		"dijit/form/FilteringSelect",
		"dojo/store/Memory",
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
function(dom, domAttr, registry, parser, Store, request, Select, FilteringSelect, Memory, Button, Checkbox,  
	query, on,json,number,domClass, html, ready,topic,Grid,Cache,CellWidget) {
	var entityClass = 'Egreso';

	var resetBienoservicio = function(proveedor){	
			request('/getBienesoServicios?proveedor=' + proveedor, 
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

//	var resetProveedor = function(bienoservicio){	
//		request('/getProveedores?bienoservicio=' + bienoservicio, {handleAs:'json'}).then(
//		function(response){
//			var items = [];
//			if (response.length == 0){
//				items.push({ "value": 'NO.REPORTADO', "label": 'NO REPORTADO' });
//			}else{
//				response.forEach(function(proveedor){
//					items.push({ "value": proveedor.value, "label": proveedor.name });
//				});			
//			}
//			var proveedorSelect = registry.byId('proveedor_Egreso');
//			proveedorSelect.options = [];
//			proveedorSelect.addOption(items);
//			proveedorSelect.reset();
//		});
//	};
	
	var resetGrid = function (){
		var grid = registry.byId('grid_Egreso');
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		grid.total=updateTotal();		
	};
	
	var resetEgreso = function(){
		dom.byId('egreso_total').innerHTML = '';
		dom.byId('numero_Egreso').innerHTML = '';
		registry.byId('detalle_Egreso').set('value','');
		registry.byId('cantidad_Egreso').set('value','');
		registry.byId('precio_Egreso').set('value','');
		resetGrid();
	};

//	parser.instantiate([dom.byId('tipo_Egreso')]);
//    var tipoSelect = registry.byId('tipo_Egreso'); 
//    resetBienoservicio(tipoSelect.value);
//    tipoSelect.onChange = resetBienoservicio;

	parser.instantiate([dom.byId('bienoservicio_Egreso')]);
    var bienoservicioSelect = registry.byId('bienoservicio_Egreso');    
//    resetProveedor(bienoservicioSelect.value);
//	bienoservicioSelect.onChange = resetProveedor; 

    parser.instantiate([dom.byId('proveedor_Egreso')]);
    var proveedorSelect = registry.byId('proveedor_Egreso');    
    resetBienoservicio(proveedorSelect.value);
    proveedorSelect.onChange = resetBienoservicio;
	
	var selects = [/*tipoSelect*/, bienoservicioSelect, proveedorSelect];
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
		dom.byId('egreso_total').innerHTML = number.format(sumTotal,{pattern:'###,###.#'});
		return sumTotal;
	};
	
	var getEgresoFormData = function(entityClass){
		var formdata = registry.byId('addEntityForm' +  '_' + entityClass).get('value');
		for (var prop in formdata) {
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
			var proveedor = registry.byId('proveedor_Egreso').value;		
			var fecha = registry.byId('fecha_Egreso').toString();
			var numero = dom.byId('numero_Egreso').innerHTML.replace('No.','');
			var gridData = getGridData();
			var comentario = registry.byId('comentario_Egreso').value;
			var sucursal = registry.byId('sucursal_Egreso').value;
			var egreso_data = {'proveedor':proveedor,'fecha':fecha,'sucursal':sucursal,'compras':gridData, 'total':updateTotal(), 
			'numero':numero, 'comentario': comentario};
			request.post('/guardarEgreso', {
					data : json.stringify(egreso_data),
					handleAs:'json'
				}).then(function(response) {
					var server_msg = registry.byId('server_message');
					if(response.result == 'SUCCESS'){
						msg = (response.message == 'Updated') ? 'Se ACTUALIZO exitosamente este Egreso! # ' : 'Se CREO exitosamente este Egreso! # '
						server_msg.set("content", msg + response.id);
						server_msg.show();
						egreso_data['proveedor']=registry.byId('proveedor_Egreso').attr('displayedValue');
						egreso_data['resumen']= gridData[0].bienoservicio;
						actualizarEgresos(response, egreso_data);
						setTimeout(function() {
							resetEgreso();
						}, 2000);
					}else{
						server_msg.set("content", response['message']);
						server_msg.show();
					}
				});
		});
	
	parser.instantiate([dom.byId('agregarCompraBtn')]);
	on(registry.byId('agregarCompraBtn'),'click',function(e){
		var form = registry.byId('addEntityForm' +  '_' + entityClass);
		if (!form.validate()){
			alert("'Cantidad' no puede estar vacio!");
			return;
		}
		var formdata = getEgresoFormData(entityClass);
		var grid = registry.byId('grid_Egreso');
		var id = formdata['bienoservicio'] + formdata['detalle'].replace(/ /g,'');
		var row = grid.store.get(id);
		if (row){
			grid.store.remove(id);	
		}
		var total = formdata.cantidad * formdata.precio;
		grid.store.add({'id':id,'bienoservicio':formdata.bienoservicio, 'proveedor':formdata.proveedor, 'detalle': formdata.detalle,'cantidad':formdata.cantidad, 
						'precio': formdata.precio, 'total':total});
		grid.total=updateTotal();

		
	});
	
	
	parser.instantiate([dom.byId('nuevo_EgresoBtn')]);
	on(registry.byId('nuevo_EgresoBtn'),'click',function(e){
		registry.byId('addEntityForm' +  '_' + entityClass).reset();
		resetGrid();
		dom.byId('numero_Egreso').innerHTML='';
	});
	
	
	var store = new Store();
	var columns = [
		{field : 'bienoservicio', name : 'Bien o Servicio', style: "text-align: center"},
		{field : 'detalle', name : 'Detalle', style: "text-align: center"},
		{field : 'cantidad', name : 'Cantidad', style: "text-align: center",
		formatter: function(data){
					return number.format(data.cantidad,{pattern:'###,###.#'});
				}
		},
		{field : 'precio', name : 'Precio Unitario', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.precio,{pattern:'###,###'});
				}
		},
		{field : 'total', name : 'Valor Total', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.total,{pattern:'###,###.#'});
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
	
	//This is a temporary solution. This code is repeated in addEntity.js and should be made reusable.
	// One approach is to create thsi view through addEntity.js and no as a custom view.
	// The other is to compenentize the logic of fillForm and include it in the custom crearFactura.js
	
	parser.instantiate([dom.byId('addEntityForm'+ '_' + entityClass)]);
	var form = registry.byId('addEntityForm'+ '_' + entityClass);
	form.listenerfunc = function(data){
        var nodelist= query('[id*='+ entityClass +']', 'addEntityForm'+ '_' + entityClass);
        if (nodelist.length == 0){
        	var contentPane= registry.byId(grid.gridName + '_add');
			contentPane.set("onDownloadEnd", function(){
				nodelist= query('[id*='+ entityClass +']', 'addEntityForm'+ '_' + entityClass );
				parser.instantiate(nodelist);
				fillForm(nodelist, data, entityClass);	
			});
        }else{
    		fillForm(nodelist, data, entityClass);
        }
	};
	topic.subscribe('EDIT_'+ entityClass.toUpperCase(), form.listenerfunc);
	
	var fillForm = function(nodelist, rowData, entityClass){
		nodelist.forEach(function(node, index, array){
			var dijit = registry.byId(node.id);
			if (dijit){
				if (dijit.id.indexOf("grid") > -1 ){
					request('/getDetails?key=' + rowData['id'] + '&entityClass=' + entityClass, {handleAs:'json'}).then(function(response)
					 {
						dijit.model.clearCache();
						dijit.model.store.setData([]);//dijit.model.store.setData(items) //should work but its not calling onCellWidgetCreated!
						response.forEach(function(item){
							dijit.store.add(item);								
						});
						dijit.body.refresh();
						if (dijit.updateTotal){
							dijit.total = dijit.updateTotal();	
						}
						if (dom.byId('numero_' + entityClass)){
							dom.byId('numero_' + entityClass).innerHTML = rowData.numero;							
						}
						if (entityClass in saludable.gridChangeFuncs)
							saludable.gridChangeFuncs[entityClass](dijit);
					});
				}else{
					var id = dijit.id;
		        	if (id.indexOf(entityClass + "_Btn_list") > -1){//For key fields that are lists
		        		var field = id.replace('_' + entityClass + '_Btn_list','');
		        		//Find the button, fill the items list
		        		var button = registry.byId(field + '_' + entityClass + '_Btn_list');
		        		button.items = rowData['text' + field].split(';').filter(function(element) { return element; });
		        		//Find the list, populate it
		        		var listName = field + '_' + entityClass + '_list';
		        		$('#'+listName).empty();
		        		button.items.forEach(function(item){
		        			$('<div><input name="toDoList" type="checkbox">' + item + '</input></div>').appendTo('#'+listName);		        			
		        		});
	
		        	}
		        	id= dijit.id.replace('_' + entityClass,''); 
		        	if(id in rowData){
		        		if (rowData[id] instanceof Array){//If a list, take first only...
		        			rowData[id]=rowData[id][0];
		        		}
		        		if (dijit instanceof Checkbox){
		        			dijit.set('checked', rowData[id]);
		        		}else{
			        		dijit.set('value', getValueFromLabel(dijit,rowData[id]),false);
			        		dijit.set("displayedValue", rowData[id],false);		        			
		        		}
		        	}
		        		   				
				}			
			}
    	});
    };
  
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
