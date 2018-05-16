function attention_viz(data) {
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