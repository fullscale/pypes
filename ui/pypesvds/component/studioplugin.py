from paste.script import templates

class StudioPlugin(templates.Template):

    egg_plugins = ['studio_plugin']
    summary = 'Project template for creating a studio plugin component'
    _template_dir = 'default_project'
    use_cheetah = False

