# djsettings

DjSettings is a Django app for changing settings in Admin panel. 
Django's built-in cache framework is used.

Quick start
===========
1. Add ``djsettings`` to your INSTALLED_APPS setting like this:


        INSTALLED_APPS = [
            ...
            'djsettings',
        ]
    
2. Run `python manage.py migrate` to create the djsettings models.

3. Create `djsettings.py` file within one of your apps. The app must be installed.


        from djsettings import djsettings, DjSettingsGroup, values
            
        @djsetting.register
        class AmazonSettings(DjSettingsGroup):
            aws_secret_key = values.StringValue(default='default')
            
            class Meta:
                verbose_name = 'AWS settings'
            
        
Accessing settings
==================
Settings values can be accessed in Python

    from djsettings import djsettings
    
    print(djsetting.aws_secret_key)
 
Editing settings
================
DjSettings integrates with ``django.contrib.admin``. 
Admin interface can be used to edit settings values.

Settings values can be assigned in Python

    from djsettings import djsettings
    
    djsetting.aws_secret_key = 'new key'

        
Value types
===========

Each value type accepts the following parameters:
- ``default`` - default value (required)
- ``required`` - value is required or not (optional)
- ``widget`` - form field widget (optional)
- ``verbose_name`` - form field label (optional)
- ``help_text`` - form field help text (optional)

StringValue
-----------
Value stores ``str`` type

Additional parameters:
- ``max_length`` - maximum length (optional)
- ``min_length`` - maximum length (optional)

BooleanValue
------------
Value stores ``bool`` type

IntegerValue
------------
Value stores ``int`` type

Additional parameters:
- ``max_value`` - maximum value (optional)
- ``min_value`` - minimum value (optional)

FloatValue
----------
Value stores ``float`` type

Additional parameters:
- ``max_value`` - maximum value (optional)
- ``min_value`` - minimum value (optional)

DecimalValue
------------
Value stores ``decimal`` type

Additional parameters:
- ``max_value`` - maximum value (optional)
- ``min_value`` - minimum value (optional)
- ``max_digits`` - maximum number of digits (optional)
- ``decimal_places`` - maximum number of decimal places (optional)

ModelChoiceValue
----------------
Value stores reference to model instance.

Additional parameters:
- ``queryset`` - ``QuerySet`` of model objects (required)