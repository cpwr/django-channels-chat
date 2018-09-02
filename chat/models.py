from django.contrib.auth.models import User
from django.db import models

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from enum import IntEnum, unique


@unique
class MessageType(IntEnum):

    MESSAGE = 0  # For standard messages
    WARNING = 1  # For yellow messages
    ALERT = 2  # For red & dangerous alerts
    MUTED = 3  # For just OK information that doesn't bother users
    ENTER = 4  # For just OK information that doesn't bother users
    LEAVE = 5  # For just OK information that doesn't bother users

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


class Message(models.Model):
    """
    This class represents a chat message. It has an author (user), timestamp and
    the message body.
    """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='user',
        related_name='from_user', db_index=True,
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='recipient',
        related_name='to_user', db_index=True,
    )
    timestamp = models.DateTimeField(
        'timestamp', auto_now_add=True, editable=False,
        db_index=True,
    )
    body = models.TextField('body')
    type = models.IntegerField(
        choices=[x for x in MessageType.choices()],
        db_index=True, default=MessageType.MESSAGE,
        null=False, blank=False,
    )

    class Meta:
        app_label = 'chat'
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-timestamp',)

    def __str__(self):
        return f"Message id={self.pk}"

    @property
    def characters(self):
        """
        Toy function to count body characters.
        :return: body's char number
        """
        return len(self.body)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {'text': '%s' % self.pk}
        channel_layer = get_channel_layer()

        Group('%s' % self.recipient.pk).send(notification)
        Group('%s' % self.author.pk).send(notification)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.pk
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super().save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()


class Room(models.Model):
    """
    A room for people to chat in.
    """

    # Room title
    title = models.CharField(max_length=255)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return "room-%s" % self.pk
