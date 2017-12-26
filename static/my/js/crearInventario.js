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
		'dijit/form/CheckBox',
		"gridx/modules/CellWidget",
		'dojo/query',
		"dojo/on",
		"dojo/json",
		"dojo/number",
		'dijit/form/Select',
		'dojo/dom-class',
		'dojox/html/entities',
		'dojo/ready',
		'dojo/topic',
		'dojo/store/Memory',
		'gridx/modules/SingleSort',
		'dijit/form/CheckBox',
		'gridx/modules/Edit',
		'dijit/form/NumberTextBox'
		], 
	function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, Checkbox, CellWidget, query, on,json,number,Select,domClass, html, ready,topic,Memory)
	{
		var entityClass = 'Inventario';
		
		var resetPorcion = function(producto){
			if (producto == 'No hay precios definidos') return;
			request.post('/getPorcion', {data : {'producto': producto}, handleAs:'json'}).then(
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
			var sucursal = registry.byId('sucursal'+ '_' + entityClass).value;
			var gridData = getGridData();
			var grid = registry.byId('grid'+ '_' + entityClass);
			var inventario_data = {'fecha':fecha,'sucursal':sucursal,'registros':gridData, 'entityClass':entityClass};
			registry.byId('standby_centerPane').show();
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
					registry.byId('standby_centerPane').hide();
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
		
		var actualizarInventarios = function(response, data, entityClass){
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