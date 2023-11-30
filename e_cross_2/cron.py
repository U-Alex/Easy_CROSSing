#!/usr/bin/env python3

import os
import django

#######################################################################

def execute_command():
    from django.conf import settings
    c_login, c_pass = settings.COMMUT_AUTH
    print(c_login, c_pass)





#######################################################################

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_cross_2.settings")
    django.setup()
    execute_command()
