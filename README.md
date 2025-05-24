# QClockTwo

QClockTwo is a sleek, desktop word clock application built with Python and Tkinter. It displays the time in a unique, text-based format using a grid of letters, where specific words are highlighted to indicate the current time (e.g., "IT IS HALF PAST THREE"). The app supports dynamic timezone updates based on city input, features a draggable window, and integrates seamlessly with the macOS menu bar, including a custom About dialog.

## Features

- **Word Clock Display**: Shows time in a 11x11 letter grid, highlighting words like "QUARTER PAST" or "TEN TO" to represent the current time.
- **Timezone Support**: Automatically detects the system timezone or allows users to set a custom timezone by entering a city name with autocomplete functionality.
- **Custom macOS Menu**: Includes a tailored application menu with a custom "About QClockTwo" dialog and a Settings option.
- **Draggable Window**: Frameless window that can be moved by clicking and dragging anywhere on the app.
- **Responsive Updates**: Updates the time display every 5 minutes to reflect the current time in the selected timezone.

## Screenshots

*(Add screenshots of the app in action here, e.g., the clock display and settings window. You can upload images to the repo and link them.)*

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS (for full menu integration; other platforms may work but are untested)
- Required Python packages (see [Dependencies](#dependencies))

### Build from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/qclocktwo.git
   cd QClockTwo

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python3.12 qclocktwo.py
   ```

## Build a Standalone macOS App

o create a standalone executable for macOS, use PyInstaller:

1. Install PyInstaller if you haven't already:
   ```bash
   pip install pyinstaller
   ```
2. Build the app:
   ```bash
   sudo pyinstaller --onefile --windowed --name "QClockTwo" qclocktwo.py
   ```
3. The executable will be created in the `dist` directory. You can move it to your Applications folder or wherever you prefer.

## Dependencies
The app relies on the following Python packages, listed in requirements.txt:

```bash
tk==0.1.0
geopy==2.4.1
ttkwidgets==0.13.0
tzlocal==5.2
timezonefinder==6.5.2
```

Install them with:

```bash
(choose one of the following based on your Python version)
pip install tk geopy ttkwidgets tzlocal timezonefinder
pip3 install tk geopy ttkwidgets tzlocal timezonefinder
pip3.12 install tk geopy ttkwidgets tzlocal timezonefinder
```

## Usage
- Launch the App: Run `python3.12 qclocktwo.py` or the built `QClockTwo.app`.
The
- View Time: The 11x11 letter grid displays the current time (e.g., "IT IS TWENTY FIVE PAST SEVEN"). Words are highlighted in white, with inactive letters in dark gray.
- Change Timezone: Click the "Settings" menu to enter a city name for timezone detection. The app will update the time display accordingly.
- Drag the Window: Click and drag anywhere on the app to move it around your desktop.

## Configuration
- Timezone: Defaults to the system timezone (detected via tzlocal). Set a custom timezone via the Settings menu.
- Autocomplete: The city input field supports autocomplete for easier timezone selection.
- Letter Grid: The 11x11 grid is defined in LETTER_GRID within `qclocktwo.py`. Modify it to change the word layout (ensure corresponding changes in minute_map and hour_map).
- Update Interval: The clock updates every 5 minutes (300,000 ms). Adjust the interval in the update_clock method if needed.

## Development Notes

- The app is designed for macOS but may work on other platforms with Tkinter support.
- Code Structure:
    - `LETTER_GRID`: Defines the 11x11 letter grid.
    - `HIGHLIGHT_GRID`: Manages which letters are highlighted based on the time.
    - `WordClockApp`: Main application class handling the UI and logic.

## Known Limitations
- Timezone lookup requires an internet connection for geopy.
- The app is primarily tested on macOS; other platforms may have untested behavior.