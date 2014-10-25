require(['dojo/request', 'dojo/dom', 'dojo/_base/fx', 'dijit/registry', 'dojo/dom-style', 'dojo/on', 'dojo/parser'], function(request, dom, fx, registry, domStyle, on, parser) {
	parser.instantiate([dom.byId('agregar_btn2')]);
	var myBut = registry.byId('agregar_btn2');
	on(myBut, "click", function(e) {
		if (registry.byId("myForm2").validate()) {
			var formdata = registry.byId("myForm2").getValues();
			request.post("/saveClient", {
				data : formdata
			}).then(function(response) {
				var grid = registry.byId("gridNode");
				if (response == 'Created') {
					var id = formdata.nombre.replace(/\s+/g, '');
					formdata['id'] = id;
					grid.store.add(formdata);
					response = 'Se creo nuevo cliente: ' + formdata['nombre'];
				} else {
					var id = formdata.nombre.replace(/\s+/g, '');
					var row = grid.store.get(id);
					grid.store.remove(id);
					formdata['id'] = id;
					grid.store.add(formdata);
					response = 'Se actualizo cliente: ' + formdata['nombre'];
				}
				dom.byId('server_response2').innerHTML = response;
				setTimeout(function() {
					dom.byId('reset2').click();
					dom.byId('server_response2').innerHTML = '';
				}, 1000);
			});
		} else {
			alert('Formulario incompleto. Favor corregir.');
			return false;
		}
		return true;
	});
});

