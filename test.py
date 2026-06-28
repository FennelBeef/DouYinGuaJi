from Operation import Operation
import cv2
import numpy as np

# 使用示例
if __name__ == '__main__':
    print("aa")
    operation = Operation()
    d = operation.get_device()  # 获取设备并返回

    WinResult = operation.check_WinResult(d)
    if "本轮未中奖" in WinResult:
        print("本轮未中奖,将参与下一次中奖")
        d.keyevent(4)

    else:
        print("恭喜，成功中奖！")

