from typing import Dict, Iterable

from .compiler import Compiler, SEP_SPACE, CompilationError, CompCtxDict
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
    Instruction
)

# instruction names
MOVE = "move"
MOVEREL = "moverel"
CLICK = "click"
WAIT = "wait"
DOUBLECLICK = "doubleclick"
JUMP = "jump"
PRINT = "print"
CENTERMOUSE = "centermouse"
PAUSE = "pause"
GOBACK = "goback"
SETOFFSET = "setoffset"
CLEAROFFSET = "clearoffset"
LABEL = "label"

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


def configure_compiler(compiler: Compiler) -> None:
    """Configure the compiler by registering command build functions."""

    @compiler.command(MOVE)
    def move_command(compiler_ctx: CompilerContextDict, x: int, y: int, t: float = 0.0) -> MouseMove:
        # additional logic can be added here using compiler_ctx if needed
        return MouseMove(x, y, t)

    @compiler.command(MOVEREL)
    def move_rel_command(compiler_ctx: CompilerContextDict, x: int, y: int, t: float = 0.0) -> MouseMoveRel:
        return MouseMoveRel(x, y, t)

    @compiler.command(CLICK)
    def click_command(compiler_ctx: CompilerContextDict, butt: str = 'left') -> Instruction:
        if butt == 'right':
            return MouseRightClick()
        else:
            return MouseLeftClick()

    @compiler.command(WAIT)
    def wait_command(compiler_ctx: CompilerContextDict, t: float) -> Wait:
        return Wait(t)

    @compiler.command(DOUBLECLICK)
    def double_click_command(compiler_ctx: CompilerContextDict) -> MouseDoubleClick:
        return MouseDoubleClick()

    @compiler.command(JUMP)
    def jump_command(compiler_ctx: CompilerContextDict, name: str, n: int = -1) -> JumpNTimes:
        return JumpNTimes(n, -100, jmp_name=name)   # jmp indx assigned at post-processing

    @compiler.command(PRINT, arg_sep=SEP_SPACE)
    def print_command(compiler_ctx: CompilerContextDict, *args: str) -> ConsolePrint:
        message = ' '.join(args)
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


    ### POST PROCESS INSTRUCTIONS

    @compiler.postprocess
    def post_process_jumps(compiler_ctx: CompilerContextDict, instructions: Iterable[Instruction]) -> Iterable[Instruction]:
        """Additional step to link all jumps to labels idxs"""

        for inst in instructions:
            if isinstance(inst, JumpNTimes):
                jmp_idx = get_label_jmp_idx(compiler_ctx, inst.jmp_name)
                inst.jump_idx = jmp_idx

        return instructions
