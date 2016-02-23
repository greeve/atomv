var slug = "rsmag";

$(document).ready(function() {
    var charts = [
        {"file": "js/rsmag-alr.json", "query": "Alice Louise Reynolds"},
        {"file": "js/rsmag-suffrage.json", "query": "suffrage"},
        {"file": "js/rsmag-poetry.json", "query": "poetry"},
        {"file": "js/rsmag-potato.json", "query": "potato"},
        {"file": "js/rsmag-candy.json", "query": "candy"}
    ]

    var arrayLength = charts.length;
    for (var i = 0; i < arrayLength; i++) {
        createFreqChart(charts[i]);
    }
});

function createFreqChart(source) {
    var heading = d3.select("#freq").append("h1").text("References to \"" + source.query + "\"");
    var margin = {top: 20, right: 20, bottom: 90, left: 40};
    var width = 960 - margin.left - margin.right;
    var height = 500 - margin.top - margin.bottom;

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .2);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(5);

    var svg = d3.select("#freq").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.json(source.file, function(data) {
        x.domain(data.map(function(d) { return d.date; }));
        y.domain([0, d3.max(data, function(d) { return d.frequency; })]);
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")") 
            .call(xAxis)
            .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", function(d) { return "rotate(-65)" });

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Frequency");

        var bars = svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function(d) { return x(d.date); })
            .attr("width", x.rangeBand())
            .attr("y", function(d) { return y(d.frequency); })
            .attr("height", function(d) { return height - y(d.frequency); })
            .on("click", function(d) { 
                var query = "(" + source.query + ")" + " AND " + "pubyear_e:[" + d.date + " TO " + d.date + "]";
                var url = "https://atom.lib.byu.edu/" + slug + "/search/?q=";
                window.open(url + query);
            });

        var title = bars.append("title").text(function(d) { return d.frequency; });
    });
}
