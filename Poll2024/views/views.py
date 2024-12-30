from django.db.models import F, Prefetch
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from Poll2024.models import Employees, Votes, DeptManager, Scales, Departments
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory
from django.views import View
from Poll2024.forms import VanillaVoteForm
from django.db import transaction

def create_init_data(limit):
    # retrieve candidate info., along with department info.
    candidates = (
        Employees.objects.prefetch_related(
            Prefetch(
                'deptmanager_set',
                queryset=DeptManager.objects.select_related('dept_no'),
                # Attribute to store prefetched data
                to_attr='prefetched_dept_info'
            )
        )
        .all()
    )

    initial = [  # initial data
        {
            'emp_no': candidate.emp_no,
            'emp_name': f"{candidate.last_name}{candidate.first_name}",
            'dept_no': candidate.prefetched_dept_info[0]
            .dept_no.dept_no if candidate.prefetched_dept_info else None,
            'dept_name': candidate.prefetched_dept_info[0]
            .dept_no.dept_name if candidate.prefetched_dept_info else None,
            'scale': 2,  # set to "称职" as default
            'index': candidate.index_2024,
        }
        for candidate in candidates[:limit] # only pick division level
    ]
    return initial

def create_ranges():
    # ranges for each line
    index_list = [(0, 12), (12, 22), (22, 34), (34, 45), (45, 54), (54, 64), (64, 76)]
    ranges = [list(range(start, end)) for start, end in index_list]
    return ranges

def create_init_data_by_division_id(dept_no):
    # retrieve candidate info., along with department info.
    candidates = (
        Employees.objects.prefetch_related(
            Prefetch(
                'deptmanager_set',
                queryset=DeptManager.objects.select_related('dept_no'),
                # Attribute to store prefetched data
                to_attr='prefetched_dept_info'
            )
        )
        .all()
    )

    initial = []
    for candidate in candidates[:76]:
        dept_no_1 = candidate.prefetched_dept_info[0].dept_no.dept_no
        dept_no_2 = candidate.prefetched_dept_info[1].dept_no.dept_no if len(candidate.prefetched_dept_info) > 1 else None
        if dept_no in [dept_no_1, dept_no_2]:
            v = {
                'emp_no': candidate.emp_no,
                'emp_name': f"{candidate.last_name}{candidate.first_name}",
                'dept_no': candidate.prefetched_dept_info[0].dept_no.dept_no,
                'dept_name': candidate.prefetched_dept_info[0].dept_no.dept_name,
                'scale': 2,  # set to "称职" as default
                'index': candidate.index_2024,
            }
            initial.append(v)

    return initial

def create_ranges_for_bureau():
    # ranges for each line
    index_list = [(0, 9), (9, 17)]
    ranges = [list(range(start, end)) for start, end in index_list]
    return ranges

def update_initial(initial):
    for node in initial:
        if node['emp_name'] == '金岸睿':
            node['dept_name'] += '、党办'
        if node['emp_name'] == '穆菁':
            node['dept_name'] += '、公司三处'

class VoteCreateProxy(LoginRequiredMixin, View):
    vote_by_division_level = reverse_lazy('Poll2024:vote_division_level')
    vote_by_section_level = reverse_lazy('Poll2024:vote_section_level')
    vote_by_bureau_level = reverse_lazy('Poll2024:vote_bureau_level')
    success = reverse_lazy('Poll2024:exit')

    def get(self, request):
        voter = request.user
        if voter.voted: # if voter already voted
            return redirect(self.success)
        if voter.title_id.title_id == 2: # if voter is in division level
            # redirect to vote_by_division_level.html
            return redirect(self.vote_by_division_level)
        elif voter.title_id.title_id == 3: # if voter is in bureau level
            return redirect(self.vote_by_section_level)
        elif voter.username == 'ardnxp': # if voter is bureau chief: Ling
            return redirect(self.vote_by_bureau_level)
        # if voter is other bureau manager: Wang, He, or An.
        elif voter.username in ['mcsznj', 'uhqtaf', 'pvqsxj']:
            return redirect(self.vote_by_division_level)


class VoteCreateDivision(LoginRequiredMixin, View):

    template = 'Poll2024/vote_by_division_level.html'
    success = reverse_lazy('Poll2024:exit')

    def get(self, request):
        initial = create_init_data(76) # all division level

        # sort initial according to index
        sorted_initial = sorted(initial, key=lambda x: x['index'])

        # create formset for vote, and set up initial data
        vote_formset = formset_factory(form=VanillaVoteForm, extra=0)
        formset = vote_formset(initial=sorted_initial)

        ranges = create_ranges()

        ctx = {'formset': formset, 'ranges': ranges}
        return render(request, self.template, ctx)

    def post(self, request):
        vote_formset = formset_factory(form=VanillaVoteForm, extra=0)

        initial = create_init_data(76)
        # Binding the POST data to the formset
        formset = vote_formset(initial=initial, data=request.POST)

        if formset.is_valid():
            # retrieve all candidates and scales
            candidates = Employees.objects.all()
            scales = Scales.objects.all()

            # Create dictionaries for quick lookup
            candidate_dict = {candidate.emp_no: candidate for candidate in candidates}
            scale_dict = {scale.scale_id: scale for scale in scales}

            # Process the valid data
            # set user as voted
            request.user.voted = True
            # create vote formset
            votes = []
            for form in formset:
                emp_id = form.cleaned_data['emp_no']
                candidate = candidate_dict.get(emp_id)

                scale_id = int(form.cleaned_data['scale'])
                scale = scale_dict.get(scale_id)

                v = Votes(
                    voter=request.user,
                    emp_no=candidate,
                    scale=scale,
                    comment=form.cleaned_data['comment'],
                )
                votes.append(v)

            with transaction.atomic():
                Votes.objects.bulk_create(votes)
                request.user.save()
                return redirect(self.success)

        else:
            ranges = create_ranges()

            ctx = {'formset': formset, 'ranges': ranges}
            return render(request, self.template, ctx)


