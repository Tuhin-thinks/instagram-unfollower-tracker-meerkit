import csv
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
import tqdm
from dotenv import load_dotenv

load_dotenv()
_csrf_token = os.environ["CSRF_TOKEN"]
_session_id = os.environ["SESSION_ID"]
_user_id = os.environ["USER_ID"]
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "x-csrftoken": _csrf_token,
    "x-ig-app-id": "936619743392459",
}

cookies = {
    "csrftoken": _csrf_token,
    "sessionid": _session_id,
}

url = "https://www.instagram.com/graphql/query"
_topsearch_url = "https://www.instagram.com/web/search/topsearch/"
_follow_doc_id = "9740159112729312"
_follow_lsd = "vfndR6YI1o9Mb1SorLFoGO"


profile_query_data_path = Path("profile_query")
profile_query_data_path.mkdir(exist_ok=True)

# username = "perspectives.with.andrea"
# username = "akshay_saraf_7712"


profile_query_data_path = Path("profile_query")
profile_query_data_path.mkdir(exist_ok=True)


def load_non_followers_csv():
    if not Path("all_non_followers.csv").exists():
        return set()
    with open("all_non_followers.csv", "r") as f:
        reader = csv.DictReader(f)
        return {row["username"] for row in reader if row["unfollow_signal"] == "True"}


def append_unfollowed_user(user_id: str, user_name: str, user_profile_url: str):
    with open(profile_query_data_path / "unfollowed_users.csv", "a", newline="") as f:
        if f.tell() == 0:
            writer = csv.writer(f)
            writer.writerow(["user_id", "username", "user_profile_url"])
        writer = csv.writer(f)
        writer.writerow([user_id, user_name, user_profile_url])


def load_unfollowed_users():
    if not (profile_query_data_path / "unfollowed_users.csv").exists():
        return set()
    with open(profile_query_data_path / "unfollowed_users.csv", "r") as f:
        reader = csv.DictReader(f)
        return {row["username"] for row in reader}


def load_user_pk_from_saved_data(username: str):
    search_path = profile_query_data_path / f"profile_query_{username}.json"
    if not search_path.exists():
        return None
    with open(search_path, "r") as f:
        data = json.load(f)
        try:
            return data["data"]["user"]["pk"]
        except (KeyError, IndexError):
            return None


def _extract_username_from_profile_link(instagram_profile_link: str) -> str:
    """Extract username from Instagram profile links like https://www.instagram.com/username/."""
    parsed = urlparse(instagram_profile_link.strip())
    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        raise ValueError(
            f"Could not extract username from profile link: {instagram_profile_link}"
        )

    username = path_parts[0].strip()
    if not username:
        raise ValueError(
            f"Could not extract username from profile link: {instagram_profile_link}"
        )
    return username


def _resolve_user_pk(username: str) -> str | None:
    """Resolve Instagram user pk either from saved profile data or topsearch endpoint."""
    user_pk = load_user_pk_from_saved_data(username)
    if isinstance(user_pk, str) and user_pk:
        return user_pk

    params = {"query": username}
    response = requests.get(
        _topsearch_url, headers=headers, cookies=cookies, params=params
    )
    if not response.ok:
        return None

    try:
        users = response.json().get("users", [])
        if not users:
            return None
        candidate = users[0].get("user", {}).get("pk")
        return str(candidate) if candidate is not None else None
    except (KeyError, ValueError, TypeError):
        return None


already_unfollowed_users = load_unfollowed_users()


