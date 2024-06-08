import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

# Function to install required packages


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Check and install required packages
try:
    import wmi
except ImportError:
    install_package('wmi')
    import wmi

try:
    import win32com.client
except ImportError:
    install_package('pywin32')
    import win32com.client

try:
    import pythoncom
except ImportError:
    install_package('pywin32')
    import pythoncom

try:
    import pywintypes
except ImportError:
    install_package('pywin32')
    import pywintypes

try:
    import winreg as reg
except ImportError:
    messagebox.showerror(
        "Error", "winreg module is required but not found. Please ensure you are running this on Windows.")
    sys.exit()


class MACChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MAC Changer by sudoSU777")
        self.root.geometry("400x300")

        # Create a frame for the interface
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        # Network Interface
        self.interface_label = tk.Label(self.frame, text="Network Interface:")
        self.interface_label.grid(row=0, column=0, pady=5, sticky="e")

        self.interface_entry = tk.Entry(self.frame, width=30)
        self.interface_entry.grid(row=0, column=1, pady=5, padx=5)

        # New MAC Address
        self.new_mac_label = tk.Label(
            self.frame, text="New MAC Address (Optional):")
        self.new_mac_label.grid(row=1, column=0, pady=5, sticky="e")

        self.new_mac_entry = tk.Entry(self.frame, width=30)
        self.new_mac_entry.grid(row=1, column=1, pady=5, padx=5)

        # Buttons
        self.change_button = tk.Button(
            self.frame, text="Change to Specific MAC", command=self.change_mac)
        self.change_button.grid(row=2, column=0, pady=5, padx=5, columnspan=2)

        self.random_button = tk.Button(
            self.frame, text="Change to Random MAC", command=self.random_mac)
        self.random_button.grid(row=3, column=0, pady=5, padx=5, columnspan=2)

        self.restore_button = tk.Button(
            self.frame, text="Restore Original MAC", command=self.restore_mac)
        self.restore_button.grid(row=4, column=0, pady=5, padx=5, columnspan=2)

        self.show_button = tk.Button(
            self.frame, text="Show Current MAC", command=self.show_mac)
        self.show_button.grid(row=5, column=0, pady=5, padx=5, columnspan=2)

        self.vendor_button = tk.Button(
            self.frame, text="Show MAC Vendor", command=self.show_vendor)
        self.vendor_button.grid(row=6, column=0, pady=5, padx=5, columnspan=2)

    def change_mac(self):
        interface = self.interface_entry.get()
        new_mac = self.new_mac_entry.get()

        if not interface or not new_mac:
            messagebox.showerror(
                "Input Error", "Please enter both interface and new MAC address.")
            return

        try:
            nic = self.get_nic(interface)
            self.set_mac(nic, new_mac)
            messagebox.showinfo("Success", f"MAC address for {
                                interface} changed to {new_mac}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change MAC address: {e}")

    def random_mac(self):
        import random
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        new_mac = ':'.join(map(lambda x: "%02x" % x, mac))
        self.new_mac_entry.delete(0, tk.END)
        self.new_mac_entry.insert(0, new_mac)
        self.change_mac()

    def restore_mac(self):
        interface = self.interface_entry.get()

        if not interface:
            messagebox.showerror(
                "Input Error", "Please enter the network interface.")
            return

        try:
            nic = self.get_nic(interface)
            self.set_mac(nic, "")
            messagebox.showinfo("Success", f"MAC address for {
                                interface} restored to original.")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to restore MAC address: {e}")

    def show_mac(self):
        interface = self.interface_entry.get()

        if not interface:
            messagebox.showerror(
                "Input Error", "Please enter the network interface.")
            return

        try:
            nic = self.get_nic(interface)
            messagebox.showinfo(
                "Current MAC", f"Current MAC Address: {nic.MACAddress}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show MAC address: {e}")

    def show_vendor(self):
        interface = self.interface_entry.get()

        if not interface:
            messagebox.showerror(
                "Input Error", "Please enter the network interface.")
            return

        try:
            nic = self.get_nic(interface)
            messagebox.showinfo("MAC Vendor", f"Vendor: {nic.Manufacturer}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show MAC vendor: {e}")

    def get_nic(self, interface):
        c = wmi.WMI()
        for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if nic.Description == interface:
                return nic
        raise Exception(f"No network interface found with name {interface}")

    def set_mac(self, nic, new_mac):
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,
                          f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{nic.Index:04}", 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, "NetworkAddress", 0, reg.REG_SZ, new_mac)
        reg.CloseKey(key)
        nic.Disable()
        nic.Enable()


if __name__ == "__main__":
    root = tk.Tk()
    app = MACChangerApp(root)
    root.mainloop()
