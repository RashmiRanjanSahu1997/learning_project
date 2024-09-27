from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, action
import random
from datetime import timedelta
from django.utils import timezone
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
)
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import APIException, NotFound
import string
from .permissions import IsSchoolAdmin
from .pagination import get_pagination
from .authentication import UserTokenAuthentication


class UsersView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer

    @action(detail=False, methods=["POST"], url_path="register")
    def register(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                if User.objects.filter(email=request.data.get("email")).exists():
                    return Response(
                        {"message": "Email already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user_data = serializer.save()
                return Response(
                    {"message": "User Added Successfully"},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return Response(
                {"message": "An unexpected error occurred"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["POST"], url_path="login")
    def login_view(self, request):
        email = request.data.get("email").lower()
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return Response(
                {
                    "message": "Invalid Credentials",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                response_data = serializer.validated_data
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(
                {"message": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e)
            return Response(
                {"message": "An unexpected error occurred"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["POST"], url_path="send-otp")
    def send_otp(self, request):
        email = request.data.get("email").lower()
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return Response(
                {"message": "You are not a registered user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            otp = "".join([str(random.randint(0, 9)) for _ in range(4)])
            OTP.objects.update_or_create(email=email, defaults={"otp": otp})
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return Response(
                {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e), "message": "Somthing went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["POST"], url_path="verify-otp")
    def verify_otp(self, request):
        try:
            email = request.data.get("email")
            otp = request.data.get("otp")
            if not email or not otp:
                raise APIException("Email and OTP are required.")
            otp_obj = OTP.objects.filter(email=email, otp=otp).first()
            if otp_obj:
                token = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=12)
                )
                otp_obj.token = token
                otp_obj.otp = ""
                otp_obj.save()
                # otp_obj.delete()
                return Response(
                    {"message": "OTP verified successfully.", "token": token},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"message": "Failed to verify OTP. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["POST"], url_path="reset-password")
    def reset_password(self, request):
        try:
            email = request.data.get("email")
            new_password = request.data.get("new_password")
            token = request.headers.get("Authorization")
            if not email or not new_password:
                raise APIException("Email and new password are required.")
            otp_obj = OTP.objects.filter(email=email, token=token).first()
            if otp_obj:
                user = User.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()
                otp_obj.delete()
                return Response(
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Failed to reset password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"message": "Failed to reset password. Username Not Found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["POST"], url_path="logout")
    def logout_view(self, request):
        serializer = UserLogoutSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.logout_user()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="dropdown-employees",
        authentication_classes=[UserTokenAuthentication],
    )
    def dropdown_employees(self, request):
        try:
            employee_type = EmployeeType.objects.all()
            employment_type = EmploymentType.objects.all()
            position = EmployeePosition.objects.all()

            employee_serializer = EmployeeTypeSerializer(employee_type, many=True)
            employment_serializer = EmploymentTypeSerializer(employment_type, many=True)
            position_serializer = EmployeePositionSerializer(position, many=True)

            return Response(
                {
                    "employment_type": employment_serializer.data,
                    "employee_type": employee_serializer.data,
                    "postion": position_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailsViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CourseDetails.objects.all()
    serializer_class = CourseDetailsSerializer


class ClassDetailsViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = ClassDetails.objects.all()
    serializer_class = ClassDetailsSerializer


class EmployeeDetailsView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer

    def update(self, request, pk=None):
        try:
            if request.user.employee_type.type == "Admin":
                employee = User.objects.get(pk=pk)
                data = request.data
                serializer = UserDetailsSerializer(employee, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "You are not authorized to perform this action."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        if request.user.employee_type.type == "Admin":
            employment_type = request.query_params.get("employment_type")
            position = request.query_params.get("position")
            employment_type = None
            position_obj = None

            if employment_type:
                employment_type = EmploymentType.objects.get(id=employment_type)
            if position:
                position_obj = EmployeePosition.objects.get(id=position)

            if employment_type and position:
                employees = (
                    User.objects.filter(
                        employee_type=employment_type, position=position_obj
                    )
                    .exclude(id=request.user.id)
                    .order_by("-created_at")
                )

            elif employment_type:
                employees = (
                    User.objects.filter(employment_type=employment_type)
                    .exclude(id=request.user.id)
                    .order_by("-created_at")
                )
            elif position:
                employees = (
                    User.objects.filter(position=position_obj)
                    .exclude(id=request.user.id)
                    .order_by("-created_at")
                )
            else:
                employee_types = EmployeeType.objects.filter(
                    type__in=["Teacher", "Other", "Driver", "Staff", "Counselor"]
                )
                employees = (
                    User.objects.filter(employee_type__in=employee_types)
                    .exclude(id=request.user.id)
                    .order_by("-created_at")
                )

            page_obj, total_page = get_pagination(request, employees)
            try:
                if serializer := UserDetailsSerializer(page_obj, many=True):
                    return Response(
                        {
                            "status": True,
                            "total_page": total_page,
                            "data": serializer.data,
                            "total_page": total_page,
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"status": False, "error": "Invalid Request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"status": False, "error": "Something Went Wrong", "msg": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # serializer = UserDetailsSerializer(employees, many=True)
            # return Response(serializer.data)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def create(self, request):
        try:
            if request.user.employee_type.type == "Admin":

                email = request.data.get("email")
                print("email: ", email)
                if User.objects.filter(email=email).exists():
                    return Response(
                        {"message": "Email already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                password = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=8)
                )
                data = request.data.copy()

                data["photo"] = request.FILES.get("photo", None)
                data["password"] = make_password(password)
                serializer = EmployeeRegistrationSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    send_mail(
                        "Your Account has been added successfully",
                        f"Your email is your Username and Your password for login is: {password}"
                        + "\nClick this link for login: https://web-app.testyourapp.online/",
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                    return Response(
                        {"message": "Employee created Successfully"},
                        status=status.HTTP_201_CREATED,
                    )

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "You are not authorized to perform this action."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class EmployeeTypeView(viewsets.ModelViewSet):
#     permission_classes = (IsAuthenticated,)

#     def list(self, request):
#         employee_type = request.query_params.get("employee_type")
#         position = request.query_params.get("position")
#         if employee_type:
#             employees = User.objects.filter(employee_type=employee_type)
#             serializer = UserDetailsSerializer(employees, many=True)
#             return Response(serializer.data)
#         elif position:
#             employees = User.objects.filter(position=position)
#             serializer = UserDetailsSerializer(employees, many=True)
#             return Response(serializer.data)
#         elif position and employee_type:
#             employees = User.objects.filter(
#                 employee_type=employee_type, position=position
#             )
#             serializer = UserDetailsSerializer(employees, many=True)
#             return Response(serializer.data)


class StudentDetailView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer

    def update(self, request, pk=None):
        try:
            if request.user.employee_type.type == "Admin":
                student = User.objects.get(pk=pk)
                data = request.data
                serializer = UserDetailsSerializer(student, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "You are not authorized to perform this action."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        if request.user.employee_type.type == "Admin":
            class_id = request.query_params.get("class_name")
            if class_id:
                class_obj = ClassDetails.objects.get(id=class_id)
                students = User.objects.filter(class_name=class_obj)
            else:
                employee_type = EmployeeType.objects.filter(type="Student").first()
                students = User.objects.filter(employee_type=employee_type).order_by(
                    "-created_at"
                )
            page_obj, total_page = get_pagination(request, students)
            try:
                if serializer := UserDetailsSerializer(page_obj, many=True):
                    return Response(
                        {
                            "status": True,
                            "total_page": total_page,
                            "data": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"status": False, "error": "Invalid Request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"status": False, "error": "Something Went Wrong", "msg": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # serializer = UserDetailsSerializer(students, many=True)
            # return Response(serializer.data)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def create(self, request):
        try:
            if request.user.employee_type.type == "Admin":
                email = request.data["basic_info"]["email"]
                if User.objects.filter(email=email).exists():
                    return Response(
                        {"message": "Email already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                password = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=8)
                )
                data = request.data.copy()
                basic_data = data.get("basic_info")
                basic_data.update(data.get("parent_info"))
                basic_data["password"] = make_password(password)
                serializer = StudentRegistrationSerializer(data=basic_data)
                if serializer.is_valid():
                    serializer.save()
                    send_mail(
                        "Your Account has been added successfully",
                        f"Your email is your Username and Your password for login is: {password} "
                        + "\nClick this link for login: https://web-app.testyourapp.online/",
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                    return Response(
                        {"message": "Student created Successfully"},
                        status=status.HTTP_201_CREATED,
                    )

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "You are not authorized to perform this action."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CourseSectionViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CourseSection.objects.all()
    serializer_class = CourseSectionSerializer


class CourseSubSectionViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CourseSubSection.objects.all()
    serializer_class = CourseSubSectionSerializer


class OverallRatingView(viewsets.ModelViewSet):
    def list(self, request, course_id):
        ratings = CourseRating.objects.filter(course_name_id=course_id)
        total_ratings = ratings.count()
        if total_ratings == 0:
            return Response({"overall_rating": 0}, status=status.HTTP_200_OK)
        total_stars = sum([rating.star for rating in ratings])
        overall_rating = total_stars / total_ratings
        return Response({"overall_rating": overall_rating}, status=status.HTTP_200_OK)


class PostCourseReview(viewsets.ModelViewSet):
    def create(self, request):
        data = request.data.copy()
        data["user"] = request.user.id
        serializer = CourseRatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Review posted successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeePositionView(viewsets.ModelViewSet):
    queryset = EmployeePosition.objects.all()
    serializer_class = EmployeePositionSerializer


class EmployeeTypeView(viewsets.ModelViewSet):
    queryset = EmployeeType.objects.all()
    serializer_class = EmployeeTypeSerializer


class EmploymentTypeView(viewsets.ModelViewSet):
    queryset = EmploymentType.objects.all()
    serializer_class = EmploymentTypeSerializer
