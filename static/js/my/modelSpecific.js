//# sourceURL=../static/js/my/modelSpecific.js
require(['dojo/dom','dijit/registry',"dojo/dom-attr",'dojo/request','dojo/topic','dojo/number','dojo/dom-style'],
function(dom,registry,domAttr,request,topic,number,domStyle)
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
			var onChangeInit = {};
			var tipoSelect = registry.byId('tipo_MovimientoDeInventario');
			tipoSelect.onChange = function(){
				if (this.value == 'SALIDA'){
					//Hide producto and porcion selects, show lote select
					domStyle.set(registry.byId('producto_MovimientoDeInventario').domNode, 'display', 'none');
					domStyle.set(registry.byId('porcion_MovimientoDeInventario').domNode, 'display', 'none');
					domStyle.set(registry.byId('lote_MovimientoDeInventario').domNode, 'display', 'block');
					var lotes = {};
					var ubicacionSelect = registry.byId('ubicacion_MovimientoDeInventario');
					onChangeInit['ubicacionSelect'] ? '' : ubicacionSelect.onChange = function(){
						onChangeInit['ubicacionSelect']=true;
						request('/getContenidoUnidadDeAlmacenamiento?ubicacion='+  this.value, {handleAs:'json'}).then(
							function(response){
								lotes = {};
								response.forEach(
								function(lote){
									var key = lote.fecha + '.' + lote.producto + '.' + lote.porcion;
									lotes[key]=lote;
								})
								if (Object.keys(lotes)[0]){
									var options = Object.keys(lotes).map(function(lote){
										return {'value': lote, 'label':lote };
									})
									loteSelect.set('options',options);
									loteSelect.startup();
								}else{
									alert('ESTA CANASTILLA ESTA VACIA.');
									tipoSelect.set('value','ENTRADA');
								}
								loteSelect.onChange();
							}
						)
					}
					var loteSelect = registry.byId('lote_MovimientoDeInventario');
					onChangeInit['loteSelect'] ? '' : loteSelect.onChange = function(){
						onChangeInit['loteSelect'] = true;
						var key = this.value;
						registry.byId('cantidad_MovimientoDeInventario').set('value',lotes[key].cantidad);
						registry.byId('producto_MovimientoDeInventario').set('value',lotes[key].producto);
						registry.byId('porcion_MovimientoDeInventario').set('value',lotes[key].porcion);
					}
					ubicacionSelect.onChange();
				}else{//ENTRADA
					//Show producto and porcion selects, hide lote select
					domStyle.set(registry.byId('producto_MovimientoDeInventario').domNode, 'display', 'block');
					domStyle.set(registry.byId('porcion_MovimientoDeInventario').domNode, 'display', 'block');
					domStyle.set(registry.byId('lote_MovimientoDeInventario').domNode, 'display', 'none');
					var cantidadField = registry.byId('cantidad_MovimientoDeInventario');
					cantidadField.set('value','');
				}
			}
			tipoSelect.onChange();
		},
		'Pedido':
		function(){	
			var resetProducto = function(cliente){	
			request.post('/getProducto', {
				data : {'cliente':cliente},
				handleAs:'json'
			}).then(function(response) {
					var items = [];
					response.forEach(function(producto){
						items.push({ "value": producto, "label": producto });
					});
//					var productoStore = new Store({
//			        	idProperty: "value",
//			            data: items
//			        });
					var productoSelect = registry.byId('producto_Venta');
//					productoSelect.setStore(productoStore);
					productoSelect.set("options", items).reset();
					resetPorcion(productoSelect.value);
				});
			};
			var resetPorcion = function(producto){
				if (producto == 'No hay precios definidos') return;
				cliente = registry.byId('cliente_Pedido').value;	
				request.post('/getPorcion', {
						data : {'cliente':cliente, 'producto': producto},
						handleAs:'json'
					}).then(function(response) {
						var items = [];
						response.forEach(function(producto){
							items.push({ "value": producto, "label": producto });
						});
						var porcionSelect = registry.byId('porcion_Venta');
						porcionSelect.set("options", items).reset();
						porcionSelect.reset();
				});
			};
		    var clienteSelect = registry.byId('cliente_Pedido');
		    clienteSelect.onChange = resetProducto;
		    var productoSelect = registry.byId('producto_Venta');
		    productoSelect.onChange = resetPorcion;
		    var porcionSelect = registry.byId('porcion_Venta');
		    resetProducto(clienteSelect.value);
			var selects = [clienteSelect, productoSelect, porcionSelect];
			selects.forEach(function(select){
				select.listenerfunc = function(data){
		    		select.addOption({ disabled:false, label:data.label, selected:true, value:data.value});
		    		var store = new Memory({data: select.options});
		    		var sorted = store.query({},{sort: [{ attribute: "label"}]});
		    		select.options = sorted;
		    		select.set("value",sorted[0].value);
		   		};
		   		topic.subscribe(select.id.replace( '_Pedido','').toUpperCase(), select.listenerfunc);
			});	
		}
	}
});