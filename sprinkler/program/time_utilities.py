"""Utilities for manipulating time"""

import datetime
import pendulum

def seconds_from_midnight(hour: int, minute: int) -> int:
    """Returns the number of seconds from midnight"""
    if hour < 0 or hour >= 24:
        raise ValueError(f"Hour must be 0 - 23: {hour}")
    if minute < 0 or minute >= 60:
        raise ValueError(f"Minute must be 0 - 59: {minute}")
    return (hour * 3600) + (minute * 60)

def utc_for_local_midnight(now: float, local_tz: str) -> float:
    """Takes the UTC now and determines the local midnight, returning a UTC float"""
    local_now = pendulum.from_timestamp(now, tz = local_tz)
    local_midnight: pendulum.datetime = local_now.set(hour = 0,
                                                      minute = 0,
                                                      second = 0,
                                                      microsecond=0)
    return local_midnight.float_timestamp

def local_dt_for_utc_now(now: float, local_tz: str)  -> datetime.datetime:
    """Takes the UTC timestampe and a local TZ and gives a datetime in the current TZ"""
    local_dt = pendulum.from_timestamp(now, tz = local_tz)
    return local_dt

def after_now(now: float, check_time: float, jitter: float) -> bool:
    """Returns true if now is within jitter seconds of check_time"""
    if now == check_time:
        return True
    if now > check_time and (now - check_time) <= jitter:
        return True
    return False
