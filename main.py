#main.py
"""
GitHub Action Code to update README file with provided images randomly.
"""

import os
import re
import sys
import base64
import requests
import random
from github import Github, GithubException

START_COMMENT = '<!--START_SECTION:update_image-->'
END_COMMENT = '<!--END_SECTION:update_image-->'
IMAGE_REPL = f"{START_COMMENT}[\\s\\S]+{END_COMMENT}"

REPO = os.getenv("INPUT_README_REPOSITORY")
IMG_REPO = os.getenv("INPUT_IMG_REPOSITORY")
IMG_PATH = os.getenv("INPUT_IMG_PATH")
GHTOKEN = os.getenv("INPUT_GH_TOKEN")
COMMIT_MSG = os.getenv("INPUT_COMMIT_MESSAGE")
WIDTH = os.getenv("INPUT_WIDTH")
HEIGHT = os.getenv("INPUT_HEIGHT")
ALIGN = os.getenv("INPUT_ALIGN")
IMG_ALT = os.getenv("INPUT_IMG_ALT")

VALID_IMAGES_EXT = ['png', 'jpg', 'jpeg', 'gif', 'svg']


def verify_image_ext(image):
    ''' Validate image obtained '''
    global VALID_IMAGES_EXT
    # if image.path.split('/')[-1].split('.')[-1].lower() not in VALID_IMAGES_EXT:
    #     print(f"Please make sure image is one of following type {VALID_IMAGES_EXT}, error caused by image - {image.path}")
    #     return False
    return True

def get_image_tag(repo):
    ''' Get new image tag <img> to place in README '''
    global IMG_PATH

    file_content = repo.get_contents(IMG_PATH)
    choose_from = file_content.decoded_content.decode()
    choose_from = choose_from[:-1] if choose_from[-1] == "" else choose_from
    images = random.sample(choose_from.split("\n"), 3)
    is_image = verify_image_ext(images)
    if not is_image:
        sys.exit(1)
    # img_src = image.download_url
    img_src1 = images[0]
    img_src2 = images[1]
    img_src3 = images[2]
    img_tag = f"""<picture>
                    <img src='{img_src1}' height={HEIGHT} width={WIDTH} align={ALIGN} alt={IMG_ALT} />
                  </picture>
                  <br>
                  <picture>
                    <img src='{img_src2}' height={HEIGHT} width={WIDTH} align={ALIGN} alt={IMG_ALT} />
                  </picture>
                  <br>
                  <picture>
                    <img src='{img_src3}' height={HEIGHT} width={WIDTH} align={ALIGN} alt={IMG_ALT} />
                  </picture>"""
    return img_tag

def decode_readme(data: str) -> str:
    '''Decode the contents of old readme'''
    decoded_bytes = base64.b64decode(data)
    return str(decoded_bytes, 'utf-8')

def generate_new_readme(readme: str, image_tag: str) -> str:
    '''Generate a new Readme.md'''
    update_readme_with = f"{START_COMMENT}\n{image_tag}\n{END_COMMENT}"
    return re.sub(IMAGE_REPL, update_readme_with, readme)

if __name__ == "__main__":
    g = Github(GHTOKEN)
    try:
        readme_repo = g.get_repo(REPO)
        img_repo = g.get_repo(IMG_REPO)
    except GithubException:
        print("Authentication Error. Try saving a GitHub Token in your Repo Secrets or Use the GitHub Actions Token, which is automatically used by the action.")
        sys.exit(1)
    image_tag = get_image_tag(img_repo)
    readme_obj = readme_repo.get_readme()
    readme_content = readme_obj.content
    readme_content_decoded = decode_readme(readme_content)
    new_readme = generate_new_readme(readme=readme_content_decoded, image_tag=image_tag)
    if readme_content_decoded != new_readme:
        readme_repo.update_file(path=readme_obj.path, message=COMMIT_MSG,
                             content=new_readme, sha=readme_obj.sha)
        print("Success")
    else:
        print("No change")