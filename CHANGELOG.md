# antsibull\-fileutils Release Notes

**Topics**

- <a href="#v1-5-1">v1\.5\.1</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
- <a href="#v1-5-0">v1\.5\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
- <a href="#v1-4-0">v1\.4\.0</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
- <a href="#v1-3-0">v1\.3\.0</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v1-2-0">v1\.2\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
- <a href="#v1-1-0">v1\.1\.0</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v1-0-1">v1\.0\.1</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v1-0-0">v1\.0\.0</a>
    - <a href="#release-summary-7">Release Summary</a>

<a id="v1-5-1"></a>
## v1\.5\.1

<a id="release-summary"></a>
### Release Summary

Maintenance release\.

<a id="minor-changes"></a>
### Minor Changes

* Declare support for Python 3\.14 \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/21](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/21)\)\.

<a id="v1-5-0"></a>
## v1\.5\.0

<a id="release-summary-1"></a>
### Release Summary

Feature release\.

<a id="minor-changes-1"></a>
### Minor Changes

* Allow <code>GitCopier</code> to copy the repository structure as well\, if it is part of the directory that is being copied \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/20](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/20)\)\.

<a id="v1-4-0"></a>
## v1\.4\.0

<a id="release-summary-2"></a>
### Release Summary

Feature release\.

<a id="minor-changes-2"></a>
### Minor Changes

* Extend <code>tempfile</code> module to make it easier to find customized temporary directories \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/18](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/18)\)\.

<a id="v1-3-0"></a>
## v1\.3\.0

<a id="release-summary-3"></a>
### Release Summary

Bugfix and feature release\.

<a id="minor-changes-3"></a>
### Minor Changes

* Provide utilities <code>antsibull\_fileutils\.tempfile\.ansible\_mkdtemp\(\)</code> and <code>antsibull\_fileutils\.tempfile\.AnsibleTemporaryDirectory</code> to create temporary directories that are not part of an <code>ansible\_collections</code> tree \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/17](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/17)\)\.

<a id="bugfixes"></a>
### Bugfixes

* Avoid copying collections into temporary directories that are part of an <code>ansible\_collections</code> tree \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/17](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/17)\)\.

<a id="v1-2-0"></a>
## v1\.2\.0

<a id="release-summary-4"></a>
### Release Summary

Feature release\.

<a id="minor-changes-4"></a>
### Minor Changes

* Allow to exclude top\-level files and directories when copying trees \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/14](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/14)\)\.

<a id="v1-1-0"></a>
## v1\.1\.0

<a id="release-summary-5"></a>
### Release Summary

Bugfix and feature release\.

<a id="minor-changes-5"></a>
### Minor Changes

* Declare support for Python 3\.13 \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/10](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/10)\)\.
* Rewrite <code>Copier</code> and <code>GitCopier</code> so that both symlinks outside the tree and symlinks inside the tree are handled more correctly\: symlinks inside the tree are kept\, while for symlinks outside the tree the content is copied\. Symlinks are normalized by default\, which makes this behavior similar to ansible\-core\'s behavior in <code>ansible\-galaxy collection build</code>\. Also copying now tries to preserve metadata \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/8](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/8)\)\.

<a id="bugfixes-1"></a>
### Bugfixes

* <code>CollectionCopier</code>\'s <code>source\_directory</code> argument now accepts <code>pathlib\.Path</code> objects in addition to <code>str</code> s \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/6](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/6)\)\.

<a id="v1-0-1"></a>
## v1\.0\.1

<a id="release-summary-6"></a>
### Release Summary

Bugfix release\.

<a id="bugfixes-2"></a>
### Bugfixes

* Remove accidentally left\-in <code>print\(\)</code> statement in <code>antsibull\_fileutils\.io\.write\_file\(\)</code> \([https\://github\.com/ansible\-community/antsibull\-fileutils/pull/5](https\://github\.com/ansible\-community/antsibull\-fileutils/pull/5)\)\.

<a id="v1-0-0"></a>
## v1\.0\.0

<a id="release-summary-7"></a>
### Release Summary

Initial release\.
