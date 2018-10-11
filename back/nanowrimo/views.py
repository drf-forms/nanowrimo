import os

from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout
from django.http import Http404
from django.conf import settings

from rest_framework import status
from rest_framework.viewsets import (ModelViewSet as DRFModelViewSet,
                                     ReadOnlyModelViewSet as DRFReadOnlyModelViewSet)
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Book
from .serializers import UserSerializer, LoginSerializer


class CoalesceFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        id_list = request.query_params.getlist('ids[]')
        if id_list:
            view.pagination_class = None
            queryset = queryset.filter(id__in=id_list)
        return queryset


class ModelViewSet(DRFModelViewSet):
    filter_backends = (CoalesceFilterBackend,)


class ReadOnlyModelViewSet(DRFReadOnlyModelViewSet):
    filter_backends = (CoalesceFilterBackend,)


class MeView(RetrieveAPIView):

    serializer_class = UserSerializer
    queryset = get_user_model().objects
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return self.get_queryset().get(pk=self.request.user.id)


class LoginView(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            login(request, serializer.validated_data['user'])
            return Response({}, status=status.HTTP_200_OK)
        return Response(None, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        logout(request)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('first_name', 'last_name',)


class EmberView(TemplateView):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            raise Http404()
        return super(EmberView, self).get(request, *args, **kwargs)


EMBER_DIST_PATH = os.path.join(settings.BASE_DIR, '..', 'front', 'dist')


def service_worker_view(request, filetype, buildhash):
    return serve(request, '{}-{}.js'.format(filetype, buildhash), EMBER_DIST_PATH)


def root_files_view(request, filename):
    return serve(request, filename, EMBER_DIST_PATH)


class BookViewset(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        print(args, kwargs)
        rv = super(BookViewset, self).dispatch(request, *args, **kwargs)
        try:
            book = self.get_object()
            request.session['current_book'] = book.id
        except Exception:
            pass
        return rv


class BookRelatedViewSet(ModelViewSet):

    def _get_kwargs(self):
        kwargs = {}
        book_id = self.request.session.get('current_book', None)
        if book_id is not None:
            try:
                kwargs['book'] = Book.objects.get(id=book_id)
            except Exception:
                pass
        return kwargs

    def get_queryset(self):
        return super(BookRelatedViewSet, self).get_queryset().filter(**self._get_kwargs())

    def perform_create(self, serializer):
        print(self._get_kwargs, self.request.session.keys())
        serializer.save(**self._get_kwargs())

    def perform_update(self, serializer):
        serializer.save(**self._get_kwargs())

