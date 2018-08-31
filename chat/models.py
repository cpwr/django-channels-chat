from channels import Group
from django.contrib.auth.models import User
from django.db import models


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
        notification = {'text': '%s' % self.id}
        Group('%s' % self.recipient.id).send(notification)
        Group('%s' % self.author.id).send(notification)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super().save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()
