# coding=utf-8
__author__ = 'Xuxh'


import os
try:
    import unittest2 as unittest
except(ImportError):
    import unittest
from appium import webdriver
from time import sleep
from datetime import datetime


from TestTasks.publiclib import configuration
from TestTasks.publiclib import myglobal
from TestTasks.publiclib import library
from TestTasks.publiclib import filterlogcat as dumplog
from TestTasks.publiclib import uiaction


# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

CONFIG = configuration.configuration()
CONFIG.fileConfig(myglobal.CONFIGURATONINI)

TEMPPATH = r'../temp/'


def init_device_environment(dname,dport,logfname):

    global DEVICENAME, PORT, LOGGER,IMAGEPATH

    DEVICENAME = dname

    PORT = dport
    LOGGER = library.create_logger(logfname)
    IMAGEPATH = os.path.join(os.path.dirname(logfname),'image')
    if not os.path.isdir(IMAGEPATH):
        os.makedirs(IMAGEPATH)

    library.init_app(DEVICENAME)


class TestScheduleTasks(unittest.TestCase):

    # @classmethod
    # def setUpClass(self):
    #
    #     desired_caps = {}
    #     desired_caps['platformName'] = CONFIG.getValue(DEVICENAME,'platformName')
    #     desired_caps['platformVersion'] = CONFIG.getValue(DEVICENAME,'platformVersion')
    #     desired_caps['deviceName'] = DEVICENAME
    #     desired_caps['app'] = PATH('../apps/' + CONFIG.getValue(DEVICENAME,'app'))
    #     #desired_caps['appPackage'] = CONFIG.getValue(DEVICENAME,'appPackage')
    #     #desired_caps['appActivity'] = CONFIG.getValue(DEVICENAME,'appActivity')
    #     self.driver = webdriver.Remote('http://127.0.0.1:' + str(PORT) +'/wd/hub',desired_caps)

    # @classmethod
    # def tearDownClass(self):
    #     self.driver.quit()

    def setUp(self):

        self.desired_caps = {}
        self.desired_caps['platformName'] = CONFIG.getValue(DEVICENAME,'platformName')
        self.desired_caps['platformVersion'] = CONFIG.getValue(DEVICENAME,'platformVersion')
        self.desired_caps['deviceName'] = DEVICENAME
        #desired_caps['app'] = PATH('../apps/' + CONFIG.getValue(DEVICENAME,'app'))
        self.desired_caps['appPackage'] = CONFIG.getValue(DEVICENAME,'appPackage')
        self.desired_caps['appActivity'] = CONFIG.getValue(DEVICENAME,'appActivity')
        self.driver= webdriver.Remote('http://127.0.0.1:' + str(PORT) +'/wd/hub',self.desired_caps)
        sleep(2)
        
        self.log_name = None
        self.log_path = None
        self.log_object = None
        self.log_reader = None
        LOGGER.debug('Start testing')

    def tearDown(self):

        self.driver.close_app()
        self.driver.quit()
        sleep(2)

    def exec_ui_action(self,ele_tag,act='click'):

        result = False
        uiconfig = configuration.configuration()
        uiconfig.fileConfig(myglobal.CONFIGUI)
        # get config value and create element direct
        value =uiconfig.getValue(DEVICENAME,ele_tag)
        uia = uiaction.UIAction(DEVICENAME,self.driver)
        element = uia.find_element(value)

        if act == 'click' and ( not element is None):
            uia.find_element(value).click()
            sleep(4)
            result = True

        return result
    #点击跳过后，点击启动按钮，上滑解锁，授权
    def log_in_application(self):

        try:
            self.exec_ui_action('GuidePag_Persimmion_Setting')
            sleep(6)
            # maybe popup window is exist, contain text u'跳过'
            self.exec_ui_action('GuidePage_Skip')
            # if don't log in at first, will directly access to main screen, so try to do twice click
            result = self.exec_ui_action('GuidePage_StartUp')
            if not result:
               self.exec_ui_action('GuidePage_StartUp_Alias')
            self.exec_ui_action('GuidePage_Info')
        except Exception,ex:
            print ex

        # swipe screen
        height = self.driver.get_window_size()['height']
        width = self.driver.get_window_size()['width']
        self.driver.swipe(int(width/2),int(height/2),int(width/2), int(height/4), 1000)
        sleep(2)

        # For some devices, maybe popup permission window
        for i in range(5):
            result = self.exec_ui_action('GuidePage_Permission')
            if result:
                break

        # wait for main window refresh
        sleep(5)

    # def log_in_application(self):
    #
    #     # maybe popup window is exist, contain text u'跳过'
    #     try:
    #         self.driver.find_element_by_id('com.vlife:id/btn_skip').click()
    #         sleep(1)
    #     except Exception,ex:
    #         print ex
    #
    #     # if don't log in at first, will directly access to main screen, so try to do twice click
    #     try:
    #         #self.driver.start_activity(CONFIG.getValue(DEVICENAME,'appPackage'),'com.vlife/.SplashActivity')
    #         self.driver.find_element_by_id('com.vlife:id/btn_login').click()
    #         sleep(3)
    #     except Exception,ex:
    #         try:
    #             self.driver.find_element_by_id('com.vlife:id/guide_go_text').click()
    #             sleep(3)
    #         except Exception,ex:
    #             LOGGER.debug(ex)
    #     try:
    #         self.driver.find_element_by_id('com.vlife:id/guide_info').click()
    #         sleep(3)
    #     except Exception,ex:
    #         LOGGER.debug(ex)
    #
    #     height = self.driver.get_window_size()['height']
    #     width = self.driver.get_window_size()['width']
    #     if int(height) > 2000:
    #         self.driver.swipe(int(width/2),int(height/2+300),int(width/2), int(height/2-500), 1000)
    #     else:
    #         self.driver.swipe(int(width/2),int(height/2+200),int(width/2), int(height/2-300), 500)
    #     sleep(2)
    #     # For some devices, maybe popup permission window
    #     for i in range(5):
    #         try:
    #             self.driver.find_element_by_id('com.android.packageinstaller:id/permission_allow_button').click()
    #             sleep(1)
    #         except Exception,ex:
    #             print ex
    #             break
    #     sleep(5)

    def dump_log_start(self):

        self.log_name =''.join([DEVICENAME,'_',datetime.now().strftime('%Y%m%d%H%M'), 'log.txt'])
        self.log_path = PATH(TEMPPATH+self.log_name)
        self.log_object = open(self.log_path, 'w+')
        self.log_reader = dumplog.DumpLogcatFileReader(self.log_object,DEVICENAME)
        self.log_reader.start()

    def dump_log_stop(self):

        self.log_reader.stop()
        self.log_object.close()
    #首次启动app后，抓取log验证是否正常发送并接收注册协议包
    def test_01_log_in(self):

        self.dump_log_start()
        self.log_in_application()
        #temp = unittest.TestCase.id()
        base_name = '01_log_in' + '.png'
        img_name = os.path.join(IMAGEPATH,base_name)
        self.driver.get_screenshot_as_file(img_name)
        self.dump_log_stop()
        keyword = 'jabber:iq:register'
        result = dumplog.keywordFilter(self.log_path,DEVICENAME,keyword,LOGGER)
        self.assertEqual(True,result)
    #触发定期联网后，关闭再打开app，查看Uid是否相同
    def test_02_network_connection_update(self):
        sleep(6)
        self.log_in_application()
        orig_uid = library.get_userid_from_file(DEVICENAME)
        LOGGER.debug('Get user id from userinfo.xml:'+orig_uid)

        self.driver.close_app()
        sleep(2)
        self.dump_log_start()
        library.wifi_operation(DEVICENAME,'OFF')
        sleep(2)
        library.update_android_time(DEVICENAME,0)
        sleep(16)
        library.wifi_operation(DEVICENAME,'ON')
        sleep(3)
        self.driver.start_activity(self.desired_caps['appPackage'],self.desired_caps['appActivity'])
        self.log_in_application()
        self.dump_log_stop()
        cur_uid = dumplog.getUserID(self.log_path,DEVICENAME,LOGGER)
        self.assertEqual(orig_uid,cur_uid)
    #清除app缓存数据后，再启动app，查看uid是否发生变化
    def test_03_clearcache_uid_update(self):

        sleep(5)
        orig_uid = library.get_userid_from_file(DEVICENAME)
        LOGGER.debug('Get user id from userinfo.xml:'+orig_uid)

        # clear cache and uninstall
        library.app_operation(DEVICENAME,'CLEAR')
        # library.app_operation(DEVICENAME,'UNINSTALL')
        # sleep(2)
        # library.app_operation(DEVICENAME,'INSTALL',self.app_path)
        # sleep(10)

        # install and read file
        library.app_operation(DEVICENAME,'LAUNCH')
        sleep(10)
        self.log_in_application()
        sleep(5)
        cur_uid = library.get_userid_from_file(DEVICENAME)
        LOGGER.debug('Get user id from userinfo.xml:'+cur_uid)
        if cur_uid != '':
            self.assertNotEqual(orig_uid,cur_uid)
        else:
            self.assertIsNot(cur_uid,'')


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestScheduleTasks)
    unittest.TextTestRunner(verbosity=2).run(suite)


