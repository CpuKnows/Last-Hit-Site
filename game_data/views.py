from django import forms
from django.forms import ModelForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.views import generic

from game_data.models import *

def index(request):
	hero_list = Hero.objects.order_by('hero_name')
	context = {'hero_list':hero_list}
	return render(request, 'game_data/index.html', context)
	
def hero_detail(request, hero_name_in):
	hero = get_object_or_404(Hero, hero_name = hero_name_in)
	#hero_player_list = get_list_or_404(Hero, hero_name = hero_name_in)
	hero_game_list = Games.objects.filter(hero = hero).order_by('last_hits', 'gpm','pub_date')
	context = {'hero': hero, 'hero_game_list': hero_game_list}
	return render(request, 'game_data/hero_detail.html', context)
	
def player_detail(request, player_name_in):
	player = get_object_or_404(Player, player_name = player_name_in)
	#player_hero_list = Hero.objects.filter(player = player)
	player_game_list = Games.objects.filter(player = player).order_by('-pub_date')
	context = {'player': player, 'player_game_list': player_game_list}
	return render(request, 'game_data/player_detail.html', context)
	
def get_hero_choices():
	return Hero.objects.all().order_by('hero_name')
	
def get_player_choices():
	return Player.objects.all().order_by('player_name')
		
def submit_game(request):
	if request.method == 'POST':
		form = GameForm(request.POST)
		
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('game_data:successful_submit'))
			
	else:
		form = GameForm()
	
	context = {'form': form}
	return render(request, 'game_data/submit_game.html', context)
	
def successful_submit(request):
	return render(request, 'game_data/successful_submit.html', {})