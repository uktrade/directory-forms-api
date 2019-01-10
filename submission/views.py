from rest_framework.generics import CreateAPIView

from submission import constants, serializers, tasks

from client.authentication import ClientSenderIdAuthentication


action_map = {
    constants.ACTION_NAME_EMAIL: (
        tasks.send_email,
        serializers.EmailActionSerializer,
    ),
    constants.ACTION_NAME_ZENDESK: (
        tasks.create_zendesk_ticket,
        serializers.ZendeskActionSerializer,
    ),
    constants.ACTION_NAME_GOV_NOTIFY: (
        tasks.send_gov_notify,
        serializers.GovNotifySerializer,
    ),
    constants.ACTION_NAME_PARDOT: (
        tasks.send_pardot,
        serializers.PardotSerializer,
    ),
}


class SubmissionCreateAPIView(CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance

        if instance.sender is None or instance.sender.is_enabled:
            task, kwargs_builder_class = action_map[instance.action_name]
            kwargs_builder = kwargs_builder_class.from_submission(instance)
            kwargs_builder.is_valid(raise_exception=True)
            task.delay(
                **kwargs_builder.validated_data,
                submission_id=instance.pk
            )
