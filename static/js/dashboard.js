// =====================
// HQ KOORDINÁTÁK (Budapest)
// =====================

const HQ = [47.4979, 19.0402];


// =====================
// FLAG EMOJI
// =====================

function getFlagEmoji(countryCode){

    if(!countryCode) return ""

    return countryCode
        .toUpperCase()
        .replace(/./g, char =>
            String.fromCodePoint(127397 + char.charCodeAt())
        )
}


// =====================
// TÉRKÉP (Magyarország fókusz)
// =====================

var map = L.map('map').setView(HQ, 7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:18
}).addTo(map);


// HQ marker

L.marker(HQ)
.addTo(map)
.bindPopup("VPN Gateway (HQ)");


// =====================
// VPN USER LOKÁCIÓK
// =====================

fetch("/api/vpn-locations/")
.then(response => response.json())
.then(data => {

    data.forEach(function(session){

        if(!session.lat || !session.lon) return

        var userLocation = [session.lat, session.lon]

        var flag = getFlagEmoji(session.country_code)

        // USER MARKER

        L.marker(userLocation)
        .addTo(map)
        .bindPopup(
            "<b>" + session.username + "</b>" +
            "<br>IP: " + session.ip +
            "<br>Ország: " + flag + " " + session.country
        )


        // HQ → USER VONAL

        L.polyline([HQ, userLocation], {
            color: "#4ea67d",
            weight: 2,
            opacity: 0.7,
            dashArray: "5,10"
        }).addTo(map)


        // rövid villanás effekt

        var circle = L.circle(userLocation, {
            radius: 30000,
            color: "#d7a300",
            fillOpacity: 0.3
        }).addTo(map)

        setTimeout(function(){
            map.removeLayer(circle)
        }, 2000)

    })

})


// =====================
// DASHBOARD STAT UPDATE
// =====================

function updateDashboard(){

    fetch("/api/dashboard-stats/")
    .then(response => response.json())
    .then(data => {

        if(document.getElementById("stat-active"))
            document.getElementById("stat-active").innerText = data.active_users

        if(document.getElementById("stat-today"))
            document.getElementById("stat-today").innerText = data.today_sessions

        if(document.getElementById("stat-total"))
            document.getElementById("stat-total").innerText = data.total_sessions

        if(document.getElementById("stat-topuser"))
            document.getElementById("stat-topuser").innerText = data.top_user

    })

}

setInterval(updateDashboard, 5000)


// =====================
// ZÁSZLÓ AZ IP ELŐTT
// =====================

document.querySelectorAll(".ip-flag").forEach(function(el){

    var code = el.dataset.code

    if(code){
        el.innerText = getFlagEmoji(code) + " "
    }

})
