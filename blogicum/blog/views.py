from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .models import Post, Category, Comment
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)
from .forms import PostCreateForm, CommentCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy


User = get_user_model()


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.select_related(
                'category',
                'author',
                'location'
            )
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        qs = Post.objects.select_related(
            'category',
            'author',
            'location'
        ).order_by('-pub_date').prefetch_related('comments')

        user = self.request.user

        if user.is_authenticated:
            return qs.filter(
                Q(is_published=True,
                  category__is_published=True,
                  pub_date__lte=timezone.now())
                | Q(author=user)
            )
        else:
            return qs.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentCreateForm()
        context['comments'] = (
            self.get_object().comments.prefetch_related('author').all()
        )
        return context


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.select_related(
                'category',
                'author',
                'location'
            )
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
                category__slug=self.kwargs['category_slug']
            )
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return context


class ProfileDetailListView(ListView):
    model = Post  # Необязателен, но для ясности укажу
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        # Может быть вынесу в отдельный base_qs дублирующий код запроса к бд
        # Комментарии еще не реализованы, надо создать модель комментариев
        if self.user == self.request.user:
            return (
                Post.objects.select_related(
                    'category',
                    'author',
                    'location'
                )
                .filter(author=self.user)
                .annotate(comment_count=Count('comments'))
                .order_by('-pub_date')
            )
        return (
            Post.objects.select_related(
                'category',
                'author',
                'location'
            )
            .filter(
                author=self.user,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    queryset = Post.objects.select_related('author', 'location', 'category')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user.username,
            }
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    queryset = Post.objects.select_related('author', 'location', 'category')

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user != post.author:
            return redirect(
                'blog:post_detail',
                post_id=post.pk,
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'
    queryset = Post.objects.select_related('author', 'location', 'category')

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user != post.author:
            return redirect('blog:index')

        return super().delete(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreateForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentCreateForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if self.request.user != comment.author:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id'],
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if self.request.user != comment.author:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id'],
            )
        return super().delete(request, *args, **kwargs)
