# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Gonzalo Pena-Castellanos (@goanpeca)
#
# Licensed under the terms of the MIT License
# (See LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Appveyor Python Client."""

# Standard library imports
import json
import textwrap

# Third party imports
import requests


# --- Errors
class AppveyorError(Exception):
    pass


class AppveyorClientError(Exception):
    pass


# --- Client
class AppveyorClient(object):
    """
    Appveyor python client.

    https://www.appveyor.com/docs/api/
    """

    _HEADERS = {
        'Content-type': 'application/json',
        'User-Agent': 'Appveyor Python Client',
    }

    def __init__(self, token, endpoint=None):
        """Appveyor python client."""
        self._endpoint = endpoint or 'https://ci.appveyor.com/'
        self._session = requests.Session()

        # Groups
        self.users = Users(self)
        self.collaborators = Collaborators(self)
        self.roles = Roles(self)
        self.projects = Projects(self)
        self.builds = Builds(self)
        self.environments = Environments(self)
        self.deployments = Deployments(self)

        # Setup
        self._session.headers.update(self._HEADERS)
        self._authenticate(token)

    # --- Helpers
    def _make_url(self, url):
        """Create full api url."""
        return '{}{}'.format(self._endpoint, url)

    @staticmethod
    def _parse_response_contents(response):
        """Parse response and convert to json if possible."""
        status_code = response.status_code
        try:
            if status_code == 200:
                contents = response.json()
            else:
                contents = {}
        except:
            error = response.text.strip()
            if not error:
                error_msg = textwrap.dedent('''
                    Unexpected error
                        Possible reasons are:
                         - Communication with Appveyor has failed.
                         - Insufficient permissions.
                         - Invalid contents returned.
                    ''')[1:]
            contents = {
                'status_code': status_code,
                'error': error_msg,
            }
            raise AppveyorError(contents)

        if status_code == 200:
            return contents
        elif status_code == 204:
            return
        else:
            contents['status_code'] = status_code
            raise AppveyorError(contents)

    def _get(self, url, data=None, json=None):
        """Send GET request with given url."""
        response = self._session.get(self._make_url(url))
        return self._parse_response_contents(response)

    def _post(self, url, data=None, json=None):
        """Send POST request with given url and keyword args."""
        response = self._session.post(
            self._make_url(url), data=data, json=json)
        return self._parse_response_contents(response)

    def _put(self, url, data=None, json=None):
        """Send PUT request with given url."""
        response = self._session.put(self._make_url(url), data=data, json=json)
        return self._parse_response_contents(response)

    def _delete(self, url, data=None, json=None):
        """Send DELETE request with given url."""
        response = self._session.delete(self._make_url(url))
        return self._parse_response_contents(response)

    def _request(self, method_url, body=None, json=None):
        """"""
        method, url = method_url.split(' ')
        func = getattr(self, '_{}'.format(method.lower()))
        return func(url, data=body, json=json)

    def _authenticate(self, token):
        """Authenticate appveyor with bearer token."""
        url = '/api/roles'
        self._session.headers['Authorization'] = "Bearer {}".format(token)
        return self._get(url)

    def account_slug_for_repo(self, repo_full_name):
        """Return the account name and project slug for a repo full name."""
        projects = self.projects.get()
        for project in projects:
            if project['repositoryName'].lower() == repo_full_name.lower():
                account_name = project['accountName']
                project_slug = project['slug']
                break

        if account_name is None and project_slug is None:
            raise AppveyorError("Repository full name '{}'"
                                "is invalid".format(repo_full_name))

        return account_name, project_slug


class _Base(object):
    """Base entity class."""

    def __init__(self, client):
        """Base entity class."""
        self._client = client


