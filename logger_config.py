import logging

logger_comp = logging.getLogger("Compiler")
logger_comp.setLevel(logging.DEBUG)  # use the actual logging level object, not a string

# Add a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # handler level

# Optional: add a formatter
formatter = logging.Formatter('%(name)s [%(levelname)s] %(message)s')
ch.setFormatter(formatter)

logger_comp.addHandler(ch)

logger_comp.info("logger_comp successfully configured")

# =================================
# ------ logger for executor
# ==================================

logger_exec = logging.getLogger("Runtime")
logger_exec.setLevel(logging.DEBUG)  # use the actual logging level object, not a string

# Add a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # handler level

# Optional: add a formatter
formatter = logging.Formatter('%(name)s [%(levelname)s] %(message)s')
ch.setFormatter(formatter)

logger_exec.addHandler(ch)

logger_exec.info("logger_exec successfully configured")