openerp.test_paie = function (instance)

{

var QWeb = instance.web.qweb;

var _t = instance.web._t;

instance.seetek_paie.Mywidget = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin,{

template : "seetek_paie.Mywidget",

events: {

'click .oe_web_example_file button': 'Upload',

},

Upload: function () {

var fileUpload = document.getElementById("fileUpload");

var regex = /^([a-zA-Z0-9\s_\\.\-:])+(.csv|.txt)$/;

if (regex.test(fileUpload.value.toLowerCase())) {

if (typeof (FileReader) != "undefined") {

var reader = new FileReader();

var tabResult = new Array();

reader.onload = function (e) {

var table = document.createElement("table");

var rows = e.target.result.split("\n");

var y = new Array();

var matricule = new Array();

for (var i = 0; i < (rows.length - 1); i++) {

var row = table.insertRow(-1);

var cells = rows[i].split(",");

if (cells[0] != 0)

{ var mat = cells[0];}

console.log("La" + i + "ème matricule est \n"+ mat);

if (cells[0]!= "")

{matricule.push(cells[0]);}

// Affiche doc

for (var j = 0; j < cells.length; j++) {

var cell = row.insertCell(-1);

cell.innerHTML = cells[j];

}

}

console.log(matricule);

var days = new Array();

var heures = new Array();

for (var i = 1; i < rows.length; i++) {

var row = table.insertRow(-1);

var cells = rows[i].split(",");

days = rows[0].split(",");

var obj = {};

var obj2 = {};

for (var j = 0; j < cells.length; j++) {

obj2[j] = cells[j];

}

obj[i] = obj2;

heures.push(obj);

}

var my_jsons_days;

var my_jsons_days_all = new Array();

var oups;

for (var i = 0; i < (rows.length - 2); i++) {

var my_jsons_days_all_temp = new Array();

for (var dd = 1; dd < days.length; dd++) {

var z;

if (heures[i][i+1][dd] > 0) { z = 'T';} else {z = 'A'; }

my_jsons_days = {"day":days[dd],"hours":heures[i][i+1][dd],"nature":z};

my_jsons_days_all_temp.push(my_jsons_days);

}

oups = {"days": my_jsons_days_all_temp};

var jsonStrssEM = JSON.stringify(oups);

console.log(jsonStrssEM);

var node = document.createElement("LI");

var textnode = document.createTextNode(jsonStrssEM);

node.appendChild(textnode);

document.getElementById("myList2").appendChild(node);

}

var dvCSV = document.getElementById("dvCSV");

dvCSV.innerHTML = "";

dvCSV.appendChild(table);

}

reader.readAsText(fileUpload.files[0]);

} else {

alert("This browser does not support HTML5.");

}

} else {

alert("Please upload a valid CSV file.");

}

},



});

instance.web.form.custom_widgets.add('momo1', 'instance.test_paie.Mywidget');

};