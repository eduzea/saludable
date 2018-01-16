//# sourceURL=../static/js/my/tablaDinamica.js
require(['dojo/request',"dijit/registry",'dojo/parser','dojo/dom','dojo/on','dojo/query',"dojo/dom-class","dojox/widget/Standby"], 
function(request,registry,parser,dom,on,query,domClass,Standby) {
	var entityClass = saludable.entityClass;
	var pivotUrl = {'Ventas': '/getAllVentas?' ,
					'Gastos': '/getAllCompras?',
					'IVA_PAGADO':'/getIVA_PAGADO?',
					'IVA_RECAUDADO':'/getIVA_RECAUDADO?',
					'UtilidadesDetallado':'/getUtilidades?detallado=true',
					'Recaudado': '/entityData?entityClass=Factura&iva=true',
					'Pagado': '/getIVAPagado?'
				}; 
	var url = pivotUrl[entityClass];
	var sortAs = $.pivotUtilities.sortAs;
	var numberFormat = $.pivotUtilities.numberFormat;
	var config = {
		'Ventas': {
				rows : ['cliente'],
				vals : ['venta'],
				aggregatorName:'Suma'
		},
		'IVA_PAGADO':{
				rows:['bienoservicio'],
				vals:['iva'],
				aggregatorName:'Suma'
		},
		'IVA_RECAUDADO':{
			rows:['producto'],
			vals:['iva'],
			aggregatorName:'Suma'
	},
		'Gastos':{
					rows: ['bienoservicio','proveedor'],
					vals: ['total'],
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
	
	parser.instantiate([dom.byId('GenerarInformeBtn_' + entityClass)]);
	//Modal to show its loading
	var standby = new Standby({target: 'pivot_standby'});
	document.body.appendChild(standby.domNode);
	standby.startup();
	on(registry.byId('GenerarInformeBtn_' + entityClass),'click', function(e){
		var desde = registry.byId('fecha_pivot_1_' + entityClass).value.toISOString().split('T')[0];
		var hasta =  registry.byId('fecha_pivot_2_' + entityClass).value.toISOString().split('T')[0];
		var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta;
		standby.show(); 
		request(url + appendUrl, {handleAs:'json'}).then(function(response) {
			totals = query(".pvtTotal")
			totals.forEach(function(node){
				domClass.add(node,'hide');
			});
			var records = response.records;
			$(function() {
				$("#" + "output_" + entityClass).pivotUI(records, config[entityClass],false,'es');
			});
			standby.hide();
		});		
	});

	parser.instantiate([dom.byId('copiarTabla_' + entityClass)]);
	on(registry.byId('copiarTabla_'+entityClass),'click', function () {
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