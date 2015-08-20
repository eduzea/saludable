//# sourceURL=../static/js/my/existencias.js
require(['dojo/store/Memory',
		 'dojo/request',
		 'dijit/registry',
		 'dojo/dom',
		 "dojo/number",
		 "dojo/on",
		 "dojox/widget/Standby",
		 'gridx/Grid',
		 'dojo/topic',
		 //Gridx modules
		 "gridx/modules/Bar",'gridx/support/Summary','gridx/support/DropDownPager','gridx/support/QuickFilter',
		 'gridx/support/LinkSizer','gridx/support/LinkPager','gridx/modules/SingleSort',"gridx/modules/Pagination","gridx/modules/pagination/PaginationBar",
		 'gridx/modules/Filter','gridx/modules/filter/FilterBar',
		 //End gridx modules
], 
function(Memory, request, registry,dom,number,on,Standby,Grid,topic) {
	var entityClass = saludable.entity_class;
	//Create and ready standby
	var standby = new Standby({target: 'centerPane'});
	document.body.appendChild(standby.domNode);
	standby.startup();
	//function to update data
	var getData = function(){
	 	standby.show();
	 	request('/getExistencias',{handleAs:'json'}).then(function(response){
	 		grid = registry.byId(entityClass + '_grid');
	 		grid.model.clearCache();
			grid.model.store.setData(response);
			grid.body.refresh();
		standby.hide();
		});
	 };
	
	//create and ready grid
	var store = new Memory({});
	var columns = [
		{field:'ciudad', name:'Ciudad',style:"text-align: center", width:'10em'},
		{field:'producto', name:'Producto',style:"text-align: center", width:'10em'},
		{field:'porcion', name:'Porcion',style:"text-align: center", width:'10em'},
		{field:'existencias', name:'Existencias',style:"text-align: center", width:'10em'},
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
     var grid = new Grid(gridProps, entityClass+'_grid');
     grid.startup();
     
     grid.listenerfunc = function(){
     	getData();
     };
     topic.subscribe('INVENTARIO', grid.listenerfunc);
     topic.subscribe('FACTURA',grid.listenerfunc);
     getData();
	registry.byId('standby_centerPane').hide();
});