//# sourceURL=../static/js/my/addEntity.js
require(['dojo/request', 'dojo/dom', 'dojo/_base/fx', 'dijit/registry', 'dojo/dom-style', 'dojo/on', 
		 'dojo/parser','dojo/query','dojo/json',
		 "dijit/form/Form", "dijit/form/Button", "dijit/form/ValidationTextBox",'dojo/domReady!'],//Modules required to avoid race condition when parsing 
function(request, dom, fx, registry, domStyle, on, parser,query,JSON,form, button, valid) {
	entity_class = saludable.entity_class;
	parser.instantiate([dom.byId('agregar_btn' + entity_class)]);
	var buttons={};
	buttons[entity_class] =  registry.byId('agregar_btn' + entity_class);
	on(buttons[entity_class], "click", function(e) {
		entity_class = saludable.entity_class; 
		if (registry.byId('addEntityForm'+ entity_class).validate()) {
			var formdata = registry.byId('addEntityForm'+ entity_class).get('value');
			formdata.entity_class = entity_class;
			request.post('/saveEntity', {
				data : formdata,
				handleAs: 'json'
			}).then(function(response) {
				var grid = registry.byId("gridNode"+ entity_class);
				var key = response.key;
				var response_user='';
				for(prop in formdata){
					formdata[prop.replace(entity_class,'')]=formdata[prop];
					delete formdata[prop];
				}
				if (response.message == 'Created') {
					formdata['id'] = key;
					grid ? grid.store.add(formdata) : '' ;
					response_user = 'Se creo nuevo ' + entity_class + ': ' + response.key;
				} else {
					if(grid){
						var row = grid.store.get(key);
						grid.store.remove(key);
						formdata['id'] = key;
						grid.store.add(formdata);					
					}
					response_user = 'Se actualizo ' + entity_class + ': ' + response.key;
				}
				dom.byId('server_response'+ entity_class).innerHTML = response_user;
				setTimeout(function() {
					//dom.byId('reset'+ entity_class).click();
					dom.byId('server_response'+ entity_class).innerHTML = '';
				}, 3000);
			});
		} else {
			alert('Formulario incompleto. Favor corregir.');
			return false;
		}
		return true;
	});
});

