from django import forms
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormView

from .forms import PlayerForm, GameForm, DotaUserCreationForm
from .models import Player, Hero, Game, DotaUser
from .rank_logic import add_update_hero_ranking, update_player_rank


class IndexView(ListView):
	template_name = 'game_data/index.html'
	context_object_name = 'latest_game_list'
	
	def get_queryset(self):
		return Game.objects.order_by('-pub_date')[:5]
	
	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)
		context['hero_list'] = Hero.objects.all()
		context['player_list'] = Player.objects.all()
		context['hero_table_widths'] = range(0, 200, 5)
		return context
		
	
class HeroDetail(DetailView):
	model = Hero
	template_name = 'game_data/hero_detail.html'
	slug_field = 'hero_name_underscored'
	slug_url_kwarg = 'hero_name_underscored'
	
	def get_context_data(self, **kwargs):
		context = super(HeroDetail, self).get_context_data(**kwargs)
		hero = get_object_or_404(Hero, hero_name_underscored=self.kwargs['hero_name_underscored'])
		context['hero_game_list'] = Game.objects.ranked(hero=hero).order_by('-last_hits', '-gpm', '-pub_date')
		return context
		
	
class PlayerDetail(DetailView):
	model = Player
	template_name = 'game_data/player_detail.html'
	
	def get_context_data(self, **kwargs):
		context = super(PlayerDetail, self).get_context_data(**kwargs)
		player = get_object_or_404(Player, pk=self.kwargs['pk'])
		context['player_game_list'] = Game.objects.filter(player=player).order_by('-last_hits', '-gpm', '-pub_date')
		return context
		

class GameCreate(CreateView):
	model = Game
	form_class = GameForm
	template_name = 'game_data/submit_game.html'
	submitted_game = None
	
	def form_valid(self, form):
		self.submitted_game = form.instance
		return super(GameCreate, self).form_valid(form)
		
	def get_success_url(self):
		if self.submitted_game:
			add_update_hero_ranking(self.submitted_game)
			update_player_rank(self.submitted_game)
		return super(GameCreate, self).get_success_url()


class UserLogin(FormView):
	form_class = AuthenticationForm
	redirect_field_name = REDIRECT_FIELD_NAME
	template_name = 'game_data/login.html'
	
	player_acct = ''
	
	def dispatch(self, *args, **kwargs):
		return super(UserLogin, self).dispatch(*args, **kwargs)
	
	def form_valid(self, form):
		login(self.request, form.get_user())
		self.player_acct = Player.objects.filter(player_acct=form.get_user())
		return super(UserLogin, self).form_valid(form)
	
	def get_success_url(self):
		if self.player_acct[0] is not None:
			success_url = reverse('game_data:player_detail', kwargs={'pk': self.player_acct[0].pk})
		else:
			success_url = reverse('game_data:index')
		return success_url


class UserCreation(FormView):
	model = DotaUser
	form_class = DotaUserCreationForm
	redirect_field_name = REDIRECT_FIELD_NAME
	template_name = 'game_data/sign_up.html'

	def dispatch(self, *args, **kwargs):
		return super(UserCreation, self).dispatch(*args, **kwargs)
	
	def form_valid(self, form):
		form.save()
		player_form = PlayerForm()
		player_form.player_acct = form
		return super(UserCreation, self).form_valid(form)

	def get_success_url(self):
		success_url = reverse('game_data:login')
		return success_url
