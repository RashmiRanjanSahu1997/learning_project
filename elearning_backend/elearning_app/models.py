import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from django.utils import timezone

GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]


class DateTimeMixin(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        auto_created=True,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


CLASS_TYPES = [
    ("online", "Online"),
    ("offline", "Offline"),
]
RECURRING = [
    ("daily", "Online"),
    ("weekly", "Weekly"),
    ("monthly", "Monthly"),
]


class EmployeeType(DateTimeMixin):
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.type)


class EmploymentType(DateTimeMixin):
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.type)


class EmployeePosition(DateTimeMixin):
    name = models.CharField(
        max_length=150, verbose_name=_("Employee Position Name"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Employee Position Table")

    def __str__(self):
        return self.name


class ClassDetails(DateTimeMixin):
    name = models.CharField(max_length=200)
    division = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _("Class Details")

    def __str__(self):
        return f"{self.name} {self.division}"


class User(AbstractUser, DateTimeMixin):
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email ID"),
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Middle Name")
    )
    contact = models.CharField(
        max_length=15, blank=True, null=True, verbose_name=_("Contact Number")
    )
    emergency_contact = models.CharField(
        max_length=15, blank=True, null=True, verbose_name=_("Emergency contact")
    )
    emergency_contact_name = models.CharField(
        max_length=15, blank=True, null=True, verbose_name=_("Emergency contact Name")
    )

    language = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Home Language")
    )
    gender = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        choices=GENDER_CHOICES,
        verbose_name=_("Gender"),
    )
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    address = models.CharField(_("Address"), max_length=255, null=True, blank=True)
    zip_code = models.CharField(_("ZIP Code"), max_length=10, null=True, blank=True)
    bio = models.TextField(_("Bio"), null=True, blank=True)
    employment_type = models.ForeignKey(
        EmploymentType, blank=True, null=True, on_delete=models.CASCADE
    )
    employee_type = models.ForeignKey(
        EmployeeType, blank=True, null=True, on_delete=models.CASCADE
    )
    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Position"),
    )
    class_name = models.ForeignKey(
        ClassDetails,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Class"),
    )
    photo = models.FileField(upload_to="media/profile/", null=True, blank=True)
    mother_first_name = models.CharField(max_length=100, null=True, blank=True)
    mother_middle_name = models.CharField(max_length=100, null=True, blank=True)
    mother_last_name = models.CharField(max_length=100, null=True, blank=True)
    father_first_name = models.CharField(max_length=100, null=True, blank=True)
    father_middle_name = models.CharField(max_length=100, null=True, blank=True)
    father_last_name = models.CharField(max_length=100, null=True, blank=True)
    mother_contact_no = models.CharField(max_length=50, null=True, blank=True)
    father_contact_no = models.CharField(max_length=50, null=True, blank=True)
    parent_mail = models.EmailField(
        verbose_name=_("Parent Email ID"),
        blank=True,
        null=True,
    )
    attendance = models.IntegerField(
        default=0, verbose_name=_("Attendance"), blank=True, null=True
    )
    leaves = models.IntegerField(
        default=0, verbose_name=_("Total Leaves"), blank=True, null=True)
    rank = models.CharField(max_length=50, null=True, blank=True,verbose_name=_("Rank"))
    taken_leaves = models.IntegerField(
        default=0, verbose_name=_("Leaves Taken"), blank=True, null=True)
    total_assignment = models.IntegerField(
        default=0, verbose_name=_("Total Assignment"), blank=True, null=True)
    completed_assignment = models.IntegerField(
        default=0, verbose_name=_("Completed Assignment"), blank=True, null=True) 
    total_homework = models.IntegerField(
        default=0, verbose_name=_("Total Homework"), blank=True, null=True) 
    completed_homework = models.IntegerField(
        default=0, verbose_name=_("Completed Homework"), blank=True, null=True) 
    fee_status = models.BooleanField(default=False,blank=True, null=True)
    employee_id = models.BigIntegerField(blank=True, null=True,unique=True,verbose_name=_("Employee ID"))
    student_id = models.BigIntegerField(blank=True, null=True,unique=True,verbose_name=_("Student ID"))
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def fullname(self):
        return self.get_full_name()


