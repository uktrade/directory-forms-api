from rest_framework.generics import ListCreateAPIView

from submission import constants, serializers, tasks
from submission.models import Submission

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


class SubmissionCreateAPIView(ListCreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def get_queryset(self):
        sso_user_id = self.request.query_params['sso_user_id']
        if not sso_user_id or not sso_user_id.isnumeric():
            return Submission.objects.none()

        return Submission.objects.filter(
            meta__sender__sso_user_id=int(sso_user_id)
        ).order_by('-created')

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
