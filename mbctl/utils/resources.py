from importlib_resources import files
import shutil
import os

def copy_resdir_content_to_target_folder(src_resource_package_name, dst_folder):
    # 将一个资源目录的所有内容递归复制到目标文件夹
    os.makedirs(dst_folder, exist_ok=True)
    src_resource = files(src_resource_package_name)
    for entry in src_resource.iterdir():
        target_path = os.path.join(dst_folder, entry.name)
        if entry.is_dir():
            copy_resdir_content_to_target_folder(entry, target_path)
        else:
            with entry.open('rb') as fsrc, open(target_path, 'wb') as fdst:
                shutil.copyfileobj(fsrc, fdst)
        print(f'Copied {entry} to {target_path}')


def copy_resdir_file_to_target_file(src_resource_package_name, src_resource_name, dst_file_path):
    # 将资源文件复制到目标文件，创建必要的目录。
    os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
    src_resource = files(src_resource_package_name).joinpath(src_resource_name)
    with src_resource.open('rb') as fsrc, open(dst_file_path, 'wb') as fdst:
        shutil.copyfileobj(fsrc, fdst)
    print(f'Copied {src_resource} to {dst_file_path}')


def get_file_content_as_str(resource_package_name, resource_name):
    # 以字符串形式获取资源文件内容
    resource = files(resource_package_name).joinpath(resource_name)
    with resource.open('r', encoding='utf-8') as f:
        return f.read()


