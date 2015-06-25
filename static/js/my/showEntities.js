//# sourceURL=../static/js/my/showEntities.js
require(['dojo/store/Memory',
		 'dojo/store/JsonRest',
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
		 "dojox/widget/Standby",
		 //Gridx modules
		 "gridx/modules/Bar",
		 'gridx/support/Summary',
		 'gridx/support/DropDownPager',
		 'gridx/support/QuickFilter',
		 'gridx/support/LinkSizer',
		 'gridx/support/LinkPager',
		 'gridx/modules/SingleSort',
		 "gridx/modules/Pagination",
		 "gridx/modules/pagination/PaginationBar",
		 'gridx/modules/Filter',
		 'gridx/modules/filter/FilterBar',
		 'gridx/support/exporter/exporter',
		 //End gridx modules
		 'dijit/form/SimpleTextarea',
		 'dijit/form/CheckBox'], 
function(Store, JsonRest, Grid, Cache, request, Button, CellWidget,registry, query, parser,dom,domConstruct,html,number,on,toCSV,aspect,topic,Standby) {
	
	//BEGIN CONFIG - this is UGLY! Consider shifting to server config...
	var urlForDetails = {'Factura':'/getVentas?facturaKey=', 'Remision':'/getVentas?facturaKey=', 
							'Egreso':'/getCompras?egresoKey='};							
	var numeroDomId = {'Factura':'numero_Factura', 'Remision':'numero_Remision', 'Egreso':'numero_Egreso'};
	//END CONFIG
	
	var entity_class = saludable.entity_class;
	
	var jsonRest = new JsonRest({
		target: '/entityData?',
		sortParam: "sortBy",
	});
	
	//CREATE GRID AFTER GETTING STRUCTURE FROM SERVER
	request('/getColumns?entityClass=' + entity_class, {handleAs:'json'}).then(function(columns) {
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
		
		//Grid properties
		var getServerPagerHtml = function(){
			return '<span id="masBtn_' + entity_class + '" class="gridxPagerStepperBtn gridxPagerPage"  tabindex="-1">mas...</span>';
		};
		
		 var gridProps = 
		 {
		 	cacheClass: Cache,
		 	store: new Store(),
          	structure: columns,
          	paginationInitialPageSize: 100,
		  	pageSize: 100,
	        barTop: [
	               //"gridx/support/Summary",
	               //"gridx/support/DropDownPager",
	               {pluginClass: "gridx/support/QuickFilter", style: 'text-align: right;'}
	        ],
	        barBottom: [
	                "gridx/support/Summary",
	                {pluginClass: "gridx/support/LinkPager", style: 'text-align: right;'},
	                { content: getServerPagerHtml()},
	                {pluginClass: "gridx/support/LinkSizer", style: 'text-align: right;'}
	        ],
	        modules: [
	          	"gridx/modules/CellWidget",
	          	'gridx/modules/SingleSort',
	            "gridx/modules/Bar",
	            "gridx/modules/Pagination",
		        'gridx/modules/filter/FilterBar',
	            "gridx/modules/Filter",
		    ]
         };
		
		//Create the grid
		var grid = new Grid(gridProps, 'gridNode_'+ entity_class);
		
		//To color anulada rows
		aspect.after(grid.body, 'onAfterRow', function(row) {
			key = row.id;
			if ('anulada' in row.grid.store.get(key)) {
				if (row.grid.store.get(key).anulada == true) {
					row.node().style.color = 'gray';
				}
			}
		}, true);
		grid.startup();
		
		//Modal to show its loading
		var standby = new Standby({target: 'gridNode_'+ entity_class});
		document.body.appendChild(standby.domNode);
		standby.startup();
		
		//Event to trigger server fetch
		dom.byId('masBtn_'+entity_class).onclick = function(){
			if(more){
				getNextPage(nextCursor,grid.pageSize);	
			}else{
				this.innerHTML='';
			}
		};

  		//FUNCTION TO GET DATA ONE PAGE AT A TIME
  		var getNextPage = function(cursor, count){
  			standby.show();
			jsonRest.query( {'entityClass':entity_class,'count':count,'cursor':cursor},
							{start: 0, count: count,
								 sort: [{ attribute: '', descending: true }]//sort field will be determined in the server...
								 }
    		).then(function(response){
    			var currentData = grid.model.store.data;
    			currentData.push.apply(currentData,response.records);
	    		grid.model.clearCache();
				grid.model.store.setData(currentData);
				grid.body.refresh();
	  			nextCursor = response.cursor;
	  			more = response.more;
	  			standby.hide();
  			});
  		};

		//GET INIT DATA
		var nextCursor = '';
		var more = true;
		getNextPage(nextCursor,grid.pageSize);  		  				
		  
  	}, function(error) {
		console.log("An errror occurred " + error);
	});
	
	parser.instantiate([dom.byId('exportarDatos_'+entity_class)]);
	var exportarBtn = registry.byId('exportarDatos_'+entity_class);
	on(exportarBtn,'click',exportarDatos);
	
	//HELPER FUNCTIONS
	
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
		        		dijit.set("displayedValue", rowData[id]);
		        	}	   				
   				}			
   			}
        });
	};
				
	var exportarDatos = function(){
		var grid = registry.byId('gridNode_'+ entity_class);
		toCSV(grid).then(function(csv){
			var win = window.open('','DATOS EXPORTADOS');
			csv = csv.replace(/\r\n/g,'<br/>');
			win.document.write(csv);
			win.document.title = entity_class;
		});
	};

});
