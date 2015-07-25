//# sourceURL=../static/js/my/cuentasPorCobrar.js
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
function(Memory, JsonRest, Grid, Cache, request, Button, CellWidget,registry, query, parser,dom,domConstruct,html,number,on,toCSV,aspect,topic,Standby) {
	var entity_class = saludable.entity_class;
	request('/getCuentasPorCobrar',{handleAs:'json'}).then(
		function(response){
			var resumenStore = new Memory({data: response});
			var resumenColumns = [
				{field:'cliente', name:'Cliente','style':"text-align: center", 'width':'20em'},
				{field:'monto', name:'Saldo','style':"text-align: center", 'width':'10em'}
			];
										
			var detalleColumn = { field : 'detalle', name : '', widgetsInCell: true, width:'5em',
			onCellWidgetCreated: function(cellWidget, column)
				{
	   				var btn = new Button({
						label : "Detalle",
						onClick : function() {
		                    var selectedRowId = cellWidget.cell.row.id;
		                    var rowData = resumenGrid.row(selectedRowId, true).rawData();
		                    request("getDetalleCuentasPorCobrar?cliente="+rowData.id,{handleAs:'json'}).then(
		                    	function(response){
		                    		var grid = registry.byId(entity_class+'_detalle_grid');
		                    		grid.model.clearCache();
									grid.model.store.setData(response);
									grid.body.refresh();
									dom.byId(entity_class + '_title').innerHTML = rowData.id; 
									var widget = registry.byId('widget'+entity_class);
									widget.selectChild(widget.getChildren()[1]);
									}
								);
							}
						});
					btn.placeAt(cellWidget.domNode);
				},
			};
			
			resumenColumns.push(detalleColumn);
			
			var gridProps = 
			 {
			 	cacheClass: Cache,
			 	store: resumenStore,
	          	structure: resumenColumns,
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

			
			var resumenGrid = new Grid(gridProps, entity_class+'_resumen_grid');
			resumenGrid.startup();
			
			var detalleColumns = [
				{field:'factura', name:'Factura', 'style':"text-align: center", 'width':'4em'},
				{field:'fecha', name:'Fecha', 'style':"text-align: center", 'width':'5em'},
				{field:'total', name:'Valor', 'style':"text-align: center", 'width':'5em'},
			];

			gridProps['store']=new Memory();
			gridProps['structure']=detalleColumns;
			var detalleGrid = new Grid(gridProps, entity_class+'_detalle_grid');
			detalleGrid.startup();
			
		}
	);
});