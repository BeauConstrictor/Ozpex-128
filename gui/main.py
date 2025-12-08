import os
import sys
import json
import shutil
import os.path
import subprocess
import tkinter as tk
from uuid import uuid4
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

os.chdir(os.path.dirname(os.path.abspath(__file__)))

default_config = {
    "term-args": [
        "--default-settings",
        "--profile", "Default Pixelated"
    ],
    "stdout-serial": False,
}

def resolve_relative_machine_data(machine: dict, base_dir: str) -> None:
        machine["ROM"] = os.path.abspath(os.path.join(base_dir, machine["ROM"]))
        
        for name in ("Cartridge A", "Cartridge B"):
            cart = machine[name]
            cart_type = cart.split(":")[0]
            cart_path = ":".join(cart.split(":")[1:])
            cart_path = os.path.abspath(os.path.join(base_dir, cart_path))
            machine[name] = cart_type + ":" + cart_path

def verify_machine(data: dict) -> bool:
    keys = {"Name": (str,),
            "ROM": (str,),
            "Cartridge A": (str, type(None)),
            "Cartridge B": (str, type(None))}
    
    for k, types in keys.items():
        if k not in data: return False
        good_type_found = False
        for t in types:
            if isinstance(data[k], t): good_type_found = True
        if not good_type_found: return False
    return True

