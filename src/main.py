# Importando as bibliotecas necessárias para criar a API RESTful e manipular dados
import csv

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# Inicializando a aplicação Flask
app = Flask(__name__)

# Configurando a conexão com o banco de dados SQLite em memória e desativando o rastreamento de modificações do
# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando o objeto SQLAlchemy para interagir com o banco de dados SQLite
db = SQLAlchemy(app)


# Definindo o modelo de dados para a tabela Movie no banco de dados
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único para cada filme
    year = db.Column(db.Integer)  # Ano de lançamento do filme
    title = db.Column(db.String(200))  # Título do filme
    producer = db.Column(db.String(200))  # Produtor do filme
    winner = db.Column(db.String(3))  # Indica se o filme é um vencedor

    # Método para representar cada instância da classe Movie
    def __repr__(self):
        return f'<Movie {self.title}>'


# Função para carregar os dados do arquivo CSV para o banco de dados SQLite
def load_data():
    with open('movielist.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            movie = Movie(year=int(row['year']), title=row['title'], producer=row['producers'], winner=row['winner'])
            db.session.add(movie)  # Adicionando cada filme à sessão do SQLAlchemy
        db.session.commit()  # Salvando todas as alterações na sessão do SQLAlchemy para o banco de dados


# Função para calcular o produtor com o maior e menor intervalo entre vitórias consecutivas
def get_producer_most_consecutive_wins():
    producers = {}
    min_producers = []
    max_producers = []

    # Itera sobre os filmes ordenados por ano
    for movie in Movie.query.order_by(Movie.year):
        if movie.winner == 'yes':
            # Verifica se o produtor já está na lista de produtores
            if movie.producer in producers:
                interval = movie.year - producers[movie.producer]['previousWin']
                # Atualiza os intervalos mínimo e máximo, se necessário
                if interval < producers[movie.producer]['min_interval']:
                    producers[movie.producer]['min_interval'] = interval
                if interval > producers[movie.producer]['max_interval']:
                    producers[movie.producer]['max_interval'] = interval
                producers[movie.producer]['previousWin'] = movie.year  # Atualiza o ano da última vitória
            else:
                # Adiciona o produtor à lista de produtores
                producers[movie.producer] = {'previousWin': movie.year, 'min_interval': float('inf'), 'max_interval': 0}

    # Filtra os produtores com os intervalos mínimos e máximos
    for producer, data in producers.items():
        if data['min_interval'] != float('inf'):
            min_producers.append({'producer': producer, 'interval': data['min_interval'],
                                  'previousWin': data['previousWin'] - data['min_interval'],
                                  'followingWin': data['previousWin']})
        if data['max_interval'] != 0:
            max_producers.append({'producer': producer, 'interval': data['max_interval'],
                                  'previousWin': data['previousWin'] - data['max_interval'],
                                  'followingWin': data['previousWin']})

    return min_producers, max_producers




# Definindo a rota para obter todos os filmes
@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()  # Obtendo todos os filmes do banco de dados
    # Transformando cada filme em um dicionário e retornando a lista de dicionários como um JSON
    movie_data = [{'year': movie.year, 'title': movie.title, 'producer': movie.producer, 'winner': movie.winner} for
                  movie in movies]
    return jsonify(movie_data)


# Definindo a rota para obter informações sobre os produtores
@app.route('/api/producer', methods=['GET'])
def get_producer_data():
    min_data, max_data = get_producer_most_consecutive_wins()  # Obtendo os dados dos produtores
    # Retornando os dados dos produtores como um JSON
    return jsonify({'min': min_data, 'max': max_data})


# Verificando se o script está sendo executado diretamente e, em caso afirmativo, carregando os dados do CSV para o banco de dados
if __name__ == '__main__':
    with app.app_context():  # Criando um contexto de aplicação temporário
        db.create_all()  # Criando as tabelas no banco de dados
        load_data()  # Carregando os dados do CSV para o banco de dados
    app.run(debug=True,host='0.0.0.0')  # Iniciando o servidor Flask em modo de depuração
