"""Unit tests for blog models."""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site
from wagtail.rich_text import RichText

from blog.models import BlogPage

User = get_user_model()


@pytest.mark.unit
class TestBlogModels(TestCase):
    """Test blog models functionality."""

    def setUp(self):
        """Set up test data."""
        # Get the root page
        self.root_page = Page.objects.get(title="Root")
        
    def test_blog_page_creation(self):
        """Test BlogPage model creation."""
        blog_page = BlogPage(
            title="Test Blog Post",
            intro="This is a test intro",
            body=RichText("<p>This is test content</p>"),
            slug="test-blog-post"
        )
        
        # Add to root page
        self.root_page.add_child(instance=blog_page)
        blog_page.save()
        
        # Test the page was created
        self.assertEqual(blog_page.title, "Test Blog Post")
        self.assertEqual(blog_page.intro, "This is a test intro")
        self.assertEqual(blog_page.slug, "test-blog-post")
        
    def test_blog_page_str_method(self):
        """Test BlogPage string representation."""
        blog_page = BlogPage(title="Test Blog Post")
        self.assertEqual(str(blog_page), "Test Blog Post")
        
    def test_blog_page_get_context(self):
        """Test BlogPage get_context method."""
        blog_page = BlogPage(
            title="Test Blog Post",
            intro="Test intro",
            body=RichText("<p>Test content</p>")
        )
        self.root_page.add_child(instance=blog_page)
        blog_page.save()
        
        # Mock request object
        from django.http import HttpRequest
        request = HttpRequest()
        
        context = blog_page.get_context(request)
        
        # Test context contains expected keys
        self.assertIn('page', context)
        self.assertEqual(context['page'], blog_page)
        
    def test_blog_page_live_and_public(self):
        """Test BlogPage live and public methods."""
        blog_page = BlogPage(
            title="Test Blog Post",
            live=True
        )
        self.root_page.add_child(instance=blog_page)
        blog_page.save()
        
        # Test live pages query
        live_pages = BlogPage.objects.live()
        self.assertIn(blog_page, live_pages)
        
        # Test public pages query  
        public_pages = BlogPage.objects.public()
        self.assertIn(blog_page, public_pages)
