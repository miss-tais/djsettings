from django.utils.text import camel_case_to_spaces


DEFAULT_NAMES = (
    'verbose_name',
)


class Options:
    def __init__(self, meta):
        self.verbose_name = None
        self.meta = meta

    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)

        self.object_name = cls.__name__
        self.verbose_name = camel_case_to_spaces(self.object_name)

        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                if name.startswith('_'):
                    del meta_attrs[name]

            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError(f"'class Meta' got invalid attribute(s): {','.join(meta_attrs)}")

        del self.meta

    def __repr__(self):
        return f'<Options for {self.object_name}>'

    def __str__(self):
        return f"{self.object_name.lower()}"

