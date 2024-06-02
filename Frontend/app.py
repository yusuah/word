#frontend 코드
import streamlit as st
import requests
from PIL import Image
import io
import base64
import pandas as pd

def main():
    st.title("영어 지문 학습 도우미")
    option = st.radio("옵션을 선택하세요", ("단어장 생성", "시험지 생성"))
    uploaded_file = st.file_uploader("영어 지문 이미지를 PNG 형식으로 업로드 하세요.", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        original_image = Image.open(uploaded_file).convert('RGBA')

        image_bytes = io.BytesIO()
        original_image.save(image_bytes, format='PNG')

        st.write(original_image)

        image_base64 = base64.b64encode(image_bytes.getvalue()).decode('ascii')

        if option == "단어장 생성":
            query = "이 문서는 Reading 영어시험을 공부하기 위한 영어 지문입니다. 하이라이트 표시된 단어들을 모두 찾아 '영단어, 한글 뜻' 형식의 CSV 표로 변환하세요. CSV의 표 줄은 '\n'으로 하고, 헤더를 추가하시오. 이때 어떠한 부차적인 수식어 (예: 알겠습니다) 등을 말하지 않고 결과만 말하세요."
        elif option == "시험지 생성":
            query = "이 문서는 Reading 영어시험을 공부하기 위한 영어 지문입니다. 하이라이트 표시된 단어들을 모두 골라 '영단어, ____________' 형식의 CSV 표로 변환하세요. CSV의 표 줄은 '\n'으로 하고, 헤더는 '하이라이트 된 영단어, 빈칸'으로 추가하시오. 이때 어떠한 부차적인 수식어 (예: 알겠습니다) 등을 말하지 않고 결과만 말하세요."

        response = requests.post(
            "https://10.32.249.134:6443/generate_content",
            json={"image": image_base64, "query": query, "option": option},
        )

        if response.status_code == 200:
            vocabulary = pd.read_csv(io.StringIO(response.text.replace('\\n', '\n').replace('\\', '').replace('"', '')))
            st.write(vocabulary)
        else:
            st.error(f'오류가 발생했습니다: {response.text}')

        # if response.status_code == 200:
        #     content_image_base64 = base64.b64decode(response.text)
        #     content_image_bytes = io.BytesIO(content_image_base64)
        #     content_image = Image.open(content_image_bytes)
        #     if option == "단어장 생성":
        #         st.image(content_image, caption='생성된 단어장', use_column_width=True)
        #     else:
        #         st.image(content_image, caption='생성된 시험지', use_column_width=True)
        # else:
        #     st.error("오류가 발생했습니다.")

if __name__ == "__main__":
    main()

