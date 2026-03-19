#!/usr/bin/env python3
"""
AQI Ventilation Monitor — Desktop GUI
======================================
Reads CSV data from ESP32 over USB-Serial (9600 baud) and displays:
  - Live AQI gauge with colour-coded category
  - Real-time sparkline charts for PM2.5, CO2, Temperature, Humidity
  - Scrolling data table
  - Automatic CSV logging to aqi_log_<date>.csv

Requirements:  pip install pyserial matplotlib
Python 3.8+

Usage:
  python aqi_monitor_gui.py              # auto-detect COM port
  python aqi_monitor_gui.py --port COM3  # specify port (Windows)
  python aqi_monitor_gui.py --port /dev/ttyUSB0  # Linux/macOS
"""

import argparse
import csv
import datetime
import os
import queue
import threading
import time
import tkinter as tk
from collections import deque
from tkinter import ttk, messagebox
import sys

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("ERROR: pyserial not installed.  Run:  pip install pyserial")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.animation as animation
except ImportError:
    print("ERROR: matplotlib not installed.  Run:  pip install matplotlib")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
BAUD_RATE      = 9600
HISTORY_POINTS = 60          # number of data points shown on charts
CHART_INTERVAL = 2000        # ms between chart refreshes
CSV_HEADER     = ["timestamp_ms", "pm1_0", "pm2_5", "pm10",
                  "co2_ppm", "temp_c", "humidity_pct", "aqi", "category",
                  "wall_time"]

AQI_COLOURS = {
    "Good":                ("#00e400", "#000000"),   # (bg, fg)
    "Moderate":            ("#ffff00", "#000000"),
    "Unhealthy_Sensitive": ("#ff7e00", "#ffffff"),
    "Unhealthy":           ("#ff0000", "#ffffff"),
    "Very_Unhealthy":      ("#8f3f97", "#ffffff"),
    "Hazardous":           ("#7e0023", "#ffffff"),
}

# ──────────────────────────────────────────────────────────────────────────────
# Serial reader thread
# ──────────────────────────────────────────────────────────────────────────────
class SerialReader(threading.Thread):
    def __init__(self, port: str, data_queue: queue.Queue):
        super().__init__(daemon=True)
        self.port       = port
        self.data_queue = data_queue
        self._stop_evt  = threading.Event()
        self.connected  = False
        self.error_msg  = ""

    def run(self):
        try:
            ser = serial.Serial(self.port, BAUD_RATE, timeout=2)
            self.connected = True
        except serial.SerialException as exc:
            self.error_msg = str(exc)
            self.connected = False
            return

        header_seen = False
        while not self._stop_evt.is_set():
            try:
                raw = ser.readline().decode("ascii", errors="ignore").strip()
            except serial.SerialException:
                break

            if not raw:
                continue

            # Skip the CSV header row from the ESP32
            if raw.startswith("timestamp_ms"):
                header_seen = True
                continue

            parts = raw.split(",")
            if len(parts) != 9:
                continue  # ignore malformed lines

            try:
                row = {
                    "timestamp_ms": int(parts[0]),
                    "pm1_0":        int(parts[1]),
                    "pm2_5":        int(parts[2]),
                    "pm10":         int(parts[3]),
                    "co2_ppm":      int(parts[4]),
                    "temp_c":       float(parts[5]),
                    "humidity_pct": float(parts[6]),
                    "aqi":          float(parts[7]),
                    "category":     parts[8],
                    "wall_time":    datetime.datetime.now().isoformat(timespec="seconds"),
                }
                self.data_queue.put(row)
            except (ValueError, IndexError):
                continue

        ser.close()

    def stop(self):
        self._stop_evt.set()


# ──────────────────────────────────────────────────────────────────────────────
# CSV logger
# ──────────────────────────────────────────────────────────────────────────────
class CSVLogger:
    def __init__(self, directory: str = "."):
        date_str  = datetime.date.today().strftime("%Y%m%d")
        filename  = f"aqi_log_{date_str}.csv"
        self.path = os.path.join(directory, filename)
        self._file   = open(self.path, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=CSV_HEADER)
        # Write header only if the file is new / empty
        if self._file.tell() == 0:
            self._writer.writeheader()

    def write(self, row: dict):
        self._writer.writerow({k: row.get(k, "") for k in CSV_HEADER})
        self._file.flush()

    def close(self):
        self._file.close()


