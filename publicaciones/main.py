import datetime
import psycopg2
from time import sleep
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# TODO: Authorization


class PostBase(BaseModel):
    routeId: int
    userId: int
    plannedStartDate: datetime.datetime
    plannedEndDate: datetime.datetime
    createdAt: datetime.datetime


class Post(PostBase):
    id: int


class PostCreate(PostBase):
    pass


def _get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("POST_DATABASE_HOST"),
        database="posts",
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )
    return conn


def get_db_connection():
    # Implement waiting for the database to be ready
    attempts = 0
    while True:
        attempts += 1
        try:
            return _get_db_connection()
        except psycopg2.OperationalError as e:
            print("Could not connect to database, trying again")
            sleep(3)
            if attempts > 5:
                print("Could not connect to database, giving up")
                raise e


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Starting up")
    print("Connecting to database for the first time")
    conn = get_db_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        print("Creating database")
        cursor.execute('CREATE DATABASE "posts"')
    except psycopg2.DatabaseError as e:
        if e.pgcode != "42P04":
            raise e
        else:
            print("Database already exists")
    finally:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS post (
                "id" SERIAL PRIMARY KEY,
                "routeId" INT NOT NULL,
                "userId" INT NOT NULL,
                "plannedStartDate" TIMESTAMP NOT NULL,
                "plannedEndDate" TIMESTAMP NOT NULL,
                "createdAt" TIMESTAMP NOT NULL
            );
            """
        )
        conn.close()


@app.get("/{post_id}", description="Get all posts")
def get_post(post_id: int) -> Post:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM post WHERE id = %s
        """,
        (post_id,),
    )
    ret = cursor.fetchone()
    conn.close()
    if not ret:
        # Send a 404 response
        raise HTTPException(status_code=404, detail="Post not found")

    return Post(
        id=ret[0],
        routeId=ret[1],
        userId=ret[2],
        plannedStartDate=ret[3],
        plannedEndDate=ret[4],
        createdAt=ret[5],
    )


@app.post("/", description="Create a new post")
def create_post(post: PostCreate) -> Post:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO post
            ("routeId", "userId", "plannedStartDate", "plannedEndDate", "createdAt")
            VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            post.routeId,
            post.userId,
            post.plannedStartDate,
            post.plannedEndDate,
            post.createdAt,
        ),
    )
    conn.commit()
    ret = cursor.fetchone()
    conn.close()

    if not ret:
        raise Exception("Could not create post")

    post_id = ret[0]

    return Post(
        id=post_id,
        routeId=post.routeId,
        userId=post.userId,
        plannedStartDate=post.plannedStartDate,
        plannedEndDate=post.plannedEndDate,
        createdAt=post.createdAt,
    )


@app.get("/ping", description="Ping the server to check if it's alive")
def ping():
    return "pong"


@app.get("/search", description="Search for posts")
def search_posts(
    when: Optional[str] = None,
    route: Optional[str] = None,
    filter: Optional[str] = None,
) -> list[Post]:
    results: list[Post] = []
    conn = get_db_connection()
    cursor = conn.cursor()
    plannedStartDate: Optional[datetime.datetime] = None
    userId: Optional[int] = None
    routeId: Optional[int] = None
    # Primero validamos
    print(when, route, filter)
    if route:
        try:
            routeId = int(route)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid route id")
    if when:
        try:
            plannedStartDate = datetime.datetime.fromisoformat(when)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

    if filter and filter != "me":
        raise HTTPException(status_code=400, detail="Invalid filter")
    else:
        # TODO: Use the actual userId from the token
        userId = 1

    where_clauses = []
    arguments = {}

    if plannedStartDate:
        where_clauses.append('"plannedStartDate" >= %(plannedStartDate)s')
        arguments["plannedStartDate"] = plannedStartDate

    if userId:
        where_clauses.append('"userId" = %(userId)s')
        arguments["userId"] = userId

    if routeId:
        where_clauses.append('"routeId" = %(routeId)s')
        arguments["routeId"] = routeId

    if len(where_clauses) == 0:
        raise HTTPException(status_code=400, detail="No valid filters provided")

    query = f"SELECT * FROM post WHERE {' AND '.join(where_clauses)}"
    cursor.execute(query, arguments)
    ret = cursor.fetchall()
    conn.close()
    if ret:
        for post in ret:
            results.append(
                Post(
                    id=post[0],
                    routeId=post[1],
                    userId=post[2],
                    plannedStartDate=post[3],
                    plannedEndDate=post[4],
                    createdAt=post[5],
                )
            )

    return results
