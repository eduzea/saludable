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
	var entityClass = saludable.entityClass;
	request('/getCuentasPorCobrar',{handleAs:'json'}).then(
		function(response){
			var resumenStore = new Memory({data: response});
			
			var numFormatter=function(data){
					return number.format(data[this.field],{pattern:'###,###'});
				};
			
			var resumenColumns = [
				{id:'cliente', field:'cliente', name:'Cliente',style:"text-align: center", width:'20em'},
				{id:'monto', field:'monto', name:'Saldo',style:"text-align: center", width:'10em', formatter: numFormatter}
			];
										
			var detalleColumn = { field : 'detalle', name : '', widgetsInCell: true, width:'5em',
			onCellWidgetCreated: function(cellWidget, column)
				{
	   				var btn = new Button({
						label : "Detalle",
						onClick : function() {
		                    var selectedRowId = cellWidget.cell.row.id;
		                    var rowData = resumenGrid.row(selectedRowId, true).rawData();
		                    registry.byId('standby_centerPane').show();
		                    request("getDetalleCuentasPorCobrar?cliente=" + encodeURIComponent(rowData.id),{handleAs:'json'}).then(
		                    	function(response){
		                    		var grid = registry.byId(entityClass+'_detalle_grid');
		                    		grid.model.clearCache();
									grid.model.store.setData(response);
									grid.body.refresh();
									dom.byId(entityClass + '_title').innerHTML = rowData.id;
									registry.byId('standby_centerPane').hide(); 
									var widget = registry.byId('widget'+entityClass);
									widget.selectChild(widget.getChildren()[1]);
									}
								);
							}
						});
					btn.placeAt(cellWidget.domNode);
				},
			};
			
			var updateTotal = function(){
				var store = registry.byId('CuentasPorCobrar_resumen_grid').store;
				var data = store.query(); 
				var sumTotal=0;
				data.forEach(function(entry){
					sumTotal = sumTotal + entry.monto;
				});
				dom.byId('cuentasPorCobrar_total').innerHTML = number.format(sumTotal,{pattern:'###,###.#'});
				dom.byId('cuentasPorCobrar_total_label').innerHTML = 'TOTAL CARTERA CLIENTES: ';
			} ;
			
			resumenColumns.push(detalleColumn);
			
			var gridProps = 
			 {
			 	store: resumenStore,
	          	structure: resumenColumns,
	          	paginationInitialPageSize: 100,
			  	pageSize: 100,
			  	sortInitialOrder : { colId: 'monto', descending: true },
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

			
			var resumenGrid = new Grid(gridProps, entityClass+'_resumen_grid');
			resumenGrid.startup();
			updateTotal();
			registry.byId('standby_centerPane').hide();
			
			var boolFormatter=function(data){
					return data[this.field] ? 'Si' : 'No';
				};
			
			var detalleColumns = [
				{id:'factura', field:'factura', name:'Factura', 'style':"text-align: center", 'width':'4em'},
				{id:'fecha', field:'fecha', name:'Fecha', 'style':"text-align: center", 'width':'5em'},
				{id: 'negocio', field:'negocio', name:'Negocio', 'style':"text-align: center", 'width':'15em'},
				{id: 'total', field:'total', name:'Valor', 'style':"text-align: center", 'width':'5em',formatter: numFormatter},
				{id: 'vencimiento', field:'vencimiento', name:'Vencimiento', 'style':"text-align: center", 'width':'5em'},
				{id: 'vencida', field:'vencida', name:'Dias Vencida', 'style':"text-align: center", 'width':'5em'},
			];

			gridProps['store']=new Memory();
			gridProps['structure']=detalleColumns;
			gridProps['sortInitialOrder'] = { colId: 'fecha', descending: false };
			var detalleGrid = new Grid(gridProps, entityClass+'_detalle_grid');
			detalleGrid.startup();
		}
	);
});