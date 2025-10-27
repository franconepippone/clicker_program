from __future__ import annotations
from typing import Any, TYPE_CHECKING, Dict, Tuple, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time

import pyautogui as gui
from pynput import keyboard

if TYPE_CHECKING:
    from executor import Executor  # only for type hints

##### Utility functions

def _add_to_history(shared: Dict):
    shared["mov_history"].append(gui.position())

def _get_from_hystory(shared: Dict) -> Tuple[int, int] | None:
    if len(shared["mov_history"]) > 0:
        return shared["mov_history"].pop(-1)

def _set_new_offset(shared: Dict, pos: Tuple[int, int]):
    shared["offset"] = pos

def _offset_point(shared: Dict, point: Tuple[int, int]) -> Tuple[int, int]:
    # adds stored offset to coordinate
    return point[0] + shared["offset"][0], point[1] + shared["offset"][1]



@dataclass
class Instruction(ABC):
    """Base instruction class"""

    @abstractmethod
    def execute(self, executor: Executor):
        """Implements execution logic for instruction"""
        raise NotImplementedError


### =================================== Internal Instructions ===================================

class SetupAndStart(Instruction):
    """ Sets up all the shared memory properties to work for all the commands """

    def execute(self, executor: Executor):
        executor.shared["mov_history"] = []     # creates history list
        _set_new_offset(executor.shared, (0,0))


### =================================== App Instructions ===================================

### --------------- MOVEMENT ---------------

class MouseCenter(Instruction):
    def execute(self, executor: Executor):
        _add_to_history(executor.shared)  # tracks history

        # Get screen width and height
        screen_width, screen_height = gui.size()

        # Calculate center coordinates
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Move mouse to center
        gui.moveTo(center_x, center_y)

@dataclass
class MouseMove(Instruction):
    """Moves mouse position to specified coordinate"""

    x: int
    y: int
    time: float = 0.0

    def execute(self, executor: Executor):
        _add_to_history(executor.shared)  # tracks history

        new_pos = _offset_point(executor.shared, (self.x, self.y))
        gui.moveTo(new_pos, duration=self.time)

        pos = gui.position()


@dataclass
class MouseMoveRel(Instruction):
    """Moves mouse position by relative coordinates"""

    x: int
    y: int
    time: float = 0.0

    def execute(self, executor: Executor):
        _add_to_history(executor.shared)  # tracks history

        gui.moveRel(self.x, self.y, self.time)


class MouseGoBack(Instruction):
    """Goes one step back in position history"""

    def execute(self, executor: Executor):
        # pop(-1) to history list
        pos = _get_from_hystory(executor.shared)

        if not pos: 
            executor.logger_internal.debug("Movement history is empty, cannot go back.")
            return
    
        gui.moveTo(pos)

class SetMouseOffset(Instruction):
    """Sets mouse coordinate origin to current mouse position"""

    def execute(self, executor: Executor):
        _set_new_offset(executor.shared, gui.position())

class ClearMouseOffset(Instruction):
    """Clears mouse position offset"""

    def execute(self, executor: Executor):
        _set_new_offset(executor.shared, (0,0))


### --------------- CLICKING ---------------

class MouseLeftClick(Instruction):
    """Left click the mouse in the current location"""

    def execute(self, executor: Executor):
        gui.leftClick()

class MouseRightClick(Instruction):
    """Right click the mouse in the current location"""

    def execute(self, executor: Executor):
        gui.rightClick()

class MouseDoubleClick(Instruction):
    """Double click the mouse in the current location"""
    def execute(self, executor: Executor):
        gui.doubleClick()


### --------------- WAITING ---------------

@dataclass
class Wait(Instruction):
    """Waits the given amount of time"""

    time_s: float

    def execute(self, executor: Executor):
        time.sleep(self.time_s)

class WaitInput(Instruction):
    """Waits until key press"""

    def _on_press(self, key: keyboard.Key):
        if key == keyboard.Key.space:
            return False    # stop listener

    def execute(self, executor: Executor):
       """Blocks until key is pressed"""
       executor.logger_internal.info("Press 'space' to resume.")
       with keyboard.Listener(on_press=self._on_press) as kb: # type: ignore
           kb.join()


### --------------- OTHERS ---------------

@dataclass
class JumpNTimes(Instruction):
    num: int
    jump_idx: int
    _cnt: int = 0
    jmp_name: str = "??"

    def execute(self, executor: Executor):
        """when jump doesnt occur, reset"""
        if self.num <= 0:
            # jump always if set to infinite jump
            executor.pc  =self.jump_idx - 1
            return

        self._cnt += 1
        if self._cnt > self.num:
            self._cnt = 0
            return  # do not jump, loop is over

        # jump
        executor.pc = self.jump_idx - 1

@dataclass
class ConsolePrint(Instruction):
    msg: str

    def execute(self, executor: Executor):
        print(self.msg)




