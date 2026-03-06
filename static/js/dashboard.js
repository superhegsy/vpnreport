// =====================
// HQ KOORDINÁTÁK
// =====================

const HQ = [47.4979, 19.0402]; // Budapest



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
// TÉRKÉP
// =====================

var map = L.map('map').setView(HQ, 7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:18
}).addTo(map)



// HQ marker

L.marker(HQ)
.addTo(map)
.bindPopup("VPN Gateway (Budapest HQ)")



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
            "<br>" + flag + " " + session.country
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

// =====================
// AUTO REFRESH VPN TABLE
// =====================

async function refreshVPNSessions(){

    try{

        const response = await fetch("/api/active-vpn/")
        const data = await response.json()

        const table = document.querySelector("#vpn-table")

        if(!table) return

        let html = `
        <tr>
        <th>Felhasználó</th>
        <th>Külső IP</th>
        <th>Kapcsolódott</th>
        <th>Duration</th>
        </tr>
        `

        data.forEach(function(s){

            let flag = ""

            if(s.country_code){
                flag = getFlagEmoji(s.country_code) + " "
            }

            html += `
            <tr>
                <td>${s.username}</td>
                <td>${flag}${s.ip}</td>
                <td>${s.connected_at}</td>
                <td>${s.duration}</td>
            </tr>
            `

        })

        table.innerHTML = html

    }catch(e){
        console.log("VPN refresh error", e)
    }

}

setInterval(refreshVPNSessions, 10000)

// =====================
// VPN CONNECT ALERT
// =====================

let knownUsers = new Set()

async function checkNewVPNUsers(){

    try{

        const response = await fetch("/api/active-vpn/")
        const sessions = await response.json()

        sessions.forEach(function(s){

            if(!knownUsers.has(s.username)){

                knownUsers.add(s.username)

                showVPNToast(s)

            }

        })

    }catch(e){
        console.log("VPN alert error", e)
    }

}



function showVPNToast(session){

    const container = document.getElementById("vpn-toast-container")

    if(!container) return

    const toast = document.createElement("div")

    toast.className = "vpn-toast"

    toast.innerHTML =
        "🟢 <b>" + session.username +
        "</b> connected from " + session.ip

    container.appendChild(toast)

    setTimeout(function(){
        toast.remove()
    }, 5000)

}

setInterval(checkNewVPNUsers, 5000)

