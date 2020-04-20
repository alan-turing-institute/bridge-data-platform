# 3D Bridge Data Platform

This repository manages the JupyterHub deployment on Kubernetes that hosts the 3D bridge data platform.

:construction: This repo is still being actively developed and is subject to change :construction:

| | CI Status |
| :--- | :--- |
| YAML | ![YAML lint](https://github.com/alan-turing-institute/bridge-data-platform/workflows/YAML%20lint/badge.svg?branch=master) |
| Deployment | [![Build Status](https://dev.azure.com/bridge-data-platform/bridge-data-platform/_apis/build/status/Continuous%20Deployment%20Helm%20Upgrade?branchName=master)](https://dev.azure.com/bridge-data-platform/bridge-data-platform/_build/latest?definitionId=2&branchName=master) |

**Table of Contents:**

- [What is a JupyterHub?](#what-is-a-jupyterhub)
- [Why a Kubernetes cluster?](#why-a-kubernetes-cluster)
- [Repository Overview](#repository-overview)
  - [Jupyter Configuration](#jupyterhub-configuration)
  - [Continuous Deployment](#continuous-deployment)
  - [Testing](#testing)
  - [Other Scripts](#other-scripts)

---

## What is a JupyterHub?

A JupyterHub is infrastructure that maps users onto computing resources.
Using specialised spawners and authentication processes, any sub-group of users can be mapped onto any type of computational resource.
A JupyterHub is one solution to the problem _I have computers that I would like to grant people access to, and Jupyter Notebooks are a good interface in this scenario_. Each user also gets a home directory with storage (separate from other users), their own compute environment (managed by Docker containers, also separated), and data can be shared with all users via data mounts.

Full Jupyter Hub documentation can be found here: <https://jupyterhub.readthedocs.io>

For more information on how the compute environment is managed, please see the Data Environment repo: [alan-turing-institute/bridge-data-environment](https://github.com/alan-turing-institute/bridge-data-environment)

## Why a Kubernetes cluster?

We chose a Kubernetes cluster to deploy the JupyterHub infrastructure onto since such clusters can scale (flexibly and automatically) with the amount of users at any given time.
This means that when fewer people are accessing the data, the Kubernetes cluster will shrink to the minimum compute resources required.
This makes it a much more financially economical choice.

Full documentation for JupyterHub on Kubernetes can be found here: <https://zero-to-jupyterhub-k8s.readthedocs.io>

## Repository Overview

### JupyterHub Configuration

The JupyterHub configuration is described (mostly) by the [`config/config-template.yaml`](config/config-template.yaml) file.
This is a template file since any secrets used during deployment have been redeacted (see the [Continuous Deployment](#continuous-deployment) section).

The configuration template is a YAML file that provides extra or overwrites values in the JupyterHub Helm Chart.
(Full documentation on Helm Charts can be found here: <https://helm.sh/docs/topics/charts/>).
The values in the configuration template govern the following:

- What authentication process we use, which users are allowed access and which of them are allowed admin access (under the `auth` flag)
- Culling of Kubernetes pods so that we can utilise the cluster as economically as possible (under the `cull` flag)
- The network policies of the JupyterHub, what kinds of inbound/outbound traffic are permitted
- Scheduling and packing of users onto cluster nodes so that scaling only happens when absolutely necessary (under the `scheduling` flag)
- What computational resources, environments and restrictions are placed on a single users server (under the `singleuser` flag)

### Continuous Deployment

This repository uses a continuous deployment pipeline to keep the configuration of the JupyterHub deployment up-to-date with the status of the repo.
This pipeline is run by [Azure Pipelines](https://docs.microsoft.com/en-gb/azure/devops/pipelines/?view=azure-devops) and the configuration can be viewed here: [`.az-pipelines/continuous-deployment.yml`](.az-pipelines/continuous-deployment.yml).

The pipeline is triggered by any merge to the master branch.
It connects to the Kubernetes cluster using a [Service Principal](https://docs.microsoft.com/en-gb/azure/active-directory/develop/app-objects-and-service-principals), installs [Helm](https://helm.sh) for interacting with the chart, and downloads the secrets from an [Azure Key Vault](https://docs.microsoft.com/en-gb/azure/key-vault/).
The secrets are then templated into the configuration file using [`sed`](https://www.gnu.org/software/sed/manual/sed.html), then the JupyterHub Helm Chart is downloaded and upgraded according to the new configuration file.

:warning: No manual updates to the configuration of the JupyterHub deployment should need to take place.
It should all be facilitated through this GitHub repository. :warning:

### Testing

Helm Charts are described by YAML files and it is very sensitive to the correct formatting of these files.
Unfortunately, Helm does fail silently when it finds a mis-formatted YAML file.
To combat this, this repository uses [YAML Lint](https://yamllint.readthedocs.io) to check the YAML files and reduce the probability of Helm failures due to mis-formatted YAML files.
This linter is applied as a [GitHub Action](https://help.github.com/en/actions), the configuration for which can be found here: [`.github/workflows/yamllint.yml`](.github/workflows/yamllint.yml).

:warning: This check is [Required Status Check](https://help.github.com/en/github/administering-a-repository/about-required-status-checks) for any Pull Request opened on this repository.
This check _must_ pass in order for the changes to be merged. :warning:

### Other Scripts

The [`scripts`](./scripts) directory contains some other scripts that may come in handy when managing the JupyterHub deployment.

#### `update_docker_tags.py`

The Docker images describing the computational environments are referenced by their image tags in the JupyterHub configuration file.
When an update is made to the cluster, these specific tags of the images are pulled to make sure they are quickly available for all users when they are requesting their servers.

Running `update_docker_tags.py` will 
