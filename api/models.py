from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver


class DefaultUser(AbstractUser):

    email = models.EmailField(max_length=50, unique=True)
    friends = models.ManyToManyField('DefaultUser', through='Friendship')

    def __str__(self):
        return self.username

    def has_friend(self, possible_friend):
        return self.friendships.filter(friend=possible_friend).exists()


class Friendship(models.Model):
    user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(DefaultUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'friend']]


class FriendRequest(models.Model):
    from_user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE, related_name='received_friend_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['from_user', 'to_user']]

    def accept_request(self):
        from_user = self.from_user
        to_user = self.to_user
        self.delete()
        Friendship.objects.get_or_create(from_user, to_user)


class Message(models.Model):
    friendship = models.ForeignKey(Friendship, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    has_been_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True)


@receiver(models.signals.post_delete, sender=Friendship)
def remove_reversed_friendship(instance, **kwargs):
    user = instance.user
    friend = instance.friend
    reversed_friendship = friend.friendships.filter(friend=user)
    if reversed_friendship.exists():
        reversed_friendship.delete()


@receiver(models.signals.post_save, sender=Friendship)
def create_reversed_friendship(instance, created, **kwargs):
    print(f'Created: {created}')
    if created:
        user = instance.user
        friend = instance.friend
        reversed_friendship, _ = Friendship.objects.get_or_create(friend=user, user=friend)


@receiver(models.signals.pre_save, sender=FriendRequest)
def stop_request_to_friend(instance, **kwargs):
    assert not instance.from_user.has_friend(instance.to_user), \
        AssertionError('Cannot send friend request to current friend!')
