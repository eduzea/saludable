//# sourceURL=../static/js/my/utilidades.js

require([
	'dojo/request',
	"dijit/registry",
	'dojo/parser',
	'dojo/dom',
	'dojo/on',
	'dojo/query',
	"dojo/number",
	"dojox/widget/Standby",
	"dojox/layout/TableContainer",
	"dijit/form/TextBox",
	], 
	function(request,registry,parser,dom,on,query,number,Standby) {
		var entityClass = 'Utilidades Simple';
		parser.instantiate([dom.byId('GenerarInformeBtn_' + entityClass)]);
		//Modal to show its loading
		var standby = new Standby({target: 'utilidades_standby'});
		document.body.appendChild(standby.domNode);
		standby.startup();
		on(registry.byId('GenerarInformeBtn_' + entityClass),'click', function(e){
			var desde = registry.byId('fecha_pivot_1_' + entityClass).value.toISOString().split('T')[0];
			var hasta =  registry.byId('fecha_pivot_2_' + entityClass).value.toISOString().split('T')[0];
			var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta;
			standby.show(); 
			request('/getUtilidades?' + appendUrl,{handleAs:'json'}).then(function(response) {
				response = response.records;
				registry.byId('utilidades_ventas').set('value',number.format(response.ventas,{pattern:'###,###.#'}));
				registry.byId('utilidades_costos_variables').set('value',number.format(response.costosVariables,{pattern:'###,###.#'}));
				registry.byId('utilidades_utilidad_bruta').set('value',number.format(response.utilidadBruta,{pattern:'###,###.#'}));
				registry.byId('utilidades_margen_bruto').set('value',number.format(response.margenBruto,{pattern:'#.#%'}));
				registry.byId('utilidades_costos_fijos').set('value',number.format(response.costosFijos,{pattern:'###,###.#'}));
				registry.byId('utilidades_utilidad_neta').set('value',number.format(response.utilidadNeta,{pattern:'###,###.#'}));
				registry.byId('utilidades_margen_neto').set('value',number.format(response.margenNeto,{pattern:'#.#%'}));
				standby.hide();
			});		
		});
		registry.byId('standby_centerPane').hide();
	});