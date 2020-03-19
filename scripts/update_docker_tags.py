import os
import json
import requests

HERE = os.path.dirname(__file__)
ABSOLUTE_HERE = os.path.dirname(os.path.realpath(__file__))


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


def get_dockerhub_tags(tag_dict):
    """Get image tags from Docker Hub for a dictionary of images

    Arguments:
        tag_dict {dict} -- A dictionary of image names and tags
    """
    api_urls = {
        "minimal-notebook": "https://hub.docker.com/v2/repositories/jupyter/minimal-notebook/tags",
        "datascience-notebook": "https://hub.docker.com/v2/repositories/jupyter/datascience-notebook/tags",
        "repo2docker": "https://hub.docker.com/v2/repositories/turinginst/bridge-data-env/tags",
    }

    for image in api_urls.keys():
        tag_dict[image] = {}
        tag_dict[image]["old_tag"] = find_most_recent_tag_dockerhub(
            image, api_urls[image]
        )


def get_config_filepath():
    """Construct the filepath of the JupyterHub config file

    Returns:
        {str} -- Absolute filepath to the JupyterHub config file
    """
    tmp = ABSOLUTE_HERE.split("/")

    if HERE in tmp:
        tmp.remove(HERE)

    tmp.extend(["config", "config-template.yaml"])

    return "/".join(tmp)


def main():
    """Main function"""
    # api_urls = {
    #     "jupyterhub": "https://raw.githubusercontent.com/alan-turing-institute/bridge-data-platform/master/config/config-template.yaml",
    #     "minimal-notebook": "https://hub.docker.com/v2/repositories/jupyter/minimal-notebook/tags",
    #     "datascience-notebook": "https://hub.docker.com/v2/repositories/jupyter/datascience-notebook/tags",
    #     "repo2docker": "https://hub.docker.com/v2/repositories/turinginst/bridge-data-env/tags",
    # }

    tag_dict = {}
    get_dockerhub_tags(tag_dict)


if __name__ == "__main__":
    main()
