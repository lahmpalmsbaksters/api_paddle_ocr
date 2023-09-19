from paddleocr import PaddleOCR
import cv2
import os
import numpy as np


def paddle_ocr_process(image_path):
    try:
        resp = []
        ocr_model = PaddleOCR(lang='en')
        path = os.path.join(os.path.dirname(__file__), 'upload_images')
        for image_list in sorted(os.listdir(path)):
            if (image_list.endswith(".png") or image_list.endswith(".jpg") or image_list.endswith(".jpeg")):
                image_path = os.path.join(path, image_list)
                print(image_path)
                cv_img = cv2.imread(image_path)
                gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                bfilter = cv2.bilateralFilter(gray_img, 11, 17, 17)
                blurred_image = cv2.GaussianBlur(bfilter, (5, 5), 0)
                _, thresholded_image = cv2.threshold(
                    blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                result = ocr_model.ocr(thresholded_image, cls=False)
                if result and result[0] and result[0][0] and result[0][0][1] and result[0][0][1][0]:
                    ocr_text = result[0][0][1]

                else:
                    ocr_text = ["No text found", "No confidence rates"]
                resp.append(ocr_text)
                print((resp))
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"File '{image_path}' has been deleted.")
                else:
                    print(f"File '{image_path}' does not exist.")

        return resp
    except Exception as e:
        return {"error": str(e)}
    # finally:
    #     for image_list in (os.listdir(path)):
    #         image_path = os.path.join(path, image_list)
    #         if os.path.exists(image_path):
    #             os.remove(image_path)
    #             print(f"File '{image_path}' has been deleted.")
    #         else:
    #             print(f"File '{image_path}' does not exist.")


def auto_ocr_process():
    i: int = 0
    path = os.path.join(os.path.dirname(__file__), 'image_for_test01')
    for image_list in os.listdir(path):
        i += 1
        if (image_list.endswith(".png")):
            print(image_list)
            image_path = os.path.join(path, image_list)
            print(image_path)
            paddle_ocr_process(image_path)
        if (i == 10):
            break
    return image_path


# auto_ocr_process()
