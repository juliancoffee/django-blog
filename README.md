# status
originated from my [learning repo]

# what
A simple blog written with Django to learn web development, in particular:
- Django router (urlconf)
- Django function-based views and templates
- Django class-based views (for example, [accounts views])
- Django ORM with its models and transactions
- Django forms
- Migrations (for example, [this migration] to fix the datatype)
- `unittests` module and its application in Django (for example, [these tests])
- Various ways to handle static files, a bit of Nginx
- A bit of CSS
- `pre-commit` (didn't really like it)
- Docker and how to optimize it for (build) speed and size
- Docker Compose and how to optimize it for development
- logging using built-in `logging` module
- Configuration of logging in Django
- Authentication and authorization (and in context of Django)
- Method "safety" with GET vs POST, CSRF
- CORS
- How to split Django codebase into apps
- htmx

And related things such as:
- wsgi
- reverse proxies
- CI via Github Actions workflows
- deployment (via render.com for now)
- SMTP
- PostgreSQL backups using pg_dump

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
<br> This link should work: https://juliancoffee-django-blog.onrender.com
<br> P. S. it's a free hosting so you might be forced to wait for about a minute for it to spin up


[learning repo]: https://github.com/juliancoffee/learn-networking/tree/main/django-blog
[accounts views]: https://github.com/juliancoffee/django-blog/blob/76f2e8fa3620b226de560891a98d41a9e6359dab/blog/accounts/views.py#L86
[this migration]: https://github.com/juliancoffee/django-blog/blob/76f2e8fa3620b226de560891a98d41a9e6359dab/blog/migrations/0006_comment_proper_ip.py#L92
[these tests]: https://github.com/juliancoffee/django-blog/blob/76f2e8fa3620b226de560891a98d41a9e6359dab/blog/accounts/tests.py#L41
