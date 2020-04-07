# -*- coding: utf-8 -*-
#
# This file is part of DataCite.
#
# Copyright (C) 2015, 2016 CERN.
#
# DataCite is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Tests for REST API."""

from __future__ import absolute_import, print_function

import io
import json
from os.path import dirname, join

import pytest
import responses
from helpers import RESTURL, get_credentials, get_rest

from datacite.errors import DataCiteForbiddenError, DataCiteGoneError, \
    DataCiteNoContentError, DataCiteNotFoundError, DataCiteServerError, \
    DataCiteUnauthorizedError


@pytest.mark.pw
def test_rest_create_draft():
    username, password, prefix = get_credentials()
    d = get_rest(username=username, password=password,
                 prefix=prefix, test_mode=True)
    doi = d.draft_doi()
    datacite_prefix = doi.split('/')[0]
    assert datacite_prefix == prefix
    url = 'https://github.com/inveniosoftware/datacite'
    new_url = d.update_url(doi, url)
    assert new_url == url


@responses.activate
def test_rest_create_draft_mock():
    prefix = '10.1234'
    mock = 'https://github.com/inveniosoftware/datacite'
    data = {"data": {"id": prefix+"/1", "attributes": {"url": mock}}}
    responses.add(
        responses.POST,
        "{0}dois".format(RESTURL),
        json=data,
        status=201,
    )
    # test_mode=False because we already introduced a fake url
    # with RESTURL variable
    d = get_rest(username='mock', password='mock',
                 prefix=prefix)
    doi = d.draft_doi()
    datacite_prefix = doi.split('/')[0]
    assert datacite_prefix == prefix

    responses.add(
        responses.PUT,
        "{0}dois/10.1234/1".format(RESTURL),
        json=data,
        status=200,
    )
    new_url = d.update_url(doi, mock)
    assert new_url == mock


#
# Tests on example files
#
TEST_JSON_FILES = [
        'data/4.3/datacite-example-complicated-v4.json',
]


def load_json_path(path):
    """Helper method for loading a JSON example file from a path."""
    path_base = dirname(__file__)
    with io.open(join(path_base, path), encoding='utf-8') as file:
        content = file.read()
    return json.loads(content)


@pytest.mark.parametrize('example_json43', TEST_JSON_FILES)
@pytest.mark.pw
def test_rest_create_public(example_json43):
    """Test creating DOIs with all example metadata"""
    example_metadata = load_json_path(example_json43)
    # We cannot use the example DOIs
    example_metadata.pop('doi')
    url = 'https://github.com/inveniosoftware/datacite'
    username, password, prefix = get_credentials()
    d = get_rest(username=username, password=password,
                 prefix=prefix, test_mode=True)
    doi = d.public_doi(example_metadata, url)
    datacite_prefix = doi.split('/')[0]
    assert datacite_prefix == prefix


@responses.activate
def test_rest_get_200():
    """Test."""
    url = "http://example.org"
    data = {"data": {"id": "10.1234/1", "attributes": {"url": url}}}
    responses.add(
        responses.GET,
        "{0}dois/10.1234/1".format(RESTURL),
        json=data,
        status=200,
    )

    d = get_rest()
    assert url == d.doi_get("10.1234/1")


@responses.activate
def test_doi_get_204():
    """Test 204 error and test_mode setting."""
    responses.add(
        responses.GET,
        "https://api.test.datacite.org/dois/10.1234/1".format(RESTURL),
        body="No Content",
        status=204,
    )

    d = get_rest(test_mode=True)
    with pytest.raises(DataCiteNoContentError):
        d.doi_get("10.1234/1")


@responses.activate
def test_doi_get_401():
    """Test."""
    responses.add(
        responses.GET,
        "{0}dois/10.1234/1".format(RESTURL),
        body="Unauthorized",
        status=401,
    )

    d = get_rest()
    with pytest.raises(DataCiteUnauthorizedError):
        d.doi_get("10.1234/1")


@responses.activate
def test_doi_get_403():
    """Test."""
    responses.add(
        responses.GET,
        "{0}dois/10.1234/1".format(RESTURL),
        body="Forbidden",
        status=403,
    )

    d = get_rest()
    with pytest.raises(DataCiteForbiddenError):
        d.doi_get("10.1234/1")


@responses.activate
def test_doi_get_404():
    """Test."""
    responses.add(
        responses.GET,
        "{0}dois/10.1234/1".format(RESTURL),
        body="Not Found",
        status=404,
    )

    d = get_rest()
    with pytest.raises(DataCiteNotFoundError):
        d.doi_get("10.1234/1")


@responses.activate
def test_doi_get_410():
    """Test."""
    responses.add(
        responses.GET,
        "{0}dois/10.1234/1".format(RESTURL),
        body="Gone",
        status=410,
    )

    d = get_rest()
    with pytest.raises(DataCiteGoneError):
        d.doi_get("10.1234/1")


@responses.activate
def test_doi_get_500():
    """Test."""
    responses.add(
        responses.GET,
        "{0}dois/10.1234/1".format(RESTURL),
        body="Internal Server Error",
        status=500,
    )

    d = get_rest()
    with pytest.raises(DataCiteServerError):
        d.doi_get("10.1234/1")
