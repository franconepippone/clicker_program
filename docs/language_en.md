# Clicker Program Language — Command Reference

This document provides a complete reference for all commands available in the integrated scripting language.  
The general command syntax is:  
 **`<command>`**` <param1> <param2> ...`  
where command parameters are separated by spaces.  
Optional parameters are shown in curly braces `{}` in this document only — **do not** include these braces in your code.

Comments begin with `;`. Everything after `;` on the same line is ignored by the compiler.  
Example:  
`wait 1 ; waits for 1 second`

---

## 🖱️ Mouse Movement Commands

- **move** `<x> <y> {<t>}`  
  Moves the mouse pointer to the absolute screen coordinates `(x, y)`.  
  The optional parameter `{t}` specifies the duration of the movement in seconds.  
  Example: `move 100 50 0.5`

- **moverel** `<dx> <dy> {<t>}`  
  Moves the mouse pointer relative to its current position by `(dx, dy)`.  
  The optional parameter `{t}` specifies the duration of the movement in seconds.  
  Example: `moverel 50 0 0.2`

---

## 🖱️ Click Commands

- **click** `{button}`  
  Performs a mouse click at the current cursor position.  
  `{button}` may be `left` or `right`.  
  If omitted, the left button is used by default.  
  Examples: `click`, `click right`, `click left`

- **doubleclick**  
  Performs a double-click at the current cursor position.  
  Example: `doubleclick`

---

## ⏱️ Timing Commands

- **wait** `<t>`  
  Pauses execution for `t` seconds.  
  Example: `wait 4.5 ; waits 4.5 seconds`

- **pause**  
  Suspends program execution until manually resumed.

---

## 🔁 Looping and Flow Control

- **label** `<name>`  
  Defines a label that can be referenced by jump or call commands.  
  Example: `label start_loop`

- **jump** `<label> {<n>}`  
  Jumps to the specified label.  
  If `{n}` is provided, the jump will be executed up to `{n}` times.  
  Once the jump limit is reached, the jump will fail, but if the same instruction is hit again, it will behave exactly like if it was hit for the first time (can be used to make nested loops).  
  Examples: `jump start_loop`, `jump start_loop 20`

- **call** `<label>`  
  Jumps unconditionally to the specified label, saving the current execution point for return.  
  Used together with **return**, this enables function-like behavior.  
  Example: `call click_function`

- **return**  
  Returns program execution to the point immediately after the corresponding **call** command.  
  **Note:** each **call** must have a matching **return** for correct execution.  
  See *example_programs/functions.txt* for code examples.

---

## 🧮 Variables

All variable operations are handled through the **var** command:

- **var** `<name> = <value>`  
  Assigns `<value>` to the variable `<name>`. `<value>` can be a literal (e.g., `10`, `2.5`) or another variable name (e.g., `x`, `my_var`).  
  Examples: `var x = 1`, `var x = y`

- **var** `<name> = <value> <OPERATION> <value>`  
  Performs a mathematical operation between two values (either literals or variables).  
  Supported operations: `+`, `-`, `*`, `/`.  
  Examples: `var x = x + 1`, `var x = y * z`

\
Most commands that accept numeric parameters (such as `move`, `moverel`, `jump`, `wait`) also accept variables as arguments.  
Examples:
- `move x y`  
- `wait PAUSE_SECS`  
- `moverel 50 y_increment`  

Here, **x**, **y**, **PAUSE_SECS**, and **y_increment** are variables defined earlier in the script.  

\
There are also special global read-only variables (prefixed with `$`) that can only be assigned to other variables or referenced in commands:
- `$MOUSE_X` — current mouse X coordinate  
- `$MOUSE_Y` — current mouse Y coordinate  
- `$OFFSET_X` — X offset applied via **setoffset**  
- `$OFFSET_Y` — Y offset applied via **setoffset**


See *example_programs/variables.txt* for practical usage examples.

---

## 💬 Console Output

- **print** `<message...>`  
  Prints a message to the console.  
  Example: `print Hello world!`

- **printvar** `<name>`  
  Displays the value of the specified variable in the console.  
  Example: `printvar x` → **Terminal: x = 3.0**

---

## 🧰 Utility Commands

- **centermouse**  
  Moves the cursor to the center of the screen.  
  Example: `centermouse`

- **goback**  
  Moves the cursor back to the previous position,  
  undoing the last movement executed with a `move` command. It can be used repeatedly to retrace the movement history.  
  Example: `goback`

