# Contributing

## Code conventions

Please, use Black for Python files: https://github.com/ambv/black

## Git branch policy

* master: last stable version (no commit, no pull request on this branch)
* develop: current state of development

## Code organisation

* app: OneTjs app code
  * models: data models used by the various parts of the app
  * templates: templates used by the various parts of the app
  * tjs: part of the app in charge of the TJS interface
  * public_pages: part of the app in charge of producing the web pages describing the app, its services, frameworks, 
  datasets...
* data: sample datasets provided for demonstration purposes
* docs: the app documentation
* static: static assets (files served as they are, like the app favicon)
