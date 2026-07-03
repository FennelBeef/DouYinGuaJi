import os
import time

import cv2
import numpy as np
from PIL import Image
from adbutils import adb, AdbError
from paddleocr import PaddleOCR


class Operation:
    def __init__(self):
        self.d = None
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False)

    def get_device(self):
        try:
            d = adb.device()  # 获取设备
        except AdbError:
            print("Error: 尚未连接手机")
        else:
            print("设备连接成功，设备序列号：" + d.serial)  # 输出设备序列号
            self.d = d
            return d

    def get_Screenshot(self, d, pic_name):
        screenshot = d.screenshot()
        try:
            screenshot.save(f"pic/{pic_name}.png")
        except IOError:
            print("Error: 没有找到文件夹，正在创建文件夹")
            os.mkdir("pic")  # 创建文件夹
            screenshot.save(f"pic/{pic_name}.png")
        # else:
        #     # print("存储完毕")
        return screenshot

    def multi_scale_template_matching(self, main_image_path, template_path, threshold=0.8,
                                      scales=[0.5, 0.75, 1.0, 1.25, 1.5]):
        """
        多尺度模板匹配，适用于模板大小可能变化的情况

        参数:
            main_image_path: 主图片路径
            template_path: 模板图片路径
            threshold: 匹配阈值
            scales: 缩放比例列表

        返回:
            bool: 是否找到匹配
            list: 匹配位置的坐标列表
        """
        # 读取图片
        main_img = cv2.imread(main_image_path)
        template = cv2.imread(template_path)
        # cv2.imshow('main_img', main_img)
        # cv2.imshow('template', template)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        if main_img is None or template is None:
            print("无法读取图片")
            return False, []

        # 获取模板尺寸
        template_h, template_w = template.shape[:2]

        found = None
        found_locations = []

        # 在不同尺度下进行匹配
        for scale in scales:
            # 调整主图大小
            resized = cv2.resize(main_img, (int(main_img.shape[1] * scale), int(main_img.shape[0] * scale)))
            r = main_img.shape[1] / float(resized.shape[1])

            # 如果调整后的图像小于模板，则跳过
            if resized.shape[0] < template_h or resized.shape[1] < template_w:
                continue

            # 进行模板匹配
            result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 如果找到更好的匹配，更新结果
            if found is None or max_val > found[0]:
                found = (max_val, max_loc, r)

        # 如果找到匹配且置信度高于阈值
        if found is not None and found[0] >= threshold:
            max_val, max_loc, r = found
            start_x = int(max_loc[0] * r)
            start_y = int(max_loc[1] * r)
            end_x = int((max_loc[0] + template_w) * r)
            end_y = int((max_loc[1] + template_h) * r)

            found_locations.append((start_x, start_y, end_x, end_y))

            return True, found_locations

        return False, []

    def click_locations(self, locations, d):
        x = (locations[0][0] + locations[0][2]) / 2
        y = (locations[0][1] + locations[0][3]) / 2
        d.click(x, y)
        time.sleep(3)  # 对应点击延迟

    def check_time(self, d):
        location = self.get_text_location("后开奖", "fudai_Content")
        print(location)

        print(location[0]) #[ 541 1429]

        self.crop_pic(770, 1480, 1015, 1520, "fudai_Content", "time-pic")  # 获取时间截图
        result = self.ocr.predict('pic/time-pic.png')  # 识别图像
        time_hour = int(self.extract_ocr_content(result)[0:2])
        time_min = int(self.extract_ocr_content(result)[2:4])
        time_second = int(self.extract_ocr_content(result)[4:6])
        time_fudai = time_hour * 3600 + time_min * 60 + time_second
        return time_fudai  # 返回剩余的福袋开奖时间

    def check_neirong(self, d):
        self.crop_pic(356, 1561, 1015, 1690, "fudai_Content", "fudai_neirong-pic")
        result = self.ocr.predict('pic/fudai_neirong-pic.png')  # 识别图像
        result = self.extract_ocr_content(result)
        return result

    def crop_pic(self, x_top=1, y_top=1, x_bottom=2, y_bottom=2, cut_pic='', new_cut_pic_name=''):
        path = os.path.dirname(__file__) + '/pic'
        pic1_path = path + '/' + cut_pic + '.png'
        pic = Image.open(pic1_path)
        pic.crop((x_top, y_top, x_bottom, y_bottom)).save(f"pic/{new_cut_pic_name}.png")

    def extract_ocr_content(self, content=[]):
        """从OCR识别结果中提取文本内容并拼接成完整字符串"""
        if not content:
            return ""
        # 获取第一个OCR结果项（通常处理单页文档）
        ocr_item = content[0]
        # 检查数据结构并提取文本
        if 'rec_texts' in ocr_item:
            # 新数据结构：直接从rec_texts字段获取文本
            extracted_content = ocr_item['rec_texts']
        else:
            # 旧数据结构：遍历结果项获取文本
            extracted_content = []
            for item in ocr_item:
                if isinstance(item, list) and len(item) > 1:
                    # 假设item的结构为 [位置信息, (识别内容, 置信度)]
                    extracted_content.append(item[1][0] if isinstance(item[1], (list, tuple)) else "")
        # 过滤空值并拼接
        contains = ''.join(text for text in extracted_content if text)
        return contains

    def check_number_of_tasks(self):
        self.crop_pic(910, 2030, 1015, 2125, "fudai_Content", "number_tasks")
        result = self.ocr.predict('pic/number_tasks.png')  # 识别图像
        text = self.extract_ocr_content(result)
        target = "未达成"
        count = text.count(target)
        return count

    def click_choujiang(self):
        choujiang_location = [(125, 2175, 960, 2300)]
        num = self.check_number_of_tasks()
        if num == 1:
            print(f"当前直播间有{num}个任务")
            self.crop_pic(choujiang_location[0][0], choujiang_location[0][1], choujiang_location[0][2],
                          choujiang_location[0][3],
                          "fudai_Content", "tasks_Content")
            result = self.ocr.predict('pic/tasks_Content.png')  # 识别图像
            text = self.extract_ocr_content(result)
            if "一键发表评论" in text:
                print(f"福袋任务：{text}")
                self.click_locations(choujiang_location, self.d)
                return True
            else:
                return False

        if num == 2:
            print(f"当前直播间有{num}个任务")
            pass
        return None

    def convert_to_grayscale(self, input_path):
        """
        将彩色图片转换为灰度图
        """
        path = os.path.dirname(__file__) + '/pic'
        input_path = path + '/' + input_path + '.png'
        try:
            # 打开图片
            img = Image.open(input_path)

            # 转换为灰度图
            gray_img = img.convert('L')

            # 保存灰度图
            gray_img.save(input_path)
            return gray_img
        except Exception as e:
            print(f"转换失败: {e}")
            return None

    def get_Screenshot_WinResult(self, d):
        self.get_Screenshot(d, "WinResult")  # 获取手机截图
        self.crop_pic(255, 1300, 830, 1360, "WinResult", "WinResult_cut_pic")
        self.convert_to_grayscale("WinResult_cut_pic")

    def check_WinResult(self, d):
        self.get_Screenshot_WinResult(d)
        result = self.ocr.predict('pic/WinResult_cut_pic.png')  # 识别图像
        result = self.extract_ocr_content(result)
        return result

    def get_text_location(self, target_text: str, pic_name):  # 返回指定文字在图片中的位置,类型为二维数组[[][]]
        match_res = []
        img_data = self.ocr.predict(f'pic/{pic_name}.png')[0]
        # print(f'img_data={img_data}')
        texts = img_data["rec_texts"]
        polys = img_data["rec_polys"]
        scores = img_data["rec_scores"]

        for text, poly, score in zip(texts, polys, scores):
            if target_text in text:
                match_res.append((text, score, poly))

        return match_res[0][2]
