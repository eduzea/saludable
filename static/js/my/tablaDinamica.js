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
	
	var meses = [ "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre" ];
    
	var ammendRecord = function (record){
		var fecha = new Date(record.fecha);
		var mes = meses[fecha.getMonth()];
		record.mes = mes;
		return record;
	};
	request(url, {handleAs:'json'}).then(function(response) {
		var records = response.records;
		var ammendedRecords = records.map(ammendRecord);
		$(function() {
			$("#" + tipo + "_output").pivotUI(ammendedRecords, config[tipo],false,'es');
		});
	});
}); 