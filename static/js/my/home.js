require(['dojo/dom','dojo/parser',"dijit/registry",  "dojo/on", "dojo/ready", "dojo/domReady!"], 
function (dom,parser,registry, on, ready) {
    ready(function () { //wait till dom is parsed into dijits
        parser.instantiate([dom.byId('homeTabContainer')]);
        var panel = registry.byId('homeTabContainer');   //get dijit from its source dom element
        on(panel, "Click", function (event) {   //for some reason onClick event doesn't work 
            saludable.entity_class = panel.selectedChildWidget.id.split('_')[0]; 
        });
    });
});