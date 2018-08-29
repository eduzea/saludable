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
	var desde, hasta, startDate, endDate;
	var records=[];
	var progressDialog = registry.byId('progress_dialog');
//	progressDialog.set('content','<img src="/static/images/loadingAnimation.gif">');
	progressDialog.set('closable', false);
	var progressBar = registry.byId('progress_bar');
	progressBar.placeAt('progress_dialog');


	var halfPointDate = function(begin, end){
    	var desdeDate = Date.parse(desde);
    	var hastaDate = Date.parse(hasta);
    	var time = hastaDate - desdeDate;
    	var newDate = new Date(desdeDate += time/2); 
		return newDate
	};
	
	var tryDateRange = function(desde, hasta){
		var appendUrl = '&fechaDesde=' + desde.toISOString().split('T')[0] +'&fechaHasta=' + hasta.toISOString().split('T')[0];
    	var deferred = request(url + appendUrl, {handleAs:'json'});
		deferred.response.then(requestGood, requestError);
	}
	
	var requestGood = function(response) {
		totals = query(".pvtTotal")
		totals.forEach(function(node){
			domClass.add(node,'hide');
		});
		records = records.concat(response.data.records);
		var progressBar = registry.byId('progress_bar');
		var progress = 100.0 * (1 - (hasta-endDate) / (startDate - endDate));
//		progressBar.set("value", progress);
		standby.hide();
		if (hasta < endDate){
			desde = hasta; //begin in the half point
			hasta = endDate;
			console.log('Trying: ' + desde + " - " + hasta);
			progressFunc();
			tryDateRange(desde, hasta);			
		}else{
			$(function() {
				$("#" + "output_" + entityClass).pivotUI(records, config[entityClass],false,'es');
			});
			progressDialog.hide();
			records = [];
		}
	};
		
	var requestError =  function(error) {
        var response = error.response;

        var serverMsg = registry.byId('server_message');
        if (response.text.search('DeadlineExceededError') != -1){
    		hasta = halfPointDate(desde,hasta);
    		console.log('Trying: ' + desde + " - " + hasta);
    		progressFunc();
    		tryDateRange(desde, hasta);
        }
        else{ //some other error
        	serverMsg.set("content","Error: " + response.text);
        	serverMsg.show();
        	clearInterval(justOneTimer);
        	progressDialog.hide()
        	
        }
        standby.hide();
    }
	
	var justOneTimer;
	
	var progressFunc = function(){
		clearInterval(justOneTimer);//stop any lingering timer before starting a new one!
		var i=0;
		var start = progressBar.value;
		justOneTimer = setInterval(function(){
			start = start + 0.5;
	       progressBar.set("value", start);//for the first 60 s add to progess
	       i = i + 1;
	       if(i > 60){ //after 60s request will time out
	    	   clearInterval(justOneTimer);
	    	   console.log('Progress: ' + progressBar.value);
	       }
	       if (progressBar.value == 100){
	    	   start = 50;
	    	   progressBar.set("value", start);
	       }
	    }, 1000);
	}
	
	on(registry.byId('GenerarInformeBtn_' + entityClass),'click', function(e){
		desde = registry.byId('fecha_pivot_1_' + entityClass).value;
		startDate = registry.byId('fecha_pivot_1_' + entityClass).value;
		hasta =  registry.byId('fecha_pivot_2_' + entityClass).value;
		endDate = registry.byId('fecha_pivot_2_' + entityClass).value;
		console.log('Trying: ' + desde + " - " + hasta);
		progressDialog.show();
		progressBar.set("value", 0);
		progressFunc();
		tryDateRange(desde, hasta);
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