from rest_framework import serializers

from base.models.group_element_year import GroupElementYear


class LinkFactory:
    def get_link(self, group_element_year: GroupElementYear):
        return Link(group_element_year)


factory = LinkFactory()


class Link(serializers.Serializer):
    parent = serializers.SerializerMethodField()
    child = serializers.SerializerMethodField()

    relative_credits = serializers.IntegerField()
    min_credits = serializers.IntegerField()
    max_credits = serializers.IntegerField()
    is_mandatory = serializers.BooleanField()
    block = serializers.SerializerMethodField()
    comment = serializers.CharField()
    comment_english = serializers.CharField()
    own_comment = serializers.CharField()
    quadrimester_derogation = serializers.CharField()
    link_type = serializers.CharField()

    def __getattr__(self, attr):
        if attr in self.get_fields().keys():
            return self.data[attr]
        return super().__getattr__(attr)

    def __dict__(self):
        return self.data

    def get_parent(self, obj):
        # TODO: Prevent cyclic import: Find another way
        from program_management.contrib.models.node import Node
        return Node(self.parent)

    def get_child(self, obj):
        # TODO: Prevent cyclic import: Find another way
        from program_management.contrib.models.node import Node
        return Node(self.child)

    def get_block(self, obj):
        return sorted([int(block) for block in str(obj.block or '')])

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        GroupElementYear.objects.create(**validated_data)
