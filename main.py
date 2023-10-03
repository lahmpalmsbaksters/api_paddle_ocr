from typing import Annotated
from typing import List

from fastapi import FastAPI, File, Form, UploadFile, status, Response
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import os
import shutil
import asyncio
from paddleocr import PaddleOCR
from pydantic import BaseModel
import urllib3


class UrlRequest(BaseModel):
    url: str


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize PaddleOCR once when the application starts
ocr_model = PaddleOCR(lang='en')


async def process_image(image_path, results):
    try:
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

        results.append(ocr_text)

        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"File '{image_path}' has been deleted.")
        else:
            print(f"File '{image_path}' does not exist.")
    except Exception as e:
        print(f"Error processing image: {str(e)}")


async def url_process_image(payload):
    try:
        results = []
        image_path = payload.url
        resp = urllib3.request('GET',
                               image_path)
        arr = np.asanyarray(bytearray(resp.data), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bfilter = cv2.bilateralFilter(gray_img, 11, 17, 17)
        blurred_image = cv2.GaussianBlur(bfilter, (5, 5), 0)
        _, thresholded_image = cv2.threshold(
            blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        result = ocr_model.ocr(
            thresholded_image, cls=False, det=True, rec=True)
        key_dict = ('result', 'confident')
        if result is not None:
            for res in result:
                for a in res:
                    print(a[1])
                    if len(key_dict) == len(a[1]):
                        resut_dict = {key_dict[i]: a[1][i]
                                      for i, _ in enumerate(a[1])}
                        print(resut_dict)
                        results.append(resut_dict)
        else:
            print("OCR did not recognize any text in the image.")

        return results
    except Exception as e:
        print(f"Error processing image: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username, "password": password}


@app.post("/files/", status_code=200)
async def upload_file(files: List[UploadFile], response: Response):
    try:
        upload_directory = "upload_images"
        os.makedirs(upload_directory, exist_ok=True)
        path = []

        # Process each file without explicit sorting
        for index, file in enumerate(files):
            if file.filename.split('.')[-1] not in ['png', 'jpg', 'jpeg']:
                response.status_code = status.HTTP_404_NOT_FOUND
                message = "Only png, jpg, and jpeg files are allowed"
            else:
                file_name = f"{index}_{file.filename.split('.')[-1]}"
                file_path = os.path.join(upload_directory, file_name)
                path.append(file_path)
                with open(file_path, "wb") as image_file:
                    shutil.copyfileobj(file.file, image_file)
                response.status_code = status.HTTP_201_CREATED
                message = "Image uploaded and saved successfully"

        # Initialize an empty list to collect OCR results
        ocr_results = []

        # Use asyncio to process images concurrently
        tasks = [process_image(p, ocr_results) for p in path]
        await asyncio.gather(*tasks)
        my_list = []
        # Concatenate with a space between elements
        my_list.append(str(ocr_results[0][0]))
        my_string = " ".join(my_list)
        print(my_string)

        content = {"code": response.status_code, "message": message,
                   "file_path": path, "result": ocr_results, "results": my_string}
        return content

    except Exception as e:
        return {"error": str(e)}


@app.post("/urls", status_code=200)
async def process_url(url_request: UrlRequest, response: Response):
    try:
        # Await the asynchronous function
        ocr_results = await url_process_image(url_request)
        content = {
            "code": response.status_code,
            "message": "success",
            "result": ocr_results
        }
        return content
    except Exception as e:
        error_message = f"Error processing image: {str(e)}"
        print(error_message)
        return {"error": error_message}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
