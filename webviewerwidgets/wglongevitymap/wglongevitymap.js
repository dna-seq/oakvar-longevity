widgetGenerators['longevitymap'] = {
	'variant': {
		'width': 500, 
		'height': 150, 
		'function': function (div, row, tabName) {
            var info = getWidgetData(tabName, 'longevitymap', row, 'info');
			var longevityId = null;
			if (info == null || info == '')
				longevityId = getWidgetData(tabName, 'longevitymap', row, 'longevitydb_id');
				
            if (longevityId == null && info == null) {
                var span = getEl('span');
                span.classList.add('nodata');
				addEl(div, addEl(span, getTn('No data')));
                return;
			}
						
			var table = getWidgetTableFrame();
			addEl(div, table);
			var thead = getWidgetTableHead(['Longevity ID', 'Association', 'Population', 'RSID', 'Gene', 'Pubmed ID'],
										   ['12%','20%', '28%', '11%', '15%', '14%']);
						
			addEl(table, thead);
			var tbody = getEl('tbody');
			addEl(table, tbody);
			function linkify(arr){
				return [arr[0], arr[1], arr[2],
						'https://www.snpedia.com/index.php/Rs'+arr[3],
						arr[4] == 'None' ? 'None' : 'https://genomics.senescence.info/longevity/gene.php?id='+arr[4],
						'https://pubmed.ncbi.nlm.nih.gov/'+arr[5]];
			};
			function subRow(arr){
				if (arr[4] == 'None')
					return [arr[3], arr[5]];
				else
					return [arr[3], arr[4], arr[5]];
			}
			
			function addRow(row, tbody){
				if (row[4].indexOf(',') != -1){
					var parts = row[4].split(',');
					for(var i in parts){
						row[4] = parts[i];
						var tr = getWidgetTableTr(linkify(row), subRow(row));
						addEl(tbody, tr);
					}
				} else {
					var tr = getWidgetTableTr(linkify(row), subRow(row));
					addEl(tbody, tr);
				}
			}
			
			if (longevityId != null){
				var row = [getWidgetData(tabName, 'longevitymap', row, 'longevitydb_id'),
							getWidgetData(tabName, 'longevitymap', row, 'association'),
							getWidgetData(tabName, 'longevitymap', row, 'population'),
							getWidgetData(tabName, 'longevitymap', row, 'rsid'),
							getWidgetData(tabName, 'longevitymap', row, 'genes'),
							getWidgetData(tabName, 'longevitymap', row, 'pmid')
				];
				addRow(row, tbody);
				
			} else {
				var rows = info.split("____");
				for (var r = 0; r < rows.length;r++){
					var row = rows[r].split("__");
					addRow(row, tbody);
					//var tr = getWidgetTableTr(linkify(row), subRow(row));
					//addEl(tbody, tr);
					
				}
			}
		
			addEl(div, addEl(table, tbody));
			
            //addInfoLine(div, 'Info', info, tabName);
		}
	},
	'info': {
		'width': 300, 
		'height': 300, 
		'function': function (div) {
			if (div != null) {
				emptyElement(div);
			}
            div.style.textAlign = 'center';
			var significant = 0;
			var nonSignificant = 0;
			var conflicted = 0;
			var d = infomgr.getData('variant'); 
			for (var i = 0; i < d.length; i++) {
				var row = d[i]; 
				var association = getWidgetData('variant', 'longevitymap', row, 'association'); 

				if (association == 'non-significant') {
					nonSignificant++;
				} else if(association == 'significant') {
                    significant++;
				} else {
					conflicted++;
				}
					
			}
			div.style.width = 'calc(100% - 37px)';
			var chartDiv = getEl('canvas');
			chartDiv.style.width = 'calc(100% - 20px)';
			chartDiv.style.height = 'calc(100% - 20px)';
			addEl(div, chartDiv);
			
			var chart = new Chart(chartDiv, {
				type: 'doughnut',
				data: {
					datasets: [{
						data: [
							significant,
							conflicted,
							nonSignificant
							
						],
						backgroundColor: [
							'#FF0000',
							'#00FF00',
							'#0000FF'
							],
					}],
					labels: [
						'Significant',
						'Conflicted',
						'Non-significant'
					]
				},
				options: {
					responsive: true,
                    responsiveAnimationDuration: 500,
                    maintainAspectRatio: false,
                    legend: {
                        position: 'bottom',
                    },
				}
			});
		}
	}
}
