# EuroLeague Final 4 Ticket Queue Auto-Joiner - Setup Guide

## Quick Start

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

This will install both Selenium and webdriver-manager, which automatically downloads and manages ChromeDriver for you (no manual download needed!).

### 2. Configure the Script

Edit `euroleague_ticket_queue.py` and set:

```python
QUEUE_OPEN_TIME = "10:00:00"  # Set to actual queue opening time (24-hour format)
```

### 3. Run the Script

**Before queue opens:**
```bash
python euroleague_ticket_queue.py
```
Choose option [1] to wait until queue opens

**When queue is already open:**
```bash
python euroleague_ticket_queue.py
```
Choose option [2] to join immediately

## How It Works

1. **Browser Setup**: Opens Chrome browser (visible, not headless)
2. **Manual Login**: You log in with your EuroLeague ID
3. **Session Preservation**: Keeps your login session active
4. **Countdown Timer**: Waits until queue opening time
5. **Auto-Refresh**: Automatically refreshes and tries to join queue
6. **Queue Monitoring**: Monitors your position and notifies when through
7. **Manual Completion**: Leaves browser open for you to complete purchase

## Tips for Success

### Timing
- Run the script 5-10 minutes before queue opens
- Make sure your system time is accurate
- Consider time zones (queue time is likely in CET/CEST)

### Before Running
- Close other Chrome instances to avoid conflicts
- Ensure stable internet connection

### During the Process
- Don't close the browser window
- Don't close the terminal/command prompt
- Keep the script running until you complete purchase
- If something goes wrong, you can take over manually



Good luck getting your Final 4 tickets! 🏀🎉
