import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'ClassDeck'
copyright = '2025, Paarth Siloiya'
author = 'Paarth Siloiya'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'shibuya'
html_static_path = ['_static']

todo_include_todos = True
