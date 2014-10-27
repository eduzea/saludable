//# sourceURL=../static/js/my/showEntities.js
require(['dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request','dijit/form/Button',
		"gridx/modules/CellWidget",'dojo/query'], 
function(Store, Grid, Cache, request, Button, CellWidget,query) {
	var entity_class = query(".entity_class");
	entity_class = entity_class[0].id;
	request('/entityData?entityClass=' + entity_class, {handleAs:'json'}).then(function(response) {
		var store = new Store({
			'data' : response.records
		});
		var columns = response.columns;
		var lastColumn = { field : 'Borrar', name : '', widgetsInCell: true,
				onCellWidgetCreated: function(cellWidget, column){
	   				var btn = new Button({
						label : "Borrar",
						onClick : function() {
		                    // get the selected row's ID
		                    var selectedRowId = cellWidget.cell.row.id;
		                    // get the data
		                    var rowData = grid.row(selectedRowId, true).rawData();
		                    request.post("deleteEntity", 
		                    	{
		                    		data: {'key':rowData.id, 'entity_class':entity_class}
		                    	}).then(function(text){
        						console.log("The server returned: ", text);
        						grid.store.remove(selectedRowId);
        						grid.model.clearCache();
        						grid.body.refresh();
        						
    						});
						}
					});
					btn.placeAt(cellWidget.domNode);
				},
		};
		columns.push(lastColumn);
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
