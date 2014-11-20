//# sourceURL=../static/js/my/showEntities.js
require(['dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request','dijit/form/Button',
		"gridx/modules/CellWidget",'dijit/registry','dojo/query', 'dojo/parser','dojo/dom','dojox/html/entities',"dojo/number",
		'gridx/modules/SingleSort'], 
function(Store, Grid, Cache, request, Button, CellWidget,registry, query, parser,dom,html,number) {
	var entity_class = saludable.entity_class;
	request('/entityData?entityClass=' + entity_class, {handleAs:'json'}).then(function(response) {
		var store = new Store({
			'data' : response.records
		});
		var columns = response.columns;
		columns.forEach(function(column){
			if (column.type == 'Integer'){
				column.formatter=function(data){
					return number.format(data[this.field],{pattern:'###,###'});
				};
			}
		});
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
		
		var getValueFromLabel = function(dijit, label){
			if (!dijit.options){
				return label;
			} 
			var options = dijit.getOptions();
			var lookup = {};
			for (var i = 0, len = options.length; i < len; i++) {
    			lookup[html.decode(options[i].label)] = options[i].value;
			}
			return lookup[label];
		};
		
		var fillForm = function(nodelist, rowData, entity_class){
			nodelist.forEach(function(node, index, array){
	   			var dijit = registry.byNode(node);
	   			if (dijit){
	   				if (dijit.id.indexOf("grid") > -1 ){
	   					request('/getVentas?facturaKey=' + rowData['id'], {handleAs:'json'}).then(function(response) {
	   						dijit.model.clearCache();
							dijit.model.store.setData(response);
							dijit.body.refresh();
							dijit.total = updateTotal();//this function is defined in crearFactura - abstraction leak, try to fix!
							dom.byId('numeroFactura').innerHTML = rowData.numero;
	   					});
	   				}else{
			        	var id= dijit.id.replace(entity_class,''); 
			        	if(id in rowData){
			        		dijit.set('value', getValueFromLabel(dijit,rowData[id]));
			        	}	   				
	   				}			
	   			} 
            });
		};
				
		var editarColumn = { field : 'Editar', name : '', widgetsInCell: true,
			onCellWidgetCreated: function(cellWidget, column){
   				var btn = new Button({
					label : "Editar",
					onClick : function() {
						registry.byId('addTabContainer').selectChild(entity_class + '_add');
						registry.byId('homeTabContainer').selectChild('addTabContainer');
	                    // get the selected row's ID
	                    var selectedRowId = cellWidget.cell.row.id;
	                    // get the data
	                    var rowData = grid.row(selectedRowId, true).rawData();
	                    var nodelist= query('[id*='+ entity_class +']', 'addEntityForm'+ entity_class );
	                    if (nodelist.length == 0){
	                    	var contentPane= registry.byId(entity_class + '_add');
							contentPane.set("onDownloadEnd", function(){
								nodelist= query('[id*='+ entity_class +']', 'addEntityForm'+ entity_class );
								parser.instantiate(nodelist);
    							fillForm(nodelist, rowData, entity_class);	
							});
	                    }else{
                    		fillForm(nodelist, rowData, entity_class);
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
			columnWidthAutoResize: true,
			width: '100%',
			heigth: '100%',
			modules: [
				"gridx/modules/CellWidget",'gridx/modules/SingleSort'
			]
		}, 'gridNode'+ entity_class);

		grid.startup();
	}, function(error) {
		console.log("An errror occurred " + error);
	});

});
