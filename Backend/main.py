#backend 코드
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key="sk-proj-yj6wGk05Ifv0nwtp67oYT3BlbkFJL5tG3pNh6ovBJsNmMAvz")
from PIL import Image
import io
import base64
import logging
import openai

app = FastAPI()

logging.basicConfig(level=logging.INFO)

class RequestData(BaseModel):
    image: str
    query: str
    option: str

@app.post("/generate_content")
async def generate_content(request_data: RequestData):
    try:
        logging.info("Decoding the image from base64")
        image_data = base64.b64decode(request_data.image)
        image_obj = Image.open(io.BytesIO(image_data))

        logging.info("Calling the OpenAI API")
        response = client.chat.completions.create(model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are a helpful and accurate English study assistant."},
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": request_data.query,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f'data:image/png;base64,{request_data.image}',
                        # "detail": "high",
                    },
                },
            ]}
        ],
        max_tokens=2048)

        logging.info("Processing the response from OpenAI API")
        content_text = response.choices[0].message.content
        return content_text

        logging.info("Generating image from the text")
        content_image = generate_image_from_text(content_text)

        logging.info("Saving to the database")
        save_to_database(image_obj, content_image, request_data.option)

        logging.info("Preparing the response image")
        content_image_bytes = io.BytesIO()
        content_image.save(content_image_bytes, format='PNG')
        return base64.b64encode(content_image_bytes.getvalue()).decode('ascii')

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_image_from_text(text):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    font = ImageFont.truetype("C:\\Windows\\Fonts\\SeoulHangangB.ttf", 24)
    lines = textwrap.wrap(text, width=60)

    max_width = max([font.getlength(line) for line in lines])
    total_height = sum([font.getbbox(line)[3] for line in lines]) + len(lines) * 5

    image = Image.new('RGB', (int(max_width) + 20, int(total_height) + 20), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    y = 10
    for line in lines:
        draw.text((10, y), line, font=font, fill=(0, 0, 0))
        y += font.getbbox(line)[3] + 5

    return image

#def save_to_database(image, content, option):
    db = mysql.connector.connect(
        host="localhost",
        user="worduser",
        password="1234",
        database="wordmaster"
    )

    cursor = db.cursor()

    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    blob_image = image_bytes.getvalue()

    content_bytes = io.BytesIO()
    content.save(content_bytes, format='PNG')
    blob_content = content_bytes.getvalue()

    if option == "단어장 생성":
        query = "INSERT INTO wordlists (image_data, wordlist) VALUES (%s, %s)"
    else:
        query = "INSERT INTO tests (image_data, test) VALUES (%s, %s)"
    values = (blob_image, blob_content)

    cursor.execute(query, values)
    db.commit()
    cursor.close()
    db.close()
