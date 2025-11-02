from __future__ import annotations
from typing import Dict, Tuple, List, Any, TypedDict, cast
from dataclasses import dataclass
import time
from enum import Enum
import logging

import pyautogui as gui
from pynput import keyboard

from app_logic.virtual_machine.executor import Executor, Instruction

##### Utility functions


class SharedRuntimeDict(TypedDict):
    """Defines the structure of the shared memory dictionary
    """
    mov_history: List[tuple[int, int]]
    pc_stack: List[int]
    safe_mode: bool
    vars: Dict[str, float]
    logger: logging.Logger
    offset: Tuple[int, int]

class VarMathOperations(Enum):
    SUM = 'sum'
    DIFFERENCE = 'diff'
    MULTIPLICATION = 'mult'
    DIV = 'div'

class val_ref:
    """Defines a reference to either a literal or a variable. 
    the get() method returns the value pointed to."""

    literal: int
    var_name: str
    
        

def _get_variable(shared: SharedRuntimeDict, name: str) -> float:
    val = shared["vars"].get(name)
    if val is None:
        raise RuntimeError(f"Undefined variable {name}")
    return val

def _set_variable(shared: SharedRuntimeDict, name: str, val: float):
    shared["vars"][name] = val

def _add_to_history(shared: SharedRuntimeDict):
    shared["mov_history"].append(gui.position())

def _get_from_hystory(shared: SharedRuntimeDict) -> Tuple[int, int] | None:
    if len(shared["mov_history"]) > 0:
        return shared["mov_history"].pop(-1)

def _set_new_offset(shared: SharedRuntimeDict, pos: Tuple[int, int]):
    shared["offset"] = pos


def _offset_point(shared: SharedRuntimeDict, point: Tuple[int, int]) -> Tuple[int, int]:
    # adds stored offset to coordinate
    return point[0] + shared["offset"][0], point[1] + shared["offset"][1]

def _push_pc(shared: SharedRuntimeDict, pc: int):
    shared["pc_stack"].append(pc)
    print(shared["pc_stack"])

def _pop_pc(shared: SharedRuntimeDict) -> int | None:
    if len(shared["pc_stack"]) > 0:
        return shared["pc_stack"].pop()
    shared["logger"].warning("Attempted return with empty stack")

def _set_safemode(shared: SharedRuntimeDict, value: bool):
    shared["safe_mode"] = value

def _get_safemode(shared: Dict) -> bool:
    return shared["safe_mode"]

def _getshrdict(executor: Executor) -> SharedRuntimeDict:
    return cast(SharedRuntimeDict, executor.shared)

### =================================== Internal Instructions ===================================

@dataclass
class SetupAndStart(Instruction):
    """ Sets up all the shared memory properties to work for all the commands """

    def execute(self, executor: Executor):
        shared: SharedRuntimeDict = _getshrdict(executor)
        shared["mov_history"] = []     # creates history list
        shared["pc_stack"] = []    # used with call / return to remember pc
        _set_new_offset(shared, (0,0))
        shared["safe_mode"] = False
        shared["vars"] = {}    # variables dict
        shared["logger"] = executor.logger_internal

### =================================== App Instructions ===================================

### --------------- MOVEMENT ---------------

class MouseCenter(Instruction):
    def execute(self, executor: Executor):
        _add_to_history(_getshrdict(executor))  # tracks history

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
        _add_to_history(_getshrdict(executor))  # tracks history

        new_pos = _offset_point(_getshrdict(executor), (self.x, self.y))
        gui.moveTo(new_pos, duration=self.time)

        pos = gui.position()


@dataclass
class MouseMoveRel(Instruction):
    """Moves mouse position by relative coordinates"""

    x: int
    y: int
    time: float = 0.0

    def execute(self, executor: Executor):
        _add_to_history(_getshrdict(executor))  # tracks history

        gui.moveRel(self.x, self.y, self.time)


class MouseGoBack(Instruction):
    """Goes one step back in position history"""

    def execute(self, executor: Executor):
        # pop(-1) to history list
        pos = _get_from_hystory(_getshrdict(executor))

        if not pos: 
            executor.logger_internal.debug("Movement history is empty, cannot go back.")
            return
    
        gui.moveTo(pos)

class SetMouseOffset(Instruction):
    """Sets mouse coordinate origin to current mouse position"""

    def execute(self, executor: Executor):
        _set_new_offset(_getshrdict(executor), gui.position())

class ClearMouseOffset(Instruction):
    """Clears mouse position offset"""

    def execute(self, executor: Executor):
        _set_new_offset(_getshrdict(executor), (0,0))


### --------------- CLICKING ---------------

class MouseLeftClick(Instruction):
    """Left click the mouse in the current location"""

    def execute(self, executor: Executor):
        if _get_safemode(_getshrdict(executor)): return  
        gui.leftClick()

class MouseRightClick(Instruction):
    """Right click the mouse in the current location"""

    def execute(self, executor: Executor):
        if _get_safemode(_getshrdict(executor)): return 
        gui.rightClick()

class MouseDoubleClick(Instruction):
    """Double click the mouse in the current location"""
    def execute(self, executor: Executor):
        if _get_safemode(_getshrdict(executor)): return
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

@dataclass
class ConsolePrint(Instruction):
    msg: str

    def execute(self, executor: Executor):
        executor.logger_internal.info(self.msg)

@dataclass
class SetSafeMode(Instruction):
    on: bool
    
    def execute(self, executor: Executor):
        _set_safemode(_getshrdict(executor), self.on)
        executor.logger_internal.info(f"Safe mode is {"enabled" if self.on else "disabled"}")

### --------------- FUNCTIONS ---------------

class Call(JumpNTimes):
    def execute(self, executor: Executor):
        _push_pc(_getshrdict(executor), executor.pc + 1) # next instruction
        super().execute(executor)

class Return(Instruction):
    def execute(self, executor: Executor):
        pc = _pop_pc(_getshrdict(executor))
        if pc:
            executor.pc = pc    # return to call point


### --------------- VARIABLES ---------------

@dataclass
class SetVar(Instruction):
    var_name: str
    val: float

    def execute(self, executor: Executor):
        _set_variable(_getshrdict(executor), self.var_name, self.val)

@dataclass
class VarMath(Instruction):
    out_var_name: str
    l_var_name: str
    r_var_name: str
    opcode: VarMathOperations

    def execute(self, executor: Executor):
        l_var: float = _get_variable(_getshrdict(executor), self.l_var_name)
        r_var: float = _get_variable(_getshrdict(executor), self.r_var_name)

        match self.opcode:
            case VarMathOperations.SUM:
                out = l_var + r_var
            case VarMathOperations.DIFFERENCE:
                out = l_var - r_var
            case VarMathOperations.MULTIPLICATION:
                out = l_var * r_var
            case VarMathOperations.DIV:
                out = l_var / r_var
            case _:
                raise RuntimeError(f"Unknown var math opcode {self.opcode}")

        _set_variable(_getshrdict(executor), self.out_var_name, out)


