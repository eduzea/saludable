//# sourceURL=../static/my/js/utils.js
define(['dojo/dom','dijit/registry','dojo/parser'],
function(dom, registry,parser){
	return{
		getDijit : function(id){
			obj = registry.byId(id)
			if (!obj){
				parser.instantiate([dom.byId(id)]);
				obj = registry.byId(id)
			}
			return obj;
		}
	}
});