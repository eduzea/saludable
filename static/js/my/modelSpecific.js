//# sourceURL=../static/js/my/modelSpecific.js
require(['dojo/dom','dijit/registry',"dojo/dom-attr",'dojo/request','dojo/topic','dojo/number'],
function(dom,registry,domAttr,request,topic,number)
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
			
			var loteSelect = registry.byId('loteDeCompra_Produccion');
			var precio = loteSelect.getOptions(loteSelect.value)['precio'];
			costoBruto = pesoFruta * precio * 1000 / grid.summarize();
			costoBrutoDom = dom.byId('costoBruto_Produccion');
			domAttr.set(costoBrutoDom,'value',number.format(costoBruto,{pattern:'###,###'}));
		}
	};
	
	//Mechanism to inject entityClass specific functionality into generic AddEntity form.

	var getLotes = function(fruta){
		request('/getLotes?fruta=' + fruta, {handleAs:'json'}).then(
			function(response){
				var items = [];
				if (response.length == 0){
					items.push({ "value": 'NO.HAY', "label": 'NO HAY' });
				}else{
					response.forEach(function(lote){
						items.push({ "value": lote.rotulo, "label": lote.rotulo, 'precio': lote.precio, 'peso':lote.peso});
					});								
				}
				var loteSelect = registry.byId('loteDeCompra_Produccion');
				loteSelect.options = [];
				loteSelect.addOption(items);
				loteSelect.reset();
				loteSelect.onChange();
			}
		);
	};

	saludable.addEntityFuncs =
	{
		'Produccion':
		function(){
			frutaSelect = registry.byId('fruta_Produccion');
			frutaSelect.onChange = function(){
				topic.publish('FRUTA_PRODUCCION',this.value);
			};
			loteSelect = registry.byId('loteDeCompra_Produccion');
			loteSelect.listenerfunc = getLotes; 
			topic.subscribe('FRUTA_PRODUCCION', loteSelect.listenerfunc);
			loteSelect.onChange = function(){
				pesoTextBox = registry.byId('pesoFruta_Produccion');
				pesoTextBox.set('value',loteSelect.getOptions(loteSelect.value)['peso']);
			};
			frutaSelect.onChange();
		}
	};
});