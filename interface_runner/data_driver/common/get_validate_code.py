#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import cv2
import time
import numpy as np
import pytesseract
from PIL import Image
from io import BytesIO
from collections import defaultdict
from interface_runner.data_driver.common.base import MyRequests

__author__ = 'weisha'
__date__ = '2020-09-28'

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(ROOT_DIR)
IMAGE_PATH = os.path.join(ROOT_DIR, "/screenshots/")


# 运营后台获取图形验证码
class GetGraphValidateCode:
    # 获取图片中像素点数量最多的像素
    def get_threshold(self, image):
        pixel_dict = defaultdict(int)
        # 像素及该像素出现次数的字典
        rows, cols = image.size
        for i in range(rows):
            for j in range(cols):
                pixel = image.getpixel((i, j))
                pixel_dict[pixel] += 1

        count_max = max(pixel_dict.values())  # 获取像素出现出多的次数
        pixel_dict_reverse = {v: k for k, v in pixel_dict.items()}
        threshold = pixel_dict_reverse[count_max]  # 获取出现次数最多的像素点
        return threshold

    # 按照阈值进行二值化处理
    # threshold: 像素阈值
    def get_bin_table(self, threshold):
        # 获取灰度转二值的映射table
        table = []
        for i in range(256):
            rate = 0.1  # 在threshold的适当范围内进行处理
            if threshold * (1 - rate) <= i <= threshold * (1 + rate):
                table.append(1)
            else:
                table.append(0)
        return table

    # 去掉二值化处理后的图片中的噪声点
    def cut_noise(self, image):
        rows, cols = image.size  # 图片的宽度和高度
        change_pos = []  # 记录噪声点位置

        # 遍历图片中的每个点，除掉边缘
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                # pixel_set用来记录该店附近的黑色像素的数量
                pixel_set = []
                # 取该点的邻域为以该点为中心的九宫格
                for m in range(i - 1, i + 2):
                    for n in range(j - 1, j + 2):
                        if image.getpixel((m, n)) != 1:  # 1为白色,0位黑色
                            pixel_set.append(image.getpixel((m, n)))

                # 如果该位置的九宫内的黑色数量小于等于4，则判断为噪声
                if len(pixel_set) <= 4:
                    change_pos.append((i, j))

        # 对相应位置进行像素修改，将噪声处的像素置为1（白色）
        for pos in change_pos:
            image.putpixel(pos, 1)

        return image  # 返回修改后的图片

    def get_code(self, image):
        # -*- coding: UTF-8 -*-、
        if str(type(image)) == "<class 'requests.models.Response'>":
            image = Image.open(BytesIO(image.content))
        imgry = image.convert('L')

        # 获取图片中的出现次数最多的像素，即为该图片的背景
        max_pixel = self.get_threshold(imgry)

        # 将图片进行二值化处理
        # 注意，是否使用二值化要看具体情况，有些图片二值化之后，可能关键信息会丢失，反而识别不出来
        table = self.get_bin_table(threshold=max_pixel)
        out = imgry.point(table, '1')
        # 去掉图片中的噪声（孤立点）
        out = self.cut_noise(out)
        # 识别图片中的数字和字母
        text = pytesseract.image_to_string(out)  # ,config='--psm 6'.strip()
        code = re.sub("\W", "", text)
        return code


class GetSliderValidateCode:
    def save_image_screen_shot(self, driver, xpath_value, image_name):
        # 获取验证码的坐标
        time.sleep(5)
        imgelement = driver.get_element('xpath', xpath_value)
        # 截屏
        driver.get_windows_img(image_name)
        # 获取验证码x,y轴坐标
        location = imgelement.location
        # 获取验证码的长宽
        size = imgelement.size
        # 获取截取的位置坐标
        rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                  int(location['y'] + size['height']))
        # 打开截屏图片
        i = Image.open(IMAGE_PATH + image_name)
        # 使用Image的crop函数，从截图中再次截取需要的区域
        result = i.crop(rangle)
        size = result.size
        return size[0]

    def save_code_image(self, driver, target_file_name, template_file_name):
        target = driver.get_element('class_name', 'yidun_bg-img')
        template = driver.get_element('class_name', 'yidun_jigsaw')

        target_link = target.get_attribute('src')
        template_link = template.get_attribute('src')
        target_img = Image.open(BytesIO(MyRequests().get(url=target_link, data=None, headers=None).content))
        template_img = Image.open(BytesIO(MyRequests().get(template_link, data=None, headers=None).content))
        target_img.save(IMAGE_PATH + target_file_name)
        template_img.save(IMAGE_PATH + template_file_name)
        # local_img = Image.open(ROOT_DIR + '/screenshots/' + target_file_name)
        size_loc = target_img.size
        return size_loc[0]
        # print(size_loc)
        # self.zoom = 256 / int(size_loc[0])
        # print('zoom:',self.zoom)

    # def get_compress(self,image,yidun_image):
    #     image_size = image.size
    #     yidun_image_size = yidun_image.size
    #     compress = int(image_size[0]) / int(yidun_image_size[0])
    #     return compress

    def get_tracks(self, distance):
        distance += 20
        v = 0
        t = 0.2
        forward_tracks = []
        current = 0
        mid = distance * 3 / 5  # 减速阀值
        while current < distance:
            if current < mid:
                a = 2  # 加速度为+2
            else:
                a = -3  # 加速度-3
            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            current += s
            forward_tracks.append(round(s))
        back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}

    def match(self, target, template):
        img_rgb = cv2.imread(IMAGE_PATH + target)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(IMAGE_PATH + template, 0)

        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        run = 1

        # 使用二分法查找阈值的精确值
        L = 0
        R = 1
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            if threshold < 0:
                return None
            loc = np.where(res >= threshold)
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        return loc[1][0]

    def crack_slider(self, driver, tracks):
        slider = driver.get_element('class_name', 'yidun_slider')
        driver.actionchains_hold(slider)
        for track in tracks['forward_tracks']:
            driver.actionchains_move(xoffset=track, yoffset=0)
        time.sleep(0.5)
        for back_tracks in tracks['back_tracks']:
            driver.actionchains_move(xoffset=back_tracks, yoffset=0)
        driver.actionchains_move(xoffset=-4, yoffset=0)
        driver.actionchains_move(xoffset=4, yoffset=0)
        time.sleep(0.5)
        driver.actionchains_release()
