# Bundler-minifier for Django framework

This module bundles and minifies static and template files for your Django project.

## How to
* copy dj-bundler into your root folder (that's the folder where your settings.py file is located)
* in Setting.json file indicate what folders do you what to works with by providing the paths for those folders, if they need to be bundles and/or minified.
<br> Folders currently supported:
<br> * static - forder which holds all your custom css/js files
<br> * assets - folder which holds all your external libraries (bootstrap and such)
<br> * templates - all your html files including layout.html or base.html
* in your setting.py development file include:
<br> * "import dj_bundler.main" on the top
<br>

