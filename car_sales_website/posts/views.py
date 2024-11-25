from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from . import forms
from . import models
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from .models import Post, Comment, Order
from .forms import CommentFrom

# Create your views here.
# @login_required 
# def add_Post(request):
#     if request.method == 'POST':
#         post_form = forms.PostFrom(request.POST)
#         if post_form.is_valid():
#             # post_form.cleaned_data['author'] = request.user
#             post_form.instance.author = request.user
#             post_form.save()
#             return redirect('add_Post')
#     else:
#         post_form = forms.PostFrom()
#     return render(request, 'add_post.html', {'form' : post_form})


# Add post user normally website e gele blank form pabe
@method_decorator(login_required, name='dispatch')
class AddPostCreateView(CreateView):
    model = models.Post
    form_class = forms.PostFrom
    template_name = 'add_post.html'
    success_url = reverse_lazy('add_Post')
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class EditPostView(UpdateView):
    model = models.Post
    form_class = forms.PostFrom
    template_name = 'add_post.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('profile')


@login_required 
def delete_Post(request, id):
    post = models.Post.objects.get(pk=id)
    post.delete()
    return redirect('homepage')


@method_decorator(login_required, name='dispatch')
class DeletePostView(DeleteView):
    model = models.Post
    template_name = 'delete.html'
    success_url = reverse_lazy('profile')
    pk_url_kwarg = 'id'

class PostDetailView(View):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=kwargs['pk'])
        comments = Comment.objects.filter(post=post)
        comment_form = CommentFrom()
        return render(request, 'post_details.html', {
            'post': post,
            'comments': comments,
            'comment_form': comment_form
        })

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=kwargs['pk'])

        # Handle Buy Now
        if 'buy_now' in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, "You must log in to buy this product.")
                return redirect('login')
            if post.quantity > 0:
                post.quantity -= 1
                post.save()
                order = Order.objects.create(user=request.user, post=post)
                print("Order Created:", order)
                messages.success(request, "Purchase successful!")
            else:
                messages.error(request, "Sorry, this item is out of stock.")
            return redirect('detail_Post', pk=post.id)

        # Handle Comment Form
        comment_form = CommentFrom(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, "Your comment has been added.")
        else:
            messages.error(request, "There was an error with your comment.")
        
        return redirect('detail_Post', pk=post.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object  # post model er object ekhane store Korlam
        comments = post.comments.all()
        comment_form = forms.CommentFrom()

        context['comments'] = comments
        context['comment_form'] = comment_form
        return context


        