class Users(_Base):
    """Appveyor user api methods."""

    def get(self, user_id=None):
        """
        Get users or user specified by user_id.

        https://www.appveyor.com/docs/api/team/#get-users
        https://www.appveyor.com/docs/api/team/#get-user
        """
        method_url = 'GET /api/users'

        if user_id:
            method_url += '/{user_id}'

        method_url = method_url.format(user_id=user_id)
        return self._client._request(method_url)

    def add(self,
            full_name,
            email,
            role_id,
            password=None,
            generate_password=False):
        """
        Add user.

        https://www.appveyor.com/docs/api/team/#add-user
        """
        method_url = 'POST /api/users'
        data = {
            "fullName": full_name,
            "email": email,
            "roleId": role_id,
            "generatePassword": generate_password,
        }

        if not generate_password:
            if password:
                data["password"] = password
                data["confirmPassword"] = password
            else:
                error_msg = 'Must provide a password if generate is Fasle'
                raise AppveyorClientError(error_msg)
        body = json.dumps(data)
        return self._client._request(method_url, body=body)

    def update(self, user):
        """
        Update user.

        ::

            user = {
               "userId": 3019,
               "fullName": "John Smith",
               "email": "john@smith.com",
               "password": None,
               "roleId": 4,
               "successfulBuildNotification": "all",
               "failedBuildNotification": "all",
               "notifyWhenBuildStatusChangedOnly": True
            }

        https://www.appveyor.com/docs/api/team/#update-user
        """
        method_url = 'PUT /api/users'
        body = json.dumps(user)
        return self._client._request(method_url, body=body)

    def delete(self, user_id):
        """
        Delete user.

        https://www.appveyor.com/docs/api/team/#delete-user
        """
        method_url = 'DELETE /api/users/{user_id}'
        method_url = method_url.format(user_id=user_id)
        return self._client._request(method_url)


class Collaborators(_Base):
    """Appveyor collaborator api methods."""

    def get(self, user_id=None):
        """
        Get collaborators or collaborator specified by user id.

        https://www.appveyor.com/docs/api/team/#get-collaborators
        https://www.appveyor.com/docs/api/team/#get-collaborator
        """
        method_url = 'DELETE /api/users'

        if user_id:
            method_url += '/{user_id}'

        method_url = method_url.format(user_id=user_id)
        return self._client._request(method_url)

    def add(self, email, role_id):
        """
        Add collaborator.

        https://www.appveyor.com/docs/api/team/#add-collaborator
        """
        method_url = 'POST /api/collaborators'
        data = {
            "email": email,
            "roleId": role_id,
        }
        body = json.dumps(data)
        return self._client._request(method_url, body=body)

    def update(self, user_id, role_id):
        """
        Update collaborator.

        https://www.appveyor.com/docs/api/team/#update-collaborator
        """
        method_url = 'PUT /api/collaborators'
        data = {
            "userId": user_id,
            "roleId": role_id,
        }
        body = json.dumps(data)
        return self._client._request(method_url, body=body)

    def delete(self, user_id):
        """
        Delete collaborator.

        https://www.appveyor.com/docs/api/team/#delete-collaborator
        """
        method_url = 'DELETE /api/collaborators/{user_id}'
        method_url = method_url.format(user_id=user_id)
        return self._client._request(method_url)


class Roles(_Base):
    """Appveyor role api methods."""

    def get(self, role_id=None):
        """
        Get roles or role specified by role id.

        https://www.appveyor.com/docs/api/team/#get-roles
        """
        method_url = 'GET /api/roles'

        if role_id:
            method_url += '/{role_id}'

        return self._client._request(method_url)

    def add_role(self, name):
        """
        Add role.

        https://www.appveyor.com/docs/api/team/#add-role
        """
        method_url = 'POST /api/roles'
        data = {"name": name, }
        body = json.dumps(data)
        return self._client._request(method_url, body=body)

    def update_role(self, role):
        """
        Update role.

        ::

            {
               "roleId":3040,
               "name":"My Role",
               "isSystem":false,
               "created":"2014-03-18T20:12:08.4749886+00:00",
               "groups":[
                  {
                     "name":"Projects",
                     "permissions":[
                        {
                           "name":"ManageProjects",
                           "description":"Create, project settings",
                           "allowed":true
                        },
                        {
                           "name":"UpdateProjectSettings",
                           "description":"Update project settings",
                           "allowed":true
                        },
                        {
                           "name":"RunProjectBuild",
                           "description":"Run project builds",
                           "allowed":false
                        },
                        {
                           "name":"DeleteProjectBuilds",
                           "description":"Delete project builds",
                           "allowed":false
                        }
                     ]
                  },
                  {
                     "name":"Environments",
                     "permissions":[
                        {
                           "name":"ManageEnvironments",
                           "description":"Create environment settings",
                           "allowed":false
                        },
                        {
                           "name":"UpdateEnvironmentSettings",
                           "description":"Update environment settings",
                           "allowed":false
                        },
                        {
                           "name":"DeployToEnvironment",
                           "description":"Deploy to environment",
                           "allowed":false
                        }
                     ]
                  },
                  {
                     "name":"Account",
                     "permissions":[
                        {
                           "name":"UpdateAccountDetails",
                           "description":"Update account details",
                           "allowed":false
                        }
                     ]
                  },
                  {
                     "name":"Users",
                     "permissions":[
                        {
                           "name":"AddUser",
                           "description":"Add new user",
                           "allowed":false
                        },
                        {
                           "name":"UpdateUserDetails",
                           "description":"Update user details",
                           "allowed":false
                        },
                        {
                           "name":"DeleteUser",
                           "description":"Delete user",
                           "allowed":false
                        }
                     ]
                  },
                  {
                     "name":"Roles",
                     "permissions":[
                        {
                           "name":"AddRole",
                           "description":"Add new role",
                           "allowed":false
                        },
                        {
                           "name":"UpdateRoleDetails",
                           "description":"Update role details",
                           "allowed":false
                        },
                        {
                           "name":"DeleteRole",
                           "description":"Delete role",
                           "allowed":false
                        }
                     ]
                  },
                  {
                     "name":"User",
                     "permissions":[
                        {
                           "name":"ConfigureApiKeys",
                           "description":"Generate API keys",
                           "allowed":false
                        }
                     ]
                  }
               ]
            }

        https://www.appveyor.com/docs/api/team/#update-role
        """
        method_url = 'PUT /api/roles'
        body = json.dumps(role)
        return self._client._request(method_url, body=body)

    def delete_role(self, role_id):
        """
        Delete role.

        https://www.appveyor.com/docs/api/team/#delete-role
        """
        method_url = 'DELETE /api/roles/{role_id}'
        return self._client._request(method_url)


