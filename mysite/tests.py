from __future__ import annotations

from typing import Optional

from django.contrib.auth.models import User
from django.test import TestCase, tag
from django.urls import URLPattern, URLResolver, get_resolver, reverse

# NOTE: I guess type definitions can't be forward-declared without a manual
# stringification
#
# Our tree has two mutually exclusive nodes:
# - One is a URLPattern which has a pattern information, but can't have any
# children.
# - Another is a subtree, which doesn't any much info except optionally
# namespace, but potentially has other patterns attached.
#
# This type properly models this relationship, albeit maybe tricky to traverse
# as each name is "dependent" on its parent, so if you want to construct a full
# name to reverse, you need to "remember" namespaces while you walk the tree.
PatternTree = URLPattern | tuple[Optional[str], list["PatternTree"]]


def list_patterns() -> list[PatternTree]:
    # Init with toplevel resolver patterns
    patterns = get_resolver().url_patterns
    # Build a recursive tree of patterns
    tree = pattern_tree(patterns)
    return tree


URL_SKIP_LIST = ["admin"]


def pattern_tree(
    patterns: list[URLPattern | URLResolver],
) -> list[PatternTree]:
    buff: list[PatternTree] = []

    # The algorithm to construct a tree is pretty simple actually.
    # Check all url_patterns
    # If it's already URLPattern, grab it.
    # If it's a URLResolver, attach its namespace to recursively walked subtree.
    for p in patterns:
        match p:
            case URLPattern() as p:
                buff.append(p)
            case URLResolver() as r:
                name = r.namespace
                if name in URL_SKIP_LIST:
                    buff.append((name, []))
                    continue

                # if not in skiplist
                subtree = pattern_tree(r.url_patterns)
                buff.append((name, subtree))
    return buff


RouteName = str
RouteData = tuple[RouteName, URLPattern]


def flatten_forest(forest: list[PatternTree]) -> list[RouteData]:
    def prefix(namespace, name):
        if namespace is not None:
            name = f"{namespace}:{name}"
        return name

    def traverse_names(
        forest: list[PatternTree],
        *,
        namespace: Optional[str],
    ) -> list[tuple[RouteName, URLPattern]]:
        buff = []
        # As mentioned in type description, the only difference from the
        # construction of the tree is that while you traverse the tree, you need
        # to accumuate nested namespaces.
        #
        # I wish I knew how to test it :thinking:
        for node in forest:
            match node:
                case URLPattern() as p:
                    name = f"{p.name}"
                    name = prefix(namespace, name)

                    buff.append((name, p))
                case [nest, subforest]:
                    traversed = traverse_names(subforest, namespace=nest)
                    for nested_name, p in traversed:
                        name = prefix(namespace, nested_name)
                        buff.append((name, p))
        return buff

    return traverse_names(forest, namespace=None)


class CanaryTest(TestCase):
    """
    The purpose of this test is to test all routes

    It is easier said than done, of course, which in hindsight, I should have
    realised when I started this beautifully foolish endeavor.

    But still, a lot of views actually don't take any arguments.
    Those that do fall into the following categories:
    - Require POST data
    - Use GET query parameters
    - Use named URL parameters
    - And something I forgot???

    Anyway, while this test ignores most of these, I'd argue it is still useful
    to check that at least most templates are correct and won't panic at
    runtime.
    This won't catch every error, but after all, we're writing tests to notice
    the presence of errors, not to confirm the absence of.

    If a function uses named url parameters, it should use @test_with decorator.
    Check its docs to learn more.
    """

    def setUp(self):
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username="staffuser", password="testpassword", is_staff=True
        )

        # Create a regular user for comparison
        self.regular_user = User.objects.create_user(
            username="regularuser", password="testpassword", is_staff=False
        )

    def assertLoads(self, url, args=None):
        args = args or []
        response = self.client.get(reverse(url, args=args))

        OK = 200
        REDIRECT = 302
        WRONG_METHOD = 405
        FORBIDDEN = 403
        NOT_FOUND = 404

        self.assertIn(
            response.status_code,
            [OK, REDIRECT, WRONG_METHOD, FORBIDDEN, NOT_FOUND],
            f"URL {url} returned status code {response.status_code}",
        )

    def try_all_patterns(self):
        patterns = list_patterns()
        forest = flatten_forest(patterns)

        for url, pattern in forest:
            with self.subTest(url=url):
                view = pattern.callback
                # NOTE: wow, mypy is smart enough to recognise hasattr()
                if hasattr(view, "test_provider"):
                    picks = view.test_provider()
                    for pick in picks:
                        with self.subTest(args=pick):
                            self.assertLoads(url, args=pick)
                else:
                    self.assertLoads(url)

    @tag("canary")
    def test_canary_anon(self):
        self.try_all_patterns()

    @tag("canary")
    def test_canary_user(self):
        self.client.force_login(self.regular_user)
        self.try_all_patterns()

    @tag("canary")
    def test_canary_staff(self):
        self.client.force_login(self.staff_user)
        self.try_all_patterns()
