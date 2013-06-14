from django.conf import settings

from groups import models as group_model
from signup import models as signup_model

import random
import math
import datetime
import pytz


def shuffle(rac):
    shuffled = []
    while len(rac):
        ridx = random.randint(0, len(rac)-1)
        shuffled += [rac[ridx]]
        del rac[ridx]
    return shuffled

def prepare_groups(max_group_size=40):
    """ Calculate grouping """

    # get all signups
    signups = signup_model.get_signups()
    tz_grouping = {}

    for user_signup in signups:
        timezone = user_signup['questions']['timezone']
        tz_offset = int(datetime.datetime.now(pytz.timezone(timezone)).strftime('%z'))
        user_signup['tz_offset'] = tz_offset
        if tz_offset in tz_grouping:
            tz_grouping[tz_offset].append(user_signup)
        else:
            tz_grouping[tz_offset] = [user_signup]

    for timezone, group in tz_grouping.items():
        tz_grouping[timezone] = shuffle(group)

    merge = lambda x,y: x + y
    tz_sorted_signups = reduce(merge, [ tz_grouping[timezone] for timezone in sorted(tz_grouping.keys())])

    groups = [ tz_sorted_signups[i:min(i+max_group_size, len(tz_sorted_signups))] for i in range(0,len(tz_sorted_signups), max_group_size)]
    return groups


def create_groups(groups, name_prefix="Group"):
    """ Create the groups in the backend """
    for i, group_data in enumerate(groups):
        group_address = "{0}-{1}@{2}".format(name_prefix.lower().replace(' ','-'), i+1, settings.EMAIL_DOMAIN)
        group_name = "{0} {1}: {2} to {3}".format(name_prefix, i+1, group_data[0]['tz_offset'], group_data[-1]['tz_offset'])
        print(group_name)
        group = group_model.create_group(group_address, group_name)

        for member in group_data:
            group_model.add_group_member(group['uri'], member['email'])

