//# sourceURL=../static/js/my/estadoDeResultados.js

require([
	'dojo/request',
	"dijit/registry",
	'dojo/parser',
	'dojo/dom',
	'dojo/on',
	'dojo/query',
	"dojo/number",
	"dojo/store/Memory",
	 'dijit/form/Button',
	 'gridx/Grid',
	 'dojo/dom-style',
	 "dijit/layout/ContentPane",
	 "dojo/dom-construct",
	 "dojo/query",
	 "dojo/dom",
	 "dojo/dom-attr",
	 //Gridx modules
	 'gridx/modules/CellWidget',
	 //End gridx modules
],function(request,registry,parser,dom,on,query,number,Memory,Button,Grid,domStyle, ContentPane,domConstruct,query,dom, attr) {	

	parser.instantiate([dom.byId('GenerarInformeBtn_estadoDeResultados')]);
	var numFormatter=function(data){
		if (data.id.indexOf('Margen')!==-1){
			return number.format(data[this.field],{pattern:'#.#%'});
		}else{
			return number.format(data[this.field],{pattern:'###,###'});			
		}
	};
	
	var config = {
		'Ventas': {
				rows : ["cliente","producto"],
				vals : ["total"],
				aggregatorName:'Suma'
		},
		'Gastos':{
					rows: ['bienoservicio'],
					vals: ['total'],
					exclusions:{},
					hiddenAttributes:[],
					aggregatorName:'Suma'
		},
		'Gastos No Operacionales':{
			rows: ['bienoservicio', 'detalle'],
			vals: ['total'],
			exclusions:{},
			hiddenAttributes:[],
			aggregatorName:'Suma'
		}
	}
	
	//Set up resumen grid
	var resumenColumns = [
		{id:'cuenta', field:'cuenta', name:'Cuenta',style:"text-align: left; font-weight: bold;", width:'12em'},
		{id:'monto', field:'monto', name:'Valor',style:"text-align: right", width:'6em', formatter: numFormatter}
	];
								
	var clearTabs = function(tabContainerId, string){
		var tc = registry.byId(tabContainerId);
		var cps = tc.getChildren();
		cps.forEach(function(cp){
			if (cp.id.indexOf(string) != -1){
				tc.removeChild(cp);
				cp.destroy();
			}
		});
		tc.tabRegister={};
	}

	
	var addTab = function(detalleId) {
		var cp = new ContentPane({
						id:'tab_estadoDeResultados'+detalleId,
						title:detalleId,
            			closable:false,
            			selected:true,
            			content: '<div class = "pivot" id="pivot_' + detalleId +'" style="margin: 10px;"></div>'
            			})
		var tc = registry.byId('widget_estadoDeResultados')
		tc.addChild(cp);
		tc.tabRegister[detalleId]=cp;
		tc.selectChild(cp);
    };

    
	var detalleColumn = { field : 'detalle', name : '', widgetsInCell: true, width:'5em',
	onCellWidgetCreated: function(cellWidget, column)
		{
			var btn = new Button({
				label : "Detalle",
				onClick : function() {
                    var selectedRowId = cellWidget.cell.row.id;
                    var rowData = resumenGrid.row(selectedRowId, true).rawData();                    
                    var tc = registry.byId('widget_estadoDeResultados'); 
                    if (typeof tc.tabRegister == "undefined"){
            			registry.byId('widget_estadoDeResultados').tabRegister = {};
            		}
            		if  (rowData.id in tc.tabRegister){
            			var cp = registry.byId('tab_estadoDeResultados'+rowData.id);
            			tc.selectChild(cp);
            			return
            		};
            		addTab(rowData.id);
                    registry.byId('standby_centerPane').show();
            		var desde = registry.byId('fecha_pivot_1_estadoDeResultados').value.toISOString().split('T')[0];
            		var hasta = registry.byId('fecha_pivot_2_estadoDeResultados').value.toISOString().split('T')[0];
            		var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta;
            		registry.byId('standby_centerPane').show();
                    request("getDetalleEstadoDeResultados?cuenta=" + encodeURIComponent(rowData.id) + appendUrl,
                    		{handleAs:'json'}).then(
                    	function(response){
            				var detalleId = rowData.id;
                    		var cuentaConfig = '';
                    		if (detalleId in config){
                    			cuentaConfig = detalleId;
                    		}else{
                    			cuentaConfig = (detalleId == 'Ingresos Operacionales') ? 'Ventas' : 'Gastos';
                    		}
                    		$(function() {
                    			$("#pivot_estadoDeResultados").pivotUI(response, config[cuentaConfig],false,'es');
                			});
            				//It seems the jquery selector can only do its thing on divs in the mark-up, not the
            				//dojo created ones. Thus we have to create it first, and then move it to the desired
            				//location.
            				domConstruct.place('pivot_estadoDeResultados',dom.byId('pivot_'+detalleId),'replace');
                			attr.set('pivot_estadoDeResultados',{"id":'pivot_'+detalleId,'style':'margin: 10px;display:block' });
            				domConstruct.create('div',{'id': 'pivot_estadoDeResultados','style':'margin: 10px;display:none'},'estadoDeResultados_resumen','first');
                			registry.byId('standby_centerPane').hide();
						});
				}
			});
			btn.placeAt(cellWidget.domNode);
		},
	setCellValue: function(gridData, storeData, cellWidget){
		if(cellWidget.cell.row.id.indexOf('Utilidad') !== -1 || cellWidget.cell.row.id.indexOf('Margen') !== -1 ){
			domStyle.set(cellWidget.domNode, 'visibility', 'hidden');
			}
		}
	};
	resumenColumns.push(detalleColumn);

	var gridProps = 
	 {
		store : new Memory(),
		structure: resumenColumns,
		modules: [
         	"gridx/modules/CellWidget",
	    ]
	 };
	var resumenGrid = new Grid(gridProps, 'estadoDeResultados_resumen_grid');
	resumenGrid.startup();	

	registry.byId('standby_centerPane').hide();
	
	//Date range selection and report data fetching functionality
	on(registry.byId('GenerarInformeBtn_estadoDeResultados'),'click', function(e){
		var desde = registry.byId('fecha_pivot_1_estadoDeResultados').value.toISOString().split('T')[0];
		var hasta =  registry.byId('fecha_pivot_2_estadoDeResultados').value.toISOString().split('T')[0];
		var appendUrl = '&fechaDesde=' + desde +'&fechaHasta=' + hasta;
		registry.byId('standby_centerPane').show();
		request('/getEstadoDeResultados?' + appendUrl,{handleAs:'json'}).then(function(response) {
			var resumenStore = new Memory({data: response.records});
			resumenGrid.model.clearCache();
			resumenGrid.model.setStore(resumenStore)
            resumenGrid.body.refresh();
			clearTabs('widget_estadoDeResultados', 'tab_estadoDeResultados');
			registry.byId('standby_centerPane').hide();
		});		
	});
	registry.byId('standby_centerPane').hide();
});