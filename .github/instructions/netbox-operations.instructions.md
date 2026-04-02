---
description: 'This file describes best practices for extending NetBox core views and adding additional tabs to the UI.'
applyTo: '**/*.py, **/*.html, **/*.toml'
---

Extending Core Views
Additional Tabs

Plugins can "attach" a custom view to a NetBox model by registering it with register_model_view(). To include a tab for this view within the NetBox UI, declare a TabView instance named tab, and add it to the template context dict:

from dcim.models import Site
from myplugin.models import Stuff
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

@register_model_view(Site, name='myview', path='some-other-stuff')
class MyView(generic.ObjectView):
    ...
    tab = ViewTab(
        label='Other Stuff',
        badge=lambda obj: Stuff.objects.filter(site=obj).count(),
        permission='myplugin.view_stuff'
    )

    def get(self, request, pk):
        ...
        return render(
            request,
            "myplugin/mytabview.html",
            context={
                "tab": self.tab,
            },
        )

ViewTab

ViewTabs are used for navigation among multiple object-specific views, such as the changelog or journal for a particular object.
render(instance)

Return the attributes needed to render a tab in HTML if the tab should be displayed. Otherwise, return None.

Parameters:
Name	Type	Description	Default
instance	Any	No description available	-
Extra Template Content

Plugins can inject custom content into certain areas of core NetBox views. This is accomplished by subclassing PluginTemplateExtension, optionally designating one or more particular NetBox models, and defining the desired method(s) to render custom content. Five methods are available:
Method	View	Description
head()	All	Custom HTML <head> block includes
navbar()	All	Inject content inside the top navigation bar
list_buttons()	List view	Add buttons to the top of the page
buttons()	Object view	Add buttons to the top of the page
alerts()	Object view	Inject content at the top of the page
left_page()	Object view	Inject content on the left side of the page
right_page()	Object view	Inject content on the right side of the page
full_width_page()	Object view	Inject content across the entire bottom of the page

Additionally, a render() method is available for convenience. This method accepts the name of a template to render, and any additional context data you want to pass. Its use is optional, however.

To control where the custom content is injected, plugin authors can specify an iterable of models by overriding the models attribute on the subclass. Extensions which do not specify a set of models will be invoked on every view, where supported.

When a PluginTemplateExtension is instantiated, context data is assigned to self.context. Available data includes:

    object - The object being viewed (object views only)
    model - The model of the list view (list views only)
    request - The current request
    settings - Global NetBox settings
    config - Plugin-specific configuration parameters

For example, accessing {\{ request.user \}} within a template will return the current user.

Declared subclasses should be gathered into a list or tuple for integration with NetBox. By default, NetBox looks for an iterable named template_extensions within a template_content.py file. (This can be overridden by setting template_extensions to a custom value on the plugin's PluginConfig.) An example is below.

from netbox.plugins import PluginTemplateExtension
from .models import Animal

class SiteAnimalCount(PluginTemplateExtension):
    models = ['dcim.site']

    def right_page(self):
        return self.render('netbox_animal_sounds/inc/animal_count.html', extra_context={
            'animal_count': Animal.objects.count(),
        })

template_extensions = [SiteAnimalCount]
