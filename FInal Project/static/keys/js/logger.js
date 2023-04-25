var buffer = [];
var url1 = '/soteria/listen/'
var url2 = '/soteria/listn2/'
var url3 = '/soteria/temp_keys_listen/'
var url4 = '/soteria/temp_mouse_listen'
var url5 = '/soteria/dropdwnln'
var url6 = '/soteria/dropdwnlisten2'
var url7 = '/soteria/mousee'
var url8 = '/soteria/mouse2'

var isOpen = false;
var lastFocus = '';
var prevClosed = false;
var page = '';

function myFunction(event, downup, name) {
    var timestamp = Date.now();
    var x = event.key;
    var stroke = {
        k: x,
        t: timestamp,
        r: downup,
        s: name,
    };
//   buffer.push(stroke);
      var data = encodeURIComponent(JSON.stringify(stroke));
      new Image().src = url1 + data;
}

function myFunction3(event, downup, name) {
    var timestamp = Date.now();
    var x = event.key;
    var stroke = {
        k: x,
        t: timestamp,
        r: downup,
        s: name,
    };
//   buffer.push(stroke);
      var data = encodeURIComponent(JSON.stringify(stroke));
      new Image().src = url3 + data;
}

function myFunction2(event, downup, name) {
    var timestamp = Date.now();
    var x = event.key;
    var stroke = {
        k: x,
        t: timestamp,
        r: downup,
        s: name,
    };
//   buffer.push(stroke);
    var data = encodeURIComponent(JSON.stringify(stroke));
    new Image().src = url2 + data;
}

//For account recovery
function mouseClick(obj, name){
    var timestamp = Date.now();
    if (lastFocus != '' && lastFocus != name){
//        close the previous if open
        if (isOpen){
            isOpen = !isOpen;
            prevClosed = true;
            saveDropdownAction(timestamp, name, checkIfOpen(), 'mouse_click');
//            console.log('prev ', lastFocus, checkIfOpen());
        }
    }
//    if (!isOpen){obj.selectedIndex = 0}
    isOpen = !isOpen;
    saveDropdownAction(timestamp, name, checkIfOpen(), 'mouse_click');
//    console.log('click ',name, checkIfOpen());
};

function saveDropdownAction(timestamp, widgetName, status, action){
    var dropdw = {
    t: timestamp,
    w: widgetName,
    s: status,
    a: action
    };
        var data = encodeURIComponent(JSON.stringify(dropdw));
        new Image().src = url5 + data;
//        if (page == 'forgotpwd1'){  // Account Recovery
//            new Image().src = url5 + data;
//        }else if (page == 'step1'){ // Enrollment
//            new Image().src = url6 + data;
//        }
}


function onChange(name) {
//    var timestamp = Date.now();
//        isOpen = !isOpen;
//        prevClosed = true;
//        saveDropdownAction(timestamp, name, checkIfOpen(), 'mouse_click');
//        console.log('change ', name, checkIfOpen());
}

function dropdownKeypress(obj, e, type, name) {
    var numkeys = [37,38,39,40,48,49,50,51,52,53,54,55,56,57];
    var timestamp = Date.now();
    if (type == 0){
        if (e.keyCode == 13) {  //Enter key
            if (!isOpen){obj.selectedIndex = 0}
            isOpen = !isOpen;
            prevClosed = false;
            saveDropdownAction(timestamp, name, checkIfOpen(), e.key);
//            console.log('enter', name, checkIfOpen());
        }else if (e.keyCode == 9){  //TAB key
             if(isOpen){
                isOpen = !isOpen;
//                console.log('tab', name, checkIfOpen());
             }
             saveDropdownAction(timestamp, name, checkIfOpen(), e.key);
        } else if (name == 'month' || name == 'day' || name == 'year'){
             if(numkeys.includes(e.keyCode) && !isOpen){    //Numbers and Arrow keys
                isOpen = !isOpen;
                prevClosed = false;
//                console.log('number', name, checkIfOpen());
             }
             saveDropdownAction(timestamp, name, checkIfOpen(), e.key);
         } else{
            if(!isOpen){
                isOpen = !isOpen;
                prevClosed = false;
//                console.log('other key', name, checkIfOpen());
             }
             saveDropdownAction(timestamp, name, checkIfOpen(), e.key);
         }
    }
}

//For account recovery

//        var data = encodeURIComponent(JSON.stringify(mouse_click));
//        new Image().src = url5 + data;

//Defines mouse clicks on widgets
function mouseDownUp(event, which, widget, widgetName, page){
    var timestamp = Date.now();
    if (event.button == 0){
        evt = 'left_mouse_'+which
    }else if (event.button == 1){
        evt = 'middle_mouse_'+which
    }else if (event.button == 2){
        evt = 'right_mouse_'+which
    }
    var stroke = {
        t: timestamp,
        e: evt,
        c: widgetName,
        w: widget,
        p: page,
    };
      var data = encodeURIComponent(JSON.stringify(stroke));
      new Image().src = url7 + data;
}


function checkIfOpen(){
           if(isOpen)
              return "open";
           else
              return "closed";
}

function onBlur(name){
    var timestamp = Date.now();
    if(isOpen && lastFocus == name && !prevClosed){
        isOpen = !isOpen;
    }
    saveDropdownAction(timestamp, name, checkIfOpen(), 'blur');
//    console.log('blur ',lastFocus, checkIfOpen());
    if (prevClosed){prevClosed = !prevClosed}
}

function onFocus(name){
    var timestamp = Date.now();
    saveDropdownAction(timestamp, name, checkIfOpen(), 'focus');
    lastFocus = name;
}


//For Enrollment
//Defines mouse enters and leaves on widgets
function mousee(event, widget, widgetName, page){
    var timestamp = Date.now();
    var stroke = {
        t: timestamp,
        e: event,
        c: widgetName,
        w: widget,
        p: page,
    };
      var data = encodeURIComponent(JSON.stringify(stroke));
      new Image().src = url7 + data;
}


//For Enrollment
//Defines mouse enters and leaves on widgets
function mousee2(event, widget, widgetName, page){
    var timestamp = Date.now();
    var stroke = {
        t: timestamp,
        e: event,
        c: widgetName,
        w: widget,
        p: page,
    };
      var data = encodeURIComponent(JSON.stringify(stroke));
      new Image().src = url8 + data;
}


$(document).ready(function(event) {
    page = (window.location.href).split("/").pop();

    // Coordinates of the Mouse
    $(document).mousemove(
        function (event) {
        var timestamp = Date.now();
        page = (window.location.href).split("/").pop();

        var xPos = event.pageX;
        var yPos = event.pageY;

//        if (page.length > 0 && page !='#'){
        if (page.includes('forgotpwd1')){
        page = 'recovery_step1'
        }else if (page.includes('forgotpwd2')){
        page = 'recovery_step2'
        }else if (page.includes('forgotpwd4')){
        page = 'recovery_step4'
        }else if (page.includes('signup1')){
        page = 'signup1'
        }else if (page.length<1 || page == '#'){
            page = 'home'
        }else {
            page = 'unknown'
        }

//            console.log(xPos, yPos);

        var width = window.innerWidth;
        var height = window.innerHeight;
        var res = (width+'x'+height)
        var movement = {
            t: timestamp,
            x_po: xPos,
            y_po: yPos,
            p: page,
            r: res,
            e: 'mouse_move',
        };
          var data = encodeURIComponent(JSON.stringify(movement));
          var p = ['recovery', 'home', 'signup1'];
          if (p.includes(page)){  // Account Recovery or login page
            new Image().src = url7 + data;
          }

    });
});


