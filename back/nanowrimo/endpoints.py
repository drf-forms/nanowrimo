from django.contrib.contenttypes.models import ContentType

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import router, register

from levit_report.models import Document
from .models import Book, Chapter, Place, Prop, Character, Scene, InventoryExchange
from .serializers import BookRelatedSerializer
from .views import BookViewset, BookRelatedViewSet


@register
class BookEndpoint(Endpoint):
    model = Book
    base_viewset = BookViewset
    exclude_fields = ('author', )


class BookRelatedEndpoint(Endpoint):
    base_viewset = BookRelatedViewSet
    base_serializer = BookRelatedSerializer


@register
class PlaceEndpoint(BookRelatedEndpoint):
    model = Place


@register
class ChapterEndpoint(BookRelatedEndpoint):
    model = Chapter


@register
class CharacterEndpoint(BookRelatedEndpoint):
    model = Character


@register
class PropEndpoint(BookRelatedEndpoint):
    model = Prop


@register
class SceneEndpoint(BookRelatedEndpoint):
    model = Scene


@register
class InventoryExchangeEndpoint(BookRelatedEndpoint):
    model = InventoryExchange


router.register(Document)
router.register(ContentType, read_only=True, list_me=False)
