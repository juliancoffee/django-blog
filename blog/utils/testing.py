def random_post_ids() -> list[tuple[int]]:
    # NOTE: it's must be a tuple
    #
    # Also, it doesn't really matter what we put here, because during tests
    # we have no posts and we'd get 404 in any case.
    random_post_id = (22,)

    return [random_post_id]
