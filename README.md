# Render Time Tracker - Blender Extension

A professional Blender extension for tracking render time statistics with live display in the render window.

## 🎯 Features

### Core Features
- ✅ **Total Render Time Tracking** - Accurate timing from start to finish
- ✅ **Per-Frame Time Analysis** - See exactly how long each frame takes
- ✅ **ETA Calculation** - Estimated time remaining based on average
- ✅ **Live Statistics** - Real-time updates during rendering
- ✅ **Progress Bar** - Visual progress indicator

### Display Locations
- 📍 **3D Viewport** - N-Panel "Render Time" tab
- 📍 **Image Editor** - "Render Stats" panel (render window)
- 📍 **Node Editor** - For compositor renders

### Export Options
- 📄 **Text Format** - Human-readable statistics
- 📄 **CSV Format** - Spreadsheet compatible
- 📄 **JSON Format** - Machine-readable data

### Additional Features
- 🔔 **Completion Notifications** - Get notified when render finishes
- 🔊 **Sound Alerts** - Optional audio notification
- 📊 **Frame History** - Complete log of all rendered frames
- ⚙️ **Auto Export** - Automatically save stats on completion

## 📦 Installation

### Method 1: Install from File (Recommended)
1. Download `render_time_tracker.zip`
2. Open Blender: **Edit > Preferences > Get Extensions**
3. Click **Install from Disk...**
4. Select the downloaded ZIP file
5. Enable the extension

### Method 2: Manual Installation
1. Extract ZIP to Blender extensions folder:
   - Windows: `%APPDATA%/Blender Foundation/Blender/4.2/extensions/user_default/`
   - macOS: `~/Library/Application Support/Blender/4.2/extensions/user_default/`
   - Linux: `~/.config/blender/4.2/extensions/user_default/`

## 🚀 Usage

### Starting a Render
1. Open the **Render Time** panel in the 3D Viewport (N-Panel)
2. Click **Image** for single frame or **Animation** for sequence
3. Watch live statistics update in real-time

### Viewing Statistics
Statistics appear in multiple locations:
- **3D Viewport Panel** - Full control and settings
- **Image Editor** - During render (Render Stats panel)
- **Console** - Detailed frame-by-frame logging

### Exporting Data
1. Click **Export Stats** button
2. Choose format (TXT/CSV/JSON)
3. Select save location
4. Data includes: frame times, timestamps, averages, totals

## ⚙️ Configuration

### Settings Panel Options
- **Show Total Time** - Display total elapsed time
- **Show Per Frame** - Show individual frame times
- **Show ETA** - Display estimated remaining time
- **Show Progress Bar** - Visual progress indicator
- **Notify on Complete** - Popup notification
- **Auto Export** - Save stats automatically

### Export Formats
```
Text (TXT):
  Total Time: 00:05:23.45
  Frames: 150
  Average: 00:00:02.15

CSV:
  Frame,Time_Seconds,Timestamp
  1,2.15,14:30:25
  2,2.08,14:30:27

JSON:
  {
    "summary": { "total_time": 323.45, ... },
    "frames": [ { "frame": 1, "time": 2.15 }, ... ]
  }
```

## 📋 Statistics Display

### Live Stats Format
```
🔴 RENDERING
⏱️ Total Time:     00:05:23.45
⚡ Last Frame:     00:00:02.15
📊 Average:        00:00:02.08
⏳ ETA:            00:15:45.30
🎬 Frames:         32 / 250
████████████████░░░░░░░░  13%
```

## 🔧 Advanced Configuration

### config.toml
Advanced users can modify `config.toml`:
```toml
[display]
header_color = "#FF6B6B"
progress_bar_color = "#4ECDC4"

[behavior]
auto_save_stats = true
save_interval = 60

[export]
include_timestamp = true
include_scene_info = true
```

## 📝 Version Info

- **Version**: 1.0.0
- **Blender**: 4.2.0+
- **Category**: Render
- **License**: GPL-3.0-or-later

## 🤝 Support

For issues and feature requests, visit:
https://github.com/shabiramir604-dev/Blender-Render-Time-Tracker

## 🙏 Credits

Created for the Blender community.
