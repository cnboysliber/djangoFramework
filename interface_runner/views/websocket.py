from django.shortcuts import render,HttpResponse
from dwebsocket.decorators import accept_websocket,require_websocket
from rest_framework.decorators import api_view, authentication_classes
import time,os,json,dwebsocket
from io import StringIO
import sys
#from interface_runner.views.do_logs import GetLog
import subprocess
#logger=GetLog().logger()
from loguru import logger



ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
log_file=os.path.join(ROOT_PATH,"logs","run_case.log")
#html_file=os.path.join(ROOT_PATH,"templates","login.html")
html_file=os.path.join(ROOT_PATH,"templates","login.html")

@api_view(["GET"])
def test_web(request):
    return render(request,html_file)


# accept_websocket-—可以接受websocket请求和普通http请求
# require_websocket----只接受websocket请求,拒绝普通http请求

# #@api_view(["POST"])
# @accept_websocket
# #@require_websocket
# def get_run_case_log(request):
#     print(request)
#     if  request.is_websocket():
#         print('websocket connection....')
#         msg = request.websocket.wait()  # 接收前端发来的消息
#         print(msg, type(msg))
#         msg=json.loads(str(msg,encoding="utf-8"))  # b'["1","2","3"]' <class 'bytes'> ['1', '2', '3']
#
#         for message in msg:
#             #message = message.decode('utf-8')  # 接收前端发来的数据
#             print(message)
#             if message == 'backup_all':  # 这里根据web页面获取的值进行对应的操作
#         #if request.is_websocket():
#                 print('收到websocket请求')
#                 with open(log_file, 'r', encoding='gbk') as f:
#                     log_length = len(f.readlines())
#                     time.sleep(1)
#                 while True:
#                     with open(log_file, 'r', encoding='gbk') as f:
#                         contents = f.readlines()
#                     for i in range(log_length):
#                         request.websocket.send(contents[i].encode('gbk'))


# @accept_websocket
def get_run_case_log(request):
    '''
    通过websocket获取日志log里面的日志，并实时返回给前端
    '''
    if request.is_websocket():
        #msg=request.websocket.wait()
        for message in request.websocket:  # 接收前端发来的消息
            message = decode(message)
            if message:
                import platform
                if platform.system().lower() == "windows":
                    f = open(log_file, "r", encoding='utf-8')
                    while True:
                        lines = f.readline()  # 读取下一行,不断轮询读取
                        if lines:
                            import base64
                            line_res = base64.b64encode(lines.encode('utf-8')).decode("utf-8")
                            request.websocket.send(line_res)
                else:
                    import subprocess
                    p = subprocess.Popen(f"tail -f {log_file}",
                                         shell=False,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
                    while True:
                        lines = p.stdout.readline()
                        if lines:
                            request.websocket.send(lines.decode('utf-8'))
            else:
                request.websocket.send("无权限".encode("utf-8"))



# @accept_websocket
def get_output(request):
    if request.is_websocket():
        read_obj = StringIO()
        sys.stdout = read_obj
        while True:
            time.sleep(2)
            logger.info(f"我不是websocket")
            logger.info(f"我是websocket{read_obj.getvalue()}")
            request.websocket.send(read_obj.getvalue().encode("utf-8"))

import shlex
# @accept_websocket
def get_output_su(request):
    if request.is_websocket():
        shell_cmd = 'java -version'
        cmd = shlex.split(shell_cmd)
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while p.poll() is None:  #查看子进程是否结束，未结束返回None
            line = p.stdout.readline()
            line = line.strip()
            if line:
                request.websocket.send(decode(line))
        if p.returncode == 0:
            line = p.stdout.readline()
            line = line.strip()
            if line:
                request.websocket.send(decode(line))
        else:
            request.websocket.send('Subprogram failed')


def decode(s):
    try:
        return s.decode('utf-8')

    except UnicodeDecodeError:
        return s.decode('gbk')


if __name__=="__main__":
    get_run_case_log()