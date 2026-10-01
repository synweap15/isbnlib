# Python 3.14 compatibility fork

Based on upstream isbnlib v3.10.14, commit
a629d91f59fcdc7d198137607faa7d51c83eae88. Original LGPL-3.0-or-later
license and attribution are retained.

This downstream revision replaces pkg_resources plugin discovery with
importlib.metadata.entry_points. It preserves ISBN parsing, checksums,
hyphenation, data, services, formatter registration and plugin error behavior.
The multiprocessing worker is module-scoped so the Python 3.14 default
forkserver start method can pickle it; task results and error handling are unchanged.
It requires Python 3.10 or later and is compatible with Setuptools 82+, which
removed pkg_resources. Package identifiers use standard dotted names and wheels
are marked Python 3 only. Consumers must pin an immutable commit.

The downstream version is 3.10.14.post1; it is not a PyPI upstream release.
No upstream issue or pull request has been submitted by this change.
