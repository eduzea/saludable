//# sourceURL=../static/js/my/cuentasPorCobrar.js
require(['dojo/store/Memory',
		 'dojo/request',
		 'dijit/form/Button',
		 'dijit/registry',
		 'dojo/dom',
		 "dojo/number",
		 "dojo/on",
		 "dojox/widget/Standby",
		 'gridx/Grid',
		 //Gridx modules
		 'gridx/modules/CellWidget',"gridx/modules/Bar",'gridx/support/Summary','gridx/support/DropDownPager','gridx/support/QuickFilter',
		 'gridx/support/LinkSizer','gridx/support/LinkPager','gridx/modules/SingleSort',"gridx/modules/Pagination","gridx/modules/pagination/PaginationBar",
		 'gridx/modules/Filter','gridx/modules/filter/FilterBar',
		 //End gridx modules
], 
function(Memory, request, Button, registry,dom,number,on,Standby,Grid) {
	var entity_class = saludable.entity_class;
	var standby = new Standby({target: entity_class+'_resumen'});
	document.body.appendChild(standby.domNode);
	standby.startup();
	standby.show();	
	request('/getCuentasPorCobrar',{handleAs:'json'}).then(
		function(response){
			var resumenStore = new Memory({data: response});
			
			var numFormatter=function(data){
					return number.format(data[this.field],{pattern:'###,###'});
				};
			
			var resumenColumns = [
				{field:'cliente', name:'Cliente',style:"text-align: center", width:'20em'},
				{field:'monto', name:'Saldo',style:"text-align: center", width:'10em', formatter: numFormatter}
			];
										
			var detalleColumn = { field : 'detalle', name : '', widgetsInCell: true, width:'5em',
			onCellWidgetCreated: function(cellWidget, column)
				{
	   				var btn = new Button({
						label : "Detalle",
						onClick : function() {
		                    var selectedRowId = cellWidget.cell.row.id;
		                    var rowData = resumenGrid.row(selectedRowId, true).rawData();
		                    standby.show();
		                    request("getDetalleCuentasPorCobrar?cliente="+rowData.id,{handleAs:'json'}).then(
		                    	function(response){
		                    		var grid = registry.byId(entity_class+'_detalle_grid');
		                    		grid.model.clearCache();
									grid.model.store.setData(response);
									grid.body.refresh();
									dom.byId(entity_class + '_title').innerHTML = rowData.id;
									standby.hide(); 
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
			standby.hide();
			
			var detalleColumns = [
				{field:'factura', name:'Factura', 'style':"text-align: center", 'width':'4em'},
				{field:'fecha', name:'Fecha', 'style':"text-align: center", 'width':'5em'},
				{field:'negocio', name:'Negocio', 'style':"text-align: center", 'width':'10em'},
				{field:'total', name:'Valor', 'style':"text-align: center", 'width':'5em',formatter: numFormatter},
				{field:'abono', name:'Abono', 'style':"text-align: center", 'width':'5em',formatter: numFormatter},
			];

			gridProps['store']=new Memory();
			gridProps['structure']=detalleColumns;
			var detalleGrid = new Grid(gridProps, entity_class+'_detalle_grid');
			detalleGrid.startup();
			
		}
	);
});