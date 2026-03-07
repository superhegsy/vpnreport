import os
import sys
import django

# projekt root hozzáadása a path-hoz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vpnreport.settings")

django.setup()

from vpn.collector import collect_fortigate_sessions

collect_fortigate_sessions()
