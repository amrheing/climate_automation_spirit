<a href="https://github.com/amrheing/climate_automation_spirit/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/amrheing/climate_automation_spirit"></a>
<a href="https://github.com/amrheing/climate_automation_spirit/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/amrheing/climate_automation_spirit"></a>
<a href="https://github.com/amrheing/climate_automation_spirit/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/amrheing/climate_automation_spirit"></a>

# climate_automation_spirit.py 

This python_script is for use in HomeAssistant

## Features
- multiple Window sensors
- multiple On / Off Switches
- presense mode
- define a globale eco and decide to use that
- all service data is given as helper objects in HA
  - input_number
  - input_boolean
  - input_text
- validation of service data
- much debug code
- switch debug on / off
- master / slave configuration for using multiple thermostats per room
- decide if window open results in eco or off mode

The overall goal of the script is no data in the script. 
All service data has to be set bei number, text or boolean helpers in HA.

The script is tested with the "Eurotronics Spirit zwave" Thermostats.

1) If one On/Off switch is off or one window is open: `hvac_mode`will be `off`
2) If not in a time schedule or precense is away: `preset_mode` will be `Heat Eco`
3) If in time_schedule: `preset_mode` will be `heat`

When setting the `hvac_mode`also the temperature is set

The script checks always the actual settings to decrease network actions

With debug mode you get a lot of information about the checks 

## Next goals

- implement an outside temperature sensor to manage the global on / off state
- holiday mode based on calender
- thermostast presets and integration of the danfoss zwave thermostat

## Installation

- put this file in your "python_scripts" folder in HomeAssistant /config
- reload the scripts
- create the automation rule

## Configuration

| Name                    | Required  | Description                                                      |
| ----------------------- | --------- | ---------------------------------------------------------------- |
| entity_ids              | True      | list of entity ids to control    (only one entry)                |
| debug                   | False     | Single Switch on / off the debug mode                            |
| switches_on_off         | False     | list switches for on  / off                                      |
| sensors_presence        | False     | list of sensors to test the precense                             |
| eco_global_temperature  | False     | eco Temperature in the house                                     |
| set_default_eco         | False     | use the global or local eco temperature - default: OFF           |
| eco_temperature         | True      | stores the actual settings                                       |
| comfort_temperature     | True      | stores the actual settings                                       |
| windows                 | False     | Window open sensors - Default: Closed                            |
| use_scheduler           | False     | devide to use the time schedules - default: on
| schedule_saturday       | False     | Time Pattern for scheduling Saturdays                            |
| schedule_sunday         | False     | Time Pattern for scheduling Sundays                              |
| schedule_weekdays       | False     | Time Pattern for scheduling Weekdays                             |
| window_off_mode         | False.    | if On the thermostat is off when window is open                  |

If you do not give a time schedule it is always in time.

## Helper Configuration

The script is able to get a very fine tuned time scheduling input.
To check the input please configure the input_text helpers with this regex validation string

([0-9]{1,2}(:[0-9]{2})?-[0-9]{1,2}(:[0-9]{2})?[,]?)*

That make the following inputs possible:

8-10,10:30-17,18:25-23:59

Every scheduling is a block: "from"-"to".
Many blocks can be set by seperated by a colon ","


## HomeAssistant Automation as Master or Single configuration

