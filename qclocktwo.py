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
    HIGHLIGHT_GRID[10][5 if is_pm else 9] = 1
    HIGHLIGHT_GRID[10][6 if is_pm else 10] = 1

class WordClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QClockTwo")
        self.configure(bg="black")
        self.geometry("500x500")
        self.overrideredirect(True)
        
        self.timezone = tzlocal.get_localzone_name() or "UTC"
        
        if os.name == "posix":
            menu_bar = tk.Menu(self)
            app_menu = tk.Menu(menu_bar, name="apple", tearoff=0)
            app_menu.add_command(label="About QClockTwo", command=self.show_about)
            app_menu.add_separator()
            app_menu.add_command(label="Quit QClockTwo", command=self.quit)
            menu_bar.add_cascade(menu=app_menu)
            settings_menu = tk.Menu(menu_bar, tearoff=0)
            settings_menu.add_command(label="Settings", command=self.show_settings)
            menu_bar.add_cascade(label="Settings", menu=settings_menu)
            self.config(menu=menu_bar)
            self.createcommand("tk::mac::standardAboutMenuItem", self.show_about)
        
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.move_window)
        
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.labels = [[tk.Label(self.canvas, text=LETTER_GRID[i][j], font=("Arial", 24), bg="black", fg="white", width=2, height=1)
                        for j in range(11)] for i in range(11)]
        for i in range(11):
            for j in range(11):
                self.labels[i][j].grid(row=i, column=j, padx=5, pady=5)
        
        self.update_clock()
    
    def show_about(self):
        win = tk.Toplevel(self)
        win.title("About QClockTwo")
        win.geometry("300x200")
        win.configure(bg="black")
        tk.Label(win, text="QClockTwo\nVersion 1.0\nWord Clock\n© 2025", font=("Arial", 12), fg="white", bg="black", justify="center").pack(pady=20)
        tk.Button(win, text="OK", command=win.destroy).pack(pady=10)
    
    def show_settings(self):
        win = tk.Toplevel(self)
        win.title("Settings")
        win.geometry("300x200")
        win.configure(bg="black")
        tk.Label(win, text="Enter City:", font=("Arial", 12), fg="white", bg="black").pack(pady=10)
        entry = tk.Entry(win)
        entry.pack(pady=10)
        
        def save():
            city = entry.get()
            tz_map = {"Berlin": "Europe/Berlin", "London": "Europe/London", "New York": "America/New_York", 
                      "Tokyo": "Asia/Tokyo", "Sydney": "Australia/Sydney", "Paris": "Europe/Paris", 
                      "Madrid": "Europe/Madrid", "Toronto": "America/Toronto", "Dubai": "Asia/Dubai", 
                      "Los Angeles": "America/Los_Angeles"}
            if tz := tz_map.get(city):
                self.timezone = tz
                win.destroy()
                self.update_clock()
            else:
                tk.Label(win, text="Timezone not found!", fg="red", bg="black").pack()
        
        tk.Button(win, text="Save", command=save).pack(pady=10)
    
    def start_move(self, event):
        self.x_offset = event.x_root - self.winfo_x()
        self.y_offset = event.y_root - self.winfo_y()
    
    def move_window(self, event):
        self.geometry(f"+{event.x_root - self.x_offset}+{event.y_root - self.y_offset}")
    
    def update_clock(self):
        try:
            time = datetime.datetime.now(pytz.timezone(self.timezone))
            update_highlight_grid(time.hour, time.minute, time.hour >= 12)
            for i in range(11):
                for j in range(11):
                    self.labels[i][j].config(fg="white" if HIGHLIGHT_GRID[i][j] else "#222222")
            self.after(300000, self.update_clock)
        except Exception:
            self.after(300000, self.update_clock)

if __name__ == "__main__":
    WordClockApp().mainloop()