from typing import Any, TypedDict

# replace with actual data
UserData = Any
# replace with actual data
PostData = Any


class ExportData(TypedDict):
    posts: list[PostData]
    users: list[UserData]


def get_all_data() -> ExportData:
    return {
        "posts": [],
        "users": [],
    }


# Create your views here.
