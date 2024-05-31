from enum import Enum

class broker_type(Enum):
    EMPLOYEE = '恒大员工'
    OWNER = '恒大老业主'





class get_project(Enum):
    '''
    根据项目目录
    '''
    broker="broker"
    customer="customer"
    middleend="middleend"
    om="om"
    prod="prod"
    agent_manager="agent_manager"
    others="未识别的项目"

