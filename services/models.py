from django.db import models
# from pygments import highlight
# from pygments.formatters.html import HtmlFormatter
# from pygments.lexers import get_all_lexers, get_lexer_by_name
# from pygments.countrys import get_all_countrys

STYLES = ['airline', 'mart', 'spa']
COUNTRIES = ['US', 'CA', 'DE', 'FR']
STYLE_CHOICES = sorted([(item, item) for item in STYLES])
COUNTRY_CHOICES = sorted((item, item) for item in COUNTRIES)


class Service(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    is_opened = models.BooleanField(default=False)
    service_type = models.CharField(
        choices=STYLE_CHOICES, default='airline', max_length=100)
    country = models.CharField(
        choices=COUNTRY_CHOICES, default='US', max_length=100)
    owner = models.ForeignKey(
        'auth.User', related_name='services', on_delete=models.CASCADE)
    contact = models.TextField()

    class Meta:
        ordering = ('created', )

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a contact HTML
        representation of the description service.
        """
        # lexer = get_lexer_by_name(self.service_type)
        # is_opened = self.is_opened and 'table' or False
        # options = self.title and {'title': self.title} or {}
        # formatter = HtmlFormatter(
        #     country=self.country, is_opened=is_opened, full=True, **options)
        # self.contact = highlight(self.description, lexer, formatter)
        super(Service, self).save(*args, **kwargs)
