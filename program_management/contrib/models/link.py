from rest_framework import serializers

from base.models.group_element_year import GroupElementYear


class LinkFactory:
    def get_link(self, group_element_year: GroupElementYear):
        return Link(
            parent=group_element_year.parent,
            child=group_element_year.child,
            instance=group_element_year,
        )


factory = LinkFactory()


class Link(serializers.Serializer):
    parent = serializers.SerializerMethodField()
    child = serializers.SerializerMethodField()

    relative_credits = serializers.IntegerField(required=False)
    min_credits = serializers.IntegerField(required=False)
    max_credits = serializers.IntegerField(required=False)
    is_mandatory = serializers.BooleanField(required=False)
    block = serializers.SerializerMethodField()
    comment = serializers.CharField(required=False)
    comment_english = serializers.CharField(required=False)
    own_comment = serializers.CharField(required=False)
    quadrimester_derogation = serializers.CharField(required=False)
    link_type = serializers.CharField(required=False)

    def __init__(self, **kwargs):
        self._parent = kwargs.pop('parent', None)
        self._child = kwargs.pop('child', None)
        super().__init__(**kwargs)

    def __getattr__(self, attr):
        if attr in self.get_fields().keys():
            return self[attr].value
        return super().__getattribute__(attr)

    def get_parent(self, obj):
        return self._parent

    def get_child(self, obj):
        return self._child

    def get_block(self, obj):
        block_str = str(obj.get('block', '')) or ''
        return sorted([int(block) for block in block_str])

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        gey_created = GroupElementYear.objects.create(
            parent_id=self.parent.pk,
            child_branch_id=self.child.pk,
            **validated_data,
        )
        return factory.get_link(gey_created)
