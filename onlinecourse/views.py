from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Course, Lesson, Enrollment, Question, Choice, Submission
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# --- CÁC HÀM XỬ LÝ LOGIC THEO YÊU CẦU CỦA QUESTION 5 ---

def submit(request, course_id):
    context = {}
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        # Lấy thông tin enrollment của user hiện tại
        enrollment = get_object_or_404(Enrollment, course=course, user=request.user)
        
        # Tạo một đối tượng Submission mới
        submission = Submission(enrollment=enrollment)
        submission.save()
        
        # Duyệt qua các câu hỏi trong khóa học để tìm các choice được chọn
        for question in course.question_set.all():
            for choice in question.choice_set.all():
                field_name = f"choice_{choice.id}"
                if field_name in request.POST:
                    submission.choices.add(choice)
                    
        submission.save()
        # Chuyển hướng sang trang kết quả bài thi
        return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id,)))

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Tính toán kết quả bài thi
    total_score = 0
    results = []
    
    # Lấy danh sách ID của các lựa chọn mà học viên đã đánh dấu
    selected_ids = [choice.id for choice in submission.choices.all()]
    
    for question in course.question_set.all():
        is_correct = question.is_get_score(selected_ids)
        if is_correct:
            total_score += question.grade
        results.append({'question': question, 'is_correct': is_correct})
        
    context['course'] = course
    context['submission'] = submission
    context['total_score'] = total_score
    context['results'] = results
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


# Các hàm có sẵn khác của hệ thống (Giữ nguyên hoặc cập nhật nếu cần)
def index(request):
    # Logic hiển thị danh sách khóa học
    pass
