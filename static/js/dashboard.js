const HQ = [47.4979, 19.0402]

let map = null

function getFlagEmoji(code){

    if(!code) return ""

    return code.toUpperCase().replace(/./g,
        c => String.fromCodePoint(127397 + c.charCodeAt())
    )

}

function initMap(){

    const mapElement = document.getElementById("map")

    if(!mapElement) return

    map = L.map("map").setView(HQ,6)

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {maxZoom:18}
    ).addTo(map)

    L.marker(HQ)
        .addTo(map)
        .bindPopup("VPN Gateway (Budapest HQ)")

    loadVPNLocations()

}


async function loadVPNLocations(){

    const res = await fetch("/api/vpn-locations/")
    const sessions = await res.json()

    sessions.forEach(s => {

        if(!s.latitude || !s.longitude) return

        const location = [s.latitude, s.longitude]

        const marker = L.marker(location).addTo(map)

        const flag = getFlagEmoji(s.country_code)

        marker.bindTooltip(
            `<b>${s.username}</b><br>${flag} ${s.remote_ip}`,
            {direction:"top"}
        )

        L.polyline([HQ,location],{
            color:"#4ea67d",
            weight:2,
            opacity:0.7,
            dashArray:"5,10"
        }).addTo(map)

    })

}



async function refreshVPNSessions(){

    const table = document.getElementById("vpn-table")

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

        html += `
        <tr>
        <td>${s.username}</td>
        <td>${flag} ${s.remote_ip}</td>
        <td>${s.connected_at}</td>
        <td>${s.duration}</td>
        </tr>
        `
    })

    table.innerHTML = html

}



async function updateDashboardStats(){

    const res = await fetch("/api/dashboard-stats/")
    const data = await res.json()

    document.getElementById("stat-active").innerText = data.active_users
    document.getElementById("stat-today").innerText = data.today_sessions
    document.getElementById("stat-topuser").innerText = data.top_user

}



function init(){

    initMap()

    updateDashboardStats()
    refreshVPNSessions()

    setInterval(updateDashboardStats,5000)
    setInterval(refreshVPNSessions,10000)

}

document.addEventListener("DOMContentLoaded",init)
