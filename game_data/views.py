from django import forms
from django.forms import ModelForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

from game_data.models import *

class IndexView(generic.ListView):
	template_name = 'game_data/index.html'
	context_object_name = 'latest_game_list'
	
	def get_queryset(self):
		return Games.objects.order_by('-pub_date')[:5]
	
	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)
		context['hero_list'] = Hero.objects.all()
		context['player_list'] = Player.objects.all()
		context['hero_table_widths'] = range(0, 200, 5)
		return context
		
	
class HeroDetail(generic.DetailView):
	model = Hero
	template_name = 'game_data/hero_detail.html'
	slug_field = 'hero_name'
	slug_url_kwarg = 'hero_name'
	
	def get_context_data(self, **kwargs):
		context = super(HeroDetail, self).get_context_data(**kwargs)
		hero = get_object_or_404(Hero, hero_name = self.kwargs['hero_name'])
		context['hero_game_list'] = Games.objects.filter(hero = hero).order_by('-last_hits', '-gpm','-pub_date')
		return context
		
	
class PlayerDetail(generic.DetailView):
	model = Player
	template_name = 'game_data/player_detail.html'
	slug_field = 'player_name'
	slug_url_kwarg = 'player_name'
	
	def get_context_data(self, **kwargs):
		context = super(PlayerDetail, self).get_context_data(**kwargs)
		player = get_object_or_404(Player, player_name = self.kwargs['player_name'])
		context['player_game_list'] = Games.objects.filter(player = player).order_by('-last_hits', '-gpm','-pub_date')
		return context
		

class GameCreate(CreateView):
	model = Games
	template_name = 'game_data/submit_game.html'
	fields = ['player', 'hero', 'last_hits', 'gpm', 'pub_date']
	