class Projects(_Base):
    """Appveyor project api methods."""

    def get(self):
        """
        Get projects.

        https://www.appveyor.com/docs/api/projects-builds/#get-projects
        """
        method_url = 'GET /api/projects'
        return self._client._request(method_url)

    def last_build(self, account_name, project_slug):
        """
        Get project last build.

        https://www.appveyor.com/docs/api/projects-builds/#get-project-last-build
        """
        method_url = 'GET /api/projects/{account_name}/{project_slug}'
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)
        return self._client._request(method_url)

    def last_branch_build(self, account_name, project_slug, build_branch):
        """
        Get project last branch build.

        https://www.appveyor.com/docs/api/projects-builds/#get-project-last-branch-build
        """
        method_url = ('GET /api/projects/{account_name}/{project_slug}'
                      '/branch/{build_branch}')
        method_url = method_url.format(
            account_name=account_name,
            project_slug=project_slug,
            build_branch=build_branch)
        return self._client._request(method_url)

    def build(self, account_name, project_slug, build_version):
        """
        Get project build by version.

        https://www.appveyor.com/docs/api/projects-builds/#get-project-build-by-version
        """
        method_url = ('GET /api/projects/{account_name}/{project_slug}'
                      '/build/{build_version}')
        method_url = method_url.format(
            account_name=account_name,
            project_slug=project_slug,
            build_version=build_version)
        return self._client._request(method_url)

    def history(self,
                account_name,
                project_slug,
                records_per_page=50,
                start_build_id=None,
                branch=None):
        """
        Get project history.

        https://www.appveyor.com/docs/api/projects-builds/#get-project-history
        """
        method_url = ('GET /api/projects/{account_name}/{project_slug}'
                      '/history?recordsNumber={records_per_page}')

        if start_build_id:
            method_url += '&startBuildId={start_build_id}'
        else:
            start_build_id = ''
            method_url += '{start_build_id}'

        if branch:
            method_url += '&branch={branch}'
        else:
            branch = ''
            method_url += '{branch}'

        method_url = method_url.format(
            account_name=account_name,
            project_slug=project_slug,
            records_per_page=records_per_page,
            start_build_id=start_build_id,
            branch=branch)
        return self._client._request(method_url)

    def deployments(self, account_name, project_slug):
        """
        Get project deployments.

        https://www.appveyor.com/docs/api/projects-builds/#get-project-deployments
        """
        method_url = ('GET /api/projects/{account_name}/{project_slug}'
                      '/deployments')
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)
        return self._client._request(method_url)

    def settings(self, account_name, project_slug):
        """
        Get project settings in YAML.

        https://www.appveyor.com/docs/api/projects-builds/#get-project-settings-in-yaml
        """
        method_url = ('GET /api/projects/{account_name}/{project_slug}'
                      '/settings/yaml')
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)
        return self._client._request(method_url)

    def add(self, repository_provider, repository_name):
        """
        Add project.

        https://www.appveyor.com/docs/api/projects-builds/#add-project
        """
        method_url = 'POST /api/projects'
        providers = [
            'gitHub', 'bitBucket', 'vso', 'gitLab', 'kiln', 'stash', 'git',
            'mercurial', 'subversion'
        ]

        if repository_provider not in providers:
            error_msg = ('Invalid repository provider. Must be one of '
                         '{}'.format(str(providers)))
            raise AppveyorClientError(error_msg)

        data = {
            "repositoryProvider": repository_provider,
            "repositoryName": repository_name,
        }

        body = json.dumps(data)
        return self._client._request(method_url, body=body)

    def update(self, account_name, project_slug, project):
        """
        Update project.

        ::

            {
               "projectId": 43682,
               "accountId": 2,
               "accountName": "appvyr",
               "builds": [],
               "name": "demo-app",
               "slug": "demo-app-335",
               "versionFormat": "1.0.{build}",
               "nextBuildNumber": 1,
               "repositoryType": "gitHub",
               "repositoryScm": "git",
               "repositoryName": "FeodorFitsner/demo-app",
               "repositoryBranch": "master",
               "webhookId": "rca5vb5qqu",
               "webhookUrl": "https://ci.appveyor.com/api/github/webhook?id=r",
               "isPrivate": false,
               "ignoreAppveyorYml": False,
               "skipBranchesWithoutAppveyorYml": False,
               "configuration": {
                  "initScripts": [],
                  "includeBranches": [],
                  "excludeBranches": [],
                  "onBuildSuccessScripts": [],
                  "onBuildErrorScripts": [],
                  "patchAssemblyInfo": False,
                  "assemblyInfoFile": "**\\AssemblyInfo.*",
                  "assemblyVersionFormat": "{version}",
                  "assemblyFileVersionFormat": "{version}",
                  "assemblyInformationalVersionFormat": "{version}",
                  "operatingSystem": [],
                  "services": [],
                  "shallowClone": False,
                  "environmentVariables": [],
                  "environmentVariablesMatrix": [],
                  "installScripts": [],
                  "hostsEntries": [],
                  "buildMode": "msbuild",
                  "platform": [],
                  "configuration": [],
                  "packageWebApplicationProjects": False,
                  "packageWebApplicationProjectsXCopy": False,
                  "packageAzureCloudServiceProjects": False,
                  "packageNuGetProjects": False,
                  "msBuildVerbosity": "minimal",
                  "buildScripts": [],
                  "beforeBuildScripts": [],
                  "afterBuildScripts": [],
                  "testMode": "auto",
                  "testAssemblies": [],
                  "testCategories": [],
                  "testCategoriesMatrix": [],
                  "testScripts": [],
                  "beforeTestScripts": [],
                  "afterTestScripts": [],
                  "deployMode": "providers",
                  "deployments": [],
                  "deployScripts": [],
                  "beforeDeployScripts": [],
                  "afterDeployScripts": [],
                  "matrixFastFinish": False,
                  "matrixAllowFailures": [],
                  "artifacts": [],
                  "notifications": []
               },
               "nuGetFeed": {
                  "id": "demo-app-tw5iw2wk3bl1",
                  "name": "Project demo-app",
                  "publishingEnabled": False,
                  "created": "2014-08-16T00:52:16.9886427+00:00"
               },
               "securityDescriptor": {
                  "accessRightDefinitions": [
                     {
                        "name": "View",
                        "description": "View"
                     },
                     {
                        "name": "RunBuild",
                        "description": "Run build"
                     },
                     {
                        "name": "Update",
                        "description": "Update settings"
                     },
                     {
                        "name": "Delete",
                        "description": "Delete project"
                     }
                  ],
                  "roleAces": [
                     {
                        "roleId": 4,
                        "name": "Administrator",
                        "isAdmin": True,
                        "accessRights": [
                           {
                              "name": "View",
                              "allowed": True
                           },
                           {
                              "name": "RunBuild",
                              "allowed": True
                           },
                           {
                              "name": "Update",
                              "allowed": True
                           },
                           {
                              "name": "Delete",
                              "allowed": True
                           }
                        ]
                     },
                     {
                        "roleId": 5,
                        "name": "User",
                        "isAdmin": False,
                        "accessRights": [
                           {
                              "name": "View"
                           },
                           {
                              "name": "RunBuild"
                           },
                           {
                              "name": "Update"
                           },
                           {
                              "name": "Delete"
                           }
                        ]
                     }
                  ]
               },
               "created": "2014-08-16T00:52:15.6604826+00:00"
            }

        https://www.appveyor.com/docs/api/projects-builds/#update-project
        """
        method_url = ('PUT /api/projects/{account_name}/{project_slug}'
                      '/settings/build-number')
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)
        body = json.dumps(project)
        return self._client._request(method_url, body=body)

    def update_settings(self, account_name, project_slug, settings):
        """
        Update project settings in YAML.

        ::

            version: 1.0.{build}
            build:
              project: MySolution.sln
              verbosity: minimal
              publish_wap: true
              ...


        https://www.appveyor.com/docs/api/projects-builds/#update-project-settings-in-yaml
        """
        method_url = ('PUT /api/projects/{account_name}/{project_slug}'
                      '/settings/build-number')
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)

        body = json.dumps(settings)
        return self._client._request(method_url, body=body)

    def update_build_number(self, account_name, project_slug,
                            next_build_number):
        """
        Update project build number.

        https://www.appveyor.com/docs/api/projects-builds/#update-project-build-number
        """
        method_url = ('PUT /api/projects/{account_name}/{project_slug}'
                      '/settings/build-number')
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)
        data = {'nextBuildNumber': next_build_number}
        return self._client._request(method_url, json=data)

    def delete_build_cache(self, account_name, project_slug):
        """
        Delete project build cache.

        https://www.appveyor.com/docs/api/projects-builds/#delete-project-build-cache
        """
        method_url = ('DELETE /api/projects/{account_name}/{project_slug}'
                      '/buildcache')
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)
        return self._client._request(method_url)

    def delete(self, account_name, project_slug):
        """
        Delete project.

        https://www.appveyor.com/docs/api/projects-builds/#delete-project
        """
        method_url = 'DELETE /api/projects/{account_name}/{project_slug}'
        method_url = method_url.format(
            account_name=account_name, project_slug=project_slug)
        return self._client._request(method_url)


