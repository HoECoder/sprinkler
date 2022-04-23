"""Sample Program Conf Data"""

from sprinkler.program.time_utilities import seconds_from_midnight

STATION_1_RUN = 55 * 60
STATION_2_RUN = 40 * 60
STATION_3_RUN = 45 * 60
STATION_4_RUN = 30 * 60
STATION_5_RUN = 50 * 60

SAMPLE_PROGRAM_DICT = {
    "start_time_of_day": seconds_from_midnight(6, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 2,
    "respect_rain": True,
    "respect_water_adjustment": True
}

SAMPLE_ODD_DAY = {
    "start_time_of_day": seconds_from_midnight(6, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 3,
    "respect_rain": True,
    "respect_water_adjustment": True
}

SAMPLE_DOW_DAY = {
    "start_time_of_day": seconds_from_midnight(6, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 1,
    "respect_rain": True,
    "respect_water_adjustment": True,
    "days_of_the_week": [0, 2, 4] # Mon, Wed, Fri - assuming 0 is Monday
}

SAMPLE_NO_ADJ_PROGRAM_DICT = {
    "start_time_of_day": seconds_from_midnight(6, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 2,
    "respect_rain": True,
    "respect_water_adjustment": False
}

SAMPLE_RUN_TIME = 0
for _entry in SAMPLE_PROGRAM_DICT["station_durations"]:
    SAMPLE_RUN_TIME += _entry["duration"]


SAMPLE_BAD_PROGRAM_DICT = {
    "station_durations": [
        {"station_id": 1, "duration": 55 * 60},
        {"station_id": 2, "duration": 40 * 60},
        {"station_id": 3, "duration": 45 * 60},
        {"station_id": 4, "duration": 30 * 60},
        {"station_id": 5, "duration": 50 * 60},
    ],
    "program_type": 2,
    "respect_rain": True,
    "respect_water_adjustment": True
}

SAMPLE_EVEN_DST_START_DICT = {
    "start_time_of_day": seconds_from_midnight(1, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 2,
    "respect_rain": True,
    "respect_water_adjustment": True
}
SAMPLE_ODD_DST_START_DICT = {
    "start_time_of_day": seconds_from_midnight(1, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 3,
    "respect_rain": True,
    "respect_water_adjustment": True
}

SAMPLE_EVEN_DST_END_DICT = {
    "start_time_of_day": seconds_from_midnight(0, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 2,
    "respect_rain": True,
    "respect_water_adjustment": True
}
SAMPLE_ODD_DST_END_DICT = {
    "start_time_of_day": seconds_from_midnight(0, 0),
    "station_durations": [
        {"station_id": 1, "duration": STATION_1_RUN},
        {"station_id": 2, "duration": STATION_2_RUN},
        {"station_id": 3, "duration": STATION_3_RUN},
        {"station_id": 4, "duration": STATION_4_RUN},
        {"station_id": 5, "duration": STATION_5_RUN},
    ],
    "program_type": 3,
    "respect_rain": True,
    "respect_water_adjustment": True
}
