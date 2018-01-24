from django.conf.urls import url

from data import views


handler404 = 'data.views.page_not_found'

urlpatterns = [
    url(r'^designers/$', views.DesignerList.as_view()),
    url(r'^designers/(?P<pk>[^/]+)/$', views.DesignerDetail.as_view()),
    url(r'^designers/(?P<designer_id>[^/]+)/items/$', views.DesignerItems.as_view()),
    url(r'^items/$', views.ItemList.as_view()),
    url(r'^items/(?P<pk>[^/]+)/$', views.ItemDetail.as_view()),
    url(r'^items/featured$', views.FeaturedItems.as_view()),
    url(r'^stores/$', views.StoreList.as_view()),
    url(r'^stores/(?P<pk>[^/]+)/$', views.StoreDetail.as_view()),
    url(r'^stores/(?P<store_id>[^/]+)/items/$', views.StoreItems.as_view()),
    url(r'^subcategories/$', views.subcategory_list, name='subcategory_list'),
    url(r'^create_user$', views.create_user, name='create_user'),
    url(r'^users/bag$', views.update_bag, name='bag'),
    url(r'^users/favorites$', views.update_favorites, name='favorites'),
    url(r'^users/preferences$', views.update_preferences, name='preferences'),
    url(r'^generate_items/$', views.generate_items, name='generate_items'),
    url(r'^generate_stores/$', views.generate_stores, name='generate_stores'),
    url(r'^generate_designers/$', views.generate_designers, name='generate_designers'),
]
