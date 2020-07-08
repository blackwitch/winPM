import os, sys , subprocess, _thread, signal
import win32gui, win32api, win32con
import psutil
import time
import logging
import json
import time
from pathlib import Path
from datetime import datetime

PMList = dict()  # process infomation list
def getPMKey(cfg_task):
    try:
        return hash(cfg_task["path"] + "/" + cfg_task["file"])
    except Exception as e:
        print("ERROR : Incorrect \"config.json\" file! ERROR => ", e)
        sys.exit(0)


#############################################################
## crontab-like code is from https://github.com/idning/pcl/blob/master/pcl/crontab.py 
class Event(object):
    def __init__(self, desc, func, args=(), kwargs={}, use_thread=False):
        """
        desc: min hour day month dow
            day: 1 - num days
            month: 1 - 12
            dow: mon = 1, sun = 7
        """
        self.desc = desc 
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.use_thread = use_thread

    #support: 
    # * 
    # 59
    # 10,20,30
    def _match(self, value, expr):
        #print 'match', value, expr
        if expr == '*':
            return True
        values = expr.split(',')
        for v in values:
            if int(v) == value:
                return True
        return False

    def matchtime(self, t):
        mins, hour, day, month, dow = self.desc.split()
        return self._match(t.minute       , mins)  and\
               self._match(t.hour         , hour)  and\
               self._match(t.day          , day)   and\
               self._match(t.month        , month) and\
               self._match(t.isoweekday() , dow)

    def check(self, t):
        if self.matchtime(t):
            if self.use_thread:
                thread.start_new_thread(self.func, self.args, self.kwargs)
            else:
                try:
                    self.func(*self.args, **self.kwargs)
                except Exception as e:
                    logging.exception(e)

class Cron(object):
    def __init__(self):
        self.events = []

    def add(self, desc, func, args=(), kwargs={}, use_thread=False):
        self.events.append(Event(desc, func, args, kwargs, use_thread))

    def run(self):
        last_run = 0
        while True:
            #wait to a new minute start
            t = time.time()
            next_minute = t - t%60 + 60
            while t < next_minute:
                sleeptime = 60 - t%60
                logging.debug('current time: %s, we will sleep %.2f seconds' %(t, sleeptime))
                time.sleep(sleeptime)
                t = time.time()

            if last_run and next_minute - last_run != 60:
                logging.warn('Cron Ignored: last_run: %s, this_time:%s' % (last_run, next_minute) )
            last_run = next_minute

            current = datetime(*datetime.now().timetuple()[:5])
            for e in self.events:
                e.check(current)
            time.sleep(0.001)
## crontab-like codes
#############################################################


#############################################################
## command thread
def command_thread():
    while True:
        try:
            line = input('>> ')
            params = line.split()
            if len(params) == 0:
                continue
        
            cmd = params[0]
            if cmd == "?" or cmd =="h" or cmd =="help" :
                print ("usage : <command> [options]")
                print ("Command list")
                print ("===============================")
                print ("command         | desc")
                print ("list            | show the process list you added")
                print ("stop [title]    | kill a process by the title in config")
                print ("start [title]   | start a process by the title in config")
                print ("restart [title] | restart a process by the title in config")
                print ("exit            | exit this program ")
            elif cmd == "list":
                print ( psutil.cpu_percent() , psutil.virtual_memory())
                print ("---------------------------------------------------------------------------------------------")
                print ("| %s | %s | %s | %s | %s | %s | %s |"% ("name".ljust(16)[:16],"job".ljust(12)[:12],"status".ljust(12)[:12],"restart".ljust(7)[:7],"cpu".ljust(4)[:4],"mem".ljust(8)[:8],"uptime".ljust(12)[:12]))
                print ("---------------------------------------------------------------------------------------------")
                try:
                    for key in PMList:
                        info = PMList[key]
                        print ("| %s | %s | %s | %s | %s | %s | %s |" % (info["name"].ljust(16)[:16],info["job"].ljust(12)[:12],info["status"].ljust(12)[:12],str(info["restart"]).ljust(7)[:7],str(info["cpu_usage"]).ljust(4)[:4],str(info["mem_usage"]).ljust(8)[:8],str(info["uptime"]).ljust(12)[:12]) )
                except Exception:
                    import traceback
                    print (traceback.format_exc())
            elif cmd == "exit":
                print("Press CTRL + C to exit this program.")
                sys.exit(0)
            elif cmd == "start":
                if len(params) < 2:
                    print ("Invalid paramater(s). Type ""?"" will show you manpage")
                    continue
                for key in PMList:
                    if params[1] == PMList[key]["name"]:
                        startProcess(PMList[key])
                        break
            elif cmd == "stop":
                if len(params) < 2:
                    print ("Invalid paramater(s). Type ""?"" will show you manpage")
                    continue
                for key in PMList:
                    if params[1] == PMList[key]["name"]:
                        stopProcess(PMList[key])
                        break
            elif cmd == "restart":
                if len(params) < 2:
                    print ("Invalid paramater(s). Type ""?"" will show you manpage")
                    continue
                for key in PMList:
                    if params[1] == PMList[key]["name"]:
                        stopProcess(PMList[key])
                        print("Wait for a sec")
                        time.sleep(3)
                        startProcess(PMList[key])
                        break
        except KeyboardInterrupt:
            print (" CTRL + C")
## command thread
#############################################################

