//# sourceURL=../static/js/my/existencias.js
require(['dojo/request',"dijit/registry",'dojo/parser','dojo/dom','dojo/on','dojo/query',"dojo/dom-class"], 
function(request,registry,parser,dom,on,query,domClass) {
	var sortAs = $.pivotUtilities.sortAs;
	var numberFormat = $.pivotUtilities.numberFormat;
	var config = {
		rows : ['producto',"porcion","ubicacion"],
		vals : ["cantidad"],
		aggregatorName:'Suma'
	};
	request('/getExistencias', {handleAs:'json'}).then(function(response) {
		totals = query(".pvtTotal")
		totals.forEach(function(node){
			domClass.add(node,'hide');
		});
		$(function() {
			$("#" + "existencias_Pivot").pivotUI(response, config,false,'es');
		});
	});		
	registry.byId('standby_centerPane').hide();
}); 