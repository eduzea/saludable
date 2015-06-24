//# sourceURL=../static/js/my/showEntities.js
require(['dojo/store/Memory',
		 'gridx/Grid',
		 'gridx/core/model/cache/Sync',
		 'dojo/request','dijit/form/Button',
		 'gridx/modules/CellWidget',
		 'dijit/registry',
		 'dojo/query',
		 'dojo/parser',
		 'dojo/dom',
		 "dojo/dom-construct",
		 'dojox/html/entities',
		 "dojo/number",
		 "dojo/on",
		 'gridx/support/exporter/toCSV',
		 'dojo/aspect',
		 'dojo/topic',
		 'gridx/modules/SingleSort',
		 "gridx/modules/Pagination",
		 "gridx/modules/pagination/PaginationBar",
		 'gridx/modules/Filter',
		 'gridx/modules/filter/FilterBar',
		 'gridx/support/exporter/exporter',
		 'dijit/form/SimpleTextarea',
		 'dijit/form/CheckBox'], 
function(Store, Grid, Cache, request, Button, CellWidget,registry, query, parser,dom,domConstruct,html,number,on,toCSV,aspect,topic) {
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
		var borrarColumn = { field : 'Borrar', name : '', widgetsInCell: true, width:'5em',
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
    						topic.publish(entity_class.toUpperCase(), {'action':'DELETE','value':rowData.id});    						
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
			if (label in lookup){
				return lookup[label];	
			}else{
				dijit.addOption({disabled:false,label:label.replace('.',' '),selected:true,value:label});
			}
			return label;
		};
		
		//This is UGLY!
		var urlForDetails = {'Factura':'/getVentas?facturaKey=', 'Remision':'/getVentas?facturaKey=', 
							'Egreso':'/getCompras?egresoKey='};
							
		var numeroDomId = {'Factura':'numero_Factura', 'Remision':'numero_Remision', 'Egreso':'numero_Egreso'};
		var fillForm = function(nodelist, rowData, entity_class){
			nodelist.forEach(function(node, index, array){
	   			var dijit = registry.byId(node.id);
	   			if (dijit){
	   				if (dijit.id.indexOf("grid") > -1 ){
	   					request(urlForDetails[entity_class] + rowData['id'] + '&tipo=' + entity_class, {handleAs:'json'}).then(function(response)
	   					 {
	   						dijit.model.clearCache();
							dijit.model.store.setData([]);//dijit.model.store.setData(items) //should work but its not calling onCellWidgetCreated!
							response.forEach(function(item){
								dijit.store.add(item);								
							});
							dijit.body.refresh();
							dijit.total = dijit.updateTotal();
							dom.byId(numeroDomId[entity_class]).innerHTML = rowData.numero;
	   					});
	   				}else{
			        	var id= dijit.id.replace('_' + entity_class,''); 
			        	if(id in rowData){
			        		dijit.set('value', getValueFromLabel(dijit,rowData[id]),false);
			        	}	   				
	   				}			
	   			}
            });
		};
				
		exportarDatos = function(){
			var grid = registry.byId('gridNode'+ entity_class);
			toCSV(grid).then(function(csv){
				var win = window.open('','DATOS EXPORTADOS');
				csv = csv.replace(/\r\n/g,'<br/>');
				win.document.write(csv);
				win.document.title = entity_class;
			});
		};
		
		
		parser.instantiate([dom.byId('exportarDatos'+entity_class)]);
		var exportarBtn = registry.byId('exportarDatos'+entity_class);
		on(exportarBtn,'click',exportarDatos);
		
		var editarColumn = { field : 'Editar', name : '', widgetsInCell: true, width:'5em',
			onCellWidgetCreated: function(cellWidget, column){
   				var btn = new Button({
					label : "Editar",
					onClick : function() {
						var widget = saludable.widgetCache['widget' + entity_class].getChildren()[0];
						widget.selectChild(widget.getChildren()[0]);
	                    // get the selected row's ID
	                    var selectedRowId = cellWidget.cell.row.id;
	                    // get the data
	                    var rowData = grid.row(selectedRowId, true).rawData();
	                    var nodelist= query('[id*='+ entity_class +']', 'addEntityForm'+ '_' + entity_class);
	                    if (nodelist.length == 0){
	                    	var contentPane= registry.byId(entity_class + '_add');
							contentPane.set("onDownloadEnd", function(){
								nodelist= query('[id*='+ entity_class +']', 'addEntityForm'+ '_' + entity_class );
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
			width: '100%',
			heigth: '100%',
			modules: [
				"gridx/modules/CellWidget",'gridx/modules/SingleSort',"gridx/modules/Pagination","gridx/modules/pagination/PaginationBar",
				'gridx/modules/Filter','gridx/modules/filter/FilterBar'
			]
		}, 'gridNode'+ entity_class);
		
		
		aspect.after(grid.body, 'onAfterRow', function(row) {
			key = row.id;
			if ('anulada' in row.grid.store.get(key)) {
				if (row.grid.store.get(key).anulada == true) {
					row.node().style.color = 'gray';
				}
			}
		}, true);


		grid.startup();
	}, function(error) {
		console.log("An errror occurred " + error);
	});

});
