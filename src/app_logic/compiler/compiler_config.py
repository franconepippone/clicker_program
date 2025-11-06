from typing import Dict, Iterable, Callable
from enum import Enum

from .compiler import Compiler, SEP_SPACE, CompilationError, CompCtxDict
from app_logic.instruction_set import ValueRef, VarMathOperations, _is_valid_var_name
from app_logic.instruction_set import (
    Wait,
    MouseLeftClick,
    MouseRightClick,
    MouseMove,
    MouseMoveRel,
    MouseDoubleClick,
    JumpNTimes,
    ConsolePrint,
    MouseCenter,
    Pause,
    MouseGoBack,
    SetupAndStart,
    SetMouseOffset,
    ClearMouseOffset,
    Instruction,
    Call,
    Return,
    SetSafeMode,
    VarMath,
    SetVar,
    PrintVar,
    EndProgram
)

from app_logic.instruction_names import *

class MathOperators(Enum):
    PLUS = "+"
    MINUS = "-"
    TIMES = "*"
    DIV = "/"
    NO_OP = "noop"

# annotated context dict (shared across command builders)
class CompilerContextDict(CompCtxDict):
    # inherits instruction_list
    found_labels: dict[str, int]

# utility functions

def get_label_jmp_idx(compiler_ctx: CompilerContextDict, name: str) -> int:
    found_labels: Dict[str, int] = compiler_ctx.get('found_labels', {})
    jmp_idx: int | None = found_labels.get(name)
    if jmp_idx is None:
        raise CompilationError(-1, f'Undefined label "{name}"')

    return jmp_idx

def get_compiler_cfg(safemode: bool) -> Callable[[Compiler], None]:
    """Returns a parametrized configuration function for the compiler"""

    def configure_compiler(compiler: Compiler) -> None:
        """Configure the compiler by registering command build functions.
        This can either be used by passing a compiler object explicitly,
        or can optionally be passed to the __init__ method of Compiler:
        > cmp = Compiler(configure_compiler)
        """

        @compiler.command('end')
        def end_command(compiler_ctx: CompilerContextDict) -> EndProgram:
            return EndProgram()

        @compiler.command(MOVE)
        def move_command(compiler_ctx: CompilerContextDict, x: ValueRef, y: ValueRef, t: float = 0.0) -> MouseMove:
            # additional logic can be added here using compiler_ctx if needed
            return MouseMove(x, y, t)

        @compiler.command(MOVEREL)
        def move_rel_command(compiler_ctx: CompilerContextDict, x: ValueRef, y: ValueRef, t: float = 0.0) -> MouseMoveRel:
            return MouseMoveRel(x, y, t)

        @compiler.command(CLICK)
        def click_command(compiler_ctx: CompilerContextDict, butt: str = 'left') -> Instruction:
            if butt == 'right':
                return MouseRightClick()
            else:
                return MouseLeftClick()

        @compiler.command(WAIT)
        def wait_command(compiler_ctx: CompilerContextDict, t: ValueRef) -> Wait:
            return Wait(t)

        @compiler.command(DOUBLECLICK)
        def double_click_command(compiler_ctx: CompilerContextDict) -> MouseDoubleClick:
            return MouseDoubleClick()

        @compiler.command(JUMP)
        def jump_command(compiler_ctx: CompilerContextDict, name: str, n: ValueRef = ValueRef('-1')) -> JumpNTimes:
            return JumpNTimes(n, -100, jmp_name=name)   # jmp indx assigned at post-processing

        @compiler.command(PRINT)
        def print_command(compiler_ctx: CompilerContextDict, message: str) -> ConsolePrint:
            return ConsolePrint(message)

        @compiler.command(CENTERMOUSE)
        def center_mouse_command(compiler_ctx: CompilerContextDict) -> MouseCenter:
            return MouseCenter()

        @compiler.command(PAUSE)
        def pause_command(compiler_ctx: CompilerContextDict) -> Pause:
            return Pause()

        @compiler.command(GOBACK)
        def go_back_command(compiler_ctx: CompilerContextDict) -> MouseGoBack: 
            return MouseGoBack()

        @compiler.command(SETOFFSET)
        def set_offset_command(compiler_ctx: CompilerContextDict) -> SetMouseOffset:
            return SetMouseOffset()

        @compiler.command(CLEAROFFSET)
        def clear_offset_command(compiler_ctx: CompilerContextDict) -> ClearMouseOffset:
            return ClearMouseOffset()

        @compiler.command(LABEL)
        def label_command(compiler_ctx: CompilerContextDict, name: str) -> None:
            if 'found_labels' not in compiler_ctx:
                compiler_ctx['found_labels'] = {}
            
            found_labels: Dict[str, int] = compiler_ctx['found_labels']

            if name in found_labels:
                raise CompilationError(-1, f'Label "{name}" already defined')
            
            jmp_idx = len(compiler_ctx["instruction_list"]) # points to the next instruction in the instruction list
            found_labels[name] = jmp_idx    # registers label

        @compiler.command(CALL)
        def call_command(compiler_ctx: CompilerContextDict, name: str) -> Call:
            # -1 is there because call inherits from jumpntimes
            return Call(ValueRef('-1'), -100, jmp_name=name)   # jmp indx assigned at post-processing

        @compiler.command(RETURN)
        def return_command(compiler_ctx: CompilerContextDict) -> Return:
            return Return()
        
        @compiler.command(PRINTVAR)
        def printvar_command(compiler_ctx: CompilerContextDict, name: str) -> PrintVar:
            return PrintVar(name)

        @compiler.command(VAR)
        def var_command(
            compiler_ctx: CompilerContextDict, 
            target_name: str, 
            action: str, 
            left_val: ValueRef, 
            operation: MathOperators = MathOperators.NO_OP,
            right_val: ValueRef  = ValueRef("-1")
        ) -> VarMath | SetVar:
            
            comm = (target_name, action, left_val, operation, right_val)
            if not _is_valid_var_name(target_name):
                raise CompilationError(-1, f"Invalid variable name: '{target_name}'")

            match comm:
                case (str() as target, "=", left, MathOperators.NO_OP, _):
                    return SetVar(target, left)
                
                case (str() as target, "=", left, MathOperators.PLUS, right):
                    
                    return VarMath(target, left, right, VarMathOperations.SUM)
                
                case (str() as target, "=", left, MathOperators.MINUS, right):
                    return VarMath(target, left, right, VarMathOperations.DIFFERENCE)
                
                case (str() as target, "=", left, MathOperators.DIV, right):
                    return VarMath(target, left, right, VarMathOperations.DIVISION)
                
                case (str() as target, "=", left, MathOperators.TIMES, right):
                    return VarMath(target, left, right, VarMathOperations.MULTIPLICATION)
                
                case _:
                    raise CompilationError(-1, "Wrong usage of 'var' command")

            
    
        ### POST PROCESS INSTRUCTIONS

        @compiler.postprocess
        def post_process_jumps(compiler_ctx: CompilerContextDict, instructions: Iterable[Instruction]) -> Iterable[Instruction]:
            """Additional step to link all jumps to labels idxs"""

            for inst in instructions:
                if isinstance(inst, (JumpNTimes, Call)):
                    jmp_idx = get_label_jmp_idx(compiler_ctx, inst.jmp_name)
                    inst.jump_idx = jmp_idx

            return instructions

        init_insts: list[Instruction] = [SetupAndStart(), Wait(ValueRef(.5))]    # waits a bit to let the dialog startup properly
        if safemode:
            init_insts.append(SetSafeMode(True))
        
        # bind initial instructions
        compiler.set_initial_instructions(init_insts)
    
    return configure_compiler