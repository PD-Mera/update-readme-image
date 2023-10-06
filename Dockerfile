FROM python:3.8.18

# Install dependencies.
ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt

# Copy code.
ADD main.py /main.py

CMD ["python", "/main.py"]
