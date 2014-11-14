require(['dojo/dom','dojo/parser',"dijit/registry",  "dojo/on", "dojo/ready", "dojo/domReady!"], 
function (dom,parser,registry, on, ready) {
    ready(function () { //wait till dom is parsed into dijits
        parser.instantiate([dom.byId('addTabContainer'),dom.byId('showTabContainer') ]);
        var panelAdd = registry.byId('addTabContainer');   //get dijit from its source dom element
        on(panelAdd, "Click", function (event) {   //for some reason onClick event doesn't work 
            saludable.entity_class = panelAdd.selectedChildWidget.id.split('_')[0]; 
        });
        var panelShow = registry.byId('showTabContainer');   //get dijit from its source dom element
        on(panelShow, "Click", function (event) {   //for some reason onClick event doesn't work 
            saludable.entity_class = panelShow.selectedChildWidget.id.split('_')[0]; 
        });
    });
});