class Builds(_Base):
    """Appveyor build api methods."""

    def start(self,
              account_name,
              project_slug,
              branch=None,
              pull_request_number=None,
              commit=None,
              environment_variables={}):
        """
        Start build for branch, commit or pull request (GitHub only).

        https://www.appveyor.com/docs/api/projects-builds/#start-build-of-branch-most-recent-commit
        https://www.appveyor.com/docs/api/projects-builds/#start-build-of-specific-branch-commit
        https://www.appveyor.com/docs/api/projects-builds/#start-build-of-pull-request-github-only
        """
        method_url = 'POST /api/builds'
        data = {
            'accountName': account_name,
            'projectSlug': project_slug,
        }

        if branch and not pull_request_number and not commit:
            data['branch'] = branch
        elif commit and not commit and not pull_request_number:
            data['commitId'] = commit
        elif pull_request_number and not commit and not branch:
            data['pullRequestId'] = pull_request_number
        else:
            error_msg = ('Must provide only one of branch or one pull request '
                         'id or one commit id')
            raise AppveyorClientError(error_msg)

        if environment_variables:
            data['environmentVariables'] = environment_variables

        body = json.dumps(data)
        return self._client._request(method_url, body=body)

    def cancel(self, account_name, project_slug, build_version):
        """
        Cancel build.

        https://www.appveyor.com/docs/api/projects-builds/#cancel-build
        """
        method_url = ('DELETE /api/builds/{account_name}/{project_slug}'
                      '/{build_version}')
        method_url = method_url.format(
            account_name=account_name,
            project_slug=project_slug,
            build_version=build_version)
        return self._client._request(method_url)

    def log(self, job_id):
        """
        Download build log.

        https://www.appveyor.com/docs/api/projects-builds/#download-build-log
        """
        method_url = 'GET /api/buildjobs/{job_id}/log'
        method_url = method_url.format(job_id=job_id)
        return self._client._request(method_url)


