from rest_framework import serializers


class PlannerRequestSerializer(serializers.Serializer):
    experiment_id = serializers.IntegerField(min_value=1)


class ExperimentPlanningRequestSerializer(serializers.Serializer):
    experiment_id = serializers.IntegerField(min_value=1)


class RetrievalRequestSerializer(serializers.Serializer):
    experiment_id = serializers.IntegerField(
        min_value=1
    )

    limit_per_query = serializers.IntegerField(
        min_value=1,
        max_value=10,
        default=3,
        required=False,
    )


class ContentGenerationRequestSerializer(serializers.Serializer):
    experiment_id = serializers.IntegerField(min_value=1)
    retrieved_context = serializers.CharField(required=False, allow_blank=True, default="")


class ValidationRequestSerializer(serializers.Serializer):
    experiment_id = serializers.IntegerField(min_value=1)


class DocumentGenerationRequestSerializer(serializers.Serializer):
    experiment_id = serializers.IntegerField(min_value=1)