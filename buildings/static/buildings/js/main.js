const map = L.map("map").setView([-1.2921, 36.8219], 15);

const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
});


const googleHybrid = L.tileLayer('http://{s}.google.com/vt?lyrs=s,h&x={x}&y={y}&z={z}',{
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});

const baseLayers = {
    "Open Street Maps": osm,
    "Google Hybrid": googleHybrid
};
osm.addTo(map);
L.control.layers(baseLayers).addTo(map);

async function fetchData() {
  const url = 'http://127.0.0.1:8000/api/v1/building/';
  try {
    response = await fetch(url, {
      method: 'GET'
    })
    if (!response.ok) {
      throw new Error(`status: ${response.status}`);
    }
    return await response.json();
  } catch(error) {
    return error.message;
  };
};

function createCustomIcon (feature, ){

};

async function main() {
  let customIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
    iconSize: [15, 25],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34]
  });
  const buildingsGeojson = await fetchData().then(result => JSON.parse(result));
  const tmp = L.geoJSON(buildingsGeojson, {
    pointToLayer: (geoJSONPoint, latLng) => L.marker(latLng, {icon: customIcon})
  }).addTo(map);
}
console.log( L.Icon.Default.prototype.options);
main();