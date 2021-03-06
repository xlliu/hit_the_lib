# -*- coding: utf-8 -*-
from __future__ import division

import gevent
import gevent.monkey

gevent.monkey.patch_all(socket=True, dns=True, time=True, select=True, thread=False, os=True, ssl=True, httplib=False,
                        subprocess=True, sys=False, aggressive=True, Event=False,
                        builtins=True, signal=True)
# gevent.monkey.patch_select()
# gevent.monkey.patch_socket()

import sys
import multiprocessing

reload(sys)
sys.setdefaultencoding('utf-8')

import pandas as pd
import requests
import math
import time

from target_site.putong import *

import copy_reg
import types


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)


copy_reg.pickle(types.MethodType, _pickle_method)


class HitTheLibrary(object):
    """测试号码工具模块
    def BarcodeSearcher(self, x):
        return x*x

    def resultCollector(self, result):
        self.test_xlliu.append(result)

    def manageWork(self):
        pool = multiprocessing.Pool(processes=1)
        for pag in range(10):
            pool.apply_async(self.BarcodeSearcher, args=(pag,),
                             callback=self.resultCollector)
        pool.close()
        pool.join()

        print self.test_xlliu

    对电话号码进行测试，
    """

    def __init__(self):
        super(HitTheLibrary, self).__init__()

        # PROXY_HOST = 'proxy.dianhua.cn'
        # PROXY_HOST = "192.168.20.199"
        self._all_tasks = []
        PROXY_HOST = "120.92.137.32"
        PROXIES = {'http': 'http://{}:8080'.format(PROXY_HOST),
                   'https': 'https://{}:8080'.format(PROXY_HOST)}

        self.session = requests.session()
        # self.session.proxies = PROXIES
        self._sites = [
            HuaLi(),
            YeShouPai(),
            RoseOnly(),
            ErShouChe(),
            GongPengJia()
        ]
        self._sites_table_columns = ["huali", "yeshoupai", "roseonly", "ershouche", "gongpingjia"]
        self._step = 5
        self._sleep = 1

        self.__run()
        # self.manageWork()

    def __core(self, tel_num):
        # gevent.sleep(4)
        # print('Running in tel_num: %s' %tel_num)
        tasks = [gevent.spawn(getattr(site, "run"), tel_num, self.session, self._TABLE) for site in self._sites]
        success_tasks_call_sites = gevent.joinall(tasks, timeout=15, raise_error=False)
        # diff = set(tasks).difference(set(success_tasks_call_sites))
        # if diff:
        #     print "==============================================="
        #     gevent.joinall(tasks, timeout=10, raise_error=False)
        # for greenlet in tasks:
        #     print "结束停止切没有异常: %s" %(greenlet.successful() if greenlet.successful() else False)
        #     print "结束停止: %s" %(greenlet.ready() if greenlet.ready() else False)
        #     print "没被捕获的异常: %s" %greenlet.exception
        # print tel_num, len(success_tasks)
        # print('Explicit context switch to foo again')

    def __table(self, phone_numbers):
        pn_list = map(lambda x: x.tolist()[0], phone_numbers.values)
        data = pd.DataFrame(index=pn_list, columns=self._sites_table_columns)
        print "总条目数: %d" % len(data.index)
        return data

    def return_params(self, dataframe):
        return dataframe

    def __generator_tasks(self, df):
        tasks = [gevent.spawn(self.__core, str(tel_num[0])) for tel_num in df]
        self._all_tasks.extend(tasks)
        gevent.joinall(tasks, raise_error=False)

    def __run(self):
        with pd.ExcelFile('dev.xlsx') as xls:
            df1 = pd.read_excel(xls, '10w')
        column = u'手机号码'

        # 测试截取30
        df1 = df1.loc[:5, [column]]
        self._TABLE = self.__table(df1)
        time_num = int(math.ceil(len(df1.index) / self._step))
        _pool = multiprocessing.Pool(processes=3)
        for n in xrange(time_num):
            print str(n * self._step), str((n + 1) * self._step - 1)
            df2 = df1.loc[n * self._step:(n + 1) * self._step - 1, [column]].values
            print "===================GoGoGo: %d=====================" % n
            _pool.apply_async(self.return_params, args=(df2,), callback=self.__generator_tasks)
            time.sleep(self._sleep)
        _pool.close()
        # _pool.join()
        nat = self._all_tasks
        print "all_tasks: %d" % len(nat)
        # 轮询
        n = 0
        while True:
            c = 0
            for x in self._all_tasks:
                cc = 1 if x.ready() else 0
                c += cc
            print "读秒次数: %d 已完成: %d/总数: %d " % (n, c, len(nat))
            if c == len(nat):
                time.sleep(1)
                self._TABLE.to_csv(path_or_buf="./data.csv", chunksize=5000)
                break
            time.sleep(1)
            n += 1
        print '==============END==============='


if __name__ == '__main__':
    #   pool = Pool(processes=1)
    # Start a worker processes.
    #   result = pool.apply_async(f, [10])
    HitTheLibrary()
