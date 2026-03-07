// =====================================================
// VPN DASHBOARD SCRIPT
// =====================================================



// =====================================================
// HQ KOORDINÁTÁK
// =====================================================

const HQ = [47.4979, 19.0402]; // Budapest



// =====================================================
// FLAG EMOJI
// =====================================================

function getFlagEmoji(countryCode) {

    if (!countryCode) return "";

    return countryCode
        .toUpperCase()
        .replace(/./g, char =>
            String.fromCodePoint(127397 + char.charCodeAt())
        );
}



// =====================================================
// TÉRKÉP INITIALIZÁLÁS
// =====================================================

const map = L.map("map").setView(HQ, 6);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18
}).addTo(map);


// HQ marker

L.marker(HQ)
    .addTo(map)
    .bindPopup("VPN Gateway (Budapest HQ)");



// =====================================================
// VPN USER LOKÁCIÓK + AUTO ZOOM
// =====================================================

fetch("/api/vpn-locations/")
.then(res => res.json())
.then(data => {

    const bounds = [];

    data.forEach(session => {

        if (!session.lat || !session.lon) return;

        const userLocation = [session.lat, session.lon];
        const flag = getFlagEmoji(session.country_code);

        bounds.push(userLocation);

        // USER MARKER

        const marker = L.marker(userLocation).addTo(map);

        // HOVER TOOLTIP

        marker.bindTooltip(
            `<b>${session.username}</b><br>${flag} ${session.ip}`,
            {
                direction: "top",
                offset: [0, -10],
                opacity: 0.9
            }
        );

        // HQ → USER kapcsolat vonal

        L.polyline([HQ, userLocation], {
            color: "#4ea67d",
            weight: 2,
            opacity: 0.7,
            dashArray: "5,10"
        }).addTo(map);

        // Rövid villanás effekt

        const pulse = L.circle(userLocation, {
            radius: 30000,
            color: "#d7a300",
            fillOpacity: 0.3
        }).addTo(map);

        setTimeout(() => map.removeLayer(pulse), 2000);

    });

    // =====================================================
    // AUTOMATIKUS ZOOM A USEREKRE
    // =====================================================

    if (bounds.length > 0) {

        bounds.push(HQ);

        map.fitBounds(bounds, {
            padding: [80, 80]
        });

    }

});



// =====================================================
// DASHBOARD STATISZTIKA FRISSÍTÉS
// =====================================================

function updateDashboardStats() {

    fetch("/api/dashboard-stats/")
    .then(res => res.json())
    .then(data => {

        const active = document.getElementById("stat-active");
        const today = document.getElementById("stat-today");
        const total = document.getElementById("stat-total");
        const top = document.getElementById("stat-topuser");

        if (active) active.innerText = data.active_users;
        if (today) today.innerText = data.today_sessions;
        if (total) total.innerText = data.total_sessions;
        if (top) top.innerText = data.top_user;

    });

}

setInterval(updateDashboardStats, 5000);



// =====================================================
// ZÁSZLÓ AZ IP ELŐTT
// =====================================================

document.querySelectorAll(".ip-flag").forEach(el => {

    const code = el.dataset.code;

    if (code) {
        el.innerText = getFlagEmoji(code) + " ";
    }

});



// =====================================================
// VPN SESSION TABLE AUTO REFRESH
// =====================================================

async function refreshVPNSessions() {

    try {

        const response = await fetch("/api/active-vpn/");
        const sessions = await response.json();

        const table = document.querySelector("#vpn-table");

        if (!table) return;

        let rows = `
        <tr>
            <th>Felhasználó</th>
            <th>Külső IP</th>
            <th>Kapcsolódott</th>
            <th>Duration</th>
        </tr>
        `;

        sessions.forEach(s => {

            const flag = s.country_code ? getFlagEmoji(s.country_code) + " " : "";

            rows += `
            <tr>
                <td>${s.username}</td>
                <td>${flag}${s.ip}</td>
                <td>${s.connected_at}</td>
                <td class="duration" data-start="${s.connected_at_iso}">
                    ${s.duration}
                </td>
            </tr>
            `;

        });

        table.innerHTML = rows;

    } catch (err) {

        console.log("VPN refresh error:", err);

    }

}

setInterval(refreshVPNSessions, 10000);



// =====================================================
// VPN CONNECT ALERT
// =====================================================

let knownUsers = new Set();

async function checkNewVPNUsers() {

    try {

        const response = await fetch("/api/active-vpn/");
        const sessions = await response.json();

        sessions.forEach(session => {

            if (!knownUsers.has(session.username)) {

                knownUsers.add(session.username);

                showVPNToast(session);

            }

        });

    } catch (err) {

        console.log("VPN alert error:", err);

    }

}



function showVPNToast(session) {

    const container = document.getElementById("vpn-toast-container");

    if (!container) return;

    const toast = document.createElement("div");

    toast.className = "vpn-toast";

    toast.innerHTML = `🟢 <b>${session.username}</b> connected from ${session.ip}`;

    container.appendChild(toast);

    setTimeout(() => toast.remove(), 5000);

}

setInterval(checkNewVPNUsers, 5000);



// =====================================================
// LIVE VPN DURATION COUNTER
// =====================================================

function updateDurations() {

    const elements = document.querySelectorAll(".duration");

    elements.forEach(el => {

        const start = new Date(el.dataset.start);
        const now = new Date();

        const diff = Math.floor((now - start) / 1000);

        const hours = Math.floor(diff / 3600);
        const minutes = Math.floor((diff % 3600) / 60);
        const seconds = diff % 60;

        el.innerText =
            String(hours).padStart(2, "0") + ":" +
            String(minutes).padStart(2, "0") + ":" +
            String(seconds).padStart(2, "0");

    });

}

setInterval(updateDurations, 1000);