def unfollow_user(username: str, retry_count: int = 3):
    if retry_count < 3:
        print(f"Retrying unfollow for {username}, attempts left: {retry_count}")

    user_id = load_user_pk_from_saved_data(username)

    assert isinstance(user_id, str), (
        f"User ID for {username} not found or invalid. Cannot proceed with unfollowing."
    )

    print(f"{user_id=}")

    variables = {
        "target_user_id": user_id,
        "container_module": "profile",
        "nav_chain": "PolarisProfilePostsTabRoot:profilePage:1:via_cold_start",
    }

    data = {
        "variables": json.dumps(variables),
        "doc_id": "9846833695423773",
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    print(response.status_code)
    print(response.json())

    if response.status_code == 200:
        append_unfollowed_user(
            user_id, username, f"https://www.instagram.com/{username}/"
        )
        return 1
    else:
        print(f"Failed to unfollow {username}. Status code: {response.status_code}")
        return -1


def follow_user(instagram_profile_link: str, retry_count: int = 3) -> int:
    """Follow an Instagram user by profile link using GraphQL mutation."""
    if retry_count < 3:
        print(
            "Retrying follow for "
            f"{instagram_profile_link}, attempts left: {retry_count}"
        )

    username = _extract_username_from_profile_link(instagram_profile_link)
    user_id = _resolve_user_pk(username)

    if not isinstance(user_id, str) or not user_id:
        print(
            "User ID for "
            f"{instagram_profile_link} not found or invalid. Cannot proceed with following."
        )
        return -1

    print(f"Following user: {username} ({user_id})")

    variables = {
        "target_user_id": user_id,
        "container_module": "profile",
        "nav_chain": "PolarisProfilePostsTabRoot:profilePage:1:via_cold_start",
    }

    follow_headers = {
        **headers,
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.instagram.com",
        "referer": f"https://www.instagram.com/{username}/",
        "x-fb-friendly-name": "usePolarisFollowMutation",
        "x-fb-lsd": _follow_lsd,
        "x-root-field-name": "xdt_create_friendship",
    }

    payload = {
        "fb_api_req_friendly_name": "usePolarisFollowMutation",
        "server_timestamps": "true",
        "lsd": _follow_lsd,
        "variables": json.dumps(variables),
        "doc_id": _follow_doc_id,
    }

    response = requests.post(url, headers=follow_headers, cookies=cookies, data=payload)

    print(response.status_code)
    try:
        print(response.json())
    except ValueError:
        print(response.text)

    if response.status_code == 200:
        return 1

    print(
        "Failed to follow "
        f"{instagram_profile_link}. Status code: {response.status_code}"
    )
    return -1


def get_user_data(
    username: str, unfollow_signal_followers_threshold: int = 10000
) -> dict[str, str | int | bool]:
    user_id_query_url = (
        f"https://www.instagram.com/web/search/topsearch/?query={username}"
    )
    resp = requests.get(user_id_query_url, headers=headers, cookies=cookies)
    if not resp.ok:
        # write response error to a file
        with open(
            profile_query_data_path / f"user_id_query_error_{username}.html", "w"
        ) as f:
            f.write(resp.text)
        print("Fetching user pk:", resp.status_code)
    resp.raise_for_status()
    # print(resp.json())
    try:
        user_id = resp.json()["users"][0]["user"]["pk"]
    except IndexError:
        return {"error": "User not found"}

    print(f"{user_id=}")

    variables = {
        "enable_integrity_filters": True,
        "id": user_id,
        "render_surface": "PROFILE",
        "__relay_internal__pv__PolarisProjectCannesEnabledrelayprovider": True,
        "__relay_internal__pv__PolarisProjectCannesLoggedInEnabledrelayprovider": True,
        "__relay_internal__pv__PolarisCannesGuardianExperienceEnabledrelayprovider": False,
        "__relay_internal__pv__PolarisCASB976ProfileEnabledrelayprovider": False,
    }

    data = {
        "variables": json.dumps(variables),
        "doc_id": "31574646175516262",  # which graphql query to use
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    if not response.ok:
        # write response error to a file
        with open(
            profile_query_data_path / f"profile_query_error_{username}.html", "w"
        ) as f:
            f.write(response.text)
        print("Fetching user profile data:", response.status_code)
    response.raise_for_status()

    profile_query_data = response.json()["data"]
    friendship_status = profile_query_data["user"]["friendship_status"]
    # extract important fields
    me_following_account = friendship_status["following"]
    being_followed_by_account = friendship_status["followed_by"]
    account_followers_count = profile_query_data["user"]["follower_count"]

    # save json a file
    with open(profile_query_data_path / f"profile_query_{username}.json", "w") as f:
        json.dump(response.json(), f, indent=4)

    result = {
        "username": username,
        "me_following_account": me_following_account,
        "being_followed_by_account": being_followed_by_account,
        "account_followers_count": account_followers_count,
    }

    # unfollow signal
    if me_following_account and not being_followed_by_account:
        if account_followers_count < unfollow_signal_followers_threshold:
            print(f"Unfollow signal for {username=}")
            result["unfollow_signal"] = True
        else:
            result["unfollow_signal"] = False
    else:
        result["unfollow_signal"] = False

    return result


@dataclass
class FollowerUserRecord:
    pk_id: str
    id: str
    fbid_v2: str
    profile_pic_id: str
    profile_pic_url: str
    username: str
    full_name: str
    is_private: bool

    @staticmethod
    def from_string(record_str: str) -> "FollowerUserRecord":
        record_data = json.loads(record_str)
        return FollowerUserRecord(**record_data)

    def __hash__(self) -> int:
        return hash(self.pk_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FollowerUserRecord):
            return NotImplemented
        return self.pk_id == other.pk_id

    def __str__(self) -> str:
        return json.dumps(self.__dict__)


def get_current_followers(
    store_data: bool = True,
    _store_fn: Callable[[list[FollowerUserRecord]], None] | None = None,
) -> list[FollowerUserRecord]:
    """Get the set of current followers"""

    followers_count = 99
    _max_fetch_count = 24
    follower_user_data_list: list[FollowerUserRecord] = []

    with requests.Session() as session:
        session.headers.update(headers)
        session.cookies.update(cookies)

        _query_params: dict[str, int | str] = {
            "search_surface": "followers_list_page",
            "count": _max_fetch_count,
        }

        _iterations = (followers_count + _max_fetch_count - 1) // _max_fetch_count
        _progress = tqdm.tqdm(
            total=_iterations,
            desc="Fetching followers",
            unit="requests",
        )
        _max_id = None
        while followers_count > 0:
            url = f"https://www.instagram.com/api/v1/friendships/{_user_id}/followers"
            if _max_id:
                _query_params = _query_params | {"max_id": _max_id}
            try:
                response = session.get(url, params=_query_params)
                followers_count_data = response.json()
            except (requests.RequestException, ValueError) as e:
                print(f"Error fetching followers: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

            _max_id = followers_count_data.get("next_max_id")
            users_data = followers_count_data.get("users", [])

            for user_data in users_data:
                follower_record = FollowerUserRecord(
                    pk_id=user_data.get("pk", ""),
                    id=user_data.get("id", ""),
                    fbid_v2=user_data.get("fbid_v2", ""),
                    profile_pic_id=user_data.get("profile_pic_id", ""),
                    profile_pic_url=user_data.get("profile_pic_url", ""),
                    username=user_data.get("username", ""),
                    full_name=user_data.get("full_name", ""),
                    is_private=user_data.get("is_private", False),
                )
                follower_user_data_list.append(follower_record)
            followers_count -= _max_fetch_count
            _progress.update(1)

    if store_data and _store_fn:
        _store_fn(follower_user_data_list)

    return follower_user_data_list


if __name__ == "__main__":
    # test follow user
    # _user_profile = "https://www.instagram.com/tusharsainn"
    # follow_result = follow_user(_user_profile)
    # print(f"Follow result: {follow_result}")
    get_current_followers()
