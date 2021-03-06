import pytest
import os
import sys

from tomlconf import File, get_app_dir

WIN = sys.platform.startswith('win')
MAC = sys.platform.startswith('darwin')


@pytest.fixture
def tmpfile(tmpdir):
    p = tmpdir.mkdir('testdir').join('testfile.txt')
    p.write('test data')
    return str(p)


def test_read_only(tmpfile):
    with File(tmpfile, 'r') as file:
        assert file.mode == 'r'
        assert file.text == 'test data'
        file.text = 'new data'
    with File(tmpfile, 'r') as file:
        assert file.text == 'test data'


def test_write_only(tmpfile):
    with File(tmpfile, 'w') as file:
        assert file.text == ''
        file.text = 'new data'
    with File(tmpfile, 'r') as file:
        assert file.text == 'new data'


def test_read_write(tmpfile):
    with File(tmpfile, 'r+') as file:
        assert file.text == 'test data'
        file.text = 'new data'
    with File(tmpfile, 'r') as file:
        assert file.text == 'new data'


def test_invalid_mode(tmpfile):
    with pytest.raises(ValueError):
        with File(tmpfile, 'w+'):
            pass


def test_encoding(tmpfile):
    with File(tmpfile, 'w', encoding='iso-8859-5') as file:
        file.text = 'test data: данные испытани'
    with pytest.raises(UnicodeDecodeError):
        with File(tmpfile, 'r') as file:
            pass
    with File(tmpfile, 'r', encoding='utf-8', errors='replace') as file:
        assert file.text == 'test data: ������ ��������'
    with File(tmpfile, 'r', encoding='iso-8859-5') as file:
        assert file.text == 'test data: данные испытани'


@pytest.mark.appdir
@pytest.mark.skipif(not WIN, reason='For Windows platforms only')
def test_get_win_app_dir():
    app_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    result = get_app_dir('Foo Bar', roaming=False)
    assert app_dir in result and 'Foo Bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(not WIN, reason='For Windows platforms only')
def test_get_win_app_dir_roaming():
    app_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
    result = get_app_dir('Foo Bar', roaming=True)
    assert app_dir in result and 'Foo Bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(not MAC, reason='For Mac platforms only')
def test_get_mac_app_dir():
    app_dir = os.path.join(
        os.path.expanduser('~'),
        '/Library/Application Support'
    )
    result = get_app_dir('Foo Bar')
    assert app_dir in result and 'Foo Bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(WIN, reason='Not needed for Windows platforms')
def test_get_posix_app_dir():
    app_dir = os.path.expanduser('~')
    result = get_app_dir('Foo Bar', force_posix=True)
    assert app_dir in result and '.foo-bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(WIN or MAC, reason='Not needed for Windows or Mac')
def test_get_nix_app_dir():
    app_dir = os.environ.get(
        'XDG_CONFIG_HOME',
        os.path.expanduser('~/.config')
    )
    result = get_app_dir('Foo Bar')
    assert app_dir in result and 'foo-bar' in result
