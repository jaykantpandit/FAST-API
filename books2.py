from typing import Optional

from fastapi import Body, FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookdRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not need on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)


    model_config = {
        'json_schema_extra': {
            "example":{
                "title": "A new book",
                "author": "Jay",
                "description": "Fast API learning",
                "rating": 2,
                "published_date": 2026

            }
        }
    }
    

BOOKS = [
    Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "A story of wealth and decadence in the Jazz Age", 5, 2024),
    Book(2, "To Kill a Mockingbird", "Harper Lee", "A tale of racial injustice in the American South", 5, 2025),
    Book(3, "1984", "George Orwell", "A dystopian novel about totalitarianism and surveillance", 5, 2020),
    Book(4, "Pride and Prejudice", "Jane Austen", "A romantic novel about manners and marriage in Regency England", 4, 2003),
    Book(5, "The Catcher in the Rye", "J.D. Salinger", "A story of teenage alienation and angst in New York City", 4, 2004),
    Book(6, "Brave New World", "Aldous Huxley", "A dystopian novel set in a technologically advanced future society", 4, 2024),
    Book(7, "The Hobbit", "J.R.R. Tolkien", "A fantasy adventure about a hobbit who embarks on an unexpected journey", 5, 2023) ,
    Book(8, "Fahrenheit 451", "Ray Bradbury", "A dystopian novel about a society that burns books", 4, 2021),
    Book(9, "The Lord of the Flies", "William Golding", "A novel about boys stranded on an island who descend into savagery", 3, 2019),
    Book(10, "Of Mice and Men", "John Steinbeck", "A story of friendship and dreams during the Great Depression", 4, 2025),
]

@app.get("/books")
def read_all_book():
    return BOOKS

@app.get("/books/publish")
def read_books_by_publish_date(publish_date: int = Query(gt = 1999, lt=2031)):
    books = []
    for book in BOOKS:
        if book.published_date == publish_date:
            books.append(book)
    return books  

@app.get("/books/{book_id}")
def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail=f"Book of id {book_id} is not found")
        

@app.get("/books/")
def read_book_by_id(rating: int = Query(gt=0, lt=6)):
    books = []
    for book in BOOKS:
        if book.rating == rating:
            books.append(book)
    return books
     

@app.post("/create-book")
def create_book(book_request: BookdRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else len(BOOKS)+1 
    return book

@app.put("/books/update_book")
def update_book(book_request: BookdRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = book_request
        

@app.delete("/books/{book_id}")
def book_delete(book_id: int= Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break