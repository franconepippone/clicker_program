from executor import Executor
from compiler import Compiler
import logger_config

program = Compiler().compile_from_file("program.txt")
if not program:
    exit()

print("Program has", len(program), "instructions. ")
Executor().load_instructions(program).execute()                   