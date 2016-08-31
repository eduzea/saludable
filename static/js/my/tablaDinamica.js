//# sourceURL=../static/js/my/tablaDinamica.js
require(['dojo/request',"dijit/registry",'dojo/parser','dojo/dom','dojo/on','dojo/query',"dojox/widget/Standby"], 
function(request,registry,parser,dom,on,query,Standby) {
	var entity_class = saludable.entity_class;
	var pivotUrl = {'Ventas': '/getProductSales?' ,
					'Gastos': '/getAllCompras?',
					'Utilidades':'/getUtilidades?',
					'Recaudado': '/entityData?entityClass=Factura&iva=true',
					'Pagado': '/getIVAPagado?'
				}; 
	var url = pivotUrl[entity_class];
	var config = {
		'Ventas': {
				rows : ['ciudad',"cliente"],
				vals : ["venta"],
				aggregatorName:'Suma'
		},
		'Gastos':{
					rows: ['sucursal','tipo','bienoservicio',"proveedor"],
					vals: ['compra'],
					exclusions:{},
					hiddenAttributes:[],
					aggregatorName:'Suma'
		},
		'Recaudado': {
				rows : ["cliente",'numero','fecha'],
				vals : ["montoIva"],
				exclusions: {'anulada':['true'],'iva':['false'] },
				hiddenAttributes:['id','empleado','anulada'],
				aggregatorName:'Suma'
		},
		'Pagado': {
				rows : ["proveedor",'numero','fecha'],
				vals : ["ivaPagado"],
				hiddenAttributes:['id','empleado'],
				aggregatorName:'Suma'
		}
	};
	
	parser.instantiate([dom.byId('GenerarInformeBtn_' + entity_class)]);
	//Modal to show its loading
	var standby = new Standby({target: 'pivot_standby'});
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
	registry.byId('standby_centerPane').hide();
}); 