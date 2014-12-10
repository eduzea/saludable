require(['dojo/dom',
		 'dojo/parser',
		 "dijit/registry",
		 "dojo/on",
		 "dojo/ready",
		 "dojo/domReady!"], 
function (dom,parser,registry, on, ready) {
    ready(function () {
    	var setEntityClass = function (event) {
            saludable.entity_class = this.selectedChildWidget.id.split('_')[0]; 
        };
        
    	parser.instantiate([dom.byId('addTabContainer'),dom.byId('showTabContainer'), dom.byId('pivotTabContainer') ]);
        
        var panelIngresosAdd = registry.byId('addIngresosTabContainer');  
        var panelEgresosAdd = registry.byId('addEgresosTabContainer');
        var panelIngresoShow = registry.byId('showIngresosTabContainer');
        var panelEgresoShow = registry.byId('showEgresosTabContainer');
        
        on(panelIngresosAdd, "Click", setEntityClass);
        on(panelEgresosAdd, "Click", setEntityClass);
        on(panelIngresoShow, "Click", setEntityClass);        
        on(panelEgresoShow, "Click", setEntityClass);
    });
});