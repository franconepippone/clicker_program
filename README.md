# Clicker Program

*An Italian version of this document is avaliable [here](docs/README_it.md).*

A software (auto-clicker / click automation tool) for automating mouse cursor operations, entirely controlled using a graphical user interface.  


---

## Overview
The Clicker Program includes a lightweight custom scripting language designed specifically for mouse automation. The language allows users to write simple, readable scripts that can control cursor movements, perform mouse clicks, define and manipulate variables, and execute conditional or loop-like logic using assembly-like commands such as `jump`, `call`, and `return`.

From the GUI, two main operations are available:

- **Run** — Executes the current script.  
  - Includes an optional **Safe Mode** that disables actual mouse clicks, allowing only cursor movement simulation.
- **Record** — Captures a sequence of mouse actions and inserts the corresponding script instructions directly into the editor.  
  - Pressing the **middle mouse button** (scroll wheel) records only a movement command, without clicks.


For a detailed reference of all scripting commands, see the [Command Reference](docs/language_en.md).

---

## Installation

**Requirements:**  
 - Python **3.8+**  
 - **pip** (Python package manager)

### 1. Clone the Repository

Using **git**:
```bash
git clone https://github.com/franconepippone/clicker_program.git
cd clicker_program
```
Or download the ZIP archive from GitHub and extract it manually.

---

### 2. Install Dependencies

This project was built using the **uv** Python package manager.

#### Option A: Using `uv` (recommended)
Install `uv` globally:
```bash
pip install uv
```
Then, in the project directory:
```bash
uv sync
```


#### Option B: Using `pip`
If you prefer to install dependencies manually:
```bash
pip install -r requirements.txt
```
>Note: Using `pip` will not automatically create or manage a virtual environment.

---

### 3. Run the Application

In the project directory:
```bash
uv run src/main.py
```

If on Windows, double-click the provided `run_win.vbs` script to launch the application.  
(You can also create a shortcut for convenience.)

---

## Additional Information

- This software is intended for **personal use only**.  
  Use it at your own risk for any serious or production scenarios.
- The GUI part of the code was heavily assisted by AI generation and might not strictly follow standard Python or coding conventions and best practices.

