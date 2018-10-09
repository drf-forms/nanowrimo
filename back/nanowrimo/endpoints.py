from django.contrib.contenttypes.models import ContentType

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import router, register

from levit_report.models import Document
from .models import Book, Chapter, Place, Prop, Character, Scene, InventoryExchange


@register
class BookEndpoint(Endpoint):
    model = Book
    exclude_fields = ('author', )


for Model in (Document, Chapter, Place, Prop, Character, Scene, InventoryExchange):
    router.register(Model)

router.register(ContentType, read_only=True, list_me=False)
