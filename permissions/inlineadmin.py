from django.contrib.admin.options import InlineModelAdmin
from django.forms.models import (
    BaseModelFormSet, BaseInlineFormSet, inlineformset_factory, modelform_defines_fields,
    modelform_factory, modelformset_factory, ModelChoiceField, InlineForeignKeyField
)
from django.db import router
from django.contrib.admin.utils import (
    NestedObjects, construct_change_message, flatten_fieldsets,
    get_deleted_objects, lookup_needs_distinct, model_format_dict,
    model_ngettext, quote, unquote,
)
from django.contrib.admin.helpers import (InlineAdminFormSet, InlineAdminForm)
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldError, ImproperlyConfigured, ValidationError,
)
from django.forms.formsets import DELETION_FIELD_NAME, TOTAL_FORM_COUNT, BaseFormSet
from django.forms.widgets import (
    HiddenInput, MultipleHiddenInput, SelectMultiple,
)
from django.utils.text import capfirst, get_text_list
from functools import partial, reduce, update_wrapper


class CheckboxInlineAdminFormSet(InlineAdminFormSet):
    """
    A wrapper around an inline formset for use in the admin system.
    """

    def __iter__(self):
        if self.has_change_permission:
            readonly_fields_for_editing = self.readonly_fields
        else:
            readonly_fields_for_editing = self.readonly_fields + flatten_fieldsets(self.fieldsets)

        for form in self.formset.initial_forms:
            original = None
            if form.instance.pk is not None:
                original = form.instance
            view_on_site_url = self.opts.get_view_on_site_url(original)

            yield InlineAdminForm(
                self.formset, form, self.fieldsets, self.prepopulated_fields,
                original, readonly_fields_for_editing, model_admin=self.opts,
                view_on_site_url=view_on_site_url,
            )
        for form in self.formset.extra_forms:
            yield InlineAdminForm(
                self.formset, form, self.fieldsets, self.prepopulated_fields,
                None, self.readonly_fields, model_admin=self.opts,
            )
        if self.has_add_permission:
            yield InlineAdminForm(
                self.formset, self.formset.empty_form,
                self.fieldsets, self.prepopulated_fields, None,
                self.readonly_fields, model_admin=self.opts,
            )


class CheckboxInlineFormSetMixin():
    def _BaseModelFormSet_construct_form(self, i, **kwargs):
        unique_instance = self.unique_queryset()[i]
        pk_required = len(unique_instance.roles.filter(pk=self.instance.pk)) > 0
        if pk_required:
            if self.is_bound:
                pk_key = '%s-%s' % (self.add_prefix(i), self.model._meta.pk.name)
                try:
                    pk = self.data[pk_key]
                except KeyError:
                    # The primary key is missing. The user may have tampered
                    # with POST data.
                    pass
                else:
                    to_python = self._get_to_python(self.model._meta.pk)
                    try:
                        pk = to_python(pk)
                    except ValidationError:
                        # The primary key exists but is an invalid value. The
                        # user may have tampered with POST data.
                        pass
                    else:
                        kwargs['instance'] = self._existing_object(pk)
            else:
                kwargs['instance'] = self.get_queryset().filter(**{self.unique_name: unique_instance})[0]
        else:
            # Set initial values for extra forms
            kwargs['instance'] = self.model(**{self.unique_name: unique_instance})
        form = super(BaseModelFormSet, self)._construct_form(i, **kwargs)
        if pk_required:
            form.fields[self.model._meta.pk.name].required = True
        return form

    def BaseModelFormSet_add_fields(self, form, index):
        """Add a hidden field for the object's primary key."""
        from django.db.models import AutoField, OneToOneField, ForeignKey
        self._pk_field = pk = self.model._meta.pk
        # If a pk isn't editable, then it won't be on the form, so we need to
        # add it here so we can tell which object is which when we get the
        # data back. Generally, pk.editable should be false, but for some
        # reason, auto_created pk fields and AutoField's editable attribute is
        # True, so check for that as well.

        def pk_is_not_editable(pk):
            return (
                (not pk.editable) or (pk.auto_created or isinstance(pk, AutoField)) or (
                    pk.remote_field and pk.remote_field.parent_link and
                    pk_is_not_editable(pk.remote_field.model._meta.pk)
                )
            )
        if pk_is_not_editable(pk) or pk.name not in form.fields:
            if form.is_bound:
                # If we're adding the related instance, ignore its primary key
                # as it could be an auto-generated default which isn't actually
                # in the database.
                pk_value = None if form.instance._state.adding else form.instance.pk
            else:
                try:
                    if index is not None:
                        pk_value = getattr(form.instance, pk.name, None)
                    else:
                        pk_value = None
                except IndexError:
                    pk_value = None
            if isinstance(pk, (ForeignKey, OneToOneField)):
                qs = pk.remote_field.model._default_manager.get_queryset()
            else:
                qs = self.model._default_manager.get_queryset()
            qs = qs.using(form.instance._state.db)
            if form._meta.widgets:
                widget = form._meta.widgets.get(self._pk_field.name, HiddenInput)
            else:
                widget = HiddenInput
            form.fields[self._pk_field.name] = ModelChoiceField(qs, initial=pk_value, required=False, widget=widget)
        super(BaseModelFormSet, self).add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].initial = form.instance.pk is not None   # DELETE 初始化，做为select方式使用


