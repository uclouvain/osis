"""
Django Unused Templates
by Alexander Meng

Generates a list of unused templates in your current directory and subdirectories
by searching all .html and .py files for the names of your templates.

IF YOU OVERRIDE DJANGO TEMPLATES, THEY MAY APPEAR IN THE LIST AS UNUSED.

"""

import os
import sys

MODULES = ['osis', 'internship', 'continuing_education', 'osis_common', 'partnership', 'dissertation', 'assistant']
OSIS_MODULES = ['assessments', 'attribution', 'backoffice', 'base', 'cms', 'education_group', 'learning_unit',
                'program_management', 'reference', 'rules_management', 'osis\\templates', 'webservices']


def _should_analyze_file(f, submodules, features=False):
    if __is_unconcerned_file(f, features):
        return False
    for folder in submodules:
        if '\\' + folder + '\\' in f:
            return True
    return False


def __is_unconcerned_file(f, features=False):
    if '\\venv' in f or '\\tests' in f or '\\Lib' in f:
        return True
    if not features and '\\features' in f:
        return False


def _get_files_of_extension(file_extension, filter):
    return [
        f[2:-1]
        for f in os.popen('dir /b /s "*.' + file_extension + '" | sort').readlines()
        if filter[0](f, **filter[1])
    ]


def _get_templates(html_files):
    # Templates will only be returned if they are located in a
    # /templates/ directory
    template_list = []
    for html_file in html_files:
        if html_file.find("/templates") != 0:
            try:
                template_list.append(html_file.rsplit("templates\\")[1])
            except IndexError:
                # The html file is not in a template directory...
                # don't count it as a template
                template_list.append("html")

    return template_list


def get_unused_templates(module=None):
    print("Start searching unused templates in module %s" % (module if module else 'osis'))
    modules_to_keep = {
        module: (_should_analyze_file, {'submodules': OSIS_MODULES if module == 'osis' or None else [module]})
        for module in MODULES
    }[module if module else 'osis']
    html_files = _get_files_of_extension('html', modules_to_keep)
    templates = _get_templates(html_files)
    py_files = _get_files_of_extension('py', modules_to_keep)
    files = py_files + html_files  # List of all files
    tl_count = [0 for _ in templates]

    unused_templates = 0
    for file in files:
        f = open(file)
        text = f.read()
        for count, template in enumerate(templates):
            if template.replace('\\', '/') in text:
                tl_count[count] = 1
        f.close()

    for count, template in enumerate(templates):
        if tl_count[count] == 0:
            print("Unused template : ", html_files[count])
            unused_templates += 1
    print("\n# Unused templates : ", unused_templates)


def main(argv):
    module = argv[0] if argv else None
    if module and module not in MODULES:
        print("First argument should be a valid module")
        sys.exit()
    get_unused_templates(module)


if __name__ == "__main__":
    main(sys.argv[1:])
