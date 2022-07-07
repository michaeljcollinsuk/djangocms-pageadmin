from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language as force_language
from django.utils.translation import ugettext_lazy as _

from cms.toolbar.items import ButtonList
from cms.toolbar import utils
from cms.utils.urlutils import admin_reverse

from djangocms_version_locking.monkeypatch.cms_toolbars import (
    ButtonWithAttributes,
)
from djangocms_versioning.cms_toolbars import VersioningToolbar

from .conf import PAGEADMIN_LIVE_URL_QUERY_PARAM_NAME
from .helpers import _get_url


def new_view_published_button(func):
    """
    The cms core does not allow for custom attributes to be specified for toolbar buttons, therefore,
    monkeypatch the method which adds view published to use the ButtonWithAttributes item from djangocms-version-locking
    """
    def inner(self, **kwargs):
        """Helper method to add a publish button to the toolbar
        """
        # Check if object is registered with versioning otherwise don't add
        if not self._is_versioned():
            return

        # Add the View published button if in edit or preview mode
        published_version = self._get_published_page_version()
        if not published_version:
            return

        if self.toolbar.edit_mode_active or self.toolbar.preview_mode_active:
            item = ButtonList(side=self.toolbar.RIGHT)
            view_published_button = ButtonWithAttributes(
                _("View Published"),
                url=published_version.get_absolute_url(),
                disabled=False,
                extra_classes=['cms-btn', 'cms-btn-switch-save'],
                html_attributes={"target": "_blank"},
            )
            item.buttons.append(view_published_button)
            self.toolbar.add_item(item)
    return inner


VersioningToolbar._add_view_published_button = new_view_published_button(VersioningToolbar._add_view_published_button)


def new_get_object_preview_url(func):
    def inner(self, obj, language=None):

        content_type = ContentType.objects.get_for_model(obj)

        live_url = _get_url(obj)

        if not language:
            language = force_language()

        with force_language(language):
            url = admin_reverse('cms_placeholder_render_object_preview', args=[content_type.pk, obj.pk])
            return f"{url}?{PAGEADMIN_LIVE_URL_QUERY_PARAM_NAME}={live_url}"
    return inner


utils.get_object_preview_url = new_get_object_preview_url(utils.get_object_preview_url)


def new_get_object_edit_url(obj, language=None):
    content_type = ContentType.objects.get_for_model(obj)

    live_url = _get_url(obj)

    if not language:
        language = force_language()

    with force_language(language):
        url = admin_reverse('cms_placeholder_render_object_edit', args=[content_type.pk, obj.pk])
        return f"{url}?{PAGEADMIN_LIVE_URL_QUERY_PARAM_NAME}={live_url}"


utils.get_object_edit_url = new_get_object_edit_url
