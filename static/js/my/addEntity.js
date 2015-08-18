//# sourceURL=../static/js/my/addEntity.js
require(['dojo/request', 'dojo/dom', 'dojo/_base/fx', 'dijit/registry', 'dojo/dom-style', 'dojo/on', 
		 'dojo/parser','dojo/query','dojo/json','dojo/topic','dojo/json','dojo/store/Memory',
		 'dojo/domReady!'],
function(request, dom, fx, registry, domStyle, on, parser,query,JSON,topic,json, Memory) {
	var entityClass = saludable.entity_class;
	parser.instantiate([dom.byId('agregar_btn' + '_' + entityClass)]);
	var buttons={};
	buttons[entityClass] =  registry.byId('agregar_btn' + '_' + entityClass);
	//Register select  to listen to topics
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
		var topicStr = element.id.substring(0,element.id.lastIndexOf( '_' + entityClass)).toUpperCase();
		console.log(selectDijit.id + ' SUBSCRIBING TO TOPIC:' + topicStr);
		topic.subscribe(topicStr, selectDijit.listenerfunc);
	});

	on(buttons[entityClass], "click", function(e) {
		if (registry.byId('addEntityForm'+ '_' + entityClass).validate()) {
			var formdata = registry.byId('addEntityForm'+  '_' + entityClass).get('value');
			formdata.entityClass = entityClass;
			proplistdata = {};
			var propNodes = query('.listBtn'); //since using button to attach list of selected key values
			if(propNodes.length > 0){
				propNodes.forEach(function(node){
					var id = node.getAttribute('widgetid');
					var propname = id.replace('_' + entityClass + '_Btn','');
					var button = registry.byId(id);
					proplistdata[propname]=button.items; 	
				});
				formdata.proplistdata = json.stringify(proplistdata);
			}
			request.post('/saveEntity', {
				data : formdata,
				handleAs: 'json'
			}).then(function(response) {
				var grid = registry.byId("gridNode"+  '_' + entityClass);
				var key = response.key;
				var response_user='';
				if (response.message == 'Created') {
					grid ? grid.store.add(response.entity) : '' ;
					response_user = 'Se creo nuevo ' + entityClass + ': ' + response.key;
				    topic.publish(entityClass.toUpperCase(), {'action':'ADD','label':response.entity.rotulo,'value':response.key});
				} else {
					if(grid){
						var row = grid.store.get(key);
						grid.store.remove(key);
						response.entity['id'] = key;
						grid.store.add(response.entity);
					}
					response_user = 'Se actualizo ' + entityClass + ': ' + response.key;
				}
				dom.byId('server_response'+ '_' + entityClass).innerHTML = response_user;
				setTimeout(function() {
					numero = registry.byId('numero'+ '_' + entityClass);
					dom.byId('server_response'+  '_' + entityClass).innerHTML = '';
					if (numero){
						value = numero.value;	
					}
					dom.byId('reset'+ '_'+ entityClass).click();
					numero ? numero.set('value', value + 1):'';
				}, 2000);
			});
		} else {
			alert('Formulario incompleto. Favor corregir.');
			return false;
		}
		return true;
	});
	var listpropBtns = query(".listBtn");
	parser.instantiate(listpropBtns);
	listpropBtns.forEach(function(buttonNode){
		button = registry.byId(buttonNode.id);
		var propname = buttonNode.id.split('_')[0];
		var listName = propname + '_' + entityClass + '_list';
		button.items = [];
		on(button, 'click', function() {
			var toAdd=registry.byId(propname +'_'+ entityClass).value;
			if (button.items.indexOf(toAdd) == -1){
				button.items.push(toAdd);		
				$('<div><input name="toDoList" type="checkbox">' + toAdd + '</input></div>').appendTo('#'+listName);				
			}
		});
	    $('#'+listName).on('click','input',function() {
	    	var value = this.nextSibling.textContent;
	        var index = button.items.indexOf(value);
			if (index !== -1) {
    			button.items.splice(index, 1);
			}
			$(this).parent().remove();
	    });
	});	
});

