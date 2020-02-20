import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing
bind = '127.0.0.1:9000'  # 绑定ip和端口号
backlog = 512  # 监听队列
chdir = '/mnt/h/trian/whlrest'  # gunicorn要切换到的目的工作目录
timeout = 30  # 超时
worker_class = 'sync'  # 使用gevent模式，还可以使用sync 模式，默认的是sync模式

# workers = multiprocessing.cpu_count() * 2 + 1  # 进程数
workers = 1
threads = 1  # 指定每个进程开启的线程数
loglevel = 'error'  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = "/home/fgf/log/gunicorn_access.log"  # 访问日志文件
errorlog = "/home/fgf/log/gunicorn_error.log"
