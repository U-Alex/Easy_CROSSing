#core__views_ext

from datetime import datetime


####################################################################################################


class ProcessLock:
    _map_cut = False
    _dt_map_cut = None
    _user_map_cut = None

    @staticmethod
    def set_map_cut(value: bool, l_user: str = False):
        ProcessLock._map_cut = value
        if value:
            ProcessLock._dt_map_cut = datetime.now().replace(microsecond=0)
            ProcessLock._user_map_cut = l_user
            # print(ProcessLock._dt_map_cut, ProcessLock._user_map_cut)

    @staticmethod
    def is_cut():
        return ProcessLock._map_cut, ProcessLock._dt_map_cut, ProcessLock._user_map_cut

