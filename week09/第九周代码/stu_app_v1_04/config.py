"""数据库连接配置。

所有模块统一从此处读取配置，避免在多处硬编码凭据。
可通过环境变量覆盖默认值：

  export DB_HOST=192.168.1.100
  export DB_USER=root
  export DB_PASSWORD=secret
  export DB_DATABASE=dbsample
"""

import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_DATABASE', 'dbsample'),
    'user': os.getenv('DB_USER', 'dylan'),
    'password': os.getenv('DB_PASSWORD', 'P@ssw0rd'),
    'charset': 'gb18030',
    'use_unicode': True,
}