```yaml
- id: 'schlafzimmer_thermostat_rechts'
  alias: Schlafzimmer Thermostat rechts Automation
  description: ''
  trigger:
  # list all parameters to get quick reactions
  - entity_id: input_boolean.heizung_global_on_off
    platform: state
  - entity_id: climate.thermostat_schlafzimmer_rechts
    platform: state
  - entity_id: input_boolean.heizung_global_home_mode
    platform: state
  - entity_id: input_boolean.heizung_sz_scheduler
    platform: state
  - entity_id: input_text.schlafzimmer_sunday
    platform: state
  - entity_id: input_text.schlafzimmer_saturday
    platform: state
  - entity_id: input_text.schlafzimmer_workdays
    platform: state
  - entity_id: input_boolean.heizung_sz_set_default_eco_temperature
    platform: state
  - entity_id: input_number.heizung_sz_eco_temperature
    platform: state
  - entity_id: input_number.heizung_sz_komfort_temperature
    platform: state
  - entity_id: input_boolean.heizung_sz_simulate_window
    platform: state
  - entity_id: binary_sensor.sz_window_left
    platform: state
  - entity_id: binary_sensor.sz_door
    platform: state
  - entity_id: binary_sensor.sz_window_right
    platform: state
  # timepattern is not needed - optional - is good to use when zwave is not so perfect :-)
  - minutes: /5
    platform: time_pattern
  condition: []
  action:
  - data_template:
      # decide what should happen when window is open
      # Switch Off: Preset Eco
      # Switch On: HVAC Off
      # Default: off <-- Eco Mode is used when windows are open
      window_off_mode: input_boolean.heizung_sz_window_off_mode             # Optional
      # temperatures
      # a eco temperature what can be used for all thermostat
      set_default_eco: input_boolean.heizung_sz_set_default_eco_temperature # Optional
      # Default: 16
      eco_global_temperature: input_number.heizung_global_eco_temperature   # Optional
      # switch on/off the scheduler
      # there are stored the last temperatures
      # No Default - value set by climate object
      eco_temperature: input_number.heizung_sz_eco_temperature              # mandatory
      comfort_temperature: input_number.heizung_sz_komfort_temperature      # mandatory
      # debug
      # Default: off <-- No debug Log entrys
      debug: input_boolean.heizung_global_debug_mode                        # Optional
      # entites to control
      # entites :: this si a list, but there is only the first one used. 
      # maybe for future purposes
      entity_ids:
      - climate.thermostat_schlafzimmer_rechts                              # mandatory
      # without scheduler Preset None == normal heating
      # Default: on
      use_scheduler: input_boolean.heizung_sz_scheduler                     # Optional
      # schedules
      # input_text helpers
      # Regex to control the data: ([0-9]{1,2}(:[0-9]{2})?-[0-9]{1,2}(:[0-9]{2})?[,]?)*
      schedule_saturdays: input_text.schlafzimmer_saturday                  # mandatory
      schedule_sundays: input_text.schlafzimmer_sunday                      # mandatory
      schedule_weekdays: input_text.schlafzimmer_workdays                   # mandatory
      # presence
      # there can be as much switches you want
      # Default: on <-- we are at home
      sensors_presence:
      - input_boolean.heizung_global_home_mode                              # Optional
      # on/off switches
      # there can be as much switches you want
      # Default: on <-- Preset None == heating
      switches_on_off:
      - input_boolean.heizung_global_on_off                                 # Optional
      # windows
      # Default: off <-- Windows Closed
      windows:
      - binary_sensor.sz_window_left                                        # Optional
      - binary_sensor.sz_door                                                  # Optional
      - binary_sensor.sz_window_right                                       # Optional
      # simulate switch for testing purposes
      - input_boolean.heizung_sz_simulate_window                            # Optional
      # Master: True // SLAVE: <masters entity_id> 
      master: True                                                          # Optional
    service: python_script.climate_automation_spirit                        # mandatory
```


## HomeAssistant Automation as Slave configuration

```yaml
- id: 'schlafzimmer_thermostat_links'
  alias: Schlafzimmer Thermostat Links Automation
  description: ''
  trigger:
  # slave is normaly only triggered by the master thermostat
  - entity_id: climate.thermostat_schlafzimmer_rechts
    platform: state
  # timepattern is not needed - is good to use as backup trigger when zwave is not so perfect :-)
  - platform: time_pattern
    minutes: /5
  condition: []
  action:
  - data_template:
      # debug
      debug: input_boolean.heizung_global_debug_mode
      # entites :: this si a list, but there is only the first one used. 
      # maybe for future purposes
      entity_ids:
      - climate.thermostat_schlafzimmer_links
      # mandatory for a slave configuration
      master: climate.thermostat_schlafzimmer_rechts
    service: python_script.climate_automation_spirit
...
