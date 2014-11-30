//# sourceURL=../static/js/my/tablaDinamica.js
require(['dojo/request'], function(request) {
	request('/entityData?entityClass=Factura', {handleAs:'json'}).then(function(response) {
		var records = response.records;
		$(function() {
			$("#output").pivotUI(records, {
				rows : ["cliente",'fecha','numero'],
				vals : ["total"],
				exclusions: {'anulada':['true']},
				hiddenAttributes:['id','empleado'],
				aggregatorName:'Suma'
			},false,'es');
		});
	});
}); 