# Project Brief: Eltako Component for Home Assistant

## Overview
This component enables the integration and control of Eltako devices with Home Assistant. It provides a bridge between Eltako's proprietary wireless protocol and the Home Assistant automation platform, allowing users to control their Eltako devices through a unified interface.

## Inspiration
The project is inspired by:
- Eltako custom component (https://gitlab.com/chrysn/home-assistant-eltako)
- Eltakobus library (https://gitlab.com/chrysn/eltakobus)
- EnOcean component by kipe (https://github.com/kipe/enocean)

## Currently Supported Devices
- F4SR14 (Simple Light)
- FUD14 (Dimmer)
- FSB14 (Cover)

## Key Technical Requirements
1. External transreceiver (USB300 or EnOcean PI) for communication with the Eltako system
2. Teach-in process for device registration as Eltako is not auto-discovery compatible
3. Unique ID management for all elements in the system
4. Virtual switch creation with proper ID management

## Core Goals
1. Provide reliable control of Eltako devices through Home Assistant
2. Support the most common Eltako device types
3. Deliver a user-friendly configuration experience
4. Enable seamless integration with Home Assistant's automation capabilities
5. Allow community contributions for additional device support

## Limitations and Constraints
- Requires external USB hardware
- Manual device registration (teach-in process)
- Base ID and device ID management
- No automatic device discovery

## Future Development
This component is open for expansion to support additional Eltako devices. Community contributions are welcome to extend the functionality and device coverage.