# ──────────────────────────────────────────────────────────────────────────────
# Main GUI
# ──────────────────────────────────────────────────────────────────────────────
class AQIMonitorApp:
    def __init__(self, root: tk.Tk, port: str):
        self.root   = root
        self.port   = port
        self.queue  = queue.Queue()
        self.logger = CSVLogger()
        self.reader = SerialReader(port, self.queue)

        # Rolling history buffers (O(1) append/pop via deque)
        self.hist_aqi  : deque[float] = deque(maxlen=HISTORY_POINTS)
        self.hist_pm25 : deque[float] = deque(maxlen=HISTORY_POINTS)
        self.hist_co2  : deque[float] = deque(maxlen=HISTORY_POINTS)
        self.hist_temp : deque[float] = deque(maxlen=HISTORY_POINTS)
        self.hist_hum  : deque[float] = deque(maxlen=HISTORY_POINTS)
        self.hist_time : deque[str]   = deque(maxlen=HISTORY_POINTS)

        self._build_ui()
        self.reader.start()
        self.root.after(500, self._check_connection)
        self.root.after(1000, self._poll_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI construction ────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.title("🌬  AQI Ventilation Monitor")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)

        # ── Top bar ──
        top = tk.Frame(self.root, bg="#1e1e2e")
        top.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(top, text="AQI Ventilation Monitor",
                 font=("Helvetica", 18, "bold"),
                 fg="#cdd6f4", bg="#1e1e2e").pack(side="left")

        self.status_lbl = tk.Label(top, text=f"⚡  {self.port}  |  Connecting…",
                                   font=("Helvetica", 11),
                                   fg="#a6adc8", bg="#1e1e2e")
        self.status_lbl.pack(side="right")

        # ── AQI gauge ──
        gauge_frame = tk.Frame(self.root, bg="#1e1e2e")
        gauge_frame.pack(fill="x", padx=10, pady=8)

        self.aqi_val_lbl = tk.Label(gauge_frame, text="AQI\n---",
                                    font=("Helvetica", 48, "bold"),
                                    fg="#cdd6f4", bg="#313244",
                                    width=8, relief="ridge", bd=2)
        self.aqi_val_lbl.grid(row=0, column=0, padx=(0, 12))

        self.cat_lbl = tk.Label(gauge_frame, text="Waiting for data…",
                                font=("Helvetica", 22, "bold"),
                                fg="#cdd6f4", bg="#313244",
                                width=22, relief="ridge", bd=2)
        self.cat_lbl.grid(row=0, column=1, padx=(0, 12))

        self.rec_lbl = tk.Label(gauge_frame, text="",
                                font=("Helvetica", 12),
                                fg="#cdd6f4", bg="#313244",
                                wraplength=380, justify="left",
                                relief="ridge", bd=2, padx=8, pady=4)
        self.rec_lbl.grid(row=0, column=2, sticky="nsew")
        gauge_frame.columnconfigure(2, weight=1)

        # ── Sensor value cards ──
        cards = tk.Frame(self.root, bg="#1e1e2e")
        cards.pack(fill="x", padx=10, pady=4)

        self.card_vars = {}
        card_defs = [
            ("PM1.0",      "µg/m³", "#89b4fa"),
            ("PM2.5",      "µg/m³", "#f38ba8"),
            ("PM10",       "µg/m³", "#fab387"),
            ("CO₂",        "ppm",   "#a6e3a1"),
            ("Temperature","°C",    "#f9e2af"),
            ("Humidity",   "%",     "#89dceb"),
        ]
        for i, (label, unit, colour) in enumerate(card_defs):
            frame = tk.Frame(cards, bg="#313244", relief="ridge", bd=2)
            frame.grid(row=0, column=i, padx=4, sticky="ew")
            cards.columnconfigure(i, weight=1)
            tk.Label(frame, text=label, font=("Helvetica", 9, "bold"),
                     fg=colour, bg="#313244").pack()
            var = tk.StringVar(value="---")
            tk.Label(frame, textvariable=var,
                     font=("Helvetica", 18, "bold"),
                     fg="#cdd6f4", bg="#313244").pack()
            tk.Label(frame, text=unit, font=("Helvetica", 8),
                     fg="#a6adc8", bg="#313244").pack()
            self.card_vars[label] = var

        # ── Charts ──
        chart_frame = tk.Frame(self.root, bg="#1e1e2e")
        chart_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self.fig = Figure(figsize=(12, 3.5), facecolor="#1e1e2e")
        self.fig.subplots_adjust(hspace=0.4, wspace=0.35)

        ax_kwargs = {"facecolor": "#313244"}
        n_cols = 4
        self.ax_aqi  = self.fig.add_subplot(1, n_cols, 1, **ax_kwargs)
        self.ax_pm25 = self.fig.add_subplot(1, n_cols, 2, **ax_kwargs)
        self.ax_co2  = self.fig.add_subplot(1, n_cols, 3, **ax_kwargs)
        self.ax_env  = self.fig.add_subplot(1, n_cols, 4, **ax_kwargs)

        for ax in (self.ax_aqi, self.ax_pm25, self.ax_co2, self.ax_env):
            ax.tick_params(colors="#a6adc8", labelsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor("#585b70")

        self.ax_aqi.set_title("AQI",         color="#cdd6f4", fontsize=9)
        self.ax_pm25.set_title("PM2.5 µg/m³",color="#cdd6f4", fontsize=9)
        self.ax_co2.set_title("CO₂ ppm",     color="#cdd6f4", fontsize=9)
        self.ax_env.set_title("Temp °C / Hum %", color="#cdd6f4", fontsize=9)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # ── Data table ──
        table_frame = tk.Frame(self.root, bg="#1e1e2e")
        table_frame.pack(fill="x", padx=10, pady=(0, 6))

        cols = ("Time", "PM2.5", "CO₂", "Temp", "Humidity", "AQI", "Category")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                 show="headings", height=5)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#313244", foreground="#cdd6f4",
                        fieldbackground="#313244", rowheight=20)
        style.configure("Treeview.Heading",
                        background="#45475a", foreground="#cdd6f4", font=("Helvetica", 9, "bold"))
        col_widths = [80, 60, 60, 60, 70, 60, 140]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="x", expand=True)
        vsb.pack(side="right", fill="y")

        # ── CSV path label ──
        self.csv_lbl = tk.Label(self.root,
                                text=f"📄  Logging → {self.logger.path}",
                                font=("Helvetica", 9), fg="#a6adc8", bg="#1e1e2e")
        self.csv_lbl.pack(pady=(0, 4))

    # ── Connection check ───────────────────────────────────────────────────
    def _check_connection(self):
        if not self.reader.connected and self.reader.error_msg:
            messagebox.showerror(
                "Serial Error",
                f"Cannot open {self.port}:\n{self.reader.error_msg}\n\n"
                "Check the port and restart the app."
            )
            self.status_lbl.config(text=f"❌  {self.port}  |  Error")
        elif self.reader.connected:
            self.status_lbl.config(text=f"✅  {self.port}  |  9600 baud  |  Connected")
        else:
            self.root.after(500, self._check_connection)

    # ── Queue polling ──────────────────────────────────────────────────────
    def _poll_queue(self):
        updated = False
        while not self.queue.empty():
            row = self.queue.get_nowait()
            self._process_row(row)
            updated = True

        if updated:
            self._refresh_charts()

        self.root.after(1000, self._poll_queue)

    def _process_row(self, row: dict):
        # Log to CSV
        self.logger.write(row)

        # Update history
        self.hist_aqi.append(row["aqi"])
        self.hist_pm25.append(row["pm2_5"])
        self.hist_co2.append(row["co2_ppm"])
        self.hist_temp.append(row["temp_c"])
        self.hist_hum.append(row["humidity_pct"])
        t = row["wall_time"][11:19]  # HH:MM:SS
        self.hist_time.append(t)

        # Update gauge
        aqi     = row["aqi"]
        cat     = row["category"]
        bg, fg  = AQI_COLOURS.get(cat, ("#313244", "#cdd6f4"))
        self.aqi_val_lbl.config(text=f"AQI\n{aqi:.0f}", bg=bg, fg=fg)
        self.cat_lbl.config(text=cat.replace("_", " "), bg=bg, fg=fg)
        self.rec_lbl.config(text=self._health_rec(cat), bg=bg, fg=fg)

        # Update cards
        self.card_vars["PM1.0"].set(str(row["pm1_0"]))
        self.card_vars["PM2.5"].set(str(row["pm2_5"]))
        self.card_vars["PM10"].set(str(row["pm10"]))
        self.card_vars["CO₂"].set(str(row["co2_ppm"]))
        self.card_vars["Temperature"].set(f"{row['temp_c']:.1f}")
        self.card_vars["Humidity"].set(f"{row['humidity_pct']:.1f}")

        # Update table (newest row at top)
        self.tree.insert("", 0, values=(
            t,
            row["pm2_5"],
            row["co2_ppm"],
            f"{row['temp_c']:.1f}",
            f"{row['humidity_pct']:.1f}",
            f"{row['aqi']:.1f}",
            cat.replace("_", " "),
        ))
        # Keep table to 50 rows
        children = self.tree.get_children()
        if len(children) > 50:
            self.tree.delete(children[-1])

    def _health_rec(self, category: str) -> str:
        recs = {
            "Good":                "✅ Excellent air quality. No action needed.",
            "Moderate":            "ℹ️  Acceptable. Unusually sensitive people may want to limit outdoor exertion.",
            "Unhealthy_Sensitive": "⚠️  Increase ventilation. Sensitive groups should reduce prolonged exertion.",
            "Unhealthy":           "🔴 Open windows / run mechanical ventilation. Limit prolonged exertion.",
            "Very_Unhealthy":      "🚨 Run air purifier. Avoid prolonged exertion. Close external doors.",
            "Hazardous":           "☠️  Hazardous! Maximum ventilation. Consider evacuating the room.",
        }
        return recs.get(category, "")

    # ── Chart refresh ──────────────────────────────────────────────────────
    def _refresh_charts(self):
        xs = range(len(self.hist_aqi))

        def _plot(ax, data, colour, ylabel=""):
            ax.clear()
            ax.set_facecolor("#313244")
            ax.tick_params(colors="#a6adc8", labelsize=7)
            for sp in ax.spines.values():
                sp.set_edgecolor("#585b70")
            if data:
                ax.plot(list(xs)[-len(data):], data, color=colour, linewidth=1.5)
                ax.fill_between(list(xs)[-len(data):], data,
                                alpha=0.25, color=colour)
                ax.set_ylim(bottom=0)

        _plot(self.ax_aqi,  self.hist_aqi,  "#f38ba8"); self.ax_aqi.set_title("AQI",          color="#cdd6f4", fontsize=9)
        _plot(self.ax_pm25, self.hist_pm25, "#89b4fa"); self.ax_pm25.set_title("PM2.5 µg/m³", color="#cdd6f4", fontsize=9)
        _plot(self.ax_co2,  self.hist_co2,  "#a6e3a1"); self.ax_co2.set_title("CO₂ ppm",      color="#cdd6f4", fontsize=9)

        # Temperature + Humidity on same axes
        self.ax_env.clear()
        self.ax_env.set_facecolor("#313244")
        self.ax_env.tick_params(colors="#a6adc8", labelsize=7)
        for sp in self.ax_env.spines.values():
            sp.set_edgecolor("#585b70")
        if self.hist_temp:
            xv = list(range(len(self.hist_temp)))
            self.ax_env.plot(xv, self.hist_temp, color="#f9e2af",
                             linewidth=1.5, label="Temp °C")
            self.ax_env.plot(xv, self.hist_hum,  color="#89dceb",
                             linewidth=1.5, label="Hum %")
            self.ax_env.legend(fontsize=7, facecolor="#313244",
                               labelcolor="#cdd6f4", framealpha=0.6)
        self.ax_env.set_title("Temp / Hum", color="#cdd6f4", fontsize=9)

        self.canvas.draw_idle()

    # ── Close handler ──────────────────────────────────────────────────────
    def _on_close(self):
        self.reader.stop()
        self.logger.close()
        self.root.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Port auto-detection
# ──────────────────────────────────────────────────────────────────────────────
def auto_detect_port() -> str:
    """Return the first USB-Serial port that looks like an ESP32."""
    candidates = []
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if any(k in desc or k in hwid for k in
               ("cp210", "ch340", "ch341", "ftdi", "silabs", "usb serial", "esp32")):
            candidates.append(p.device)

    if candidates:
        return candidates[0]

    # Fallback: first available port
    all_ports = [p.device for p in serial.tools.list_ports.comports()]
    if all_ports:
        return all_ports[0]

    return "/dev/ttyUSB0"  # last-resort default


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="AQI Ventilation Monitor — reads ESP32 over USB-Serial")
    parser.add_argument("--port", default=None,
                        help="Serial port (e.g. COM3 or /dev/ttyUSB0). "
                             "Auto-detected if omitted.")
    args = parser.parse_args()

    port = args.port or auto_detect_port()
    print(f"Using serial port: {port}")

    root = tk.Tk()
    root.geometry("1100x720")
    AQIMonitorApp(root, port)
    root.mainloop()


if __name__ == "__main__":
    main()
