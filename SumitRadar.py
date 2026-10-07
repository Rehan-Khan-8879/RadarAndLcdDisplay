import tkinter as tk
import serial
import threading
import math
import time


PORT = "COM7"    # CHANGE this according to DEVICE MANAGER
BAUDRATE = 115200

MAX_DISTANCE = 40
DOT_LIFETIME = 2.0   # Change this for Dot time in Scanner





WIDTH = 900
HEIGHT = 600

BG = "#000000"
GREEN = "#00ff41"
DARK_GREEN = "#064d18"
RED = "#ff3333"
WHITE = "#ffffff"




ser = None
running = True

current_angle = 90
current_distance = MAX_DISTANCE

targets = []

data_lock = threading.Lock()



# useing for Serial reading
def read_serial():

    global current_angle
    global current_distance

    while running:

        if ser is None:
            time.sleep(0.1)
            continue

        try:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            parts = line.split(",")

            if len(parts) != 2:
                continue

            angle = int(parts[0])
            distance = int(parts[1])

            if not 0 <= angle <= 180:
                continue

            if distance < 0:
                continue

            if distance > MAX_DISTANCE:
                distance = MAX_DISTANCE

            with data_lock:

                current_angle = angle
                current_distance = distance

                # Store real detections with timestamp
                if 2 <= distance < MAX_DISTANCE:

                    targets.append(
                        (angle, distance, time.time())
                    )

                # Remove old targets
                current_time = time.time()

                targets[:] = [
                    target
                    for target in targets
                    if current_time - target[2] <= DOT_LIFETIME
                ]

        except (ValueError, serial.SerialException):

            time.sleep(0.01)


# =====================================================
# RADAR GUI
# =====================================================

