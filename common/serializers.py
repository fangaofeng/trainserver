from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers


from rest_framework.utils import model_meta
from rest_framework.serializers import raise_errors_on_nested_writes


class OwnerFlexFSerializer(FlexFieldsModelSerializer):
    creater = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )


class OwnerFieldSerializer(serializers.ModelSerializer):
    creater = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )


class ADDDELSerializer(serializers.ModelSerializer):

    # PUT add manytomany
    # PATCH delete manytomany
    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                if self.partial:
                    field.remove(*value)  # 对象不存在时，没有提示
                else:
                    field.add(*value)
            else:
                setattr(instance, attr, value)
        if not self.partial:
            instance.save()

        return instance


class CurrentUserDepartmentDefault:
    def set_context(self, serializer_field):

        self.department = getattr(serializer_field.context['request'].user, 'managerdepartment', None)

    def __call__(self):
        return self.department

    def __repr__(self):
        return '%s()' % self.__class__.__name__
