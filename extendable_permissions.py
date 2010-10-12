from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django import template
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib import admin

class ExtendablePermissionAdminMixin(object):
    def get_model_perms(self, request):
        object_name = self.opts.object_name.lower()
        app_label = self.opts.app_label.lower()
        permissions = ([perm[0][:len(perm[0]) - 1 - len(object_name)]
                        for perm in getattr(self.opts, 'permissions', ())]
                       + ['add', 'change', 'delete'])
        return dict((permission, request.user.has_perm("%s.%s_%s" % (app_label, permission, object_name)))
                    for permission in permissions)

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        perm = opts.app_label + '.%s_' + opts.object_name.lower()
        if request.method == 'POST':
            return request.user.has_perm(perm % 'change')
        else:
            return request.user.has_perm(perm % 'change') or request.user.has_perm(perm % 'view') or request.user.has_perm(perm % 'view_own') 

    def has_real_change_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_real_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': self.admin_site.root_path,
        })
        if not self.has_real_change_permission(request, obj):
            for fieldset in context['adminform']:
                for line in fieldset:
                    for field in line:
                        field.field.field.widget.attrs['disabled'] = 'disabled'
            for formset in context['inline_admin_formsets']:
                for form in formset:
                    for fieldset in form:
                        for line in fieldset:
                            for field in line:
                                field.field.field.widget.attrs['disabled'] = 'disabled'

        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.change_form_template or [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ], context, context_instance=context_instance)

    def queryset(self, request):
        qs = admin.ModelAdmin.queryset(self, request)
        opts = self.opts
        perm = opts.app_label + '.%s_' + opts.object_name.lower()
        if request.user.has_perm(perm % 'view'):
            return qs
        elif request.user.has_perm(perm % 'view_own'):
            return qs.filter(**{self.owner_field: request.user})
        else:
            return qs.filter(**{self.owner_field: -1}) # The empty QuerySet :)
