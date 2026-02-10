from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["home", "ehawp5", "offer", "privacy"]

    def location(self, item):
        return reverse(item)
