# 💕 Two-Do List

*A to-do list, for two.*

A real-time shared todo list, calendar, and shopping list for two people on the same network. No accounts, no cloud, no subscriptions — just run it on any computer at home and open it on your phones.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-2.0+-green) ![No DB](https://img.shields.io/badge/Database-none-lightgrey)

---

## Features

- ✅ **Shared todo list** — add, check off, and delete tasks together in real time
- 📅 **Shared calendar** — monthly grid with event dots, tap any day to add events
- 🔁 **Recurring events** — daily, weekly, monthly, or custom days (e.g. dance class every Tue & Thu)
- 🛒 **Shared shopping list** — grouped by aisle, drag items between categories, share to WhatsApp
- 📺 **TV dashboard** — cast to your TV via Chromecast, shows todo list + live clock
- 👤 **Who added it** — tag items as You, Her, or Us with emoji labels
- ⚡ **Live sync** — changes appear on the other person's screen in under a second (long-polling, no WebSockets needed)
- 📱 **Mobile friendly** — works great on phones, just open the browser
- 💾 **No database** — all data stored in plain JSON files on disk
- 🏠 **Local network only** — your data never leaves your home

---

## Requirements

- Python 3.8 or newer
- Flask (`pip install flask`)
- Any modern browser

---

## Quick Start

### Windows

1. **Install Python** if you don't have it: https://python.org/downloads  
   *(tick "Add Python to PATH" during install)*

2. **Download and extract** this project somewhere permanent, e.g. `C:\todo-app`

3. **Open PowerShell** in that folder and install Flask:
   ```powershell
   pip install flask
   ```

4. **Run the server:**
   ```powershell
   python server.py
   ```

5. **Open in your browser:** http://localhost:5001

6. **Share with your partner** — find your PC's local IP:
   ```powershell
   ipconfig
   # look for "IPv4 Address" under your Wi-Fi adapter e.g. 192.168.1.42
   ```
   They open `http://192.168.1.42:5001` on their phone (must be on the same Wi-Fi).

---

### Mac / Linux

```bash
pip3 install flask
python3 server.py
```

Then open http://localhost:5001. Find your local IP with:
```bash
# Mac
ipconfig getifaddr en0

# Linux
ip addr show | grep 'inet '
```

---

### Linux / WSL (Windows Subsystem for Linux)

If running inside WSL, other devices can't reach WSL directly. You need to forward the port from Windows into WSL.

**In WSL — start the server:**
```bash
pip3 install flask
python3 server.py
```

**In Windows Admin PowerShell — forward the port:**
```powershell
# Get the WSL internal IP
$wslIp = (wsl ip addr show eth0 | Select-String 'inet ' | ForEach-Object { $_.ToString().Trim().Split(' ')[1].Split('/')[0] })

# Forward Windows port 5001 → WSL
netsh interface portproxy delete v4tov4 listenport=5001 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5001 connectaddress=$wslIp

# Open firewall
New-NetFirewallRule -DisplayName "Todo App" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow
```

> **Note:** WSL's internal IP changes on every reboot. Re-run the PowerShell block after each restart, or set up a startup script (see [Auto-start on Windows](#auto-start-on-windows) below).

---

## Auto-start on Windows

So the server starts automatically every time Windows boots:

1. Make sure the app is in a permanent location (e.g. `C:\todo-app`, not Downloads)

2. Run this once in **Admin PowerShell:**
```powershell
$action = New-ScheduledTaskAction `
  -Execute "python.exe" `
  -Argument "C:\todo-app\server.py" `
  -WorkingDirectory "C:\todo-app"

$trigger = New-ScheduledTaskTrigger -AtStartup

$settings = New-ScheduledTaskSettingsSet `
  -RestartCount 999 `
  -RestartInterval (New-TimeSpan -Minutes 1) `
  -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask `
  -TaskName "TodoApp" `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -RunLevel Highest `
  -User "$env:USERDOMAIN\$env:USERNAME" `
  -Description "Start two-do app on boot"
```

3. Test it without rebooting:
```powershell
Start-ScheduledTask -TaskName "TodoApp"
```

To remove it later:
```powershell
Unregister-ScheduledTask -TaskName "TodoApp" -Confirm:$false
```

---

## Usage Guide

### To-Do Tab

| Action | How |
|--------|-----|
| Add a task | Type in the box, press Enter or + |
| Pick a category | Use the emoji dropdown (🛒 🍽️ 🎬 etc.) |
| Mark done | Tap the circle on the left |
| Delete | Hover over a task, tap ✕ |
| Filter | Use the buttons: All / To do / Done / Yours / Hers / Ours |

**Today's plans** strip at the bottom always shows today's calendar events so you never have to switch tabs to check.

---

### Schedule Tab

| Action | How |
|--------|-----|
| View a month | Use ‹ › arrows |
| Add an event | Tap any day on the grid |
| See a day's events | Tap the day — events appear below the calendar |
| Delete an event | Hover over the event card, tap ✕ |

**Days with events** show small coloured dots:
- 🌹 Rose dot = one-time event
- 🌿 Green dot = recurring event

#### Recurring Events

When adding an event, choose how often it repeats:

| Option | Description |
|--------|-------------|
| Does not repeat | One-time event |
| Every day | Repeats daily from the start date |
| Every week | Repeats on the same weekday |
| Every month | Repeats on the same date each month |
| Custom days | Pick specific weekdays (e.g. Tue + Thu for dance class) |

All recurring options support an optional **end date**. Leave it blank to repeat forever.

> Recurring events are stored as a single record — the app expands them on the fly. Deleting a recurring event removes the whole series.

---

### Shopping Tab

| Action | How |
|--------|-----|
| Add an item | Type name, set quantity, unit, and aisle, press + |
| 1x vs 🔁 Weekly | Choose before adding — weekly items stay on the list after shopping |
| Check off | Tap the circle as you grab items in the store |
| Move to different aisle | Drag the ⠿ handle and drop onto another aisle section |
| Done shopping | Tap **✓ Done Shopping** — clears checked items, resets weekly ones |
| Share list | Tap **📤 Share List** — copies a WhatsApp-ready formatted list to clipboard |

**Aisles available:** Produce, Dairy, Meat, Bakery, Pantry, Frozen, Personal Care, Household, Drinks, Pet, Other.

**WhatsApp export format:**
```
🛒 Shopping List
_Mar 1_

*🥦 Produce*
• 2kg Apples 🔁
• Spinach

*🥛 Dairy*
• 6x Eggs
```

---

### TV Dashboard

A separate page designed to be cast to your TV via Chromecast — dark background, large text readable from across the room.

**Open it at:** `http://YOUR-PC-IP:5001/dashboard`

**To cast with Chromecast:**
1. Open Chrome on your phone or laptop
2. Go to `http://YOUR-PC-IP:5001/dashboard`
3. Tap the three dots menu → **Cast**
4. Select your Chromecast

The dashboard shows:
- Live clock and date
- All active todo items (large, readable)
- Progress stats — items left, items done, progress bar
- Recently completed items
- Auto-updates in real time as you tick things off on your phone

---

### Who Is Adding?

Switch between **🌸 You**, **💛 Her**, and **💑 Us** at the top before adding anything. This tags the item so you can filter later and see who added what.

---

## File Structure

```
todo-app/
├── server.py          ← Flask backend — REST API + long-poll sync
├── requirements.txt   ← Python dependencies (just Flask)
├── tasks.json         ← your to-do list (auto-created on first use)
├── events.json        ← your calendar events (auto-created on first use)
├── shopping.json      ← your shopping list (auto-created on first use)
├── .last_change       ← timestamp file used for sync (auto-created)
├── README.md          ← this file
└── static/
    ├── index.html     ← the entire frontend (HTML + CSS + JS in one file)
    └── dashboard.html ← TV dashboard page
```

> ⚠️ Your data lives in the `.json` files. When updating the app, only replace `server.py`, `index.html`, and `dashboard.html` — never delete the `.json` files or you'll lose your data.

---

## How It Works (Technical)

### Backend (`server.py`)

A small Flask app with three sets of REST endpoints — tasks, events, and shopping. Data lives in plain JSON files (no database needed). A `threading.Lock()` prevents file corruption when two people save at the same time.

**API endpoints:**
```
GET    /api/tasks              → return all tasks
POST   /api/tasks              → create a task
PUT    /api/tasks/<id>         → update a task (toggle done, edit text)
DELETE /api/tasks/<id>         → delete a task

GET    /api/events             → return all events
POST   /api/events             → create an event (with recurrence fields)
PUT    /api/events/<id>        → update an event
DELETE /api/events/<id>        → delete an event

GET    /api/shopping           → return all shopping items
POST   /api/shopping           → create a shopping item
PUT    /api/shopping/<id>      → update an item (check off, change aisle etc.)
DELETE /api/shopping/<id>      → delete an item
POST   /api/shopping/clear-checked → clear checked items after shopping

GET    /api/poll/<ts>          → long-poll: blocks up to 25s, returns when anything changes
```

### Real-Time Sync (Long Polling)

Instead of WebSockets, the app uses **long polling**:

1. Your browser calls `GET /api/poll/<timestamp>`
2. Flask sleeps in a loop, checking every 500ms if anything changed
3. The moment data changes, Flask returns immediately with fresh tasks, events, and shopping
4. Your browser renders the update, then fires another poll immediately
5. This creates a persistent loop that delivers updates in under 1 second

Simple, reliable, and works on any network without special configuration.

### Recurrence Engine (Frontend)

Recurring events are stored **once** with metadata fields (`recur`, `recur_days`, `recur_end`). The frontend has a small `eventOccursOn(event, date)` function that computes whether any event falls on a given day. This means:

- The calendar dots are computed live
- Today's strip is computed live
- No duplicate records are ever stored
- Deleting a series deletes one record

---

## Customisation

**Change the port** — edit the last line of `server.py`:
```python
app.run(host="0.0.0.0", port=5001, ...)  # change 5001 to whatever you like
```

**Change the names/emoji** — search `index.html` for `🌸 You`, `💛 Her`, `💑 Us` and replace with whatever you like.

**Add more task categories** — find the `<select class="cat-select">` in `index.html` and add more `<option>` emoji.

**Add more shopping aisles** — find the `<select id="sh-aisle">` in `index.html` and add more `<option>` entries.

---

## Troubleshooting

**"No module named flask"**
```bash
pip install flask
# or on some systems:
pip3 install flask
python3 -m pip install flask
```

**Port already in use**
Something else is using port 5001. Either stop that process or change the port in `server.py`.

**Partner can't connect from their phone**
- Make sure they're on the **same Wi-Fi network** (not mobile data)
- Check your firewall allows port 5001 (see Windows setup above)
- Use your PC's local IP (e.g. `192.168.1.42`), not `localhost`

**Changes not showing up in real time**
Check the sync indicator dot at the top of the app. If it shows "offline" or "reconnecting", the browser can't reach the server — refresh the page.

**Drag and drop not working on mobile**
The drag-to-reorder feature uses the HTML5 drag API which has limited support on mobile browsers. Use the aisle dropdown when adding items instead, or edit on desktop.

---

## License

Do whatever you want with this. It's a personal project — make it your own. 💕
