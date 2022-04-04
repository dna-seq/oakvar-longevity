widgetGenerators['longevitymap'] = {
	'variant': {
		'width': 500, 
		'height': 150, 
		'function': function (div, row, tabName) {
            var info = getWidgetData(tabName, 'longevitymap', row, 'info');
            if (info == null || info == '') {
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
						
			var rows = info.split("____");
			for (var r = 0; r < rows.length;r++){
				var row = rows[r].split("__");
				var tr = getWidgetTableTr(row);
				addEl(tbody, tr);
				
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
