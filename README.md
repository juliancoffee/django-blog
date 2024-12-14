# status
originated from my [learning repo]

# what
simple blog written with Django with the goal of learning web development

# run
There are two main options
- `./start_docker.sh` which will start docker-compose and re-build what needs
    re-building.
- `./simple_start.sh` will start docker with db stuff, and then you'll need
    to run Django as you normally do it. Don't forget your `.env` file and
    keep in mind that it won't work without staticfiles collected, unless you
    run it with `DEBUG=1`.

# deploy
There's additionally a render.yaml blueprint for render.com.
You'd need to connect the repo.

[learning repo]: https://github.com/juliancoffee/tree/main/django-blog
