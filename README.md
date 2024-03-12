# Python-GUIApp

Proiect realizat la materia "Programare in Python" din anul 3, semestrul 1.

Am implementat o aplicatie grafica de tip client-server folosind modulul "customtkinter", prin intermediul careia un client poate cauta un film in baza de date a serverului (am folosit sqlite). Daca filmul exista in baza de date, serverul va intoarce clientului detalii despre filmul cautat (rating, trailers si reviews, cele din urma fiind luate de pe "IMDB", folosind "BeautifulSoup" pentru web-scraping), iar daca nu exista, serverul va prelua informatii de pe "Rotten Tomatoes".
