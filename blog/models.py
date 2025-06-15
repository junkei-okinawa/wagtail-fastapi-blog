from typing import ClassVar

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels: ClassVar[list] = [*Page.content_panels, FieldPanel("intro")]

    subpage_types: ClassVar[list[str]] = ["blog.BlogPage"]

    def get_context(self, request):
        """パフォーマンス最適化: 子ページを効率的に取得"""
        context = super().get_context(request)

        # select_related/prefetch_related でクエリ数を削減
        blog_pages = (
            self.get_children()
            .live()
            .public()
            .specific()
            .select_related("content_type")
            .order_by("-first_published_at")[:10]
        )  # 最新10件のみ

        context["blog_pages"] = blog_pages
        return context


class BlogPage(Page):
    date = models.DateField("Post date", db_index=True)  # インデックス追加
    intro = models.CharField(max_length=250, db_index=True)  # インデックス追加
    body = RichTextField(blank=True)

    search_fields: ClassVar[list] = [
        *Page.search_fields,
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types: ClassVar[list[str]] = ["blog.BlogIndexPage"]

    class Meta:
        # データベースレベルでのソート最適化
        indexes: ClassVar[list] = [
            models.Index(fields=["-date"]),
            models.Index(fields=["intro", "date"]),
        ]
