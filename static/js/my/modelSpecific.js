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
		},
		'MovimientoDeInventario':
		function(){
			var original = {};
			var tipoSelect = registry.byId('tipo_MovimientoDeInventario');
			tipoSelect.onChange = function(){
				if (this.value == 'SALIDA'){
					var lotes = {};
					var ubicacionSelect = registry.byId('ubicacion_MovimientoDeInventario');
					ubicacionSelect.onChange = function(){
						request('/getContenidoUnidadDeAlmacenamiento?ubicacion='+  this.value, {handleAs:'json'}).then(
							function(response){
								lotes = {};
								response.forEach(
								function(lote){
									if (lote.fecha in lotes){
										if (lote.producto in lotes[lote.fecha]){
											if (lote.porcion in lotes[lote.fecha][lotes.producto]){
												lotes[lote.fecha][lotes.producto][lote.porcion] = lote.cantidad;
											}else{
												lotes[lote.fecha][lotes.producto] = {};
												lotes[lote.fecha][lotes.producto][lote.porcion] = lote;
											}
										}else{
											lotes[lote.fecha][lote.producto] = {};
											lotes[lote.fecha][lote.producto][lote.porcion]= lote.cantidad;
										}
										lotes[lote.fecha][lote.producto];
									}else{
										lotes[lote.fecha] = {};
										lotes[lote.fecha][lote.producto] = {};
										lotes[lote.fecha][lote.producto][lote.porcion] = lote.cantidad;
									}
								})
								fechaSelect.set('value',Object.keys(lotes)[0]);
								fechaSelect.onChange();
							}
						)
					}
					var fechaSelect = registry.byId('fecha_MovimientoDeInventario');
					fechaSelect.onChange = function(){
						var fecha = this.value.toISOString().slice(0,10);
						if (!lotes.hasOwnProperty(fecha)){
							if (tipoSelect.value == 'SALIDA'){
								alert("Esta canastilla no contiene este lote!");
								fechaSelect.set('value',Object.keys(lotes)[0]);
							}
							return;
						}
						var productoSelect = registry.byId('producto_MovimientoDeInventario');
						productoSelect.onChange = function(){
							var producto = this.value;
							var porcionSelect = registry.byId('porcion_MovimientoDeInventario');
							porcionSelect.onChange = function(){
								var porcion = this.value;
								var cantidadField = registry.byId('cantidad_MovimientoDeInventario');
								cantidadField.set('value',lotes[fecha][producto][porcion])
							}
							var items =[];
							var options = Object.keys(lotes[fecha][producto]);
							options.forEach(function(option){
								items.push({ "value": option, "label": option});
							});
							if (! ('porcion' in original) ){
								original['porcion'] = porcionSelect.options; //copy the options to restore if needed 
							}
							porcionSelect.set("options", items)
							porcionSelect.startup();
							porcionSelect.onChange();

						}
						var items = [];
						var options = Object.keys(lotes[fecha]);
						options.forEach(function(option){
							items.push({ "value": option, "label": option});
						});					
						if (! ('producto' in original) ){
							original['producto'] = productoSelect.options; //copy the options to restore if needed 
						}
						productoSelect.set("options", items)
						productoSelect.startup();
						productoSelect.onChange();
					}
					ubicacionSelect.onChange();
				}else{//ENTRADA
					if ('producto' in original){
						var productoSelect = registry.byId('producto_MovimientoDeInventario');
						productoSelect.set("options", original['producto'])
						productoSelect.startup();
					}

					if ('porcion' in original){
						var porcionSelect = registry.byId('porcion_MovimientoDeInventario');
						porcionSelect.set("options", original['porcion'])
						porcionSelect.startup();
					}
					var cantidadField = registry.byId('cantidad_MovimientoDeInventario');
					cantidadField.set('value','');
				}
			}
		}
	};
});