# Bundler-minifier for Django framework

This module bundles and minifies static and template files for your Django project.

## Current limitations
* current version works with only <u>one set</u> of template/static files. In case there are multiple apps that include their own template/static folders, dj_bundler folder will need to be copied to each app folder and import/run statements in your settings.py file will need to be created for each app.
* all links to static files in .html files have to be provided in <code> {% static 'foldername/filename.suffix' %} </code> manner. 
* dj-bundler puts a time-code to each static file each time it runs.

## How to use dj-bundler
* copy dj__bundler folder into your root folder (that's the folder where your settings.py file/s is located)
* in Setting.json file indicate what folders you what to works with by providing the paths for those folders, if they need to be bundles and/or minified.
<br> Folders currently supported:
<br> * static - forder which holds all your css/js files, images and such
<br> * templates - all your html files including layout, html or base.html

* in your setting.py development file include to the bottom:
<br> <code>from .dj_bundler import main    
    main.main(BASE_DIR)</code>

* run <code>$ py manage.py runserver</code> command. Production static files and templates will be created and updated each time the development server reloads.

# Important notes
* dj-bundler requires you to have separate development and production folders for templates and static files. Providing the same path for development and production will lead to development files to be lost.
* dj_bundler forlder may be placed in to a different forder rather than your project folder. this will require you to ament the import statement in your settings.py file accordings.

# todo
* add Settings.json input validation
* include comments in html and css
* allow for a few different apps (different static and template folders)
* catch errors
* provide logging of last run
* implement file stamp changing only for static files that have been changed

