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
"""Tests to assure the Solr Services."""
from __future__ import annotations

from search_api.services.solr import SolrDoc

def create_solr_doc(identifier, name, state, legal_type, bn=None) -> SolrDoc:
    return SolrDoc({
        'identifier': identifier,
        'name': name,
        'status': state,
        'legaltype': legal_type,
        'bn': bn
    })

SOLR_TEST_DOCS = [
    create_solr_doc('CP1234567', 'test 1234', 'ACTIVE', 'CP', 'BN00012334'),
    create_solr_doc('CP0234567', 'tester 1111', 'HISTORICAL', 'CP', '09876K'),
    create_solr_doc('CP0034567', 'tests 2222', 'ACTIVE', 'CP'),
    create_solr_doc('BC0004567', 'test 3333', 'ACTIVE', 'BEN', '00987766800988'),
    create_solr_doc('BC0000567', '4444 test', 'HISTORICAL', 'BC', 'BN9000776557'),
    create_solr_doc('BC0000067', 'single', 'ACTIVE', 'BEN', '242217'),
    create_solr_doc('BC0000007', 'lots of words in here', 'ACTIVE', 'BEN', '124221'),
    create_solr_doc('BC0020047', 'NOt Case SENSitive', 'ACTIVE', 'BEN', '1255323221')
]