class Environments(_Base):
    """
    Appveyor environment api methods.

    https://www.appveyor.com/docs/api/environments-deployments/#environments
    """

    def get(self):
        """
        Get environments.

        https://www.appveyor.com/docs/api/environments-deployments/#get-environments
        """
        method_url = 'GET /api/environments'
        return self._client._request(method_url)

    def settings(self, deployment_environment_id):
        """
        Get environment settings.

        https://www.appveyor.com/docs/api/environments-deployments/#get-environment-settings
        """
        method_url = ('GET /api/environments/'
                      '{deployment_environment_id}/settings')
        method_url = method_url.format(
            deployment_environment_id=deployment_environment_id, )
        return self._client._request(method_url)

    def deployments(self, deployment_environment_id):
        """
        Get environment deployments.

        https://www.appveyor.com/docs/api/environments-deployments/#get-environment-deployments
        """
        method_url = ('GET /api/environments/'
                      '{deployment_environment_id}/deployments')
        method_url = method_url.format(
            deployment_environment_id=deployment_environment_id, )
        return self._client._request(method_url)

    def add(self, environment):
        """
        Add environment.

        ::

            example_environment = {
               "name": "production",
               "provider": "FTP",
               "settings": {
                  "providerSettings": [
                     {
                        "name":"server",
                        "value": {
                           "value": "ftp.myserver.com",
                           "isEncrypted": False
                        }
                     },
                     {
                        "name": "username",
                        "value": {
                           "value": "ftp-user",
                           "isEncrypted": False
                        }
                     },
                     {
                        "name": "password",
                        "value": {
                           "value": "password",
                           "isEncrypted": True
                        }
                     }
                  ],
                  "environmentVariables": [
                     {
                        "name": "my-var",
                        "value": {
                           "value": "123",
                           "isEncrypted": False
                        }
                     }
                  ]
               }
            }

        https://www.appveyor.com/docs/api/environments-deployments/#add-environment
        """
        method_url = 'POST /api/environments'
        body = json.dumps(environment)
        return self._client._request(method_url, body=body)

    def update(self, environment):
        """

        ::
            {
               "deploymentEnvironmentId": 3018,
               "name": "production",
               "environmentAccessKey": "gi3ttevuk7123",
               "settings": {
                  "providerSettings": [
                     {
                        "name": "server",
                        "value": {
                           "isEncrypted": False,
                           "value": "ftp.myserver.com"
                        }
                     },
                     {
                        "name": "username",
                        "value": {
                           "isEncrypted": False,
                           "value": "ftp-user"
                        }
                     },
                     {
                        "name": "password",
                        "value": {
                           "isEncrypted": True,
                           "value": "password"
                        }
                     }
                  ],
                  "environmentVariables": [
                     {
                        "name": "my-var",
                        "value": {
                           "isEncrypted": False,
                           "value": "123"
                        }
                     }
                  ],
                  "provider": "FTP"
               }
            }

        https://www.appveyor.com/docs/api/environments-deployments/#update-environment
        """
        method_url = 'PUT /api/environments'
        body = json.dumps(environment)
        return self._client._request(method_url, body=body)

    def delete(self, deployment_environment_id):
        """
        Delete environment

        https://www.appveyor.com/docs/api/environments-deployments/#delete-environment
        """
        method_url = 'DELETE /api/environments/{deployment_environment_id}'
        method_url = method_url.format(
            deployment_environment_id=deployment_environment_id, )
        return self._client._request(method_url)


