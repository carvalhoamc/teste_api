# Importa os módulos necessários para testes
import pytest
from flask_testing import TestCase

# Importa o aplicativo Flask, o banco de dados e a classe Movie do arquivo principal (main)
from main import app, db, Movie

# Define uma classe de teste que herda de TestCase
class MainTest(TestCase):
    # Método para criar o aplicativo Flask de teste
    def create_app(self):
        # Configura o banco de dados em memória e define o modo de teste
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        return app

    # Método chamado antes de cada teste para configurar o ambiente
    def setUp(self):
        # Cria todas as tabelas no banco de dados de teste
        db.create_all()
        # Adiciona um filme de teste ao banco de dados de teste
        test_movie = Movie(year=2022, title='Test Movie', producer='Test Producer', winner='yes')
        db.session.add(test_movie)
        db.session.commit()

    # Método chamado após cada teste para limpar o ambiente
    def tearDown(self):
        # Remove a sessão do banco de dados de teste
        db.session.remove()
        # Destrói todas as tabelas no banco de dados de teste
        db.drop_all()

    # Teste para verificar se a rota '/api/movies' retorna os filmes corretamente
    def test_get_movies(self):
        # Faz uma requisição GET para a rota '/api/movies'
        response = self.client.get('/api/movies')
        # Verifica se a resposta tem código de status 200 (OK)
        self.assert200(response)
        # Verifica se há exatamente um filme na resposta
        self.assertEqual(len(response.json), 1)
        # Verifica se as informações do filme na resposta correspondem ao filme de teste
        self.assertEqual(response.json[0]['title'], 'Test Movie')
        self.assertEqual(response.json[0]['year'], 2022)
        self.assertEqual(response.json[0]['producer'], 'Test Producer')
        self.assertEqual(response.json[0]['winner'], 'yes')

    # Teste para verificar se a rota '/api/producer' retorna os dados do produtor corretamente
    def test_get_producer_data(self):
        # Faz uma requisição GET para a rota '/api/producer'
        response = self.client.get('/api/producer')
        # Verifica se a resposta tem código de status 200 (OK)
        self.assert200(response)
        # Verifica se o produtor com o menor intervalo está correto na resposta, se existir
        if response.json['min']:
            self.assertEqual(response.json['min'][0]['producer'], 'Test Producer')
        # Verifica se o produtor com o maior intervalo está correto na resposta, se existir
        if response.json['max']:
            self.assertEqual(response.json['max'][0]['producer'], 'Test Producer')

# Executa os testes usando o Pytest
if __name__ == '__main__':
    pytest.main()