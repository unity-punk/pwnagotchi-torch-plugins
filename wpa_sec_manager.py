import os
import io
import csv
import hashlib
import logging
import subprocess
import pwnagotchi.plugins as plugins
from flask import render_template_string, redirect, Response, send_from_directory, abort

HTML_TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "plugins" %}

{% block title %}
    WPA-SEC Potfile Manager
{% endblock %}

{% block styles %}
{{ super() }}
    <style>
        .wsm-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        #wsmSearch {
            flex: 1;
            min-width: 220px;
            padding: 8px 10px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .wsm-btn {
            padding: 8px 14px;
            font-size: 15px;
            background-color: #2c3e50;
            color: #fff;
            border: none;
            border-radius: 4px;
            text-decoration: none;
            cursor: pointer;
            display: inline-block;
        }
        .wsm-btn:hover {
            background-color: #1a252f;
        }
        .wsm-btn-csv {
            background-color: #27ae60;
        }
        .wsm-btn-csv:hover {
            background-color: #1e8449;
        }
        .wsm-btn-qr {
            padding: 5px 10px;
            font-size: 13px;
            background-color: #2980b9;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .wsm-btn-qr:hover {
            background-color: #1f618d;
        }
        .wsm-stats {
            margin-bottom: 10px;
            font-weight: bold;
        }
        .wsm-table {
            width: 100%;
            border-collapse: collapse;
        }
        .wsm-table th, .wsm-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            word-break: break-all;
        }
        .wsm-table th {
            background-color: #f4f4f4;
        }
        /* QR Popup Modal */
        .wsm-modal {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.65);
        }
        .wsm-modal-content {
            background-color: #fff;
            margin: 8% auto;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 340px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        .wsm-modal-content img {
            width: 240px;
            height: 240px;
            margin: 12px 0;
            border: 1px solid #eee;
        }
        .wsm-close {
            float: right;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            color: #555;
            line-height: 1;
        }
        .wsm-close:hover {
            color: #000;
        }
    </style>
{% endblock %}

{% block content %}
    <h2>WPA-SEC Potfile Manager</h2>
    
    <div class="wsm-stats">
        Showing <span id="wsmCount">{{ entries|length }}</span> of {{ entries|length }} unique SSIDs
    </div>
    
    <div class="wsm-controls">
        <input type="text" id="wsmSearch" onkeyup="filterPotfile()" placeholder="Search by SSID, Password, BSSID, or Station...">
        <a href="/plugins/wpa_sec_manager/clean" class="wsm-btn">Sort & Remove Duplicates</a>
        <a href="/plugins/wpa_sec_manager/export" class="wsm-btn wsm-btn-csv">Export to CSV</a>
    </div>
    
    <table class="wsm-table" id="wsmTable">
        <thead>
            <tr>
                <th>SSID</th>
                <th>Password</th>
                <th>BSSID (AP)</th>
                <th>Station MAC</th>
                <th>Connect</th>
            </tr>
        </thead>
        <tbody>
            {% for row in entries %}
            <tr>
                <td><strong>{{ row.ssid }}</strong></td>
                <td><code>{{ row.password }}</code></td>
                <td>{{ row.bssid }}</td>
                <td>{{ row.station }}</td>
                <td>
                    {% if row.qr_file %}
                    <button type="button"
                            class="wsm-btn-qr"
                            data-ssid="{{ row.ssid }}"
                            data-pass="{{ row.password }}"
                            data-img="/plugins/wpa_sec_manager/qr/{{ row.qr_file }}"
                            onclick="openQrModal(this)">
                        QR Code
                    </button>
                    {% else %}
                    <span>N/A</span>
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="5">No entries found in {{ potfile_path }}.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <!-- QR Popup Modal -->
    <div id="qrModal" class="wsm-modal" onclick="closeQrModal(event)">
        <div class="wsm-modal-content" onclick="event.stopPropagation()">
            <span class="wsm-close" onclick="document.getElementById('qrModal').style.display='none'">&times;</span>
            <h3 id="modalSsid" style="margin-top: 5px; word-break: break-all;"></h3>
            <img id="modalQrImg" src="" alt="Wi-Fi QR Code">
            <p style="margin: 5px 0;">Password: <code id="modalPass"></code></p>
        </div>
    </div>
    
    <script>
        function filterPotfile() {
            const query = document.getElementById("wsmSearch").value.toLowerCase();
            const rows = document.getElementById("wsmTable").getElementsByTagName("tr");
            let visible = 0;
            
            for (let i = 1; i < rows.length; i++) {
                const text = (rows[i].textContent || rows[i].innerText).toLowerCase();
                if (text.indexOf(query) !== -1) {
                    rows[i].style.display = "";
                    visible++;
                } else {
                    rows[i].style.display = "none";
                }
            }
            document.getElementById("wsmCount").innerText = visible;
        }
        
        function openQrModal(btn) {
            document.getElementById("modalSsid").innerText = btn.getAttribute("data-ssid");
            document.getElementById("modalPass").innerText = btn.getAttribute("data-pass");
            document.getElementById("modalQrImg").src = btn.getAttribute("data-img");
            document.getElementById("qrModal").style.display = "block";
        }
        
        function closeQrModal(event) {
            if (event.target.id === "qrModal") {
                document.getElementById("qrModal").style.display = "none";
            }
        }
    </script>
{% endblock %}
"""
class WpaSecManager(plugins.Plugin):
    __author__ = '666'
    __version__ = '1.2.0'
    __license__ = 'GPL3'
    __description__ = 'Deduplicates by SSID, sorts, exports CSV, generates local QR codes, and provides a searchable Web UI.'

    def __init__(self):
        self.potfile_path = '/etc/pwnagotchi/handshakes/wpa-sec.cracked.potfile'
        self.qr_dir = '/etc/pwnagotchi/handshakes/qrcodes'
        self.last_mtime = 0

    def on_loaded(self):
        if 'potfile_path' in self.options:
            self.potfile_path = self.options['potfile_path']
        if 'qr_dir' in self.options:
            self.qr_dir = self.options['qr_dir']

        os.makedirs(self.qr_dir, exist_ok=True)
        logging.info(f"[wpa_sec_manager] Loaded. Potfile: {self.potfile_path} | QR dir: {self.qr_dir}")
        self.clean_and_sort()

    def on_internet_available(self, agent):
        if os.path.exists(self.potfile_path):
            mtime = os.path.getmtime(self.potfile_path)
            if mtime != self.last_mtime:
                self.clean_and_sort()

    @staticmethod
    def _escape_wifi_field(value):
        for ch in ('\\', ';', ',', '"', ':'):
            value = value.replace(ch, '\\' + ch)
        return value

    def ensure_qr_code(self, ssid, password):
        if not ssid:
            return None

        os.makedirs(self.qr_dir, exist_ok=True)
        digest = hashlib.sha256(f"{ssid}\x00{password}".encode('utf-8')).hexdigest()[:16]
        filename = f"{digest}.png"
        filepath = os.path.join(self.qr_dir, filename)

        if os.path.exists(filepath):
            return filename

        esc_ssid = self._escape_wifi_field(ssid)
        if password:
            esc_pass = self._escape_wifi_field(password)
            payload = f"WIFI:T:WPA;S:{esc_ssid};P:{esc_pass};;"
        else:
            payload = f"WIFI:T:nopass;S:{esc_ssid};;"

        try:
            subprocess.run(
                ['qrencode', '-o', filepath, '-s', '6', '-m', '2', payload],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            return filename
        except FileNotFoundError:
            logging.error("[wpa_sec_manager] 'qrencode' is not installed. Run: sudo apt-get install -y qrencode")
            return None
        except subprocess.CalledProcessError as e:
            logging.error(f"[wpa_sec_manager] qrencode failed for {ssid}: {e.stderr.decode('utf-8', errors='replace')}")
            return None

    def read_entries(self, generate_qr=False):
        entries = []
        if not os.path.exists(self.potfile_path):
            return entries

        seen_ssids = set()
        try:
            with open(self.potfile_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    raw = line.strip()
                    if not raw:
                        continue

                    parts = raw.split(':', 3)
                    if len(parts) == 4:
                        bssid, station, ssid, password = parts
                        if ssid in seen_ssids:
                            continue
                        seen_ssids.add(ssid)

                        qr_file = self.ensure_qr_code(ssid, password) if generate_qr else None
                        entries.append({
                            'bssid': bssid,
                            'station': station,
                            'ssid': ssid,
                            'password': password,
                            'qr_file': qr_file,
                            'raw': raw
                        })
                    else:
                        if raw in seen_ssids:
                            continue
                        seen_ssids.add(raw)
                        entries.append({
                            'bssid': '',
                            'station': '',
                            'ssid': raw,
                            'password': '',
                            'qr_file': None,
                            'raw': raw
                        })
        except Exception as e:
            logging.error(f"[wpa_sec_manager] Error reading {self.potfile_path}: {e}")

        entries.sort(key=lambda x: (x['ssid'].lower(), x['bssid'].lower()))
        return entries

    def clean_and_sort(self):
        if not os.path.exists(self.potfile_path):
            return

        entries = self.read_entries(generate_qr=True)
        output = ''.join(row['raw'] + '\n' for row in entries)

        try:
            with open(self.potfile_path, 'r', encoding='utf-8', errors='replace') as f:
                if f.read() == output:
                    self.last_mtime = os.path.getmtime(self.potfile_path)
                    return

            with open(self.potfile_path, 'w', encoding='utf-8') as f:
                f.write(output)

            self.last_mtime = os.path.getmtime(self.potfile_path)
            logging.info(f"[wpa_sec_manager] Cleaned, sorted, and generated QR codes for {len(entries)} entries.")
        except Exception as e:
            logging.error(f"[wpa_sec_manager] Error writing {self.potfile_path}: {e}")

    def export_csv(self):
        entries = self.read_entries(generate_qr=False)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['SSID', 'Password', 'BSSID', 'Station MAC'])
        for row in entries:
            writer.writerow([row['ssid'], row['password'], row['bssid'], row['station']])

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=wpa-sec-cracked.csv'}
        )

    def on_webhook(self, path, request):
        if path == 'clean':
            self.clean_and_sort()
            return redirect('/plugins/wpa_sec_manager/')
        elif path == 'export':
            return self.export_csv()
        elif path and path.startswith('qr/'):
            filename = os.path.basename(path[3:])
            if not filename.endswith('.png'):
                abort(404)
            return send_from_directory(self.qr_dir, filename)

        entries = self.read_entries(generate_qr=True)
        return render_template_string(
            HTML_TEMPLATE,
            entries=entries,
            potfile_path=self.potfile_path
        )