# PLD_ControlSystem_Python

## Overview

`PLD_ControlSystem_Python` is a modular Python-based control system for a Pulsed Laser Deposition (PLD) experiment. It integrates hardware control, data acquisition, and user-friendly interfaces to manage the various components involved in PLD thin film synthesis.

The system is designed for flexibility, remote operation, and reproducibility in experimental workflows.

---

## Features

- 🔧 Backend control for:
  - Multi-target carousel (Neocera)
  - Laser attenuator
  - Eurotherm 2408 temperature controller
  - Vacuum system (Pfeiffer)
  - Throttle valve (MKS)
  - Mass flow controllers (Alicat)
  - Stage motion (Newport XPS-RL-D)

- 🧠 Modular device drivers with serial communication
- 🖥️ Front-end interfaces built using the `panel` library
- 🐳 Docker support for portable deployment
- 📄 Device-level documentation and troubleshooting guides


## Repository Structure
PLD_ControlSystem_Python/
├── src/pld_controlsystem_python
│ ├── panels/ # Panel-based GUI interfaces
│ └── devices/ # Individual hardware controllers
├── docs/ # Markdown-based documentation
├── notebooks/ # Test notebooks and demos
├── Dockerfile # Container setup
└── README.md
