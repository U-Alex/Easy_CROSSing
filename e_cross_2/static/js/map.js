
window.onload = function init() {
    h_num_list();
    document.getElementById("go_bu").disabled = true;
    document.getElementById("go_agr").disabled = true;
    //if (document.getElementById("id_kvar").value != "1") {
        document.getElementById("go_kvar").setAttribute('onclick', 'window.open("/cable/?kv='+id_kvar.value+'")');
    //}
    //else { document.getElementById("go_kvar").disabled = true;}
    setTimeout(to_coord, 1000);
}

function to_coord() {
    if (document.getElementById("cx").value != "") {
        var xy = viewer.viewport.imageToViewportCoordinates(document.getElementById("cx").value, document.getElementById("cy").value);
        viewer.viewport.zoomTo(15, false, false);
        viewer.viewport.panTo(xy, false);
        to_frame(document.getElementById("cx").value+','+document.getElementById("cy").value);
    }
}
//document.oncontextmenu = function (){return false};

var viewer = OpenSeadragon({
    id: "maps",
    prefixUrl: "/static/js/images/",
    tileSources: "/media/map/"+document.getElementById("m_num").value+"/map.dzi",
    visibilityRatio: 0.8,
    animationTime:  0.8,
    // toolbar:       "toolbarDiv",
    // showNavigator:  true,
    showNavigationControl: false,
    // navigatorId:   "navigatorDiv",
    //debugMode:  true,
});

viewer.addHandler('canvas-double-click', function(event) {
    // The canvas-click event gives us a position in web coordinates.
    var webPoint = event.position;
    // Convert that to viewport coordinates, the lingua franca of OpenSeadragon coordinates.
    var viewportPoint = viewer.viewport.pointFromPixel(webPoint);
    // Convert from viewport coordinates to image coordinates.
    var imagePoint = viewer.viewport.viewportToImageCoordinates(viewportPoint);
    // Show the results.
    //console.log(webPoint.toString(), viewportPoint.toString(), imagePoint.toString());
    var coord1 = imagePoint.toString().slice(1,-1);
    //console.log(coord1);
    to_frame(coord1);
    // Disable zoom on click/touch
    event.preventDefaultAction = true;
    //button manage
    document.getElementById("go_bu").disabled = true;
    document.getElementById("go_agr").disabled = true;
    document.getElementById("id_h_num").value = "";
    document.getElementById("id_agr_list").value = "---";
});

viewer.addHandler('canvas-click', function(event) {
    // Disable zoom on click/touch
    event.preventDefaultAction = true;
    //document.getElementById("info1").innerHTML = 'Left mouse';
});

viewer.addHandler('canvas-nonprimary-press', function(event) {
    if (event.button === 2) { // Right mouse
        //document.getElementById("info1").innerHTML = 'Right mouse';
    }
    if (event.button === 1) { // center_btn
        //document.getElementById("info1").innerHTML = 'center_btn mouse';
    }
    //If you want to disable the standard right-click menu, you can do something like this (assuming jQuery):
    //$(viewer.element).on('contextmenu', function(event) {event.preventDefault();
});

function to_frame(coord) {
    document.getElementById("coord").value = coord;
    //iframe = document.getElementById('obj_list');
    //iframe.src = '/find/get_obj/?coord='+coord;
    obj_from_map('/find/get_obj/?coord='+coord);
}
function obj_from_map(url) {
    var http2 = new getXmlHttp();
    //console.log(url);
    http2.open("GET", url, true);
    http2.onreadystatechange = function() {
        if (http2.readyState == 4 && http2.status == 200) {
            var answer = http2.responseText;
            document.getElementById("obj_in_map").innerHTML = answer;
        }
        else {document.getElementById("obj_in_map").innerHTML = "error";}
    }
    http2.send(null);
}
/* */

id_street.addEventListener('change', function(){
    //console.log(this.value);
    h_num_list();
}, false);

function h_num_list() {
    var http = new getXmlHttp();
    var url = "/find/js_request/?str=" + id_street.value;
    http.open("GET", url, true);
    http.onreadystatechange = function() {
        if (http.readyState == 4 && http.status == 200) {
            var answer = http.responseText;
            if (answer != 'False') {
                var arr1 = answer.slice(2,-3).split("',)('");
                id_h_num.options.length = 0;
                id_h_num.options[id_h_num.options.length] = new Option('');
                for (var i=0, len=arr1.length; i<len; i++) {
                    id_h_num.options[id_h_num.options.length] = new Option(arr1[i]);
                }
            }
        }
    }
    http.send(null);
}

