from django.db import models
from django.forms import ModelForm

class Player(models.Model):
	player_name = models.CharField(max_length = 50)
	overall_rank = models.PositiveIntegerField()
	
	def __unicode__(self):
		return self.player_name
	
class Hero(models.Model):
	player = models.ForeignKey(Player)
	hero_name = models.CharField(max_length = 50)
	rank_number = models.PositiveIntegerField()
	
	def __unicode__(self):
		return self.hero_name
	
class Games(models.Model):
	player = models.ForeignKey(Player)
	hero = models.ForeignKey(Hero)
	last_hits = models.PositiveIntegerField()
	gpm = models.PositiveIntegerField()
	pub_date = models.DateTimeField(auto_now_add = True)
	
class PlayerForm(ModelForm):
	class Meta:
		model = Player
		
class HeroForm(ModelForm):
	class Meta:
		model = Hero
		
class GameForm(ModelForm):
	class Meta:
		model = Games