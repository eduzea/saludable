require(['dojo/dom',
		 'dojo/parser',
		 "dijit/registry",
		 "dojo/on",
		 "dojo/ready",
		 "dojo/domReady!"], 
function (dom,parser,registry, on, ready) {
    ready(function () {
        parser.instantiate([dom.byId('addTabContainer'),dom.byId('showTabContainer'), dom.byId('pivotTabContainer') ]);
        var panelAdd = registry.byId('addTabContainer');  
        on(panelAdd, "Click", function (event) {
            saludable.entity_class = panelAdd.selectedChildWidget.id.split('_')[0]; 
        });
        var panelShow = registry.byId('showTabContainer'); 
        on(panelShow, "Click", function (event) {
            saludable.entity_class = panelShow.selectedChildWidget.id.split('_')[0]; 
        });
        var panelShow = registry.byId('pivotTabContainer');
        on(panelShow, "Click", function (event) {
            saludable.entity_class = panelShow.selectedChildWidget.id.split('_')[0]; 
        });
    });
});