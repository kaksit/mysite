
from multiprocessing import context
from django.shortcuts import render,get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from taggit.models import Tag
from django.db.models import Count

# Create your views here.

def post_list(request,tag_slug=None):
    posts=Post.published.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        posts=posts.filter(tags__in=[tag])
    paginator=Paginator(posts,4)
    page=request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
    context={
        "posts":posts,
        "page":page,
        "tag":tag,
        }
    return render(request,'blog/post/list.html/',context)

# class PostListView(ListView):
#     queryset=Post.objects.all()
#     context_object_name="posts"
#     paginate_by=4
#     template_name='blog/post/list.html'


def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post,slug=post, status="published",publish__year=year,publish__month=month,publish__day=day)
    # این قسمت گرفتن کامنتها و فرستادن برای نمایش زیر پوستها است 
    comments=post.comments.filter(active=True)
    # بر گشت پوستهای مشابه
    post_tags_ids=post.tags.values_list('id',flat=True)
    similar_posts=Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts=similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    # این قسمت مربوط به فرم نظر سنجی است که زیز پستها قرلر می گیرد 
    if request.method == 'POST':
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
           new_comment=comment_form.save(commit=False)
           new_comment.post=post
           new_comment.save()
           return HttpResponseRedirect(request.path_info)
    else:
        comment_form=CommentForm()

    context={
        "post" : post,
        "form":comment_form,
        "comments":comments,
        "similar_posts":similar_posts,

    }

    return render(request,'blog/post/detail.html/',context)

def post_share(request,post_id):
    post=get_object_or_404(Post,id=post_id,status="published")
    if request.method=='POST':
        form=EmailPostForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            post_url=request.build_absolute_uri(
                post.get_absolute_url())
            subject=f"{cd['name']} recommevd you"
            message=f"{post.title} in { post_url} and {cd['comments']}"
            send_mail(subject,message,"kaksite.com@gmail.com",[cd['to']])

    else:
        form=EmailPostForm()
    context={
        "post":post,
        "form":form,
    
        }
    return render(request,'blog/post/share.html',context)



