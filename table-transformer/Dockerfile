FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Copy environment files and code
COPY . /app

# Create and activate Conda environment with Python 3.12
RUN conda create -n myenv python=3.12.7 -y && \
    echo "conda activate myenv" >> ~/.bashrc

# Use conda run to install packages in myenv
RUN conda run -n myenv python -m pip install --upgrade pip && \
    conda run -n myenv python -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/ && \
    conda run -n myenv pip install paddleocr && \
    conda run -n myenv pip install ultralytics pandas streamlit

# Set environment to auto-activate conda env on start
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit app
CMD ["conda", "run", "--no-capture-output", "-n", "myenv", "streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]