import customtkinter as ctk
import subprocess
import requests
from PIL import Image, ImageTk
from io import BytesIO
import platform
import psutil
import time

def get_system_info():
    info = {}
    try:
        # Hardware Information
        info['CPU'] = platform.processor()
        info['Cores'] = psutil.cpu_count(logical=False)
        info['Threads'] = psutil.cpu_count(logical=True)
        info['RAM'] = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
        
        # Windows Information
        info['OS'] = platform.system()
        info['OS Version'] = platform.version()
        info['OS Release'] = platform.release()
        
        # Network Information
        info['Hostname'] = platform.node()
        info['IP Address'] = requests.get('https://api.ipify.org').text
        
        # Disk Information
        disk = psutil.disk_usage('/')
        info['Disk Total'] = f"{round(disk.total / (1024**3), 2)} GB"
        info['Disk Used'] = f"{round(disk.used / (1024**3), 2)} GB"
        
    except Exception as e:
        info['Error'] = str(e)
    return info

def update_theme(choice):
    ctk.set_appearance_mode(choice)
    root.update()

def create_info_tab(parent):
    tab = ctk.CTkScrollableFrame(parent)
    
    info = get_system_info()
    for key, value in info.items():
        frame = ctk.CTkFrame(tab)
        label = ctk.CTkLabel(frame, text=f"{key}:", font=("Arial", 12, "bold"))
        value_label = ctk.CTkLabel(frame, text=value)
        copy_btn = ctk.CTkButton(frame, text="📋", width=30, command=lambda v=value: root.clipboard_append(v))
        
        label.pack(side="left", padx=5)
        value_label.pack(side="left", padx=5)
        copy_btn.pack(side="right", padx=5)
        frame.pack(fill="x", pady=2)
    
    return tab

def create_hwid_tab(parent):
    tab = ctk.CTkFrame(parent)
    
    hwid = subprocess.check_output(["powershell", "-Command", "(Get-WmiObject Win32_ComputerSystemProduct).UUID"], shell=True).decode().strip()
    
    hwid_frame = ctk.CTkFrame(tab)
    hwid_label = ctk.CTkLabel(hwid_frame, text=f"HWID: {hwid}", font=("Arial", 12))
    copy_btn = ctk.CTkButton(hwid_frame, text="Copy", command=lambda: root.clipboard_append(hwid))
    
    hwid_label.pack(side="left", padx=5)
    copy_btn.pack(side="right", padx=5)
    hwid_frame.pack(pady=20)
    
    return tab

def main():
    global root
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue")
    
    root = ctk.CTk()
    root.title("ag7-dev.de - HWID Tool")
    root.geometry("400x600") 
    
    theme_selector = ctk.CTkOptionMenu(root, values=["System", "Dark", "Light"], command=update_theme)
    theme_selector.pack(side="top", anchor="ne", padx=10, pady=10)
    
    tabview = ctk.CTkScrollableFrame(root)
    tabview.pack(expand=True, fill="both", padx=10, pady=10)
    
    tab1 = create_hwid_tab(tabview)
    tab2 = create_info_tab(tabview)
    
    tab1.pack(fill="both", expand=True)
    tab2.pack(fill="both", expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
