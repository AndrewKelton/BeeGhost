# test_cli.py

import pytest

import BeeGhost.cli as cli

@pytest.mark.parametrize(
    "platform",
    ["youtube", "instagram", "x"],
)
def test_valid_platform(platform):
    args = cli.parse_args([platform, "comments"])
    assert args.platform == platform

@pytest.mark.parametrize(
    "removal_type",
    ["comments", "likes", "reposts", "story_replies"],
)
def test_valid_removal_type(removal_type):
    args = cli.parse_args(["instagram", removal_type])
    assert args.removal_type == removal_type
    
def test_invalid_removal_type():
    with pytest.raises(SystemExit) as error:
        cli.parse_args(["instagram", "not-a-removal-type"])
    
    assert error.value.code == 2

def test_missing_args():
    with pytest.raises(TypeError) as error:
        cli.parse_args()

def test_missing_removal_type():
    with pytest.raises(SystemExit) as error:
        cli.parse_args(["instagram"])
    
    assert error.value.code == 2

def test_parse_headless():
    args = cli.parse_args(["instagram", "likes", "--headless"])
    assert args.headless == True
    
    args = cli.parse_args(["instagram", "likes"])
    assert args.headless == False
