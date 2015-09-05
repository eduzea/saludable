//# sourceURL=../static/js/my/consolidarFactura.js
require(['dojo/dom',
		'dojo/parser',
		"dijit/registry",
		'dojo/query',
		"dojo/on",
		"dojo/number",
		"dojo/store/Memory", 
		'dojo/request',
		"dojox/widget/Standby",
		'gridx/Grid',
		'gridx/core/model/cache/Sync',
		'dojo/request',
		"dojo/json",
		'dijit/form/Button',
		'dojo/dom-class',
		'gridx/modules/CellWidget',
		"gridx/modules/Bar",
		'gridx/support/Summary',
	 	'gridx/support/QuickFilter',
	 	'gridx/support/LinkSizer',
	 	'gridx/support/LinkPager',
	 	'gridx/modules/SingleSort',
	 	"gridx/modules/Pagination",
	 	'gridx/modules/Filter',
	 	'gridx/modules/filter/FilterBar',
	 	'gridx/modules/IndirectSelect',
	 	'gridx/modules/RowHeader',
	 	'gridx/modules/select/Row',
		"dojo/domReady!"], 
function(dom, parser, registry, query, on, number, Store, request, Standby, Grid, Cache, request, json, Button, domClass){
	
	var getRemisiones = function(cliente){	
		registry.byId('standby_centerPane').show();
			request.get('/entityData?entityClass=Remision&cliente=' + cliente + '&sortBy=-numero',
			 {handleAs:'json'}).then(
				function(response) {
					var grid = registry.byId('grid_consolidarFactura');
		    		grid.model.clearCache();
		    		grid.model.store.setData(response.records);
					grid.body.refresh();
					registry.byId('standby_centerPane').hide();
			});
		};
		
	parser.instantiate([dom.byId('cliente_consolidarFactura')]);
	var clienteSelect = registry.byId('cliente_consolidarFactura');
    clienteSelect.onChange = getRemisiones;
    
	//CREATE GRID AFTER GETTING STRUCTURE FROM SERVER
	request('/getColumns?entityClass=Remision', {handleAs:'json'}).then(function(response) {
		var columns = response['columns'];
		columns.forEach(function(column){
			if (column.type == 'Integer'){
				column.formatter=function(data){
					return number.format(data[this.field],{pattern:'###,###'});
				};
			}
		});

		var gridProps = 
			 {
			 	store: new Store(),
	          	structure: columns,
	          	barTop: [
		               {pluginClass: "gridx/support/QuickFilter", style: 'text-align: right;'}
		        ],
		        barBottom: [
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
		            'gridx/modules/select/Row',
		            'gridx/modules/RowHeader',
		            'gridx/modules/IndirectSelect'
			    ]
	         };
			
		//Create the grid
		var grid = new Grid(gridProps, 'grid_consolidarFactura');
		grid.startup();
		domClass.add(dom.byId('grid_consolidarFactura'),'remision-grid');
		
		var btn = new Button({
			label : "Crear Factura", 
			onClick : function() {
				var selected = registry.byId('grid_consolidarFactura').select.row.getSelected();
				request.post('/consolidarFactura',{
					data : json.stringify(selected),
					handleAs:'json'
				}).then(function(response) {
					actualizarFacturas(response);
					var url = '/mostrarFactura?id=' + response.numero + '&entityClass=Factura';
					window.open(url);
				});
			}
		},'consolidarFactura_Btn');
		
		registry.byId('standby_centerPane').hide();
		
		//HELPER FUNCTIONS
		var actualizarFacturas = function(factura){
			var grid = registry.byId('gridNode_Factura');
			if(grid){
				var key = factura.numero;
				factura.id = key;
				factura.numero = key;
				var row = grid.store.get(key);
				if (row){
					grid.store.remove(key);
				}
				grid.store.add(factura);
			}
		};
		
	});	
});
