define(['dojo/request','dojo/dom',"dojo/_base/fx"], 
   function (request,dom,fx) {
   	send2server = function(formdata) {
     request.post("addClient", {data: formdata}).then(function(response){
        dom.byId('server_response').innerHTML = response;
      	fx.fadeOut({node: "server_response", duration: 3000}).play();
		setTimeout(function(){dom.byId('reset').click();},3000);
    });
      };
    return {'send2server' : send2server};
});

