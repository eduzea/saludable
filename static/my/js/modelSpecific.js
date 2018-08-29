//# sourceURL=../static/js/my/modelSpecific.js
require(['dojo/dom','dijit/registry',"dojo/dom-attr",'dojo/request','dojo/topic','dojo/number',
	'dojo/dom-style','dojo/on',"dijit/Dialog",'dojo/parser',"dojo/dom-construct",'dijit/form/Button',
	"dojo/json",'dojo/store/Memory',"dijit/form/FilteringSelect","dojo/domReady!"],
function(dom,registry,domAttr,request,topic,number,domStyle,on,Dialog,parser,domConstruct,Button,json,Memory,FilteringSelect)
{
	//prevent access to uninstantiated dijits
	var getDijit = function(id){
		obj = registry.byId(id)
		if (!obj){
			parser.instantiate([dom.byId(id)]);
			obj = registry.byId(id)
		}
		return obj;
	} 
	
	//Specify model specific grid summary operations. Use saludable namespace for global scope.
	saludable.gridSummaryFuncs = 
	{'ProductoPorcion': 
		function(entry){ return entry['porcion'].replace('.g','').replace('.Unidad','') * entry['cantidad'];},
	 'Venta': function(entry){ return entry['total'];}
	 };
	 
	saludable.config = {'dontResetAfterSave' : {'Pedido':''}}
	 
	//Specify model specific logic for click events
	saludable.gridChangeFuncs =
	{
		'Produccion':
		function(grid){
		}
	};
	
	//Mechanism to inject entityClass specific functionality into generic AddEntity form.

	var getLotes = function(materiaPrima){
		request('/getLotes?materiaPrima=' + materiaPrima, {handleAs:'json'}).then(
			function(response){
				var items = [];
				if (response.length == 0){
					items.push({ "value": 'NO.HAY', "label": 'NO HAY' });
				}else{
					response.forEach(function(lote){
						var compraKey = lote.egreso + "." + lote.bienoservicio + "." + lote.detalle.replace(" ",".");
						items.push({ "value": lote.fecha, 
									 "label": lote.fecha,
									 "compraKey":compraKey
									});
					});								
				}
				var loteSelect = registry.byId('lote_Componente');
				loteSelect.options = [];
				loteSelect.addOption(items);
				loteSelect.reset();
				loteSelect.onChange();
			}
		);
	};

	var getMateriasPrimas = function(producto){
		request('/getMateriasPrimasPorProducto?producto=' + producto, {handleAs:'json'}).then(
				function(response){
					var materiaPrimaSelect = registry.byId('materiaPrima_Componente');
					materiaPrimaSelect.options = [];
					materiaPrimaSelect.addOption(response);
					materiaPrimaSelect.reset();
					materiaPrimaSelect.onChange();
				});
	}
	
	saludable.setupPUC = function(model,initClase){
		//LOAD PUC
		var pucStore;
		request('/getPUC?clase=' + initClase, {
			handleAs : 'json'
		}).then(function(response) {
			var grupos = response.grupos;
			var cuentas = response.cuentas;
			var subcuentas = response.subcuentas;
			var grupoSelect = registry.byId('grupo_' + model);
			var cuentaSelect = registry.byId('cuenta_' + model );
			var subCuentaSelect = registry.byId('subcuenta_' + model);

			var options = [];
			grupos.forEach(function(option){
				options.push({ "value": option['pucnumber'], "label": option['nombre'] });
			});
			grupoSelect.set("options", options)
			grupoSelect.startup();
			grupoSelect.onChange = function(value){
				var options = [];
				var selected = cuentas.filter(function(item){
					return item.grupo == value;
					})
				selected.forEach(function(option){
					options.push({ "value": option['pucnumber'], "label": option['nombre'] });
				});
				cuentaSelect.set("options", options)
				cuentaSelect.startup();
				cuentaSelect.onChange(cuentaSelect.value)
			};
			cuentaSelect.onChange = function(value){
				var options = [];
				var selected = subcuentas.filter(function(item){
					return item.cuenta == value;
					})
				selected.forEach(function(option){
					options.push({ "value": option['pucnumber'], "label": option['nombre'] });
				});
				subCuentaSelect.set("options", options)
				subCuentaSelect.startup();
			};

			grupoSelect.onChange(grupoSelect.value);
			cuentaSelect.onChange(cuentaSelect.value)
		});
	};
	saludable.addEntityFuncs =
	{
		'Activo':function(){saludable.setupPUC('Activo',1)},			
		'Pasivo':function(){saludable.setupPUC('Pasivo',2)},
		'Produccion':
		function(){
			materiaPrimaSelect = registry.byId('materiaPrima_Componente');
			materiaPrimaSelect.onChange = function(value){
				value = value ? value : this.value;
				getLotes(value);
			};
			loteSelect = registry.byId('lote_Componente');
			loteSelect.onChange = function(value){
				var selected = loteSelect.options.filter(function(element){ return element.selected == true })[0]
				registry.byId('loteKey_Componente').set('value',selected.compraKey);
			}
			productoSelect = registry.byId('producto_Produccion');
			productoSelect.onChange = function(value){
				value = value ? value : this.value;
				getMateriasPrimas(value);
			};
			productoSelect.onChange();
		},
		'MovimientoDeInventario':
		function(){
			var original = {};
			var onChangeInit = {};
			var fechaLote = getDijit('fechaLote_MovimientoDeInventario');
			domStyle.set(fechaLote.domNode, 'display', 'none');//hidden field
			registry.byId('lote_MovimientoDeInventario').addOption({disabled:true,label:'NA',selected:true,value:'NA'});
			var tipoSelect = registry.byId('tipo_MovimientoDeInventario');
			tipoSelect.onChange = function(){
				if (this.value == 'SALIDA'){
					//Hide producto and porcion selects, show lote select
					domStyle.set(registry.byId('producto_MovimientoDeInventario').domNode, 'display', 'none');
					domStyle.set(registry.byId('porcion_MovimientoDeInventario').domNode, 'display', 'none');
					domStyle.set(registry.byId('fechaLote_MovimientoDeInventario').domNode, 'display', 'none');
					domStyle.set(registry.byId('lote_MovimientoDeInventario').domNode, 'display', 'block');
					var lotes = {};
					var ubicacionSelect = registry.byId('ubicacion_MovimientoDeInventario');
					onChangeInit['ubicacionSelect'] ? '' : 
						ubicacionSelect.onChange = function(){
						onChangeInit['ubicacionSelect']=true;
						request('/getContenidoUnidadDeAlmacenamiento?ubicacion='+  this.value, {handleAs:'json'}).then(
							function(response){
								lotes = {};
								response.forEach(
								function(lote){
									var key = lote.fecha + '.' + lote.producto + '.' + lote.porcion;
									lotes[key]=lote;
								})
								if (tipoSelect.value == 'SALIDA'){
									if (Object.keys(lotes)[0]){
										var options = Object.keys(lotes).map(function(lote){
											return {'value': lote, 'label':lote };
										})
										loteSelect.set('options',options);
										loteSelect.startup();
										loteSelect.onChange();
									}else{
										alert('ESTA CANASTILLA ESTA VACIA.');
										tipoSelect.set('value','ENTRADA');
									}									
								}
							}
						)
					}
					var loteSelect = registry.byId('lote_MovimientoDeInventario');
					onChangeInit['loteSelect'] ? '' : 
						loteSelect.onChange = function(){
						onChangeInit['loteSelect'] = true;
						var key = this.attr('displayedValue');
						registry.byId('cantidad_MovimientoDeInventario').set('value',lotes[key].cantidad);
						registry.byId('producto_MovimientoDeInventario').set('value',lotes[key].producto);
						registry.byId('porcion_MovimientoDeInventario').set('value',lotes[key].porcion);
						registry.byId('fechaLote_MovimientoDeInventario').set('value',lotes[key].fecha);
					}
					ubicacionSelect.onChange();
				}else{//ENTRADA
					//Show producto and porcion selects, hide lote select
					domStyle.set(registry.byId('producto_MovimientoDeInventario').domNode, 'display', 'block');
					registry.byId('producto_MovimientoDeInventario').reset();
					domStyle.set(registry.byId('porcion_MovimientoDeInventario').domNode, 'display', 'block');
					registry.byId('porcion_MovimientoDeInventario').reset();
					domStyle.set(registry.byId('lote_MovimientoDeInventario').domNode, 'display', 'none');
					var cantidadField = getDijit('cantidad_MovimientoDeInventario');
					cantidadField.set('value','');
				}
			}
			tipoSelect.onChange();
		},
		'Pedido':
		function(){
			//Adjust buttons
			var saveBtn = getDijit('agregar_btn_Pedido');
			saveBtn.set('label','Guardar Pedido y generar Orden de Salida');
			var resetBtn = getDijit('reset_Pedido');
			resetBtn.set('label','Nuevo Pedido');
			var old = resetBtn.onClick; 
			resetBtn.onClick = function(){
				var oldRet = old();
				request('/getNext?entityClass=Pedido').then(function(response){
					registry.byId('numero_Pedido').set('value',parseInt(response));
					return oldRet;
				});
			}
			console.log("CREATING DIALOG");
			var myDialog = new Dialog({
			        title: "ORDEN DE SALIDA",
			        style: "width: 500px",
			        id:"ordenDeSalida_dialog"
			    });
			var listenerFunc = function(e) {
				key = registry.byId('numero_Pedido').value;
				request('/crearOrdenDeSalida?pedido=' + key).then(
						function(html) {
							 myDialog.set('content',html);
							 myDialog.show();
							 doit = false;
						})
			};
			topic.subscribe('PEDIDO', listenerFunc);
			
			///////////////////////////////
			var resetProducto = function(cliente){	
			request.post('/getProducto', {
				data : {'cliente':cliente},
				handleAs:'json'
			}).then(function(response) {
					var items = [];
					response.forEach(function(producto){
						items.push({ "value": producto, "label": producto });
					});
					var productoSelect = registry.byId('producto_Venta');
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
		},
		'Porcion':
		function(){
			var unidadesInput = registry.byId('unidades_Porcion');
			unidadesInput.set('uppercase',false);
		},
		'Bienoservicio':
			//Should implement dynamic selects here.
		function(){			
		}
	},
	saludable.showEntitiesFuncs={
			'Factura':function(){
				var grid = getDijit('gridNode_Factura')
				grid.hiddenColumns.add("Borrar");
				grid.hiddenColumns.remove("Imprimir");
			}	
	};
});