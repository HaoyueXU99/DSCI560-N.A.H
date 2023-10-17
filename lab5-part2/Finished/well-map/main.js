
// JavaScript

import './style.css';
import { Map, View, Feature, Overlay } from 'ol';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer';
import { OSM, Vector as VectorSource } from 'ol/source';
import { Point } from 'ol/geom';
import { Style, Icon } from 'ol/style';
import { fromLonLat } from 'ol/proj';  


async function fetchWellData() {
    const response = await fetch("http://localhost:5000/get_well_data");
    const data = await response.json();

    return data.map(item => {
        return {
            id: item.File_Number,
            name: item.Well_name,
            APINumber: item.APINumber,
            lon: parseFloat(item.Longitude),
            lat: parseFloat(item.Latitude),
            Date_stimulated: item.Date_stimulated,
            Stim_formation: item.Stim_formation,
            Top: item.Top,
            Bottom: item.Bottom,
            Stim_stages: item.Stim_stages,
            Volume: item.Volume,
            Units: item.Units,
            Type_treatment: item.Type_treatment,
            Acid_Percentage: item.Acid_Percentage,
            Proppant_Lbs: item.Proppant_Lbs,
            Max_Pressure: item.Max_Pressure,
            Max_Rate: item.Max_Rate,
            Well_status: item.Well_status,
            Well_type: item.Well_type,
            Closest_city: item.Closest_city,
            data: item.Details
        };
    });
}

function wellsToFeatures(wells) {
    return wells.map(well => {
        const feature = new Feature({
            geometry: new Point(fromLonLat([well.lon, well.lat])),
            data: well
        });
        feature.setStyle(new Style({
            image: new Icon({
                anchor: [0.5, 1],
                src: 'oil-well.svg',
                scale: 0.3
            })
        }));
        return feature;
    });
}

async function initMap() {
    const wellData = await fetchWellData();
    const wellFeatures = wellsToFeatures(wellData);

    const wellsLayer = new VectorLayer({
        source: new VectorSource({
            features: wellFeatures
        })
    });

    const popupContainer = document.getElementById('popup');
    const popup = new Overlay({
        element: popupContainer,
        positioning: 'bottom-center',
        stopEvent: false
    });

    const map = new Map({
        target: 'map',
        layers: [
            new TileLayer({ source: new OSM() }),
            wellsLayer
        ],
        view: new View({
            center: fromLonLat([-103.6459, 48.0726]),
            zoom: 12
        }),
        overlays: [popup]
    });

    // map.on('click', event => {
    //     const clickedFeature = map.forEachFeatureAtPixel(event.pixel, feature => feature);
    //     if (clickedFeature) {
    //         const wellData = clickedFeature.get('data');
    //         popupContainer.innerHTML = `
    //             <div><strong>Name:</strong> ${wellData.name}</div>
    //             <div><strong>Additional Details:</strong> ${wellData.data}</div>
    //         `;
    //         popup.setPosition(event.coordinate);
    //         popupContainer.style.display = 'block';
    //     } else {
    //         popupContainer.style.display = 'none';
    //     }
    // });

    map.on('click', event => {
        const clickedFeature = map.forEachFeatureAtPixel(event.pixel, feature => feature);
        if (clickedFeature) {
            const wellData = clickedFeature.get('data');
            popupContainer.innerHTML = `
                <table class="info-table">
                    <tr>
                        <td><strong>Name:</strong></td><td colspan="3">${wellData.name}</td>
                    </tr>
                    <tr>
                        <td><strong>API Number:</strong></td><td colspan="3">${wellData.APINumber}</td>
                    </tr>
                    <tr>
                        <td><strong>Longitude:</strong></td><td>${wellData.lon}</td>
                        <td><strong>Latitude:</strong></td><td>${wellData.lat}</td>
                    </tr>
                    <tr>
                        <td><strong>Date Stimulated:</strong></td><td>${wellData.Date_stimulated}</td>
                        <td><strong>Stim Formation:</strong></td><td>${wellData.Stim_formation}</td>
                    </tr>
                    <tr>
                        <td><strong>Top:</strong></td><td>${wellData.Top}</td>
                        <td><strong>Bottom:</strong></td><td>${wellData.Bottom}</td>
                    </tr>
                    <tr>
                        <td><strong>Stim Stages:</strong></td><td>${wellData.Stim_stages}</td>
                        <td><strong>Volume:</strong></td><td>${wellData.Volume}</td>
                    </tr>
                    <tr>
                        <td><strong>Units:</strong></td><td>${wellData.Units}</td>
                        <td><strong>Type of Treatment:</strong></td><td>${wellData.Type_treatment}</td>
                    </tr>
                    <tr>
                        <td><strong>Acid Percentage:</strong></td><td>${wellData.Acid_Percentage}</td>
                        <td><strong>Proppant Lbs:</strong></td><td>${wellData.Proppant_Lbs}</td>
                    </tr>
                    <tr>
                        <td><strong>Max Pressure:</strong></td><td>${wellData.Max_Pressure}</td>
                        <td><strong>Max Rate:</strong></td><td>${wellData.Max_Rate}</td>
                    </tr>
                    <tr>
                        <td><strong>Well Status:</strong></td><td>${wellData.Well_status}</td>
                        <td><strong>Well Type:</strong></td><td>${wellData.Well_type}</td>
                    </tr>
                    <tr>
                        <td><strong>Closest City:</strong></td><td colspan="3">${wellData.Closest_city}</td>
                    </tr>
                    <tr>
                        <td><strong>Additional Details:</strong></td><td colspan="3">${wellData.data}</td>
                    </tr>
                </table>
            `;
            popup.setPosition(event.coordinate);
            popupContainer.style.display = 'block';
        } else {
            popupContainer.style.display = 'none';
        }
    });


    map.on('pointermove', event => {
        if (map.hasFeatureAtPixel(event.pixel)) {
            map.getViewport().style.cursor = 'pointer';
        } else {
            map.getViewport().style.cursor = 'default';
        }
    });
}

initMap();
