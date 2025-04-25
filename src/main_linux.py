import asyncio
import subprocess
from Xlib import display

def get_mouse_position():
    d = display.Display()
    s = d.screen()
    root = s.root
    data = root.query_pointer()._data
    return data["root_x"], data["root_y"]

def get_monitors():
    result = subprocess.run(['xrandr'], capture_output=True, text=True)
    monitors = []
    for line in result.stdout.splitlines():
        if ' connected' in line and '+' in line:
            parts = line.split()
            resolution_part = [p for p in parts if '+' in p][0]
            res, x, y = resolution_part.split('+')
            width, height = map(int, res.split('x'))
            x, y = int(x), int(y)
            monitors.append((x, y, width, height))
    return monitors

def get_monitor_from_position(x, y):
    for mon_x, mon_y, mon_w, mon_h in get_monitors():
        if mon_x <= x < mon_x + mon_w and mon_y <= y < mon_y + mon_h:
            return (mon_x, mon_y, mon_w, mon_h)
    return None

async def monitor_mouse_edges():
    border_threshold = 1
    seen_edges = set()

    while True:
        x, y = get_mouse_position()
        monitor = get_monitor_from_position(x, y)

        if not monitor:
            await asyncio.sleep(0.05)
            continue

        mon_x, mon_y, mon_w, mon_h = monitor
        edges = set()

        if x <= mon_x + border_threshold:
            edges.add("LEFT")
        if x >= mon_x + mon_w - border_threshold:
            edges.add("RIGHT")
        if y <= mon_y + border_threshold:
            edges.add("TOP")
        if y >= mon_y + mon_h - border_threshold:
            edges.add("BOTTOM")

        for edge in edges - seen_edges:
            print(f"Mouse reached {edge} edge of monitor at ({mon_x}, {mon_y})")

        seen_edges = edges
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(monitor_mouse_edges())