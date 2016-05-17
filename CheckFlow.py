from pysnmp.hlapi import *


def get_snmp_data(ip, ifIndex, community_name, direction,engine):
    community = CommunityData(community_name)
    target = UdpTransportTarget((ip, 161))
    if direction == 'in':
        errorIndication, errorStatus, errorIndex, varBinds = \
            next(getCmd(engine,community, target, ContextData(),
                        ObjectType(ObjectIdentity('IF-MIB', 'ifHCInOctets', ifIndex))))
    elif direction == 'out':
        errorIndication, errorStatus, errorIndex, varBinds = \
            next(getCmd(engine, community, target, ContextData(),
                        ObjectType(ObjectIdentity('IF-MIB', 'ifHCOutOctets', ifIndex))))
    else:
        return None
    if errorIndication:
        return 0
    else:
        return int(varBinds[0][1].prettyPrint())


