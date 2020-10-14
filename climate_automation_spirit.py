# Definitions

#get debug
sensor = data.get("debug", None)
ENTITY_ID = ""
if sensor != None:
	sensor_state = hass.states.get(sensor).state
	if sensor_state == "on":
		DEBUG = True
	else:
		DEBUG = False
else:
	DEBUG = False

def ld(msg, *args):
	if DEBUG == True:
		logger.info("%s :: %s", ENTITY_ID, msg % args)

logger.info("Start climate_automation_spirit - DEBUG: %s", DEBUG)

# Defaults
DEFAULT_ECO = 16												# will be set if no input is available
DEFAULT_COMFORT = 21										# will be set if no input is available
DEFAULT_PRESENSE = True									# in default we are at home
DEFAULT_SWITCH_ON_OFF = True						# in default the climate should be on
DEFAULT_WINDOW_OPEN = False							# in default all windows are closed
DEFAULT_SET_DEFAULT_ECO = False					# the global eco temperature will be ignored
DEFAULT_USE_WINDOW_AUTOMATION = False		# no recognition of open windows
DEFAULT_USE_SCHEDULER = False						# Time scheduleing if climate control is off
DEFAULT_IN_TIME = False 								# If schedule is used, eco mode will be default
DEFAULT_WINODW_OFF_MODE = False 				# If winodw is open, eco mode will be set
DEFAULT_MASTER = True										# used to backup the temperatures - only one in a room should do this

# parameters for automation rule
PARAM_ENTITY_IDS = "entity_ids"
PARAM_ENTITY_ID = "entity_id"
PARAM_SWITCHES_ON_OFF = "switches_on_off"
PARAM_WINDOW_SENSORS = "windows"
PARAM_PRESENCE_SENSORS = "sensors_presence"
PARAM_GLOBAL_ECO = "eco_global_temperature"
PARAM_SCHEDULE_WEEKDAYS = "schedule_weekdays"
PARAM_SCHEDULE_SATURDAYS = "schedule_saturdays"
PARAM_SCHEDULE_SUNDAYS = "schedule_sundays"
PARAM_SET_DEFAULT_ECO = "set_default_eco"
PARAM_USE_SCHEDULER = "use_scheduler"
PARAM_USE_WiNDOW_AUTOMATION = "use_window_automation"
PARAM_ECO_TEMPERATURE = "eco_temperature"
PARAM_COMFORT_TEMPERATURE = "comfort_temperature"
PARAM_WINDOW_OFF_MODE = "window_off_mode"
PARAM_MASTER = "master"

# load initial data

try:
	ENTITY_IDS = data.get(PARAM_ENTITY_IDS, [])
	logger.info("+ loaded entitys: %s", ENTITY_IDS)
except:
	logger.info("ERROR loading entitys")
	
ENTITY_ID = ENTITY_IDS[0]
logger.info("%s :: Entity to control", ENTITY_ID)

MASTER = data.get(PARAM_MASTER, True)
logger.info("--> MASTER: %s", MASTER)
	

# climate entitiy attributes
# get attributes

# attributes for eurotronics zwave spirit thermostat
CLIMATE_HVAC_MODES = "hvac_modes"
CLIMATE_HVAC_MODE = "hvac_mode"
CLIMATE_MIN_TEMP = "min_temp"
CLIMATE_MAX_TEMP = "max_temp"
CLIMATE_PRESET_MODES = "preset_modes"
CLIMATE_CURRENT_TEMPERATURE = "current_temperature"
CLIMATE_TEMPERATURE = "temperature"
CLIMATE_PRESET_MODE = "preset_mode"
CLIMATE_NODE_ID = "node_id"
CLIMATE_VALUE_INDEX = "value_index"
CLIMATE_VALUE_INSTANCE = "value_instance"
CLIMATE_VALUE_ID = "value_id"
CLIMATE_FRIENDLY_NAME = "friendly_name"
CLIMATE_TARGET_HIGH = "target_temp_high"
CLIMATE_TARGET_LOW = "target_temp_low"

