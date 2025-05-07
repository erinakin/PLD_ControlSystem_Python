# Neocera PLD Multi-Target Carousel Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Hardware Components](#hardware-components)
3. [Hardware Code](#hardware-code)
4. [Backend Software](#backend-software)
5. [Front-End Software](#front-end-software)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Troubleshooting](#troubleshooting)
9. [Safety Considerations](#safety-considerations)

---

## Introduction

This documentation provides an overview of the hardware and software components of an Open Source controller for the Neocera PLD Multi-Target Carousel system. The system consists of two stepper motors controlling rotation and rastering, an Arduino UNO microcontroller, and a Python-based user interface using the `Panel` library.

## Hardware Components

Below is a list of the hardware components used in this system:

| Component                             | Quantity | Function                                             | Connection Details                             |
| ------------------------------------- | -------- | ---------------------------------------------------- | ---------------------------------------------- |
| **Arduino UNO**                       | 1x       | Main microcontroller for motor control               | Connected to stepper motor drivers and sensors |
| **A4988 Stepper Motor Drivers**       | 2x       | Drives the stepper motors                            | Receives signals from Arduino microcontroller  |
| **Stepper Motor 1 (Rotation)**        | 1x       | Controls the rotation of the target carousel         | Connected to motor driver                      |
| **Stepper Motor 2 (Rastering)**       | 1x       | Moves the targets and carousel in a rastering motion | Connected to motor driver                      |
| **5mm DIP LEDs**                      | 5x       | Status indicators                                    | Connected to Arduino pins                      |
| **Pin Header Set**                    | 1x       | Connects components to the breadboard                | Various connections                            |
| **Molex 6 Circuit Wire Connector**    | 2x       | Connects stepper motors to the drivers               | Wired between motors and drivers               |
| **100uF Electrolytic Capacitor**      | 1x       | Stabilizes power to motor drivers                    | Connected to stepper driver power rails        |
| **10k Through-Hole Resistor**         | 1x       | Used for pull-up/pull-down logic                     | Connected to control pins                      |
| **Assorted Single-Core Jumper Wires** | 1x set   | Facilitates wiring between components                | Various connections                            |
| **Standoffs (Optional)**              | 1x set   | Provides physical support for the board              | Used for mounting                              |
| **Custom Back Plate (Optional)**      | 1x       | Secures components                                   | Optional for assembly                          |

### A4988 Stepper Motor Driver Connections

#### **Stepper Driver 1 (Rotate driver)**
- **STEP input** → Digital pin 2
- **DIRECTION input** → Digital pin 3
- **ENABLE input** → Digital pin 4
- **VMOT (24V power supply)** → 24V Power Supply
- **GND** → Common Ground
- **MS1** 
- **MS2**
- **MS3**
#### **Stepper Driver 2 (Raster Driver)**
- **STEP input** → Digital pin 5
- **DIRECTION input** → Digital pin 6
- **ENABLE input** → Digital pin 7
- **VMOT (24V power supply)** → 24V Power Supply
- **GND** → Common Ground
- **MS1**
- **MS2**
- **MS3**

**[Placeholder for hardware diagram image]**

## Hardware Code

The **PLDStepper** library manages the stepper motor control for the Neocera PLD Multi-Target Carousel. It defines motor control functions and parameters.

### **File: pld_stepper.h**

**Summary:**
This header file defines the **PLDStepper** class, which controls the Neocera Multi-Target Carousel stepper motors. It includes variables for motor direction, speed, and state tracking, as well as functions for various motor operations like homing, rastering, and rotation.

### **File: PLDStepper.cpp**

**Summary:**
This implementation file contains the definitions of the **PLDStepper** class functions. It provides the logic to initialize and control the stepper motors, including rotation, homing, rastering, and continuous motion. It also handles motor speed adjustments and stopping conditions.

### **File: carouselCtrl.ino**

**Summary:**
This is the main Arduino control script for the Neocera PLD Multi-Target Carousel. It initializes two **PLDStepper** motor objects—one for rotation and one for rastering—and manages their movements based on serial commands. The script handles:

- Receiving commands via serial communication.
- Setting motor speeds and angles for both rotation and rastering.
- Executing homing, rotation, rastering, and continuous rotation modes.
- Monitoring motor states and stopping conditions.
- Updating status bits to signal ongoing operations.

## Backend Software

The Python backend interacts with the hardware through serial commands.

## Front-End Software

The front-end interface is built using the `Panel` Python library for user interaction.

## Installation & Setup

1. Install Python dependencies:
   ```sh
   pip install panel pyserial
   ```
2. Upload the Arduino code to the Arduino UNO.
3. Connect the hardware components as per the wiring diagram.

## Usage Guide

1. Open the Python script and launch the Panel UI.
2. Use the UI controls to move the carousel.
3. Monitor system responses on the interface.

## Troubleshooting

### Common Issues & Solutions

1. **Stepper motor not moving**
   - Check the wiring connections between the motor and the driver.
   - Ensure the motor driver is receiving power.
   - Verify the Arduino is sending correct signals.

2. **Erratic motor behavior or noise**
   - Check if the current settings on the A4988 driver are correctly adjusted.
   - Make sure the capacitor is properly connected to prevent voltage fluctuations.
   - Ensure the stepper motor coils are wired correctly.

## Safety Considerations

1. **Electrical Safety**
   - Ensure that all connections are properly insulated to prevent short circuits.
   - Avoid touching the circuit while power is applied.
   - Use appropriate rated power supplies and fuses where necessary.

2. **Mechanical Safety**
   - The carousel moves with force—keep hands clear of moving parts during operation.
   - Secure all components properly to prevent unexpected movement.

3. **Thermal Safety**
   - Stepper motor drivers and motors can generate heat—ensure adequate ventilation.
   - If components become excessively hot, power down and troubleshoot before resuming operation.

4. **Emergency Stop Protocol**
   - Always have an emergency stop mechanism in place.
   - If erratic behavior occurs, immediately disconnect power and inspect the system.

**[Placeholder for troubleshooting images]**

