//# sourceURL=../static/js/my/numeros.js
require(['dojo/request',"dijit/registry",'dojo/parser','dojo/dom','dojo/on'], 
function(request,registry,parser,dom,on) {
	var actualizarNumero = function(model, numero){
		var url = '/setNumero?tipo=' + model + '&numero=' + numero; 
		request(url).then(function(response) {
			dom.byId('numeroMsg').innerHTML = response;
		});
	};
	var numbers = ['Factura','Remision','Egreso','Deuda','OtrosIngresos','PagoRecibido'];
	numbers.forEach(function(model){
		parser.instantiate([dom.byId('num'+ model + 'Btn')]);
		parser.instantiate([dom.byId('numerox_' + model)]);
		var numBtn = registry.byId('num'+ model + 'Btn');
		on(numBtn,'click',function(){
			actualizarNumero(model,registry.byId('numerox_' + model).value);		
		});
	});
	registry.byId('standby_centerPane').hide();
});