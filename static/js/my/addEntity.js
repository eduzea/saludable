require(['dojo/request', 'dojo/dom', 'dojo/_base/fx', 'dijit/registry', 'dojo/dom-style', 'dojo/on', 
		 'dojo/parser','dojo/query',
		 "dijit/form/Form", "dijit/form/Button", "dijit/form/ValidationTextBox",'dojo/domReady!'],//Modules required to avoid race condition when parsing 
function(request, dom, fx, registry, domStyle, on, parser,query,form, button, valid) {
	parser.instantiate([dom.byId('agregar_btn')]);
	var myBut = registry.byId('agregar_btn');
	on(myBut, "click", function(e) {
		parser.instantiate([dom.byId('myForm')]); 
		if (registry.byId("myForm").validate()) {
			var formdata = registry.byId("myForm").getValues();
			var handler = query(".handler");
			request.post(handler[0].id, {
				data : formdata
			}).then(function(response) {
				var grid = registry.byId("gridNode");
				var key = (formdata.nombre + formdata.negocio).replace(/\s+/g, '');
				if (response == 'Created') {
					formdata['id'] = key;
					grid.store.add(formdata);
					response = 'Se creo nuevo cliente: ' + formdata['nombre'] + ' ' + formdata['negocio'];
				} else {
					var row = grid.store.get(key);
					grid.store.remove(key);
					formdata['id'] = key;
					grid.store.add(formdata);
					response = 'Se actualizo cliente: ' + formdata['nombre'] + ' ' +  formdata['negocio'];
				}
				dom.byId('server_response').innerHTML = response;
				setTimeout(function() {
					dom.byId('reset').click();
					dom.byId('server_response').innerHTML = '';
				}, 1000);
			});
		} else {
			alert('Formulario incompleto. Favor corregir.');
			return false;
		}
		return true;
	});
});

