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
}


// ================= TABLE =================

async function refreshVPNSessions(){

    const table = document.getElementById("vpn-table")
    if(!table) return

    const res = await fetch("/api/active-vpn/")
    const sessions = await res.json()

    let html = `
    <tr>
    <th>Felhasználó</th>
    <th>Külső IP</th>
    <th>Kapcsolódott</th>
    <th>Duration</th>
    </tr>
    `

    sessions.forEach(s => {

        const flag = getFlagEmoji(s.country_code)

        const hours = Math.floor(s.duration/3600)
        const minutes = Math.floor((s.duration%3600)/60)

        const duration =
            hours > 0
            ? `${hours}h ${minutes}m`
            : `${minutes}m`

        html += `
        <tr>
        <td>${s.username}</td>
        <td>${flag} ${s.remote_ip}</td>
        <td>${s.connected_at}</td>
        <td>${duration}</td>
        </tr>
        `
    })

    table.innerHTML = html
}


// ================= STATS =================

async function updateDashboardStats(){

    const res = await fetch("/api/dashboard-stats/")
    const data = await res.json()

    document.getElementById("stat-active").innerText = data.active_users
    document.getElementById("stat-today").innerText = data.today_sessions
    document.getElementById("stat-topuser").innerText = data.top_user
}


// ================= INIT =================

function init(){

    initMap()

    updateDashboardStats()
    refreshVPNSessions()

    setInterval(updateDashboardStats,5000)
    setInterval(refreshVPNSessions,5000)
    setInterval(loadVPNLocations,10000)
}

document.addEventListener("DOMContentLoaded",init)

function updateClock(){

    const now = new Date()

    const time =
        String(now.getHours()).padStart(2,"0")+":"+
        String(now.getMinutes()).padStart(2,"0")+":"+
        String(now.getSeconds()).padStart(2,"0")

    const date =
        now.getFullYear()+"."+
        String(now.getMonth()+1).padStart(2,"0")+"."+
        String(now.getDate()).padStart(2,"0")

    const t = document.getElementById("clock-time")
    const d = document.getElementById("clock-date")

    if(t) t.innerText = time
    if(d) d.innerText = date
}

setInterval(updateClock,1000)
updateClock()
