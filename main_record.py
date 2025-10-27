from recorder import Recorder

program = Recorder().start()
if not program:
    print("empty program")
    exit()

for i in program:
    print(i) 