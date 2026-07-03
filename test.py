from Operation import Operation
import cv2
import numpy as np


def get_text_location(target_text: str, pic_name):  # 返回指定文字在图片中的位置,类型为二维数组[[][]]
    match_res = []
    img_data = operation.ocr.predict(f'pic/{pic_name}.png')[0]
    # print(f'img_data={img_data}')
    texts = img_data["rec_texts"]
    polys = img_data["rec_polys"]
    scores = img_data["rec_scores"]

    for text, poly, score in zip(texts, polys, scores):
        if target_text == text:
            match_res.append((text, score, poly))

    return match_res


if __name__ == '__main__':
    operation = Operation()
    result = get_text_location("后开奖", "fudai_Content")
    print(result)
