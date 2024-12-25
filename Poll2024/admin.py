from django.contrib import admin
from django import forms
from .models import Question, Choice, Employees, Departments, Titles
from .models import DeptManager


#class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]

# Register your models here.
# admin.site.register(Question, QuestionAdmin)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['dept_name', 'created_date', 'location']

admin.site.register(Departments, DepartmentAdmin)

class TitleForm(forms.ModelForm):
    class Meta:
        model = Titles
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定制 emp_no 字段的显示
        self.fields['emp_no'].queryset = Employees.objects.all()
        self.fields['emp_no'].label_from_instance = lambda obj: f"{obj.emp_no} ({obj.last_name}{obj.first_name})"

class TitleAdmin(admin.ModelAdmin):
    form = TitleForm

admin.site.register(Titles, TitleAdmin)

class DepartmentInline(admin.StackedInline):
    model = Departments

class TitleInline(admin.StackedInline):
    model = Titles

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

class EmployeeAdmin(admin.ModelAdmin):
    inlines = [TitleInline]
    list_display = ['emp_no', 'get_fullname', 'get_departments', 'get_title']
    form = EmployeeForm

    def get_fullname(self, obj):
        return f"{obj.last_name}{obj.first_name}"

    get_fullname.short_description = "姓名"

    def save_model(self, request, obj, form, change):
        # 先保存 Employee 实例
        super().save_model(request, obj, form, change)

        # 处理多对多的 Department 并创建 Management 记录
        if 'departments' in form.cleaned_data:
            departments = form.cleaned_data['departments']
            # 删除旧的 Management 记录（可选）
            DeptManager.objects.filter(emp_no=obj).delete()
            # 创建新的 Management 记录
            for department in departments:
                DeptManager.objects.create(emp_no=obj, dept_no=department)

    def get_departments(self, obj):
        # 查询通过 DeptManager 表与 Employee 关联的部门
        departments = Departments.objects.filter(deptmanager__emp_no=obj)
        return ", ".join([dept.dept_name for dept in departments])

        # optimized version
        # departments = obj.deptmanager_set.prefetch_related('dept_no')
        # return ", ".join([dm.dept_no.dept_name for dm in departments])

    get_departments.short_description = '部门'

    def get_title(self, obj):
        titles = Titles.objects.filter(emp_no=obj)
        return ", ".join([i.title for i in titles])

    get_title.short_description = "职级"


admin.site.register(Employees, EmployeeAdmin)

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

class DeptManagerAdmin(admin.ModelAdmin):
    form = DeptManagerForm

admin.site.register(DeptManager, DeptManagerAdmin)