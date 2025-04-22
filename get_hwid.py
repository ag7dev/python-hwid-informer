import customtkinter as ctk
import subprocess
import requests
import platform
import psutil
import socket
import uuid
import datetime
from typing import Dict

def get_system_info() -> Dict[str, str]:
    info = {}
    try:
        # Operating System Info
        info['Operating System'] = f"{platform.system()} {platform.release()} (Build {platform.version()})"
        info['System Type'] = platform.architecture()[0]
        info['Hostname'] = platform.node()

        # Boot & Uptime Info
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        info['Boot Time'] = boot_time.strftime("%Y-%m-%d %H:%M:%S")
        info['Uptime'] = str(uptime).split('.')[0]

        # Processor Info
        info['Processor'] = platform.processor()
        info['Physical Cores'] = str(psutil.cpu_count(logical=False))
        info['Logical Cores'] = str(psutil.cpu_count(logical=True))

        # CPU Frequency
        try:
            freq = psutil.cpu_freq()
            info['CPU Frequency'] = f"Current: {round(freq.current, 2)} MHz | Min: {round(freq.min, 2)} MHz | Max: {round(freq.max, 2)} MHz"
        except:
            info['CPU Frequency'] = "Unavailable"

        # Memory Info
        mem = psutil.virtual_memory()
        info['Total RAM'] = f"{round(mem.total / (1024**3), 2)} GB"
        info['Available RAM'] = f"{round(mem.available / (1024**3), 2)} GB"

        # Disk Info
        disks = []
        for part in psutil.disk_partitions():
            if 'fixed' in part.opts.lower():
                usage = psutil.disk_usage(part.mountpoint)
                disks.append(f"{part.device} ({part.fstype}) - "
                             f"{round(usage.used / (1024**3), 1)}GB / {round(usage.total / (1024**3), 1)}GB")
        info['Disks'] = "\n".join(disks) if disks else "No disks found"

        # Network Interfaces
        try:
            interfaces = psutil.net_if_addrs()
            net_info = []
            for iface, addrs in interfaces.items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        net_info.append(f"{iface}: {addr.address}")
            info['Network Interfaces'] = "\n".join(net_info) if net_info else "No interfaces found"
        except:
            info['Network Interfaces'] = "Unavailable"

        # MAC Address
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(40, -1, -8)])
            info['MAC Address'] = mac
        except:
            info['MAC Address'] = "Unavailable"

        # Public IP
        try:
            info['Public IP'] = requests.get('https://api.ipify.org', timeout=5).text
        except:
            info['Public IP'] = "Unavailable"

        # GPU Info
        try:
            gpu = subprocess.check_output(
                "wmic path win32_VideoController get name",
                shell=True,
                stderr=subprocess.STDOUT
            ).decode().split('\n')[1].strip()
            info['Graphics Card'] = gpu if gpu else "Not detected"
        except:
            info['Graphics Card'] = "Unavailable"

        # Motherboard Info
        try:
            baseboard = subprocess.check_output(
                "wmic baseboard get product,Manufacturer",
                shell=True,
                stderr=subprocess.STDOUT
            ).decode().split('\n')[1].strip()
            info['Motherboard'] = baseboard if baseboard else "Not detected"
        except:
            info['Motherboard'] = "Unavailable"

        # BIOS Info
        try:
            bios = subprocess.check_output(
                "wmic bios get smbiosbiosversion",
                shell=True,
                stderr=subprocess.STDOUT
            ).decode().split('\n')[1].strip()
            info['BIOS Version'] = bios if bios else "Not detected"
        except:
            info['BIOS Version'] = "Unavailable"

        # Logged In Users
        try:
            users = psutil.users()
            info['Logged In Users'] = ", ".join([u.name for u in users]) if users else "None"
        except:
            info['Logged In Users'] = "Unavailable"

        # Battery Info
        battery = psutil.sensors_battery()
        if battery:
            info['Battery'] = f"{battery.percent}% remaining"
            info['On AC Power'] = "Yes" if battery.power_plugged else "No"
        else:
            info['Battery'] = "Unavailable"

    except Exception as e:
        info['Error'] = str(e)
    return info

def create_info_tab(parent) -> ctk.CTkScrollableFrame:
    tab = ctk.CTkScrollableFrame(parent)

    info = get_system_info()
    for key, value in info.items():
        frame = ctk.CTkFrame(tab, corner_radius=5)
        label = ctk.CTkLabel(frame, text=f"{key}:", width=180, anchor="w")
        value_label = ctk.CTkLabel(frame, text=value, wraplength=350, anchor="w", justify="left")
        copy_btn = ctk.CTkButton(
            frame,
            text="📋",
            width=30,
            command=lambda v=value: (root.clipboard_clear(), root.clipboard_append(v))
        )

        frame.grid_columnconfigure(1, weight=1)
        label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        value_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        copy_btn.grid(row=0, column=2, padx=5, pady=2)
        frame.pack(fill="x", pady=2)

    return tab

def get_hwid() -> str:
    try:
        return subprocess.check_output(
            "wmic csproduct get uuid",
            shell=True,
            stderr=subprocess.STDOUT
        ).decode().split('\n')[1].strip()
    except Exception as e:
        return f"Error retrieving HWID: {str(e)}"

def create_hwid_tab(parent) -> ctk.CTkFrame:
    tab = ctk.CTkFrame(parent)

    hwid = get_hwid()
    hwid_frame = ctk.CTkFrame(tab, corner_radius=10)
    ctk.CTkLabel(hwid_frame, text="HWID:", font=("Arial", 14, "bold")).pack(pady=5)

    textbox = ctk.CTkTextbox(hwid_frame, height=50, width=300)
    textbox.insert("1.0", hwid)
    textbox.configure(state="disabled")
    textbox.pack(pady=5, padx=10)

    copy_btn = ctk.CTkButton(
        hwid_frame,
        text="Copy HWID",
        command=lambda: (root.clipboard_clear(), root.clipboard_append(hwid))
    )
    copy_btn.pack(pady=10)

    hwid_frame.pack(pady=20, padx=20, fill="both", expand=True)
    return tab

def main():
    global root
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("ag7-dev.de - System Info Tool")
    root.geometry("700x800")
    root.minsize(650, 600)

    # Theme Selector
    theme_frame = ctk.CTkFrame(root)
    theme_frame.pack(pady=10, padx=10, fill="x")
    ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left", padx=10)
    theme_selector = ctk.CTkOptionMenu(
        theme_frame,
        values=["System", "Dark", "Light"],
        command=lambda mode: ctk.set_appearance_mode(mode)
    )
    theme_selector.pack(side="right", padx=10)

    # Tabs
    tabview = ctk.CTkTabview(root)
    tabview.pack(expand=True, fill="both", padx=10, pady=10)

    tab1 = tabview.add("HWID")
    tab2 = tabview.add("System Info")

    create_hwid_tab(tab1).pack(expand=True, fill="both")
    create_info_tab(tab2).pack(expand=True, fill="both")

    root.mainloop()

if __name__ == "__main__":
    main()
