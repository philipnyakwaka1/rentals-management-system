let map = L.map('map').setView([-1.2921, 36.8219], 10);

var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
});


let googleHybrid = L.tileLayer('http://{s}.google.com/vt?lyrs=s,h&x={x}&y={y}&z={z}',{
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});

var baseLayers = {
    "Open Street Maps": osm,
    "Google Hybrid": googleHybrid
};
L.control.layers(baseLayers).addTo(map);