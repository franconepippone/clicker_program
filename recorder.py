from typing import List
import time

from pynput import mouse, keyboard

from commands import (
    Instruction,
    Wait,
    MouseLeftClick,
    MouseRightClick,
    MouseMove,
    MouseDoubleClick
)

# ================================
# === Input Recorder ===
# ================================

class Recorder:
    """Records user mouse/keyboard actions into a list of Instruction objects"""

    DOUBLE_CLICK_THRESHOLD = .25    #seconds

    instructions: List[Instruction]
    _last_time: float
    _recording: bool

    def __init__(self):
        self.instructions = []
        self._last_time = time.time()
        self._recording = False

    def _add_wait_if_needed(self) -> float:
        """Adds a Wait instruction based on time since last event.
        Returns delta time from last mouse event
        """
        now = time.time()
        delta = now - self._last_time
        self._last_time = now
        if delta > 0.1:  # Ignore very small pauses
            self.instructions.append(Wait(delta))
        return delta

    # -----------------------------
    # Mouse Events
    # -----------------------------

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool):
        if not self._recording or not pressed: return
        delta_t = self._add_wait_if_needed()

        # add move
        self.instructions.append(MouseMove(x, y))

        # add click
        if button == mouse.Button.left:
            is_double_click = delta_t < self.DOUBLE_CLICK_THRESHOLD
            self.instructions.append(MouseLeftClick() if not is_double_click else MouseDoubleClick())
        elif button == mouse.Button.right:
            self.instructions.append(MouseRightClick())

    # -----------------------------
    # Keyboard Events
    # -----------------------------
    def _on_press(self, key: keyboard.Key):
        if key == keyboard.Key.esc:  # Stop recording on ESC
            print("Recording stopped.")
            self._recording = False
            return False  # Stop listener

    # -----------------------------
    # Recording Control
    # -----------------------------
    def start(self):
        """Begin recording mouse/keyboard events"""
        print("Recording... (press ESC to stop)")
        self._recording = True
        self._last_time = time.time()

        with mouse.Listener(on_click=self._on_click) as m_listener, \
             keyboard.Listener(on_press=self._on_press) as k_listener: # type: ignore
            k_listener.join()

        print("Recording complete. {} instructions captured.".format(len(self.instructions)))

    def get_instructions(self) -> List[Instruction]:
        return self.instructions



if __name__ == "__main__":
    recorder = Recorder()
    recorder.start()

    print(recorder.get_instructions())