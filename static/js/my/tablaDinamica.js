//# sourceURL=../static/js/my/tablaDinamica.js
require(['dojo/request',"dijit/registry",'dojo/parser','dojo/dom','dojo/on'], 
function(request,registry,parser,dom,on) {
	var tipo = saludable.entity_class;
	var config = {
		'Clientes': {
				rows : ["cliente",'producto'],
				vals : ["venta"],
				exclusions: {'anulada':['true']},
				hiddenAttributes:['id','empleado'],
				aggregatorName:'Suma'
		}
	};
	
	
	parser.instantiate([dom.byId('GenerarInformeBtn')]);
	on(registry.byId('GenerarInformeBtn'),'click', function(e){
		var desde = registry.byId('fecha_pivot_1').value.toISOString().split('T')[0];
		var hasta =  registry.byId('fecha_pivot_2').value.toISOString().split('T')[0];
		var url = '/getProductSales?fechaDesde=' + desde +'&fechaHasta=' + hasta;
		request(url, {handleAs:'json'}).then(function(response) {
			var records = response.records;
			$(function() {
				$("#" + tipo + "_output").pivotUI(records, config[tipo],false,'es');
			});
		});		
	});
}); 