class CheckboxInlineFormSet(BaseInlineFormSet, CheckboxInlineFormSetMixin):
    """A formset for child objects related to a parent."""

    def initial_form_count(self):
        """Return the number of forms that are required in this FormSet."""

        return self.max_num

    def _construct_form(self, i, **kwargs):
        form = self._BaseModelFormSet_construct_form(i, **kwargs)
        if self.save_as_new:
            mutable = getattr(form.data, '_mutable', None)
            # Allow modifying an immutable QueryDict.
            if mutable is not None:
                form.data._mutable = True
            # Remove the primary key from the form's data, we are only
            # creating new instances
            form.data[form.add_prefix(self._pk_field.name)] = None
            # Remove the foreign key from the form's data
            form.data[form.add_prefix(self.fk.name)] = None
            if mutable is not None:
                form.data._mutable = mutable

        # Set the fk value here so that the form can do its validation.
        fk_value = self.instance.pk
        if self.fk.remote_field.field_name != self.fk.remote_field.model._meta.pk.name:
            fk_value = getattr(self.instance, self.fk.remote_field.field_name)
            fk_value = getattr(fk_value, 'pk', fk_value)
        setattr(form.instance, self.fk.get_attname(), fk_value)
        return form

    def add_fields(self, form, index):
        self.BaseModelFormSet_add_fields(form, index)
        if self._pk_field == self.fk:
            name = self._pk_field.name
            kwargs = {'pk_field': True}
        else:
            # The foreign key field might not be on the form, so we poke at the
            # Model field to get the label, since we need that for error messages.
            name = self.fk.name
            kwargs = {
                'label': getattr(form.fields.get(name), 'label', capfirst(self.fk.verbose_name))
            }

        # The InlineForeignKeyField assumes that the foreign key relation is
        # based on the parent model's pk. If this isn't the case, set to_field
        # to correctly resolve the initial form value.
        if self.fk.remote_field.field_name != self.fk.remote_field.model._meta.pk.name:
            kwargs['to_field'] = self.fk.remote_field.field_name

        # If we're adding a new object, ignore a parent's auto-generated key
        # as it will be regenerated on the save request.
        if self.instance._state.adding:
            if kwargs.get('to_field') is not None:
                to_field = self.instance._meta.get_field(kwargs['to_field'])
            else:
                to_field = self.instance._meta.pk
            if to_field.has_default():
                setattr(self.instance, to_field.attname, None)

        form.fields[name] = InlineForeignKeyField(self.instance, **kwargs)

    def _should_delete_form(self, form):
        """Return whether or not the form was marked for deletion."""
        return form.instance.pk is not None and not form.cleaned_data.get(DELETION_FIELD_NAME, False)

    def _should_add_form(self, form):
        """Return whether or not the form was marked for deletion."""
        if hasattr(form, 'cleaned_data'):
            return form.instance.pk is None and form.cleaned_data.get(DELETION_FIELD_NAME, False)
        return False

    def full_clean(self):
        """
        Clean all of self.data and populate self._errors and
        self._non_form_errors.
        """
        self._errors = []
        self._non_form_errors = self.error_class()
        empty_forms_count = 0

        if not self.is_bound:  # Stop further processing.
            return
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            # Empty forms are unchanged forms beyond those with initial data.

            # if not form.has_changed() and i >= self.initial_form_count():
            #    empty_forms_count += 1
            # Accessing errors calls full_clean() if necessary.
            # _should_delete_form() requires cleaned_data.
            form_errors = form.errors
            if self.can_delete and self._should_delete_form(form):
                continue
            self._errors.append(form_errors)
        try:
            if (self.validate_max and
                    self.total_form_count() - len(self.deleted_forms) > self.max_num) or \
                    self.management_form.cleaned_data[TOTAL_FORM_COUNT] > self.absolute_max:
                raise ValidationError(ngettext(
                    "Please submit %d or fewer forms.",
                    "Please submit %d or fewer forms.", self.max_num) % self.max_num,
                    code='too_many_forms',
                )
            if (self.validate_min and
                    self.total_form_count() - len(self.deleted_forms) - empty_forms_count < self.min_num):
                raise ValidationError(ngettext(
                    "Please submit %d or more forms.",
                    "Please submit %d or more forms.", self.min_num) % self.min_num,
                    code='too_few_forms')
            # Give self.clean() a chance to do cross-form validation.
            self.clean()
        except ValidationError as e:
            self._non_form_errors = self.error_class(e.error_list)

    @property
    def extra_forms(self):
        """Return a list of all the extra forms in this formset."""
        extra_forms = [form for form in self.forms if self._should_add_form(form)]
        return extra_forms

    @property
    def deleted_forms(self):
        """Return a list of forms that have been marked for deletion."""
        if not self.is_valid() or not self.can_delete:
            return []
        # construct _deleted_form_indexes which is just a list of form indexes
        # that have had their deletion widget set to True
        if not hasattr(self, '_deleted_form_indexes'):
            self._deleted_form_indexes = []
            for i in range(0, self.total_form_count()):
                form = self.forms[i]
                # if this is an extra form and hasn't changed, don't consider it
                # if i >= self.initial_form_count() and not form.has_changed():
                #     continue
                if form.has_changed() and self._should_delete_form(form):
                    self._deleted_form_indexes.append(i)
        return [self.forms[i] for i in self._deleted_form_indexes]


