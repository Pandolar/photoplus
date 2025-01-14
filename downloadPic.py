# python3
# -- coding: utf-8 --
# -------------------------------
# @Author : Terry
# @File : down.py
# @Time : 2024/2/5 10:34
# -------------------------------
import os
import time
import requests
import hashlib
from operator import itemgetter

# 常量
SALT = 'laxiaoheiwu'
DEFAULT_COUNT = 9999

# 定义请求的参数
BASE_PARAMS = {
    'isNew': False,
    'ppSign': 'live',
    'picUpIndex': '',
}

# 对象按键排序
def obj_key_sort(obj):
    sorted_obj = sorted(obj.items(), key=itemgetter(0))
    sorted_obj_dict = {k: str(v) for k, v in sorted_obj if v is not None}
    return '&'.join([f"{k}={v}" for k, v in sorted_obj_dict.items()])

# MD5加密
def md5(value):
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()

# 获取所有图片
def get_all_images(activity_no, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    timestamp = int(time.time() * 1000)
    params = {
        **BASE_PARAMS,
        'activityNo': activity_no,
        'count': DEFAULT_COUNT,
        'page': 1,
        '_t': timestamp,
    }

    # 生成签名
    sorted_params = obj_key_sort(params)
    sign = md5(sorted_params + SALT)
    params['_s'] = sign

    try:
        response = requests.get('https://live.photoplus.cn/pic/pics', params=params)
        response.raise_for_status()  # 如果响应状态不是200，就主动抛出异常
    except requests.RequestException as err:
        print(f"请求失败: {err}")
        return

    try:
        result = response.json()
    except ValueError:
        print("响应内容不是有效的JSON格式")
        return

    if 'result' not in result:
        print("未找到图片数据")
        return

    total_pics = result['result']['pics_total']
    photographer = result['result']['pics_array'][0]['camer']

    print(f"开始下载图片，共 {total_pics} 张，摄影师: {photographer}")

    downloaded_count = 0
    for pic in result['result']['pics_array']:
        image_url = "https:" + pic['origin_img']
        image_name = pic['pic_name']
        if download_image(image_url, save_path, image_name):
            downloaded_count += 1
            print(f"已下载第 {downloaded_count} 张图片: {image_name}")

    print(f"下载完成，共下载 {downloaded_count} 张图片")

# 下载单张图片
def download_image(url, save_path, file_name):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 如果响应状态不是200，就主动抛出异常
    except requests.RequestException as err:
        print(f"下载失败: {err}")
        return False

    time.sleep(2)  # 防止请求过于频繁
    with open(os.path.join(save_path, file_name), 'wb') as file:
        file.write(response.content)
    return True

# 主函数
def main():
    activity_no = input("请输入 photoplus 活动编号 (例如: 87654321): ")
    if not activity_no.isnumeric():
        print("活动编号输入错误，请输入数字")
        return

    save_path = input("请输入图片保存路径 (例如: ../Pics/): ")
    if not save_path:
        print("保存路径不能为空")
        return

    get_all_images(int(activity_no), save_path)

if __name__ == "__main__":
    main()
