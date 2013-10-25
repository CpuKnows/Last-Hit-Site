from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from game_data import views
from game_data.views import *

urlpatterns = patterns('',
                       url(r'^$', IndexView.as_view(), name='index'),
                       url(r'^submit_game/$', GameCreate.as_view(), name='submit_game'),
                       url(r'^successful_submit/$', TemplateView.as_view(template_name = 'game_data/successful_submit.html'), name='successful_submit'),
                       url(r'^hero/(?P<hero_name_underscored>[\w-]+)/$', HeroDetail.as_view(), name='hero_detail'),
                       url(r'^player/(?P<player_name_underscored>[\w-]+)/$', PlayerDetail.as_view(), name='player_detail'),)