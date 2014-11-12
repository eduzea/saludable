//# sourceURL=../static/js/my/showEntities.js
require(['dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request','dijit/form/Button',
		"gridx/modules/CellWidget",'dijit/registry','dojo/query', 'dojo/parser'], 
function(Store, Grid, Cache, request, Button, CellWidget,registry, query, parser) {
	entity_class = saludable.entity_class;
	request('/entityData?entityClass=' + entity_class, {handleAs:'json'}).then(function(response) {
		var store = new Store({
			'data' : response.records
		});
		var columns = response.columns;
		var borrarColumn = { field : 'Borrar', name : '', widgetsInCell: true,
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
		
		var fillForm = function(nodelist, rowData){
			nodelist.forEach(function(node, index, array){
	   			var dijit = registry.byNode(node);
	   			if (dijit){
		        	var id= dijit.id.replace(entity_class,''); 
		        	if(id in rowData){
		        		registry.byNode(node).attr('value', rowData[id]);
		        	}	   				
	   			} 
            });
		};
		
		var editarColumn = { field : 'Editar', name : '', widgetsInCell: true,
			onCellWidgetCreated: function(cellWidget, column){
   				var btn = new Button({
					label : "Editar",
					onClick : function() {
	                    // get the selected row's ID
	                    var selectedRowId = cellWidget.cell.row.id;
	                    // get the data
	                    var rowData = grid.row(selectedRowId, true).rawData();
	                    var tabContainer = registry.byId('homeTabContainer');
	                    var nodelist= query('[id*='+ entity_class +']', 'addEntityForm'+ entity_class );
	                    if (nodelist.length == 0){
	                    	var contentPane= registry.byId(entity_class + '_add');
							contentPane.set("onDownloadEnd", function(){
								nodelist= query('[id*='+ entity_class +']', 'addEntityForm'+ entity_class );
								parser.instantiate(nodelist);
    							fillForm(nodelist, rowData);	
							});
							tabContainer.selectChild(entity_class + '_add');	
	                    }else{
                    		tabContainer.selectChild(entity_class + '_add');
                    		fillForm(nodelist, rowData);
	                    }
	                }
				});
				btn.placeAt(cellWidget.domNode);
			},
		};
		columns.push(borrarColumn);
		columns.push(editarColumn);
		var grid = new Grid({
			cacheClass : Cache,
			store : store,
			structure : columns,
			modules: [
				"gridx/modules/CellWidget"
			]
		}, 'gridNode'+ entity_class);

		grid.startup();
	}, function(error) {
		console.log("An errror occurred " + error);
	});

});
