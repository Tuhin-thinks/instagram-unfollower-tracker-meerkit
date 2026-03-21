import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "tests" / "outputs"


def build_profile_from_env():
    from insta_interface import InstagramProfile

    csrf_token = os.environ["IG_CSRF_TOKEN"]
    session_id = os.environ["IG_SESSION_ID"]
    user_id = os.environ["IG_USER_ID"]
    return InstagramProfile(
        csrf_token=csrf_token,
        session_id=session_id,
        user_id=user_id,
    )


def write_following_to_txt(profile) -> Path:
    from insta_interface import get_current_following_v2

    following_users = get_current_following_v2(profile=profile, store_data=False)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"following_users_{profile.user_id}_{timestamp}.txt"

    with output_path.open("w", encoding="utf-8") as file_obj:
        file_obj.write(f"profile_user_id={profile.user_id}\n")
        file_obj.write(f"total_following={len(following_users)}\n\n")

        for user in following_users:
            file_obj.write(f"username={user.username}\n")
            file_obj.write(f"full_name={user.full_name}\n")
            file_obj.write(f"pk_id={user.pk_id}\n")
            file_obj.write(f"is_private={user.is_private}\n")
            file_obj.write(f"profile_pic_url={user.profile_pic_url}\n")
            file_obj.write("-" * 40 + "\n")

    return output_path


def main() -> None:
    profile = build_profile_from_env()
    output_path = write_following_to_txt(profile)
    print(f"Wrote following users to: {output_path}")


if __name__ == "__main__":
    main()