class OTP(DateTimeMixin):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=4)
    token = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"


class CourseDetails(DateTimeMixin):
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=250, blank=True, null=True)
    class_name = models.ForeignKey(
        ClassDetails,
        on_delete=models.CASCADE,
        verbose_name=_("Class"),
        blank=True,
        null=True,
    )
    duration = models.DurationField(
        verbose_name=_("Class Time"), default=timezone.timedelta(hours=1)
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Created By"),
    )

    class Meta:
        verbose_name = _("Course Details")

    def __str__(self):
        if self.title == None:
            return "ERROR-COURSE NAME IS NULL"
        return self.title or ""


class CourseSection(DateTimeMixin):
    section = models.CharField(max_length=250, verbose_name=_("Section Name"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Created By"),
    )
    course_name = models.ForeignKey(
        CourseDetails,
        on_delete=models.CASCADE,
        verbose_name=_("Course Details"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Course Section")

    def __str__(self):
        return self.section


class CourseSubSection(DateTimeMixin):
    sub_section_name = models.CharField(
        max_length=250, verbose_name=_("SubSection Name"), blank=True, null=True
    )
    course_section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        verbose_name=_("Course Section"),
        blank=True,
        null=True,
    )
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    image = models.FileField(
        upload_to="media/sub_section_files/",
        verbose_name=_("Video/Image"),
        blank=True,
        null=True,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Created By"),
    )

    class Meta:
        verbose_name = _("Course SubSection")

    def __str__(self):
        return self.sub_section_name


class CourseRating(DateTimeMixin):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_("user")
    )
    course_name = models.ForeignKey(
        CourseDetails,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Course Name"),
    )
    star = models.IntegerField(default=0, verbose_name=_("Star"), blank=True, null=True)
    comment = models.TextField(
        max_length=5000, verbose_name=_("Comment"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Course Rating Table")


class QuizSection(DateTimeMixin):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_("user")
    )
    course_name = models.ForeignKey(
        CourseDetails,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Course Name"),
    )
    comment = models.TextField(
        max_length=5000, verbose_name=_("Comment"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Quiz Section")


class CourseType(DateTimeMixin):
    type_name = models.CharField(
        max_length=150, verbose_name=_("Course Type Name"), blank=True, null=True
    )
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Course Type Table")

    def __str__(self):
        return self.type_name


class CourseLevel(DateTimeMixin):
    level_name = models.CharField(
        max_length=150, verbose_name=_("Course Level Name"), blank=True, null=True
    )
    created_by = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Created By")
    )

    class Meta:
        verbose_name = _("Course Level Table")


# class TeachersFeedback(models.Model):
#     uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
#     feedback = models.CharField(max_length=100,verbose_name=_('Teachers Feedback'),blank=True,null=True)
#     teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('user'))
#     feedback_by = models.ForeignKey(Student,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('user'))
#     created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
#     course_level = models.ForeignKey(CourseLevel,on_delete=models.CASCADE,verbose_name=_('Course Level'),blank=True,null=True)


#     class Meta:
#         verbose_name = _("Teachers Feedback Table")


#     def __str__(self):
#         return self.feedback
class BlacklistedToken(DateTimeMixin):
    token = models.CharField(max_length=355, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

class Division(DateTimeMixin):
    name = models.CharField(
        max_length=150, verbose_name=_("Division"), blank=True, null=True
    )
class SubjectDetails(DateTimeMixin):
    name = models.CharField(
        max_length=150, verbose_name=_("Division"), blank=True, null=True
    )

class TimeTableManage(DateTimeMixin):
    teacher = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE)
    class_name = models.ForeignKey(
        ClassDetails, blank=True, null=True, on_delete=models.CASCADE)
    division = models.ForeignKey(
        Division, blank=True, null=True, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        SubjectDetails, blank=True, null=True, on_delete=models.CASCADE
    )