# values for the eurotronics zwave spirit thermostat 
HVAC_MODE_OFF = "off"
HVAC_MODE_HEAT = "heat"

PRESET_MODE_ECO = "Heat Eco"
PRESET_MODE_BOOST = "boost"
PRESET_MODE_MANUFACTURE = "Manufacturer Specific"
PRESET_MODE_NONE = "none"

# climate service commands
DOMAIN_CLIMATE = "climate"
DOMAIN_INPUT_NUMBER = "input_number"

# thermostat presets
SERVICE_TURN_OFF = "turn_off"
SERVICE_TURN_ON = "turn_on"
SERVICE_SET_HVAC_MODE = "set_hvac_mode"
SERVICE_SET_PRESET_MODE = "set_preset_mode"
SERVICE_SET_TEMPERATURE = "set_temperature"
SERVICE_SET_VALUE = "set_value"
SERVICE_DATA = []

SENSOR_ON = "on"
SENSOR_OFF = "off"

# Set decider to default
ENTITY_IDS = []
WINDOW_OPEN = DEFAULT_WINDOW_OPEN
PRESENSE = DEFAULT_PRESENSE
SWITCH_ON_OFF = DEFAULT_SWITCH_ON_OFF
IN_TIME = DEFAULT_IN_TIME
IN_TIME = DEFAULT_IN_TIME

##########################################################################################
#  Functions which are independent the climate ENTITY_ID                                 #
##########################################################################################

##########################################################################################
# - my functions work with global variables which where previously set                   #
#   i know that is not the best way to create functions :-)                              #
# - variable data is given as parameter                                                  #
##########################################################################################

# retrieve the parameters value
def get_data_from_param(var, attr):
	ld("### get_data_from_param - var: %s attr: %s", var, attr)
	try:
		result = data.get(attr, None)
		ld("- data got for %s: %s", attr, result)
		if result == None:
			return var
		return result
	except:
		return var
		
# retrieve the value of a value given by a parameter	
def get_data_from_entity(var, attr):
	ld("### get-data_from_entity: var: %s attr: %s", var, attr)
	try:
		sensor = data.get(attr, None)
		ld("- data got for %s: %s", attr, sensor)
		try:
			result = hass.states.get(sensor).state
			ld("-- data got for %s: %s", sensor, result)
			return result
		except:
			return var
	except:
		return var

# function to check the state in time schedules
def is_time_between(now, begin_time, end_time) -> bool:
	ld("### is_time_between: Now: %s - Begin: %s - End: %s", now, begin_time, end_time)
	try:
		xhour = int(begin_time.split(":")[0])
	except:
		xhour = 0
	try:
		xmin = int(begin_time.split(":")[1])
	except:
		xmin = 0
	begin = datetime.time(hour=xhour, minute=xmin)
	ld("- beginn time: %s", begin)

	try:
		yhour = int(end_time.split(":")[0])
	except:
		yhour = 0
	try:
		ymin = int(end_time.split(":")[1])	
	except:
		ymin = 0
	end = datetime.time(hour=yhour, minute=ymin)
	ld("- end time: %s", end)

	ld("+ check %s < %s < %s", begin, now, end)
	try:
		if now >= begin and now <= end:
			ld("- is in time slot!")
			return True
		else:  
			ld("- not in time slot")
			return False
	except:
		ld("- time format wrong")
		return False

# function returns the status of the time schedule?
def is_in_time(schedule) -> bool:
	if schedule != None:
		slots = schedule.split(",")
		for slot in slots:
			start = slot.split("-")[0]
			end = slot.split("-")[1]
			ld("+ Slot: %s - Start: %s - End: %s", slot, start, end)
			if is_time_between(now, start, end) == True:
				return True
			else:
				return DEFAULT_IN_TIME

