from __future__ import annotations
from typing import Dict, Tuple, List
from dataclasses import dataclass
import time

import pyautogui as gui
from pynput import keyboard

from app_logic.virtual_machine.executor import Executor, Instruction

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

def _push_pc(shared: Dict, pc: int):
    print("PUSHING PC: ", pc)
    shared["inst_ptr"].append(pc)
    print(shared["inst_ptr"])

def _pop_pc(shared: Dict) -> int | None:
    print("POPPING PC")
    if len(shared["inst_ptr"]) > 0:
        return shared["inst_ptr"].pop()
    else:
        print("WARNING")

### =================================== Internal Instructions ===================================

class SetupAndStart(Instruction):
    """ Sets up all the shared memory properties to work for all the commands """

    def execute(self, executor: Executor):
        executor.shared["mov_history"] = []     # creates history list
        executor.shared["inst_ptr"] = []    # used with call / return to remember pc
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

class Pause(Instruction):
    """Pauses """

    def _on_press(self, key: keyboard.Key):
        if key == keyboard.Key.space:
            return False    # stop listener

    def execute(self, executor: Executor):
       """Pauses executor"""
       executor.pause()


### --------------- OTHERS ---------------

@dataclass
class JumpNTimes(Instruction):
    num: int # if set to -1 do infinte jump
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
        if self._cnt >= self.num:
            self._cnt = 0
            return  # do not jump, loop is over

        # jump
        executor.pc = self.jump_idx - 1

class Call(JumpNTimes):
    def execute(self, executor: Executor):
        _push_pc(executor.shared, executor.pc + 1) # next instruction
        super().execute(executor)

class Return(Instruction):
    def execute(self, executor: Executor):
        pc = _pop_pc(executor.shared)
        if pc:
            executor.pc = pc    # return to call point

@dataclass
class ConsolePrint(Instruction):
    msg: str

    def execute(self, executor: Executor):
        executor.logger_internal.info(self.msg)




