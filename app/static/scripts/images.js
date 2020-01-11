
function get_viz_size() {
  graphHeight = document.getElementById('viz').clientHeight;
  graphWidth = document.getElementById('viz').clientWidth;
  return {
    h: graphHeight,
    w: graphWidth,
    xmid: graphWidth/2,
    ymid: graphHeight/2
  }
}


function show_images(data) {

  var div_size = get_viz_size()

  // setting formating for chart
  var margin = {top: 50, right: 50, bottom: 50, left: 50},
      width = div_size.w - margin.left - margin.right,
      height = div_size.h - margin.top - margin.bottom;
  var valueLabelMargin = 0
  var leftMargin = 0

  // create our svg
  var svg = d3.select("#viz").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .attr("id","viz_svg")
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

  // setting scale based on formating

  scale = d3.scaleLinear().range([height, 0]);
  scale.domain([0,10]);
  box_size = height/10

 
  // place images
  svg.selectAll(".frame")
      .data(data)
    .enter().append("image")
      .attr("class", "img")
      .attr("height", function(d) { return box_size })
      .attr("width", function(d) { return box_size })
      .attr("x", function(d,i) { return width/2 - height/2 - box_size + scale(Math.floor(i/10)); })
      .attr("y", function(d,i) { return scale(i%10); })
      .attr("xlink:href", function(d) { return d['url']; })
      .attr("opacity",.5)


