//# sourceURL=../static/js/my/pYg.js

require([
	'dojo/request',
	"dijit/registry",
	'dojo/parser',
	'dojo/dom','dojo/on',
	'dojo/query',
	"dojox/widget/Standby",
	'dojo/dom-construct'], 
	function(request,registry,parser,dom,on,query,Standby,domConstruct) {
		var entityClass = saludable.entityClass;
		parser.instantiate([dom.byId('GenerarInformeBtn_' + entityClass)]);
		//Modal to show its loading
		var standby = new Standby({target: 'PyG_/pYg.html'});
		document.body.appendChild(standby.domNode);
		standby.startup();
		on(registry.byId('GenerarInformeBtn_' + entityClass),'click', function(e){
			var desde = registry.byId('fecha_pivot_1_' + entityClass).value.toISOString().split('T')[0];
			var hasta =  registry.byId('fecha_pivot_2_' + entityClass).value.toISOString().split('T')[0];
			var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta;
			standby.show(); 
			request('/getPyG?' + appendUrl /*,{handleAs:'json'}*/).then(function(response) {//Two options: get data and build view in JS or get template from python
				//var records = response.records;
				//console.log(records);
				domConstruct.place(response,'output_PyG','only');
				standby.hide();
			});		
		});
		registry.byId('standby_centerPane').hide();
	});