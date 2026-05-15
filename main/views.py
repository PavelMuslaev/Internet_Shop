from typing import Any, Callable, ClassVar

from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import DetailView, TemplateView

from .models import Category, Product, Size


class IndexView(TemplateView):
    """Render the home page shell and its HTMX partial."""

    template_name = "main/base.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add navigation categories to the base home context."""
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["current_category"] = None
        return context

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Return only the home partial for HTMX requests."""
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "main/home_content.html", context)

        return TemplateResponse(request, self.template_name, context)


class CatalogView(TemplateView):
    """Render the product catalog with search, category and filter support."""

    template_name = "main/base.html"

    FILTER_MAPPING: ClassVar[
        dict[str, Callable[[QuerySet[Product], str], QuerySet[Product]]]
    ] = {
        "color": lambda queryset, value: queryset.filter(color__iexact=value),
        "min_price": lambda queryset, value: queryset.filter(price__gte=value),
        "max_price": lambda queryset, value: queryset.filter(price__lte=value),
        "size": lambda queryset, value: queryset.filter(
            product_sizes__size__name=value
        ),
    }

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Build catalog context from URL kwargs and GET filters."""
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get("category_slug")
        categories = Category.objects.all()
        products = Product.objects.all().order_by("-created_at")
        current_category = None

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)

        if query := self.request.GET.get("q"):
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            if value := self.request.GET.get(param):
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = ""

        filter_params["q"] = query or ""

        context.update(
            {
                "categories": categories,
                "products": products,
                "current_category": current_category,
                "filter_params": filter_params,
                "sizes": Size.objects.all(),
                "search_query": query or "",
            }
        )

        if self.request.GET.get("show_search") == "true":
            context["show_search"] = True
        elif self.request.GET.get("reset_search") == "true":
            context["reset_search"] = True

        return context

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Render catalog partials for HTMX requests and the full shell otherwise."""
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            if context.get("show_search"):
                return TemplateResponse(request, "main/search_input.html", context)
            if context.get("reset_search"):
                return TemplateResponse(request, "main/search_button.html", {})
            template = (
                "main/filter_modal.html"
                if request.GET.get("show_filters") == "true"
                else "main/catalog.html"
            )
            return TemplateResponse(request, template, context)
        return TemplateResponse(request, self.template_name, context)


class ProductDetailView(DetailView):
    """Render a single product page by slug."""

    model = Product
    template_name = "main/base.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add category navigation and related products to the detail context."""
        context = super().get_context_data(**kwargs)
        product = self.object
        context["categories"] = Category.objects.all()
        context["related_products"] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        context["current_category"] = product.category.slug
        return context

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Return only the product detail partial for HTMX requests."""
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "main/product_detail.html", context)
        return TemplateResponse(request, self.template_name, context)
