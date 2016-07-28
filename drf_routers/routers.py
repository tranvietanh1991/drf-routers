"""
Routers for nested resources.

Example:

    # urls.py

    from rest_framework_nested import routers

    router = routers.SimpleRouter()
    router.register(r'domains', DomainViewSet)

    domains_router = routers.NestedSimpleRouter(router, r'domains', lookup='domain')
    domains_router.register(r'nameservers', NameserverViewSet)

    url_patterns = patterns('',
        url(r'^', include(router.urls)),
            url(r'^', include(domains_router.urls)),
            )

        router = routers.DefaultRouter()
        router.register('users', UserViewSet, 'user')
        router.register('accounts', AccountViewSet, 'account')

        urlpatterns = router.urls
"""
from __future__ import unicode_literals
import logging
logger = logging.getLogger(__name__)

from collections import OrderedDict, namedtuple
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import NoReverseMatch
from django.core.urlresolvers import reverse


class LookupMixin(object):
	"""
	Deprecated.

	No method override is needed since Django Rest Framework 2.4.
	"""


def reverseBase(request, view_name, absolute=False, urlconf=None, args=None, kwargs=None, prefix=None,
				current_app=None):
	if not request.resolver_match.namespace:
		namespace = ''
	else:
		namespace = request.resolver_match.namespace + ':'
	rev_url = reverse(namespace + view_name, urlconf, args, kwargs, prefix, current_app);
	if absolute:
		rev_url = request.build_absolute_uri(rev_url)
	return rev_url;


class GroupedRouter(DefaultRouter):
	"""
	The GroupedRouter router extends the DefaultRouter, add feature to include another
	GroupedRouter, NestedRouter or DefaultRounter to show in api root view
	"""
	include_root_view = True
	include_format_suffixes = True
	root_view_name = 'api-root'

	def __init__(self, root_view_name='api-root'):
		super(self.__class__, self).__init__();
		self.includeRouterList = []
		self.root_view_name = root_view_name

	def get_api_root_view(self):
		"""
		Return a view to use as the API root.
		"""
		# api_root_dict = {}
		list_name = self.routes[0].name
		# for prefix, viewset, basename in self.registry:
		# 	api_root_dict[prefix] = basename, viewset  # list_name.format(basename=basename)
		routerSelf = self;
		class_name = self.root_view_name.replace('-', '_').capitalize()

		class APIRoot(APIView):
			_ignore_model_permissions = True

			def get(self, request, *args, **kwargs):
				ret = []
				for r in routerSelf.includeRouterList:
					logger.debug("root_view_name:%s" % r.root_view_name);
					try:
						ret += [{
							'name': r.root_view_name,
							'url': reverseBase(request, r.root_view_name, absolute=True),
						}]
					except NoReverseMatch:
						continue;

				for api_prefix, api_viewset, api_basename in routerSelf.registry:
					logger.debug("api_prefix=%s | api_viewset=%s | api_basename=%s"%(api_prefix, api_viewset, api_basename));
					for route in routerSelf.get_routes(api_viewset):
						# Only actions which actually exist on the viewset will be bound
						mapping = routerSelf.get_method_map(api_viewset, route.mapping)
						if not mapping:
							continue

						viewName = route.name.format(basename=api_basename);

						reverseKwagrs = {};

						# suffix = route.initkwargs.get('suffix');
						# if suffix==u'List':
						# 	pass;
						# elif suffix==u'Instance':
						# 	reverseKwagrs = {'pk':1}

						if 'lookup' in route.url:
							reverseKwagrs = {'pk': 1}

						logger.debug("viewName:%s" % viewName);
						try:
							ret += [{
								'name': viewName,
								'methods': mapping,
								'url': reverseBase(request, viewName, absolute=True, kwargs=reverseKwagrs),
								# 'url': request.build_absolute_uri(request.get_full_path()+url[1:-1].format(prefix=prefix,lookup='1',trailing_slash='/')),
								# 'initKwagrs': str(route.initkwargs),

							}];
						except NoReverseMatch:
							continue;

				return Response(ret)

		APIRoot.__name__ = self.root_view_name;
		return APIRoot.as_view()

	def get_urls(self):
		urlpatterns = super(self.__class__, self).get_urls();
		for r in self.includeRouterList:
			urlpatterns.append(url('^' + r.root_view_name + '/', include(r.urls)));

		return urlpatterns;

	def include(self, r):
		""" Include another router to this route

		:param r: an instance of DefaultRouter
		:return:
		"""
		self.includeRouterList.append(r);


class NestedRouter(DefaultRouter):
	def __init__(self, parent_router, parent_prefix, *args, **kwargs):
		""" Create a NestedRouter nested within `parent_router`
		Args:

		parent_router: Parent router. Mayb be a simple router or another nested
			router.

		parent_prefix: The url prefix within parent_router under which the
			routes from this router should be nested.

		lookup:
			The regex variable that matches an instance of the parent-resource
			will be called '<lookup>_<parent-viewset.lookup_field>'
			In the example above, lookup=domain and the parent viewset looks up
			on 'pk' so the parent lookup regex will be 'domain_pk'.
			Default: 'nested_<n>' where <n> is 1+parent_router.nest_count

		"""
		self.parent_router = parent_router
		self.parent_prefix = parent_prefix
		self.nest_count = getattr(parent_router, 'nest_count', 0) + 1
		self.nest_prefix = kwargs.pop('lookup', 'nested_%i' % self.nest_count) + '_'
		super(NestedRouter, self).__init__(*args, **kwargs)
		parent_registry = [registered for registered in self.parent_router.registry if
						   registered[0] == self.parent_prefix]
		try:
			parent_registry = parent_registry[0]
			parent_prefix, parent_viewset, parent_basename = parent_registry
		except:
			raise RuntimeError('parent registered resource not found')

		nested_routes = []
		parent_lookup_regex = parent_router.get_lookup_regex(parent_viewset, self.nest_prefix)

		self.parent_regex = '{parent_prefix}/{parent_lookup_regex}/'.format(
			parent_prefix=parent_prefix,
			parent_lookup_regex=parent_lookup_regex
		)
		if hasattr(parent_router, 'parent_regex'):
			self.parent_regex = parent_router.parent_regex + self.parent_regex

		for route in self.routes:
			route_contents = route._asdict()

			# This will get passed through .format in a little bit, so we need
			# to escape it
			escaped_parent_regex = self.parent_regex.replace('{', '{{').replace('}', '}}')

			route_contents['url'] = route.url.replace('^', '^' + escaped_parent_regex)
			nested_routes.append(type(route)(**route_contents))

		self.routes = nested_routes
