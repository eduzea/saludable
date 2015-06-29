//# sourceURL=../static/js/my/tablaDinamica.js
require(['dojo/request',"dijit/registry",'dojo/parser','dojo/dom','dojo/on','dojo/query',"dojox/widget/Standby"], 
function(request,registry,parser,dom,on,query,Standby) {
	var entity_class = saludable.entity_class;
	var pivotUrl = {'Clientes': '/getProductSales?' ,
					'IVA': '/entityData?entityClass=Factura'
				}; 
	var url = pivotUrl[entity_class];
	var config = {
		'Clientes': {
				rows : ["cliente",'producto'],
				vals : ["venta"],
				aggregatorName:'Suma'
		},
		'IVA': {
				rows : ["cliente",'numero','fecha'],
				vals : ["montoIva"],
				exclusions: {'anulada':['true'],'iva':['false'] },
				hiddenAttributes:['id','empleado','anulada'],
				aggregatorName:'Suma'
			}
	};
	
	parser.instantiate([dom.byId('GenerarInformeBtn_' + entity_class)]);
	//Modal to show its loading
	var standby = new Standby({target: "output_" + entity_class});
	document.body.appendChild(standby.domNode);
	standby.startup();
	on(registry.byId('GenerarInformeBtn_' + entity_class),'click', function(e){
		var desde = registry.byId('fecha_pivot_1_' + entity_class).value.toISOString().split('T')[0];
		var hasta =  registry.byId('fecha_pivot_2_' + entity_class).value.toISOString().split('T')[0];
		var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta;
		standby.show(); 
		request(url + appendUrl, {handleAs:'json'}).then(function(response) {
			var records = response.records;
			$(function() {
				$("#" + "output_" + entity_class).pivotUI(records, config[entity_class],false,'es');
			});
			standby.hide();
		});		
	});

	parser.instantiate([dom.byId('copiarTabla_' + entity_class)]);
	on(registry.byId('copiarTabla_'+entity_class),'click', function () {
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