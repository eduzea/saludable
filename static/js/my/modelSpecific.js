//# sourceURL=../static/js/my/modelSpecific.js
require(['dojo/dom','dijit/registry',"dojo/dom-attr"],
function(dom,registry,domAttr)
{
	//Specify model specific grid summary operations
	saludable.gridSummaryFuncs = 
	{'ProductoPorcion': 
		function(entry){ return entry['porcion'].replace('.g','').replace('.Unidad','') * entry['cantidad'];},
	 'Venta': function(entry){ return entry['total'];}
	 };
	 
	 
	//Specify model specific logic for click events
	saludable.gridChangeFuncs =
	{
		'Produccion':
		function(grid){
			var pesoFruta = registry.byId('pesoFruta_Produccion').value;
			var rendimiento = 100 * grid.summarize() / (pesoFruta * 1000);
			var rendimientoDom = dom.byId('rendimiento_Produccion');
			domAttr.set(rendimientoDom,'value',rendimiento);
		}
	};	
});