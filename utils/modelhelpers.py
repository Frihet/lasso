import django.db.models.fields.related
import django.contrib.admin.util

class SubclasModelMixin(object):
    @classmethod
    def get_model_subclass_relations(cls, other = None):
        if other: cls = other
        res = {}
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, django.db.models.fields.related.SingleRelatedObjectDescriptor) and issubclass(attr.related.model, cls) and cls is not attr.related.model:
                res[name] = attr.related.model
        return res

    @classmethod
    def get_model_superclass_relations(cls, other = None):
        if other: cls = other
        res = {}
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, django.db.models.fields.related.ReverseSingleRelatedObjectDescriptor) and issubclass(cls, attr.field.rel.to) and cls is not attr.field.rel.to:
                res[name] = attr.field.rel.to
        return res

    @property
    def subclassobject(self):
        for name in self.get_model_subclass_relations().iterkeys():
            # Use try around this since Django throws DoesNotExist instead of AttributeError... Bah!
            try:
                value = getattr(self, name, None)
            except:
                value = None
            if value is not None:
                return value
        return self

    @property
    def superclassobject(self):
        for name in self.get_model_superclass_relations().iterkeys():
            # Use try around this since Django throws DoesNotExist instead of AttributeError... Bah!
            try:
                value = getattr(self, name)
            except:
                value = None
            if value is not None:
                return value
        return self

class MustBeOverriddenError(Exception):
    pass

def subclassproxy(fn):
    is_property = isinstance(fn, property)
    if is_property:
        fn = fn.fget

    name = fn.func_name

    def proxy(self, *arg, **kw):
        if self.subclassobject is self:
            try:
                return fn(self, *arg, **kw)
            except MustBeOverriddenError:
                try:
                    strrepr = unicode(self)
                except:
                    strrepr = id(self)
                raise NotImplementedError("%s.%s is a subclass proxy, but %s is not an instance of a subclass that overides it" % (type(self), name, strrepr))
        res = getattr(self.subclassobject, name)
        if not is_property:
            res = res(*arg, **kw)
        return res

    if is_property:
        proxy = property(proxy)
    return proxy



django.contrib.admin.util.old_format_callback = django.contrib.admin.util._format_callback
def _format_callback(obj, user, admin_site, levels_to_root, perms_needed):
    res = django.contrib.admin.util.old_format_callback(obj, user, admin_site, levels_to_root, perms_needed)

    subclass_key = SubclasModelMixin.get_model_subclass_relations(type(obj))
    try:
        subclassobject = getattr(obj, subclass_key.keys()[0], None)
    except:
        subclassobject = None

    if subclassobject and obj._meta.verbose_name in perms_needed:
        perms_needed.remove(obj._meta.verbose_name)
    return res
django.contrib.admin.util._format_callback = _format_callback
