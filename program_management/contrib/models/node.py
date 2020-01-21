from rest_framework import serializers

from program_management.contrib.models.link import Link
from program_management.models.element import Element
from program_management.models.enums import node_type


class NodeFactory:
    def get_node(self, element: Element):
        node_cls = {
            node_type.EDUCATION_GROUP: NodeEductionGroupYear,   # TODO: Remove when migration is done

            node_type.GROUP: NodeGroupYear,
            node_type.LEARNING_UNIT: NodeLearningUnitYear,
            node_type.LEARNING_CLASS: NodeLearningClassYear
        }[element.node_type]
        return node_cls(element)


factory = NodeFactory()


class Node(serializers.Serializer):
    children = Link(read_only=True, many=True, default=list())

    def add_child(self, node):
        link_to_append = Link(parent=self, child=node)
        self.children = Link(data=self.children.data + [link_to_append], many=True)

    def __getattr__(self, attr):
        if attr in self.get_fields().keys():
            return self.data[attr]
        return super().__getattr__(attr)


class NodeEductionGroupYear(Node):      # TODO: Remove when migration is done
    pk = serializers.IntegerField(read_only=True, source='education_group_year.pk')
    acronym = serializers.CharField(source='education_group_year.acronym')
    title = serializers.CharField(source='education_group_year.title')
    year = serializers.IntegerField(source='education_group_year.academic_year.year')


class NodeGroupYear(Node):
    pk = serializers.IntegerField(read_only=True, source='group_year.pk')
    acronym = serializers.CharField(source='group_year.acronym')
    title = serializers.CharField(source='group_year.title')
    year = serializers.IntegerField(source='group_year.academic_year.year')


class NodeLearningUnitYear(Node):
    pk = serializers.IntegerField(read_only=True, source='learning_unit_year.pk')
    acronym = serializers.CharField(source='learning_unit_year.acronym')
    title = serializers.CharField(source='learning_unit_year.complete_title')
    year = serializers.IntegerField(source='learning_unit_year.academic_year.year')


class NodeLearningClassYear(Node):
    pk = serializers.IntegerField(read_only=True, source='learning_unit_class.pk')
    year = serializers.IntegerField(source='learning_unit_class.academic_year.year')
