from cronk.json_to_cron import json_to_cron


def test_cron_to_json_handles_happy_path():
    with open("tests/json_to_cron_test_happy.json") as fp:
        assert json_to_cron(fp) == [
            "# Intro comment",
            "",
            "# First action comment",
            "0 * * * * echo 'hello world'",
            "# Second action",
            "# comment",
            "1 * * * * echo 'farewell'",
            "# Outro",
        ]


# TODO: Test sad path
