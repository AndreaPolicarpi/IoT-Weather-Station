
$(document).ready(function(){
  var jsonData = JSON.parse(document.querySelector('#jsonData').getAttribute('data-json'));
  console.log(jsonData)
  var time = jsonData.map((item) => item.time);
  var temperature = jsonData.map((item) => item.temperature);
  var humidity = jsonData.map((item) => item.humidity);
  console.log(time)
  console.log(temperature)
  console.log(humidity)

  var trace1 = {
    type: "scatter",
    mode: "lines",
    name: 'Actual temperature',
    x: time,
    y: temperature,
    line: {color: '#17BECF'}
  }

  //  per previsioni
  var trace2 = {
    type: "scatter",
    mode: "lines",
    name: 'AAPL Low',
    x: time,
    y: humidity,
    line: {color: '#7F7F7F'}
  }

  var data_temp = [trace1];
  var data_hum = [trace2];

  var layout_temp = {
    title: 'Temperature',
    width: 800,
    height: 300,
    margin: {
      l: 70,
      r: 10,
      b: 35,
      t: 60,
      pad: 0
    },
    xaxis: {
      autorange: true,
      range: [time[0], time[-1]],
      rangeslider: {range: [time[0], time[-1]]},
      type: 'date'
    },
    yaxis: {
      autorange: true,
      range: [0.0, 50.0],
      type: 'linear'
    }
  };

  var layout_hum = {
    title: 'Humidity',
    width: 800,
    height: 300,
    margin: {
      l: 70,
      r: 10,
      b: 35,
      t: 60,
      pad: 0
    },
    xaxis: {
      autorange: true,
      range: [time[0], time[-1]],
      rangeslider: {range: [time[0], time[-1]]},
      type: 'date'
    },
    yaxis: {
      autorange: true,
      range: [0.0, 50.0],
      type: 'linear'
    }
  };

  var config = {responsive: true}

  Plotly.newPlot('temperature_chart', data_temp, layout_temp, config);
  Plotly.newPlot('humidity_chart', data_hum, layout_hum, config);
});