# function to check presense
def is_at_home() -> bool:
	for presense in SENSORS_PRESENCE:
		presense_state = hass.states.get(presense).state
		ld("+ %s has state: %s", presense, presense_state)

		if presense_state != SENSOR_ON:
		# if any presense is not ON, then PRESENSE go to False
			ld("+ %s is gone to OFF", presense)
			return False
		else:
			return True
				
# this create a basic service_data Array with entity_id only
def service_data(entity):
	sd = []
	sd = {"entity_id": entity}
	return sd
	
##########################################################################################
#  Functions to control the climate entity                                               #
##########################################################################################
					 
##########################################################################################			 
# set thermostat off only if not current to reduce commands
def call_climate_off():
	func = "call_climate_off"
	ld("+ Current state: %s - Current HVAC Mode: %s", current_preset, current_mode)
	if current_mode != HVAC_MODE_OFF:
		try:
			SERVICE_DATA = service_data(ENTITY_ID)
			ld("- Set climate to OFF - %s", SERVICE_DATA)
			hass.services.call(DOMAIN_CLIMATE, SERVICE_TURN_OFF, SERVICE_DATA, False)
		except:
			ld("- %s - Set climate off fails", func)
	else:
		ld("- No need to change the hvac mode")

##########################################################################################			 
# set thermostat hvac mode
def set_climate_hvac_mode(target_mode):
	func = "set_climate_hvac_mode"
	ld("+ Current HVAC Mode: %s - Current Preset: %s", current_mode, current_preset)
	if current_mode != target_mode:
		try:
			SERVICE_DATA = service_data(ENTITY_ID)
			SERVICE_DATA[CLIMATE_HVAC_MODE] = target_mode
			ld("- Set climate to mode: %s - Service Data: %s", target_mode, SERVICE_DATA)
			hass.services.call(DOMAIN_CLIMATE, SERVICE_SET_HVAC_MODE, SERVICE_DATA, False)
		except:
			ld("- %s - Set climate off fails", func)
	else:
		ld("- No need to change the hvac mode")

		
##########################################################################################
# set climate to preset mode
def set_climate_preset_mode(preset_mode):
	func = "set_climate_preset_mode"
	ld("+ Current Preset: %s - Current HVAC Mode: %s", current_preset, current_mode)
	try:
		if current_preset != preset_mode:
			SERVICE_DATA = service_data(ENTITY_ID)
			SERVICE_DATA[CLIMATE_PRESET_MODE] = preset_mode
			ld("+ Set preset_mode to %s - %s", preset_mode, SERVICE_DATA)
			hass.services.call(DOMAIN_CLIMATE, SERVICE_SET_PRESET_MODE, SERVICE_DATA, False)
		else:
			ld("+ No need to change the Preset Mode")
	
	except:
		logger.info("- %s - Set the Preset mode fails on: %s", func, ENTITY_ID)
			
##########################################################################################			 
# set thermostat temperature
def set_climate_setpoint(target_temperature):
	func = "set_climate_setpoint"
	ld("+ Current setpoint: %s", current_setpoint)
	if current_setpoint != target_temperature:
		try:
			SERVICE_DATA = service_data(ENTITY_ID)
			SERVICE_DATA[CLIMATE_TEMPERATURE] = float(target_temperature)
			SERVICE_DATA[CLIMATE_HVAC_MODE] = HVAC_MODE_HEAT
			ld("- Set climate setpoint to %s - %s", target_temperature, SERVICE_DATA)
			hass.services.call(DOMAIN_CLIMATE, SERVICE_SET_TEMPERATURE, SERVICE_DATA, False)
		except:
			ld("- %s - Set climate setpoint fails", func)
	else:
		ld("- No need to change setpoint")



##########################################################################################
#  Functions special for the climate ENTITY_ID                                           #
##########################################################################################


