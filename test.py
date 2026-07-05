from mimetypes import init

from Operation import Operation
import cv2
import numpy as np


class test:
    def __init__(self):
        self.operation = Operation()

    def get_text_location(self, target_text: str, pic_name):  # 返回指定文字在图片中的位置,类型为二维数组[[][]]
        match_res = []
        img_data = self.operation.ocr.predict(f'pic/{pic_name}.png')[0]
        # print(f'img_data={img_data}')
        texts = img_data["rec_texts"]
        polys = img_data["rec_polys"]
        scores = img_data["rec_scores"]

        for text, poly, score in zip(texts, polys, scores):
            if target_text in text:
                match_res.append((text, score, poly))

        return match_res[0][2]

    def check_time(self):
        # 裁剪"后开奖"文字所在区域的截图，用于后续定位该文字在屏幕上的位置
        self.operation.crop_pic(920, 1390, 1015, 1580, "fudai_Content", "HouKaiJiang_Location")
        HouKaiJiang_Relative_location = self.operation.get_text_location("后开奖", "HouKaiJiang_Location")
        print(f"HouKaiJiang_Relative_location={HouKaiJiang_Relative_location}")
        print(f"HouKaiJiang_Relative_location[1,1]={HouKaiJiang_Relative_location[1, 1]}")
        HouKaiJiang_location = [
            920, 1390 + HouKaiJiang_Relative_location[0, 1], 1015, 1390 + HouKaiJiang_Relative_location[-1, 1]]
        print(HouKaiJiang_location)  # [ 541 1429]

        # self.crop_pic(770, 1480, 1015, 1520, "fudai_Content", "time-pic")  # 获取时间截图
        # result = self.ocr.predict('pic/time-pic.png')  # 识别图像
        # time_hour = int(self.extract_ocr_content(result)[0:2])
        # time_min = int(self.extract_ocr_content(result)[2:4])
        # time_second = int(self.extract_ocr_content(result)[4:6])
        # time_fudai = time_hour * 3600 + time_min * 60 + time_second
        # return time_fudai  # 返回剩余的福袋开奖时间


if __name__ == '__main__':
    test1 = test()
    test1.check_time()
