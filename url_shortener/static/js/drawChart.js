google.charts.load('current', { 'packages': ['corechart'] });
	google.charts.setOnLoadCallback(drawChart);

	function drawChart() {

		var data = google.visualization.arrayToDataTable([
			['Short URL', 'Hits'],
			{% for obj in url %}
	['{{ obj['short_url']['S'] }}', {{ obj['hits']['N'] }}],

		{% endfor %}
		]);

	var options = {
		title: 'Statistics Per URL',
		is3D: true
	};

	var chart = new google.visualization.PieChart(document.getElementById('graph'));

	chart.draw(data, options);
	}