from django.db import models
from django.contrib.auth.models import AbstractUser

class DefaultUser(AbstractUser):

    email = models.EmailField(max_length=50, unique=True)
    friends = models.ManyToManyField('DefaultUser', through='Friendship')

    def __str__(self):
        return self.username

    def has_friend(self, possible_friend):
        return self.friendships.filter(friend=possible_friend).exists()

class FriendshipQuerySet(models.QuerySet):

    def create(self, user: DefaultUser, friend: DefaultUser):
        default_fs = super().create(user=user, friend=friend)
        reversed_fs = super().create(user=friend, friend=user)
        default_fs.reversed = reversed_fs
        reversed_fs.reversed = default_fs
        default_fs.save()
        reversed_fs.save()
        return default_fs

class Friendship(models.Model):
    user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(DefaultUser, on_delete=models.CASCADE)
    reversed = models.ForeignKey('Friendship', on_delete=models.CASCADE, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = FriendshipQuerySet.as_manager()

    class Meta:
        unique_together = [['user', 'friend']]

class FriendRequestManager(models.Manager):
    def create(self, from_user: DefaultUser, to_user: DefaultUser):
        friendship_queryset = from_user.friendships.filter(friend__username=to_user.username)
        assert not friendship_queryset.exists(), AssertionError('User already friend in friend list.')
        self.super().create(from_user=from_user, to_user=to_user)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE, related_name='received_friend_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    objects = FriendRequestManager

    class Meta:
        unique_together = [['from_user', 'to_user']]

    def accept_request(self) -> Friendship:
        from_user = self.from_user
        to_user = self.to_user
        friendship, _ = Friendship.objects.get_or_create(user=from_user, friend=to_user)
        self.delete()
        return friendship

    def reject_request(self):
        self.delete()

class Message(models.Model):
    friendship = models.ForeignKey(Friendship, on_delete=models.CASCADE, related_name='messages')
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    has_been_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True)
