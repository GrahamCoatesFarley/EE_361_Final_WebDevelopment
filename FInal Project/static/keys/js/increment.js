function keep(event) {
    if (localStorage.num2){
        num = localStorage.num2;
        num = num+(event.key)
        localStorage.setItem("num2", num);
    } else{
        localStorage.setItem("num2", event.key);
    }

}

function getNumber(){
var valueTyped = document.getElementById("number2").value;
localStorage.setItem("num2", valueTyped);
//alert(valueTyped)
}

//    var num = document.getElementById("number").value;
////    alert(inputVal)
//    var stroke = {
//        k: num,
//    };
//    var data = encodeURIComponent(JSON.stringify(stroke));
//    new Image().src = "/aetna/increment/" + data;

//Redirect
//location.href = "/aetna/landingpage/";


//function change(foo, bar){
//$.ajax({
//    url: 'ajax/foo/',
//    data : {
//        'foo': foo,
//        'bar': bar
//    },
//    success: function (data) {
//        $("#idImg").html(data);
//    }
//});