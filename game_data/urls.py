from django.conf.urls import patterns, url

from game_data import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^submit_game/$', views.submit_game, name='submit_game'),
                       url(r'^successful_submit/$', views.successful_submit, name='successful_submit'),
					   url(r'^hero/(?P<hero_name_in>[a-zA-Z]+)/$', views.hero_detail, name='hero_detail'),
                       url(r'^player/(?P<player_name_in>[a-zA-Z]+)/$', views.player_detail, name='player_detail'),)