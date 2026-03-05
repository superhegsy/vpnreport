# VPN Monitoring Dashboard

![Python](https://img.shields.io/badge/python-3.x-blue)
![Django](https://img.shields.io/badge/django-6.x-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A Django-based VPN monitoring dashboard that visualizes VPN connections on a world map and generates usage reports.

The system parses VPN logs (for example FortiGate IPsec logs), stores sessions in a database and displays them in a real-time dashboard.

---

# Dashboard Preview

![Dashboard Screenshot](docs/dashboard.png)

---

# Features

- VPN session monitoring
- World map visualization (Leaflet)
- GeoIP location lookup
- Country statistics chart
- Country flags in map and table
- Live dashboard statistics
- VPN session table
- PDF reports (daily / weekly / monthly)
- Real-time dashboard updates

---

# Architecture
