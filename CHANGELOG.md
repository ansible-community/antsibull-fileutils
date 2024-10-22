# antsibull\-fileutils Release Notes

**Topics**

- <a href="#v1-1-0">v1\.1\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v1-0-1">v1\.0\.1</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v1-0-0">v1\.0\.0</a>
    - <a href="#release-summary-2">Release Summary</a>

<a id="v1-1-0"></a>
## v1\.1\.0

<a id="release-summary"></a>
### Release Summary

Bugfix and feature release\.

<a id="minor-changes"></a>
### Minor Changes

* Declare support for Python 3\.13 \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/10](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/10)\)\.
* Rewrite <code>Copier</code> and <code>GitCopier</code> so that both symlinks outside the tree and symlinks inside the tree are handled more correctly\: symlinks inside the tree are kept\, while for symlinks outside the tree the content is copied\. Symlinks are normalized by default\, which makes this behavior similar to ansible\-core\'s behavior in <code>ansible\-galaxy collection build</code>\. Also copying now tries to preserve metadata \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/8](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/8)\)\.

<a id="bugfixes"></a>
### Bugfixes

* <code>CollectionCopier</code>\'s <code>source\_directory</code> argument now accepts <code>pathlib\.Path</code> objects in addition to <code>str</code> s \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/6](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/6)\)\.

<a id="v1-0-1"></a>
## v1\.0\.1

<a id="release-summary-1"></a>
### Release Summary

Bugfix release\.

<a id="bugfixes-1"></a>
### Bugfixes

* Remove accidentally left\-in <code>print\(\)</code> statement in <code>antsibull\_fileutils\.io\.write\_file\(\)</code> \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/5](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/5)\)\.

<a id="v1-0-0"></a>
## v1\.0\.0

<a id="release-summary-2"></a>
### Release Summary

Initial release\.
