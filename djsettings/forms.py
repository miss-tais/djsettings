from django import forms

from .registries import djsetting


class DjSettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for group in djsetting.get_all_setting_groups():
            for setting in group._meta.settings:
                if setting.form_field:
                    self.fields[setting.name] = setting.form_field
                    self.fields[setting.name].initial = getattr(djsetting, setting.name)
                    self.fields[setting.name].default = setting.default

    def save(self):
        for group in djsetting.get_all_setting_groups():
            for setting in group._meta.settings:
                setattr(djsetting, setting.name, self.cleaned_data[setting.name])
