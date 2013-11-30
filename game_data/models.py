from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.urlresolvers import reverse
from django.db.models import F, Q, Max, Avg


class PlayerManager(models.Manager):
	def create_player(self, player_acct):
		if not player_acct:
			msg = "Player must have a name"
			raise ValueError(msg)

		player = self.create(player_acct=player_acct)
		return player

	def ranked(self, **kwargs):
		return self.filter(overall_rank__isnull=False, **kwargs)

	def worse_rank(self, rank):
		results = self.filter(overall_rank__isnull=False)
		return results.filter(Q(overall_rank__gt=rank))

	def worse_avg(self, avg_last_hits, avg_gpm):
		results = self.filter(overall_rank__isnull=False)
		return results.filter(Q(avg_last_hits=avg_last_hits, avg_gpm__lt=avg_gpm) | Q(avg_last_hits__lt=avg_last_hits))


class Player(models.Model):
	player_acct = models.ForeignKey(settings.AUTH_USER_MODEL)
	overall_rank = models.PositiveIntegerField(blank=True, null=True)
	avg_last_hits = models.DecimalField(max_digits=6, decimal_places=2, default=0, blank=True)
	avg_gpm = models.DecimalField(max_digits=6, decimal_places=2, default=0, blank=True)
	
	objects = PlayerManager()

	def __unicode__(self):
		return self.player_acct.get_short_name()


class Hero(models.Model):
	hero_name_underscored = models.CharField(max_length=60)
	hero_name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.hero_name_underscored


class GameManager(models.Manager):

	def ranked(self, **kwargs):
		return self.filter(rank_number__isnull=False, **kwargs)

	def worse_rank(self, hero, rank):
		return self.filter(hero=hero, rank_number__isnull=False).filter(rank_number__gt=rank)

	def worse_games(self, hero, last_hits, gpm):
		ret_filter = self.filter(Q(last_hits=last_hits, gpm__lt=gpm) | Q(last_hits__lt=last_hits))
		ret_filter = ret_filter.filter(hero=hero, rank_number__isnull=False)
		return ret_filter


class Game(models.Model):
	player = models.ForeignKey(Player, null=True)
	hero = models.ForeignKey(Hero)
	last_hits = models.PositiveIntegerField()
	gpm = models.PositiveIntegerField()
	pub_date = models.DateTimeField(auto_now_add=True)
	rank_number = models.PositiveIntegerField(null=True)

	objects = GameManager()

	def __unicode__(self):
		return u'%s %s' % (self.hero.hero_name, self.player.player_acct)

	def get_absolute_url(self):
		return reverse('game_data:successful_submit')


class DotaUserManager(BaseUserManager):
	def create_user(self, email, gamer_tag, password=None):
		if not email:
			msg = "User must have an email address"
			raise ValueError(msg)

		if not gamer_tag:
			msg = "User must have a Gamer Tag"
			raise ValueError(msg)

		user = self.model(email=DotaUserManager.normalize_email(email), gamer_tag=gamer_tag)
		user.set_password(password)
		user.save(using=self._db)

		player = Player.objects.create_player(user)
		player.save()
		return user

	def create_superuser(self, email, gamer_tag, password):
		user = self.create_user(email, gamer_tag=gamer_tag, password=password)
		user.is_staff = True
		user.is_admin = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class DotaUser(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(verbose_name="email address", max_length=255, unique=True, db_index=True)
	gamer_tag = models.CharField(max_length=255, unique=True)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["gamer_tag", ]

	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)

	objects = DotaUserManager()

	def get_short_name(self):
		return self.gamer_tag

	def __unicode__(self):
		return self.email