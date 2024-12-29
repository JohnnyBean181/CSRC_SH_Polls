from django import forms
from .models import Employees, Departments, Titles, DeptManager

class TitleForm(forms.ModelForm):
    class Meta:
        model = Titles
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定制 emp_no 字段的显示
        self.fields['emp_no'].queryset = Employees.objects.all()
        self.fields['emp_no'].label_from_instance = lambda obj: f"{obj.emp_no} ({obj.last_name}{obj.first_name})"

class EmployeeForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Departments.objects,
        widget=forms.CheckboxSelectMultiple,  # 使用复选框
        required=True # ,
        #to_field_name= "dept_name"
    )

    class Meta:
        model = Employees
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定制 emp_no 字段的显示
        self.fields['departments'].label_from_instance = lambda obj: obj.dept_name

class DeptManagerForm(forms.ModelForm):

    class Meta:
        model = DeptManager
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定制 emp_no 字段的显示
        self.fields['dept_no'].queryset = Departments.objects.all()
        self.fields['dept_no'].label_from_instance = lambda obj: f"{obj.dept_no} ({obj.dept_name})"
        self.fields['emp_no'].queryset = Employees.objects.all()
        self.fields['emp_no'].label_from_instance = lambda obj: f"{obj.emp_no} ({obj.last_name}{obj.first_name})"
