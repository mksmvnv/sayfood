.PHONY: all lint
.SILENT: all lint

SRC_DIR 	= ./backend
BLACKFLAGS 	= --config pyproject.toml 

all: lint

lint:
	black $(SRC_DIR) $(BLACKFLAGS) 
	flake8 $(SRC_DIR) || true