import customtkinter as ctk
import requests
import webbrowser
import threading
import time
from tkinter import filedialog

# OS download links
os_links = {
    "FreeBSD 14.2-RELEASE (amd64)": "https://download.freebsd.org/ftp/releases/ISO-IMAGES/14.2/FreeBSD-14.2-RELEASE-amd64-disc1.iso",
    "Arch Linux (Latest ISO)": "https://geo.mirror.pkgbuild.com/iso/latest/archlinux-x86_64.iso",
    "Windows 10 (Open browser for ISO)": "https://www.microsoft.com/software-download/windows10"
}

# Stop flag
stop_download_flag = {"stop": False}

# Convert seconds to min:sec format
def format_eta(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}m {seconds}s"

# Download function
def download_os(name, url, status_label, progress_bar, path_entry, speed_label):
    if "microsoft.com" in url:
        status_label.configure(text="Opening browser for Windows 10 download...")
        webbrowser.open(url)
        return

    filename = path_entry.get().strip()
    if not filename:
        status_label.configure(text="Please select a save location.")
        return

    status_label.configure(text=f"Downloading {name}...")
    progress_bar.set(0)
    stop_download_flag["stop"] = False
    speed_label.configure(text="")

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = int(r.headers.get('content-length', 0))
            downloaded = 0
            start_time = time.time()

            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if stop_download_flag["stop"]:
                        status_label.configure(text="Download canceled.")
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = downloaded / total_length
                        progress_bar.set(progress)

                        elapsed = time.time() - start_time
                        speed = downloaded / (1024 * 1024) / elapsed if elapsed > 0 else 0
                        remaining = total_length - downloaded
                        eta = remaining / (speed * 1024 * 1024) if speed > 0 else 0

                        speed_label.configure(
                            text=f"Speed: {speed:.2f} MB/s | ETA: {format_eta(eta)}"
                        )

        status_label.configure(text=f"{name} downloaded successfully.")
        speed_label.configure(text="Download complete.")
    except Exception as e:
        status_label.configure(text=f"Error: {e}")
        speed_label.configure(text="")

# Start download thread
def start_download(os_choice, status_label, progress_bar, path_entry, speed_label):
    name = os_choice.get()
    url = os_links[name]
    threading.Thread(
        target=download_os,
        args=(name, url, status_label, progress_bar, path_entry, speed_label),
        daemon=True
    ).start()

# Stop download
def stop_download(status_label, speed_label):
    stop_download_flag["stop"] = True
    status_label.configure(text="Stopping download...")
    speed_label.configure(text="")

# Browse save location
def browse_file(path_entry, os_choice):
    default_name = os_links[os_choice.get()].split("/")[-1]
    file_path = filedialog.asksaveasfilename(
        defaultextension=".iso",
        filetypes=[("ISO files", "*.iso")],
        initialfile=default_name
    )
    if file_path:
        path_entry.delete(0, ctk.END)
        path_entry.insert(0, file_path)

# Main GUI
def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("OS Downloader")
    app.geometry("500x420")

    title = ctk.CTkLabel(app, text="Select an OS to Download", font=ctk.CTkFont(size=18, weight="bold"))
    title.pack(pady=20)

    os_choice = ctk.CTkOptionMenu(app, values=list(os_links.keys()))
    os_choice.set("FreeBSD 14.2-RELEASE (amd64)")
    os_choice.pack(pady=10)

    path_frame = ctk.CTkFrame(app)
    path_frame.pack(pady=10, padx=10, fill="x")

    path_entry = ctk.CTkEntry(path_frame, placeholder_text="Choose save location")
    path_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)

    browse_btn = ctk.CTkButton(path_frame, text="Browse", width=80, command=lambda: browse_file(path_entry, os_choice))
    browse_btn.pack(side="right", padx=(0, 5))

    progress_bar = ctk.CTkProgressBar(app, width=400)
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    speed_label = ctk.CTkLabel(app, text="", wraplength=450)
    speed_label.pack(pady=5)

    status_label = ctk.CTkLabel(app, text="", wraplength=450)
    status_label.pack(pady=10)

    btn_frame = ctk.CTkFrame(app)
    btn_frame.pack(pady=10)

    download_button = ctk.CTkButton(
        btn_frame, text="Start Download",
        command=lambda: start_download(os_choice, status_label, progress_bar, path_entry, speed_label)
    )
    download_button.pack(side="left", padx=10)

    stop_button = ctk.CTkButton(
        btn_frame, text="Stop", fg_color="red", hover_color="darkred",
        command=lambda: stop_download(status_label, speed_label)
    )
    stop_button.pack(side="right", padx=10)

    app.mainloop()

if __name__ == "__main__":
    main()
