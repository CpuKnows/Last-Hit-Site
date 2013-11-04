from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dotalh.views.home', name='home'),
    # url(r'^dotalh/', include('dotalh.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	url(r'^game_data/', include('game_data.urls', namespace = "game_data")),
	url(r'^admin/', include(admin.site.urls)),
)
