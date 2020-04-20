import os
import json
import yaml
import requests

SCRIPTS_PATH = "scripts"
ABSOLUTE_HERE = os.path.dirname(os.path.realpath(__file__))
IMAGE_LIST = ["minimal-notebook", "datascience-notebook", "repo2docker"]

API_URLS = {
    "minimal-notebook": "https://hub.docker.com/v2/repositories/jupyter/minimal-notebook/tags",
    "datascience-notebook": "https://hub.docker.com/v2/repositories/jupyter/datascience-notebook/tags",
    "repo2docker": "https://hub.docker.com/v2/repositories/turinginst/bridge-data-env/tags",
}


def compare_tags(tag_dict):
    for image in IMAGE_LIST:
        if tag_dict[image]["old_tag"] == tag_dict[image]["new_tag"]:
            del tag_dict[image]


def find_most_recent_tag_dockerhub(name, url):
    """Find most recent tag of an image from Docker Hub

    Arguments:
        name {str} -- Name of the image
        url {str} -- API URL of the Docker Hub image repository

    Returns:
        new_tag {str} -- Most recent image tag from Docker Hub
    """
    res = json.loads(requests.get(url).text)

    updates_sorted = sorted(res["results"], key=lambda k: k["last_updated"])

    if updates_sorted[-1]["name"] == "latest":
        new_tag = updates_sorted[-2]["name"]
    else:
        new_tag = updates_sorted[-1]["name"]

    return new_tag


def get_config_filepath():
    """Construct the filepath of the JupyterHub config file

    Returns:
        {str} -- Absolute filepath to the JupyterHub config file
    """
    tmp = ABSOLUTE_HERE.split("/")

    if SCRIPTS_PATH in tmp:
        tmp.remove(SCRIPTS_PATH)

    tmp.extend(["config", "config-template.yaml"])

    return "/".join(tmp)


def get_config_tags(tag_dict):
    """Find old image tags from JupyterHub config file

    Arguments:
        tag_dict {dict -- A dictionary containing images and tags
    """
    print("Pulling currently deployed image tags...")

    filename = get_config_filepath()
    with open(filename, "r") as stream:
        config = yaml.safe_load(stream)

    tag_dict["minimal-notebook"]["old_tag"] = config["singleuser"]["image"]["tag"]

    for image in ["datascience-notebook", "repo2docker"]:
        for profile in config["singleuser"]["profileList"]:
            datascience_cond = (image == "datascience-notebook") and (
                profile["display_name"] == "Data Science Environment"
            )
            r2d_cond = (image == "repo2docker") and (
                profile["display_name"] == "Custom repo2docker image"
            )

            if datascience_cond or r2d_cond:
                old_image = profile["kubespawner_override"]["image"]
                old_tag = old_image.split(":")[-1]
                tag_dict[image]["old_tag"] = old_tag


def get_dockerhub_tags(tag_dict):
    """Get image tags from Docker Hub for a dictionary of images

    Arguments:
        tag_dict {dict} -- A dictionary of image names and tags
    """
    print("Pulling most recent tags from Docker Hub...")

    for image in IMAGE_LIST:
        tag_dict[image]["new_tag"] = find_most_recent_tag_dockerhub(
            image, API_URLS[image]
        )


def main():
    """Main function"""
    # Construct dict for image tags
    tag_dict = {}
    for image in IMAGE_LIST:
        tag_dict[image] = {}

    get_config_tags(tag_dict)
    get_dockerhub_tags(tag_dict)
    compare_tags(tag_dict)

    if bool(tag_dict):
        print("Tags to be updated: [name: old_tag...new_tag]")
        for image in tag_dict.keys():
            print(
                f"{image}: {tag_dict[image]['old_tag']}...{tag_dict[image]['new_tag']}"
            )
    else:
        print("Image tags are up to date!")


if __name__ == "__main__":
    main()
