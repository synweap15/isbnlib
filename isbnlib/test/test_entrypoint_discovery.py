"""Regression coverage for standard-library plugin discovery."""

import importlib
import importlib.util
import sys
from types import SimpleNamespace

import pytest

from .. import config, registry


@pytest.fixture(autouse=True)
def restore_registry():
    options = dict(config.options)
    yield
    config.options.clear()
    config.options.update(options)
    importlib.reload(registry)


def test_real_installed_metadata_plugin_is_discovered(tmp_path, monkeypatch):
    metadata = tmp_path / "isbn_fixture-1.0.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text("Metadata-Version: 2.1\nName: isbn-fixture\nVersion: 1.0\n")
    (metadata / "entry_points.txt").write_text(
        "[isbnlib.metadata]\nfixture = isbn_fixture_plugin:query\n"
    )
    (tmp_path / "isbn_fixture_plugin.py").write_text(
        "def query(isbn): return {'ISBN-13': isbn, 'Title': 'Fixture'}\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    config.options['LOAD_METADATA_PLUGINS'] = True
    importlib.invalidate_caches()
    importlib.reload(registry)
    assert 'fixture' in registry.PROVIDERS
    assert registry.services['fixture']('9780140328721')['Title'] == 'Fixture'
    assert importlib.util.find_spec('pkg_resources') is None
    sys.modules.pop('isbn_fixture_plugin', None)


def test_disabled_plugin_groups_are_not_loaded(monkeypatch):
    def unexpected(**kwargs):
        raise AssertionError('Disabled discovery was called')
    monkeypatch.setattr(importlib.metadata, 'entry_points', unexpected)
    config.options['LOAD_METADATA_PLUGINS'] = False
    config.options['LOAD_FORMATTER_PLUGINS'] = False
    importlib.reload(registry)
    assert set(registry.PROVIDERS) == {'goob', 'openl', 'wiki'}


def test_broken_plugin_preserves_builtin_services(monkeypatch, caplog):
    def fail():
        raise ImportError('Fixture plugin is unavailable')
    def discover(**kwargs):
        return [SimpleNamespace(name='broken', load=fail)]
    monkeypatch.setattr(importlib.metadata, 'entry_points', discover)
    config.options['LOAD_METADATA_PLUGINS'] = True
    importlib.reload(registry)
    assert 'broken' not in registry.PROVIDERS
    assert set(registry.PROVIDERS) == {'goob', 'openl', 'wiki'}
    assert 'Some metadata plugins were not loaded!' in caplog.text


def test_formatter_group_preserves_registration_contract(monkeypatch):
    groups = []
    def discover(**kwargs):
        groups.append(kwargs['group'])
        if kwargs['group'] == 'isbnlib.formatters':
            return [SimpleNamespace(name='fixture', load=lambda: 'CUSTOM')]
        return []
    monkeypatch.setattr(importlib.metadata, 'entry_points', discover)
    config.options['LOAD_METADATA_PLUGINS'] = True
    config.options['LOAD_FORMATTER_PLUGINS'] = True
    importlib.reload(registry)
    assert groups == ['isbnlib.metadata', 'isbnlib.formatters']
    assert registry.bibformatters['fixture'] == 'custom'
    assert 'fixture' in registry.BIBFORMATS
