//# sourceURL=../static/js/my/addEntity.js
require(['dojo/request', 'dojo/dom', 'dojo/_base/fx', 'dijit/registry', 'dojo/dom-style', 'dojo/on', 
		 'dojo/parser','dojo/query','dojo/json','dojo/topic','dojo/json',
		 'dojo/domReady!'],//Modules required to avoid race condition when parsing 
function(request, dom, fx, registry, domStyle, on, parser,query,JSON,topic,json) {
	var entity_class = saludable.entity_class;
	parser.instantiate([dom.byId('agregar_btn' + entity_class)]);
	var buttons={};
	buttons[entity_class] =  registry.byId('agregar_btn' + entity_class);
	on(buttons[entity_class], "click", function(e) {
		var entity_class = saludable.entity_class; 
		if (registry.byId('addEntityForm'+ entity_class).validate()) {
			var formdata = registry.byId('addEntityForm'+ entity_class).get('value');
			formdata.entity_class = entity_class;
			proplistdata = {};
			var propNodes = query('.listpropTextarea'); 
			if(propNodes){
				propNodes.forEach(function(node){
					var propname = node.id.replace(entity_class,'').replace('text','');
					var textarea = registry.byId(node.id);
					proplistdata[propname]=textarea.value; 	
				});
				formdata.proplistdata = json.stringify(proplistdata);
			}
			request.post('/saveEntity', {
				data : formdata,
				handleAs: 'json'
			}).then(function(response) {
				var grid = registry.byId("gridNode"+ entity_class);
				var key = response.key;
				var response_user='';
				if (response.message == 'Created') {
					response.entity['id'] = key;
					grid ? grid.store.add(response.entity) : '' ;
					response_user = 'Se creo nuevo ' + entity_class + ': ' + response.key;
				    topic.publish(entity_class, { key: key });
				} else {
					if(grid){
						var row = grid.store.get(key);
						grid.store.remove(key);
						response.entity['id'] = key;
						grid.store.add(response.entity);
					}
					response_user = 'Se actualizo ' + entity_class + ': ' + response.key;
				}
				dom.byId('server_response'+ entity_class).innerHTML = response_user;
				setTimeout(function() {
					dom.byId('reset'+ entity_class).click();
					dom.byId('server_response'+ entity_class).innerHTML = '';
				}, 3000);
				numero = registry.byId('numero'+entity_class);
				if (numero){
					value = numero.value;
					numero.set('value',value + 1);	
				}
			});
		} else {
			alert('Formulario incompleto. Favor corregir.');
			return false;
		}
		return true;
	});
	var listpropBtns = query(".listprop");
	parser.instantiate(listpropBtns);
	listpropBtns.forEach(function(buttonNode){
		button = registry.byId(buttonNode.id);
		var propname = button.id.split('_')[1];
		if (button.id.search('Agregar') != -1){
			on(button,"click",function(e){
				bienoservicio = registry.byId(propname + entity_class).value;
				var textarea = registry.byId('text' + propname + entity_class);
				var text = textarea.value + bienoservicio +'; ';
				textarea.set('value',text);
			});	
		}else{
			on(button,"click",function(e){
			bienoservicio = registry.byId(propname + entity_class).value;
			var textarea = registry.byId('text' + propname + entity_class);
			var text = textarea.value.replace(bienoservicio+';','').trim();
			textarea.set('value',text);
		});
		}
	});
});

