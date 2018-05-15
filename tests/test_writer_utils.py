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
