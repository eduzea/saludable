define(['dojo/request'], 
   function (request) {
   	send2server = function(formdata) {
     request.post("addClient", {data: formdata}).then(function(text){
        console.log("The server returned: ", text);
    });
      };
    return {'send2server' : send2server};
});

