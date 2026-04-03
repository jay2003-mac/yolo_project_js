.PHONY: help generate validate train train-all train-m3 train-m4 train-m5 train-m6 list status camera

PYTHON := python
MAIN := main.py

help:
	@echo "X-Ray Screw Detection - Available Commands"
	@echo ""
	@echo "Data Generation:"
	@echo "  make generate       - Generate synthetic dataset"
	@echo ""
	@echo "Validation:"
	@echo "  make validate       - Validate M3 dataset"
	@echo "  make validate-m4    - Validate M4 dataset"
	@echo ""
	@echo "Training:"
	@echo "  make train          - Train M3 model (default: 20 epochs)"
	@echo "  make train-m4       - Train M4 model"
	@echo "  make train-m5       - Train M5 model"
	@echo "  make train-m6       - Train M6 model"
	@echo "  make train-all      - Train all screw types"
	@echo ""
	@echo "Management:"
	@echo "  make list           - List trained models"
	@echo "  make status         - Show project status"
	@echo "  make camera         - Show camera config"
	@echo ""

generate:
	$(PYTHON) $(MAIN) generate

validate:
	$(PYTHON) $(MAIN) validate --type m3

validate-m4:
	$(PYTHON) $(MAIN) validate --type m4

validate-m5:
	$(PYTHON) $(MAIN) validate --type m5

validate-m6:
	$(PYTHON) $(MAIN) validate --type m6

train: train-m3

train-m3:
	$(PYTHON) $(MAIN) train --type m3 --epochs 20 --batch 32

train-m4:
	$(PYTHON) $(MAIN) train --type m4 --epochs 20 --batch 32

train-m5:
	$(PYTHON) $(MAIN) train --type m5 --epochs 20 --batch 32

train-m6:
	$(PYTHON) $(MAIN) train --type m6 --epochs 20 --batch 32

train-all:
	$(PYTHON) $(MAIN) train-all --epochs 20 --batch 32

list:
	$(PYTHON) $(MAIN) list

status:
	$(PYTHON) $(MAIN) status

camera:
	$(PYTHON) $(MAIN) camera
