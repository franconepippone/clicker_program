from __future__ import annotations
from typing import List, TypedDict, Dict, Callable, get_type_hints, Any, Iterable, TypeVar, TypeAlias 
import re
import logging
import inspect

from app_logic.virtual_machine.executor import Instruction
from app_logic.instruction_set import SetupAndStart

logger = logging.getLogger("Compiler")


SEP_SPACE = ' '
SEP_COMMA = ','

class CompilationError(Exception):
    line_i: int

    def __init__(self, line_i: int, *args: object) -> None:
        super().__init__(*args)
        self.line_i = line_i
    
    def get_line(self) -> int:
        return self.line_i


class CompCtxDict(TypedDict):
    instruction_list: List[Instruction]

T = TypeVar("T", bound=CompCtxDict)
PostProcessFunc: TypeAlias  = Callable[[T, Iterable[Instruction]], Iterable[Instruction]]

class Compiler:

    COMMENT = r";"
    command_table: Dict[str, Callable[..., Instruction]] # build methods

    compilation_ctx: CompCtxDict   # context dict shared across all command builders over the whole compilation (e.g. to store variables)
    instructions: List[Instruction]

    post_process_fn: PostProcessFunc | None = None 

    def __init__(self, configure_function: Callable[[Compiler], None] | None = None) -> None:
        self.found_labels = {}
        self.instructions = []
        self.compilation_ctx = {"instruction_list" : self.instructions}
        self.command_table = {}

        if configure_function:
            configure_function(self)

    def _preprocess_line(self, org_line: str) -> str:
        """ Strips tabs, indent, collapses spaces and removes comments """
        return re.sub(r'\s+', ' ', org_line.split(self.COMMENT, 1)[0].strip()).strip()

    def _build_instruction(self, line: str, line_i: int) -> Instruction | None:
        """Takes a sanitized text line and calls respective command builder if command is registered. 
        Can return an instruction object, or just execute interal compile time logic (i.e. label command).
        """

        words: List[str] = line.split(" ", 1)
        command: str = words[0]     # should always be present because of sanitazing step
        args_string: str = words[1] if len(words) > 1 else ""

        # fetches command build function
        build_function = self.command_table.get(command, None)   
        if not build_function: 
            raise CompilationError(line_i, f'Unkwown command: "{command}"')
        
        try:
            return build_function(args_string)    # builds the instruction object
        except CompilationError as e:
            raise CompilationError(line_i, *e.args) 
        except Exception as e:
            raise CompilationError(line_i, f'Failed to build command "{command}", raised error: {e}')
    
    def generate_instructions(self, lines: List[str]) -> List[Instruction] | None:
        """Given a list of raw text lines, generate a list of instructions if possible. Returns None 
        if compilation raises any errors, and logs to logger.
        """
        
        self.instructions = [SetupAndStart()]   # only initial setup instruction
        self.compilation_ctx = {"instruction_list" : self.instructions}

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

    def compile_from_src(self, src_text: str):
        inst_list = self.generate_instructions(src_text.splitlines())
        if inst_list is None:
            return
        
        # if a post_process_step is registered, call it
        if self.post_process_fn:
            logger.info("Performing post-processing pass.")
            try:
                return list(self.post_process_fn(self.compilation_ctx, inst_list.copy()))
            except CompilationError as e:
                logger.critical("(line %s) %s", e.line_i + 1, e.args[0])
                return

        return inst_list

    def compile_from_file(self, filepath: str) -> List[Instruction] | None:
        with open(filepath, "r") as f:
            src_text = f.read()
        
        return self.compile_from_src(src_text)

    def postprocess(self, func: PostProcessFunc) -> PostProcessFunc:
        """Decorator to bind a post_process_function. Can also be called directly"""
        self.post_process_fn = func
        return func

    def command(self, command_name: str, arg_sep: str = SEP_SPACE) -> Callable:
        """Decorator to register a command builder with automatic type casting."""

        def decorator(func: Callable) -> Callable:
            sig = inspect.signature(func)
            hints = get_type_hints(func)
            params = list(sig.parameters.values())[1:]  # skip compiler_ctx
            params_amount = len(params)

            def cast(value: Any, typ: type) -> Any:
                """Try to cast string values to annotated types."""
                if isinstance(value, str) and typ is not str:
                    try:
                        return typ(value)
                    except Exception:
                        # optionally log casting error here
                        raise ValueError(f"Cannot cast value '{value}' to type {typ}")
                    
                return value

            def wrapper(arg_string: str) -> Instruction:
                """Wrapper that splits arg_string and casts args before calling the actual command builder.
                """
                # only perform params_amount - 1 split
                args: list[str] = arg_string.split(arg_sep, params_amount - 1) if arg_string else []

                bound_args: list[Any] = []

                # cast and bind positional args
                for arg, param in zip(args, params):
                    typ = hints.get(param.name, type(arg))
                    bound_args.append(cast(arg, typ))

                # fill in remaining params with defaults
                for param in params[len(args):]:
                    if param.default is not inspect._empty:
                        val = cast(param.default, hints.get(param.name, type(param.default)))
                        bound_args.append(val)

                return func(self.compilation_ctx, *bound_args)

            self.command_table[command_name] = wrapper  # register command
            return wrapper

        return decorator



if __name__ == "__main__":
    import utils.logger_config as logger_config    # to load configs

    with open("program.txt", "r") as f:
        text_lines = [line for line in f]

    comp = Compiler()
    s = comp._preprocess_line(" \t\t    ")

    comp.generate_instructions(text_lines)

    for inst in comp.get_instructions():
        print(inst)
