import os
import shutil

# 源目录和目标目录
src_dir = './music_temp'
dst_dir = './music'

# 确保目标目录存在
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

# 遍历源目录下的所有文件
for filename in os.listdir(src_dir):
    # 删除文件名中的空格
    new_filename = filename.replace(' ', '')
    # 构建完整的文件路径
    src_file_path = os.path.join(src_dir, filename)
    dst_file_path = os.path.join(dst_dir, new_filename)

    # 检查是否为文件
    if os.path.isfile(src_file_path):
        # 复制文件到目标目录
        shutil.copy(src_file_path, dst_file_path)
        print(f'Copied "{src_file_path}" to "{dst_file_path}"')

print("All files have been copied with spaces removed from their names.")
