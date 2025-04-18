docker build -t tfg .
docker run -it --rm \
    -p 3000:3000 -p 8000:8000\
    -v $(pwd):/app \
    tfg
