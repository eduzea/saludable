//# sourceURL=../static/js/my/crearFactura.js

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
		'dojox/html/entities',
		'dojo/ready',
		'dojo/topic',
		'dojo/store/Memory',
		'dijit/form/CheckBox',
		'gridx/modules/SingleSort',
		'gridx/modules/Edit',
		'dijit/form/NumberTextBox'
		], 
function(dom, domAttr, registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json,number,Select,domClass, html, ready,topic,Memory,Checkbox) {
	var entityClass = saludable.entity_class;	
	
	var resetCliente = function(cliente){	
		request.post('/getClientes', {handleAs:'json'}).then(function(response){
			var items = [];
			response.forEach(function(cliente){
				items.push({ "value": cliente.value, "label": cliente.name });
			});
			var clienteSelect = registry.byId('cliente'+ '_' + entityClass);
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
					var productoSelect = registry.byId('producto'+ '_' + entityClass);
					productoSelect.setStore(productoStore);
					productoSelect.reset();
					resetPorcion(productoSelect.value);
			});
		};	
	
	var resetPorcion = function(producto){
			if (producto == 'No hay precios definidos') return;
			cliente = registry.byId('cliente'+ '_' + entityClass).value;	
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
					var porcionSelect = registry.byId('porcion'+ '_' + entityClass);
					porcionSelect.setStore(porcionStore);
					porcionSelect.reset();
			});
		};
		
    parser.instantiate([dom.byId('cliente'+ '_' + entityClass)]);
    var clienteSelect = registry.byId('cliente'+ '_' + entityClass);
    clienteSelect.onChange = resetProducto; 
    clienteSelect.set('style','font-size:70%');
    resetProducto(clienteSelect.value);
    	
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
	
	var selects = [clienteSelect, productoSelect, porcionSelect];
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

  	
	var updateTotal = function(){
		var data = getGridData();
		var sumTotal=0;
		data.forEach(function(entry){
			sumTotal = sumTotal + entry.precio * entry.cantidad ;
		});
		var grid = registry.byId('grid'+ '_' + entityClass);
		var conIva = registry.byId('iva'+ '_' + entityClass).checked;
		var iva = conIva ? 0.16 : 0;
		grid.subtotal = sumTotal;
		grid.iva = Math.floor(sumTotal * iva);
		grid.total = grid.subtotal + grid.iva;
		dom.byId('subtotal').innerHTML = number.format(grid.subtotal,{pattern:'###,###.#'});
		dom.byId('iva').innerHTML = number.format(grid.iva,{pattern:'###,###.#'});
		dom.byId('total').innerHTML = number.format(grid.total,{pattern:'###,###.#'});
	};
	
	parser.instantiate([dom.byId('iva'+ '_' + entityClass)]);
    on(registry.byId('iva'+ '_' + entityClass), 'change', updateTotal);
		
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
	
	var actualizarFacturas = function(response, data, entityClass){
		var id = 'gridNode'+ '_' + entityClass;
		var grid = registry.byId(id);
		var key = response.id;
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
	
	parser.instantiate([dom.byId('guardar'+ '_' + entityClass + 'Btn')]);
	on(registry.byId('guardar'+ '_' + entityClass +'Btn'),'click',
		function(e){
			var cliente = registry.byId('cliente'+ '_' + entityClass).value;
			var fecha = registry.byId('fecha'+ '_' + entityClass).toString();
			var numero = dom.byId('numero'+ '_' + entityClass).innerHTML.replace('No.','');
			var gridData = getGridData();
			var grid = registry.byId('grid'+ '_' + entityClass);
			updateTotal();
			var factura_data = {'cliente':cliente,'fecha':fecha,'ventas':gridData, 'subtotal':grid.subtotal,'montoIva':grid.iva,'total':grid.total,  
			'numero':numero, 'entity_class':entityClass};
			request.post('/guardarFactura', {
					data : json.stringify(factura_data),
					handleAs:'json'
				}).then(function(response) {
					var message='';
					if(response.result == 'Success'){
						message = 'Se grabo exitosamente este pedido!';
						factura_data['cliente']=registry.byId('cliente'+ '_' + entityClass).attr('displayedValue');
						actualizarFacturas(response, factura_data, entityClass);
						var pagina = registry.byId( '_' + entityClass + 'PorPagina').checked;
						var url = '/mostrarFactura?id='+response.id + '&entityClass=' + entityClass+ '&pagina='+ pagina.toString();
						window.open(url);
					}else{
						message = 'No se pudo guardar este pedido!';
					}
					dom.byId('mensaje'+ '_' + entityClass).innerHTML = message;
					setTimeout(function() {
						var grid =registry.byId('grid'+ '_' + entityClass);
						grid.model.clearCache();
						grid.model.store.setData([]);
        				grid.body.refresh();
						dom.byId('mensaje'+ '_' + entityClass).innerHTML = '';
						dom.byId('total').innerHTML = '';
						dom.byId('subtotal').innerHTML = '';
						dom.byId('iva').innerHTML = '';
						dom.byId('numero'+ '_' + entityClass).innerHTML = '';
					}, 2000);
					topic.publish('FACTURA',{'action':'ADD', 'id':response.id});
				});
		});
	
	parser.instantiate([dom.byId('agregarPedidoBtn'+ '_' + entityClass)]);
	on(registry.byId('agregarPedidoBtn'+ '_' + entityClass),'click',function(e){
		var form = registry.byId('addEntityForm' +  '_' + entityClass);
		if (!form.validate()){
			alert("'Cantidad' no puede estar vacio!");
			return;
		}
		var formdata = getFormData(entityClass);
		request.post("getPrice",
		{
			data: {'producto':formdata['producto'], 'cliente':formdata['cliente'], 'porcion': formdata['porcion']}
		}).then(function(precio){
			if (precio == 'list index out of range'){
				alert("No hay precio definido para esta combinacion producto x cliente! Definelo primero.");
				return;	
			}
			var grid = registry.byId('grid'+ '_' + entityClass);
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
	
	parser.instantiate([dom.byId('nueva'+ '_' + entityClass+'Btn')]);
	on(registry.byId('nueva'+ '_' + entityClass+'Btn'),'click',function(e){
		registry.byId('addEntityForm' +  '_' + entityClass).reset();
		var grid = registry.byId('grid'+ '_' + entityClass);
		grid.model.clearCache();
		grid.model.store.setData([]);
		grid.body.refresh();		
		updateTotal();
		dom.byId('numero'+ '_' + entityClass).innerHTML='';
	});
	
	if (dom.byId('anular'+ '_' + entityClass+'Btn')){
		parser.instantiate([dom.byId('anular'+ '_' + entityClass+'Btn')]);
		on(registry.byId('anular'+ '_' + entityClass+'Btn'),'click',function(e){
			var numero = dom.byId('numero'+ '_' + entityClass).innerHTML;
			request('/anularFactura?tipo=' + entityClass + '&id=' + numero).then(function(){
				registry.byId('anulada'+ '_' + entityClass).set('value','ANULADA');
				domAttr.set('anulada'+ '_' + entityClass, 'style', 'visibility:visible;color:red');
			});
		});		
	}
	parser.instantiate([dom.byId('anulada'+ '_' + entityClass)]);
	var anuladaText= registry.byId('anulada'+ '_' + entityClass);
	anuladaText.onChange = function(anulada){
		this.set('value',anulada ? 'ANULADA' : '');
		domAttr.set('anulada'+ '_' + entityClass, 'style', 'width:100px;border:none;color:red');
		};

	
	var store = new Store();
	var columns = [
		{field : 'producto', name : 'Producto', style: "text-align: center"},
		{field : 'porcion', name : 'Porcion', style: "text-align: center"},
		{field : 'cantidad', name : 'Cantidad', style: "text-align: center"},
		{field : 'precio', name : 'Precio Unitario', style: "text-align: center", editable: true,
				editor: "dijit.form.NumberTextBox", 
				formatter: function(data){
					return number.format(data.precio,{pattern:'###,###'});
				}
				
		},
		{field : 'venta', name : 'Valor Total', style: "text-align: center", 
				formatter: function(data){
					return number.format(data.venta,{pattern:'###,###.#'});
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
		modules : [	"gridx/modules/CellWidget",
					'gridx/modules/SingleSort',
					'gridx/modules/Edit'
					]
	}, 'grid'+ '_' + entityClass);
	grid.startup();
	grid.edit.connect(grid.edit, "onApply", function(cell) {
		var origData = grid.store.get(cell.row.id);
			var venta = origData['cantidad'] * origData['precio'];
			origData['venta'] = venta;
			grid.row(cell.row.id).setRawData(origData);  
			updateTotal();
		}
	);
	grid.updateTotal = updateTotal;
	domClass.add(dom.byId('grid'+ '_' + entityClass),'factura-grid');
	
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
