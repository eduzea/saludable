//# sourceURL=../static/js/my/addEntity.js
require(['dojo/request', 'dojo/dom', 'dojo/_base/fx', 'dijit/registry', 'dojo/dom-style', 'dojo/on', 
		 'dojo/parser','dojo/query','dojo/json','dojo/topic','dojo/json','dojo/store/Memory',
		 'dojo/domReady!'],
function(request, dom, fx, registry, domStyle, on, parser,query,JSON,topic,json, Memory) {
	var entity_class = saludable.entity_class;
	parser.instantiate([dom.byId('agregar_btn' + '_' + entity_class)]);
	var buttons={};
	buttons[entity_class] =  registry.byId('agregar_btn' + '_' + entity_class);
	//Register select buttons to listen to topics
	var selects = query("[data-dojo-type='dijit/form/Select']");
	parser.instantiate(selects);
	selects.forEach(function(element){
		var selectDijit = registry.byId(element.id);
		selectDijit.listenerfunc = function(data){
			if (data.action == 'ADD'){
				selectDijit.addOption({ disabled:false, label:data.label, selected:true, value:data.value});
    			var store = new Memory({data: selectDijit.options});
    			var sorted = store.query({},{sort: [{ attribute: "label"}]});
    			selectDijit.options = sorted;
    			selectDijit.set("value",sorted[0].value);	
			}else if (data.action == 'DELETE'){
				selectDijit.removeOption(data.value);	
			}
    	};
		var topicStr = element.id.substring(0,element.id.lastIndexOf( '_' + entity_class)).toUpperCase();
		console.log(selectDijit.id + ' SUBSCRIBING TO TOPIC:' + topicStr);
		topic.subscribe(topicStr, selectDijit.listenerfunc);
	});

	on(buttons[entity_class], "click", function(e) {
		var entity_class = saludable.entity_class; 
		if (registry.byId('addEntityForm'+ '_' + entity_class).validate()) {
			var formdata = registry.byId('addEntityForm'+  '_' + entity_class).get('value');
			formdata.entity_class = entity_class;
			proplistdata = {};
			var propNodes = query('.listpropTextarea'); 
			if(propNodes){
				propNodes.forEach(function(node){
					var propname = node.id.replace('_' + entity_class,'').replace('text','');
					var textarea = registry.byId(node.id);
					proplistdata[propname]=textarea.value; 	
				});
				formdata.proplistdata = json.stringify(proplistdata);
			}
			request.post('/saveEntity', {
				data : formdata,
				handleAs: 'json'
			}).then(function(response) {
				var grid = registry.byId("gridNode"+  '_' + entity_class);
				var key = response.key;
				var response_user='';
				if (response.message == 'Created') {
					grid ? grid.store.add(response.entity) : '' ;
					response_user = 'Se creo nuevo ' + entity_class + ': ' + response.key;
				    topic.publish(entity_class.toUpperCase(), {'action':'ADD','label':response.entity.rotulo,'value':response.key});
				} else {
					if(grid){
						var row = grid.store.get(key);
						grid.store.remove(key);
						response.entity['id'] = key;
						grid.store.add(response.entity);
					}
					response_user = 'Se actualizo ' + entity_class + ': ' + response.key;
				}
				dom.byId('server_response'+ '_' + entity_class).innerHTML = response_user;
				setTimeout(function() {
					numero = registry.byId('numero'+ '_' + entity_class);
					dom.byId('reset'+ '_'+ entity_class).click();
					dom.byId('server_response'+  '_' + entity_class).innerHTML = '';
					if (numero){
						value = numero.value;
						numero.set('value', value + 1);	
					}
				}, 3000);
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
		var propname = button.id.split('_')[2];
		if (button.id.search('Agregar') != -1){
			on(button,"click",function(e){
				bienoservicio = registry.byId(propname +  '_' + entity_class).attr('displayedValue');
				var textarea = registry.byId('text' + propname + '_' + entity_class);
				var text = textarea.value + bienoservicio +';';
				textarea.set('value',text);
			});	
		}else{
			on(button,"click",function(e){
			bienoservicio = registry.byId(propname + '_' + entity_class).attr('displayedValue');
			var textarea = registry.byId('text' + propname +  '_' + entity_class);
			var text = textarea.value.replace(bienoservicio + ';','').trim();
			textarea.set('value',text);
		});
		}
	});
});

