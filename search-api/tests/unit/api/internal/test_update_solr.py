# Copyright © 2022 Province of British Columbia
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
"""Test-Suite to ensure that the solr business update endpoints/functions work as expected."""
import json
import copy
import time
from datetime import datetime
from http import HTTPStatus

import pytest
from dateutil.relativedelta import relativedelta

from search_api.enums import DocumentType
from search_api.models import Document, DocumentAccessRequest, User
from search_api.services.authz import STAFF_ROLE
from search_api.services.validator import RequestValidator

from tests.unit import MockResponse
from tests.unit.utils import SOLR_UPDATE_REQUEST_TEMPLATE as REQUEST_TEMPLATE
from tests.unit.services.utils import create_header
from tests import integration_solr


@integration_solr
def test_update_business_in_solr(session, client, jwt, mocker):
    """Assert that update operation is successful."""
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(REQUEST_TEMPLATE),
                              headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                          'content-type': 'application/json'})
                              )
    # check
    assert api_response.status_code == HTTPStatus.OK
    time.sleep(2)  # wait for solr to register update
    identifier = REQUEST_TEMPLATE['business']['identifier']
    search_response = client.get(f'/api/v1/businesses/search/facets?query=value:{identifier}',
                                 headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                             'content-type': 'application/json'})
                                 )
    assert search_response.status_code == HTTPStatus.OK
    assert len(search_response.json['searchResults']['results']) == 1


@integration_solr
def test_update_business_no_tax_id(session, client, jwt, mocker):
    """Assert that update operation is successful."""
    no_tax_id = copy.deepcopy(REQUEST_TEMPLATE)
    del no_tax_id['business']['taxId']
    no_tax_id['business']['identifier'] = 'FM1111111'
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(no_tax_id),
                              headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                          'content-type': 'application/json'})
                              )
    # check
    assert api_response.status_code == HTTPStatus.OK
    time.sleep(2)  # wait for solr to register update
    identifier = no_tax_id['business']['identifier']
    search_response = client.get(f'/api/v1/businesses/search/facets?query=value:{identifier}',
                                 headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                             'content-type': 'application/json'})
                                 )
    assert search_response.status_code == HTTPStatus.OK
    assert len(search_response.json['searchResults']['results']) == 1


@integration_solr
@pytest.mark.parametrize('test_name,legal_type,identifier,expected', [
    ('test_bc_add_prfx', 'BC', '0123456', 'BC0123456'),
    ('test_cc_add_prfx', 'CC', '1234567', 'BC1234567'),
    ('test_ulc_add_prfx', 'ULC', '2345678', 'BC2345678'),
    ('test_ben_add_prfx', 'BEN', '0000001', 'BC0000001'),
    ('test_bc_prfx_given', 'BC', 'BC0123466', 'BC0123466'),
    ('test_cc_prfx_given', 'CC', 'BC1234577', 'BC1234577'),
    ('test_ulc_prfx_given', 'ULC', 'BC234588', 'BC234588'),
    ('test_ben_add_prfx', 'BEN', 'BC0000002', 'BC0000002'),
    ('test_wrong_type_no_prfx', 'S', '0000003', '0000003'),
    ('test_wrong_type_prfx_given', 'S', 'S3456790', 'S3456790')
])
def test_update_bc_class_adds_prefix(session, client, jwt, test_name, legal_type, identifier, expected):
    """Assert prefixes are added to BC, ULC and CC identifiers and only when no prefix is given."""
    request_json = copy.deepcopy(REQUEST_TEMPLATE)
    del request_json['parties']
    request_json['business']['legalType'] = legal_type
    request_json['business']['identifier'] = identifier

    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                          'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.OK
    time.sleep(2)  # wait for solr to register update
    search_response = client.get(f'/api/v1/businesses/search/facets?query=value:{expected}::identifier:{expected}',
                                 headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                             'content-type': 'application/json'}))

    assert search_response.status_code == HTTPStatus.OK
    assert len(search_response.json['searchResults']['results']) == 1
    assert search_response.json['searchResults']['results'][0]['identifier'] == expected


@integration_solr
def test_update_business_in_solr_missing_data(session, client, jwt, mocker):
    """Assert that error is returned."""
    request_json = copy.deepcopy(REQUEST_TEMPLATE)
    del request_json['business']['identifier']
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                          'content-type': 'application/json'})
                              )
    # check
    assert api_response.status_code == HTTPStatus.BAD_REQUEST


@integration_solr
def test_update_business_in_solr_invalid_data(session, client, jwt, mocker):
    """Assert that error is returned."""
    request_json = copy.deepcopy(REQUEST_TEMPLATE)
    request_json['parties'][0]['officer']['partyType'] = 'test'
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                          'content-type': 'application/json'})
                              )
    # check
    assert api_response.status_code == HTTPStatus.BAD_REQUEST
