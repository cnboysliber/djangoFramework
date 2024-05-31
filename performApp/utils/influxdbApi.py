from django.conf import settings
from influxdb_metrics.utils import query
from influxdb import InfluxDBClient

from FasterRunner.utils.logging import logger
from performApp.utils import error as err


class InfluxDBofJmeter(object):
    """
    influxdb 数据库操作
    """

    @staticmethod
    def get_application_data(application, start_time, end_time):
        """
        查询接口总响应数据信息
        :param application 任务ID
        :param start_time 毫秒时间戳
        :param end_time 毫秒时间戳
        :return:
        """
        client = InfluxDBClient(
            settings.INFLUXDB_HOST,
            settings.INFLUXDB_PORT,
            settings.INFLUXDB_USER,
            settings.INFLUXDB_PASSWORD,
            settings.INFLUXDB_DATABASE,
            timeout=settings.INFLUXDB_TIMEOUT,
            ssl=getattr(settings, 'INFLUXDB_SSL', False),
            verify_ssl=getattr(settings, 'INFLUXDB_VERIFY_SSL', False),
            proxies=getattr(settings, 'INFLUXDB_PROXIES', None),
        )
        sql = f'SELECT mean("avg") as "avg", mean("pct90.0") as "pct90", mean("pct95.0") as "pct95",' \
              f' mean("pct99.0") as "pct99", sum("count") as "count", mean("count") as "tps" FROM "jmeter" WHERE ' \
              f'("application" =~ /^{application}/) ' \
              f'AND time >= {start_time}ms AND time < {end_time}ms GROUP BY "transaction", "statut"'
        try:
            logger.info(sql)
            ret = client.query(sql)
        except Exception as e:
            logger.error(str(e))
            raise err.AppError(500, '查询influxDB异常：%s' % e)
        logger.info(ret.__dict__)
        return ret.__dict__ if ret else ret


if __name__ == '__main__':
    import time, os

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FasterRunner.settings.dev')
    influx = InfluxDBofJmeter()
    start = 1629295200000
    end = 1629302399000
    result = influx.get_application_data('1000001011384602', start, end)
    print(1111111111, result)







