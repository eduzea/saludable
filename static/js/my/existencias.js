//# sourceURL=../static/js/my/existencias.js
require(['dojo/store/Memory',
		 'dojo/request',
		 'dijit/registry',
		 'dojo/dom',
		 "dojo/number",
		 "dojo/on",
		 "dojox/widget/Standby",
		 'gridx/Grid',
		 //Gridx modules
		 "gridx/modules/Bar",'gridx/support/Summary','gridx/support/DropDownPager','gridx/support/QuickFilter',
		 'gridx/support/LinkSizer','gridx/support/LinkPager','gridx/modules/SingleSort',"gridx/modules/Pagination","gridx/modules/pagination/PaginationBar",
		 'gridx/modules/Filter','gridx/modules/filter/FilterBar',
		 //End gridx modules
], 
function(Memory, request, registry,dom,number,on,Standby,Grid) {
	var entity_class = saludable.entity_class;
	var standby = new Standby({target: entity_class+'_grid'});
	document.body.appendChild(standby.domNode);
	standby.startup();
	standby.show();	
	request('/getExistencias',{handleAs:'json'}).then(
		function(response){
			var store = new Memory({data: response});
			var columns = [
				{field:'ciudad', name:'Ciudad',style:"text-align: center", width:'50em'},
				{field:'fecha', name:'Fecha',style:"text-align: center", width:'10em'},
				{field:'producto', name:'producto',style:"text-align: center", width:'10em'},
				{field:'porcion', name:'porcion',style:"text-align: center", width:'10em'},
				{field:'existencias', name:'existencias',style:"text-align: center", width:'10em'},
			];
			
			var gridProps = 
			 {
			 	store: store,
	          	structure: columns,
	          	paginationInitialPageSize: 100,
			  	pageSize: 100,
		        barTop: [
		               {pluginClass: "gridx/support/QuickFilter", style: 'text-align: right;'}
		        ],
		        barBottom: [
		                "gridx/support/Summary",
		                {pluginClass: "gridx/support/LinkPager", style: 'text-align: right;'},
		                {pluginClass: "gridx/support/LinkSizer", style: 'text-align: right;'}
		        ],
		        modules: [
		          	'gridx/modules/SingleSort',
		            "gridx/modules/Bar",
		            "gridx/modules/Pagination",
			        'gridx/modules/filter/FilterBar',
		            "gridx/modules/Filter",
			    ]
	         };
	         var grid = new Grid(gridProps, entity_class+'_grid');
	         grid.startup();
	         standby.hide();
			
		}
	);
});