FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY pipeline.py README.md ./
RUN mkdir -p artifacts
EXPOSE 8080
CMD ["sh", "-c", "python pipeline.py --output-dir artifacts --rows ${ROWS:-3000} --seed ${SEED:-42} && python -m http.server 8080 --directory artifacts"]
