import json
import html
import os

filepath="f+attention-newstest2017.b12.hyp"
with open(filepath) as fp:
    content = fp.readlines()
    sent = {}
    sentences = []
    first = True
    for line in content:
        tokens = line.split('|||')
        if first:
            first=False
            sent['id'] = tokens[0]
            sent['src'] = html.escape(tokens[1]).strip().split(' ')
            sent['score'] = tokens[2]
            sent['trg'] = html.escape(tokens[3]).strip().split(' ')
            sent['src_length'] = tokens[4]
            sent['trg_lenght'] = tokens[5]
            sent['attentions'] = []
        elif len(tokens) == 1 and tokens[0] == '\n':
            first = True
            sentences.append(sent)
            sent={}
        else:
            sent['attentions'].append(tokens[0].split(' '))


#    print("data = '" + json.dumps(sentences).replace("\\n", "").replace("'", "\\'") + "';")

html_string = "<html><head>"
html_string += """
<style>
.word {
    padding:0 5px;
}

.sentence {
    margin: 10px 0;
}

.trg .word:hover {
    background-color: rgba(255, 0, 0, .5);
}
</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script> var data = %s; </script>
<script>
document.addEventListener("DOMContentLoaded", function(event) { 
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
});
 </script>
 </head>
 <body>
 <div id="sentences"></div>
 </body>
 </html>
 """ % json.dumps(sentences, ensure_ascii=True).replace("\\n", "")

print(html_string)