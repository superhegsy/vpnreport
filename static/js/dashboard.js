// =====================================================
// VPN DASHBOARD SCRIPT (STABLE VERSION)
// =====================================================


// ================= CONFIG =================

const HQ = [47.4979, 19.0402]

const MAP_ZOOM_DEFAULT = 6
const MAP_ZOOM_SINGLE = 7
const MAP_ZOOM_MULTI = 6

let map
let knownUsers = new Set()


// ================= UTIL =================

function setText(id, value) {

    const el = document.getElementById(id)

    if (el) el.innerText = value

}

function getFlagEmoji(code) {

    if (!code) return ""

    return code
        .toUpperCase()
        .replace(/./g, char =>
            String.fromCodePoint(127397 + char.charCodeAt())
        )

}


// ================= DATE FIX =================
// ISO datetime javítás JS-nek

function parseISODate(value) {

    if (!value) return null

    // levágjuk a microsecond részt
    const clean = value.split(".")[0]

    return new Date(clean)

}


// ================= MAP =================

function initMap() {

    const mapElement = document.getElementById("map")
    if (!mapElement) return

    map = L.map("map").setView(HQ, MAP_ZOOM_DEFAULT)

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        { maxZoom: 18 }
    ).addTo(map)

    L.marker(HQ)
        .addTo(map)
        .bindPopup("VPN Gateway (Budapest HQ)")

    loadVPNLocations()

}


async function loadVPNLocations() {

    try {

        const res = await fetch("/api/vpn-locations/")
        const sessions = await res.json()

        const bounds = []
        const users = []

        sessions.forEach(session => {

            if (!session.lat || !session.lon) return

            const location = [session.lat, session.lon]
            const flag = getFlagEmoji(session.country_code)

            users.push(location)
            bounds.push(location)

            const marker = L.marker(location).addTo(map)

            marker.bindTooltip(
                `<b>${session.username}</b><br>${flag}${session.ip}`,
                {
                    direction: "top",
                    offset: [0, -10],
                    opacity: 0.9
                }
            )

            L.polyline([HQ, location], {
                color: "#4ea67d",
                weight: 2,
                opacity: 0.7,
                dashArray: "5,10"
            }).addTo(map)

            pulse(location)

        })

        applyZoom(users, bounds)

    }

    catch (err) {

        console.error("VPN map error:", err)

    }

}


function applyZoom(users, bounds) {

    if (!map) return

    if (users.length === 1) {

        map.fitBounds([HQ, users[0]], {
            padding: [120, 120],
            maxZoom: MAP_ZOOM_SINGLE
        })

    }

    else if (users.length > 1) {

        bounds.push(HQ)

        map.fitBounds(bounds, {
            padding: [80, 80],
            maxZoom: MAP_ZOOM_MULTI
        })

    }

}


function pulse(location) {

    if (!map) return

    const pulse = L.circle(location, {
        radius: 30000,
        color: "#d7a300",
        fillOpacity: 0.3
    }).addTo(map)

    setTimeout(() => map.removeLayer(pulse), 2000)

}


// ================= DASHBOARD STATS =================

async function updateDashboardStats() {

    try {

        const res = await fetch("/api/dashboard-stats/")
        const data = await res.json()

        setText("stat-active", data.active_users)
        setText("stat-today", data.today_sessions)
        setText("stat-topuser", data.top_user)

    }

    catch (err) {

        console.error("Dashboard stats error:", err)

    }

}


// ================= VPN TABLE =================

async function refreshVPNSessions() {

    try {

        const res = await fetch("/api/active-vpn/")
        const sessions = await res.json()

        const table = document.getElementById("vpn-table")
        if (!table) return

        let html = `
        <tr>
        <th>Felhasználó</th>
        <th>Külső IP</th>
        <th>Kapcsolódott</th>
        <th>Duration</th>
        </tr>
        `

        sessions.forEach(s => {

            const flag = s.country_code
                ? getFlagEmoji(s.country_code) + " "
                : ""

            html += `
            <tr>
                <td>${s.username}</td>
                <td>${flag}${s.ip}</td>
                <td>${s.connected_at}</td>
                <td class="duration" data-start="${s.connected_at_iso}">
                    ${s.duration}
                </td>
            </tr>
            `
        })

        table.innerHTML = html

    }

    catch (err) {

        console.error("VPN table error:", err)

    }

}


// ================= VPN ALERT =================

async function checkNewVPNUsers() {

    try {

        const res = await fetch("/api/active-vpn/")
        const sessions = await res.json()

        sessions.forEach(session => {

            if (!knownUsers.has(session.username)) {

                knownUsers.add(session.username)
                showVPNToast(session)

            }

        })

    }

    catch (err) {

        console.error("VPN alert error:", err)

    }

}


function showVPNToast(session) {

    const container = document.getElementById("vpn-toast-container")
    if (!container) return

    const toast = document.createElement("div")

    toast.className = "vpn-toast"

    toast.innerHTML =
        `🟢 <b>${session.username}</b> connected from ${session.ip}`

    container.appendChild(toast)

    setTimeout(() => toast.remove(), 5000)

}


// ================= LIVE DURATION =================

function updateDurations() {

    const now = new Date()

    document.querySelectorAll(".duration").forEach(el => {

        const start = parseISODate(el.dataset.start)

        if (!start) return

        const diff = Math.floor((now - start) / 1000)

        if (diff < 0) return

        const h = Math.floor(diff / 3600)
        const m = Math.floor((diff % 3600) / 60)
        const s = diff % 60

        el.innerText =
            String(h).padStart(2, "0") + ":" +
            String(m).padStart(2, "0") + ":" +
            String(s).padStart(2, "0")

    })

}


// ================= CLOCK =================

function updateClock() {

    const now = new Date()

    const time =
        String(now.getHours()).padStart(2, "0") + ":" +
        String(now.getMinutes()).padStart(2, "0") + ":" +
        String(now.getSeconds()).padStart(2, "0")

    const date =
        now.getFullYear() + "." +
        String(now.getMonth() + 1).padStart(2, "0") + "." +
        String(now.getDate()).padStart(2, "0")

    setText("clock-time", time)
    setText("clock-date", date)

}


// ================= INIT =================

function init() {

    initMap()

    updateDashboardStats()
    refreshVPNSessions()
    updateClock()

    setInterval(updateDashboardStats, 5000)
    setInterval(refreshVPNSessions, 10000)
    setInterval(checkNewVPNUsers, 5000)
    setInterval(updateDurations, 1000)
    setInterval(updateClock, 1000)

}

document.addEventListener("DOMContentLoaded", init)
