require(['dojo/store/Memory', 'gridx/Grid', 'gridx/core/model/cache/Sync', 'dojo/request'], function(Store, Grid, Cache, request) {
	request('/clientData').then(function(data) {
		var store = new Store({
			'data' : JSON.parse(data)
		});
		var columns = [
			{ field : 'nombre', name : 'Nombre'},
			{ field : 'ciudad', name : 'Ciudad'},
			{ field : 'direccion', name : 'Direccion'},
			{ field : 'telefono', name : 'Telefono'},
			{ field : 'nit', name : 'NIT'},
			{ field : 'diasPago', name : 'Dias para pago'}
		];
		var grid = new Grid({
			cacheClass : Cache,
			store : store,
			structure : columns
		}, 'gridNode');
		grid.startup();
	}, function(error) {
		console.log("An errror occurred " + error);
	});

});
