FROM python:3.7-alpine
WORKDIR /ElevateSecurityTakeHome
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 9000
ADD . .
CMD python app.py