# Eltako Component for Home Assistant (HA)
---------------------------------------

This component enables the posibility to control some of the Eltako Devices
It is inspired by :

- Eltako custom component (https://gitlab.com/chrysn/home-assistant-eltako) and his library Eltakobus (https://gitlab.com/chrysn/eltakobus)
- EnOncean component by kipe (https://github.com/kipe/enocean)

It currently supports the devices I have at home :

- F4SR14 (Simple Light)
- FUD14 (Dimmer)
- FSB14 (Cover)

If you want to participate and add your devices, feel free to make a PR :)

## Before beginnning...

Before beginning There are some things you need to know :

- This component needs an external transreceiver to communicate with your Eltako System like an USB Dongle (USB300) or "EnOcean PI". I only tested with an USB300
- Eltako System is NOT a system where the elements are automatically discovered. You need to "teach-in" your switches to let it know what to do when it receives a radio message
- Each element (F4SR14, FUD14, ..., Switches, Sensors, ...) has a unique ID
- You can not register your physical wall switches directly to HA. Instead you need to create and teach-in "virtual switches" with their own IDs. Thoses virtual switches can't have any device ID because they need to use the "Base ID" of your external transreceiver (Like USB300).
    - First you need to find your transreceiver's base ID. There are several ways to find your base ID :
        - With a software called DolphinView (Windows, need registering to download it)
        - With this component
    - Define an ID for each of your virtual switches with the "basedId + offset" where the offset should be in the range [0, 128]. Please take a look at the Excel file of this repository to compute the ids
- You need to find your actuator's ID
