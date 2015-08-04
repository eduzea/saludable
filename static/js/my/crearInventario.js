//# sourceURL=../static/js/my/crearInventario.js
require(['dojo/dom',
		'dojo/dom-attr',
		'dijit/registry',
		'dojo/parser',
		'dojo/store/Memory',
		'gridx/Grid',
		'gridx/core/model/cache/Sync',
		'dojo/request', 
		'dijit/form/Button',
		"gridx/modules/CellWidget",
		'dojo/query',
		"dojo/on",
		"dojo/json",
		"dojo/number",
		'dijit/form/Select',
		'dojo/dom-class',
		'dojo/ready',
		'dojo/topic',
		'dojo/store/Memory',
		'gridx/modules/SingleSort',
		'dijit/form/CheckBox',
		'gridx/modules/Edit',
		'dijit/form/NumberTextBox'
		], 
	function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number,Select,domClass, ready,topic,Memory)
	{
		var entityClass = 'Inventario';
		
		var resetPorcion = function(producto){
			if (producto == 'No hay precios definidos') return;
			request.post('/getPorcion', {handleAs:'json'}).then(
				function(porciones) {
					var items = [];
					porciones.forEach(function(porcion){
						items.push({ "value": porcion, "name": porcion });
					});
					var porcionStore = new Store({
			        	idProperty: "value",
			            data: items
			        });
					porcionSelect.setStore(porcionStore);
					porcionSelect.reset();
			});
		};
		
		var productoSelect = new Select({
	        name: "producto"+ '_' + entityClass,
	        style: "width: 200px;font-size:70%",
	        store: new Store(),
	        labelAttr: "name",
	        maxHeight: -1, // tells _HasDropDown to fit menu within viewport
	        onChange: resetPorcion
		}, "producto"+ '_' + entityClass);
		productoSelect.startup();
		
	    var porcionSelect = new Select({
		        name: "porcion"+ '_' + entityClass,
		        style: "font-size:70%",
		        labelAttr: "name",
		        maxHeight: -1, // tells _HasDropDown to fit menu within viewport
		}, "porcion"+ '_' + entityClass);
		porcionSelect.startup();
		
		var selects = [productoSelect, porcionSelect];
		selects.forEach(function(select){
			select.listenerfunc = function(data){
	    		select.addOption({ disabled:false, label:data.label, selected:true, value:data.value});
	    		var store = new Memory({data: select.options});
	    		var sorted = store.query({},{sort: [{ attribute: "label"}]});
	    		select.options = sorted;
	    		select.set("value",sorted[0].value);
	   		};
	   		topic.subscribe(select.id.replace( '_' + entityClass,'').toUpperCase(), select.listenerfunc);
		});
		
		request.get('/entityData?entityClass=Producto', {handleAs:'json'}).then(function(response){
			var items = [];
			response.records.forEach(function(producto){
				items.push({ "value": producto.id, "name": producto.nombre });
			});
			var productoStore = new Store({
	        	idProperty: "value",
	            data: items
	        });
			productoSelect.setStore(productoStore);
			productoSelect.reset();
		});
		
		var getFormData = function(entityClass){
			var formdata = registry.byId('addEntityForm' + '_' + entityClass).get('value');
			for (prop in formdata) {
				formdata[prop.replace('_' + entityClass, '')] = formdata[prop];
				delete formdata[prop];
			}
			return formdata;
		};
	
		var getGridData = function(){
			var store = registry.byId('grid'+ '_' + entityClass).store;
			return store.query();
		};
		
		parser.instantiate([dom.byId('agregarBtn'+ '_' + entityClass)]);
		on(registry.byId('agregarBtn'+ '_' + entityClass),'click',function(e){
			var form = registry.byId('addEntityForm' +  '_' + entityClass);
			if (!form.validate()){
				alert("'Cantidad' no puede estar vacio!");
				return;
			}
			var formdata = getFormData(entityClass);
			var grid = registry.byId('grid'+ '_' + entityClass);
			var id = formdata['producto'] + formdata['porcion'];
			var row = grid.store.get(id);
			if (row){
				grid.store.remove(id);	
			}
			grid.store.add({'id':id,'producto':formdata.producto,'porcion': formdata.porcion,'existencias':formdata.existencias});
		});
		
		parser.instantiate([dom.byId('nueva'+ '_' + entityClass+'Btn')]);
		on(registry.byId('nueva'+ '_' + entityClass+'Btn'),'click',function(e){
			registry.byId('addEntityForm' +  '_' + entityClass).reset();
			var grid = registry.byId('grid'+ '_' + entityClass);
			grid.model.clearCache();
			grid.model.store.setData([]);
			grid.body.refresh();		
		});	

		var store = new Store();
		var columns = [
			{field : 'producto', name : 'Producto', style: "text-align: center"},
			{field : 'porcion', name : 'Porcion', style: "text-align: center"},
			{field : 'existencias', name : 'Existencias', style: "text-align: center"},
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
			modules : [	"gridx/modules/CellWidget",
						'gridx/modules/SingleSort',
						'gridx/modules/Edit'
						]
		}, 'grid'+ '_' + entityClass);
		grid.startup();
		domClass.add(dom.byId('grid'+ '_' + entityClass),'factura-grid');
				
		parser.instantiate([dom.byId('guardar'+ '_' + entityClass + 'Btn')]);
		on(registry.byId('guardar'+ '_' + entityClass +'Btn'),'click',
		function(e){
			var fecha = registry.byId('fecha'+ '_' + entityClass).toString();
			var ciudad = registry.byId('ciudad'+ '_' + entityClass).value;
			var gridData = getGridData();
			var grid = registry.byId('grid'+ '_' + entityClass);
			var inventario_data = {'fecha':fecha,'ciudad':ciudad,'registros':gridData, 'entityClass':entityClass};
			request.post('/guardarInventario', {
					data : json.stringify(inventario_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este inventario!';
						actualizarInventarios(response, inventario_data, entityClass);
					}else{
						message = 'No se pudo guardar este inventario!';
					}
					dom.byId('mensaje'+ '_' + entityClass).innerHTML = message;
					setTimeout(function() {
						var grid =registry.byId('grid'+ '_' + entityClass);
						grid.model.clearCache();
						grid.model.store.setData([]);
        				grid.body.refresh();
						dom.byId('mensaje'+ '_' + entityClass).innerHTML = '';
					}, 2000);
					
					topic.publish('INVENTARIO', {'action':'ADD'});
				});
		});
		
		var actualizarInventarios = function(response, data, entity_class){
			var id = 'gridNode'+ '_' + entityClass;
			var grid = registry.byId(id);
			var key = response.inventarioId;
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
	}
);