# check first if an entity is given
if  ENTITY_ID != "":

	ld("+ work with enitiy: %s", ENTITY_ID)
	# get the current thermostat values
	try:
		actual_states = hass.states.get(ENTITY_ID)
		#ld("\"%s\" - Climate RAW: %s", ENTITY_ID, actual_states)
	except:
		ld("Entity: %s could not be retrieved")
		
	try:
		current_mode = actual_states.state
		ld("Current State: %s", current_mode)
	except:
		ld("- get state fails")
		
	try:
		current_preset = actual_states.attributes.get(CLIMATE_PRESET_MODE)
		ld("- Current Preset: %s", current_preset)
	except:
		ld("- get preset of %s fails")
	
	try:
		current_setpoint = actual_states.attributes.get(CLIMATE_TEMPERATURE)
		ld("- Current Set Point: %s", current_setpoint)
	except:
		ld("- get setpoint fails")
		
	try:	
		current_temperature = actual_states.attributes.get(CLIMATE_CURRENT_TEMPERATURE)
		ld("- Current temperture: %s", current_temperature)
	except:
		ld("- get current temperature fails")	
	
	if MASTER == True:

		SWITCHES_ON_OFF = get_data_from_param([], PARAM_SWITCHES_ON_OFF)
		ld("--> SWITCHES_ON_OFF: %s", SWITCHES_ON_OFF)

		WINDOW_OFF_MODE = get_data_from_entity(DEFAULT_WINODW_OFF_MODE, PARAM_WINDOW_OFF_MODE)
		ld("--> WINDOW_OFF_MODE: %s", WINDOW_OFF_MODE)

		SENSORS_WINDOWS = get_data_from_param([], PARAM_WINDOW_SENSORS)
		ld("--> SENSORS_WINDOWS: %s", SENSORS_WINDOWS)

		SENSORS_PRESENCE = get_data_from_param([], PARAM_PRESENCE_SENSORS)
		ld("--> SENSORS_PRESENCE: %s", SENSORS_PRESENCE)

		TEMPERATURE_ECO_GLOBAL = get_data_from_entity(DEFAULT_ECO, PARAM_GLOBAL_ECO)
		ld("--> TEMPERATURE_ECO_GLOBAL: %s", TEMPERATURE_ECO_GLOBAL)
		TEMPERATURE_SET_DEFAULT_ECO = get_data_from_entity(DEFAULT_SET_DEFAULT_ECO, PARAM_SET_DEFAULT_ECO)
		ld("--> TEMPERATURE_SET_DEFAULT_ECO: %s", TEMPERATURE_SET_DEFAULT_ECO)

		# should be only used for storing the current temperatures
		SENSOR_TEMP_ECO = get_data_from_param(None, PARAM_ECO_TEMPERATURE)
		TEMPERATURE_ECO = get_data_from_entity(None, PARAM_ECO_TEMPERATURE)
		SENSOR_TEMP_COMFORT = get_data_from_param(None, PARAM_COMFORT_TEMPERATURE)
		TEMPERATURE_COMFORT = get_data_from_entity(None, PARAM_COMFORT_TEMPERATURE)

		# scheduler configuration
		USE_SCHEDULER = get_data_from_entity(DEFAULT_USE_SCHEDULER, PARAM_USE_SCHEDULER)
		ld("-->  USE_SCHEDULER: %s", USE_SCHEDULER)
		SCHEDULE_WEEKDAYS = get_data_from_entity("", PARAM_SCHEDULE_WEEKDAYS)
		ld("--> SCHEDULE_WEEKDAYS: %s", SCHEDULE_WEEKDAYS)
		SCHEDULE_SATURDAYS = get_data_from_entity("", PARAM_SCHEDULE_SATURDAYS)
		ld("--> SCHEDULE_SATURDAYS: %s", SCHEDULE_SATURDAYS)
		SCHEDULE_SUNDAYS = get_data_from_entity("", PARAM_SCHEDULE_SUNDAYS)
		ld("--> SCHEDULE_SUNDAYS: %s", SCHEDULE_SUNDAYS)
		
		# set USE_SCHEDULER
		if USE_SCHEDULER == "on":
			USE_SCHEDULER = True
		else:
			USE_SCHEDULER = False
	
		# set SET_ECO_TO_DEFAULT
		if TEMPERATURE_SET_DEFAULT_ECO == "on":
			TEMPERATURE_SET_DEFAULT_ECO = True
		else:
			TEMPERATURE_SET_DEFAULT_ECO = False
	
		# set WINDOW_OFF_MODE
		if WINDOW_OFF_MODE == "on":
			WINDOW_OFF_MODE = True
		else:
			WINDOW_OFF_MODE = False
		
		##########################################################################################
		#  get all the states to control                                                         #
		##########################################################################################

	
		# presense
		ld("### Check presense ###")
	
		PRESENSE = is_at_home()

		# windows are allways checked
		ld("### check window states ###")
		try:
			ld("- Window automation will be used")
			for window in SENSORS_WINDOWS: 
					window_state = hass.states.get(window).state
					ld("- %s has state: %s", window, window_state)
		
					# We invert this statement to catch 'None' as well
					if hass.states.is_state(window, SENSOR_ON):
					# if any Windows is open, then WINDOW_OPEN get True
						ld("- %s is open", window)
						WINDOW_OPEN = True
		except:
			# windows are closed
			WINDOW_OPEN = False
			ld("Window Check fails")
	
		# Switches ON or OFF
		# check if switch states are OFF
		# default: True  climate automation is ON
		ld("### check OFF sensor states ###")
		# if any SENSOR_OFF is OFF, the switch get False
		try:
			for switch in SWITCHES_ON_OFF:
				switch_state = hass.states.get(switch).state
				if switch_state == SENSOR_OFF:
					ld("+ Climate automation will be OFF")
					SWITCH_ON_OFF = False
		except:
			SWITCH_ON_OFF = True
			ld("ON/OFF Switch check fails")


		target_preset = current_preset
		target_mode = current_mode
	
		ld("MASTER: %s", MASTER)
	
		# Check if Climate should be on
		if current_setpoint != None:
			if current_preset == PRESET_MODE_ECO:
				SERVICE_DATA = service_data(SENSOR_TEMP_ECO)
				SERVICE_DATA['value'] = float(current_setpoint)
			if current_preset == PRESET_MODE_NONE:
				SERVICE_DATA = service_data(SENSOR_TEMP_COMFORT)
				SERVICE_DATA['value'] = float(current_setpoint)
			ld("+ Update sith Service Data %s", SERVICE_DATA)
			hass.services.call(DOMAIN_INPUT_NUMBER, SERVICE_SET_VALUE, SERVICE_DATA, False)

		logger.info("%s :: --> Actual States %s - Preset: %s - Setpoint: %s - Temperature: %s", ENTITY_ID, current_mode, current_preset, current_setpoint, current_temperature)		
		logger.info("%s :: --> Start Logic: SWITCH_ON_OFF: %s - WINDOW OPEN: %s - IN_TIME: %s - PRESENCE: %s", ENTITY_ID, SWITCH_ON_OFF, WINDOW_OPEN, IN_TIME, PRESENSE)
		
		if SWITCH_ON_OFF == True:
			ld("+ climate should be on")
			# Check if Home Mode
			if PRESENSE == True:
				# we are at home --> HEAT ON, PRESET ECO
				ld("+ We are at home --> Preset: %s", PRESET_MODE_NONE) 
				target_mode = HVAC_MODE_HEAT
				target_preset = PRESET_MODE_ECO
					
				# check the windows
				if WINDOW_OPEN == True:
					ld("- Windows are open")
					if WINDOW_OFF_MODE == False:
						ld("+ Window Open --> ECO")
						# Window open --> ECO
						target_mode = HVAC_MODE_HEAT
						target_preset = PRESET_MODE_ECO
					else:
						ld("Window open --> OFF")
						target_mode = HVAC_MODE_OFF
				else:
					target_mode = HVAC_MODE_HEAT
					# Check if schedule should be used
					if USE_SCHEDULER == True: 	
					# Time Schedules
						# helpers
						NO_TIME = datetime.time.fromisoformat("00:00:00")
						now = dt_util.now().time()
						# Monday: 0 -- Sunday: 7
						thisDay = dt_util.now().weekday()
						ld("+ thisDay: %s", thisDay)

						ld("+ get_time_schedule of day %s", thisDay)
						switcher = {
								0: SCHEDULE_WEEKDAYS,
								1: SCHEDULE_WEEKDAYS,
								2: SCHEDULE_WEEKDAYS,
								3: SCHEDULE_WEEKDAYS,
								4: SCHEDULE_WEEKDAYS,
								5: SCHEDULE_SATURDAYS,
								6: SCHEDULE_SUNDAYS
							} 
						time_schedule = switcher.get(thisDay, None)

						ld("+ Time Schedule is %s", time_schedule)

						IN_TIME = is_in_time(time_schedule)

						if IN_TIME == True:
							ld("+ we are in heating time")
							target_preset = PRESET_MODE_NONE
						else:
							ld("- we are out of heating time")
							target_preset = PRESET_MODE_ECO
					else:
						ld("- leave all as it is")
			else:
				logger.info("- We are out not at home")
				target_preset = PRESET_MODE_ECO

		else:
			logger.info("+ There is a OFF state -> Thermostat will be off")
			target_mode = HVAC_MODE_OFF
		
		logger.info("%s :: --> Target Mode: %s - Target Preset: %s", ENTITY_ID, target_mode, target_preset)
		#set hvac mode			
		if target_mode == HVAC_MODE_OFF:
			set_climate_hvac_mode(target_mode)
		
		# set the target preset if hvac mode is heat
		if target_mode == HVAC_MODE_HEAT:
			set_climate_hvac_mode(HVAC_MODE_HEAT)
			set_climate_preset_mode(target_preset)

		if current_preset == PRESET_MODE_ECO:
			slave_setpoint = TEMPERATURE_ECO
			if TEMPERATURE_SET_DEFAULT_ECO == True:
				ld("+ we use the global eco temperature")
				set_climate_setpoint(TEMPERATURE_ECO_GLOBAL)
	else:
		# the master need a little time to send his status data back
		time.sleep(2)
		# Her starts the SLAVE Konfiguration
		ld("+ This Thermostat is SLAVE of: %s", MASTER)
		
		try:
			ld("Retrieve States from Master %s", MASTER)
			master_states = hass.states.get(MASTER)
		except:
			ld("Entity: %s could not be retrieved", MASTER)

		try:
			master_mode = master_states.state
			ld("Master State: %s", current_mode)
		except:
			ld("- get state of master fails")

		try:
			master_preset = master_states.attributes.get(CLIMATE_PRESET_MODE)
			ld("- Master Preset: %s", current_preset)
		except:
			ld("- get preset of master fails")

		try:
			master_setpoint = master_states.attributes.get(CLIMATE_TEMPERATURE)
			ld("- Master Set Point: %s", current_setpoint)
		except:
			ld("- get setpoint of master fails")

		logger.info("%s :: --> Target Mode: %s - Preset: %s - SetPoint: %s", ENTITY_ID, master_mode, master_preset, master_setpoint)
		set_climate_hvac_mode(master_mode)
		if master_mode != HVAC_MODE_OFF:
			set_climate_preset_mode(master_preset)
			time.sleep(2)
			set_climate_setpoint(master_setpoint)
			

ld("-------------- DONE ------------------")		
