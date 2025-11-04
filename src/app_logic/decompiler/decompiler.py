from typing import List, Tuple, Dict, Callable, Iterable
import logging
from datetime import datetime

from app_logic.virtual_machine.executor import Instruction
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
    ClearMouseOffset
)

from app_logic.instruction_names import *


logger = logging.getLogger("Decompiler")


class Decompiler:
    """Decompiles an instruction list into source code in the clicker scripting language.
    Not much work has been done to make this class flexible like the Compiler class, as it's usage is very limited up
    to now
    """

    INSTRUCTION_TABLE: Dict[type, Callable[..., str] | None]

    def __init__(self) -> None:

        def _dcp_move(i: MouseMove) -> str: return f"{MOVE} {i.x()} {i.y()} {str(i.time) if i.time > 0 else ''}"
        def _dcp_moverel(i: MouseMoveRel) -> str: return f"{MOVEREL} {i.x()} {i.y()} {str(i.time) if i.time > 0 else ''}"
        def _dcp_click_left(i: MouseLeftClick) -> str: return f"{CLICK} left"
        def _dcp_click_right(i: MouseRightClick) -> str: return f"{CLICK} right"
        def _dcp_doubleclick(i: MouseDoubleClick) -> str: return DOUBLECLICK
        def _dcp_wait(i: Wait) -> str: return f"{WAIT} {i.time_s()}"
        def _dcp_waitinput(i: Pause) -> str: return PAUSE
        def _dcp_jump(i: JumpNTimes) -> str: return f"{JUMP} {i.jmp_name}"
        def _dcp_print(i: ConsolePrint) -> str: return f"{PRINT} {i.msg}"
        def _dcp_centermouse(i: MouseCenter) -> str: return CENTERMOUSE
        def _dcp_goback(i: MouseGoBack) -> str: return GOBACK
        def _dcp_setoffset(i: SetMouseOffset) -> str: return SETOFFSET
        def _dcp_clearoffset(i: ClearMouseOffset) -> str: return CLEAROFFSET
        
        
        self.INSTRUCTION_TABLE = {
            MouseMove : _dcp_move,
            MouseMoveRel : _dcp_moverel,
            MouseLeftClick : _dcp_click_left,
            MouseRightClick : _dcp_click_right,
            MouseDoubleClick : _dcp_doubleclick,
            Wait : _dcp_wait,
            Pause : _dcp_waitinput,
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
            f"; Generated automatically by Mouse Recorder | {datetime.now().strftime("%m-%d %H:%M:%S")}",
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

