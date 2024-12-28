import os
import pymssql

# 数据库连接信息
server = 'localhost:1433'  # 替换为你的服务器名称或IP地址
database = 'python_final'
username = 'sa'
password = 'yyk200412='

# 文件夹路径
path = './music'

# 连接到数据库
conn = pymssql.connect(server, username, password, database)
cursor = conn.cursor()

# 遍历文件夹下的所有文件
for filename in os.listdir(path):
    # 检查是否为文件
    if os.path.isfile(os.path.join(path, filename)):
        # 分割文件名和扩展名
        name, ext = os.path.splitext(filename)
        # 检查文件名是否包含'-'
        if '-' in name:
            # 分割歌手和歌曲名
            artist_name, title = name.split('-', 1)
            # 插入数据库
            cursor.execute("""
                INSERT INTO music (title, artist_name)
                VALUES (%s, %s)
            """, (title.strip(), artist_name.strip()))

# 提交事务
conn.commit()

# 关闭连接
cursor.close()
conn.close()

print("All files have been processed and data inserted into the database.")
