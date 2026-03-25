from pathlib import Path


def get_pass():
    """
    获取密码
    :return:
    """
    pass_file = Path(__file__).resolve().parents[1] / ".pass" / "model"
    with pass_file.open("r", encoding="utf-8") as f:
        api_key = f.read().strip()
        return api_key