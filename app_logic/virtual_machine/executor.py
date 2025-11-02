from __future__ import annotations
from typing import Tuple, Iterable, Dict, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import threading

logger = logging.getLogger("Runtime")

@dataclass
class Instruction(ABC):
    """Base instruction class"""

    @abstractmethod
    def execute(self, executor: Executor):
        """Implements execution logic for instruction"""
        raise NotImplementedError


class Executor:
    """Helper class to execute a list of instruction"""

    program: Tuple[Instruction, ...] = tuple()
    pc: int = 0
    running: bool = False
    logger_internal = logger
    shared: Dict
    play_event: None | threading.Event = None
    pause_callback: None | Callable[[], None] = None
    resume_callback: None | Callable[[], None] = None

    def load_instructions(self, instructions: Iterable[Instruction]) -> Executor:
        self.program = tuple(instructions)
        return self
    
    def set_pause_callback(self, cb: Callable[[], None]):
        """Sets a callback to be called when execution is paused.
        Only works when a play_event is provided to execute().
        """
        self.pause_callback = cb
    
    def set_resume_callback(self, cb: Callable[[], None]):
        """Sets a callback to be called when execution is resumed.
        Only works when a play_event is provided to execute().
        """
        self.resume_callback = cb

    def is_paused(self) -> bool:
        """Returns whether execution is currently paused."""
        if self.play_event is None:
            return False
        return not self.play_event.is_set()

    def pause(self):
        """Pauses execution"""
        if self.play_event is not None:
            if not self.play_event.is_set():
                return  # already paused
            self.play_event.clear()
            if self.pause_callback:
                self.pause_callback()
            logger.info("Execution paused.")
    
    def resume(self):
        """Resumes execution"""
        if self.play_event is not None:
            if self.play_event.is_set():
                return  # already playing
            self.play_event.set()
            if self.resume_callback:
                self.resume_callback()
            logger.info("Execution resumed.")

    def execute(self, play_event: None | threading.Event = None):
        """Executes loaded program. A threading event can be provided to allow finer control over pausing in a different thread.
        If none is provided, an event will be created. You can use is_paused(), pause() and resume() methods to control execution from 
        another thread."""

        if len(self.program) == 0:
            logger.warning("Program does not contain any instruction.")
            return

        self.shared = {}    # where commands can store shared temporary runtime data

        self.pc = 0
        self.running = True
        self.play_event = play_event if play_event is not None else threading.Event()
        self.play_event.set()  # start in playing state

        logger.info("Beginning execution")
        while self.running:

            if self.play_event is not None:
                if not self.play_event.is_set():
                    logger.debug("Execution is now waiting to be resumed.")
                self.play_event.wait()  # will block here if paused

            if self.pc >= len(self.program):
                break
            
            inst: Instruction = self.program[self.pc]
            try:
                inst.execute(self)
            except Exception as e:
                logger.critical(f"Execution of {inst} raised an exception: {e}")
                return 

            logger.debug(f"Executed instruction {inst}")

            self.pc += 1
        
        logger.info("Program terminated.")
            



        