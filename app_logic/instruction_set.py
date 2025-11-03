from __future__ import annotations
from typing import Dict, Tuple, List, Any, TypedDict, cast, overload, TypeVar, Type
from dataclasses import dataclass
import time
from enum import Enum
import logging
import re

import pyautogui as gui
from pynput import keyboard

from app_logic.virtual_machine.executor import Executor, Instruction

##### Utility classes

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
    DIVISION = 'div'

class ValueRef:
    """Descriptor that represents a reference to a literal or runtime variable."""

    literal: float | None
    var_name: str
    SHARED_DICT: SharedRuntimeDict

    def __init__(self, input: str):
        s = input.strip()
        try:
            self.literal = float(s)
            self.var_name = ""
        except ValueError:
            # MOVED IN COMPILER_CONFIG
            #if not _is_valid_var_name(s):
            #    raise Exception(f"Invalid variable name: {s}")
            self.literal = None
            self.var_name = s
    
    def __repr__(self) -> str:
        return self.__class__.__name__ + (f"(var={self.var_name})" if self.literal is None else f"(literal={self.literal})" )
    
    def __call__(self) -> float:
        return self.value

    @property
    def value(self) -> float:
        """Return the resolved value."""
        if self.literal is not None:
            return self.literal
        return _get_variable(self.SHARED_DICT, self.var_name)

    @classmethod
    def bind_shared_runtime_dict(cls, shared_dict: SharedRuntimeDict):
        cls.SHARED_DICT = shared_dict


## Utility memory functions
# 
# we could put all of these as class methods inside a class, so that the dict is not passed
# for each call but stored in the initial one.
# Partically equivalent to just storing the dict in a global variable

def _is_valid_var_name(name: str) -> bool:
    """
    Check whether a given string is a valid variable name.

    A valid name must:
    - be non-empty
    - start with a letter (A–Z, a–z) or underscore (_)
    - contain only letters, digits, and underscores
    """
    if not name or not isinstance(name, str):
        return False

    # Match: starts with letter or underscore, followed by letters/digits/underscores
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name):
        return False
    return True


def _get_variable(shared: SharedRuntimeDict, name: str) -> float:
    val = shared["vars"].get(name)
    if val is None:
        raise RuntimeError(f"Undefined variable '{name}'")
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

def _get_safemode(shared: SharedRuntimeDict) -> bool:
    return shared["safe_mode"]

def _getshrdict(executor: Executor) -> SharedRuntimeDict:
    return cast(SharedRuntimeDict, executor.shared)

def _point(x: int | float, y: int | float) -> Tuple[int, int]:
    """Convert two arguments to tuple of integer representing point on screen"""
    return int(x), int(y)

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
        ValueRef.bind_shared_runtime_dict(shared)    # set the class variable to the shared dictionary, so all val_ref objects have access to it

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

    x: ValueRef
    y: ValueRef
    time: float = 0.0

    def execute(self, executor: Executor):
        _add_to_history(_getshrdict(executor))  # tracks history
    
        new_pos = _offset_point(_getshrdict(executor), _point(self.x(), self.y()))
        gui.moveTo(new_pos, duration=self.time)

        pos = gui.position()


@dataclass
class MouseMoveRel(Instruction):
    """Moves mouse position by relative coordinates"""

    x: ValueRef
    y: ValueRef
    time: float = 0.0

    def execute(self, executor: Executor):
        _add_to_history(_getshrdict(executor))  # tracks history

        gui.moveRel(self.x(), self.y(), self.time)


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

    time_s: ValueRef

    def execute(self, executor: Executor):
        time.sleep(self.time_s())

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
    num: ValueRef       # if set to -1 do infinte jump
    jump_idx: int
    _cnt: int = 0
    jmp_name: str = "??"

    def execute(self, executor: Executor):
        """when jump doesnt occur, reset"""
        if self.num() <= 0:
            # jump always if set to infinite jump
            executor.pc  =self.jump_idx - 1
            return

        self._cnt += 1
        if self._cnt >= self.num():
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
class PrintVar(Instruction):
    var_name: str

    def execute(self, executor: Executor):
        val = _get_variable(_getshrdict(executor), self.var_name)
        executor.logger_internal.info(f"{self.var_name} = {val}")


@dataclass
class SetVar(Instruction):
    var_name: str
    val: ValueRef

    def execute(self, executor: Executor):
        _set_variable(_getshrdict(executor), self.var_name, self.val())

@dataclass
class VarMath(Instruction):
    out_var_name: str
    l_val: ValueRef
    r_val: ValueRef
    opcode: VarMathOperations

    def execute(self, executor: Executor):
        match self.opcode:
            case VarMathOperations.SUM:
                out = self.l_val() + self.r_val()
            case VarMathOperations.DIFFERENCE:
                out = self.l_val() - self.r_val()
            case VarMathOperations.MULTIPLICATION:
                out = self.l_val() * self.r_val()
            case VarMathOperations.DIVISION:
                out = self.l_val() / self.r_val()
            case _:
                raise RuntimeError(f"Unknown var math opcode {self.opcode}")

        _set_variable(_getshrdict(executor), self.out_var_name, out)


