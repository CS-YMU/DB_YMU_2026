"""数据库连接配置 —— 中间件的数据源配置层

本模块演示数据库应用系统中"中间件"概念的第一层：连接配置。
应用程序不直接硬编码数据库连接信息，而是通过配置字典统一管理，
支持环境变量覆盖，便于在不同环境（开发/测试/生产）间切换。

参考：week09/stu_app_v1_04/config.py 的配置模式
"""
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'dylan'),
    'password': os.getenv('DB_PASSWORD', 'P@ssw0rd'),
    'database': os.getenv('DB_DATABASE', 'DB06'),
    'charset': 'utf8mb4',
    'use_unicode': True,
}
