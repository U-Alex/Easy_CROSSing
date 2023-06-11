# core__e_config

class conf:
    #
    SCRIPT_PATH = "e_cross_2/static/MagickSlicer-master/magick-slicer.sh"
    #
    ##HOME_PATH = os.getcwd()
    #HOME_PATH = '/home/'               #for production server
    HOME_PATH = '/home/uaa/django_2/'     #for dev server
    #
    MAP_PATH =  "e_cross_2/media/map/"
    MAP1_PATH = "e_cross_2/media/map_1/"
    MAP2_PATH = "e_cross_2/media/map_2/"
    #

    MONTHS = {1:('январь'), 2:('февраль'), 3:('март'), 4:('апрель'),
              5:('май'), 6:('июнь'), 7:('июль'), 8:('август'),
              9:('сентябрь'), 10:('октябрь'), 11:('ноябрь'), 12:('декабрь')
              }
    YEARS = range(2009, 2026)

#mod core
    #
    OBJECT_TYPE = ['здание',  'УД',    'кросс','акт.оборуд.','крт','порт кросса','порт оборуд.','порт крт', 'муфта',   'кабель, волокно','объект', 'порт комм.вирт.','заявка','абон.устр-во']
    #              0           1        2       3             4     5             6              7           8          9                 10        11                12       13
    MODELS_LIST = ['Building','Locker','Cross','Device',     'Box','Cross_ports','Device_ports','Box_ports','Coupling','Coupling_ports' ,'PW_cont','Device_ports_v', 'Appp',  'Subunit']
    #
    OPERATION_1 = ['',
                   'создание',                          #  1
                   'редактирование',                    #  2
                   'внешняя кроссировка',               #  3
                   'внутренняя кроссировка',            #  4
                   'абонентская кроссировка',           #  5
                   'снятие внешней кроссировки',        #  6
                   'снятие внутр. кроссировки',         #  7
                   'снятие аб. кр.',                    #  8
                   'смена статуса',                     #  9
                   'добавление кабеля в крт',           # 10
                   'смена типа',                        # 11
                   'прокладка кабеля',                  # 12
                   'удаление',                          # 13
                   'перенос кабеля',                    # 14
                   'обн.конфигурации портов',           # 15
                   'обмен с NSD',                       # 16
                   'обмен с билингом',                  # 17
                   'блокировка портов',                 # 18
                   '']
    #
    OPERATION_1_8 = ['-',
                     '(закр./отмена)',                  #  1
                     '(переезд)',                       #  2
                     '(смена ресурсов)']                #  3
    #
    OPERATION_1_9 = ['',
                     '(внешняя кр.)',                   #  1
                     '(внутр./аб. кр.)']                #  2
    #
    OPERATION_1_16 = ['',
                      '.1.(создание откл.)',            #  1
                      '.2.(отправка данных)',           #  2
                      '.3.(подтверждение откл.)',       #  3
                      '']

#mod app_proc
    #
    TYPE_PROC_LIST = [[0, 'установка'], [1, 'снятие']]
    #
    APP_REJECT = [[0, '----'], [1, 'некорректная заявка'], [2, 'отказ заявителя'], [3, 'дом не подключен'], [4, 'подъезд не подключен']]
    #
    APP_DELAY = [[0, '----'], [1, 'добавить коммутатор'], [2, 'добавить кабель'], [3, 'согласование с юр.отделом'], [4, 'техзадание']]
#
    #
    COLOR_APP = ['white', 'yellow', 'lawngreen', 'gray', 'pink', 'lightcoral']
    #
    COLOR_CROSS = ['white', 'lawngreen', 'yellow', 'pink', 'aqua', 'gray']
    #
    COLOR_PLINT = ['violet', 'brown', 'blue', 'green', 'orange', 'teal', 'black', 'black', 'black', 'black']
    #
    APP_REJECT_LIST = ['----', 'некорректная заявка', 'отказ заявителя', 'дом не подключен', 'подъезд не подключен']
    APP_REJECT_LIST2 = ['----', 'некорректная заявка', 'отказ заявителя', '', '', 'ресурсы были сняты ранее']
    #
    APP_DELAY_LIST = ['----', 'добавить коммутатор', 'добавить кабель', 'согласование с юр.отделом', 'техзадание']
    #billing
    DOG_STATUS_LIST = ['Активен', 'В отключении', 'Отключен', 'Закрыт', 'Приостановлен', 'В подключении']

#mod cross
    #
    STATUS_LIST = [[0, '---'], [1, 'активная'], [2, 'бронь'], [3, 'служебная'], [4, 'СЛ']]
    #
    STATUS_LIST_LO = [[0, 'в проекте'], [1, 'монтаж'], [2, 'в работе'], [3, 'отключен']]
    #
    COLOR_LIST_LO = ['orange', 'yellow', 'lawngreen', 'gray']##FF707E
    #
    PRI_LIST_F = [[1, 'закрытие договора (отмена брони)'], [2, 'переезд'], [3, 'смена ресурсов']]