class VoteCreateSection(LoginRequiredMixin, View):

    template = 'Poll2024/vote_by_section_level.html'
    success = reverse_lazy('Poll2024:exit')

    def get(self, request):
        initial = create_init_data_by_division_id(request.user.dept_no.dept_no)
        dept_name = Departments.objects.get(dept_no=request.user.dept_no.dept_no)

        # sort initial according to index
        sorted_initial = sorted(initial, key=lambda x: x['index'])

        # create formset for vote, and set up initial data
        vote_formset = formset_factory(form=VanillaVoteForm, extra=0)
        formset = vote_formset(initial=sorted_initial)

        r = range(len(initial))

        ctx = {'formset': formset, 'range': r, 'dept_name': dept_name}
        return render(request, self.template, ctx)

    def post(self, request):
        vote_formset = formset_factory(form=VanillaVoteForm, extra=0)

        initial = create_init_data_by_division_id(request.user.dept_no.dept_no)
        dept_name = Departments.objects.get(dept_no=request.user.dept_no.dept_no)

        # sort initial according to index
        sorted_initial = sorted(initial, key=lambda x: x['index'])

        # Binding the POST data to the formset
        formset = vote_formset(initial=sorted_initial, data=request.POST)

        if formset.is_valid():
            # retrieve all candidates and scales
            candidates = Employees.objects.all()
            scales = Scales.objects.all()

            # Create dictionaries for quick lookup
            candidate_dict = {candidate.emp_no: candidate for candidate in candidates}
            scale_dict = {scale.scale_id: scale for scale in scales}

            # Process the valid data
            # set user as voted
            request.user.voted = True
            # create vote formset
            votes = []
            for form in formset:
                emp_id = form.cleaned_data['emp_no']
                candidate = candidate_dict.get(emp_id)

                scale_id = int(form.cleaned_data['scale'])
                scale = scale_dict.get(scale_id)

                v = Votes(
                    voter=request.user,
                    emp_no=candidate,
                    scale=scale,
                    comment=form.cleaned_data['comment'],
                )
                votes.append(v)

            with transaction.atomic():
                Votes.objects.bulk_create(votes)
                request.user.save()
                return redirect(self.success)

        else:
            r = range(len(initial))

            ctx = {'formset': formset, 'range': r, 'dept_name': dept_name}
            return render(request, self.template, ctx)


class VoteCreateBureau(LoginRequiredMixin, View):

    template = 'Poll2024/vote_by_bureau_level.html'
    success = reverse_lazy('Poll2024:exit')

    def get(self, request):
        initial = create_init_data(17) # all division leader
        update_initial(initial)

        # create formset for vote, and set up initial data
        vote_formset = formset_factory(form=VanillaVoteForm, extra=0)
        formset = vote_formset(initial=initial)

        ranges = create_ranges_for_bureau

        ctx = {'formset': formset, 'ranges': ranges}
        return render(request, self.template, ctx)

    def post(self, request):
        vote_formset = formset_factory(form=VanillaVoteForm, extra=0)

        initial = create_init_data(17) # all division leader
        update_initial(initial)

        # Binding the POST data to the formset
        formset = vote_formset(initial=initial, data=request.POST)

        if formset.is_valid():
            # retrieve all candidates and scales
            candidates = Employees.objects.all()
            scales = Scales.objects.all()

            # Create dictionaries for quick lookup
            candidate_dict = {candidate.emp_no: candidate for candidate in candidates}
            scale_dict = {scale.scale_id: scale for scale in scales}

            # Process the valid data
            # set user as voted
            request.user.voted = True
            # create vote formset
            votes = []
            for form in formset:
                emp_id = form.cleaned_data['emp_no']
                candidate = candidate_dict.get(emp_id)

                scale_id = int(form.cleaned_data['scale'])
                scale = scale_dict.get(scale_id)

                v = Votes(
                    voter=request.user,
                    emp_no=candidate,
                    scale=scale,
                    comment=form.cleaned_data['comment'],
                )
                votes.append(v)

            with transaction.atomic():
                Votes.objects.bulk_create(votes)
                request.user.save()
                return redirect(self.success)

        else:
            ranges = create_ranges_for_bureau

            ctx = {'formset': formset, 'ranges': ranges}
            return render(request, self.template, ctx)


class Logout(LoginRequiredMixin, View):

    def get(self, request):

        return render(request, 'Poll2024/exit.html')
