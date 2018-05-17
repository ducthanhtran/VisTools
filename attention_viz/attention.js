function attention_viz_overlay(data) {
    var sentences = document.getElementById("sentences")
    for(var i = 0; i < data.length; ++i) {

        // console.log("trg",data[i].trg.length)
        // console.log("src", data[i].src.length)
        // console.log("attention", data[i].attentions.length)
        var src = document.createElement("div")
        src.setAttribute("class", "src");
        src.id="src-" + i
        for(var j = 0; j < data[i].src.length; ++j){
            var word = document.createElement("span")
            word.setAttribute("class", "word");
            word.id = "source-" + j
            word.innerHTML = data[i].src[j]
            src.appendChild(word)
        }

        var trg = document.createElement("div")
        trg.setAttribute("class", "trg");
        for(var j = 0; j < data[i].trg.length; ++j){
            var word = document.createElement("span")
            word.id = "target-" + j
            word.setAttribute("class", "word");
            word.dataset.src_id = "src-" + i
            word.dataset.attention = JSON.stringify(data[i].attentions[j])
            word.innerHTML = data[i].trg[j]
            word.onmouseover = function() {
                var src_sen = document.getElementById(this.dataset.src_id)
                var attentions = JSON.parse(this.dataset.attention)
                var sum = 0
                for( var s = 0; s < attentions.length; ++s){
                    sum += parseFloat(attentions[s])
                }
                for( var child_id = 0; child_id < src_sen.children.length; ++child_id){
                    child = src_sen.children[child_id]
                    color = parseFloat(attentions[child_id])/sum
                    child.style.backgroundColor = "rgba(255, 0, 0, " + color +")"
                }
            }
            trg.appendChild(word)
        }
        var sen = document.createElement("div")
        sen.setAttribute("class", "sentence")
        var p = document.createTextNode( "sentence " + data[i].id)
        var h2 = document.createElement("h2")
        h2.appendChild(p)
        sen.appendChild(h2)
        sen.id = "sentence-" + data[i].id
        sen.appendChild(src)
        sen.appendChild(trg)
        sentences.appendChild(sen)
    }
}

var decodeHTML = function (html) {
	var txt = document.createElement('textarea');
	txt.innerHTML = html;
	return txt.value;
};

function writeDownloadLink(){

    try {
        var isFileSaverSupported = !!new Blob();
    } catch (e) {
        alert("blob not supported");
    }
    var html = d3.select("#"+this.dataset.svg_id)
        .attr("title", this.dataset.title)
        .attr("version", 1.1)
        .attr("encoding", "utf-8")
        .attr("xmlns", "http://www.w3.org/2000/svg")
        .node().parentNode.innerHTML;

    var blob = new Blob([html], {type: "image/svg+xml"});
    saveAs(blob, this.dataset.filename);
};

function attention_viz_matrix(data){
    for (var k = 0; k < data.length; ++k) {
        var sen_data = []
        var trgLength = parseInt(data[k].trg_lenght);
        var srcLength = parseInt(data[k].src_length)
        var sentenceId = parseInt(data[k].id)
        for (var i = 0; i < trgLength; ++i) {
            for (var j = 0; j < srcLength; ++j) {
                var newItem = {}
                newItem.srcWord = decodeHTML(data[k].src[j])
                newItem.trgWord = decodeHTML(data[k].trg[i])
                newItem.value = data[k].attentions[i][j]
                sen_data.push(newItem)
            }
        }

        var itemSize = 22,
            cellSize = 21,
            margin = {top: 120, right: 20, bottom: 20, left: 110};

        var width = cellSize*srcLength + margin.left + margin.right,
            height = cellSize*trgLength + margin.top;

        var sen_div = d3.select('#sentences')
            .append("div")
            .attr("class", "sentence-matrix")
            .attr("id", "sentence-" + sentenceId);
        sen_div.append("h2").text("Sentence " + sentenceId);
        sen_div.append("button")
            .text("Download")
            .attr("data-svg_id", "svg-"+sentenceId)
            .attr("data-title", "Sentence "+sentenceId)
            .attr("data-filename", "sentence-"+sentenceId)
            .on("click", writeDownloadLink)

        var svg_div = sen_div.append("div");
        var svg = svg_div
            .append("svg")
            .attr("id", "svg-" + sentenceId)
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


        var x_elements = data[k].src.map(function(item){return decodeHTML(item)}),
            y_elements =  data[k].trg.map(function(item){return decodeHTML(item)});

        var xScale = d3.scale.ordinal()
            .domain(x_elements)
            .rangeBands([0, x_elements.length * itemSize]);

        var xAxis = d3.svg.axis()
            .scale(xScale)
            .tickFormat(function (d) {
                return d;
            })
            .orient("top")

        d3.selectAll(".axis path")
            .style("stroke", "#000000")
            .style("fill", "none")
            .style("stroke-width", "1px");
        d3.selectAll(".axis line")
            .style("stroke", "#000000")
            .style("fill", "none")
            .style("stroke-width", "1px");
        svg.append("text")
          .attr("transform",
                "translate(" + (width/2) + " ," + (-margin.top + 30) + ")")
          .style("text-anchor", "middle")
          .text("Source");


        var yScale = d3.scale.ordinal()
            .domain(y_elements)
            .rangeBands([0, y_elements.length * itemSize]);

        var yAxis = d3.svg.axis()
            .scale(yScale)
            .tickFormat(function (d) {
                return d;
            })
            .orient("left");

        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left)
            .attr("x",0 - (height / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .text("Target");

        var cells = svg.selectAll('rect')
            .data(sen_data)
            .enter().append('g').append('rect')
            .attr('class', 'cell')
            .attr('width', cellSize)
            .attr('height', cellSize)
            .attr('y', function (d) {
                return yScale(d.trgWord);
            })
            .attr('x', function (d) {
                return xScale(d.srcWord);
            })
            .attr('fill', '#000000')
            .attr('opacity', function (d) {
                return  d.value;
            });

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .selectAll('text')
            .attr('font-weight', 'normal');

        svg.append("g")
            .attr("class", "x axis")
            .call(xAxis)
            .selectAll('text')
            .attr('font-weight', 'normal')
            .style("text-anchor", "start")
            .attr("dx", ".8em")
            .attr("dy", ".5em")
            .attr("transform", function (d) {
                return "rotate(-65)";
            });

    }
}