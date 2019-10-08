import decimal

from djsettings import DjSettingsGroup, register, values


@register()
class TestStringSettings(DjSettingsGroup):
    test_string = values.StringValue(default='test string setting')

    class Meta:
        verbose_name = 'Test string setting'


@register()
class TestBooleanSettings(DjSettingsGroup):
    test_boolean = values.StringValue(default='test boolean setting')

    class Meta:
        verbose_name = 'Test boolean setting'



# @register()
# class ErrorDefaultSettings(DjSettingsGroup):
#     test_text_value_error = values.StringValue(default=False)
#     test_boolean_value_error = values.BooleanValue(default='faaalse')
#     test_integer_value_error = values.IntegerValue(default='text')
#     test_decimal_value_error = values.DecimalValue(default='decimal.Decimal(0.99)')
#     test_float_value_error = values.DecimalValue(default='0.99ddd')
#
#     class Meta:
#         verbose_name = 'Error default settings'


# from djsettings import djsetting
# from djsettings.models import DjSetting
#
# # print("from class", CheckSettings.test_text_value)
# print("from registry", djsetting.test_text_value)
# print('====')
#
# print("update to 'sdsdfsd'")
# c_s = CheckSettings()
# print(c_s.test_text_value)
# c_s.test_text_value = 'sdsdfsd'
# print(c_s.test_text_value)
# print('from db after update', DjSetting.objects.filter(name='test_text_value').first().raw_value)
# print("from registry after from initialized class updated", djsetting.test_text_value)
# print('====')
#
# print("update to 'test updated'")
# djsetting.test_text_value = 'test updated'
# print('from db after update', DjSetting.objects.filter(name='test_text_value').first().raw_value)
# print("from registry after from registry updated", djsetting.test_text_value)
# print('-----------------------')
# print('====')
#
# print(djsetting.test_boolean_value)
# djsetting.test_boolean_value = False
# print(djsetting.test_boolean_value)
# print('-----------------------')
#
# print(djsetting.test_integer_value)
# djsetting.test_integer_value = 99
# print(djsetting.test_integer_value)
# print('-----------------------')
#
# print(djsetting.test_decimal_value)
# djsetting.test_decimal_value = decimal.Decimal(9.99)
# print(djsetting.test_decimal_value)
# print('-----------------------')
#
# print(djsetting.test_float_value)
# djsetting.test_float_value = 9.99
# print(djsetting.test_float_value)
# print('-----------------------')
#
# djsetting.test_float_value2 = 'ssss'
# djsetting.test_float_value = 'ssss'

# for setting_name in dir(djsetting):
# from .models import DjSetting
# print("update to 'test updated'")
# print(getattr(djsetting, setting_name))
# setattr(djsetting, setting_name, 'test updated from form')
# print(getattr(djsetting, setting_name))
# print('from db after update', DjSetting.objects.filter(name=setting_name).first().raw_value)
# print("from registry after from registry updated", setting_name)
# print('====')
