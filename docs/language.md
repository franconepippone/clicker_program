# Clicker Program Language Command Reference (Compact)

This is a compact reference for all commands in the Clicker Program Language.  
Arguments are space-separated. **Optional arguments are shown in curly braces `{}` in this document only**; the curly braces are not used in the language itself.

Use `;` to comment a line.  
Ex. usage: `wait 1 ; waits for 1 second`



---

### Move Commands

- **move** `<x> <y> {<t>}`  
  Moves mouse to absolute coordinates `(x, y)`. Optional `{t}` = duration in seconds.  
  Ex. usage: `move 100 50 0.5`

- **moverel** `<dx> <dy> {<t>}`  
  Moves mouse relative to current position `(dx, dy)`. Optional `{t}` = duration.  
  Ex. usage: `moverel 50 0 0.2`

---

### Click Commands

- **click** `{button}`  
  Mouse click at current position. `{button}` = `left` or `right`. If no button argument is given, mouse will left click.  
  Ex. usage: `click`, `click right`,  `click left`

- **doubleclick**  
  Double click at current position.  
  Ex. usage: `doubleclick`

---

### Wait Commands

- **wait** `<t>`  
  Waits `t` seconds.  
  Ex. usage: `wait 4.5    ; waits for 4.5 seconds`

- **waitinput**  
  Waits for user input before continuing (spacebar press by default).  
  Ex. usage: `waitinput`

---

### Loop & Jump Commands

- **label** `<name>`  
  Defines a label to jump to.  
  Ex. usage: `label LOOPx`

- **jump** `<label> {<n>}`  
  Jumps to the specified label. If `{n}` is given, the jump will be executed up to `{n}` times; once that number is reached, the next call will fail and program will continue to the next instruction. After that, the jump can be used again, allowing loops and nested loops to repeat multiple times.  
  Ex. usage: `jump LOOPy`, `jump LOOPx 100`



---

### Console / Output

- **print** `<message...>`  
  Prints message to console.  
  Ex. usage: `print Hello world!`

---

### Mouse Utilities

- **centermouse**  
  Moves mouse to screen center.  
  Ex. usage: `centermouse`

- **goback**  
  Goes back one step in the mouse position history, effectively canceling
  the latest update created with a move command.  
  Ex. usage: `goback`


