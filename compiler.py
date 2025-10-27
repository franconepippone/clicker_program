from typing import List, Tuple, Dict, Callable
import re
import logging

from commands import (
    Instruction,
    Wait,
    MouseLeftClick,
    MouseRightClick,
    MouseMove,
    MouseMoveRel,
    MouseDoubleClick,
    JumpNTimes,
    ConsolePrint,
    MouseCenter,
    WaitInput,
    MouseGoBack,
    SetupAndStart
)

logger = logging.getLogger("Compiler")


class CompilationError(Exception):
    line_i: int

    def __init__(self, line_i: int, *args: object) -> None:
        super().__init__(*args)
        self.line_i = line_i
    
    def get_line(self) -> int:
        return self.line_i



class Compiler:

    COMMENT = r";"
    COMMAND_TABLE: Dict[str, Callable]

    # these are not executable commands, only exist for the compiler
    COMPILER_DIRECTIVES: Dict[str, Callable]

    found_labels: Dict[str, int]    # name, idx pair
    instructions: List[Instruction] 

    def __init__(self) -> None:
        self.found_labels = {}
        self.instructions = []

        self.COMMAND_TABLE = {
            "move" : lambda x, y, t='0.0': MouseMove(int(x), int(y), float(t)),
            "moverel" : lambda x, y, t='0.0' : MouseMoveRel(int(x), int(y), float(t)),
            "click" : lambda butt='left': MouseRightClick() if butt == 'right' else MouseLeftClick(),
            "wait"  : lambda t='0.0' : Wait(float(t)),
            "doubleclick" : lambda: MouseDoubleClick(),
            "jump" : lambda name, n=-1: JumpNTimes(int(n), self._get_label_jmp_idx(name), jmp_name=name),
            "print" : lambda *args: ConsolePrint(' '.join(args)),
            "centermouse" : lambda: MouseCenter(),
            "waitinput" : lambda: WaitInput(),
            "goback" : lambda: MouseGoBack()
        }

        self.COMPILER_DIRECTIVES = {
            "label" : self._register_label
        }

    def _get_label_jmp_idx(self, name: str) -> int:
        jmp_idx: int | None = self.found_labels.get(name)
        if not jmp_idx:
            raise CompilationError(-1, f'Undefined label "{name}"')

        return jmp_idx

    def _register_label(self, name: str):
        if name in self.found_labels:
            raise CompilationError(-1, f'Label "{name}" already defined')
        
        jmp_idx = len(self.instructions) # points to the next instruction in the instruction list
        self.found_labels[name] = jmp_idx    # registers label

    def _preprocess_line(self, org_line: str) -> str:
        """ Strips tabs, indent, collapses spaces and removes comments """
        return re.sub(r'\s+', ' ', org_line.split(self.COMMENT, 1)[0].strip()).strip()

    def _build_instruction(self, line: str, line_i: int) -> Instruction | None:
        """Takes a sanitized text line and tries to decode command either into an instruction or in 
        a compile time directive (i.e. labels)
        """

        words: List[str] = line.split(" ")
        command: str = words[0]     # should always be present because of sanitazing step
        args: List[str] = words[1:] # might be empty list

        # fetches compiler directives first
        directive_function = self.COMPILER_DIRECTIVES.get(command, None)
        if directive_function:
            try:
                directive_function(*args)
            except (TypeError, ValueError) as e:
                raise CompilationError(line_i, f'Failed to execute directive "{command}", raised error: {e}')
            except CompilationError as e:
                raise CompilationError(line_i, *e.args)
            return None

        # fetches command build function
        build_function = self.COMMAND_TABLE.get(command, None)   
        if not build_function: 
            raise CompilationError(line_i, f'Unkwown command: "{command}"')
        
        try:
            return build_function(*args)    # builds the instruction object
        except (TypeError, ValueError) as e:
            raise CompilationError(line_i, f'Failed to build command "{command}", raised error: {e}')
        except CompilationError as e:
                raise CompilationError(line_i, *e.args)
    
    def generate_instructions(self, lines: List[str]) -> List[Instruction] | None:
        """Given a list of raw text lines, generate a list of instructions if possible. Returns None 
        if compilation raises any errors, and logs to logger.
        """
        
        self.instructions = [SetupAndStart()]   # only initial setup instruction
        self.found_labels = {}

        for line_i, raw_line in enumerate(lines):
            line = self._preprocess_line(raw_line)
            if line == "": continue # skips this line if it's empty

            inst: None | Instruction = None

            try:
                inst = self._build_instruction(line, line_i)
            except CompilationError as e:
                logger.critical("(line %s) %s", e.line_i + 1, e.args[0])
                return
            
            # if an instruction was actually built
            if inst:
                self.instructions.append(inst)

        logger.info("Compilation successfull, created %s instructions.", len(self.instructions))
        return self.instructions

    def get_instructions(self) -> List[Instruction]:
        """Gets latest compiled instructions"""
        return self.instructions

    def compile_from_file(self, filepath: str) -> List[Instruction] | None:
        with open("program.txt", "r") as f:
            text_lines = [line for line in f]
        
        return self.generate_instructions(text_lines)



if __name__ == "__main__":
    import logger_config    # to load configs

    with open("program.txt", "r") as f:
        text_lines = [line for line in f]

    comp = Compiler()
    s = comp._preprocess_line(" \t\t    ")

    comp.generate_instructions(text_lines)

    for inst in comp.get_instructions():
        print(inst)
