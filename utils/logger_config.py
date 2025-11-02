import logging


# Add a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # handler level

# Optional: add a formatter
formatter = logging.Formatter('%(name)s [%(levelname)s] %(message)s')
ch.setFormatter(formatter)


logger_comp = logging.getLogger("Compiler")
logger_comp.setLevel(logging.DEBUG)  # use the actual logging level object, not a string

logger_comp.addHandler(ch)

logger_comp.info("logger_comp successfully configured")

# =================================
# ------ logger for executor
# ==================================

logger_exec = logging.getLogger("Runtime")
logger_exec.setLevel(logging.DEBUG)  # use the actual logging level object, not a string

logger_exec.addHandler(ch)

# logger_exec.info("logger_exec successfully configured")

# =================================
# ------ logger for executor
# ==================================

logger_decompiler = logging.getLogger("Decompiler")
logger_decompiler.setLevel(logging.DEBUG)  # use the actual logging level object, not a string


logger_decompiler.addHandler(ch)

# logger_decompiler.info("logger_decompiler successfully configured")

# =================================
# ------ logger for executor
# ==================================

logger_editor = logging.getLogger("Editor")
logger_editor.setLevel(logging.DEBUG)  # use the actual logging level object, not a string

logger_editor.addHandler(ch)

# logger_editor.info("logger_editor successfully configured")

# =================================
# ------ logger for Recorder
# ==================================

logger_recorder = logging.getLogger("Recorder")
logger_recorder.setLevel(logging.DEBUG)  # use the actual logging level object, not a string

logger_recorder.addHandler(ch)