"""Evidence rendering in the approved role-brief PDF.

Proves the approved brief includes a finding's reviewer note and supporting
source quotations (with source title + locator) and excludes unapproved
findings that share the queried role. Uses an isolated temp database.

PDF test cases:
- test_approved_brief_includes_note_quotations_and_excludes_unapproved:
  an approved finding's reviewer note, supporting quotations (with source
  title and page/section locator) appear in the approved-only PDF, while
  unapproved findings sharing the Nurse role are excluded.
- test_draft_brief_includes_unapproved_findings: the draft export (approved_only
  off) is marked DRAFT and includes the unapproved Nurse-role finding excluded
  above, confirming the filter is approval-based rather than role-based.
- test_no_reviewer_note_label_when_note_not_supplied: approving a finding with
  no review note still renders its quotations, but the "Reviewer note:" label is
  absent from the PDF.
"""
import io
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from backend.app import app
from backend import store


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('GOLIVE_DB', str(tmp_path / 'brief.sqlite3'))
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    with TestClient(app) as c:
        yield c


def _analyze(client):
    r = client.post('/api/analyze', json={'use_llm': False})
    assert r.status_code == 200
    return r.json()


def _brief_text(client, role='Nurse', approved_only=True):
    params = {'role': role}
    if not approved_only:
        params['approved_only'] = 'false'
    pdf = client.get('/api/exports/brief.pdf', params=params)
    assert pdf.status_code == 200
    raw = ' '.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf.content)).pages)
    return ' '.join(raw.split())  # collapse wrapping/newlines for stable substring checks


def _flat(s):
    return ' '.join((s or '').split())


def test_approved_brief_includes_note_quotations_and_excludes_unapproved(client):
    _analyze(client)
    note = 'Checked against the fictional pilot plan.'
    r = client.patch('/api/impacts/duplicate_entry',
                     json={'status': 'approved', 'owner': 'Nursing education lead', 'review_note': note})
    assert r.status_code == 200

    flat = _brief_text(client, role='Nurse', approved_only=True)

    # The approved finding is included.
    assert 'Duplicate entry' in flat
    # The reviewer note is included when supplied.
    assert _flat(note) in flat

    # The approved finding's supporting source quotations are included.
    finding = next(i for i in store.get_impacts() if i['id'] == 'duplicate_entry')
    assert finding['status'] == 'approved'
    assert finding['citations'], 'expected citations on the approved finding'
    any_quote_in_pdf = False
    for c in finding['citations']:
        q = _flat(c.get('quote') or '')
        if q and q in flat:
            any_quote_in_pdf = True
        # Each quotation's source title and page/section locator appear.
        assert _flat(c.get('title') or '') in flat
        assert _flat(c.get('locator') or '') in flat
    assert any_quote_in_pdf, 'no supporting source quotation appeared in the PDF'

    # An unapproved finding that shares the Nurse role is excluded, proving the
    # filter is approval-based, not merely role-based.
    assert 'No path for an unavailable assessment' not in flat
    assert 'Notification review owner is unassigned' not in flat


def test_draft_brief_includes_unapproved_findings(client):
    _analyze(client)
    # Nothing is approved.
    flat = _brief_text(client, role='Nurse', approved_only=False)
    assert 'DRAFT' in flat
    # The unapproved Nurse-role finding excluded above now appears in a draft.
    assert 'No path for an unavailable assessment' in flat


def test_no_reviewer_note_label_when_note_not_supplied(client):
    _analyze(client)
    # Approve without a review note.
    r = client.patch('/api/impacts/duplicate_entry', json={'status': 'approved', 'owner': 'Rollout lead'})
    assert r.status_code == 200
    flat = _brief_text(client, role='Nurse', approved_only=True)
    # The finding and its quotation still appear.
    assert 'Duplicate entry' in flat
    finding = next(i for i in store.get_impacts() if i['id'] == 'duplicate_entry')
    assert any(_flat((c.get('quote') or '')) in flat for c in finding['citations'])
    # No reviewer note is rendered because none was supplied.
    assert 'Reviewer note:' not in flat
