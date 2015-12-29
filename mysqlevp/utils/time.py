from __future__ import print_function, absolute_import, unicode_literals

from datetime import datetime


def tzlc(dt, tz, truncate_to_sec=True):
    if dt is None:
        return None
    if truncate_to_sec:
        dt = dt.replace(microsecond=0)
    return tz.localize(dt)


def naive_dt2str(data, tz):
    assert(isinstance(data, dict))
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = str(tz.localize(value.replace(microsecond=0)))
    return data
