"""
k8s_delete_from_yaml

Pulled from GitHub PR to allow deletion from yaml using the Kubernetes API.
"""
# Copyright 2018 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# from PR https://github.com/kubernetes-client/python/pull/1392
# if this is ever merged we don't need to pull this file in ourselves
# I thought about writing the code myself but it exists so I might as well use it
# and not waste time making my own hacky solution

# Did have to modify slightly to allow passing of yaml docs vs files

import re
from os import path

import yaml

from kubernetes import client


def delete_from_yaml(k8s_client, yaml_file=None, yaml_objects=None, verbose=False,
                     namespace="default", **kwargs):
    """
    Delete a resource from a yaml file.
    Input:
    yaml_file: string. Contains the path to yaml file.
    k8s_client: an ApiClient object, initialized with the client args.
    verbose: If True, print confirmation from the create action.
        Default is False.
    namespace: string. Contains the namespace to create all
        resources inside. The namespace must preexist otherwise
        the resource creation will fail. If the API object in
        the yaml file already contains a namespace definition
        this parameter has no effect.
    Available parameters for creating <kind>:
    :param async_req bool
    :param str pretty: If 'true', then the output is pretty printed.
    :param str dry_run: When present, indicates that modifications
        should not be persisted. An invalid or unrecognized dryRun
        directive will result in an error response and no further
        processing of the request.
        Valid values are: - All: all dry run stages will be processed
    Raises:
        FailToDeleteError which holds list of `client.rest.ApiException`
        instances for each object that failed to delete.
    """

    if yaml_objects:
        yml_document_all = yaml_objects
    elif yaml_file:
        with open(path.abspath(yaml_file), encoding='utf-8') as y_file:
            yml_document_all = yaml.safe_load_all(y_file)
    else:
        raise ValueError(
            'One of `yaml_file` or `yaml_objects` arguments must be provided')
    for yml_document in yml_document_all:
        try:
            delete_from_dict(k8s_client, yml_document, verbose,
                                namespace=namespace, **kwargs)
        except FailToDeleteError as failure:
            for general_exception in failure.api_exceptions:
                if general_exception.status != 404:
                    print(failure)



def delete_from_dict(k8s_client, yml_document, verbose,
                     namespace="default", **kwargs):
    """
    Delete a kubernetes resource from a dictionary containing valid kubernetes
    API object (i.e. List, Service, etc).
    Input:
    k8s_client: an ApiClient object, initialized with the client args.
    yml_document: a dictionary holding valid kubernetes objects
    verbose: If True, print confirmation from the create action.
        Default is False.
    namespace: string. Contains the namespace to create all
        resources inside. The namespace must preexist otherwise
        the resource creation will fail. If the API object in
        the yaml file already contains a namespace definition
        this parameter has no effect.
    Raises:
        FailToDeleteError which holds list of `client.rest.ApiException`
        instances for each object that failed to create.
    """
    api_exceptions = []
    if "List" in yml_document["kind"]:
        kind = yml_document["kind"].replace("List", "")
        for yml_doc in yml_document["items"]:
            if kind != "":
                yml_doc["apiVersion"] = yml_document["apiVersion"]
                yml_doc["kind"] = kind
            try:
                delete_from_yaml_single_item(
                    k8s_client, yml_doc, verbose, namespace=namespace, **kwargs
                )
            except client.rest.ApiException as api_exception:
                api_exceptions.append(api_exception)
    else:
        try:
            delete_from_yaml_single_item(
                k8s_client, yml_document, verbose,
                namespace=namespace, **kwargs
            )
        except client.rest.ApiException as api_exception:
            api_exceptions.append(api_exception)

    if api_exceptions:
        raise FailToDeleteError(api_exceptions)


def delete_from_yaml_single_item(k8s_client,
                                 yml_document, verbose=False, **kwargs):
    """
    Deletes a single object from yaml.
    """
    # get group and version from apiVersion
    group, _, version = yml_document["apiVersion"].partition("/")
    if version == "":
        version = group
        group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    group = "".join(group.rsplit(".k8s.io", 1))
    # convert group name from DNS subdomain format to
    # python class name convention
    group = "".join(word.capitalize() for word in group.split('.'))
    func = "{0}{1}Api".format(group, version.capitalize()) # pylint: disable=consider-using-f-string
    k8s_api = getattr(client, func)(k8s_client)
    kind = yml_document["kind"]
    kind = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', kind)
    kind = re.sub('([a-z0-9])([A-Z])', r'\1_\2', kind).lower()
    if hasattr(k8s_api, "create_namespaced_{0}".format(kind)): # pylint: disable=consider-using-f-string
        if "namespace" in yml_document["metadata"]:
            namespace = yml_document["metadata"]["namespace"]
            kwargs["namespace"] = namespace
        name = yml_document["metadata"]["name"]
        res = getattr(k8s_api, "delete_namespaced_{}".format(kind))( # pylint: disable=consider-using-f-string
            name=name,
            body=client.V1DeleteOptions(propagation_policy="Background",
                                        grace_period_seconds=5), **kwargs)
    else:
        # get name of object to delete
        name = yml_document["metadata"]["name"]
        kwargs.pop('namespace', None)
        res = getattr(k8s_api, "delete_{}".format(kind))( # pylint: disable=consider-using-f-string
            name=name,
            body=client.V1DeleteOptions(propagation_policy="Background",
                                        grace_period_seconds=5), **kwargs)
    if verbose:
        msg = "{0} deleted.".format(kind) # pylint: disable=consider-using-f-string
        if hasattr(res, 'status'):
            msg += " status='{0}'".format(str(res.status)) # pylint: disable=consider-using-f-string
        print(msg)


class FailToDeleteError(Exception):
    """
    An exception class for handling error if an error occurred when
    handling a yaml file during deletion of the resource.
    """

    def __init__(self, api_exceptions): # pylint: disable=super-init-not-called
        self.api_exceptions = api_exceptions

    def __str__(self):
        msg = ""
        for api_exception in self.api_exceptions:
            msg += "Error from server ({0}):{1}".format( # pylint: disable=consider-using-f-string
                api_exception.reason, api_exception.body)
        return msg
