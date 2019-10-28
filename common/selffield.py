from rest_framework import serializers
from django.utils import six
class ChoiceField(serializers.ChoiceField):


    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        try:
            return self.choice_strings_to_values.get(six.text_type(data), data)
        except KeyError:
            self.fail('invalid_choice', input=data)

    def to_representation(self, value):
        if value in ('', None):
            return value
        return self.choice_values_to_strings.get(six.text_type(value), value)
    def _get_choices(self):
        return self._choices

    def _set_choices(self, choices):
        super(ChoiceField, self)._set_choices(choices)
        #
        self.choice_strings_to_values = {
            six.text_type(value): key for key,value in self.choices.items()
        }
        self.choice_values_to_strings = {
            six.text_type(key): value for key,value in self.choices.items()
        }

    choices = property(_get_choices, _set_choices)