class MachinesList(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.listbox = tk.Listbox(self)
        self.listbox.bind('<<ListboxSelect>>', self.onselect)
        self.listbox.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.list_machines()
            
    def onselect(self, event: tk.Event) -> None:
        index = int(self.listbox.curselection()[0])
        
        try:
            machine = self.machines[index]
            uuid = self.machine_uuids[index]
        except IndexError:
            return
        
        self.master.machine_view.show_machine(machine, uuid)
        
    def list_machines(self) -> None:
        self.machines = []
        self.machine_uuids = []
        
        self.listbox.delete(0, tk.END)
        
        for m in os.listdir("machines/"):
            with open(f"machines/{m}", "r") as f:
                machine = json.load(f)
                if not verify_machine(machine):
                    messagebox.showerror("Error", "An invalid machine file is "
                                         "currently managed.")
                    continue
            self.listbox.insert(tk.END, machine["Name"])
            self.machines.append(machine)
            self.machine_uuids.append(m)
        
class MachineView(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.deselect()
        
    def deselect(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
            
        self.default_label = tk.Label(self, text="Select a machine, or create "
                                                 "a new one.")
        self.default_label.pack(expand=True, fill=tk.BOTH)
    
    def show_machine(self, attributes: dict, uuid: str|None) -> None:
        self.default_label.destroy()
        
        for widget in self.winfo_children():
            widget.destroy()

        title = tk.Label(self, text=f"{attributes['Name']}", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        attr_label = tk.Label(self, text="Configuration:")
        attr_label.pack(anchor="w", padx=5)

        attr_listbox = tk.Listbox(self)
        for k,v in attributes.items():
            attr_listbox.insert(tk.END, f"{k}: {v}")
        attr_listbox.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        buttons_section = tk.Frame(self)
        buttons_section.pack(pady=10)
        
        delete_button = tk.Button(buttons_section, text="Remove",
                                 command=lambda: self.remove())
        delete_button.grid(row=0, column=0, padx=5)
        
        if uuid is None:
            delete_button.config(state="disabled")
        self.uuid = uuid
        
        start_button = tk.Button(buttons_section, text="Start",
                                 command=lambda: self.start_machine(attributes))
        start_button.grid(row=0, column=1, padx=5)
        
    def remove(self) -> None:
        os.remove(f"machines/{self.uuid}")
        self.master.machines_list.list_machines()
        self.deselect()
    
    def start_machine(self, config: dict) -> None:
        try:
            with open("config.json", "r") as f:
                app_config = json.load(f)
        except:
            messagebox.showwarning("Warning", "Failed to read the config file.")
            app_config = default_config
            
        stdout_serial = app_config.get("stdout-serial",
                                       default_config["stdout-serial"])
        
        command = []
        
        if not stdout_serial:
            crt = shutil.which("cool-retro-term")
            if not crt:
                messagebox.showerror("Error", "Ozpex 128 requires Cool Retro Term "
                                    "to be installed and in the system PATH.")
                return
            
            command += [crt,
                    "--workdir", os.getcwd(),
                    "-T", config["Name"],
            ]
            
            command += app_config.get("term-args", default_config["term-args"])
            
            command += ["-e"]
        
        command += [
                sys.executable, "../main.py","--rom", config["ROM"]
        ]
        
        if config["Cartridge A"] is not None:
            command += ["-1", config["Cartridge A"]]
        if config["Cartridge B"] is not None:
            command += ["-2", config["Cartridge B"]]
            
        subprocess.Popen(command, cwd=os.getcwd())
            
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Ozpex 128")
        self.geometry("700x500")

        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Quit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)
        
        machine_menu = tk.Menu(self.menubar, tearoff=0)
        machine_menu.add_command(label="New", command=self.machine_new)
        machine_menu.add_command(label="Import", command=self.machine_import)
        machine_menu.add_command(label="Open", command=self.machine_open)
        self.menubar.add_cascade(label="Machine", menu=machine_menu)

        self.machines_list = MachinesList(self, bd=2, relief=tk.SUNKEN)
        self.machines_list.grid(row=0, column=0, sticky="nsew")

        self.machine_view = MachineView(self, bd=2, relief=tk.SUNKEN)
        self.machine_view.grid(row=0, column=1, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        
    def machine_new(self) -> None:
        popup = tk.Toplevel()
        popup.title("New Machine")
        popup.grab_set()
        popup.attributes("-topmost", True)

        tk.Label(popup, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        text_entry = tk.Entry(popup, width=40)
        text_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        tk.Label(popup, text="ROM:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        rom_var = tk.StringVar()
        rom_entry = tk.Entry(popup, textvariable=rom_var, width=40)
        rom_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="we")
        tk.Button(popup, text="Browse", command=lambda: rom_var.set(filedialog.askopenfilename())).grid(row=1, column=3, padx=5, pady=5)

        tk.Label(popup, text="Cartridge A:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        dropdown_a = ttk.Combobox(popup, values=["ROM", "BBRAM"], width=10)
        dropdown_a.grid(row=2, column=1, padx=5, pady=5)
        file_a_var = tk.StringVar()
        file_a_entry = tk.Entry(popup, textvariable=file_a_var, width=30)
        file_a_entry.grid(row=2, column=2, padx=5, pady=5)
        tk.Button(popup, text="Browse", command=lambda: file_a_var.set(filedialog.askopenfilename())).grid(row=2, column=3, padx=5, pady=5)

        tk.Label(popup, text="Cartridge B:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        dropdown_b = ttk.Combobox(popup, values=["ROM", "BBRAM"], width=10)
        dropdown_b.grid(row=3, column=1, padx=5, pady=5)
        file_b_var = tk.StringVar()
        file_b_entry = tk.Entry(popup, textvariable=file_b_var, width=30)
        file_b_entry.grid(row=3, column=2, padx=5, pady=5)
        tk.Button(popup, text="Browse", command=lambda: file_b_var.set(filedialog.askopenfilename())).grid(row=3, column=3, padx=5, pady=5)

        def submit():
            name = text_entry.get().strip()
            rom = rom_var.get().strip()
            cs1_type = dropdown_a.get()
            cs1 = f"{dropdown_a.get().lower()}:{file_a_var.get()}" if cs1_type else None
            cs2_type = dropdown_b.get()
            cs2 = f"{dropdown_b.get().lower()}:{file_b_var.get()}" if cs2_type else None
            
            if not name:
                messagebox.showerror("Missing Name", "You must give your "
                                                     "machine a name.")
                return
            if not rom:
                messagebox.showerror("Missing ROM", "You must give your "
                                                     "machine a ROM.")
                return
            
            data = {
                "Name": name,
                "ROM": rom,
                "Cartridge A": cs1,
                "Cartridge B": cs2,
            }
            with open(f"machines/{uuid4()}.json", "w") as f:
                json.dump(data, f, indent=4)
            
            self.machines_list.list_machines()
            
            popup.destroy()

        tk.Button(popup, text="Submit", command=submit).grid(row=4, column=0, columnspan=4, pady=10)
        
    def machine_import(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select a Machine JSON file",
            filetypes=[("Machine files", ("*.mach", "*.json")), ("All files", "*")]
        )
        if not filename: return
        
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                if not verify_machine(data):
                    messagebox.showerror("Import Error", "The file contains "
                                         "invalid machine data.")
                    return
        except:
            messagebox.showerror("JSON Error", "Could not parse the JSON data.")
            return
        
        base_dir = os.path.dirname(filename)
        resolve_relative_machine_data(data, base_dir)
    
        with open(f"machines/{uuid4()}.json", "w") as f:
            json.dump(data, f, indent=4)
        
        self.machines_list.list_machines()
        
    def machine_open(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select a Machine JSON file",
            filetypes=[("Machine files", ("*.mach", "*.json")), ("All files", "*")]
        )
        if not filename: return
        
        try:
            with open(filename, "r") as f:
                machine = json.load(f)
                if not verify_machine(machine):
                    messagebox.showerror("Open Error", "The file contains "
                                         "invalid machine data.")
                    return
        except:
            messagebox.showerror("JSON Error", "Could not parse the JSON data.")
            return
        
        base_dir = os.path.dirname(filename)
        resolve_relative_machine_data(machine, base_dir)
    
        self.machine_view.show_machine(machine, None)

        
if __name__ == "__main__":
    App().mainloop()