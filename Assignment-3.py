import json
import requests
import redis
from flask import Flask, render_template, request
import matplotlib.pyplot as plt

app = Flask(__name__)

class DataProcessor:
    def __init__(self, api_url, headers, redis_host='localhost', redis_port=6379):
        self.api_url = api_url
        self.headers = headers
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    def fetch_data_from_api(self):
        """
        Fetches JSON data from the specified API.

        Returns:
        - dict: The JSON data.
        """
        response = requests.get(self.api_url, headers=self.headers, params={'page': '1'})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data from API. Status code: {response.status_code}")


    def insert_into_redis(self, data):
        json_data = json.dumps(data)
        self.redis_client.set('example_key', json_data)

    def visualize_data(self):
        """
        Visualizes data from Redis using a generic approach.
        """
        # Fetch data from Redis (assuming it's already inserted)
        json_data = self.redis_client.get('example_key')

        # Deserialize JSON data
        data = json.loads(json_data)

        # Example: Generic visualization
        plot_path = self._generic_visualization(data.get('movie_results', []))
        return plot_path

    def _generic_visualization(self, movie_results):
        """
        A generic method for visualization based on the structure of the data.

        Parameters:
        - movie_results (list): List of movie results.
        """
        # Example: Plotting a bar chart for the number of movies per year
        years = [movie['year'] for movie in movie_results]
        unique_years = set(years)
        year_counts = {year: years.count(year) for year in unique_years}

        plt.bar(year_counts.keys(), year_counts.values())
        plt.xlabel('Years')
        plt.ylabel('Number of Movies')
        plt.title('Movies per Year')
        
        # Save the plot as an image
        plot_path = 'static/plot.png'
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path


    def perform_aggregation(self):
        """
        Performs aggregation on the data from Redis.

        Returns:
        - dict: The aggregated data.
        """
        # Fetch data from Redis (assuming it's already inserted)
        json_data = self.redis_client.get('example_key')

        # Deserialize JSON data
        data = json.loads(json_data)

        # Example: Calculate the total number of results
        total_results = int(data.get('Total_results', 0))
        return total_results

    
    def search_data(self, query):
        """
        Searches for specific data in Redis based on the provided query.

        Parameters:
        - query (str): The search query.

        Returns:
        - dict: The search results.
        """
        # Fetch data from Redis (assuming it's already inserted)
        json_data = self.redis_client.get('example_key')

        # Deserialize JSON data
        data = json.loads(json_data)

        # Extract the 'movie_results' list
        movie_results = data.get('movie_results', [])

        # Example: Simple search based on a query in movie titles
        results = [movie for movie in movie_results if query.lower() in movie.get('title', '').lower()]
        return {'search_results': results}

processor = DataProcessor(api_url='https://movies-tv-shows-database.p.rapidapi.com/',
                          headers = {
	"Type": "get-trending-movies",
	"X-RapidAPI-Key": "425313084amsh4e8c96c668410b4p1ef836jsn7e1962a7d38d",
	"X-RapidAPI-Host": "movies-tv-shows-database.p.rapidapi.com"
})

@app.route('/')
def index():
    # Fetch data from API
    json_data = processor.fetch_data_from_api()

    # Insert data into Redis
    processor.insert_into_redis(json_data)

    # Visualize data and get the plot path
    plot_path = processor.visualize_data()

    # Perform aggregation
    aggregation_result = processor.perform_aggregation()

    # Search for specific data
    search_result = processor.search_data('example_query')

    return render_template('index.html', plot_path=plot_path, aggregation_result=aggregation_result, search_result=search_result)

@app.route('/search_movies', methods=['POST'])
def search_movies():
    # Get the movie name from the form data
    movie_name = request.form.get('movie_name')

    # Use the movie name in the search_data method
    search_result = processor.search_data(movie_name)

    # Visualize data and get the plot path
    plot_path = processor.visualize_data()

    # Perform aggregation
    aggregation_result = processor.perform_aggregation()

    # Render the template with the updated search result
    return render_template('index.html', plot_path=plot_path, aggregation_result=aggregation_result, search_result=search_result)

if __name__ == "__main__":
    app.run(debug=True)
