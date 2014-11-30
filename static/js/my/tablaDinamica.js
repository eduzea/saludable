//# sourceURL=../static/js/my/tablaDinamica.js
require(['dojo/request'], 
function(request) {
	var tipo = saludable.entity_class;
	var url = (tipo == 'clientes') ? '/entityData?entityClass=Factura' : '/getProductSales';
	var config = {
		'clientes': {
				rows : ["cliente",'fecha','numero'],
				vals : ["total"],
				exclusions: {'anulada':['true']},
				hiddenAttributes:['id','empleado'],
				aggregatorName:'Suma'
		},
		'productos': {
				rows : ["producto",'porcion'],
				vals : ["venta"],
				aggregatorName:'Suma'
			}
	};
	request(url, {handleAs:'json'}).then(function(response) {
		var records = response.records;
		$(function() {
			$("#" + tipo + "_output").pivotUI(records, config[tipo],false,'es');
		});
	});
}); 