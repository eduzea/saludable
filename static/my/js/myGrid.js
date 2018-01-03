//# sourceURL=../static/js/my/myGrid.js
define([
	"dojo/_base/declare",
	'dojo/store/Memory',
	'gridx/Grid',    
	'gridx/core/model/cache/Sync',	
	'dojo/request','dijit/form/Button',
	'gridx/modules/CellWidget',
	'dijit/registry',
	'dojo/query',
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
function(	declare, Store, Grid, Cache, request, Button, CellWidget, registry, query, dom, 
			domConstruct, html, number, on, toCSV, aspect, topic, Standby) 
{
	var addBorrarColumn = function(columns){
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
	                    		data: {'key':rowData.id, 'entityClass':grid.gridName}
	                    	}).then(function(text){
    						console.log("The server returned: ", text);
    						grid.store.remove(selectedRowId);
    						grid.model.clearCache();
    						grid.body.refresh();
    						topic.publish(grid.gridName.toUpperCase(), {'action':'DELETE','value':rowData.id});    						
						});
					}
				});
				btn.placeAt(cellWidget.domNode);
			},
		};
		columns.push(borrarColumn);		
	};
	
	var addEditColumn = function(columns){
		var editarColumn = { field : 'Editar', name : '', widgetsInCell: true, width:'5em',
			onCellWidgetCreated: function(cellWidget, column){
   				var btn = new Button({
					label : "Editar",
					parentGrid : grid, 
					onClick : function() {
						var grid = this.parentGrid;
						//var widget = saludable.getWidget(grid.gridName).getChildren()[0];
						var widget = saludable.getWidget(grid.gridName).getChildren()[0].getChildren()[0];
						widget.selectChild(widget.getChildren()[0]);
	                    // get the selected row's ID
	                    var selectedRowId = cellWidget.cell.row.id;
	                    // get the data
	                    var rowData = grid.row(selectedRowId, true).rawData();
	                    topic.publish('EDIT_' + grid.gridName.toUpperCase(), rowData);
	                }
				});
				btn.placeAt(cellWidget.domNode);
			},
		};
		columns.push(editarColumn);
	};
	
	var prepareColumns = function(columns,borrar,editar){
		columns.forEach(function(column){
			if (column.type == 'Integer'){
				column.formatter=function(data){
					return number.format(data[this.field],{pattern:'###,###.#'});
				};
			}
		});
		if (borrar){	
			addBorrarColumn(columns);
		}
		if (editar){
			addEditColumn(columns);
		}
		return columns;
	};
	
	var getServerPagerHtml = function(gridName){
			return '<span id="masBtn_' + gridName + '" class="gridxPagerStepperBtn gridxPagerPage"  tabindex="-1">mas...</span>';
	};
	
	gridProps = {
		 	cacheClass: Cache,
	        barTop: [
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
	grid=null;
	var appendData = function(records){
			var currentData = this.model.store.data;
			currentData.push.apply(currentData,records);
    		grid.model.clearCache();
			grid.model.store.setData(currentData);
			grid.body.refresh();
   	};
		
   var MyGrid = declare("MyGrid", [],
   {
		_gridProps : gridProps,
   		constructor: function(args){
   			gridProps.store = new Store();
   			gridProps.pageSize = args.pageSize;
   			gridProps.paginationInitialPageSize = args.pageSize;
   			gridProps.sortInitialOrder = { colId: args.sortColumnId, descending: true };
   			gridProps.barBottom[2] = {content: getServerPagerHtml(args.gridName)};
			request(args.columnsURL, {handleAs:'json'}).then(function(response){
				gridProps.structure = prepareColumns(response.columns,args.borrar,args.editar);
   				grid = new Grid(gridProps, args.targetNode);
   				grid.gridName = args.gridName;
				grid.startup();
				aspect.after(grid.body, 'onAfterRow', function(row) {
					key = row.id;
					if ('anulada' in row.grid.store.get(key)) {
						if (row.grid.store.get(key).anulada == true) {
							row.node().style.color = 'gray';
						}
					}
				}, true);
				args.callback();
			});
   		},
   		grid:function(){
   			grid.appendData = appendData;
   			grid.dataFetchTrigger = function(){
   				return dom.byId('masBtn_' + this.gridName);
   			};
   			return grid;}
   	});
   return MyGrid;
}); // end define