#
    #
    MAC_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
    #
    IP_RE = r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)[\.\,]){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
    #
    DEV_FIND_PARAM = ['ip', 'mac', 'sn', 'vlan']
    #
    COLOR_CROSS = ['white', 'lawngreen', 'yellow', 'pink', 'aqua', 'gray']
    #
    COLOR_PLINT = ['violet', 'brown', 'blue', 'green', 'orange', 'teal', 'black', 'lightcoral', 'gray', 'black']
    #
    PRI_LIST = ['', '', ' (переезд)', ' (смена ресурсов)']
    #
    COLOR_CRAB = ['black', 'green', 'orange', 'violet', 'olive', 'red']
    #
    #COLOR_CABLE = ['white', '#BFFFBB', '#FFD39B', '#BCD2EE', 'white', 'white', 'white', 'white', 'white', 'white']
    #
    KEY_DOOR_TYPE = ['', 'в ключнице', 'универсальный внутр.', 'замок открыт', 'замок сломан', 'универс.навесной', 'треугольник малый', 'треугольник большой']
    #
    POE_TYPE = [[0, '---'], [1, 'порт'], [2, 'PoE-инжектор'], [3, 'отдельный б.п.']]
    #
#mod cable
    #
    OBJ_LIST = [['1', 'опора'], ['2', 'колодец']]
    #
    INT_C_STATUS_LIST = [['0', ''], ['1', 'транзит'], ['2', 'варка']]
#
    #
    RU_COLOR_LIST ={'bisque':           'натуральный',
                    'beige':            'неокрашенный',
                    '#ff2222':          'красный',
                    'yellow':           'жёлтый',
                    'limegreen':        'зеленый',
                    'royalblue':        'синий',
                    'sienna':           'коричневый',
                    '#565656':          'чёрный',
                    'orange':           'оранжевый',
                    '#b300ff':          'фиолетовый',
                    'white':            'белый',
                    'silver':           'серый',
                    'mediumturquoise':  'бирюзовый',
                    'hotpink':          'розовый',
                    'cyan':             'голубой',
                    'lime':             'лайм',
                    'crimson':          'малиновый',
                    'olive':            'оливковый',
                    'tan':              'танин',
                    '#44ff00':          'салатовый',
                    '#cfb18a':          'бежевый',
                    '#ff2323':          'красный+k.m',
                    '#ffff01':          'жёлтый+k.m',
                    '#33cd33':          'зеленый+k.m',
                    '#426ae1':          'синий+k.m',
                    '#882d18':          'коричневый+k.m',
                    '#565657':          'чёрный+k.m',
                    '#ff7f01':          'оранжевый+k.m',
                    '#b300fe':          'фиолетовый+k.m',
                    '#fffffe':          'белый+k.m',
                    '#c0c0c1':          'серый+k.m',
                    '#ff69b5':          'розовый+k.m',
                    '#00fffe':          'голубой+k.m',
                    }
    #
    N_CAB_COLORS = {1:  'deepskyblue',
                    2:  'aquamarine',
                    3:  'greenyellow',
                    4:  'gold',
                    5:  'salmon',
                    6:  'plum',
                    7:  'wheat',
                    8:  'sandybrown',
                    9:  '#B5FFCE',
                    10: '#B5FFCE',
                    }
    #длина кроссировки патчкордом, m
    CROSS_LEN = 3

#mod statist
    #
    #OFFICE_LIST = [[''],
    #               ['CO-1', 'CO-5', 'CO-1-1', 'CO-1-2', 'CO-1-3', 'CO-5-1'],
    #               ['CO-2', 'CO-3', 'CO-4', 'CO-3-1', 'CO-3-2', 'CO-4-1']
    #               ]

#mod eq_rent
    #
    #EQ_TYPE_LIST = [[1, 'TV приставка'], [2, 'Роутер']]
    #
    #EQ_OFFICE_LIST = [[1, 'тех.под.'], [2, 'СО-1'], [3, 'СО-2']]
    #
    #EQ_STATUS_LIST = [[0, 'свободно'], [1, 'в работе'], [2, 'отсутствует']]
    #
    #EQ_STATUS_COLOR_LIST = ['lemonchiffon', 'lawngreen', 'gray']
    #
    #EQ_CANCEL_LIST = [[0, 'возврат от абонента'], [1, 'отмена установки']]
    #
    #EQ_FIRM_ID_LIST = [1, 3, 2] #0xxxxx,1xxxxx,2xxxxx
    #
    #EQ_OPERATION = ['',
    #                'создание',                          #  1
    #                'редактирование',                    #  2
    #                'установка',                         #  3
    #                'возврат',                           #  4
    #                'перемещение',                       #  5
    #                'удаление',                          #  6
    #                ]
    #
    #EQ_TEMP_OFF = ['', 'тех.под.', 'CO-1', 'CO-2']
    #EQ_TEMP_FIRM = ['', 'Телевокс', 'Телевокс-TV', 'Телематик']

#mod mess
    #
    #groups_mess = {'0': 'Всем', 'tu': 'Техучет', 'tp': 'Техподдержка', 'of': 'Абонентский отдел'}
