# Copyright © 2022 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE_2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test suite to ensure that the Solr Service is working as expected for all queries."""
import time
from http import HTTPStatus

import pytest
from flask import Flask

from search_api.services import solr
from search_api.services.solr import Solr, SolrDoc, SolrField

from tests import integration_solr
from . import SOLR_TEST_DOCS


@integration_solr
@pytest.mark.parametrize('test_name,query,expected', [
    ('test_doesnt_match_identifier', 'CP00', []),
    ('test_doesnt_match_bn', 'BN00012334', []),
    ('test_name_exact', 'tests 2222', ['tests 2222']),
    ('test_case', 'not case sensitive', ['NOt Case SENSitive']),
    ('test_partial_1', 'tester', ['tester 1111']),
    ('test_partial_2', 'tester 11', ['tester 1111']),
    ('test_partial_3', 'lots of wor', ['lots of words in here']),
    ('test_all_words_match', 'tests oops 2222', []),
    ('test_stem_matches', 'test 2222', ['tests 2222']),
    ('test_multiple_matches', 'test', ['test 1234', 'tester 1111', 'tests 2222', 'test 3333', '4444 test']),
])
def test_solr_suggest_name(app, test_name, query, expected):
    """Assert that solr suggest call works as expected."""
    # setup
    solr.init_app(app)
    solr.delete_all_docs()
    solr.create_or_replace_docs(SOLR_TEST_DOCS)
    time.sleep(1)  # wait for solr to register update
    # call suggester
    suggestions = solr.suggest(query, 10, True)
    assert len(suggestions) == len(expected)
    for name in expected:
        assert name.upper() in suggestions


