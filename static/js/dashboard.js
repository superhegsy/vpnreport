const HQ = [47.4979, 19.0402]

let map = null
let markerLayer = null


function getFlagEmoji(code){

    if(!code) return ""

    return code.toUpperCase().replace(/./g,
        c => String.fromCodePoint(127397 + c.charCodeAt())
    )
}


// ================= MAP =================

function initMap(){

    const mapElement = document.getElementById("map")
    if(!mapElement) return

    map = L.map("map").setView(HQ,6)

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {maxZoom:18}
    ).addTo(map)

    markerLayer = L.layerGroup().addTo(map)

    L.marker(HQ)
        .addTo(markerLayer)
        .bindPopup("VPN Gateway (Budapest HQ)")

    loadVPNLocations()
}


async function loadVPNLocations(){

    try{

        const res = await fetch("/api/vpn-locations/")
        const sessions = await res.json()

        markerLayer.clearLayers()

        L.marker(HQ)
            .addTo(markerLayer)
            .bindPopup("VPN Gateway (Budapest HQ)")

        sessions.forEach(s => {

            if(!s.latitude || !s.longitude) return

            const location = [s.latitude, s.longitude]

            const flag = getFlagEmoji(s.country_code)

            const marker = L.marker(location)

            marker.bindTooltip(
                `<b>${s.username}</b><br>${flag} ${s.remote_ip}`,
                {direction:"top"}
            )

            marker.addTo(markerLayer)

            L.polyline([HQ,location],{
                color:"#4ea67d",
                weight:2,
                opacity:0.7,
                dashArray:"5,10"
            }).addTo(markerLayer)

        })

    }catch(err){
        console.warn("Map error",err)
    }
}


// ================= STATS =================

async function updateDashboardStats(){

    try{

        const res = await fetch("/api/dashboard-stats/")
        const data = await res.json()

        const active = document.getElementById("stat-active")
        const today = document.getElementById("stat-today")
        const top = document.getElementById("stat-topuser")

        if(active) active.innerText = data.active_users
        if(today) today.innerText = data.today_sessions
        if(top) top.innerText = data.top_user

    }catch(err){
        console.warn("Stats error",err)
    }
}


// ================= INIT =================

function init(){

    initMap()
    updateDashboardStats()

    setInterval(updateDashboardStats,5000)
    setInterval(loadVPNLocations,10000)
}

document.addEventListener("DOMContentLoaded",init)
