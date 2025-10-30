from typing import List, Tuple, Dict, Callable, Iterable
import re
import logging

from executor import Instruction
import language_specs as langcmd
from instruction_set import (
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
    SetupAndStart,
    SetMouseOffset,
    ClearMouseOffset
)

logger = logging.getLogger("Decompiler")

class Decompiler:

    INSTRUCTION_TABLE: Dict[type, Callable[..., str] | None]

    def __init__(self) -> None:

        def _dcp_move(i: MouseMove) -> str: return f"{langcmd.MOVE} {i.x} {i.y} {str(i.time) if i.time > 0 else ''}"
        def _dcp_moverel(i: MouseMoveRel) -> str: return f"{langcmd.MOVEREL} {i.x} {i.y} {str(i.time) if i.time > 0 else ''}"
        def _dcp_click_left(i: MouseLeftClick) -> str: return f"{langcmd.CLICK} left"
        def _dcp_click_right(i: MouseRightClick) -> str: return f"{langcmd.CLICK} right"
        def _dcp_doubleclick(i: MouseDoubleClick) -> str: return langcmd.DOUBLECLICK
        def _dcp_wait(i: Wait) -> str: return f"{langcmd.WAIT} {i.time_s}"
        def _dcp_waitinput(i: WaitInput) -> str: return langcmd.WAITINPUT
        def _dcp_jump(i: JumpNTimes) -> str: return f"{langcmd.JUMP} {i.jmp_name}"
        def _dcp_print(i: ConsolePrint) -> str: return f"{langcmd.PRINT} {i.msg}"
        def _dcp_centermouse(i: MouseCenter) -> str: return langcmd.CENTERMOUSE
        def _dcp_goback(i: MouseGoBack) -> str: return langcmd.GOBACK
        def _dcp_setoffset(i: SetMouseOffset) -> str: return langcmd.SETOFFSET
        def _dcp_clearoffset(i: ClearMouseOffset) -> str: return langcmd.CLEAROFFSET
        
        
        self.INSTRUCTION_TABLE = {
            MouseMove : _dcp_move,
            MouseMoveRel : _dcp_moverel,
            MouseLeftClick : _dcp_click_left,
            MouseRightClick : _dcp_click_right,
            MouseDoubleClick : _dcp_doubleclick,
            Wait : _dcp_wait,
            WaitInput : _dcp_waitinput,
            JumpNTimes : _dcp_jump,
            ConsolePrint : _dcp_print,
            MouseCenter : _dcp_centermouse,
            MouseGoBack : _dcp_goback,
            SetMouseOffset : _dcp_setoffset,
            ClearMouseOffset : _dcp_clearoffset,
            SetupAndStart : None
        }

    def decompile_to_src(self, instructions: Iterable[Instruction]) -> str:
        """Turns list of instructions into source code
        """
        src: List[str] = [
            "; Decompiled source code",
            "; Generated automatically by Mouse Recorder",
            ""
        ]

        for inst in instructions:
            inst_class: type[Instruction] = type(inst)   # get class

            if not inst_class in self.INSTRUCTION_TABLE:
                logger.critical(f"Unknown/unregistered instruction: {inst_class}")
                return "; ERROR: Unknown/unregistered instruction encountered during decompilation."
            
            dcp_fn = self.INSTRUCTION_TABLE[inst_class]
            if dcp_fn:
                command_str: str | None = dcp_fn(inst)
                if command_str:
                    src.append(command_str)
        
        return "\n".join(src)

