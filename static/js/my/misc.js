define(['dojo/request','dojo/dom',"dojo/_base/fx","dijit/registry","dojo/dom-style"], 
   function (request,dom,fx,registry,domStyle) {
   	send2server = function(formdata) {
     request.post("addClient", {data: formdata}).then(function(response){
		var grid = registry.byId("gridNode");
		if(response == 'Created'){
			var id = formdata.nombre.replace(/\s+/g, '');
			formdata['id']=id;
			grid.store.add(formdata);
			response = 'Se creo nuevo cliente: ' + formdata['nombre']; 	
		}else{
			var id = formdata.nombre.replace(/\s+/g, '');
			var row = grid.store.get(id);
			grid.store.remove(id);
			formdata['id']=id;
			grid.store.add(formdata);
			response = 'Se actualizo cliente: ' + formdata['nombre'];
		}
		dom.byId('server_response').innerHTML = response;
		setTimeout(function(){dom.byId('reset').click();dom.byId('server_response').innerHTML = '';},1000);
    });
      };
    return {'send2server' : send2server};
});

