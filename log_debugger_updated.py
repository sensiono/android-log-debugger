import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Canvas, Frame, Scrollbar
import subprocess

class LogDebuggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Log Debugger")
        self.root.geometry("1400x900")
        self.root.configure(bg="#ecf0f1")
        self.device_id = None
        
        # Define commands and their keywords
        self.commands = {
            "logcat": [
                {
                    "command": ["adb", "logcat", "-d", "-A 9"],
                    "keywords": [
                        "AUDIOFOCUS_LOSS",
                        "AUDIOFOCUS_LOSS_TRANSIENT",
                        "AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK",
                        "AUDIOFOCUS_NONE",
                        "AUDIOFOCUS_GAIN",
                        "AUDIOFOCUS_GAIN_TRANSIENT",
                        "AUDIOFOCUS_GAIN_TRANSIENT_EXCLUSIVE",
                        "AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK",
                        "AUDIOFOCUS_REQUEST_GRANTED",
                        "AUDIOFOCUS_REQUEST_FAILED",
                        "AUDIOFOCUS_REQUEST_DELAYED",
                        "ANR",
                        "am_anr"
                    ],
                },
            ],
            "dumpsys audio": [
                {
                    "command": ["adb", "shell", "dumpsys", "audio"],
                    "keywords": [
                        "AudioFocusInfo",
                        "STREAM_MUSIC:"
                    ],
                },
            ],
            "dumpsys media.audio_policy": [
                {
                    "command": ["adb", "shell", "dumpsys", "media.audio_policy"],
                    "keywords": [
                        "entertainment",
                        "Audio Patches:"
                    ],
                },
            ],
            "dumpsys media.audio_flinger": [
                {
                    "command": ["adb", "shell", "dumpsys", "media.audio_flinger"],
                    "keywords": [
                        "Patches"
                    ],
                },
            ],
            "ANRs and Deadlocks": [
                {
                    "command": ["adb", "shell", "grep", "am_anr", "/data/anr"],
                    "keywords": [
                        "WATCHDOG KILLING SYSTEM PROCESS",
                        "ANR"
                    ],
                },
            ],
            "Activities": [
                {
                    "command": ["adb", "shell", "dumpsys", "activity", "activities"],
                    "keywords": [
                        "am_focused_activity",
                        "Start proc"
                    ],
                },
            ],
            "Memory Issues": [
                {
                    "command": ["adb", "shell", "dumpsys", "meminfo"],
                    "keywords": [
                        "am_low_memory",
                        "am_proc_died",
                        "am_proc_start"
                    ],
                },
            ],
        }
        
        self.create_main_frame()

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights to fill space
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Title Label
        title_label = ttk.Label(
            self.main_frame, text="Android Debugger", font=("Arial", 24, "bold"), foreground="#000000"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)

        # Create buttons for ADB commands in a scrollable frame
        self.create_adb_control_panel()

        # Connect Button
        connect_button = ttk.Button(
            self.main_frame, text="Connect to Device", command=self.connect_device, style="TButton"
        )
        connect_button.grid(row=3, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))

        # Add space around buttons
        self.main_frame.columnconfigure(0, weight=1)

        # Button styling
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#3498db", foreground="#000000")
        self.style.map("TButton", background=[("active", "#2980b9")], foreground=[("active", "#000000")])

    def create_adb_control_panel(self):
        canvas = Canvas(self.main_frame, bg="#ecf0f1")
        scroll_y = Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scroll_x = Scrollbar(self.main_frame, orient="horizontal", command=canvas.xview)

        self.adb_frame = Frame(canvas, bg="#ecf0f1")
        self.adb_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.adb_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scroll_y.grid(row=1, column=1, sticky="ns")
        scroll_x.grid(row=2, column=0, sticky="ew")

        # Configure grid to expand
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.create_adb_control_buttons()

    def create_adb_control_buttons(self):
        """Create ADB control buttons for managing the server and devices."""
        adb_commands = [
            ("Start-server", ["adb", "start-server"]),
            ("Kill-server", ["adb", "kill-server"]),
            ("Devices", ["adb", "devices"]),
            ("Connect", ["adb", "connect", "127.0.0.1:5555"]),
            ("Disconnect", ["adb", "disconnect"]),
            ("Help", ["adb", "help"]),
            ("Version", ["adb", "version"]),
        ]
        for idx, (label, command) in enumerate(adb_commands):
            button = ttk.Button(
                self.adb_frame, text=label, command=lambda cmd=command: self.run_adb_command(cmd), style="TButton"
            )
            button.grid(row=0, column=idx, padx=5, pady=5, sticky=tk.W)

    def run_adb_command(self, command):
        """Run the specified ADB command and display the output."""
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
            output = result.stdout.strip() or result.stderr.strip()
            messagebox.showinfo("Command Output", output)
        except Exception as e:
            messagebox.showerror("Error", f"Error executing ADB command: {e}")

    def connect_device(self):
        try:
            result = subprocess.run(
                ["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8"
            )
            output = result.stdout.strip().split("\n")
            devices = [line for line in output[1:] if line.strip() and "device" in line]
            if len(devices) == 0:
                messagebox.showwarning("No Device", "No devices connected for debugging.")
            elif len(devices) > 1:
                messagebox.showwarning("Multiple Devices", "More than one device is connected. Please connect only one.")
            else:
                self.device_id = devices[0].split()[0]
                messagebox.showinfo("Device Connected", f"Connected to device {self.device_id}")
                self.show_logs_page()
        except Exception as e:
            messagebox.showerror("Error", f"Error connecting to device: {e}")

    def show_logs_page(self):
        # Destroy existing widgets and show log page
        for widget in self.root.winfo_children():
            widget.destroy()
        self.logs_frame = ttk.Frame(self.root, padding="20")
        self.logs_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for logs frame
        self.logs_frame.grid_rowconfigure(0, weight=0)
        self.logs_frame.grid_rowconfigure(1, weight=1)
        self.logs_frame.grid_columnconfigure(0, weight=1)
        self.logs_frame.grid_columnconfigure(1, weight=1)

        # Back Button
        back_button = ttk.Button(self.logs_frame, text="← Back", command=self.create_main_frame, style="TButton")
        back_button.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

        # Scrollable Text Area
        self.log_text = scrolledtext.ScrolledText(
            self.logs_frame, wrap=tk.WORD, width=140, height=20, font=("Arial", 10)
        )
        self.log_text.grid(row=1, column=0, columnspan=4, pady=20, padx=10, sticky="nsew")
        self.log_text.configure(bg="#ecf0f1", fg="#000000", insertbackground="black")

        # Command Sections and Buttons with Scrolling
        self.create_keyword_scrollable()

    def create_keyword_scrollable(self):
        canvas = Canvas(self.logs_frame, bg="#ecf0f1")
        scroll_y = Scrollbar(self.logs_frame, orient="vertical", command=canvas.yview)
        
        self.keyword_frame = Frame(canvas, bg="#ecf0f1")
        self.keyword_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.keyword_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.grid(row=2, column=0, columnspan=4, sticky="nsew")
        scroll_y.grid(row=2, column=5, sticky="ns")

        self.display_command_buttons()

    def display_command_buttons(self):
        """Display command buttons with all keywords regardless of presence in the output."""
        col_counter = 0
        for command_name, command_list in self.commands.items():
            command_label = ttk.Label(
                self.keyword_frame, text=command_name, font=("Arial", 14, "bold"), foreground="#000000"
            )
            command_label.grid(row=0, column=col_counter, sticky=tk.W, padx=10, pady=(10, 5))

            for command_info in command_list:
                for idx, keyword in enumerate(command_info["keywords"]):
                    button = ttk.Button(
                        self.keyword_frame,
                        text=keyword,
                        command=lambda cmd=command_info["command"], kw=keyword: self.show_command_output(cmd, kw),
                        style="TButton",
                    )
                    button.grid(row=1 + idx, column=col_counter, padx=5, pady=5, sticky=tk.W)
            col_counter += 1

    def show_command_output(self, command, keyword):
        """Execute the command and filter the output for the keyword."""
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
            output_lines = result.stdout.splitlines() if result.stdout else []

            # Filter lines containing the keyword
            filtered_lines = [line for line in output_lines if keyword in line]

            # Clear previous text and display filtered output
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "\n".join(filtered_lines))

            if not filtered_lines:
                messagebox.showinfo(
                    "No Results", f"No lines found containing '{keyword}' in the output of {command}."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error executing command: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LogDebuggerApp(root)
    root.mainloop()