class RadarGUI:

    def __init__(self, root):

        self.root = root

        root.title(
            "Arduino HC-SR04 Radar"
        )

        root.configure(
            bg="#101820"
        )

        root.geometry(
            "950x760"
        )

        root.resizable(
            False,
            False
        )


        # =============================================
        # TITLE
        # =============================================

        title = tk.Label(
            root,
            text="ULTRASONIC RADAR SYSTEM",
            font=("Arial", 22, "bold"),
            fg=GREEN,
            bg="#101820"
        )

        title.pack(pady=10)


        # =============================================
        # RADAR CANVAS
        # =============================================

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=1,
            highlightbackground=GREEN
        )

        self.canvas.pack(
            padx=10
        )


        # =============================================
        # STATUS
        # =============================================

        self.status = tk.Label(
            root,
            text="CONNECTING...",
            font=("Consolas", 12),
            fg=GREEN,
            bg="#101820"
        )

        self.status.pack(pady=8)


        # =============================================
        # READING
        # =============================================

        self.info = tk.Label(
            root,
            text="Angle: --°    Distance: -- cm",
            font=("Consolas", 16, "bold"),
            fg=WHITE,
            bg="#101820"
        )

        self.info.pack(pady=5)


        # =============================================
        # CLEAR BUTTON
        # =============================================

        tk.Button(
            root,
            text="CLEAR TARGETS",
            command=self.clear_targets,
            bg="#173b25",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(pady=5)


        self.draw_radar()

        self.update_radar()

        root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )


    # =================================================
    # CLEAR TARGETS
    # =================================================

    def clear_targets(self):

        with data_lock:
            targets.clear()


    # =================================================
    # DRAW RADAR
    # =================================================

    def draw_radar(self):

        c = self.canvas

        c.delete("background")

        self.cx = WIDTH / 2
        self.cy = HEIGHT - 45

        self.radius = min(
            WIDTH / 2 - 50,
            HEIGHT - 80
        )


        # =============================================
        # DISTANCE RINGS
        # =============================================

        for cm in range(
            4,
            MAX_DISTANCE + 1,
            4
        ):

            r = (
                self.radius
                * cm
                / MAX_DISTANCE
            )

            c.create_arc(
                self.cx - r,
                self.cy - r,
                self.cx + r,
                self.cy + r,
                start=0,
                extent=180,
                style=tk.ARC,
                outline=DARK_GREEN,
                width=2,
                tags="background"
            )

            c.create_text(
                self.cx + 8,
                self.cy - r + 12,
                text=f"{cm} cm",
                fill=GREEN,
                font=("Consolas", 9),
                tags="background"
            )


        # =============================================
        # ANGLE LINES
        # =============================================

        for angle in range(
            0,
            181,
            30
        ):

            x, y = self.point(
                angle,
                MAX_DISTANCE
            )

            c.create_line(
                self.cx,
                self.cy,
                x,
                y,
                fill=DARK_GREEN,
                width=1,
                tags="background"
            )

            c.create_text(
                x,
                y - 15,
                text=f"{angle}°",
                fill=GREEN,
                font=("Consolas", 10),
                tags="background"
            )


        # =============================================
        # CENTER
        # =============================================

        c.create_oval(
            self.cx - 5,
            self.cy - 5,
            self.cx + 5,
            self.cy + 5,
            fill=GREEN,
            outline=GREEN,
            tags="background"
        )


    # =================================================
    # CONVERT POLAR → SCREEN
    # =================================================

    def point(
        self,
        angle,
        distance
    ):

        theta = math.radians(angle)

        r = (
            self.radius
            * min(distance, MAX_DISTANCE)
            / MAX_DISTANCE
        )

        x = (
            self.cx
            - r * math.cos(theta)
        )

        y = (
            self.cy
            - r * math.sin(theta)
        )

        return x, y


    # =================================================
    # UPDATE RADAR
    # =================================================

    def update_radar(self):

        if not running:
            return

        with data_lock:

            angle = current_angle
            distance = current_distance

            current_time = time.time()

            # Remove expired dots
            targets[:] = [
                target
                for target in targets
                if current_time - target[2] <= DOT_LIFETIME
            ]

            visible_targets = list(targets)


        c = self.canvas

        c.delete("dynamic")


        # =============================================
        # DETECTED OBJECTS
        # =============================================

        for a, d, timestamp in visible_targets:

            x, y = self.point(
                a,
                d
            )

            c.create_oval(
                x - 4,
                y - 4,
                x + 4,
                y + 4,
                fill=RED,
                outline=RED,
                tags="dynamic"
            )


        # =============================================
        # SCANNING LINE
        # =============================================

        x, y = self.point(
            angle,
            MAX_DISTANCE
        )

        c.create_line(
            self.cx,
            self.cy,
            x,
            y,
            fill=GREEN,
            width=3,
            tags="dynamic"
        )


        # =============================================
        # CURRENT READING
        # =============================================

        self.info.config(
            text=(
                f"Angle: {angle:3d}°    "
                f"Distance: {distance:3d} cm"
            )
        )


        # =============================================
        # CONNECTION STATUS
        # =============================================

        if ser and ser.is_open:

            self.status.config(
                text=(
                    f"CONNECTED | {PORT} | "
                    f"RANGE: {MAX_DISTANCE} cm | "
                    f"DOT TIME: {DOT_LIFETIME} sec"
                ),
                fg=GREEN
            )

        else:

            self.status.config(
                text="NOT CONNECTED",
                fg=RED
            )


        self.root.after(
            30,
            self.update_radar
        )


    # =================================================
    # CLOSE
    # =================================================

    def close(self):

        global running

        running = False

        if ser is not None:

            try:
                ser.close()
            except:
                pass

        self.root.destroy()


# =====================================================
# MAIN
# =====================================================

def main():

    global ser

    root = tk.Tk()

    try:

        ser = serial.Serial(
            PORT,
            BAUDRATE,
            timeout=1
        )

        time.sleep(2)

        threading.Thread(
            target=read_serial,
            daemon=True
        ).start()

    except serial.SerialException as e:

        print("Serial connection failed:")
        print(e)

        print(
            "Check the Arduino COM port."
        )

        ser = None

    RadarGUI(root)

    root.mainloop()


# =====================================================
# START
# =====================================================

if __name__ == "__main__":

    main()
