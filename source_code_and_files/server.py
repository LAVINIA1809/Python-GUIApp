import socket
import sqlite3
import DB_operations
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

# DB_operations.create_table()
# cursor.execute("SELECT id, title FROM Movies")
# DB_operations.drop_table()


rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
conn.close()

def get_imdb_reviews(url, title):
    page_to_scrape = requests.get(url)
    soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
    
    reviews = soup.findAll("div", attrs={"class":"text show-more__control"})
    users = soup.findAll("span", attrs={"class":"display-name-link"})

    max_length = 800
    filtered_reviews = []

    for user, review in zip(users, reviews):
        if len(review.text) <= max_length:
            filtered_reviews.append(user.text + ':\n' + review.text)
    
    reviews_json = json.dumps(filtered_reviews)
    reviews = json.loads(reviews_json)
    cursor.execute("UPDATE Movies SET reviews_list = ? WHERE title = ?", (reviews_json, title))
    conn.commit()
    return reviews


def format_reviews(reviews_list):
    formatted_reviews = ""

    for review in reviews_list:
        words = review.split()
        char_count = 0
        current_line = ""

        for word in words:
            if char_count < 60:
                current_line += word + " "
                char_count += len(word)
            else:
                formatted_reviews += current_line.strip() + '\n'
                current_line = word + " "
                char_count = len(word)
        
        formatted_reviews += current_line.strip() + '\n\n'

    return formatted_reviews

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 5678))
s.listen(5)

while True:
    print("Server is listening...")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")

    while True:
        msg = clientsocket.recv(1024)
        if not msg:
            break

        movie_input = msg.decode("utf-8")
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, rating, trailer_link, reviews from Movies where title LIKE '%' || ? || '%' OR actors LIKE '%' || ? || '%'", (movie_input, movie_input,))
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                title, rating, trailer_link, reviews = row
                clientsocket.sendall(bytes(f"\n\nRating of the movie \"{title}\": {rating}/100.\n", "utf-8"))
                clientsocket.sendall(bytes(f"\nAvailable trailers: \n (section)", "utf-8"))

                trailers = trailer_link.split(',')
                
                for trailer in trailers:
                    link = str(trailer)
                    clientsocket.sendall(bytes(link + "(section)", "utf-8"))

                cursor.execute("SELECT reviews_list FROM Movies WHERE title = ?", (title,))
                result = cursor.fetchone()

                if result and result[0]:
                    reviews_list = json.loads(result[0])
                else:
                    reviews_list = get_imdb_reviews(reviews, title)
                formatted_reviews = format_reviews(reviews_list)
                clientsocket.sendall(bytes(f"\n\nUsers reviews: \n\n" + formatted_reviews + "(section)", "utf-8"))
            clientsocket.sendall(bytes("\nThe end of the results\n", "utf-8"))
        else:
            cursor.execute("SELECT title, rating, movie_info, trailers FROM ImportedMovies WHERE title LIKE '%' || ? || '%'", (movie_input,))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    title, rating, movie_info, trailers = row
                    clientsocket.sendall(bytes(f"\n\nRotten Tomatoes rating of the movie \"{title}\": " + str(rating) + '/100.', "utf-8"))
                    clientsocket.sendall(bytes('\n\n' + "Movie info:\n" + movie_info + '(section)\n\n', "utf-8"))
                    clientsocket.sendall(bytes('\n\n' + trailers + "(section)", "utf-8"))   
                    clientsocket.sendall(bytes("\nThe end of the results", "utf-8"))
            else:
                encoded_movie_input = quote(movie_input)
                url = f'https://www.rottentomatoes.com/search?search={encoded_movie_input}'
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")

                fran_movies = soup.findAll("a", attrs={"class":"unset", "data-qa":"info-name"})
                movies = [link for link in fran_movies if 'https://www.rottentomatoes.com/' in link.get('href', '')]

                if movies:
                    movie_link = movies[0]['href']

                    movie_page = requests.get(movie_link)
                    movie_soup = BeautifulSoup(movie_page.text, "html.parser")

                    selected_movie = movie_soup.find('h1', attrs={"slot":"title", "class":"title", "data-qa":"score-panel-title"}).text
                    audience_rating = movie_soup.find('score-board-deprecated')['audiencescore']
                    movie_info = movie_soup.find('p', attrs={"data-qa":"movie-info-synopsis"})
                    movie_url = f'https://www.youtube.com/results?search_query={encoded_movie_input}+official+trailer'

                    movie_infos = movie_info.text.split()
                    formatted_movie_info = " "
                    chars_per_line = 0
                    curent_line = " "
                    for word in movie_infos:
                        if chars_per_line <= 60:
                            curent_line += word + " "
                            chars_per_line += len(word)
                        else:
                            formatted_movie_info += curent_line.strip() + '\n'
                            curent_line = word + " "
                            chars_per_line = len(word)
                    formatted_movie_info += curent_line.strip() +'\n'

                    clientsocket.sendall(bytes(f"\n\nRotten Tomatoes rating of the movie \"{selected_movie}\": " + str(audience_rating) + '/100.', "utf-8"))
                    clientsocket.sendall(bytes('\n\n' + "Movie info:\n" + formatted_movie_info + '(section)\n\n', "utf-8"))  
                    clientsocket.sendall(bytes('\n\n' + movie_url + "(section)", "utf-8")) 
                    clientsocket.sendall(bytes("\nThe end of the results", "utf-8"))

                    cursor.execute("INSERT INTO ImportedMovies (title, rating, movie_info, trailers) VALUES (?, ?, ?, ?)", (selected_movie, str(audience_rating), formatted_movie_info, movie_url))
                    conn.commit()
                else: 
                    clientsocket.sendall(bytes(f"The movie {movie_input} not found!", "utf-8"))
                    clientsocket.sendall(bytes("\n\nThe end of the results", "utf-8"))
        cursor.close()
        conn.close()




