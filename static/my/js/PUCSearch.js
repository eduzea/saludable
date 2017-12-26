//# sourceURL=../static/js/my/PUCSearch.js

require([ 'dijit/registry', 'dojo/store/Memory', 'dojo/request',
		"dijit/form/FilteringSelect", 'dojo/domReady!' ], function(registry,
		Memory, request, FilteringSelect) {
	//LOAD PUC
	var pucStore;
	request('/getPUC', {
		handleAs : 'json'
	}).then(function(response) {
		pucStore = new Memory({
			data : response,
			idProperty : 'pucnumber'
		});
		var subcuentaStore = new Memory({
			data : pucStore.query({
				pucnumber : new RegExp("^[0-9]{6}$")
			}),
			idProperty : 'pucnumber'
		});
		var subcuentaSelect = new FilteringSelect({
			id : "subcuentaSelect",
			name : "Subcuenta",
			value : "510506",
			store : subcuentaStore,
			searchAttr : "Subcuenta_Nombre",
			queryExpr : "*${0}*",
			autoComplete : false
		}, "subcuentaSelect");
		subcuentaSelect.startup();

		var claseStore = new Memory({
			data : pucStore.query({
				pucnumber : new RegExp("^[0-9]{1}$")
			}),
			idProperty : 'pucnumber'
		});
		var claseSelect = new FilteringSelect({
			id : "claseSelect",
			name : "Clase",
			value : "5",
			store : claseStore,
			searchAttr : "Clase_Nombre"
		}, "claseSelect");
		claseSelect.startup();

		var grupoStore = new Memory({
			data : pucStore.query({
				pucnumber : new RegExp("^[0-9]{2}$")
			}),
			idProperty : 'pucnumber'
		});
		var grupoSelect = new FilteringSelect({
			id : "grupoSelect",
			name : "Grupo",
			value : "51",
			store : grupoStore,
			searchAttr : "Grupo_Nombre"
		}, "grupoSelect");
		grupoSelect.startup();

		var cuentaStore = new Memory({
			data : pucStore.query({
				pucnumber : new RegExp("^[0-9]{4}$")
			}),
			idProperty : 'pucnumber'
		});
		var cuentaSelect = new FilteringSelect({
			id : "cuentaSelect",
			name : "Cuenta",
			value : "5105",
			store : cuentaStore,
			searchAttr : "Cuenta_Nombre"
		}, "cuentaSelect")
		cuentaSelect.startup();

		subcuentaSelect.onChange = function(subcuenta) {
			subcuentaRecord = subcuentaSelect.store.query({
				'pucnumber' : subcuenta
			})[0];
			cuentaSelect.set('value', subcuentaRecord['Cuenta']);
			grupoSelect.set('value', subcuentaRecord['Grupo']);
			claseSelect.set('value', subcuentaRecord['Clase']);
		}

	});
	registry.byId('standby_centerPane').hide();
});
