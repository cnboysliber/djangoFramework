import configparser, os


class NewConfigParser(configparser.RawConfigParser):
    def __init__(self, defaults=None):
        configparser.RawConfigParser.__init__(self, defaults=None)
        # configparser.RawConfigParser()

    def optionxform(self, optionstr):
        return optionstr


class Config():
    def __init__(self, conf_name, encoding='utf-8'):
        self.cf = NewConfigParser()
        self.file = conf_name
        self.cf.read(self.file, encoding)

    def get_intValue(self, section, option):
        return self.cf.getint(section, option)

    def get_boolean(self, section, option):
        return self.cf.getboolean(section, option)

    def get_str(self, section, option):
        return self.cf.get(section, option)

    def get_float(self, section, option):
        return self.cf.getfloat(section, option)

    def set_value(self, section, option, value):
        self.cf.set(section, option, value)
        # print(self.get_str(section, option))

    def write_file(self):
        try:
            with open(self.file, "w+") as f:
                self.cf.write(f)
        except ImportError:
            f.close()

    def get_sections(self):
        '''
        获取配置文件下所有sections
        :return:sections
        '''
        return self.cf.sections()

    def get_options(self, section):
        '''
        获取某个section下所有option
        :return: options
        '''
        return self.cf.options(section)


class GetInfo:
    def __init__(self, file):
        self.file = file
        self.cf = Config(self.file)

    def get_info(self, section, option):
        return self.cf.get_str(section, option)

    def write_info(self, section, option, value):
        # print(section, option,value)
        self.cf.set_value(section, option, value)
        self.cf.write_file()

    def get_info_for_public(self, section):
        '''
        获取某个section下所有options，并以option为key，对应值为value，添加到字典
        :param section:
        :return:
        '''
        publicDict = {}
        options = self.cf.get_options(section)
        for option in options:
            try:
                value = eval(self.cf.get_str(section, option))
            except Exception as e:
                value = self.cf.get_str(section, option)
            publicDict[option] = value
        return publicDict


if __name__ == "__main__":
    cf = Config(r"d:\workplace\FCB_Auto_Test\config\db\test_db.cfg")
    result = cf.get_sections()
    print(result)
    for i in result:
        res = cf.get_options(i)
        print(res)
