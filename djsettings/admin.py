from functools import update_wrapper

from django.contrib import admin, messages
from django.db import router, transaction
from django.contrib.admin.options import csrf_protect_m
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.helpers import Fieldset

from .models import DjSetting
from .forms import DjSettingsForm
from .registries import djsetting


@admin.register(DjSetting)
class DjSettingAdmin(admin.ModelAdmin):
    change_list_template = 'admin/djsettings/change_list.html'
    change_list_form = DjSettingsForm

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            path('', wrap(self.change_list_view), name='%s_%s_changelist' % info),
        ]
        return urlpatterns

    @csrf_protect_m
    def change_list_view(self, request, extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._changeform_view(request, extra_context)

    def _changeform_view(self, request, extra_context):
        opts = self.model._meta
        app_label = opts.app_label
        form = self.change_list_form()

        if request.method == 'POST':
            form = self.change_list_form(request.POST, request.FILES)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, _('DjSettings updated successfully.'))

        fieldsets = (Fieldset(form,
                              name=group._meta.verbose_name,
                              fields=[setting.name for setting in group._meta.settings])
                     for group in djsetting.get_all_setting_groups())

        context = dict(
            self.admin_site.each_context(request),
            title=str(opts.verbose_name_plural),
            app_label=app_label,
            opts=opts,
            form=form,
            fieldsets=fieldsets,
            media=self.media + form.media,
            module_name=str(opts.verbose_name_plural),
        )
        context.update(extra_context or {})
        return TemplateResponse(request, self.change_list_template, context)
