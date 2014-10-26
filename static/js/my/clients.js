require(['dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request','dijit/form/Button',
		"gridx/modules/CellWidget"], 
function(Store, Grid, Cache, request, Button, CellWidget) {
	request('/clientData').then(function(data) {
		var store = new Store({
			'data' : JSON.parse(data)
		});
		var columns = [
			{ field : 'nombre', name : 'Nombre'},
			{ field : 'negocio', name : 'Negocio'},
			{ field : 'ciudad', name : 'Ciudad'},
			{ field : 'direccion', name : 'Direccion'},
			{ field : 'telefono', name : 'Telefono'},
			{ field : 'nit', name : 'NIT'},
			{ field : 'diasPago', name : 'Dias para pago'},
			{ field : 'Borrar', name : '', widgetsInCell: true,
				onCellWidgetCreated: function(cellWidget, column){
	   				var btn = new Button({
						label : "Borrar",
						onClick : function() {
		                    // get the selected row's ID
		                    var selectedRowId = cellWidget.cell.row.id;
		                    // get the data
		                    var rowData = grid.row(selectedRowId, true).rawData();
		                    var key = (rowData.nombre + rowData.negocio).replace(/\s+/g, '');
		                    request.post("deleteClient", {data: {'key':key}}).then(function(text){
        						console.log("The server returned: ", text);
        						grid.store.remove(selectedRowId);
        						grid.model.clearCache();
        						grid.body.refresh();
        						
    						});
						}
					});
					btn.placeAt(cellWidget.domNode);
				},
			}
		];
		var grid = new Grid({
			cacheClass : Cache,
			store : store,
			structure : columns,
			modules: [
				"gridx/modules/CellWidget"
			]
		}, 'gridNode');

		grid.startup();
	}, function(error) {
		console.log("An errror occurred " + error);
	});

});
