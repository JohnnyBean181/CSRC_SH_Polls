from django import forms
from pkg_resources import require

from .models import Employees, Votes

SCALE_CHOICES = [
    (1, "优秀"),
    (2, "称职"),
    (3, "基本称职"),
    (4, "不称职"),
]


class VoteForm(forms.ModelForm):
    class Meta:
        model = Votes
        fields = '__all__'


class VanillaVoteForm(forms.Form):
    my_attrs = {
        'readonly': 'readonly',
        'style': 'border:none;'
                 'background:none;'
                 'width: 100px;'
                 'height: 35px;'
                 'font-size: 18px;'
                 'font-family: "仿宋";'
                 'text-align: center;',
        'class': 'clickable-readonly-input',
    }

    dept_no = forms.IntegerField()
    dept_name = forms.CharField()
    emp_no = forms.IntegerField()
    emp_name = forms.CharField()
    emp_name.widget = forms.TextInput(attrs=my_attrs)
    scale = forms.ChoiceField(
        choices=SCALE_CHOICES,  #
        widget=forms.Select(attrs={'class': 'centered-select'})
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'label': "评论",  #
            'cols': 10,
            'rows': 3,
            'placeholder': "至少4字",
        })
    )

    def clean(self):
        """
        Custom form cleaning method to validate constraints.
        """
        # Calls the parent's clean method to do initial validation.
        cleaned_data = super().clean()

        # Check if a comment is provided when the scale is '不称职' (Not Competent).
        scale_value = int(cleaned_data.get('scale'))
        comment = cleaned_data.get('comment')

        # '不称职' or '基本称职'.
        if scale_value >= 3 and len(comment.strip()) < 4:
            self.add_error('comment', "字数太少。")

        if len(comment.strip()) > 49:
            self.add_error('comment', "字数太多。")

        return cleaned_data  # Always return the cleaned data, whether it has errors or not.


