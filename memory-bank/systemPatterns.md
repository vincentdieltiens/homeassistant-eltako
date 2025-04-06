# System Patterns: Eltako Component for Home Assistant

## System Architecture
The Eltako component integrates with Home Assistant following the standard integration model:
1. Discovery and configuration via config_flow
2. Communication with hardware via the Dongle class
3. Device representation through entities (lights, covers, binary_sensors)
4. Event management via the Home Assistant event bus

## Key Design Patterns
1. **Entity-Platform Pattern**: Each device type (light, cover) is implemented as a separate entity
2. **Observer Pattern**: Entities subscribe to dongle events to receive state updates
3. **Command Pattern**: Translation of Home Assistant actions into commands for Eltako devices
4. **Repository Pattern**: Centralized management of entities and their states

## Component Structure
```
homeassistant_eltako/
├── __init__.py            # Integration entry point
├── config_flow.py         # Configuration flow
├── const.py               # Constants
├── dongle.py              # Transceiver communication
├── binary_sensor.py       # Binary sensor entities
├── light.py               # Light entities
├── cover.py               # Cover entities
└── utils.py               # Utility functions
```

## Data Flow
1. **Input**: Radio messages are received by the USB dongle
2. **Processing**: The dongle decodes messages and sends them to the event bus
3. **Distribution**: Relevant entities receive events and update their state
4. **Output**: User commands are translated into radio messages and sent by the dongle

## Major Technical Decisions
1. Use of an asynchronous communication model for stability
2. Clear separation between hardware communication and business logic
3. Flexibility to add new device types
4. Explicit management of IDs and teach-in processes 