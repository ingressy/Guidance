import curses
import time
import ADC
import motors

def draw_slider(stdscr, label, value, start_y, start_x, height=20):
    mid = height // 2
    filled_pos = int((value / 100) * mid)
    filled_neg = int((-value / 100) * mid) if value < 0 else 0

    stdscr.addstr(start_y, start_x, label)
    for i in range(height):
        y = start_y + 1 + i
        if i == mid:
            stdscr.addstr(y, start_x, "|---|")
        elif value >= 0 and i >= mid - filled_pos and i < mid:
            stdscr.addstr(y, start_x, "|###|")
        elif value < 0 and i >= mid and i < mid + filled_neg:
            stdscr.addstr(y, start_x, "|xxx|")
        else:
            stdscr.addstr(y, start_x, "|   |")

    stdscr.addstr(start_y + 1 + height, start_x, f"{value:+.0f}%")


def draw_steering(stdscr, value, y, width=40):
    mid = width // 2
    filled = int(abs(value) / 100 * mid)
    bar = [" "] * width
    bar[mid] = "|"
    if value > 0:
        for i in range(mid, mid + filled):
            bar[i] = "#"
    elif value < 0:
        for i in range(mid - filled, mid):
            bar[i] = "#"
    stdscr.addstr(y, 0, "Lenkung: [" + "".join(bar) + "]")
    stdscr.addstr(y + 1, 0, f"         {value:+.0f}%")


def get_info(adc):
    volt = adc.get_12voltage(1)
    amp = adc.get_ampere(0)

    return [
        f"Volt: {volt}V",
        f"Ampere: {amp}A",
    ]


def draw_info_box(stdscr, lines, start_y, start_x, width=24):
    border = "+" + "-" * (width - 2) + "+"
    stdscr.addstr(start_y,     start_x, border)
    stdscr.addstr(start_y + 1, start_x, "| INFO |")
    stdscr.addstr(start_y + 2, start_x, border)
    for i, line in enumerate(lines):
        # Text auf Boxbreite kürzen/auffüllen
        content = line[:width - 4].ljust(width - 4)
        stdscr.addstr(start_y + 3 + i, start_x, f"| {content} |")
    bottom_y = start_y + 3 + len(lines)
    stdscr.addstr(bottom_y, start_x, border)


def main(stdscr):

    adc = ADC.ADC()

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    gas = 0
    lenkung = 0

    last_update = 0.0
    info_lines = get_info(adc)  # Startwert

    while True:
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key in (ord('w'), curses.KEY_UP):
            gas = min(100, gas + 2)
        elif key in (ord('s'), curses.KEY_DOWN):
            gas = max(-100, gas - 2)
        elif key in (ord('d'), curses.KEY_RIGHT):
            lenkung = min(100, lenkung + 2)
        elif key in (ord('a'), curses.KEY_LEFT):
            lenkung = max(-100, lenkung - 2)

        if gas > 0:
            motors.vorwaerts(gas)
        elif gas < 0:
            motors.rueckwaerts(gas)
        else:
            motors.stop()

        if lenkung > 0:
            motors.rechts(lenkung)
        elif lenkung < 0:
            motors.links(lenkung)
        else:
            motors.stoplenkung()


        # alle 3 Sekunden Info neu berechnen
        now = time.time()
        if now - last_update >= 3.0:
            info_lines = get_info(adc)
            last_update = now

        stdscr.clear()
        stdscr.addstr(0, 0, "W/S = Gas  |  A/D = Lenkung  |  q = Beenden")

        draw_slider(stdscr, "Gas/Bremse", gas, start_y=2, start_x=2)
        draw_steering(stdscr, lenkung, y=26)

        # Info-Box rechts neben den Regler (Spalte 20)
        draw_info_box(stdscr, info_lines, start_y=2, start_x=20)

        stdscr.refresh()
        time.sleep(0.02)

curses.wrapper(main)
