#from django.http import Http404
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse
# from django.template import loader

from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    """ full version
    template = loader.get_template("Poll2024/index.html")
    context = {
        "latest_question_list": latest_question_list,
    }
    return HttpResponse(template.render(context, request))
    """

    """ short version"""
    context = {"latest_question_list": latest_question_list}
    return render(request, "Poll2024/index.html", context)
    #output = ", ".join([q.question_text for q in latest_question_list])
    #return HttpResponse(output)

def detail(request, question_id):
    #return HttpResponse("You're looking at question %s." % question_id)
    """ full version
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "Poll2024/detail.html", {"question": question})
    """

    """ short version"""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "Poll2024/detail.html", {"question": question})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
