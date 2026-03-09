
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home/index.html"

    # def post(self, request, *args, **kwargs):
    #     try:
    #         data = json.loads(request.body)
    #     except json.JSONDecodeError:
    #         return JsonResponse(
    #             {'error': 'JSON inválido'},
    #             status=400
    #         )

    #     # IP simple
    #     ip = request.META.get('REMOTE_ADDR')

    #     # Aquí luego puedes guardar en DB
    #     # VisitorLog.objects.create(ip=ip, ...)

    #     return JsonResponse({'ok': True})