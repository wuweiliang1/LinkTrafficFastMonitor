import Model
import configparser
import concurrent.futures
import time
import threading
import sys
from pysnmp.hlapi import *


def main():
    config = configparser.ConfigParser()
    config.read(sys.path[0] + '/config.ini', encoding='UTF-8')
    linklist = []
    for link_config in config.sections():
        linklist.append(Model.Link(link_config, config[link_config]['cir'], config[link_config]['srcip'],
                                   config[link_config]['community'], config[link_config]['ifIndex'],
                                   config[link_config]['threshold_in'],config[link_config]['threshold_out'], config[link_config]['description'],
                                   config[link_config]['mib_interval'], config[link_config]['multiplier'],
                                   config[link_config]['exceed_alert_threshold']))
    # with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    #     for link in linklist:
    #         executor.submit(start_listen, link, mutex)
    #         time.sleep(0.5)
    for link in linklist:
        thread_local_engine = SnmpEngine()
        t = threading.Thread(target=start_listen, args=(link, thread_local_engine))
        t.start()
        time.sleep(0.5)


def start_listen(linkobj, engine):
    while True:
        linkobj.update_record(engine)
        linkobj.check_speed()
        time.sleep(linkobj.update_interval)


if len(sys.argv) == 2 and sys.argv[1] == '--shell':
    main()
else:
    print('For safety reason, you should not run this program manually.')
    print('Please use the management script (CoreLinkMonitor.sh) instead')
    print('Common Usage: ./CoreLinkMonitor.sh start|stop|reload|check')
