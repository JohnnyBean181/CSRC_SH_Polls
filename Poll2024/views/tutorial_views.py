from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from ..models import Choice, Question


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
    return render(request, "Poll2024/Tutorial/index.html", context)
    #output = ", ".join([q.question_text for q in latest_question_list])
    #return HttpResponse(output)

class IndexView(generic.ListView):
    template_name = "Poll2024/Tutorial/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]

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
    return render(request, "Poll2024/Tutorial/detail.html", {"question": question})

class DetailView(generic.DetailView):
    model = Question
    template_name = "Poll2024/Tutorial/detail.html"

def results(request, question_id):
    #response = "You're looking at the results of question %s."
    #return HttpResponse(response % question_id)
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "Poll2024/Tutorial/results.html", {"question": question})

class ResultsView(generic.DetailView):
    model = Question
    template_name = "Poll2024/Tutorial/results.html"

def vote(request, question_id):
    # return HttpResponse("You're voting on question %s." % question_id)
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "Poll2024/Tutorial/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("Poll2024:results", args=(question.id,)))


