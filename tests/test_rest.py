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

import pytest
import responses
from helpers import RESTURL, get_credentials, get_rest

from datacite.errors import DataCiteForbiddenError, DataCiteGoneError, \
    DataCiteNoContentError, DataCiteNotFoundError, DataCiteServerError, \
    DataCiteUnauthorizedError


@pytest.mark.pw
def test_rest_create_get():
    username, password, prefix = get_credentials()
    d = get_rest(username=username, password=password,
                 prefix=prefix, test_mode=True)
    d.draft_doi()


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
