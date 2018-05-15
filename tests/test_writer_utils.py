from pathlib import Path
import pytest
import wrzoho.writer


def test_parsing_input_csv(tmpdir):
    incsv = tmpdir.join("create_contacts.csv")
    incsv.write("""last_name,first_name,campaign_source__id
Doe,Jane,42
Doe,John,999
Hoe,Mary,666""")
    parsed = list(wrzoho.writer.parse_input_csv(incsv.strpath))
    expected = [
        {"last_name":"Doe","first_name":"Jane","campaign_source":{"id":"42"}},
        {"last_name":"Doe","first_name":"John","campaign_source":{"id":"999"}},
        {"last_name":"Hoe","first_name":"Mary","campaign_source":{"id":"666"}}
    ]
    assert parsed == expected

def test_deciding_action_from_filename_invalid_action():
    path = Path('./cancel_Contact.csv')
    with pytest.raises(ValueError) as err:
        wrzoho.writer.decide_action_from_filename(path)
    assert err.match("Don't know what to do with")


def test_deciding_action_from_filename_invalid_module():
    path = Path('./create_invalidmodule.csv')
    with pytest.raises(ValueError) as err:
        wrzoho.writer.decide_action_from_filename(path)
    assert err.match("module name in the input csv must be one of")

def test_deciding_action_valid_actions():

    cases = [
        (Path("./create_contacts.csv"), ('create', 'contacts')),
        (Path("./update_contacts.csv"), ('update', 'contacts')),
        (Path("./delete_contacts.csv"), ('delete', 'contacts')),
        (Path("./create_leads.csv"), ('create', 'leads')),
        (Path("./update_leads.csv"), ('update', 'leads')),
        (Path("./delete_leads.csv"), ('delete', 'leads')),
    ]
    for path, expected in cases:
        action_module = wrzoho.writer.decide_action_from_filename(path)
        assert action_module == expected