def stopProcess(task):
    HWnd = win32gui.FindWindow(None, task["name"])
    if HWnd != 0:
        try:
            if task["buttons"]["STOP"]:
                btnHnd= win32gui.FindWindowEx(HWnd, 0 , "Button", task["buttons"]["STOP"])
                if btnHnd != 0:
                    win32api.SendMessage(btnHnd, win32con.BM_CLICK, 0, 0)
                else:
                    print(task["buttons"]["STOP"], " button isn't there.")
                time.sleep(5);

            if task["buttons"]["QUIT"]:
                btnHnd= win32gui.FindWindowEx(HWnd, 0 , "Button", task["buttons"]["QUIT"])
                if btnHnd != 0:
                    win32api.SendMessage(btnHnd, win32con.BM_CLICK, 0, 0)
                else:
                    print(task["buttons"]["QUIT"], " button isn't there.")
                time.sleep(5);

        except:
            time.sleep(1)

    HWnd = win32gui.FindWindow(None, task["name"])
    if HWnd != 0:
        os.system("taskkill /f /im "+task["proc_name"])
        time.sleep(1)
    task["bStop"] = True
    task["status"] = "stop"
    task["pid"] = 0
    task["hwnd"] = None
    task["mem_usage"] = 0
    task["cpu_usage"] = 0
    task["uptime"] = 0
    print (" STOP [" + task["name"] + "]")


def startProcess(task):
    # execute the app
    HWnd = win32gui.FindWindow(None, task["name"])
    boolAlreadyStart = True
    if HWnd == 0:
        boolAlreadyStart = False
        os.chdir(os.path.realpath(task["app_path"]))
        myProcess = subprocess.Popen(task["app"])
        time.sleep(5)
        HWnd = win32gui.FindWindow(None, task["name"])
    if HWnd == 0:
        print(task["name"], " is failed to execute.")
    else:
        if boolAlreadyStart == False:
            try:
                if task["buttons"]["START"]:
                    btnHnd= win32gui.FindWindowEx(HWnd, 0 , "Button", task["buttons"]["START"])
                    if btnHnd != 0:
                        win32api.SendMessage(btnHnd, win32con.BM_CLICK, 0, 0)
                    else:
                        print(task["buttons"]["START"], " button isn't there.")
            except:
                time.sleep(1)
            print(task["name"]," starts!")
            task["bStop"] = False
            task["status"] = "running"
            task["restart"] = int(task["restart"]) + 1
            print( "RESTART ", task["restart"])
            print (" START [" + task["name"] + "]")
        else:
            print("[" + task["name"],"] is running already")

if __name__ == "__main__":
    try:
        def get_pid(process_name):
            try:
                processes = filter(lambda p: psutil.Process(p).name() == process_name, psutil.pids())
                for pid in processes:
                    return pid
                return -1
            except Exception as e:
                print ("GET_PID NOT FOUND ", process_name, e)
                return -1
    
        def task_update():
            for key in PMList:
                if PMList[key]["hwnd"] == None:
                    PMList[key]["hwnd"] = win32gui.FindWindow(None,PMList[key]["name"])
                PMList[key]["pid"] = get_pid(PMList[key]["proc_name"])

                if PMList[key]["pid"]> 0 and PMList[key]["bStop"] == False:
                    PMList[key]["status"] = psutil.Process(PMList[key]["pid"]).status()
                    PMList[key]["cpu_usage"] = psutil.Process(PMList[key]["pid"]).cpu_percent()
                    try:
                        PMList[key]["mem_usage"] = psutil.Process(PMList[key]["pid"]).memory_full_info().uss
                    except:
                        PMList[key]["mem_usage"] = 0
                    try:
                        pidcreated = datetime.fromtimestamp(psutil.Process(PMList[key]["pid"]).create_time())
                        diff = datetime.now() - pidcreated
                        PMList[key]["uptime"] =diff
                    except Exception:
                        import traceback
                        print (traceback.format_exc())
                        PMList[key]["uptime"] = -1
                else:
                    PMList[key]["status"] = "stop"
                    PMList[key]["hwnd"] =  None
                    PMList[key]["mem_usage"] = 0
                    PMList[key]["cpu_usage"] = 0
                    PMList[key]["uptime"] = 0

        def runTask(task, schedule, cron):
            myProcess = None
        
            def sustenance_task():
                if task["bStop"] == True:
                    return
                HWnd = win32gui.FindWindow(None, task["name"])
                if HWnd == 0:
                    startProcess(task)

            def restart_task():
                if task["bStop"] == True:
                    return
                stopProcess(task)
                startProcess(task)

            if task["job"] == "sustenance":
                cron.add(schedule, sustenance_task)
            elif task["job"] == "restart":
                cron.add(schedule, restart_task)
            else:
                print(" Incorrect job type = ", task["job"])

        # loading config file
        try:
            with open('config.json') as config_file:
                config = json.load( config_file )
                if len(config['task']) <=0:
                    print(" There is no Task.")
        except Exception as e:
            print("ERROR : You need \"config.json\" file!", e)
            sys.exit(0)

        cron = Cron()
        for cfg_task in config['task']:
            key = getPMKey(cfg_task)
            app_path = cfg_task["path"]
            app =cfg_task["path"] + "/" + cfg_task["file"]
            PMList[key] = {"key" : key, "app_path" : app_path, "app":app, "proc_name":cfg_task["file"],"buttons":cfg_task["buttons"], "job":cfg_task["job"], "hwnd": None, "pid": None, "name": cfg_task["title"],"bStop": False, "status": "stop", "cpu_usage": -1, "mem_usage": -1, "uptime": -1, "restart": 0}
            runTask(PMList[key],cfg_task["schedule"]["cron"], cron)
        # add task for updating task status
        task_update()
        cron.add("* * * * *", task_update)
        # console interface
        cmdThread = _thread.start_new_thread(command_thread, ())
        cron.run()
    except KeyboardInterrupt:
        print(" BYE!! ")
        sys.exit(0)
