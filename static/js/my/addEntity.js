//# sourceURL=../static/js/my/addEntity.js
require(['dojo/request', 'dojo/dom', 'dojo/_base/fx', 'dijit/registry', 'dojo/dom-style','dojox/html/entities','dojo/on', 
		 'dojo/parser','dojo/query','dojo/json','dojo/topic','dojo/json','dojo/store/Memory','dojo/dom-class',"dojo/number",
		 'gridx/Grid', 'dijit/form/Button', 'dijit/form/CheckBox', 'gridx/modules/CellWidget',
		 'dojo/domReady!'],
function(request, dom, fx, registry, domStyle, html, on, parser,query,JSON,topic,json, Memory, domClass, number, Grid, Button, Checkbox) {
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
		topic.subscribe(topicStr, selectDijit.listenerfunc);
	});
	
	//Utility func to serialize arrays to strings before passing to a grid
	function prepareForGrid(object){
		for (field in object){
			objStrings = [];
			if ( object[field] instanceof Array){
				object[field].forEach(function(item){
					objStrings.push(item.rotulo);					
				});
				object[field] = objStrings.toString();
			} 
		}
		return object;
	}
	
	//Save button
	on(buttons[entityClass], "click", function(e) {
		if (registry.byId('addEntityForm'+ '_' + entityClass).validate()) {
			//Get top form data
			var formdata = registry.byId('addEntityForm'+  '_' + entityClass).get('value');
			for(var key in formdata) {//In case the form has controls that return values as array (eg. checkbox)
			    if(formdata.hasOwnProperty(key)) {
			    	if (Array.isArray(formdata[key])){
        				formdata[key] = formdata[key].length > 0 ? formdata[key][0] : false;				    		
			    	}

    			}
			}
			formdata.entityClass = entityClass;
			//Get data from repeated Key fields, if any
			var propNodes = query('.listBtn'); //since we are using button to attach list of selected key values
			if(propNodes.length > 0){
				propNodes.forEach(function(node){
					var id = node.getAttribute('widgetid');
					var propname = id.replace('_Btn_list','');
					var button = registry.byId(id);
					formdata[propname]= json.stringify(button.items); 	
				});
			}
			
			//Get data from grids, if any
			var grids = query('div[id^=grid_]div[id$=' + entityClass + ']');
			grids.forEach(function(grid){
				var store = registry.byNode(grid).store;
				var field = grid.id.replace('grid_','');//server expects field_parent...
				formdata[field] = json.stringify(store.query());
			});
			request.post('/saveEntity', {
				data : formdata,
				handleAs: 'json'
			}).then(function(response) {
				var grid = registry.byId("gridNode"+  '_' + entityClass);
				var key = response.key;
				var response_user='';
				if (response.message == 'Created') {
					response.entity.id = key;
					grid ? grid.store.add(prepareForGrid(response.entity)) : '' ;
					response_user = 'Se creo nuevo ' + entityClass + ': ' + response.key;
				    topic.publish(entityClass.toUpperCase(), {'action':'ADD','label':response.entity.rotulo,'value':response.key});
				} else {
					if(grid){
						var row = grid.store.get(key);
						grid.store.remove(key);
						response.entity['id'] = key;
						grid.store.add(prepareForGrid(response.entity));
					}
					response_user = 'Se actualizo ' + entityClass + ': ' + response.key;
					topic.publish(entityClass.toUpperCase(), {'action':'UPDATE','label':response.entity.rotulo,'value':response.key});
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
					//Clear grids, if any
					var grids = query('div[id^=grid_]div[id$=' + entityClass + ']');
					grids.forEach(function(grid){
						grid = registry.byNode(grid);
						grid.model.clearCache();
						grid.model.store.setData([]);
        				grid.body.refresh();
        				if (entityClass in saludable.gridChangeFuncs)
								saludable.gridChangeFuncs[entityClass](grid);
					});
					
				}, 2000);
			});
		} else {
			alert('Formulario incompleto. Favor corregir.');
			return false;
		}
		return true;
	});
	//Set up Repeated Key properties, if any
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
	
	var getFormData = function(form,entityClass){
		var formdata = form.get('value');
		for (prop in formdata) {
			formdata[prop.replace('_' + entityClass, '')] = formdata[prop];
			delete formdata[prop];
		}
		return formdata;
	};
		
	//Set up Repeated Structured properties, if any
	var grids = query(".grid_"+entityClass);
	grids.forEach(function(grid){
		var field = grid.id.replace('grid_','').replace('_' + entityClass,'');
		var entityType = grid.getAttribute('model');
		request('/getColumns?entityClass=' + entityType, {handleAs:'json'}).then(function(response) {
			var columns = response['columns'];
			columns.forEach(function(column){
				if (column.type == 'Integer'){
					column.formatter=function(data){
						return number.format(data[this.field],{pattern:'###,###'});
					};
				}
			});
			var borrarColumn = { field : 'Borrar', name : '', widgetsInCell: true, width:'5em',
				onCellWidgetCreated: function(cellWidget, column){
	   				var btn = new Button({
						label : "Borrar",
						onClick : function() {
		                    var selectedRowId = cellWidget.cell.row.id;
							gridObj.store.remove(selectedRowId);
							gridObj.model.clearCache();
							gridObj.body.refresh();
							if (entityClass in saludable.gridChangeFuncs)
								saludable.gridChangeFuncs[entityClass](gridObj);
						}
					});
					btn.placeAt(cellWidget.domNode);
				},
			};
			columns.push(borrarColumn);
			entityType = grid.getAttribute('model');
			var gridObj = new Grid({
			store : new Memory(),
			structure : columns,
			modules : [	"gridx/modules/CellWidget",
						]
			}, 'grid_' + field + '_' + entityClass);
			gridObj.startup();
			gridObj.entityType = entityType;
			gridObj.entityKey = response.key;
			domClass.add(dom.byId(grid.id),'struct-grid');
			
			//Function To summarize grid
			gridObj.summarize = 	function(){
			    var store = this.store; 
			    var data = store.query();
			    var sumTotal=0;
			    data.forEach(function(entry){
			         sumTotal = sumTotal + saludable.gridSummaryFuncs[entityType](entry);
			    });
			    return sumTotal;
			};
			//To add objects to grid
			parser.instantiate([dom.byId(field + '_' + entityClass +  '_Btn')]);
			on(registry.byId(field + '_' + entityClass +  '_Btn'),'click',function(e){
				var form = registry.byId(field +  '_' + entityClass);
				if (!form.validate()){
					alert("'Cantidad' no puede estar vacio!");
					return;
				}
				var grid = registry.byId('grid_'+ field + '_' + entityClass);
				var formdata = getFormData(form, grid.entityType);
				var id = '';
				grid.entityKey.forEach(function(keypart){
					id += formdata[keypart];
				});
				var row = grid.store.get(id);
				if (row){
					grid.store.remove(id);	
				}
				formdata['id']=id;
				grid.store.add(formdata);
				if (entityClass in saludable.gridChangeFuncs)
					saludable.gridChangeFuncs[entityClass](grid);
			});
		});
	});
	
	parser.instantiate([dom.byId('addEntityForm'+ '_' + entityClass)]);
	var form = registry.byId('addEntityForm'+ '_' + entityClass);
	form.listenerfunc = function(data){
        var nodelist= query('[id*='+ entityClass +']', 'addEntityForm'+ '_' + entityClass);
        if (nodelist.length == 0){
        	var contentPane= registry.byId(grid.gridName + '_add');
			contentPane.set("onDownloadEnd", function(){
				nodelist= query('[id*='+ entityClass +']', 'addEntityForm'+ '_' + entityClass );
				parser.instantiate(nodelist);
				fillForm(nodelist, data, entityClass);	
			});
        }else{
    		fillForm(nodelist, data, entityClass);
        }
	};
	topic.subscribe('EDIT_'+ entityClass.toUpperCase(), form.listenerfunc);
	
	if (entityClass in saludable.addEntityFuncs)
					saludable.addEntityFuncs[entityClass]();
	
	
	var fillForm = function(nodelist, rowData, entityClass){
		nodelist.forEach(function(node, index, array){
			var dijit = registry.byId(node.id);
			if (dijit){
				if (dijit.id.indexOf("grid") > -1 ){
					request('/getDetails?key=' + rowData['id'] + '&entityClass=' + entityClass, {handleAs:'json'}).then(function(response)
					 {
						dijit.model.clearCache();
						dijit.model.store.setData([]);//dijit.model.store.setData(items) //should work but its not calling onCellWidgetCreated!
						response.forEach(function(item){
							dijit.store.add(item);								
						});
						dijit.body.refresh();
						if (dijit.updateTotal){
							dijit.total = dijit.updateTotal();	
						}
						if (dom.byId('numero_' + entityClass)){
							dom.byId('numero_' + entityClass).innerHTML = rowData.numero;							
						}
						if (entityClass in saludable.gridChangeFuncs)
							saludable.gridChangeFuncs[entityClass](dijit);
					});
				}else{
					var id = dijit.id;
		        	if (id.indexOf(entityClass + "_Btn_list") > -1){//For key fields that are lists
		        		var field = id.replace('_' + entityClass + '_Btn_list','');
		        		//Find the button, fill the items list
		        		var button = registry.byId(field + '_' + entityClass + '_Btn_list');
		        		button.items = rowData['text' + field].split(';').filter(function(element) { return element; });
		        		//Find the list, populate it
		        		var listName = field + '_' + entityClass + '_list';
		        		$('#'+listName).empty();
		        		button.items.forEach(function(item){
		        			$('<div><input name="toDoList" type="checkbox">' + item + '</input></div>').appendTo('#'+listName);		        			
		        		});
	
		        	}
		        	id= dijit.id.replace('_' + entityClass,''); 
		        	if(id in rowData){
		        		if (rowData[id] instanceof Array){//If a list, take first only...
		        			rowData[id]=rowData[id][0];
		        		}
		        		if (dijit instanceof Checkbox){
		        			dijit.set('checked', rowData[id]);
		        		}else{
			        		dijit.set('value', getValueFromLabel(dijit,rowData[id]),false);
			        		dijit.set("displayedValue", rowData[id],false);		        			
		        		}
		        	}
		        		   				
				}			
			}
    	});
    };
  
	var getValueFromLabel = function(dijit, label){
		if (!dijit.options){
			return label;
		} 
		var options = dijit.getOptions();
		var lookup = {};
		for (var i = 0, len = options.length; i < len; i++) {
			lookup[html.decode(options[i].label)] = options[i].value;
		}
		if (label in lookup){
			return lookup[label];	
		}else{
			dijit.addOption({label:label.replace('.',' '),selected:true, value:label.replace(' ','.')});
		}
	return label;
	};
	registry.byId('standby_centerPane').hide();
});

