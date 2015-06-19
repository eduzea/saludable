//# sourceURL=../static/js/my/tablaDinamica.js
require(['dojo/request',"dijit/registry",'dojo/parser','dojo/dom','dojo/on','dojo/query'], 
function(request,registry,parser,dom,on,query) {
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

	parser.instantiate([dom.byId('copiarTabla')]);
	on(registry.byId('copiarTabla'),'click', function () {
		el = query(".pvtTable")[0];
        var body = document.body, range, sel;
        if (document.createRange && window.getSelection) {
            range = document.createRange();
            sel = window.getSelection();
            sel.removeAllRanges();
            try {
                range.selectNodeContents(el);
                sel.addRange(range);
            } catch (e) {
                range.selectNode(el);
                sel.addRange(range);
            }
        } else if (body.createTextRange) {
            range = body.createTextRange();
            range.moveToElementText(el);
            range.select();
        }
        alert('Usa Ctr + C para copiar el informe. Despues pegalo en Excel.');
    });
	
}); 