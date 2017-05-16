import radio_export.main as module


def test_chunks():
    input_list = [1, 2, 3]
    chunk_size = 2
    expected = [[1, 2], [3, ]]
    actual = module._chunks(input_list, chunk_size)

    assert list(actual) == expected