class Deployments(_Base):
    """
    Appveyor deployment api methods.

    https://www.appveyor.com/docs/api/environments-deployments/#deployments
    """

    def get(self, deployment_id):
        """
        Get deployment.

        https://www.appveyor.com/docs/api/environments-deployments/#get-deployment
        """
        method_url = 'GET /api/deployments/{deployment_id}'
        method_url = method_url.format(deployment_id=deployment_id)
        return self._client._request(method_url)

    def start(self,
              account_name,
              project_slug,
              environment_name,
              build_version,
              build_job_id=None,
              environment_variables={}):
        """
        Start deployment.

        https://www.appveyor.com/docs/api/environments-deployments/#start-deployment
        """
        method_url = 'POST /api/deployments'
        data = {
            "environmentName": environment_name,
            "accountName": account_name,
            "projectSlug": project_slug,
            "buildVersion": build_version,  # Build to deploy
            "environmentVariables": environment_variables
        }

        # Optional job id with artifacts if build contains multiple jobs
        if build_job_id:
            data["buildJobId"] = build_job_id

        body = json.dumps(data)
        return self._client._request(method_url, body=body)

    def cancel(self, deployment_id):
        """
        Cancel deployment.

        https://www.appveyor.com/docs/api/environments-deployments/#cancel-deployment
        """
        method_url = 'PUT /api/deployments/stop'
        data = {"deploymentId": deployment_id}
        body = json.dumps(data)
        return self._client._request(method_url, body=body)