class CheckboxInlineModelAdmin(InlineModelAdmin):
    """
    Options for inline editing of ``model`` instances.

    Provide ``fk_name`` to specify the attribute name of the ``ForeignKey``
    from ``model`` to its parent. This is required if ``model`` has more than
    one ``ForeignKey`` to its parent.
    """
    formset = CheckboxInlineFormSet
    unique_name = None
    template = 'admin/edit_inline/tabular_select.html'

    def __init__(self, parent_model, admin_site):
        super().__init__(parent_model, admin_site)
        self.extra = 0
        # self.can_delete = False
        self.unique_name = self._get_unique_name()
        self.unique_model = self._get_unique_foreign_model()

    def _get_unique_name(self):
        """
        Find and return the unique_together  other filed from model if there is one
        (return None if can_fail is True and no such field exists). If unique_name is
        provided, assume it is the name of the unique_together field. Unless can_fail is
        True, raise an exception if there isn't a unique_together from model.
        """
        opts = self.model._meta

        if hasattr(opts, 'unique_together'):
            unique_together = list(self.model._meta.unique_together[0])
            if not len(unique_together) == 2:
                raise ValueError(
                    "'%s' unique_together  is too complex not support '%s'." % (opts.label, unique_together)
                )
            else:
                unique_together.remove(self.fk_name)

                if self.unique_name is None:
                    self.unique_name = unique_together[0]
                else:
                    if self.unique_name != unique_together[0]:
                        raise ValueError(
                            "'%s' has no unique_together named ['%s' ,'%s']." % (opts.label, self.fk, unique_name)
                        )

        return self.unique_name

    def _get_unique_foreign_model(self):
        """
        Find and return the unique_together  other filed from model if there is one
        (return None if can_fail is True and no such field exists). If unique_name is
        provided, assume it is the name of the unique_together field. Unless can_fail is
        True, raise an exception if there isn't a unique_together from model.
        """
        from django.db.models import ForeignKey
        opts = self.model._meta
        if self.unique_name:
            fks_to_unique = [f for f in opts.fields if f.name == self.unique_name]
            if len(fks_to_unique) == 1:
                fk = fks_to_unique[0]
                if not isinstance(fk, ForeignKey):
                    raise ValueError(
                        "unique_name '%s' is not a ForeignKey to '%s'." % (self.unique_name, opts.label)
                    )
                self.unique_model = fk.related_model
            elif not fks_to_unique:
                raise ValueError(
                    "'%s' has no field named '%s'." % (opts.label, fk_name)
                )
        else:
            raise ValueError(
                "'%s' has no unique_name '%s'." % (self.__name__)
            )
        return self.unique_model

    def get_unique_queryset(self):
        return self.unique_model.objects.all          # objects = _default_manager

    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        return self.unique_model.objects.count()

    # def get_formset(self, request, obj=None, **kwargs):
    #     Formset.unique_name = self.unique_name
    #     Formset.unique_queryset = self.get_unique_queryset()
    #     # Formset._queryset = self.get_unique_queryset()
    #     return Formset

    def get_formset(self, request, obj=None, **kwargs):
        """Return a BaseInlineFormSet class for use in admin add/change views."""
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        exclude.extend(self.get_readonly_fields(request, obj))
        if excluded is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # InlineModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # If exclude is an empty list we use None, since that's the actual
        # default.
        exclude = exclude or None
        can_delete = self.can_delete and self.has_delete_permission(request, obj)
        defaults = {
            'form': self.form,
            'formset': self.formset,
            'fk_name': self.fk_name,
            'fields': fields,
            'exclude': exclude,
            'formfield_callback': partial(self.formfield_for_dbfield, request=request),
            'extra': self.get_extra(request, obj, **kwargs),
            'min_num': self.get_min_num(request, obj, **kwargs),
            'max_num': self.get_max_num(request, obj, **kwargs),
            'can_delete': can_delete,
            **kwargs,
        }

        base_model_form = defaults['form']
        can_change = self.has_change_permission(request, obj) if request else True
        can_add = self._has_add_permission(request, obj) if request else True

        class SelectProtectedModelForm(base_model_form):

            def hand_clean_Select(self):
                """
                We don't validate the 'DELETE' field itself because on
                templates it's not rendered using the field information, but
                just using a generic "deletion_field" of the InlineModelAdmin.
                """
                if self.cleaned_data.get(
                        'pk', None):
                    if not self.cleaned_data.get(
                            DELETION_FIELD_NAME, False):
                        using = router.db_for_write(self._meta.model)
                        collector = NestedObjects(using=using)
                        if self.instance._state.adding:
                            return
                        collector.collect([self.instance])
                        if collector.protected:
                            objs = []
                            for p in collector.protected:
                                objs.append(
                                    # Translators: Model verbose name and instance representation,
                                    # suitable to be an item in a list.
                                    _('%(class_name)s %(instance)s') % {
                                        'class_name': p._meta.verbose_name,
                                        'instance': p}
                                )
                            params = {
                                'class_name': self._meta.model._meta.verbose_name,
                                'instance': self.instance,
                                'related_objects': get_text_list(objs, _('and')),
                            }
                            msg = _("Deleting %(class_name)s %(instance)s would require "
                                    "deleting the following protected related objects: "
                                    "%(related_objects)s")
                            raise ValidationError(msg, code='deleting_protected', params=params)
                else:
                    if self.cleaned_data.get(
                            DELETION_FIELD_NAME, False):
                        using = router.db_for_write(self._meta.model)
                        collector = NestedObjects(using=using)
                        if self.instance._state.adding:
                            return

            def is_valid(self):
                result = super().is_valid()
                self.hand_clean_Select()
                return result

            def has_changed(self):
                # Protect against unauthorized edits.
                if not can_change and not self.instance._state.adding:
                    return False
                if not can_add and self.instance._state.adding:
                    return False
                return super().has_changed()

        defaults['form'] = SelectProtectedModelForm

        if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
            defaults['fields'] = forms.ALL_FIELDS

        Formset = inlineformset_factory(self.parent_model, self.model, **defaults)

        Formset.unique_name = self.unique_name
        Formset.unique_queryset = self.get_unique_queryset()
        return Formset
