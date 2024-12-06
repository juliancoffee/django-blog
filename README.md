# status
originated from my [learning repo]

# what
simple blog written with django

# run
There are two options.

The first one is using docker-compose.
```bash
$ docker compose up
```
The second one is by using start_docker.sh which will do roughly the same, but
also will rebuild web server Dockerfile.
```bash
$ ./start_docker.sh
```

Another option is to run only DB and adminer, and then run the server locally.
Run this one in one shell.
```bash
$ ./simple_start.sh
```
Run this one in the other (check .env.example file for environment variables).
```bash
$ uv run manage.py runserver
```

[learning repo]: https://github.com/juliancoffee/tree/main/django-blog
