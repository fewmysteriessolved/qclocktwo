import os
import tkinter as tk
import datetime
import pytz
import tzlocal

os.environ["TK_LIBRARY"] = "/System/Library/Frameworks/Tk.framework"

LETTER_GRID = [
    "ITLISASAMPM",
    "ACQUARTERDC",
    "TWENTYFIVEX",
    "HALFTENFTOU",
    "PASTERUNINE",
    "ONESIXTHREE",
    "FOURFIVETWO",
    "EIGHTELEVEN",
    "SEVENTWELVE",
    "TENSEOCLOCK",
    "ERZIPMNOTAM"
]

HIGHLIGHT_GRID = [[0] * 11 for _ in range(11)]

def update_highlight_grid(hour, minute, is_pm):
    global HIGHLIGHT_GRID
    HIGHLIGHT_GRID = [[0] * 11 for _ in range(11)]
    
    # Highlight "IT IS"
    for i, j in [(0, 0), (0, 1), (0, 3), (0, 4)]:
        HIGHLIGHT_GRID[i][j] = 1
    
    rounded_minute = round(minute / 5) * 5
    minute_map = {
        0: [(9, 5, 11)],
        5: [(2, 6, 10), (4, 0, 4)],
        10: [(3, 4, 7), (4, 0, 4)],
        15: [(1, 2, 9), (4, 0, 4)],
        20: [(2, 0, 6), (4, 0, 4)],
        25: [(2, 0, 10), (4, 0, 4)],
        30: [(3, 0, 4), (4, 0, 4)],
        35: [(2, 0, 10), (3, 8, 10)],
        40: [(2, 0, 6), (3, 8, 10)],
        45: [(1, 2, 9), (3, 8, 10)],
        50: [(3, 4, 7), (3, 8, 10)],
        55: [(2, 6, 10), (3, 8, 10)]
    }
    
    for i, start, end in minute_map.get(rounded_minute, []):
        for j in range(start, end):
            HIGHLIGHT_GRID[i][j] = 1
    
    hour = (hour % 12) + 1 if rounded_minute >= 35 else hour % 12 or 12
    hour_map = {
        1: (5, 0, 3), 2: (6, 8, 11), 3: (5, 6, 11), 4: (6, 0, 4),
        5: (6, 4, 8), 6: (5, 3, 6), 7: (8, 0, 5), 8: (7, 0, 5),
        9: (4, 7, 11), 10: (9, 0, 3), 11: (7, 5, 11), 12: (8, 5, 11)
    }
    
    if i := hour_map.get(hour):
        for j in range(i[1], i[2]):
            HIGHLIGHT_GRID[i[0]][j] = 1
    
    # AM/PM
    HIGHLIGHT_GRID[10][4 if is_pm else 9] = 1
    HIGHLIGHT_GRID[10][5 if is_pm else 10] = 1

class WordClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QClockTwo")
        self.configure(bg="black")
        self.geometry("500x500")
        self.overrideredirect(True)
        
        self.timezone = tzlocal.get_localzone_name() or "UTC"
        self.show_inactive_letters = True  # Default setting
        
        # Create context menu with submenus
        self.context_menu = tk.Menu(self, tearoff=0, bg="black", fg="white", 
                                   activebackground="gray", activeforeground="white")
        
        # Visibility submenu
        self.visibility_menu = tk.Menu(self.context_menu, tearoff=0, bg="black", fg="white",
                                      activebackground="gray", activeforeground="white")
        self.show_inactive_var = tk.BooleanVar(value=self.show_inactive_letters)
        self.visibility_menu.add_checkbutton(label="Show inactive letters", 
                                           variable=self.show_inactive_var,
                                           command=self.toggle_visibility)
        
        # Timezone submenu
        self.timezone_menu = tk.Menu(self.context_menu, tearoff=0, bg="black", fg="white",
                                    activebackground="gray", activeforeground="white")
        self.timezone_var = tk.StringVar(value=self.timezone)
        
        # Add timezone options
        timezones = [
            ("Local", "local"),
            ("Berlin", "Europe/Berlin"),
            ("London", "Europe/London"), 
            ("New York", "America/New_York"),
            ("Tokyo", "Asia/Tokyo"),
            ("Sydney", "Australia/Sydney"),
            ("Paris", "Europe/Paris"),
            ("Madrid", "Europe/Madrid"),
            ("Toronto", "America/Toronto"),
            ("Dubai", "Asia/Dubai"),
            ("Los Angeles", "America/Los_Angeles")
        ]
        
        for name, tz in timezones:
            self.timezone_menu.add_radiobutton(label=name, 
                                             variable=self.timezone_var,
                                             value=tz,
                                             command=self.change_timezone)
        
        # Main menu items
        self.context_menu.add_cascade(label="Visibility", menu=self.visibility_menu)
        self.context_menu.add_cascade(label="Timezone", menu=self.timezone_menu)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="About", command=self.show_about)
        self.context_menu.add_command(label="Quit", command=self.quit)
        
        if os.name == "posix":
            menu_bar = tk.Menu(self)
            app_menu = tk.Menu(menu_bar, name="apple", tearoff=0)
            app_menu.add_command(label="About QClockTwo", command=self.show_about)
            app_menu.add_separator()
            app_menu.add_command(label="Quit QClockTwo", command=self.quit)
            menu_bar.add_cascade(menu=app_menu)
            self.config(menu=menu_bar)
            self.createcommand("tk::mac::standardAboutMenuItem", self.show_about)
        
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.move_window)
        
        # Try multiple right-click event bindings for cross-platform compatibility
        self.bind("<Button-2>", self.show_context_menu)  # Middle-click (sometimes right-click on Mac)
        self.bind("<Button-3>", self.show_context_menu)  # Right-click
        self.bind("<Control-Button-1>", self.show_context_menu)  # Ctrl+click (Mac right-click)
        
        # Also try key binding as fallback
        self.bind("<Control-m>", self.show_context_menu)  # Ctrl+M to show menu
        self.bind("<Double-Button-1>", self.test_event)  # Double-click test
        self.focus_set()  # Make sure the window can receive key events
        
        # Create main frame for the grid
        self.main_frame = tk.Frame(self, bg="black")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        font_size = int(500/20)  # Initial font size based on default 500x500 window
        self.labels = [[tk.Label(self.main_frame, text=LETTER_GRID[i][j], 
                                font=("Arial", font_size), 
                                bg="black", fg="white", width=2, height=1)
                        for j in range(11)] for i in range(11)]
        for i in range(11):
            for j in range(11):
                self.labels[i][j].grid(row=i, column=j, padx=5, pady=5)
                # Bind multiple event types to each label
                self.labels[i][j].bind("<Button-2>", self.show_context_menu)
                self.labels[i][j].bind("<Button-3>", self.show_context_menu)
                self.labels[i][j].bind("<Control-Button-1>", self.show_context_menu)
                self.labels[i][j].bind("<Control-m>", self.show_context_menu)
                # Also bind left-click for moving
                self.labels[i][j].bind("<ButtonPress-1>", self.start_move)
                self.labels[i][j].bind("<B1-Motion>", self.move_window)
        
        self.update_clock()
    
    def toggle_visibility(self):
        """Toggle letter visibility setting from context menu"""
        # Add a small delay to prevent menu from reopening
        self.after(50, self._toggle_visibility_delayed)
    
    def _toggle_visibility_delayed(self):
        """Delayed visibility toggle to prevent menu conflicts"""
        self.show_inactive_letters = self.show_inactive_var.get()
        self.update_letter_visibility()
        print(f"Letter visibility toggled: {self.show_inactive_letters}")
    
    def change_timezone(self):
        """Change timezone from context menu"""
        # Add a small delay to prevent menu from reopening
        self.after(50, self._change_timezone_delayed)
    
    def _change_timezone_delayed(self):
        """Delayed timezone change to prevent menu conflicts"""
        new_tz = self.timezone_var.get()
        if new_tz == "local":
            self.timezone = tzlocal.get_localzone_name() or "UTC"
        else:
            self.timezone = new_tz
        print(f"Timezone changed to: {self.timezone}")
        self.update_clock()
    
    def test_event(self, event):
        """Test function to see if events are working"""
        print("Double-click detected! Events are working.")
        return "break"
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        print(f"Context menu triggered! Event: {event}, X: {event.x_root}, Y: {event.y_root}")
        try:
            # Make sure any previous menu is properly closed
            self.context_menu.unpost()
            # Small delay to ensure clean menu display
            self.after(10, lambda: self._show_menu_delayed(event.x_root, event.y_root))
        except Exception as e:
            print(f"Error showing context menu: {e}")
            # Fallback - just show the visibility settings directly
            self.show_visibility_settings()
    
    def _show_menu_delayed(self, x, y):
        """Show menu with slight delay to prevent conflicts"""
        try:
            self.context_menu.post(x, y)
        except Exception as e:
            print(f"Error in delayed menu show: {e}")
        finally:
            try:
                self.context_menu.grab_release()
            except:
                pass
    
    def show_visibility_settings(self):
        """Show letter visibility settings dialog"""
        win = tk.Toplevel(self)
        win.title("Letter Visibility Settings")
        win.geometry("300x150")
        win.configure(bg="black")
        win.transient(self)
        win.grab_set()

        # Center the window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
        y = (win.winfo_screenheight() // 2) - (win.winfo_height() // 2)
        win.geometry(f"+{x}+{y}")

        tk.Label(win, text="Letter Visibility:", font=("Arial", 12), fg="white", bg="black").pack(pady=10)
        
        visibility_var = tk.BooleanVar(value=self.show_inactive_letters)
        checkbox = tk.Checkbutton(
            win,
            text="Show inactive letters",
            variable=visibility_var,
            fg="white",
            bg="black",
            selectcolor="black",
            activebackground="black",
            activeforeground="white"
        )
        checkbox.pack(pady=10)

        def save_and_close():
            self.show_inactive_letters = visibility_var.get()
            self.update_letter_visibility()
            win.destroy()

        def cancel():
            win.destroy()

        button_frame = tk.Frame(win, bg="black")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save", command=save_and_close, bg="gray", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel, bg="gray", fg="white").pack(side=tk.LEFT, padx=5)
    
    def update_letter_visibility(self):
        """Update the visibility of letters based on current settings"""
        for i in range(11):
            for j in range(11):
                if HIGHLIGHT_GRID[i][j]:
                    self.labels[i][j].config(fg="white")
                else:
                    self.labels[i][j].config(fg="#222222" if self.show_inactive_letters else "black")
    
    def show_about(self):
        win = tk.Toplevel(self)
        win.title("About QClockTwo")
        win.geometry("300x250")
        win.configure(bg="black")
        win.transient(self)
        tk.Label(win, text="Never gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you", font=("Arial", 15), fg="white", bg="black", justify="center").pack(pady=20)
    
    def show_resolution(self):
        win = tk.Toplevel(self)
        win.title("Letter Visibility Settings")
        win.geometry("300x150")
        win.configure(bg="black")

        # Visibility settings only
        visibility_frame = tk.Frame(win, bg="black")
        visibility_frame.pack(pady=30)
        visibility_var = tk.BooleanVar(value=True)
        tk.Label(win, text="Letter Visibility:", font=("Arial", 12), fg="white", bg="black").pack()
        tk.Checkbutton(
            visibility_frame,
            text="Show inactive letters",
            variable=visibility_var,
            fg="white",
            bg="black",
            selectcolor="black"
        ).pack()

        def save():
            show_inactive = visibility_var.get()
            # Store the setting for use in update_clock
            self.show_inactive_letters = show_inactive
            for i in range(11):
                for j in range(11):
                    self.labels[i][j].config(
                        fg="white" if HIGHLIGHT_GRID[i][j] else ("#222222" if show_inactive else "black")
                    )

        tk.Button(win, text="Save", command=save).pack(pady=20)

    def show_settings(self):
        win = tk.Toplevel(self)
        win.title("Timezone Settings")
        win.geometry("300x200")
        win.configure(bg="black")
        win.transient(self)
        
        # Center the window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
        y = (win.winfo_screenheight() // 2) - (win.winfo_height() // 2)
        win.geometry(f"+{x}+{y}")
        
        tk.Label(win, text="Enter City:", font=("Arial", 12), fg="white", bg="black").pack(pady=10)
        city_entry = tk.Entry(win)
        city_entry.pack(pady=10)
        
        def save():
            city = city_entry.get()
            tz_map = {"Berlin": "Europe/Berlin", "London": "Europe/London", "New York": "America/New_York", 
                      "Tokyo": "Asia/Tokyo", "Sydney": "Australia/Sydney", "Paris": "Europe/Paris", 
                      "Madrid": "Europe/Madrid", "Toronto": "America/Toronto", "Dubai": "Asia/Dubai", 
                      "Los Angeles": "America/Los_Angeles"}
            if city and (tz := tz_map.get(city)):
                self.timezone = tz
            win.destroy()
            self.update_clock()
        
        tk.Button(win, text="Save", command=save, bg="gray", fg="white").pack(pady=20)
    
    def start_move(self, event):
        self.x_offset = event.x_root - self.winfo_x()
        self.y_offset = event.y_root - self.winfo_y()
    
    def move_window(self, event):
        self.geometry(f"+{event.x_root - self.x_offset}+{event.y_root - self.y_offset}")
    
    def update_clock(self):
        try:
            time = datetime.datetime.now(pytz.timezone(self.timezone))
            update_highlight_grid(time.hour, time.minute, time.hour >= 12)
            self.update_letter_visibility()
            self.after(300000, self.update_clock)
        except Exception:
            self.after(300000, self.update_clock)

if __name__ == "__main__":
    WordClockApp().mainloop()