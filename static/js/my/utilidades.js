//# sourceURL=../static/js/my/utilidades.js

require([
	'dojo/request',
	"dijit/registry",
	'dojo/parser',
	'dojo/dom','dojo/on',
	'dojo/query',
	"dojox/widget/Standby",
	'dojo/dom-construct'], 
	function(request,registry,parser,dom,on,query,Standby,domConstruct) {
		var entity_class = 'Utilidades';
		parser.instantiate([dom.byId('GenerarInformeBtn_' + entity_class)]);
		//Modal to show its loading
		var standby = new Standby({target: 'utilidades.html'});
		document.body.appendChild(standby.domNode);
		standby.startup();
		on(registry.byId('GenerarInformeBtn_' + entity_class),'click', function(e){
			var desde = registry.byId('fecha_pivot_1_' + entity_class).value.toISOString().split('T')[0];
			var hasta =  registry.byId('fecha_pivot_2_' + entity_class).value.toISOString().split('T')[0];
			var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta;
			standby.show(); 
			request('/getUtilidades?' + appendUrl /*,{handleAs:'json'}*/).then(function(response) {
				var records = response.records;
				console.log(records);
				standby.hide();
			});		
		});
		registry.byId('standby_centerPane').hide();
	});