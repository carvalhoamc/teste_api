# Use a imagem base do Anaconda com Python 3.11
FROM continuumio/anaconda3:latest

# Definir o diretório de trabalho
WORKDIR /app/

# Copie o diretório de dados para o diretório de trabalho do contêiner
COPY ../dados/movielist.csv .

# Copie os scripts para o diretório de trabalho do contêiner
COPY src/main.py .
COPY src/testes_integracao.py .

# Instalar as dependências do pip
RUN pip install --no-cache-dir flask flask_sqlalchemy pytest pandas numpy watchdog werkzeug
RUN pip install --upgrade watchdog
# Expor a porta em que o servidor Flask estará escutando
EXPOSE 5000

# Comando para executar o seu aplicativo
CMD [ "python", "main.py" ]