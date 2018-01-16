//# sourceURL=../static/js/my/showEntities.js
require(['my/myGrid',
		 'dojo/store/JsonRest',
		 'dijit/registry',
		 'dojo/query',
		 'dojo/parser',
		 'dojo/dom',
		 "dojo/dom-construct",
		 'dojox/html/entities',
		 "dojo/number",
		 "dojo/on",
		 'dojo/topic',
		 "dojox/widget/Standby",
		 'dijit/form/SimpleTextarea',
		 'dijit/form/CheckBox'], 
function(MyGrid, JsonRest, registry, query, parser, dom, domConstruct, html, number, on,topic,Standby) {
	
	var entityClass = saludable.entityClass;

	var jsonRest = new JsonRest({
		target: '/entityData?',
		sortParam: "sortBy",
	});
	jsonRest.more = true;
	jsonRest.nextCursor = '';

	var grid = new MyGrid(
		{	'gridName':entityClass,
			'targetNode': 'gridNode_' + entityClass,
			'columnsURL': '/getColumns?entityClass=' + entityClass,
			'borrar':true,
			'editar':true,
			'pageSize' : 100,
			'callback': function(){//put here anything that needs to happen after the grid is init.
				//GET INIT DATA
				grid = grid.grid();
				var nextCursor = '';
				getNextPage('',grid.pageSize);
				var moreButton = grid.dataFetchTrigger();
				moreButton.onclick = function(){
					if(jsonRest.more){
						getNextPage(jsonRest.nextCursor,grid.pageSize);	
					}else{
						this.innerHTML='';
					}
				};
				saludable.showEntitiesFuncs[entityClass]();
			}
		}
	);

	
	//FUNCTION TO GET DATA ONE PAGE AT A TIME
	var getNextPage = function(cursor, count){
		registry.byId('standby_centerPane').show();
		jsonRest.query( {'entityClass':entityClass,'count':count,'cursor':cursor},
						{start: 0, count: count,
							 sort: [{ attribute: '', descending: true }]//sort field will be determined in the server...
							 }
		).then(function(response){
			grid.appendData(response.records);
  			jsonRest.nextCursor = response.cursor;
  			jsonRest.more = response.more;
  			registry.byId('standby_centerPane').hide();
		});
	};
	
});
