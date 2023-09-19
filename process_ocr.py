import os
import cv2
import asyncio
from paddleocr import PaddleOCR

async def process_image(image_path, ocr_model):
    try:
        resp = []
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

        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"File '{image_path}' has been deleted.")
        else:
            print(f"File '{image_path}' does not exist.")

        return resp
    except Exception as e:
        return {"error": str(e)}

async def process_images_in_directory():
    try:
        resp = []
        ocr_model = PaddleOCR(lang='en')
        path = os.path.join(os.path.dirname(__file__), 'upload_images')
        tasks = []

        for image_list in sorted(os.listdir(path)):
            if (image_list.endswith(".png") or image_list.endswith(".jpg") or image_list.endswith(".jpeg")):
                image_path = os.path.join(path, image_list)
                task = asyncio.create_task(process_image(image_path, ocr_model))
                tasks.append(task)

        results = await asyncio.gather(*tasks)
        resp.extend(results)
        return resp
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(process_images_in_directory())
