import os
import sys
import tkinter as tk
import datetime
import pytz  # Needed for timezone handling
from geopy.geocoders import Nominatim  # Needed for city lookup
from ttkwidgets.autocomplete import AutocompleteEntry  # Needed for typeahead functionality
import tzlocal
from timezonefinder import TimezoneFinder  # Import timezone detection

# Set correct Tkinter environment for macOS
os.environ["TK_LIBRARY"] = "/System/Library/Frameworks/Tk.framework"

# Letter grid representing the word clock
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

# Initialize highlight grid (all set to invisible)
HIGHLIGHT_GRID = [[0 for _ in range(11)] for _ in range(11)]


def update_highlight_grid(hour, minute, is_pm):
    """ Updates the highlight grid based on the current time """
    global HIGHLIGHT_GRID
    HIGHLIGHT_GRID = [[0 for _ in range(11)] for _ in range(11)]  # Reset grid

    # Always highlight "IT IS"
    for i, j in [(0, 0), (0, 1), (0, 3), (0, 4)]:
        HIGHLIGHT_GRID[i][j] = 1

    # Round minutes to the nearest 5
    rounded_minute = round(minute / 5) * 5

    # Minute word mappings
    minute_map = {
        0: [(9, 5, 11)],  # "O'CLOCK"
        5: [(2, 6, 10), (4, 0, 4)],  # "FIVE PAST"
        10: [(3, 4, 7), (4, 0, 4)],  # "TEN PAST"
        15: [(1, 2, 9), (4, 0, 4)],  # "QUARTER PAST"
        20: [(2, 0, 6), (4, 0, 4)],  # "TWENTY PAST"
        25: [(2, 0, 10), (4, 0, 4)],  # "TWENTY FIVE PAST"
        30: [(3, 0, 4), (4, 0, 4)],  # "HALF PAST"
        35: [(2, 0, 10), (3, 8, 10)],  # "TWENTY FIVE TO"
        40: [(2, 0, 6), (3, 8, 10)],  # "TWENTY TO"
        45: [(1, 2, 9), (3, 8, 10)],  # "QUARTER TO"
        50: [(3, 4, 7), (3, 8, 10)],  # "TEN TO"
        55: [(2, 6, 10), (3, 8, 10)]  # "FIVE TO"
    }

    if rounded_minute in minute_map:
        for i, start, end in minute_map[rounded_minute]:
            for j in range(start, end):
                HIGHLIGHT_GRID[i][j] = 1

    # Adjust hour for "TO" cases
    if rounded_minute >= 35:
        hour = (hour % 12) + 1
    if hour == 0:
        hour = 12

    # Hour word mappings
    hour_map = {
        1: (5, 0, 3), 2: (6, 8, 11), 3: (5, 6, 11), 4: (6, 0, 4),
        5: (6, 4, 8), 6: (5, 3, 6), 7: (8, 0, 5), 8: (7, 0, 5),
        9: (4, 7, 11), 10: (9, 0, 3), 11: (7, 5, 11), 12: (8, 5, 11)
    }

    if hour in hour_map:
        i, start, end = hour_map[hour]
        for j in range(start, end):
            HIGHLIGHT_GRID[i][j] = 1

    # Highlight AM/PM
    if is_pm:
        HIGHLIGHT_GRID[10][4] = 1  # P
        HIGHLIGHT_GRID[10][5] = 1  # M
    else:
        HIGHLIGHT_GRID[10][9] = 1  # A
        HIGHLIGHT_GRID[10][10] = 1  # M


class WordClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QClockTwo")
        self.configure(bg="black")
        self.geometry("500x500")
        self.overrideredirect(True)  # Removes window frame

        # Detect system timezone, fallback to UTC if there's no internet
        try:
            self.timezone = tzlocal.get_localzone_name()  # Auto-detect timezone
        except Exception:
            self.timezone = "UTC"  # Fallback to UTC

        # Setup macOS app menu integration
        self.setup_menu()

        # Bind mouse events for dragging
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.move_window)

        # Create a canvas to hold the letter grid
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Label grid to display letters
        self.labels = [[None for _ in range(11)] for _ in range(11)]

        # Initialize labels (ONLY ONCE)
        for i in range(11):
            for j in range(11):
                self.labels[i][j] = tk.Label(
                    self.canvas,
                    text=LETTER_GRID[i][j],
                    font=("Arial", 24),
                    bg="black",
                    fg="white",
                    width=2,
                    height=1
                )
                self.labels[i][j].grid(row=i, column=j, padx=5, pady=5)

        # Start time updates
        self.update_clock()

    def setup_menu(self):
        """ Integrates the existing macOS app menu and adds a Settings option """
        menu_bar = tk.Menu(self)

        if sys.platform == "darwin":
            self.createcommand('tk::mac::ShowPreferences', self.show_settings)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Set timezone", command=self.show_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.config(menu=menu_bar)

    def start_move(self, event):
        """ Store the initial position when mouse clicks the window """
        self.x_offset = event.x_root - self.winfo_x()
        self.y_offset = event.y_root - self.winfo_y()

    def move_window(self, event):
        """ Move the window based on mouse movement """
        new_x = event.x_root - self.x_offset
        new_y = event.y_root - self.y_offset
        self.geometry(f"+{new_x}+{new_y}")

    def show_settings(self):
        """ Opens the Settings window to enter a city for timezone lookup with typeahead """
        settings_window = tk.Toplevel(self)  # ✅ Ensure this is defined first
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        settings_window.configure(bg="black")

        tk.Label(settings_window, text="Enter City:", font=("Arial", 12), fg="white", bg="black").pack(pady=10)

        cities = ["Berlin", "London", "New York", "Tokyo", "Sydney", "Paris", "Madrid", "Toronto", "Dubai", "Los Angeles"]
        city_entry = AutocompleteEntry(settings_window, completevalues=cities)  # Autocomplete city input
        city_entry.pack(pady=10)

        def save_timezone():
            geolocator = Nominatim(user_agent="QClockTwo")
            city_name = city_entry.get()
            location = geolocator.geocode(city_name)

            if location:
                print(f"Found location: {location}")
                print(f"Latitude: {location.latitude}, Longitude: {location.longitude}")  # Debugging print

                # Use timezonefinder instead of relying on country codes
                tf = TimezoneFinder()
                timezone = tf.timezone_at(lng=float(location.longitude), lat=float(location.latitude))

                if timezone:
                    print(f"Setting timezone: {timezone}")  # Debugging print
                    self.timezone = timezone  # ✅ Store as string, NOT as `pytz` object
                    settings_window.destroy()
                    self.update_clock()
                else:
                    print("Could not determine timezone.")  # Debugging print
                    tk.Label(settings_window, text="Timezone not found!", fg="red", bg="black").pack()
            else:
                print("City not found!")  # Debugging print
                tk.Label(settings_window, text="City not found!", fg="red", bg="black").pack()



        tk.Button(settings_window, text="Save", command=save_timezone).pack(pady=10)


    def update_clock(self):
        """ Updates the word clock display with correct timezone """
        try:
            current_time = datetime.datetime.now(pytz.timezone(self.timezone))  # ✅ Now self.timezone is a string
            hour, minute = current_time.hour, current_time.minute
            is_pm = hour >= 12

            hour = hour % 12 or 12
            update_highlight_grid(hour, minute, is_pm)

            for i in range(11):
                for j in range(11):
                    self.labels[i][j].config(fg="white" if HIGHLIGHT_GRID[i][j] else "#222222")

            self.after(300000, self.update_clock)

        except Exception as e:
            print(f"Error in update_clock: {e}")  # ✅ Debugging print




if __name__ == "__main__":
    app = WordClockApp()
    app.mainloop()
