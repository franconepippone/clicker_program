from __future__ import annotations
from typing import Tuple, Iterable, Dict
from commands import Instruction
import logging

from pynput import mouse, keyboard

logger = logging.getLogger("Runtime")


class Executor:
    """Helper class to execute a list of instruction"""

    program: Tuple[Instruction, ...] = tuple()
    pc: int = 0
    running: bool = False
    logger_internal = logger
    shared: Dict

    def _on_press(self, key: keyboard.Key):
        if key == keyboard.Key.esc:  # Stop recording on ESC
            logger.info("ESC pressed, stopping execution...")
            self.running = False
            return False  # Stop listener

    def load_instructions(self, instructions: Iterable[Instruction]) -> Executor:
        self.program = tuple(instructions)
        return self
    
    def execute(self):
        """Executes loaded program"""
        if len(self.program) == 0:
            logger.warning("Program does not contain any instruction.")
            return
        
        kblistener = keyboard.Listener(on_press=self._on_press)  # type: ignore
        kblistener.start()
        kblistener.wait()

        self.shared = {}    # where commands can store shared temporary runtime data

        self.pc = 0
        self.running = True
        logger.info("Beginning execution, press ESC to terminate.")
        while self.running:
            if self.pc >= len(self.program):
                break
            
            inst: Instruction = self.program[self.pc]
            inst.execute(self)
            logger.debug(f"Executed instruction {inst}")

            self.pc += 1
        
        logger.info("Program terminated.")
            


if __name__ == "__main__":
    import logger_config


        