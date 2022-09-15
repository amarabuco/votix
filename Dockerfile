FROM python:3.8

EXPOSE 80:8501

WORKDIR /usr/src/app

COPY ./app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "streamlit", "run", "./app/app/ranking.py" ]