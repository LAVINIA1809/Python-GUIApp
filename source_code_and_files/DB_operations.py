import sqlite3

def create_table():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    with open("C:\\Users\\bvivi\\Desktop\\Python\\Proiect\\movies_data_sql.txt") as file:
        sql_script = file.read()

    cursor.executescript(sql_script)
    conn.commit()
    cursor.close()
    conn.close()

def drop_table():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE Movies")
    cursor.execute("DROP TABLE ImportedMovies")
    conn.commit()
    cursor.close()
    conn.close()

def delete_som_quick():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ImportedMovies WHERE title LIKE 'Song of China'")

    conn.commit()
    conn.close()

#delete_som_quick()



