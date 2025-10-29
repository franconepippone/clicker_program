from __future__ import annotations
from typing import Tuple, Iterable, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

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

    def load_instructions(self, instructions: Iterable[Instruction]) -> Executor:
        self.program = tuple(instructions)
        return self
    
    def execute(self):
        """Executes loaded program"""
        if len(self.program) == 0:
            logger.warning("Program does not contain any instruction.")
            return

        self.shared = {}    # where commands can store shared temporary runtime data

        self.pc = 0
        self.running = True
        logger.info("Beginning execution")
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


        