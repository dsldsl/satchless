from __future__ import absolute_import
from django.db import models
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor
from django.dispatch import receiver

class SubtypedManager(models.Manager):
    def find_subclasses(self, root):
        for a in dir(root):
            attr = getattr(root, a)
            if isinstance(attr, ReverseOneToOneDescriptor):
                child = attr.related.model
                if (issubclass(child, root) and
                    child is not root):
                    yield a
                    for s in self.find_subclasses(child):
                        yield '%s__%s' % (a, s)

    # https://code.djangoproject.com/ticket/16572
    #def get_queryset(self):
    #    qs = super(SubtypedManager, self).get_queryset()
    #    subclasses = list(self.find_subclasses(self.model))
    #    if subclasses:
    #        return qs.select_related(*subclasses)
    #    return qs


class Subtyped(models.Model):
    subtype_attr = models.CharField(max_length=500, editable=False)
    __in_unicode = False

    objects = SubtypedManager()

    class Meta:
        abstract = True

    def __str__(self):
        # XXX: can we do it in more clean way?
        if self.__in_unicode:
            return super(Subtyped, self).__unicode__()
        elif type(self.get_subtype_instance()) == type(self):
            self.__in_unicode = True
            res = self.__unicode__()
            self.__in_unicode = False
            return res
        else:
            return self.get_subtype_instance().__unicode__()

    def get_subtype_instance(self):
        """
        Caches and returns the final subtype instance. If refresh is set,
        the instance is taken from database, no matter if cached copy
        exists.
        """
        subtype = self
        path = self.subtype_attr.split()
        whoami = self._meta.model_name
        remaining = path[path.index(whoami)+1:]
        for r in remaining:
            subtype = getattr(subtype, r)
        return subtype

    def store_subtype(self, klass):
        if not self.id:
            path = [self]
            parents = list(self._meta.parents.keys())
            while parents:
                parent = parents[0]
                path.append(parent)
                parents = list(parent._meta.parents.keys())
            path = [p._meta.model_name for p in reversed(path)]
            self.subtype_attr = ' '.join(path)


@receiver(models.signals.pre_save)
def _store_content_type(sender, instance, **kwargs):
    if isinstance(instance, Subtyped):
        instance.store_subtype(instance)