id_h_num.addEventListener('change', function(){
    //console.log(this.value);
    if (id_h_num.value != "") {
        h_num_get("/find/js_request/?bu=" + id_street.value+",,"+id_h_num.value, false, false);
    }
    else {document.getElementById("go_bu").disabled = true;}
}, false);

id_agr_list.addEventListener('change', function(){
    //console.log(this.value);
    if (id_agr_list.value != "---") {
        h_num_get("/find/js_request/?agr=" + id_agr_list.value, true, false);
    }
    else {document.getElementById("go_agr").disabled = true;}
}, false);

id_kvar.addEventListener('change', function(){
    //console.log(this.value);
    if (id_kvar.value != 1) {
        h_num_get("/find/js_request/?kv=" + id_kvar.value, false, true);
    }
}, false);

function h_num_get(url, agr, kv) {
    var http2 = new getXmlHttp();
    //console.log(url);
    http2.open("GET", url, true);
    http2.onreadystatechange = function() {
        if (http2.readyState == 4 && http2.status == 200) {
            var answer2 = http2.responseText;
            //iframe = document.getElementById('obj_list');
            if (answer2 != 'False') {
                var arr2 = answer2.split(",");
                //console.log(arr2);
                var zoom;
                if (agr){
                    //iframe.src = "/find/get_obj/?agr="+arr2[2];
                    obj_from_map("/find/get_obj/?agr="+arr2[2]);
                    document.getElementById("go_agr").setAttribute('onclick', 'window.open("/cross/build='+arr2[3]+'/locker='+arr2[2]+'/")');
                    //console.log(document.getElementById("go_agr").getAttribute('onclick'));
                    document.getElementById("go_bu").disabled = true;
                    document.getElementById("go_agr").disabled = false;
                    document.getElementById("go_kvar").disabled = true;
                    document.getElementById("id_h_num").value = "";
                    document.getElementById("id_kvar").value = "1";
                    zoom = 15;
                }
                else if (kv){;
                    //iframe.src = "/find/get_obj/";
                    //obj_from_map("/find/get_obj/");
                    document.getElementById("obj_in_map").innerHTML = "&nbsp;";
                    //document.getElementById("go_kvar").setAttribute('onclick', 'window.open("/cable/?kv='+arr2[2]+'")');
                    document.getElementById("go_kvar").setAttribute('onclick', 'window.open("/cable/kv='+arr2[2]+'/")');
                    document.getElementById("go_bu").disabled = true;
                    document.getElementById("go_agr").disabled = true;
                    document.getElementById("go_kvar").disabled = false;
                    document.getElementById("id_h_num").value = "";
                    document.getElementById("id_agr_list").value = "---";
                    document.getElementById("coord").value = "";
                    zoom = 10;
                }
                else {
                    //iframe.src = "/find/get_obj/?bu="+arr2[2];
                    obj_from_map("/find/get_obj/?bu="+arr2[2]);
                    document.getElementById("go_bu").setAttribute('onclick', 'window.open("/cross/build='+arr2[2]+'/")');
                    //console.log(document.getElementById("go_bu").getAttribute('onclick'));
                    document.getElementById("go_bu").disabled = false;
                    document.getElementById("go_agr").disabled = true;
                    document.getElementById("go_kvar").disabled = true;
                    document.getElementById("id_agr_list").value = "---";
                    document.getElementById("id_kvar").value = "1";
                    zoom = 15;
                }
                if (arr2[0] != "0" && arr2[1] != "0") {
                    var xy = viewer.viewport.imageToViewportCoordinates(arr2[0], arr2[1]);
                    viewer.viewport.zoomTo(zoom, false, false);
                    viewer.viewport.panTo(xy, false);
                    document.getElementById("coord").value = arr2[0]+","+arr2[1];
                }
                else {document.getElementById("coord").value = "";}
            }
            else {
                document.getElementById("coord").value = "";
                //iframe.src = "/find/get_obj/";
                //obj_from_map("/find/get_obj/");
                document.getElementById("obj_in_map").innerHTML = "&nbsp";
                //console.log("false");
            }
        }
    }
    http2.send(null);
}

function getXmlHttp() {
    var xmlhttp;
    try { xmlhttp = new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {
        try { xmlhttp = new ActiveXObject("Microsoft.XMLHTTP"); } catch (e2) {
            xmlhttp = false; } }
    if (!xmlhttp && typeof XMLHttpRequest!='undefined') { xmlhttp = new XMLHttpRequest(); }
    return xmlhttp;
}