@integration_solr
@pytest.mark.parametrize('test_name,query,query_field,base_fields,expected_field,expected', [
    ('test_identifier_1', 'CP00', SolrField.IDENTIFIER_Q, True, SolrField.IDENTIFIER, ['CP0034567']),
    ('test_identifier_2', 'CP567', SolrField.IDENTIFIER_Q, True, SolrField.IDENTIFIER, ['CP0034567', 'CP1234567', 'CP0234567']),
    ('test_bn', '0012334', SolrField.BN_Q, True, SolrField.BN, ['BN00012334']),
    ('test_name_exact', 'tests 2222', SolrField.NAME_Q, True, SolrField.NAME, ['tests 2222']),
    ('test_case', 'not case sensitive', SolrField.NAME_Q, True, SolrField.NAME, ['NOt Case SENSitive']),
    ('test_partial_1', 'tester', SolrField.NAME_Q, True, SolrField.NAME, ['tester 1111']),
    ('test_partial_2', 'tester 11', SolrField.NAME_Q, True, SolrField.NAME, ['tester 1111']),
    ('test_partial_3', 'lots of wor', SolrField.NAME_Q, True, SolrField.NAME, ['lots of words in here']),
    ('test_partial_4', 'ots of ords', SolrField.NAME_SINGLE, True, SolrField.NAME, ['lots of words in here']),
    ('test_all_words_match', 'tests oops 2222', SolrField.NAME_Q, True, SolrField.NAME, []),
    ('test_multiple_matches', 'test 1', SolrField.NAME_Q, True, SolrField.NAME, ['test 1234', 'tester 1111']),
    ('test_parties_1', 'org', SolrField.PARTY_NAME_Q, False, SolrField.PARTY_NAME, ['org 1', 'test org partner']),
    ('test_parties_2', 'person', SolrField.PARTY_NAME_Q, False, SolrField.PARTY_NAME, ['person 1', 'test person partner']),
    ('test_parties_3', 'test Person', SolrField.PARTY_NAME_Q, False, SolrField.PARTY_NAME, ['test person partner']),
    ('test_parties_4', 'test partner', SolrField.PARTY_NAME_Q, False, SolrField.PARTY_NAME, ['test org partner', 'test person partner']),
    ('test_special_chars_name_&&', '01 special && char', SolrField.NAME_Q, True, SolrField.NAME, ['01 solr special && char']),
    ('test_special_chars_name_||', '02 special || char', SolrField.NAME_Q, True, SolrField.NAME, ['02 solr special || char']),
    ('test_special_chars_name_:', '03 special: char', SolrField.NAME_Q, True, SolrField.NAME, ['03 solr special: char']),
    ('test_special_chars_name_+', '04 special + char', SolrField.NAME_Q, True, SolrField.NAME, ['04 solr special + char']),
    ('test_special_chars_name_-', '05 special - char', SolrField.NAME_Q, True, SolrField.NAME, ['05 solr special - char']),
    ('test_special_chars_name_!', '06 special ! char', SolrField.NAME_Q, True, SolrField.NAME, ['06 solr special ! char']),
    ('test_special_chars_name_\\', '07 special \ char', SolrField.NAME_Q, True, SolrField.NAME, ['07 solr special \ char']),
    ('test_special_chars_name_()', '08 special (char)', SolrField.NAME_Q, True, SolrField.NAME, ['08 solr special (char)']),
    ('test_special_chars_name_"', '09 special " char"', SolrField.NAME_Q, True, SolrField.NAME, ['09 solr special " char"']),
    ('test_special_chars_name_~', '10 special ~ char', SolrField.NAME_Q, True, SolrField.NAME, ['10 solr special ~ char']),
    ('test_special_chars_name_*', '11 special* char', SolrField.NAME_Q, True, SolrField.NAME, ['11 solr special* char']),
    ('test_special_chars_name_?', '12 special? char', SolrField.NAME_Q, True, SolrField.NAME, ['12 solr special? char']),
    ('test_special_chars_name_/', '13 special / char', SolrField.NAME_Q, True, SolrField.NAME, ['13 solr special / char']),
    ('test_special_chars_name_X', 'many special =&{}^%`#|<>,.@$;_chars', SolrField.NAME_Q, True, SolrField.NAME, ['many special =&{}^%`#|<>,.@$;_chars']),
    ('test_special_operators_OR', 'special OR operator', SolrField.NAME_Q, True, SolrField.NAME, ['special OR AND NOT operators']),
    ('test_special_operators_AND', 'special AND operator', SolrField.NAME_Q, True, SolrField.NAME, ['special OR AND NOT operators']),
    ('test_special_operators_NOT', 'special NOT operator', SolrField.NAME_Q, True, SolrField.NAME, ['special OR AND NOT operators']),
    ('test_accented_character_1', 'EBENISTERIE', SolrField.NAME_SINGLE, True, SolrField.NAME, ['DIVINE ÉBÉNISTERIE INC.']),
    ('test_accented_character_2', 'EBENISTERIE', SolrField.NAME_Q, True, SolrField.NAME, ['DIVINE ÉBÉNISTERIE INC.']),
    ('test_accented_character_4', 'EBENISTERIE', SolrField.NAME_STEM_AGRO, True, SolrField.NAME, ['DIVINE ÉBÉNISTERIE INC.']),
    ('test_+&and_+_1', 'special + match', SolrField.NAME_Q, True, SolrField.NAME, ['special and match 1', 'special + match 2', 'special+match 3', 'special & match 4', 'special&match 5']),
    ('test_+&and_+_2', 'special+match', SolrField.NAME_Q, True, SolrField.NAME, ['special and match 1', 'special + match 2', 'special+match 3', 'special & match 4', 'special&match 5']),
    ('test_+&and_&_1', 'special & match', SolrField.NAME_Q, True, SolrField.NAME, ['special and match 1', 'special + match 2', 'special+match 3', 'special & match 4', 'special&match 5']),
    ('test_+&and_&_2', 'special&match', SolrField.NAME_Q, True, SolrField.NAME, ['special and match 1', 'special + match 2', 'special+match 3', 'special & match 4', 'special&match 5']),
    ('test_+&and_and', 'special and match', SolrField.NAME_Q, True, SolrField.NAME, ['special and match 1', 'special + match 2', 'special+match 3', 'special & match 4', 'special&match 5']),
    ('test_dash_1', 'special-dash match', SolrField.NAME_Q, True, SolrField.NAME, ['special-dash match 1', 'special - dash match 2', 'special dash match 3']),
    ('test_dash_2', 'special - dash match', SolrField.NAME_Q, True, SolrField.NAME, ['special-dash match 1', 'special - dash match 2', 'special dash match 3']),
    ('test_dash_3', 'special dash match', SolrField.NAME_Q, True, SolrField.NAME, ['special-dash match 1', 'special - dash match 2', 'special dash match 3']),
])
def test_solr_query(app, test_name, query, query_field, base_fields, expected_field, expected):
    """Assert that solr query call works as expected."""
    # setup
    solr.init_app(app)
    solr.delete_all_docs()
    solr.create_or_replace_docs(SOLR_TEST_DOCS)
    time.sleep(1)  # wait for solr to register update
    query = {'value': Solr.prep_query_str(query)}
    search_params = Solr.build_split_query(query, [query_field, SolrField.NAME_STEM_AGRO], [SolrField.NAME_Q])
    search_params['fl'] = solr.base_fields if base_fields else solr.party_fields
    # call select
    resp = solr.query(search_params, 0, 10)
    docs = resp['response']['docs']
    # test
    assert len(docs) == len(expected)
    for doc in docs:
        assert doc[expected_field] in expected
