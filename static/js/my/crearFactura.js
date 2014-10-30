//# sourceURL=../static/js/my/crearFactura.js

require(['dojo/dom','dijit/registry','dojo/parser','dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request', 'dijit/form/Button', 
"gridx/modules/CellWidget", 'dojo/query',"dojo/on","dojo/_base/json"], 
function(dom,registry, parser, Store, Grid, Cache, request, Button, CellWidget, query, on,json) {
	parser.instantiate([dom.byId('agregarPedidoBtn')]);
	on(registry.byId('agregarPedidoBtn'),'click',function(e){
		var formdata = registry.byId('ventaForm').get('value');
		for (prop in formdata) {
			formdata[prop.replace('crearFactura', '')] = formdata[prop];
			delete formdata[prop];
		}
		request.post("getPrice",
		{
			data: {'fruta':formdata['fruta'], 'client':formdata['client'], 'porcion': formdata['porcion']}
		}).then(function(precio){
			if (precio == 'list index out of range'){
				alert("No hay precio definido para esta combinacion producto x cliente! Definelo primero.");
				return;	
			}
			formdata['id'] = json.toJson(formdata);
			formdata['precio']=precio;
			var grid = registry.byId('gridFactura');
			var row = grid.store.get(formdata['id']);
			if (row){
				grid.store.remove(formdata['id']);	
			}
			grid.store.add(formdata);
		});

		
	});
	var store = new Store();
	var columns = [
		{field : 'fruta', name : 'Fruta', style: "text-align: center"},
		{field : 'porcion', name : 'Porcion', style: "text-align: center"},
		{field : 'cantidad', name : 'Cantidad', style: "text-align: center"},
		{field : 'precio', name : 'Precio Unitario', style: "text-align: center"},
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
		modules : ["gridx/modules/CellWidget"]
	}, 'gridFactura');
	grid.startup();
}); 
